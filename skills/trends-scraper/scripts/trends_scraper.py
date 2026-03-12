"""
trends-scraper — Google Trends data collection for industry_trends Neon table.

Tier 1: pytrends (free)
Tier 2: SERP API (paid fallback — activates on pytrends 429)
Tier 3: Apify (paid fallback — activates on SERP API failure)
Layer 2: GPT-4o niche relevance scoring and analysis
"""
import argparse
import json
import logging
import os
import sys
import time
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv
from pytrends.exceptions import ResponseError
from pytrends.request import TrendReq

load_dotenv('/home/clawdbot/shared/.env')

import openai

# Resolve OPENROUTER_API_KEY
_OPENROUTER_KEY = os.getenv('OPENROUTER_API_KEY')
if _OPENROUTER_KEY:
    os.environ['OPENROUTER_API_KEY'] = _OPENROUTER_KEY

BASE_DIR = Path(__file__).resolve().parent.parent
NICHE_KEYWORDS_PATH = Path('/home/clawdbot/workspace-suwaida/skills/linkedin-content-intelligence/assets/niche-keywords.json')
ANALYSIS_PROMPT_PATH = Path('/home/clawdbot/workspace-suwaida/skills/linkedin-content-intelligence/references/analysis-prompts-trends.md')
NEON_CLIENT_DIR = Path('/home/clawdbot/workspace-suwaida/skills/linkedin-content-intelligence/scripts/db')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger(__name__)

# Load config
with open(BASE_DIR / 'assets' / 'config.json') as _f:
    _FULL_CONFIG = json.load(_f)
    _CONFIG = _FULL_CONFIG['defaults']
    _APIFY_CONFIG = _FULL_CONFIG.get('apify', {})

BATCH_SIZE = _CONFIG['batch_size']
SLEEP_BETWEEN_BATCHES = _CONFIG['sleep_between_batches']
SLEEP_GEO_PASS = _CONFIG['sleep_geo_pass']
SLEEP_ON_429 = _CONFIG['sleep_on_429']
NICHE_THRESHOLD = _CONFIG['niche_relevance_threshold']
KEYWORD_MAX_CAP = _CONFIG['keyword_max_cap']
GPT_MODEL = _CONFIG['gpt_model']
GPT_TEMPERATURE = _CONFIG['gpt_temperature']

SERP_URL = 'https://serpapi.com/search'


# --- Exceptions ---

class PyTrendsRateLimitError(Exception):
    pass


class TrendsScraperError(Exception):
    pass


# Import Apify helpers (Tier 3 — loaded lazily to avoid hard fail if not installed)
def _import_apify():
    sys.path.insert(0, str(BASE_DIR / 'scripts'))
    from apify_helper import fetch_apify_trends, ApifyRunError, ApifyTimeoutError
    return fetch_apify_trends, ApifyRunError, ApifyTimeoutError


# --- Keyword Loading ---

def load_keywords(keywords_override: str | None) -> list:
    if keywords_override:
        kws = [k.strip() for k in keywords_override.split(',') if k.strip()]
        log.info(f"Using {len(kws)} keywords from --keywords flag")
    else:
        with open(BASE_DIR / 'assets' / 'default-keywords.json') as f:
            base = json.load(f)['keywords']

        niche = []
        if NICHE_KEYWORDS_PATH.exists():
            try:
                with open(NICHE_KEYWORDS_PATH) as f:
                    data = json.load(f)
                    raw = data if isinstance(data, list) else data.get('keywords', [])
                    # Normalize: niche items may be dicts {"keyword": "...", ...} or plain strings
                    niche = [item['keyword'] if isinstance(item, dict) else item for item in raw]
                log.info(f"Loaded {len(niche)} keywords from niche-keywords.json")
            except Exception as e:
                log.warning(f"Could not load niche-keywords.json: {e} — using base keywords only")
        else:
            log.warning(f"niche-keywords.json not found at {NICHE_KEYWORDS_PATH} — using base 10 only")

        seen = set()
        kws = []
        for k in base + niche:
            if k not in seen:
                seen.add(k)
                kws.append(k)

    if len(kws) > KEYWORD_MAX_CAP:
        log.warning(f"Keyword count {len(kws)} exceeds max cap {KEYWORD_MAX_CAP} — truncating")
        kws = kws[:KEYWORD_MAX_CAP]

    log.info(f"Total keywords to process: {len(kws)}")
    return kws


