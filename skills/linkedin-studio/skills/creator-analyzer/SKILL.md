---
name: ls:creator-analyzer
description: >
  PROACTIVELY scrapes and analyzes LinkedIn creator posts to extract winning content
  patterns, high-engagement hooks, and CTA structures for AI consulting niches.
  Triggers on creator URL inputs, competitor benchmarking requests, hook inspiration
  tasks, LinkedIn content gap analysis, and post structure research. Uses a
  3-fallback chain (Playwright → SerpAPI → manual paste) to maximize data collection
  reliability. Stores structured analysis in Neon creator_posts_cache and returns
  actionable pattern reports for content generation.
model: sonnet
context: fork
allowed-tools: Bash Read Write WebFetch WebSearch
hooks:
  PreToolUse:
    - validate_creator_inputs
  PostToolUse:
    - log_scrape_result
  Stop:
    - confirm_cache_write
metadata:
  version: "2.0.0"
---

# ls:creator-analyzer

Scrapes LinkedIn creator posts and extracts the patterns behind top-performing content.
Filters for the top 20% of posts by engagement. Outputs an actionable insight report
saved to Neon `creator_posts_cache`.

→ See references/SCRAPING-STRATEGY.md for full fallback chain configuration
→ See references/NEON-SCHEMA.md for creator_posts_cache table structure
→ See references/PATTERN-TAXONOMY.md for hook type and CTA format classifications

---

## Phase 1: Input Creator URLs or Names

**Accepted inputs:**
- Direct LinkedIn profile URLs: `https://www.linkedin.com/in/username/`
- Creator names (fuzzy-matched against stored cache first)
- Comma-separated list of up to 20 creators
- Niche keyword — auto-discovers top 10 creators via SerpAPI

**Validation:**
- At least 1 creator URL or name required
- Strip trailing slashes and normalize URL format
- If name provided without URL, attempt SerpAPI lookup before scraping

```python
def normalize_profile_url(raw: str) -> str:
    """Normalize LinkedIn URL to consistent format."""
    raw = raw.strip().rstrip('/')
    if not raw.startswith('https://www.linkedin.com/in/'):
        raise ValueError(f"Invalid LinkedIn URL: {raw}")
    return raw
```

**Cache check:** Before any scraping, query Neon `creator_posts_cache` for existing
data younger than 24 hours. Return cached results if available to avoid redundant requests.

---

## Phase 2: Scrape Posts (3-Fallback Chain)

Attempt each method in order. Move to next fallback only on failure.

### Method 1 — Playwright (Primary, no subscription required)
```python
from playwright.async_api import async_playwright

async def scrape_with_playwright(profile_url: str) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Navigate to creator's recent activity feed
        activity_url = f"{profile_url}recent-activity/shares/"
        await page.goto(activity_url, wait_until='networkidle')
        await page.wait_for_selector('[data-urn*="share"]', timeout=10000)
        posts = await page.query_selector_all('[data-urn*="share"]')
        return [await extract_post_data(post) for post in posts]
```
- Extracts: post text, reaction count, comment count, share count, post URL, date
- Rate limiting: 2-second delay between profiles, max 5 concurrent sessions
- On block/CAPTCHA: immediately fall to Method 2

### Method 2 — SerpAPI LinkedIn Search (Fallback 1)
```python
import requests

def scrape_with_serpapi(creator_name: str, api_key: str) -> list[dict]:
    params = {
        "engine": "google",
        "q": f'site:linkedin.com/posts "{creator_name}"',
        "api_key": api_key,
        "num": 20
    }
    resp = requests.get("https://serpapi.com/search", params=params)
    results = resp.json().get("organic_results", [])
    return [parse_serpapi_result(r) for r in results]
```
- Note: SerpAPI returns limited metadata (no reaction counts); engagement estimated
  from snippet length and keyword signals
- Cost: counts against SerpAPI quota — use sparingly
- On API key missing or quota exceeded: fall to Method 3

### Method 3 — Manual Paste (Fallback 2)
```
SCRAPING BLOCKED for: {creator_url}

Manual collection required:
1. Open {creator_url}/recent-activity/shares/ in your browser
2. Copy the page source or paste the visible post text below
3. Format: one post per block, separated by "---"

Paste posts here and type DONE when finished:
```
- Parse pasted content using pattern matching for text, approximate engagement signals
- Flag all manually-collected posts with `source: manual_paste` in cache

→ See references/SCRAPING-STRATEGY.md for Playwright session management and anti-detection headers

---

## Phase 3: Filter Top Performers (Top 20% by Engagement)

Calculate engagement score for each collected post:
```python
def engagement_score(post: dict) -> float:
    reactions = post.get('reactions', 0)
    comments = post.get('comments', 0)
    shares = post.get('shares', 0)
    # Comments weighted 3x (highest intent signal)
    return reactions + (comments * 3) + (shares * 2)
```

