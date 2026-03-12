# REDDIT-INTEGRATION.md — Reddit API Integration Reference

## Overview

The research engine uses two Reddit data sources in a fallback chain:
1. **Pushshift** — no auth required, best for bulk historical search
2. **PRAW** — official Reddit API, requires credentials, best for real-time data

When both fail, the Reddit research step is skipped (not a blocking error).

---

## Pushshift

### Overview

Pushshift is a community-maintained Reddit archive API. It allows searching posts and
comments without authentication and supports high-volume queries.

### Base URL

```
https://api.pushshift.io
```

Store in environment:
```bash
PUSHSHIFT_BASE_URL=https://api.pushshift.io
```

### Authentication

None required. Pushshift is publicly accessible with no API key.

### Rate Limits

- **200 requests per minute** (observed practical limit)
- Add 0.3 second delay between requests to stay safely under limit
- No daily quota — limits are per-minute only

### Common Endpoints

#### Search submissions (posts)

```bash
GET /reddit/search/submission/?q={keyword}&subreddit={sub}&size=25&sort=score&after=30d
```

Parameters:

| Parameter   | Description                                            | Example              |
|-------------|--------------------------------------------------------|----------------------|
| `q`         | Search query                                           | `AI replacing jobs`  |
| `subreddit` | Subreddit name (no r/ prefix)                          | `Entrepreneur`       |
| `size`      | Number of results (max 100)                            | `25`                 |
| `sort`      | Sort order: `score`, `num_comments`, `created_utc`     | `score`              |
| `after`     | Time filter: `30d`, `7d`, `1y`                         | `30d`                |
| `score`     | Minimum score filter                                   | `>10`                |

```python
import requests
import os
import time

def pushshift_search(keyword: str, subreddit: str, limit: int = 25) -> list[dict]:
    base_url = os.environ.get("PUSHSHIFT_BASE_URL", "https://api.pushshift.io")
    url = f"{base_url}/reddit/search/submission/"
    params = {
        "q": keyword,
        "subreddit": subreddit,
        "size": limit,
        "sort": "score",
        "after": "30d"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    time.sleep(0.3)  # Rate limit buffer
    return response.json().get("data", [])
```

#### Search comments

```bash
GET /reddit/search/comment/?q={keyword}&subreddit={sub}&size=25&sort=score
```

Same parameters as submissions. Use comments to surface pain-point language.

---

## PRAW (Python Reddit API Wrapper)

### Overview

PRAW is the official Python Reddit API client. It provides real-time access to current
posts, comments, and search. Requires a Reddit developer application.

### Installation

```bash
pip install praw
```

### Environment Variables

```bash
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
REDDIT_USER_AGENT=linkedin-studio-research/1.0 by /u/your_reddit_username
```

### Application Setup

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" → select "script"
3. Set redirect URI to `http://localhost:8080`
4. Copy `client_id` (shown under app name) and `client_secret`

### Client Initialization

```python
import praw
import os

reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    username=os.environ["REDDIT_USERNAME"],
    password=os.environ["REDDIT_PASSWORD"],
    user_agent=os.environ["REDDIT_USER_AGENT"]
)
```

### Rate Limits

- **60 requests per minute** (enforced by Reddit OAuth)
- PRAW handles rate limiting automatically — it will sleep when limits are hit
- Do not add manual sleeps when using PRAW; it will delay unnecessarily

### Common Operations

#### Search a subreddit

```python
results = []
for post in reddit.subreddit("Entrepreneur").search(
    query="AI automation business",
    sort="top",
    time_filter="month",
    limit=25
):
    results.append({
        "title": post.title,
        "selftext": post.selftext,
        "score": post.score,
        "num_comments": post.num_comments,
        "url": post.url,
        "created_utc": post.created_utc
    })
```

#### Search across multiple subreddits

```python
# Combine multiple subreddits with '+'
combined = reddit.subreddit("Entrepreneur+smallbusiness+startups")
for post in combined.search("content marketing ROI", sort="top", limit=50):
    # process post
    pass
```

---

## Default Subreddits

The research engine searches these subreddits by default. All are relevant to the
LinkedIn Studio target audience (creators, consultants, founders, marketers).