def make_batches(keywords: list, size: int = BATCH_SIZE) -> list:
    return [keywords[i:i + size] for i in range(0, len(keywords), size)]


# --- Tier 1: pytrends ---

def fetch_pytrends_batch(kw_list: list, geo: str, timeframe: str) -> dict:
    """Single pytrends batch for one geo. Raises PyTrendsRateLimitError on 429."""
    pt = TrendReq(hl='en-US', tz=360)
    pt.build_payload(kw_list, cat=0, timeframe=timeframe, geo=geo)

    try:
        df = pt.interest_over_time()
        rq = pt.related_queries()
    except ResponseError as e:
        if '429' in str(e):
            log.warning(f"pytrends 429 on geo={geo}, batch={kw_list} — sleeping {SLEEP_ON_429}s")
            time.sleep(SLEEP_ON_429)
            raise PyTrendsRateLimitError()
        raise

    results = {}
    for kw in kw_list:
        if df.empty or kw not in df.columns:
            results[kw] = {'interest_score': 0.0, 'direction': 'stable', 'related_queries': []}
            continue

        series = df[kw].fillna(0)
        interest_score = round(float(series.mean()), 1)

        direction = 'stable'
        if len(series) >= 4:
            tail = list(series.iloc[-4:])
            slope = tail[-1] - tail[0]
            if float(series.max()) > 90:
                direction = 'breakout'
            elif slope > 5:
                direction = 'rising'
            elif slope < -5:
                direction = 'declining'

        related = []
        try:
            rising_df = rq.get(kw, {}).get('rising')
            if rising_df is not None and not rising_df.empty:
                for _, row in rising_df.head(5).iterrows():
                    related.append({
                        'query': str(row.get('query', '')),
                        'value': str(row.get('value', '')),
                    })
        except Exception as e:
            log.debug(f"related_queries parse error for '{kw}': {e}")

        results[kw] = {
            'interest_score': interest_score,
            'direction': direction,
            'related_queries': related,
        }

    return results


def fetch_pytrends_geo_pair(kw_list: list, timeframe: str) -> dict:
    """Fetch US + GB for one batch. Merges results. Raises PyTrendsRateLimitError if either geo 429s."""
    us = fetch_pytrends_batch(kw_list, 'US', timeframe)
    time.sleep(SLEEP_GEO_PASS)
    gb = fetch_pytrends_batch(kw_list, 'GB', timeframe)

    merged = {}
    for kw in kw_list:
        u = us.get(kw, {'interest_score': 0.0, 'direction': 'stable', 'related_queries': []})
        g = gb.get(kw, {'interest_score': 0.0, 'direction': 'stable', 'related_queries': []})

        avg_score = round((u['interest_score'] + g['interest_score']) / 2, 1)
        direction = u['direction'] if u['interest_score'] >= g['interest_score'] else g['direction']

        seen_queries = set()
        combined_related = []
        for rq in u['related_queries'] + g['related_queries']:
            q = rq.get('query', '')
            if q and q not in seen_queries:
                seen_queries.add(q)
                combined_related.append(rq)

        merged[kw] = {
            'interest_score': avg_score,
            'direction': direction,
            'related_queries': combined_related[:10],
        }

    return merged


