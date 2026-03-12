# SERP API Reference

**Base URL:** `https://serpapi.com/search`
**Auth:** `api_key` query parameter — value from `SERP_API_KEY` in `shared/.env`
**Docs:** https://serpapi.com/google-trends-api

---

## Endpoint 1: Google Trends (per keyword)

```
GET https://serpapi.com/search
  ?engine=google_trends
  &q={keyword}
  &date=today+1-m
  &geo=US
  &api_key={SERP_API_KEY}
```

**Parameters:**

| Param | Required | Values | Notes |
|-------|----------|--------|-------|
| `engine` | yes | `google_trends` | — |
| `q` | yes | keyword string | URL-encoded |
| `date` | yes | `today 1-m`, `today 3-m`, `now 7-d` | Must use `+` not space in URL |
| `geo` | no | `US`, `GB`, `''` | Default: global |
| `api_key` | yes | from env | — |

**Key response path:**
```
response['interest_over_time']['timeline_data']
```

Each timeline item:
```json
{
  "date": "Dec 29, 2025",
  "timestamp": "1735430400",
  "values": [
    {
      "query": "AI consulting",
      "value": "72",
      "extracted_value": 72
    }
  ]
}
```

**Interest score extraction (this skill):**
```python
values = []
for point in response['interest_over_time']['timeline_data']:
    for item in point.get('values', []):
        values.append(float(item.get('extracted_value', 0)))
score = sum(values) / len(values) if values else 0.0
```

**Direction:** same slope calculation as pytrends (last 4 points).

---

## Endpoint 2: Google Trends Trending Now (bonus signal)

```
GET https://serpapi.com/search
  ?engine=google_trends_trending_now
  &frequency=weekly
  &geo=US
  &api_key={SERP_API_KEY}
```

**Parameters:**

| Param | Required | Values |
|-------|----------|--------|
| `engine` | yes | `google_trends_trending_now` |
| `frequency` | yes | `daily`, `weekly` |
| `geo` | no | ISO country code |

**Key response path:**
```
response['trending_searches']  # list of trending topic objects
```

This endpoint is called once per run (US only) as a bonus context signal. Non-blocking — if it fails, the run continues without it.

---

## GB Geo Pass

Same as Endpoint 1 with `&geo=GB`. Run after US pass. Merge results: average `extracted_value` arrays, keep direction from higher-scoring geo.

---

## Error Handling

```python
data = resp.json()
if 'error' in data:
    log.warning(f"SERP API error: {data['error']}")
    # continue — do not crash
```

Common errors:
- `"Your account credit balance is too low."` — out of credits, skip Tier 2, go to Tier 3
- `"Invalid API key."` — check `SERP_API_KEY` in shared/.env
- HTTP 429 — rate limited; add `time.sleep(2)` between per-keyword calls

---

## Pricing

- SERP API charges per search
- 30 keywords × 2 geos = 60 calls per full Tier 2 run
- Estimated cost at ~$0.005/call: **~$0.30 per full Tier 2 run**
- Tier 2 only activates when pytrends 429s — expected to be rare (monthly, not weekly)
- Monitor SERP API credit balance monthly

---

## Rate Limit Notes

- No documented hard rate limit for paid accounts
- As a precaution, add `time.sleep(0.5)` between per-keyword calls in production
- The trending_now endpoint is one call total per run — no rate concern
