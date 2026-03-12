# GOOGLE-TRENDS-PARAMS.md — pytrends Configuration Reference

## Installation

```bash
pip install pytrends
```

Requires Python 3.8+. No API key needed — pytrends uses the public Google Trends
interface. Rate limits apply (see below).

---

## Default Parameters

These defaults should be used in the research engine unless explicitly overridden:

```python
from pytrends.request import TrendReq

pytrends = TrendReq(
    hl='en-US',    # Language: English (US)
    tz=360         # Timezone offset in minutes: 360 = UTC-6 (Central Time)
)

# Build payload
pytrends.build_payload(
    kw_list=['your keyword here'],    # Up to 5 keywords per request
    timeframe='today 1-m',           # Last 30 days
    geo='US',                        # Geographic filter: United States
    gprop=''                         # Property: '' = web search (default)
)
```

### Parameter Reference

| Parameter   | Default         | Options                                                                 |
|-------------|-----------------|-------------------------------------------------------------------------|
| `hl`        | `'en-US'`       | Any BCP 47 language tag (e.g., `'en-GB'`, `'es-ES'`)                   |
| `tz`        | `360`           | Timezone offset in minutes from UTC (e.g., `0` = UTC, `300` = EST)     |
| `timeframe` | `'today 1-m'`   | See timeframe options below                                             |
| `geo`       | `'US'`          | ISO 3166-1 alpha-2 country code, or `''` for worldwide                 |
| `gprop`     | `''`            | `''` web, `'images'`, `'news'`, `'youtube'`, `'froogle'`               |

### Timeframe Options

| Value              | Meaning                          |
|--------------------|----------------------------------|
| `'now 1-H'`        | Last 1 hour                      |
| `'now 4-H'`        | Last 4 hours                     |
| `'now 1-d'`        | Last 1 day                       |
| `'now 7-d'`        | Last 7 days                      |
| `'today 1-m'`      | Last 30 days (recommended)       |
| `'today 3-m'`      | Last 90 days                     |
| `'today 12-m'`     | Last 12 months                   |
| `'today 5-y'`      | Last 5 years                     |
| `'all'`            | Since 2004                       |
| `'2025-01-01 2025-12-31'` | Custom date range         |

---

## Available Methods

### interest_over_time()

Returns a DataFrame with daily or weekly interest values (0–100) for each keyword.

```python
df = pytrends.interest_over_time()
# Columns: keyword names + 'isPartial' flag
# Index: datetime
# Values: 0-100 (100 = peak popularity in period)

# Get peak value for scoring
trend_score = int(df['your keyword'].max())

# Get trend direction (rising vs falling)
first_half = df['your keyword'].head(len(df) // 2).mean()
second_half = df['your keyword'].tail(len(df) // 2).mean()
trend_direction = "rising" if second_half > first_half else "falling"
```

### related_queries()

Returns two DataFrames per keyword: `top` (most searched) and `rising` (breakout queries).

```python
related = pytrends.related_queries()
# Structure: {keyword: {'top': DataFrame, 'rising': DataFrame}}

rising_df = related['your keyword']['rising']
# Columns: 'query', 'value'
# 'value' is 'Breakout' (string) or integer % increase

# Extract rising queries
rising_keywords = rising_df[rising_df['value'] == 'Breakout']['query'].tolist()
rising_keywords += rising_df[rising_df['value'] != 'Breakout']['query'].tolist()
```

### trending_searches()

Returns today's trending searches in a given country (no payload needed).

```python
trending = pytrends.trending_searches(pn='united_states')
# Returns a single-column DataFrame of trending search terms
trending_list = trending[0].tolist()
```

---

## Rate Limiting

Google Trends aggressively rate-limits automated access.

### Limits

- Maximum **10 requests per minute** under normal conditions
- Stricter limits apply after repeated requests — observed ~5 requests/minute in practice
- Google may return HTTP 429 after 3–5 rapid requests without delays

### Required Delay Between Requests

```python
import time
import random

# Minimum: 6 seconds between requests (10 req/min)
# Recommended: 8-12 seconds with jitter for safety
time.sleep(random.uniform(8, 12))
```

### Exponential Backoff on 429

```python
import time

def pytrends_request_with_backoff(pytrends_fn, max_retries=4):
    for attempt in range(max_retries):
        try:
            return pytrends_fn()
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                wait = (2 ** attempt) * 15  # 15s, 30s, 60s, 120s
                print(f"Rate limited. Waiting {wait}s before retry {attempt + 1}...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Max retries exceeded for Google Trends request")
```

---

## Common Errors and Fixes

### ResponseError: The request failed: Google returned a response with code 429

**Cause:** Too many requests sent too quickly.

**Fix:** Add minimum 10-second delay between requests. If persistent, wait 15–30 minutes
before retrying. Use exponential backoff (see above).

### ResponseError: The request failed: Google returned a response with code 500

**Cause:** Google Trends internal error, often triggered by an empty or invalid keyword.

**Fix:** Validate keyword is non-empty and contains no special characters. Retry once after 5 seconds.

### Empty DataFrame returned (no data)

**Cause:** Keyword has insufficient search volume in the selected `geo` + `timeframe`.

**Fix:** Broaden `geo` to `''` (worldwide) or extend `timeframe` to `'today 3-m'`.
If still empty, assign `trend_score = 0`.

```python
df = pytrends.interest_over_time()
if df.empty or keyword not in df.columns:
    trend_score = 0
else:
    trend_score = int(df[keyword].max())
```

### KeyError on keyword column

**Cause:** pytrends modifies keyword strings (strips special chars). Use the exact string
from `df.columns` rather than the original input.

**Fix:**
```python
actual_col = [c for c in df.columns if c != 'isPartial'][0]
trend_score = int(df[actual_col].max())
```

---

## Extracting Rising Queries and Breakout Keywords

Rising queries are the most valuable output for topic research — they signal emerging
interest before the topic becomes saturated.

```python
def get_rising_keywords(keyword: str) -> list[str]:
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(
        kw_list=[keyword],
        timeframe='today 1-m',
        geo='US'
    )

    time.sleep(10)  # Rate limit buffer

    related = pytrends.related_queries()
    rising_df = related.get(keyword, {}).get('rising')

    if rising_df is None or rising_df.empty:
        return []

    # Breakout = >5000% increase, listed as string "Breakout"
    breakout = rising_df[rising_df['value'] == 'Breakout']['query'].tolist()

    # High-rise = numeric % increase, sort descending
    numeric_rising = rising_df[rising_df['value'] != 'Breakout'].copy()
    numeric_rising = numeric_rising.sort_values('value', ascending=False)
    top_numeric = numeric_rising['query'].head(5).tolist()

    return breakout + top_numeric
```

### Using Rising Keywords for Topic Discovery

```python
base_topics = ["AI tools for consultants", "LinkedIn content strategy", "solopreneur growth"]

all_rising = []
for topic in base_topics:
    rising = get_rising_keywords(topic)
    all_rising.extend(rising)
    time.sleep(random.uniform(10, 15))  # Rate limit buffer between topics

# Deduplicate and return
unique_rising = list(dict.fromkeys(all_rising))
print(f"Found {len(unique_rising)} rising keyword opportunities")
```