def fetch_all_pytrends(keywords: list, timeframe: str, skip_related: bool = False) -> tuple:
    """
    Orchestrate all pytrends batches. On 429, escalates remaining keywords to SERP API.
    Returns (results_dict, source_tag_str).
    """
    batches = make_batches(keywords)
    results = {}
    source = 'pytrends'

    for i, batch in enumerate(batches):
        if i > 0:
            time.sleep(SLEEP_BETWEEN_BATCHES)
        try:
            batch_result = fetch_pytrends_geo_pair(batch, timeframe)
            if skip_related:
                for v in batch_result.values():
                    v['related_queries'] = []
            results.update(batch_result)
            log.info(f"Batch {i+1}/{len(batches)} complete — {len(batch)} keywords via pytrends")
        except PyTrendsRateLimitError:
            fetched_so_far = set(results.keys())
            remaining = [k for k in keywords if k not in fetched_so_far]
            log.warning(f"pytrends 429 at batch {i+1} — escalating {len(remaining)} remaining keywords to SERP API")
            serp_results = fetch_serp_api(remaining, timeframe)
            results.update(serp_results)
            source = 'pytrends+serp_api'
            break

    return results, source


# --- Tier 2: SERP API ---

def _parse_serp_interest(response_data: dict) -> tuple:
    """Parse SERP API google_trends response. Returns (interest_score, direction)."""
    iot = response_data.get('interest_over_time', {})
    timeline = iot.get('timeline_data') or []
    values = []
    for point in timeline:
        for item in point.get('values', []):
            try:
                values.append(float(item.get('extracted_value', 0)))
            except (TypeError, ValueError):
                pass

    if not values:
        return 0.0, 'stable'

    score = round(sum(values) / len(values), 1)
    direction = 'stable'
    if len(values) >= 4:
        slope = values[-1] - values[-4]
        if max(values) > 90:
            direction = 'breakout'
        elif slope > 5:
            direction = 'rising'
        elif slope < -5:
            direction = 'declining'

    return score, direction


def fetch_serp_api(keywords: list, timeframe: str) -> dict:
    """Tier 2 fallback. Calls SERP API per keyword for US + GB. Non-crashing per keyword."""
    api_key = os.getenv('SERP_API_KEY')
    if not api_key:
        log.error("SERP_API_KEY not set — cannot use Tier 2 fallback. Attempting Tier 3.")
        return fetch_apify(keywords, timeframe)

    results = {}

    for kw in keywords:
        us_score, us_dir = 0.0, 'stable'
        gb_score, gb_dir = 0.0, 'stable'

        for geo_code in ['US', 'GB']:
            try:
                resp = requests.get(SERP_URL, params={
                    'engine': 'google_trends',
                    'q': kw,
                    'date': timeframe,
                    'geo': geo_code,
                    'api_key': api_key,
                }, timeout=30)
                data = resp.json()
                if 'error' in data:
                    log.warning(f"SERP API error for '{kw}' geo={geo_code}: {data['error']}")
                    continue
                score, direction = _parse_serp_interest(data)
                if geo_code == 'US':
                    us_score, us_dir = score, direction
                else:
                    gb_score, gb_dir = score, direction
            except Exception as e:
                log.warning(f"SERP API request failed for '{kw}' geo={geo_code}: {e}")

        time.sleep(0.5)  # Rate limit per SERP API docs
        avg_score = round((us_score + gb_score) / 2, 1)
        direction = us_dir if us_score >= gb_score else gb_dir

        results[kw] = {
            'interest_score': avg_score,
            'direction': direction,
            'related_queries': [],
        }
        log.info(f"SERP API: '{kw}' → score={avg_score}, direction={direction}")

    # Bonus: trending now (non-blocking)
    try:
        resp = requests.get(SERP_URL, params={
            'engine': 'google_trends_trending_now',
            'frequency': 'weekly',
            'geo': 'US',
            'api_key': api_key,
        }, timeout=30)
        trending = resp.json().get('trending_searches', [])
        log.info(f"SERP trending_now: {len(trending)} trending searches fetched")
    except Exception as e:
        log.debug(f"trending_now call skipped: {e}")

    return results


