# Integration Guide — LinkedIn Studio

> Setup instructions for every external service used by LinkedIn Studio. Follow each section to configure credentials and verify connectivity.

---

## 1. Neon PostgreSQL

**Used for:** Persistent storage across all skills -- topic bank, content queue, performance data, brand voice, hooks, pain points, trends, competitor data, AI blocklist.
**Skills that use it:** All 15 skills read from or write to Neon.

### Setup

1. Create a free Neon account at [neon.tech](https://neon.tech)
2. Create a new project (name: `linkedin-studio` or similar)
3. Copy the connection string from the Neon dashboard (use the pooled connection string for serverless)

### Environment Variable

```
NEON_DATABASE_URL=postgresql://user:password@ep-xxxxx.us-east-2.aws.neon.tech/linkedin_studio?sslmode=require
```

### Where to Set

Add to your Claude Code `settings.json` under the `env` key, or export in your shell profile.

### Initialize Schema

```bash
psql "$NEON_DATABASE_URL" -f .claude/skills/linkedin-studio/database/schema.sql
```

### Verify

```bash
psql "$NEON_DATABASE_URL" -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"
```

Expected: 10 tables listed (ai_phrases_blocklist, brand_voice_profile, competitor_tracker, content_queue, creator_posts_cache, hook_library, pain_points, post_performance, topic_bank, trends).

---

## 2. Metricool

**Used for:** Scheduling LinkedIn posts and pulling performance analytics.
**Skills that use it:** `ls:batch-scheduler`, `ls:analytics-dashboard`

### Setup

1. Create a Metricool account at [metricool.com](https://metricool.com)
2. Connect your LinkedIn profile in Metricool settings
3. Navigate to Settings > API to generate your API key
4. Your user ID is displayed on the same page

### Environment Variables

```
METRICOOL_API_KEY=your-api-key-here
METRICOOL_USER_ID=your-user-id-here
```

### Where to Set

Claude Code `settings.json` under the `env` key.

### Verify

```bash
curl -s -H "Authorization: Bearer $METRICOOL_API_KEY" \
  "https://app.metricool.com/api/v1/user/$METRICOOL_USER_ID/profile" | jq '.name'
```

Expected: Your Metricool account name returned.

---

## 3. Reddit (Pushshift + PRAW)

**Used for:** Extracting audience pain points from subreddits.
**Skills that use it:** `ls:pain-point-miner`

### Setup

1. Go to [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
2. Click "create another app" at the bottom
3. Select "script" as the app type
4. Set redirect URI to `http://localhost:8080`
5. Note the client ID (under the app name) and client secret

### Environment Variables

```
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
REDDIT_USERNAME=your-reddit-username
REDDIT_PASSWORD=your-reddit-password
```

### Where to Set

Claude Code `settings.json` under the `env` key.

### Verify

```python
import praw
reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    username="YOUR_USERNAME",
    password="YOUR_PASSWORD",
    user_agent="linkedin-studio/1.0"
)
print(reddit.user.me())
```

Expected: Your Reddit username printed.

---

## 4. SerpAPI

**Used for:** Searching LinkedIn creator profiles and posts when Playwright scraping is unavailable or blocked.
**Skills that use it:** `ls:creator-analyzer`, `ls:competitor-tracker`

### Setup

1. Create an account at [serpapi.com](https://serpapi.com)
2. Copy your API key from the dashboard
3. Free tier: 100 searches/month (sufficient for moderate use)

### Environment Variable

```
SERPAPI_KEY=your-serpapi-key-here
```

### Where to Set

Claude Code `settings.json` under the `env` key.

### Verify

```bash
curl -s "https://serpapi.com/account.json?api_key=$SERPAPI_KEY" | jq '.plan_name, .searches_remaining'
```

Expected: Your plan name and remaining search count.

---

## 5. Canva MCP

**Used for:** Creating LinkedIn carousel designs and single-image posts using Canva brand kits.
**Skills that use it:** `ls:canva-designer`

### Setup

1. Canva MCP is available as a Claude Code MCP integration
2. Ensure the Canva MCP server is configured in your Claude Code settings
3. Authenticate via OAuth when prompted on first use
4. Optionally set a default brand kit ID for consistent styling

### Environment Variable

```
CANVA_API_KEY=your-canva-api-key (if using direct API instead of MCP)
```

### Where to Set

For MCP integration: Configure in Claude Code MCP settings (no env var needed).
For direct API: Claude Code `settings.json` under the `env` key, or shell profile.

### Verify

Use the Claude Code MCP tool to list your Canva designs:
```
/ls:canva-design test
```

Expected: Canva MCP responds with design options or brand kit confirmation.

---

## 6. OpenAI (DALL-E)

**Used for:** Generating images from structured prompts for LinkedIn posts.
**Skills that use it:** `ls:visual-prompter`

### Setup

1. Get an API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Ensure your account has DALL-E API access enabled
3. Note: DALL-E 3 is recommended for quality; DALL-E 2 for speed/cost

### Environment Variable

```
OPENAI_API_KEY=sk-your-openai-key-here
```

### Where to Set

Claude Code `settings.json` under the `env` key.

### Verify

```bash
curl -s https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | jq '.data[] | select(.id | startswith("dall-e")) | .id'
```

Expected: `dall-e-2` and/or `dall-e-3` listed.

---

## 7. Google Trends (pytrends)

**Used for:** Surfacing trending keywords and related queries for content ideation.
**Skills that use it:** `ls:research-engine`

### Setup

No API key required. The `pytrends` Python library accesses Google Trends without authentication.

However, Google may rate-limit or block repeated requests from the same IP. A proxy is optional but recommended for heavy use.

### Environment Variable (Optional)

```
GOOGLE_TRENDS_PROXY=http://your-proxy:port
```

### Where to Set

Claude Code `settings.json` under the plugin environment block (only if using a proxy).

### Verify

```python
from pytrends.request import TrendReq
pytrends = TrendReq(hl='en-US', tz=360)
pytrends.build_payload(['AI agents'], timeframe='now 7-d')
df = pytrends.interest_over_time()
print(df.head())
```

Expected: A dataframe with interest-over-time values for "AI agents".

---

## 8. Playwright

**Used for:** Headless browser scraping of LinkedIn creator profiles (primary scraping method before SerpAPI fallback).
**Skills that use it:** `ls:creator-analyzer`, `ls:competitor-tracker`

### Setup

1. Install Playwright: `pip install playwright && playwright install chromium`
2. Playwright runs in headless mode by default
3. LinkedIn scraping may require authentication cookies or a logged-in browser context

### Environment Variables

```
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_TIMEOUT_MS=30000
```

### Where to Set

Claude Code `settings.json` under the `env` key.

### Verify

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.linkedin.com")
    print(page.title())
    browser.close()
```

Expected: "LinkedIn: Log In or Sign Up" (or similar LinkedIn page title).

---

## Fallback Chain

Several skills use a multi-step fallback strategy when a primary integration is unavailable:

```
ls:creator-analyzer / ls:competitor-tracker:
  1. Playwright (headless browser)  -->  if blocked/timeout
  2. SerpAPI (search API)           -->  if quota exhausted
  3. Manual input (user pastes post text)

ls:research-engine:
  1. Google Trends (pytrends)       -->  if rate-limited
  2. Reddit (PRAW)                  -->  always available as secondary signal
  3. Creator analysis (cached data) -->  fallback to existing creator_posts_cache

ls:visual-prompter:
  1. Canva MCP (design generation)  -->  if MCP unavailable
  2. DALL-E API (image generation)  -->  if quota exhausted
  3. Prompt-only output (JSON prompt returned for manual use)
```

---

## Quick Reference: All Environment Variables

| Variable                | Required | Used By                              |
|-------------------------|----------|--------------------------------------|
| `NEON_DATABASE_URL`     | Yes      | All skills                           |
| `METRICOOL_API_KEY`     | Yes*     | batch-scheduler, analytics-dashboard |
| `METRICOOL_USER_ID`     | Yes*     | batch-scheduler, analytics-dashboard |
| `REDDIT_CLIENT_ID`      | Yes*     | pain-point-miner                     |
| `REDDIT_CLIENT_SECRET`  | Yes*     | pain-point-miner                     |
| `REDDIT_USERNAME`       | Yes*     | pain-point-miner                     |
| `REDDIT_PASSWORD`       | Yes*     | pain-point-miner                     |
| `SERPAPI_KEY`           | Yes*     | creator-analyzer, competitor-tracker |
| `CANVA_API_KEY`         | No**     | canva-designer                       |
| `OPENAI_API_KEY`        | Yes*     | visual-prompter                      |
| `GOOGLE_TRENDS_PROXY`   | No       | research-engine                      |
| `PLAYWRIGHT_HEADLESS`   | No       | creator-analyzer, competitor-tracker |
| `PLAYWRIGHT_TIMEOUT_MS` | No       | creator-analyzer, competitor-tracker |

*Required only if using the skills that depend on this service. Core writing and humanization skills work without these.
**Not needed if using Canva via MCP integration (preferred method).
