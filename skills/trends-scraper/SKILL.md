---
name: trends-scraper
description: Tracks Google Trends for AI consulting keywords across US and UK. Use when you need trending keyword intelligence, niche relevance scoring, or want to identify rising topics in the AI consulting space.
allowed-tools: Bash Read Write
metadata: {"clawdbot":{"requires":{"env":["OPENROUTER_API_KEY","NEON_DATABASE_URL","SERP_API_KEY"],"bins":["python3"]},"primaryEnv":"OPENROUTER_API_KEY"}}
context: fork
agent: general-purpose
---

# trends-scraper

Fetches Google Trends data for 30 AI consulting keywords (US + GB), scores each for niche relevance using GPT-4o, and writes qualifying results to the `industry_trends` Neon table. Primary consumer: Suwaida's LinkedIn content intelligence pipeline. Available to all 16 agents.

**Skill path:** `/home/clawdbot/shared/skills/trends-scraper/`
**Pipeline context:** Stage 1 of Suwaida's Monday content intelligence run. Outputs feed into the synthesizer and post-generator stages.

---

## Overview

### What It Does

1. Loads 30 keywords (10 base + 20 from Suwaida's niche-keywords.json)
2. Fetches Google Trends data — interest scores, direction, rising related queries
3. Runs a dual geo pass (US first, then GB) and merges results per keyword
4. Sends all keyword data to GPT-4o for niche relevance scoring and content angle extraction
5. Filters to keywords with niche_relevance_score >= 0.5
6. Writes passing keywords to the `industry_trends` Neon table (upsert — safe to re-run)

### Free-First Design

Every run attempts Tier 1 (pytrends, free) first. Paid tiers activate only on failure:
- pytrends rate-limited (429) → escalate to SERP API
- SERP API unavailable → escalate to Apify

Budget target: $0.00 in normal operation. Max ~$0.50/week if fallbacks activate.

### Who Uses This Skill

- **Suwaida** — primary consumer via `pipeline.py`
- Any agent needing current AI consulting keyword intelligence
- Noor (Research) — ad hoc trend lookups

---

## Prerequisites

### Environment Variables

All in `/home/clawdbot/shared/.env`.

| Variable | Required | When Used |
|----------|----------|-----------|
| `OPENROUTER_API_KEY` | Always | GPT-4o Layer 2 analysis (via OpenRouter) |
| `NEON_DATABASE_URL` | Always | DB writes |
| `SERP_API_KEY` | Tier 2 fallback only | Loaded only when pytrends 429s |
| `APIFY_API_TOKEN` | Tier 3 fallback only | Loaded only when Tier 2 fails |

### Python Dependencies

```bash
pip install pytrends>=4.9.2 openai>=1.0.0 psycopg2-binary>=2.9 \
            requests>=2.31 python-dotenv>=1.0.0 apify-client>=1.0.0
```

### External File Dependencies

| File | Purpose | Behavior if Missing |
|------|---------|-------------------|
| `workspace-suwaida/skills/linkedin-content-intelligence/assets/niche-keywords.json` | 20 niche keywords | Warning logged, runs with base 10 only |
| `workspace-suwaida/skills/linkedin-content-intelligence/references/analysis-prompts-trends.md` | GPT-4o prompt | Hard fail — required |

---

## Quick Start

```bash
# Dry run — see what would be written without touching the DB
python3 /home/clawdbot/shared/skills/trends-scraper/scripts/trends_scraper.py --dry-run

# Normal run (pipeline mode)
python3 /home/clawdbot/shared/skills/trends-scraper/scripts/trends_scraper.py \
  --run-id abc-123 --week-of 2026-02-23

# Custom keywords, dry run
python3 /home/clawdbot/shared/skills/trends-scraper/scripts/trends_scraper.py \
  --keywords "AI governance,AI audit,AI compliance" --dry-run
```

---

## CLI Reference

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--run-id` | str | auto UUID | Links this run to a pipeline execution. Pass from `pipeline.py`. |
| `--week-of` | str | current Monday (ISO) | Pipeline week identifier. Format: `YYYY-MM-DD`. |
| `--dry-run` | flag | false | Print results to stdout. No DB writes. |
| `--keywords` | str | (from JSON files) | Comma-separated keyword list. Overrides default + niche keywords. |
| `--geo` | str | `US,GB` | Geo codes for SERP API override. pytrends always uses US + GB. |
| `--timeframe` | str | `today 1-m` | pytrends/SERP timeframe string. |
| `--skip-related` | flag | false | Skip rising related queries extraction. Faster, less signal. |

---

## Usage Examples

### Pipeline call (from pipeline.py)

```python
import subprocess

result = subprocess.run(
    ["python3",
     "/home/clawdbot/shared/skills/trends-scraper/scripts/trends_scraper.py",
     "--run-id", run_id,
     "--week-of", week_of],
    capture_output=True, text=True, check=True
)
log.info(f"trends-scraper: {result.stdout[-500:]}")
```

### Standalone — US only, skip related queries

```bash
python3 scripts/trends_scraper.py --geo US --skip-related --dry-run
```

### Force specific timeframe

```bash
python3 scripts/trends_scraper.py --timeframe "today 3-m" --dry-run
```

### Test with minimal keyword set

```bash
python3 scripts/trends_scraper.py \
  --keywords "AI consulting,AI ROI,AI strategy" \
  --run-id test-001 --week-of 2026-02-23 --dry-run
```

---

## Architecture

### Three-Tier Fallback

```
┌─────────────────────────────────────────────────────────┐
│  Tier 1 — pytrends (FREE)                               │
│  ├─ 5 keywords per batch                                │
│  ├─ sleep(2) between batches                            │
│  ├─ sleep(1) between US and GB geo passes               │
│  ├─ On 429: sleep(60) → raise PyTrendsRateLimitError    │
│  └─ Covers: interest_over_time(), related_queries()     │
└───────────────────────┬─────────────────────────────────┘
                        │ 429 on any batch
┌───────────────────────▼─────────────────────────────────┐
│  Tier 2 — SERP API (PAID FALLBACK)                      │
│  ├─ Per-keyword HTTP call to serpapi.com                │
│  ├─ US pass + GB pass per keyword                       │
│  ├─ Bonus: trending_now endpoint (non-blocking)         │
│  ├─ On SERP_API_KEY missing or HTTP error: skip → Tier 3│
│  └─ Cost: ~$0.30 for a full 30-keyword run              │
└───────────────────────┬─────────────────────────────────┘
                        │ SERP API unavailable
┌───────────────────────▼─────────────────────────────────┐
│  Tier 3 — Apify (PAID DOUBLE-FALLBACK)                  │
│  ├─ Actor: epctex/google-trends-scraper (verify first)  │
│  ├─ Poll with wait_for_run() — 600s timeout, 15s poll   │
│  ├─ On ApifyRunError/Timeout: log critical, return {}   │
│  └─ Cost: TBD — see references/apify-actors.md          │
└─────────────────────────────────────────────────────────┘
                        │ all tiers complete
┌───────────────────────▼─────────────────────────────────┐
│  Layer 2 — GPT-4o Analysis (always runs)                │
│  ├─ Loads analysis-prompts-trends.md from Suwaida WS    │
│  ├─ All keywords in one call (~30 items)                │
│  ├─ Returns: niche_relevance_score, shelf_life, angle   │
│  └─ Filter: keep niche_relevant=true AND score >= 0.5   │
└───────────────────────┬─────────────────────────────────┘
                        │ passing keywords only
┌───────────────────────▼─────────────────────────────────┐
│  Neon Write — industry_trends table (upsert)            │
│  ON CONFLICT (trend_name, week_of) DO UPDATE            │
└─────────────────────────────────────────────────────────┘
```

**Fallback scope:** Per-run, not per-keyword. If pytrends 429s on batch 3, all remaining keywords (batches 4–6) go to SERP API. Already-fetched batches (0–2) remain from pytrends.

---

## Data Flow

Step-by-step, from invocation to DB write:

```
1. load_keywords()
   ├─ Read assets/default-keywords.json → 10 base keywords
   ├─ Read niche-keywords.json → up to 20 more
   ├─ Deduplicate, enforce 40-keyword cap
   └─ Return: ['AI consulting', 'AI ROI', ...]

2. make_batches(keywords, size=5)
   └─ Return: [['kw1','kw2','kw3','kw4','kw5'], ...]  — 6 batches for 30 kws

3. fetch_all_pytrends(keywords, timeframe)
   For each batch i:
     ├─ if i > 0: sleep(2)
     ├─ fetch_pytrends_geo_pair(batch, timeframe)
     │   ├─ fetch_pytrends_batch(batch, 'US', timeframe)
     │   ├─ sleep(1)
     │   └─ fetch_pytrends_batch(batch, 'GB', timeframe)
     │       → merge: avg interest, union related, higher-score geo wins direction
     └─ merge batch result into master dict
   On 429: remaining keywords → fetch_serp_api() → merge into master

4. analyze_with_gpt4o(raw_data)
   ├─ Load system + user prompt from analysis-prompts-trends.md
   ├─ Format TRENDS_JSON array from raw_data
   ├─ POST to gpt-4o (temperature=0.3, response_format=json_object)
   └─ Parse response → list of per-keyword analysis dicts

5. filter_results(analysis)
   └─ Keep: niche_relevant=True AND niche_relevance_score >= 0.5

6. map_to_db_row() for each passing keyword
   └─ Map all fields per column mapping table below

7. write_to_neon(rows, dry_run)
   └─ Upsert each row → industry_trends
```

---

## Batching Strategy

### Why Batching

pytrends enforces a hard limit of 5 keywords per `build_payload()` call. 30 keywords = 6 batches.

### Sleep Pattern

```
Batch 0: fetch US (no sleep before) → sleep(1) → fetch GB → merge
sleep(2)
Batch 1: fetch US → sleep(1) → fetch GB → merge
sleep(2)
...
Batch 5: fetch US → sleep(1) → fetch GB → merge (no sleep after last)

Total minimum time: 5 × 2s (between batches) + 6 × 1s (between geos) = 16s
```

### Geo Dual-Pass Merge Logic

For each keyword, after US and GB fetches:
- `interest_score` = average of US score and GB score
- `direction` = taken from whichever geo returned higher interest_score
- `related_queries` = union of US and GB rising queries, deduplicated by query string, capped at 10

US and GB serve different audience signals for Yasmine's content. US reflects scale; GB reflects European professional behaviour patterns.

---

## Fallback Tiers — Detail

### Tier 1: pytrends

**Activation:** Default — every run starts here.
**Cost:** Free.
**Coverage:** interest_over_time(), related_queries() (rising).
**429 trigger:** Google detects high request volume from the IP.
**429 handling:**
1. `ResponseError` with '429' in message is caught in `fetch_pytrends_batch()`
2. `sleep(60)` immediately (gives Google time to reset)
3. Raises `PyTrendsRateLimitError`
4. `fetch_all_pytrends()` catches it, records which keywords are unprocessed, hands off to Tier 2

Never retry pytrends after a 429. Escalate immediately.

### Tier 2: SERP API

**Activation:** When pytrends raises `PyTrendsRateLimitError` for any batch.
**Cost:** ~$0.005/call × 60 calls (30 keywords × 2 geos) = ~$0.30 for a full run.
**Partial activation:** If pytrends fetched batches 0–2 before 429, only batches 3–5 hit SERP API (~36 calls = ~$0.18).
**SERP API missing:** If `SERP_API_KEY` not in env, logs error and attempts Tier 3.
**Per-keyword errors:** Logged and skipped — script continues with remaining keywords.

### Tier 3: Apify

**Activation:** Only when SERP API is unavailable (missing key, out of credits, or HTTP failure).
**Cost:** TBD — see `references/apify-actors.md`. Actor must be verified before production use.
**Polling:** `wait_for_run()` polls every 15s, times out at 600s.
**On failure:** Logs CRITICAL, returns empty dict for affected keywords. Pipeline continues with whatever data was collected from earlier tiers.

---

## 429 Handling

```
fetch_pytrends_batch()
  ├─ catches ResponseError
  ├─ checks '429' in str(e)
  ├─ sleep(60)  ← rate limit recovery window
  └─ raises PyTrendsRateLimitError

fetch_all_pytrends()
  ├─ catches PyTrendsRateLimitError
  ├─ calculates remaining = all keywords not yet in results dict
  ├─ calls fetch_serp_api(remaining, timeframe)
  └─ merges SERP results with pytrends results already in master dict

Result: merged dataset from multiple tiers — transparent to Layer 2 analysis
```

The 429 escalation is per-run, triggered once. If SERP API also fails, Tier 3 handles the remaining keywords.

---

## Related Queries Extraction

### What They Are

`related_queries()['rising']` returns search terms that are accelerating in growth relative to their baseline. A value of 5000 = +5000% growth — a breakout rising term.

**Why rising queries matter:** They identify what the audience is searching for *before* it peaks — high-value for content timing. A keyword like "AI consulting" might be stable, but its rising related query "AI consulting ROI" might be the actual emerging angle.

### How They Flow

```
pytrends.related_queries()[keyword]['rising']
→ DataFrame with columns: query, value
→ Extract top 5 rows: [{'query': '...', 'value': '5000'}, ...]
→ Stored in raw_data[keyword]['related_queries']
→ Passed to GPT-4o as part of TRENDS_JSON
→ Included in evidence JSONB column in industry_trends
```

### Skipping Related Queries

`--skip-related` strips related_queries from all results before GPT-4o analysis. Use when:
- Speed is critical (saves ~2s per batch from additional pytrends calls)
- Running a keyword-count-only audit
- Related queries aren't needed for the current use case

---

## Niche Relevance Filter

GPT-4o returns a `niche_relevance_score` (0.0–1.0) and a boolean `niche_relevant` flag for each keyword.

**Filter applied:**
```python
passing = [a for a in analysis
           if a.get('niche_relevant') is True
           and float(a.get('niche_relevance_score', 0)) >= 0.5]
```

**What gets excluded (score < 0.5):**
- Consumer-facing terms (e.g., "ChatGPT for free")
- Off-niche technology (e.g., "Python programming")
- Terms with no B2B or AI consulting relevance
- Ambiguous terms where niche relevance cannot be determined

**Log output:** `"X of Y keywords passed niche filter (threshold=0.5)"`

**If all keywords fail:** Check OPENROUTER_API_KEY is valid, prompt file loads correctly, and keywords aren't too generic. See troubleshooting.md.

---

## Layer 2 AI Analysis

### What GPT-4o Returns Per Keyword

| Field | Type | Description |
|-------|------|-------------|
| `niche_relevant` | bool | True if relevant to AI consulting niche |
| `niche_relevance_score` | float | 0.0–1.0 confidence |
| `trend_context` | str | Why it's trending — specific real-world cause |
| `audience_reading` | str | Who is searching and their likely intent |
| `content_angle` | str | Specific LinkedIn post POV for Yasmine's audience |
| `shelf_life` | str | evergreen / trending_now / rising / fading |
| `shelf_life_reasoning` | str | Why this shelf_life classification |
| `urgency_to_post` | str | this_week / this_month / this_quarter / anytime |
| `risk_flag` | str | none / sensitive / controversial / polarising |
| `risk_notes` | str | Risk detail if flag != none |
| `example_hook` | str | Specific LinkedIn opening line |

### Shelf Life Classification

| shelf_life | Meaning | Post Timing |
|------------|---------|-------------|
| `trending_now` | Active peak — post within 7 days | Urgent |
| `rising` | Growing — post within 30 days | This month |
| `evergreen` | Always relevant — any time | Anytime |
| `fading` | Declining — skip or deprioritise | Skip |

### Model Settings

- Model: `gpt-4o`
- Temperature: `0.3` (low — consistent, analytical outputs)
- Response format: `json_object` (prevents markdown wrapping)
- All 30 keywords in a single call — fits well within context

---

## Neon Table: industry_trends

### Column Mapping

| Column | Type | Source | Value |
|--------|------|--------|-------|
| `trend_name` | text | keyword | Raw keyword string |
| `trend_category` | text | hardcoded | Always `'ai_consulting'` |
| `description` | text | GPT `trend_context` | Why it's trending |
| `emergence_stage` | text | mapped from `shelf_life` | See mapping below |
| `signal_strength` | text | mapped from `urgency_to_post` | See mapping below |
| `evidence` | jsonb | scraper output | `{interest_score, direction, related_queries}` |
| `strategic_implications` | text | GPT `content_angle` | LinkedIn post angle |
| `monitoring_status` | text | hardcoded | Always `'active'` |
| `last_checked_date` | date | `date.today()` | Updated each run |
| `internal_notes` | text | GPT fields | `audience_reading + "\n\nRisk: " + risk_notes` |
| `detected_at` | timestamptz | `datetime.utcnow()` | First detection timestamp |
| `week_of` | date | `--week-of` arg | Pipeline week — ISO date |
| `run_id` | text | `--run-id` arg | UUID — pipeline traceability |

### emergence_stage Mapping

| shelf_life (GPT) | emergence_stage (DB) |
|-----------------|---------------------|
| `rising` | `emerging` |
| `trending_now` | `active` |
| `peaking` | `active` |
| `fading` | `declining` |
| `evergreen` | `active` |

### signal_strength Mapping

| urgency_to_post (GPT) | signal_strength (DB) |
|----------------------|---------------------|
| `this_week` | `high` |
| `this_month` | `medium` |
| `this_quarter` | `low` |
| `anytime` | `low` |

### evidence JSONB Structure

```json
{
  "interest_score": 72.4,
  "direction": "rising",
  "related_queries": [
    {"query": "AI consulting firms", "value": "5000"},
    {"query": "AI ROI measurement", "value": "3200"}
  ]
}
```

### Conflict Resolution SQL

```sql
INSERT INTO industry_trends
    (trend_name, trend_category, description, emergence_stage, signal_strength,
     evidence, strategic_implications, monitoring_status, last_checked_date,
     internal_notes, detected_at, week_of, run_id)
VALUES (...)
ON CONFLICT (trend_name, week_of) DO UPDATE SET
    signal_strength = EXCLUDED.signal_strength,
    evidence = EXCLUDED.evidence,
    last_checked_date = EXCLUDED.last_checked_date,
    run_id = EXCLUDED.run_id,
    description = EXCLUDED.description,
    strategic_implications = EXCLUDED.strategic_implications,
    internal_notes = EXCLUDED.internal_notes;
```

Re-running the same week overwrites with fresh data. First `detected_at` is preserved (not updated on conflict).

---

## Configuration

`assets/config.json` — runtime defaults. CLI flags always override.

```json
{
  "defaults": {
    "timeframe": "today 1-m",
    "geo": ["US", "GB"],
    "batch_size": 5,
    "sleep_between_batches": 2,
    "sleep_geo_pass": 1,
    "sleep_on_429": 60,
    "niche_relevance_threshold": 0.5,
    "keyword_max_cap": 40,
    "apify_timeout": 600,
    "apify_poll_interval": 15,
    "gpt_model": "gpt-4o",
    "gpt_temperature": 0.3
  },
  "apify": {
    "actor_id": "epctex/google-trends-scraper"
  }
}
```

**To adjust threshold:** Edit `niche_relevance_threshold` — raising to 0.7 gives a tighter filter; lowering to 0.4 lets more keywords through.
**To change actor:** Update `apify.actor_id` and verify new actor's schema against `apify_client.py`.

---

## Pipeline Integration

This skill is Stage 1 of Suwaida's Monday pipeline. Execution order:

```
1. trends-scraper       ← this skill
2. reddit-scraper       (parallel or sequential)
3. synthesizer          (consumes industry_trends + reddit outputs)
4. post-generator       (LinkedIn content creation)
```

**`pipeline.py` interface:**
- Calls `trends_scraper.py` as a subprocess
- Passes `--run-id` (shared UUID for full pipeline traceability) and `--week-of`
- Checks exit code: 0 = success, 1 = unrecoverable error
- On exit 1: pipeline halts or skips trend data (depending on pipeline config)

**Exit codes:**
- `0` — Success (even if 0 rows written — not a fatal error)
- `1` — Unrecoverable error (missing required env var, GPT-4o failure, etc.)

---

## Cost Guide

| Scenario | Tier Used | Estimated Cost |
|----------|-----------|---------------|
| Normal weekly run (no rate limits) | pytrends only | $0.00 |
| pytrends rate-limited mid-run | pytrends + SERP API partial | ~$0.05–$0.18 |
| pytrends fully blocked, SERP takes all | SERP API full run | ~$0.30 |
| SERP API also fails, Apify activated | Apify (verify cost) | TBD |
| GPT-4o analysis (all 30 keywords) | Layer 2, always | ~$0.02–$0.05 |
| **Typical weekly total** | pytrends | **~$0.02–$0.05** |
| **Worst-case weekly total** | All fallbacks | **~$0.35–$0.55** |

Monitor SERP API credit balance monthly. Apify should activate < once per month in practice.

---

## Resource Reference Map

| Situation | File | Purpose |
|-----------|------|---------|
| pytrends behaving unexpectedly | `references/pytrends-guide.md` | API surface, rate limits, known issues |
| SERP API response parsing | `references/serp-api-reference.md` | Endpoints, response schema, key paths |
| Apify actor setup or pricing | `references/apify-actors.md` | Actor research, input/output schema |
| GPT-4o prompt tuning | `references/analysis-prompt.md` | Prompt copy + usage notes |
| Error investigation | `references/troubleshooting.md` | Indexed symptom → fix |
| Runtime defaults | `assets/config.json` | All tunable parameters |
| Base keyword set | `assets/default-keywords.json` | 10 base seed keywords |
| Niche keywords | `workspace-suwaida/skills/linkedin-content-intelligence/assets/niche-keywords.json` | 20 niche-specific keywords |
| GPT-4o prompt (canonical) | `workspace-suwaida/skills/linkedin-content-intelligence/references/analysis-prompts-trends.md` | What `trends_scraper.py` reads at runtime |

---

## Decision Trees

Three decision trees: which tier is active, whether to adjust the niche threshold, and how to read unexpected dry-run output.

→ See [references/decision-trees.md](references/decision-trees.md) for full trees and real-world scenarios.

---

## Troubleshooting

See `references/troubleshooting.md` for indexed symptom → fix reference.

Quick reference:

| Symptom | First Action |
|---------|-------------|
| `ResponseError: 429` not caught | `pip install --upgrade pytrends` |
| Empty DataFrame for all keywords | Check IP rate limiting; try again in 10 min |
| `KeyError: SERP_API_KEY` | Check `grep SERP_API_KEY /home/clawdbot/shared/.env` |
| `industry_trends` upsert fails | Check UNIQUE constraint `(trend_name, week_of)` exists |
| All keywords score < 0.5 | Verify `OPENROUTER_API_KEY` and prompt path |
| GPT-4o malformed JSON | Check raw response in logs; prompt format issue |
| Apify actor not found | Search Apify Store for replacement; update config.json |
| `niche-keywords.json` missing | Warning only — runs with base 10 keywords |

---

**v1.0.0 — 2026-02-26:** Initial build. 3-tier fallback (pytrends → SERP API → Apify), dual geo US+GB, GPT-4o Layer 2 analysis, Neon upsert to `industry_trends`.
