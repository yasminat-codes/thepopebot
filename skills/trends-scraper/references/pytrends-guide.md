# pytrends Guide

**Library:** `pytrends` (unofficial Google Trends API wrapper)
**Install:** `pip install pytrends>=4.9.2`

---

## Initialization

```python
from pytrends.request import TrendReq
pt = TrendReq(hl='en-US', tz=360)
```

- `hl='en-US'` — language for labels (does not affect raw data)
- `tz=360` — US Central timezone offset; does not change underlying data, just label formatting

---

## build_payload()

```python
pt.build_payload(
    kw_list,          # list of 1–5 keyword strings — HARD LIMIT
    cat=0,            # category filter (0 = all)
    timeframe=timeframe,  # see Timeframe Formats below
    geo=geo,          # see Geo Codes below
    gprop=''          # '' = web search; 'youtube', 'news', 'images', 'froogle' also valid
)
```

**5 keyword hard limit per call.** Exceeding it raises a ResponseError or silently drops extras. This skill batches in groups of 5.

---

## interest_over_time()

```python
df = pt.interest_over_time()
```

Returns a pandas DataFrame. Columns: one per keyword + `isPartial`. Index: datetime. Values: 0–100 (relative interest, not absolute search volume).

**Score calculation (this skill):**
```python
interest_score = float(df[kw].fillna(0).mean())
```

**Direction calculation (last 4 data points):**
```python
tail = list(df[kw].fillna(0).iloc[-4:])
slope = tail[-1] - tail[0]
if df[kw].max() > 90:
    direction = 'breakout'
elif slope > 5:
    direction = 'rising'
elif slope < -5:
    direction = 'declining'
else:
    direction = 'stable'
```

**Empty DataFrame:** When a keyword has no measurable interest, `df` will be empty or the column will be all zeros. Always check `df.empty` and `kw not in df.columns` before accessing.

---

## related_queries()

```python
rq = pt.related_queries()
# rq is a dict: {keyword: {'top': DataFrame, 'rising': DataFrame}}
```

`rq[kw]['rising']` — queries accelerating in growth (high-value signal).
`rq[kw]['top']` — highest-volume related searches (more stable, less novel).

**This skill uses rising only.**

**Safe access pattern:**
```python
rising_df = rq.get(kw, {}).get('rising')
if rising_df is not None and not rising_df.empty:
    for _, row in rising_df.head(5).iterrows():
        related.append({'query': row['query'], 'value': str(row['value'])})
```

`value` in the rising DataFrame is a relative percentage gain, not an absolute number. A value of 5000 means +5000% growth — "breakout rising."

---

## Geo Codes

| Market | Code |
|--------|------|
| United States | `'US'` |
| United Kingdom | `'GB'` |
| Global | `''` (empty string) |
| Germany | `'DE'` |

This skill uses `'US'` and `'GB'` — two passes per batch.

---

## Timeframe Formats

| Format | Meaning |
|--------|---------|
| `'today 1-m'` | Last 30 days (default for this skill) |
| `'today 3-m'` | Last 90 days |
| `'now 7-d'` | Last 7 days |
| `'today 12-m'` | Last 12 months |
| `'2025-01-01 2025-12-31'` | Custom date range |

---

## Rate Limits

Google rate-limits pytrends by IP (not by account — it's an unofficial API).

**Triggers:**
- Too many requests in a short window
- Concurrent requests (always serial — never thread pytrends)
- VPS/cloud IPs flagged as scrapers

**This skill's mitigations:**
- `sleep(2)` between batches (proactive — prevents hitting limits)
- `sleep(1)` between US and GB geo passes within a batch
- On `ResponseError` with '429' in message: `sleep(60)`, then raise `PyTrendsRateLimitError`
- `PyTrendsRateLimitError` triggers escalation to Tier 2 (SERP API)

Never retry pytrends after a 429 in the same run. Escalate immediately.

---

## Known Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `ResponseError: 429` | Rate limited | sleep(60), escalate to SERP API |
| Empty DataFrame | Keyword has no measurable interest | Return interest_score=0, skip |
| `KeyError` on rq[kw] | Keyword not in response | Use `.get()` with defaults |
| Partial data (`isPartial=True`) | Data for current period still accumulating | Normal — include in calculation |
| All values = 100 for one keyword | That keyword dominates all others in relative terms | Valid — pytrends is relative, not absolute |
| Google silently blocks query | Keyword triggers content policy filter | Returns empty — treat as interest_score=0 |