Filter steps:
1. Remove posts with fewer than 3 data points (likely scraping artifacts)
2. Calculate 80th percentile threshold across all posts collected
3. Keep only posts at or above threshold
4. Minimum floor: always keep at least 3 posts per creator even if all underperform

---

## Phase 4: Extract Patterns

For each top-performing post, classify and extract:

**Hook type classification:**
- `question_hook` — Opens with a question ("Why are most AI implementations failing?")
- `stat_hook` — Opens with a number or data point ("87% of AI projects never ship")
- `contrarian_hook` — Challenges common belief ("Cold outreach is not dead")
- `story_hook` — Opens with "I" + personal narrative
- `list_hook` — Opens with a count ("5 things I learned...")
- `pain_hook` — Opens by naming a pain ("Struggling to explain AI ROI to clients?")

**Structural patterns extracted:**
- Hook length in words (first sentence)
- Post length in words (total)
- Paragraph count and avg paragraph length
- Presence of line breaks / white space formatting
- Emoji usage (count and position)
- CTA type: `comment_prompt`, `dm_offer`, `link_drop`, `tag_someone`, `none`
- Hashtag count and placement (inline vs end)

**Aggregate summary per creator:**
```python
patterns = {
    "top_hook_types": Counter(hook_types).most_common(3),
    "avg_word_count": mean(word_counts),
    "avg_paragraph_count": mean(para_counts),
    "dominant_cta": Counter(cta_types).most_common(1)[0],
    "emoji_usage": "heavy" | "moderate" | "minimal" | "none",
    "posting_time_pattern": extracted_from_timestamps
}
```

→ See references/PATTERN-TAXONOMY.md for full classification rules and examples

---

## Phase 5: Save to Neon creator_posts_cache

```sql
INSERT INTO creator_posts_cache (
  cache_id, creator_url, creator_name, post_url,
  post_text, engagement_score, reactions, comments, shares,
  hook_type, cta_type, word_count, post_date,
  scrape_source, scraped_at
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, NOW())
ON CONFLICT (post_url) DO UPDATE
  SET engagement_score = EXCLUDED.engagement_score,
      scraped_at = NOW();
```

Also upsert the aggregated pattern summary:
```sql
INSERT INTO creator_posts_cache (
  cache_id, creator_url, is_summary_row, pattern_json, updated_at
) VALUES ($1, $2, TRUE, $3, NOW())
ON CONFLICT (creator_url, is_summary_row) DO UPDATE
  SET pattern_json = EXCLUDED.pattern_json,
      updated_at = NOW();
```

→ See references/NEON-SCHEMA.md for full creator_posts_cache DDL

---

## Phase 6: Return Insight Report

```
CREATOR ANALYSIS COMPLETE

CREATORS ANALYZED: {N}
POSTS COLLECTED: {total} total, {top_performers} top performers (top 20%)
SCRAPE METHODS: Playwright {p_count}, SerpAPI {s_count}, Manual {m_count}

TOP PERFORMING HOOK TYPES:
  1. {hook_type} — {count} posts, avg engagement {score}
  2. {hook_type} — {count} posts, avg engagement {score}
  3. {hook_type} — {count} posts, avg engagement {score}

STRUCTURAL PATTERNS:
  Average post length: {N} words
  Optimal paragraph count: {N}
  Dominant CTA format: {cta_type}
  Emoji strategy: {usage_level}

TOP 3 HOOKS TO STEAL (adapted):
  1. "{adapted_hook}" (from {creator}, {engagement_score} engagement)
  2. "{adapted_hook}" (from {creator}, {engagement_score} engagement)
  3. "{adapted_hook}" (from {creator}, {engagement_score} engagement)

CACHE: {new} new posts stored, {updated} updated, {skipped} skipped (cached <24h)
NEXT: Pass patterns to ls:content-writer or ls:idea-bank
```

---

## Error Handling

| Error | Recovery |
|---|---|
| Playwright install missing | `npx playwright install chromium` and retry |
| LinkedIn login wall | Switch to SerpAPI fallback immediately |
| SerpAPI quota exhausted | Log warning, proceed with manual paste for remaining creators |
| Zero posts collected | Return empty result with explicit message; do not write to Neon |
| Neon write failure | Retry 3x (2s, 4s, 8s); log warning and return in-memory results |

All errors logged with `[creator-analyzer][ERROR]` prefix.

---

## References

- `references/SCRAPING-STRATEGY.md` — Playwright config, anti-detection, session management
- `references/NEON-SCHEMA.md` — creator_posts_cache DDL and indexes
- `references/PATTERN-TAXONOMY.md` — Hook type and CTA classification rules with examples