| Subreddit         | Focus Area                                   |
|-------------------|----------------------------------------------|
| r/Entrepreneur    | Founder + business owner pain points         |
| r/smallbusiness   | SMB operational challenges                   |
| r/consulting      | Consultant-specific discussions              |
| r/startups        | Early-stage growth and strategy              |
| r/freelance       | Freelancer pain points and income            |
| r/marketing       | Marketing strategies and tactics             |
| r/artificial      | AI tools and automation discussions          |

To search all defaults at once with PRAW:
```python
DEFAULT_SUBREDDITS = "Entrepreneur+smallbusiness+consulting+startups+freelance+marketing+artificial"
```

---

## Fallback Chain Implementation

```python
async def search_reddit(keyword: str, limit_per_sub: int = 25) -> list[dict]:
    """
    Fallback chain: Pushshift → PRAW → skip
    Returns normalized post list.
    """
    subreddits = [
        "Entrepreneur", "smallbusiness", "consulting",
        "startups", "freelance", "marketing", "artificial"
    ]
    results = []

    # Level 1: Pushshift
    pushshift_ok = True
    try:
        for sub in subreddits:
            posts = pushshift_search(keyword, sub, limit=limit_per_sub)
            results.extend(normalize_pushshift(posts))
    except Exception as e:
        pushshift_ok = False
        log.warning(f"Pushshift unavailable: {e} — falling to PRAW")

    if results:
        return results

    # Level 2: PRAW
    praw_ok = all([
        os.environ.get("REDDIT_CLIENT_ID"),
        os.environ.get("REDDIT_CLIENT_SECRET"),
        os.environ.get("REDDIT_USERNAME"),
        os.environ.get("REDDIT_PASSWORD"),
    ])

    if praw_ok:
        try:
            reddit = praw.Reddit(
                client_id=os.environ["REDDIT_CLIENT_ID"],
                client_secret=os.environ["REDDIT_CLIENT_SECRET"],
                username=os.environ["REDDIT_USERNAME"],
                password=os.environ["REDDIT_PASSWORD"],
                user_agent=os.environ.get("REDDIT_USER_AGENT", "linkedin-studio/1.0")
            )
            combined_subs = "+".join(subreddits)
            for post in reddit.subreddit(combined_subs).search(keyword, sort="top", time_filter="month", limit=50):
                results.append(normalize_praw(post))
        except Exception as e:
            log.warning(f"PRAW unavailable: {e} — skipping Reddit research")
    else:
        log.info("PRAW credentials not set — skipping Reddit research")

    # Level 3: Skip (not a blocking error)
    if not results:
        log.info("Reddit research skipped — no data sources available")

    return results
```

---

## Data Normalization

Both Pushshift and PRAW results are normalized to the same schema before scoring:

```python
def normalize_pushshift(post: dict) -> dict:
    return {
        "title": post.get("title", ""),
        "body": post.get("selftext", ""),
        "score": post.get("score", 0),
        "num_comments": post.get("num_comments", 0),
        "subreddit": post.get("subreddit", ""),
        "url": f"https://reddit.com{post.get('permalink', '')}",
        "created_utc": post.get("created_utc", 0),
        "source": "pushshift"
    }

def normalize_praw(post) -> dict:
    return {
        "title": post.title,
        "body": post.selftext,
        "score": post.score,
        "num_comments": post.num_comments,
        "subreddit": str(post.subreddit),
        "url": post.url,
        "created_utc": post.created_utc,
        "source": "praw"
    }
```

---

## Pain Keyword Detection

After fetching posts, scan for pain language to contribute to `pain_intensity` scoring:

```python
PAIN_KEYWORDS = [
    "struggling", "frustrated", "problem", "help", "anyone else",
    "how do I", "failing", "can't figure out", "stuck", "overwhelmed",
    "burning out", "nobody talks about", "myth", "truth about",
    "why doesn't", "am I the only one", "does anyone", "advice needed",
    "driving me crazy", "can't believe", "nightmare", "disaster",
    "gave up", "quit", "exhausted", "no one tells you"
]

def count_pain_words(text: str) -> int:
    text_lower = text.lower()
    return sum(1 for kw in PAIN_KEYWORDS if kw in text_lower)
```
