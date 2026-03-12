"""Apify client utility for trends-scraper (Tier 3 fallback)."""
import json
import logging
import os
import time

from dotenv import load_dotenv

load_dotenv('/home/clawdbot/shared/.env')

from apify_client import ApifyClient

log = logging.getLogger(__name__)


class ApifyTimeoutError(Exception):
    pass


class ApifyRunError(Exception):
    pass


def get_client() -> ApifyClient:
    token = os.environ.get('APIFY_API_TOKEN', '')
    if not token:
        raise ApifyRunError("APIFY_API_TOKEN not set in environment — cannot use Apify tier")
    return ApifyClient(token)


def run_actor(actor_id: str, input_data: dict) -> str:
    client = get_client()
    run = client.actor(actor_id).call(run_input=input_data, wait_secs=0)
    log.info(f"Started Apify actor {actor_id}, run_id={run['id'][:8]}")
    return run['id']


def get_run_status(run_id: str) -> str:
    client = get_client()
    run = client.run(run_id).get()
    return run['status']


def fetch_dataset(run_id: str) -> list:
    client = get_client()
    items = list(client.run(run_id).dataset().iterate_items())
    log.info(f"Fetched {len(items)} items from run {run_id[:8]}")
    return items


def wait_for_run(run_id: str, timeout: int = 600, poll_interval: int = 15) -> list:
    elapsed = 0
    while elapsed < timeout:
        status = get_run_status(run_id)
        log.info(f"Apify run {run_id[:8]}: {status} ({elapsed}s elapsed)")
        if status == 'SUCCEEDED':
            return fetch_dataset(run_id)
        if status in ('FAILED', 'ABORTED', 'TIMED-OUT'):
            raise ApifyRunError(f"Run {run_id[:8]} ended with: {status}")
        time.sleep(poll_interval)
        elapsed += poll_interval
    raise ApifyTimeoutError(f"Run {run_id[:8]} timed out after {timeout}s")


def fetch_apify_trends(keywords: list, geo: str = 'US', timeframe: str = 'today 1-m', actor_id: str = 'epctex/google-trends-scraper') -> dict:
    """
    Run epctex/google-trends-scraper actor and return results in the standard
    trends dict schema: {keyword: {interest_score, direction, related_queries}}.
    """
    input_data = {
        'queries': keywords,
        'geo': geo,
        'timeframe': timeframe,
        'maxItems': len(keywords) * 10,
    }

    run_id = run_actor(actor_id, input_data)
    raw_items = wait_for_run(run_id)

    results = {}
    for item in raw_items:
        keyword = item.get('query') or item.get('keyword', '')
        if not keyword:
            continue

        # Actor returns timelineData as list of {date, value} or similar
        timeline = item.get('timelineData') or item.get('interest_over_time') or []
        values = []
        for point in timeline:
            v = point.get('value') or point.get('extracted_value') or 0
            try:
                values.append(float(v))
            except (TypeError, ValueError):
                pass

        interest_score = round(sum(values) / len(values), 1) if values else 0.0

        direction = 'stable'
        if len(values) >= 4:
            slope = values[-1] - values[-4]
            if slope > 5:
                direction = 'breakout' if max(values) > 90 else 'rising'
            elif slope < -5:
                direction = 'declining'

        rising = item.get('risingRelatedQueries') or item.get('rising_related_queries') or []
        related = []
        for rq in rising[:5]:
            q = rq.get('query', '') if isinstance(rq, dict) else str(rq)
            val = rq.get('value', '') if isinstance(rq, dict) else ''
            related.append({'query': q, 'value': val})

        results[keyword] = {
            'interest_score': interest_score,
            'direction': direction,
            'related_queries': related,
        }

    log.info(f"fetch_apify_trends: parsed {len(results)} keywords from Apify run {run_id[:8]}")
    return results