# --- Tier 3: Apify ---

def fetch_apify(keywords: list, timeframe: str) -> dict:
    """Tier 3 fallback — delegates to apify_client.fetch_apify_trends()."""
    try:
        fetch_apify_trends, ApifyRunError, ApifyTimeoutError = _import_apify()
        actor_id = _APIFY_CONFIG.get('actor_id', 'epctex/google-trends-scraper')
        results = fetch_apify_trends(keywords, geo='US', timeframe=timeframe, actor_id=actor_id)
        log.info(f"Apify Tier 3: fetched {len(results)} keywords")
        return results
    except Exception as e:
        log.critical(f"Apify Tier 3 failed: {e} — returning empty results for {len(keywords)} keywords")
        return {kw: {'interest_score': 0.0, 'direction': 'stable', 'related_queries': []} for kw in keywords}


# --- Layer 2: GPT-4o Analysis ---

def _load_analysis_prompt() -> tuple:
    """Load system + user prompt template from analysis-prompts-trends.md."""
    if not ANALYSIS_PROMPT_PATH.exists():
        raise TrendsScraperError(f"Analysis prompt not found: {ANALYSIS_PROMPT_PATH}")

    text = ANALYSIS_PROMPT_PATH.read_text()

    system_prompt = ''
    user_prompt_template = ''

    if '## System Prompt' in text and '## User Prompt' in text:
        parts = text.split('## User Prompt', 1)
        sys_section = parts[0].split('## System Prompt', 1)[-1].strip()
        user_section = parts[1].strip()
        # Strip any leading markdown from the user prompt section header content
        system_prompt = sys_section
        user_prompt_template = user_section
    else:
        # Fallback: treat full text as user prompt, use a sensible system prompt
        system_prompt = (
            'You are an expert in search intelligence and content timing strategy for B2B audiences. '
            'Analyse trending topics in the AI consulting and implementation niche.'
        )
        user_prompt_template = text

    return system_prompt, user_prompt_template


