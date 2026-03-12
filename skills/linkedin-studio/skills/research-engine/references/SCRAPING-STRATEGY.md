# SCRAPING-STRATEGY.md — LinkedIn 3-Fallback Scraping Chain

## Overview

LinkedIn data collection uses a 3-level fallback chain. Each level is tried in order.
If a level fails or is unavailable, the next level is triggered automatically.
The research engine always attempts the highest-fidelity option first.

---

## Fallback Chain Summary

```
Level 1: Playwright (headless browser)
    ↓ fails (blocked, timeout, no cookies)
Level 2: SerpAPI (LinkedIn search via Google)
    ↓ fails (quota exhausted, API key missing)
Level 3: Manual paste (user provides content directly)
```

---

## Level 1: Playwright Headless Browser

### When to Use

Use Playwright when LinkedIn session cookies are available and the target content
requires authenticated access (e.g., full post text, exact engagement counts).

### Configuration

```python
PLAYWRIGHT_HEADLESS = True        # Set via environment variable
PLAYWRIGHT_RATE_LIMIT_SECONDS = 2 # Minimum seconds between requests
PLAYWRIGHT_MAX_CONCURRENT = 5     # Maximum parallel browser contexts
PLAYWRIGHT_TIMEOUT_MS = 30000     # 30 second page load timeout
PLAYWRIGHT_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
```

### Environment Variables

```bash
PLAYWRIGHT_HEADLESS=true
LINKEDIN_COOKIES_PATH=./secrets/linkedin-cookies.json  # Netscape cookie format
```

### Rate Limiting

- Minimum 2 seconds between each request (enforced with `asyncio.sleep(2)`)
- Maximum 5 concurrent browser contexts at any time
- If LinkedIn returns a CAPTCHA page or login redirect, treat as blocked and fall to Level 2
- Randomize wait between 2–4 seconds using `random.uniform(2, 4)` to avoid pattern detection

### Detection Triggers (fall to Level 2)

- HTTP 999 response (LinkedIn bot block)
- Redirect to `linkedin.com/login` or `linkedin.com/checkpoint`
- CAPTCHA detected in page HTML (`aria-label="Captcha"`)
- Timeout after 30 seconds
- `playwright._impl._errors.TimeoutError` raised

### Data Collected

```python
{
    "post_text": str,
    "author_name": str,
    "author_title": str,
    "reactions": int,
    "comments": int,
    "shares": int,
    "post_url": str,
    "scraped_at": str,  # ISO 8601
    "source": "playwright"
}
```

---

## Level 2: SerpAPI LinkedIn Search

### When to Use

Use SerpAPI when Playwright is blocked or cookies are not available. SerpAPI proxies
LinkedIn searches through Google Search, returning post snippets without authentication.

### Configuration

```python
SERPAPI_BASE_URL = "https://serpapi.com/search"
SERPAPI_ENGINE = "google"
SERPAPI_RATE_LIMIT_SECONDS = 1   # 1 second between requests
SERPAPI_MONTHLY_FREE_LIMIT = 100  # Free tier: 100 searches/month
```

### Environment Variables

```bash
SERPAPI_KEY=your_serpapi_key_here
```

### Search Query Template

```python
query = f'site:linkedin.com/posts "{keyword}" -inurl:jobs -inurl:company'
params = {
    "engine": "google",
    "q": query,
    "api_key": os.environ["SERPAPI_KEY"],
    "num": 10,
    "hl": "en",
    "gl": "us"
}
response = requests.get(SERPAPI_BASE_URL, params=params)
results = response.json().get("organic_results", [])
```

### Data Collected

SerpAPI returns snippets, not full post text. Normalize to the same schema:

```python
{
    "post_text": result.get("snippet", ""),   # truncated — typically 160 chars
    "author_name": extract_author(result.get("title", "")),
    "author_title": "",   # not available via SerpAPI
    "reactions": 0,       # not available via SerpAPI
    "comments": 0,        # not available via SerpAPI
    "shares": 0,          # not available via SerpAPI
    "post_url": result.get("link", ""),
    "scraped_at": datetime.utcnow().isoformat(),
    "source": "serpapi"
}
```

### Detection Triggers (fall to Level 3)

- `SERPAPI_KEY` environment variable not set
- SerpAPI returns `{"error": "Your account has run out of searches."}` (quota exhausted)
- HTTP 401 or 403 from SerpAPI
- `results` list is empty after query

---

## Level 3: Manual Paste

### When to Use

Use Manual Paste when both Playwright and SerpAPI are unavailable or have failed.
The skill prompts the user to paste LinkedIn post text directly into the conversation.

### Prompt to User

```
Automated LinkedIn scraping is currently unavailable.
Please paste one or more LinkedIn posts related to your topic below.
Format: paste the full post text, then type "---" on a new line to separate multiple posts.
```

### Data Collected

The skill parses pasted text blocks separated by `---`:

```python
{
    "post_text": pasted_block.strip(),
    "author_name": "manual_input",
    "author_title": "",
    "reactions": 0,
    "comments": 0,
    "shares": 0,
    "post_url": "",
    "scraped_at": datetime.utcnow().isoformat(),
    "source": "manual"
}
```

Manual paste data is still processed by the scoring model. Because engagement signals
are unavailable, `creator_engagement` defaults to 50 (neutral) for manual posts.

---

## Data Normalization Across Sources

All three sources produce data in the same normalized schema:

```python
NormalizedPost = {
    "post_text": str,          # Full or partial post text
    "author_name": str,        # Author display name or "manual_input"
    "author_title": str,       # Author job title (may be empty)
    "reactions": int,          # Total reactions count (0 if unknown)
    "comments": int,           # Total comments count (0 if unknown)
    "shares": int,             # Total shares count (0 if unknown)
    "post_url": str,           # Direct URL to post (may be empty)
    "scraped_at": str,         # ISO 8601 UTC timestamp
    "source": str              # "playwright" | "serpapi" | "manual"
}
```

When `reactions`, `comments`, or `shares` are 0 due to source limitations, the
scoring model reduces the `creator_engagement` component to its neutral baseline (50)
rather than penalizing with a 0.

---

## Fallback Detection Logic

```python
async def scrape_linkedin(keyword: str) -> list[NormalizedPost]:
    # Level 1: Playwright
    if cookies_available() and not playwright_blocked:
        try:
            posts = await scrape_with_playwright(keyword)
            if posts:
                return posts
        except (TimeoutError, BlockedError, CaptchaError):
            log.warning("Playwright blocked — falling to SerpAPI")

    # Level 2: SerpAPI
    if os.environ.get("SERPAPI_KEY") and not serpapi_quota_exhausted:
        try:
            posts = await scrape_with_serpapi(keyword)
            if posts:
                return posts
        except (QuotaError, AuthError):
            log.warning("SerpAPI unavailable — falling to manual paste")

    # Level 3: Manual paste
    return await prompt_manual_paste(keyword)
```