def analyze_with_gpt4o(trends_data: dict) -> list:
    """
    Submit all keyword data to GPT-4o for niche relevance scoring.
    Returns list of per-keyword analysis dicts.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        raise TrendsScraperError(
            "OPENROUTER_API_KEY not found in shared/.env"
        )

    system_prompt, user_prompt_template = _load_analysis_prompt()

    trends_array = []
    for kw, data in trends_data.items():
        trends_array.append({
            'keyword': kw,
            'interest_score': data.get('interest_score', 0),
            'direction': data.get('direction', 'stable'),
            'related_queries': data.get('related_queries', []),
            'period': 'last 30 days',
        })

    trends_json_str = json.dumps(trends_array, indent=2)
    user_prompt = user_prompt_template.replace('{TRENDS_JSON}', trends_json_str)

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    log.info(f"Calling GPT-4o for {len(trends_array)} keywords...")

    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            response_format={'type': 'json_object'},
            temperature=GPT_TEMPERATURE,
        )
    except Exception as e:
        log.error(f"GPT-4o call failed: {e}")
        return []

    raw = response.choices[0].message.content
    try:
        parsed = json.loads(raw)
        # GPT wraps array in a key — unwrap if needed
        if isinstance(parsed, dict):
            for v in parsed.values():
                if isinstance(v, list):
                    parsed = v
                    break
        if not isinstance(parsed, list):
            log.error(f"GPT-4o returned unexpected structure: {type(parsed)}")
            return []
        log.info(f"GPT-4o analysis complete: {len(parsed)} keyword objects")
        return parsed
    except json.JSONDecodeError as e:
        log.error(f"GPT-4o returned malformed JSON: {e}\nRaw: {raw[:500]}")
        return []


# --- Filter + Mapping ---

def filter_results(analysis: list) -> list:
    passing = [
        a for a in analysis
        if a.get('niche_relevant') is True and float(a.get('niche_relevance_score', 0)) >= NICHE_THRESHOLD
    ]
    log.info(f"{len(passing)} of {len(analysis)} keywords passed niche filter (threshold={NICHE_THRESHOLD})")
    return passing


_SHELF_LIFE_MAP = {
    'rising': 'emerging',
    'trending_now': 'active',
    'peaking': 'active',
    'fading': 'declining',
    'evergreen': 'active',
}

_URGENCY_MAP = {
    'this_week': 'high',
    'this_month': 'medium',
    'this_quarter': 'low',
    'anytime': 'low',
}


def map_to_db_row(keyword: str, trend_data: dict, analysis: dict, run_id: str, week_of: str) -> dict:
    shelf_life = analysis.get('shelf_life', 'evergreen')
    urgency = analysis.get('urgency_to_post', 'anytime')

    evidence = {
        'interest_score': trend_data.get('interest_score', 0),
        'direction': trend_data.get('direction', 'stable'),
        'related_queries': trend_data.get('related_queries', []),
    }

    audience_reading = analysis.get('audience_reading', '')
    risk_notes = analysis.get('risk_notes', '')
    internal_notes = audience_reading
    if risk_notes:
        internal_notes += f"\n\nRisk: {risk_notes}"

    return {
        'trend_name': keyword,
        'trend_category': 'ai_consulting',
        'description': analysis.get('trend_context', ''),
        'emergence_stage': _SHELF_LIFE_MAP.get(shelf_life, 'active'),
        'signal_strength': _URGENCY_MAP.get(urgency, 'low'),
        'evidence': json.dumps(evidence),
        'strategic_implications': analysis.get('content_angle', ''),
        'monitoring_status': 'active',
        'last_checked_date': date.today().isoformat(),
        'internal_notes': internal_notes,
        'detected_at': datetime.utcnow().isoformat(),
        'week_of': week_of,
        'run_id': run_id,
    }


# --- Neon Write ---

def write_to_neon(rows: list, dry_run: bool) -> int:
    if dry_run:
        print("\n=== DRY RUN — No DB writes ===")
        for i, row in enumerate(rows, 1):
            print(f"\n[{i}] {row['trend_name']}")
            print(f"  Emergence: {row['emergence_stage']} | Signal: {row['signal_strength']}")
            print(f"  Description: {row['description'][:120]}...")
            print(f"  Angle: {row['strategic_implications'][:120]}...")
        return 0

    conn_str = os.getenv('NEON_DATABASE_URL')
    if not conn_str:
        raise TrendsScraperError("NEON_DATABASE_URL not set in shared/.env")

    sql = """
        INSERT INTO industry_trends
            (trend_name, trend_category, description, emergence_stage, signal_strength,
             evidence, strategic_implications, monitoring_status, last_checked_date,
             internal_notes, detected_at, week_of, run_id)
        VALUES
            (%(trend_name)s, %(trend_category)s, %(description)s, %(emergence_stage)s,
             %(signal_strength)s, %(evidence)s::jsonb, %(strategic_implications)s,
             %(monitoring_status)s, %(last_checked_date)s, %(internal_notes)s,
             %(detected_at)s, %(week_of)s, %(run_id)s)
        ON CONFLICT (trend_name, week_of) DO UPDATE SET
            signal_strength = EXCLUDED.signal_strength,
            evidence = EXCLUDED.evidence,
            last_checked_date = EXCLUDED.last_checked_date,
            run_id = EXCLUDED.run_id,
            description = EXCLUDED.description,
            strategic_implications = EXCLUDED.strategic_implications,
            internal_notes = EXCLUDED.internal_notes
    """

    written = 0
    conn = psycopg2.connect(conn_str)
    try:
        with conn.cursor() as cur:
            for row in rows:
                try:
                    cur.execute(sql, row)
                    written += 1
                    log.info(f"Wrote: {row['trend_name']} (signal={row['signal_strength']})")
                except Exception as e:
                    log.error(f"DB error for '{row['trend_name']}': {e}")
                    conn.rollback()
                    conn = psycopg2.connect(conn_str)
        conn.commit()
    finally:
        conn.close()

    return written


# --- Importable entry point ---

def run(run_id: str, week_of: str, keywords=None, geo=None, timeframe='today 1-m', dry_run=False) -> int:
    """
    Importable entry point for pipeline.py.
    Returns count of rows written to industry_trends.
    """
    # Load keywords
    kw_list = keywords
    if kw_list is None:
        kw_list = load_keywords(None)
    elif isinstance(kw_list, str):
        kw_list = [k.strip() for k in kw_list.split(',')]

    # Fetch trends with 3-tier fallback
    raw_data, source = fetch_all_pytrends(kw_list, timeframe)

    if not raw_data:
        log.warning("No trend data retrieved from any source")
        return 0

    # Analyze with GPT-4o
    analysis = analyze_with_gpt4o(raw_data)
    filtered = filter_results(analysis)

    if dry_run:
        log.info(f"[dry-run] Would write {len(filtered)} keywords to industry_trends")
        for a in filtered[:5]:
            log.info(f"  {a.get('keyword', 'unknown')}: score={a.get('niche_relevance_score', 0):.2f}")
        return len(filtered)

    # Map to DB rows and write
    rows = [map_to_db_row(a.get('keyword', ''), raw_data.get(a.get('keyword', ''), {}), a, run_id, week_of)
            for a in filtered if a.get('keyword')]
    return write_to_neon(rows, dry_run=False)


# --- CLI ---

def _current_monday() -> str:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Google Trends for AI consulting keywords and write to industry_trends.'
    )
    parser.add_argument('--run-id', default=str(uuid.uuid4()),
                        help='UUID for this pipeline run (default: auto-generated)')
    parser.add_argument('--week-of', default=_current_monday(),
                        help='ISO date for pipeline week (default: current Monday)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print results without writing to DB')
    parser.add_argument('--keywords',
                        help='Comma-separated keywords (overrides default-keywords.json + niche-keywords.json)')
    parser.add_argument('--geo', default='US,GB',
                        help='Comma-separated geo codes (default: US,GB)')
    parser.add_argument('--timeframe', default='today 1-m',
                        help='pytrends timeframe string (default: today 1-m)')
    parser.add_argument('--skip-related', action='store_true',
                        help='Skip related queries extraction (faster, less signal)')
    args = parser.parse_args()

    log.info(f"trends-scraper starting | run_id={args.run_id} | week_of={args.week_of} | dry_run={args.dry_run}")

    try:
        keywords = load_keywords(args.keywords)
        raw_data, source = fetch_all_pytrends(keywords, args.timeframe, skip_related=args.skip_related)

        if not raw_data:
            log.error("No trend data collected from any tier — exiting")
            sys.exit(1)

        analysis = analyze_with_gpt4o(raw_data)
        if not analysis:
            log.error("GPT-4o analysis returned no results — exiting")
            sys.exit(1)

        passing = filter_results(analysis)

        rows = []
        for item in passing:
            kw = item.get('keyword', '')
            trend_data = raw_data.get(kw, {})
            row = map_to_db_row(kw, trend_data, item, args.run_id, args.week_of)
            rows.append(row)

        written = write_to_neon(rows, args.dry_run)

        log.info(
            f"trends-scraper complete | source={source} | "
            f"keywords={len(raw_data)} | passed_filter={len(passing)} | rows_written={written}"
        )

        if args.dry_run:
            print(f"\nSource: {source}")
            print(f"Keywords fetched: {len(raw_data)}")
            print(f"Passed niche filter: {len(passing)}/{len(raw_data)}")
            print(f"Rows written: 0 (dry run)")

        sys.exit(0)

    except TrendsScraperError as e:
        log.critical(f"Unrecoverable error: {e}")
        sys.exit(1)
    except Exception as e:
        log.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
