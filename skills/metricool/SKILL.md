---
name: metricool
description: Complete Metricool API integration for social media analytics, ads management, content scheduling, and reporting. Use when working with Metricool, social media analytics, cross-platform metrics, Instagram/Facebook/TikTok/YouTube/LinkedIn/X analytics, ad campaigns, or post scheduling. Requires METRICOOL_USER_TOKEN, METRICOOL_USER_ID, METRICOOL_BLOG_ID.
allowed-tools: Read Write Bash(curl:*) Bash(jq:*)
metadata: {"clawdbot":{"requires":{"env":["METRICOOL_USER_TOKEN","METRICOOL_USER_ID","METRICOOL_BLOG_ID"],"bins":["curl","jq"]},"primaryEnv":"METRICOOL_USER_TOKEN","emoji":"📊","homepage":"https://metricool.com"}}
---

# Metricool API Integration

Complete wrapper for Metricool's 100+ API endpoints across social media analytics, ads management, content scheduling, and reporting.

## When to Use This Skill

Use when users request:
- Social media analytics (Instagram, Facebook, TikTok, YouTube, LinkedIn, X, Pinterest, Twitch, Bluesky, Threads)
- Ad campaign performance (Facebook Ads, Google Ads, TikTok Ads)
- Post scheduling and content planning
- Competitor analysis across platforms
- Report generation and templates
- Link in Bio management
- Real-time analytics and visitor tracking

## Prerequisites

- [ ] Metricool Advanced or Custom plan (API access required)
- [ ] API token from Account Settings → API tab
- [ ] Environment variables configured

**→ Full setup guide: [references/API-AUTHENTICATION.md](references/API-AUTHENTICATION.md)**

## Quick Start

```bash
# Set environment variables
export METRICOOL_USER_TOKEN="your-token-from-settings"
export METRICOOL_USER_ID="your-user-id"
export METRICOOL_BLOG_ID="your-brand-id"

# Get all your brands
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# Get Instagram posts analytics
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

**→ Quick start guide: [QUICKSTART.md](QUICKSTART.md)**

## Authentication

All Metricool API calls require **3 parameters**:

| Parameter | Location | Description |
|-----------|----------|-------------|
| `userToken` | Header `X-Mc-Auth` | API token from Account Settings → API tab |
| `userId` | Query param | User identifier for Metricool account |
| `blogId` | Query param | Brand identification number (in browser URL) |

**Base URL:** `https://app.metricool.com/api`

**→ Full authentication details: [references/API-AUTHENTICATION.md](references/API-AUTHENTICATION.md)**

## Endpoint Categories

### Admin & Profiles

Brand management, profile CRUD, account settings.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/admin/simpleProfiles` | GET | List all user brands |
| `/admin/profiles-auth` | GET | Authenticated user brands |
| `/admin/add-profile` | GET | Create new profile |
| `/admin/delete-profile` | GET | Remove current brand |
| `/admin/restore-profile` | GET | Restore deleted brand |

**→ All admin endpoints: [references/ENDPOINTS-ADMIN.md](references/ENDPOINTS-ADMIN.md)**

### Analytics (Multi-Platform)

Retrieve performance metrics for all connected social platforms.

| Platform | Endpoints | Key Metrics |
|----------|-----------|-------------|
| Instagram | `/stats/instagram/posts`, `/stats/instagram/reels`, `/stats/instagram/stories` | Likes, comments, saves, reach |
| Facebook | `/stats/facebook/posts`, `/stats/fbgroup/posts` | Engagement, reach, shares |
| TikTok | `/stats/tiktok/videos` | Views, likes, shares, comments |
| YouTube | `/stats/youtube/videos` | Views, watch time, subscribers |
| LinkedIn | `/stats/linkedin/posts` | Impressions, clicks, engagement |
| X (Twitter) | `/stats/twitter/posts`, `/stats/rt/twitter/tweets/{type}` | Impressions, retweets, likes |
| Pinterest | Via `/stats/timeline/{metric}` | Saves, impressions, clicks |
| Twitch | `/stats/twitch/videos`, `/stats/twitch/clips` | Views, clips, subscriptions |
| Bluesky | Via `/stats/bluesky/posts` | Likes, reposts, replies |
| Threads | Via `/stats/threads/posts` | Likes, quotes, replies |

**→ All analytics endpoints: [references/ENDPOINTS-ANALYTICS.md](references/ENDPOINTS-ANALYTICS.md)**
**→ Platform support matrix: [references/PLATFORM-SUPPORT.md](references/PLATFORM-SUPPORT.md)**

### Ads Management

Campaign performance for Facebook Ads, Google Ads, TikTok Ads.

| Endpoint | Purpose |
|----------|---------|
| `/stats/facebookads/campaigns` | Facebook Ads campaigns with metrics |
| `/stats/facebookads/metricvalue` | Specific metric values |
| `/stats/adwords/campaigns` | Google Ads campaigns (deprecated) |
| `/stats/adwords/keywords` | Google Ads keyword performance |
| `/stats/tiktokads/campaigns` | TikTok Ads campaigns |

**→ All ads endpoints: [references/ENDPOINTS-ADS.md](references/ENDPOINTS-ADS.md)**

### Content & Engagement

Post management, comments, likes, competitor analysis.

| Endpoint | Purpose |
|----------|---------|
| `/stats/postmessage/{provider}` | Post message or comment |
| `/stats/deletecomment/{provider}` | Delete comment |
| `/stats/postlike/{provider}` | Like/unlike comment |
| `/stats/network_competitors` | List competitors |
| `/stats/network_competitors_posts` | Competitor post analysis |

**→ All content endpoints: [references/ENDPOINTS-CONTENT.md](references/ENDPOINTS-CONTENT.md)**

### Scheduling & Planner

Post scheduling, hashtag suggestions, best time to post.

| Endpoint | Purpose |
|----------|---------|
| `/actions/setTimeZone` | Define user timezone |
| `/actions/instagram/suggestions/hashtags` | Instagram hashtag suggestions |
| `/actions/twitter/suggestions` | Twitter account suggestions |
| `/actions/linkedin/suggestions` | LinkedIn company suggestions |
| `/actions/facebook/suggestions` | Facebook page suggestions |
| `/actions/bluesky/suggestions` | Bluesky account suggestions |

**→ All scheduling endpoints: [references/ENDPOINTS-SCHEDULING.md](references/ENDPOINTS-SCHEDULING.md)**

### Reports

Template management, logo customization, PDF generation.

| Endpoint | Purpose |
|----------|---------|
| `/stats/report/savetemplate` | Save report template |
| `/stats/report/deletetemplate` | Delete template |
| `/stats/report/duplicatetemplate` | Duplicate template |
| `/stats/report/reporttemplateName` | List all templates |
| `/stats/report/updatereportlogo` | Save logo for report |

**→ All report endpoints: [references/ENDPOINTS-REPORTS.md](references/ENDPOINTS-REPORTS.md)**

### Link in Bio

Instagram bio link management (catalogs, buttons, images).

| Endpoint | Purpose |
|----------|---------|
| `/linkinbio/instagram/getbiocatalog` | Get bio link contents |
| `/linkinbio/instagram/addcatalogitems` | Add pictures to bio link |
| `/linkinbio/instagram/addcatalogButton` | Add button to bio link |
| `/linkinbio/instagram/editcatalogbutton` | Update button |
| `/linkinbio/instagram/deletecatalogitem` | Delete item from bio |

**→ All Link in Bio endpoints: [references/ENDPOINTS-LINKINBIO.md](references/ENDPOINTS-LINKINBIO.md)**

### Real-Time Analytics

Live visitor tracking and current session data.

| Endpoint | Purpose |
|----------|---------|
| `/stats/rt/values` | Today's page views, visits, visitors |
| `/stats/rt/pvperhour` | Page views per hour distribution |
| `/stats/rt/sessions` | Real-time visit list |
| `/stats/rt/distribution/{type}` | Visit distribution by type |

**→ All real-time endpoints: [references/ENDPOINTS-REALTIME.md](references/ENDPOINTS-REALTIME.md)**

### Google My Business

GMB reviews and media management.

| Endpoint | Purpose |
|----------|---------|
| `/stats/gmb/review` | GMB reviews with metrics |
| `/stats/gmb/reviewbyid` | Get specific review |
| `/stats/gmb/review/reply` | Reply to review |
| `/stats/gmb/media/{type}` | GMB media |

**→ All GMB endpoints: [references/ENDPOINTS-GMB.md](references/ENDPOINTS-GMB.md)**

## Decision Trees

**If** retrieving analytics for a single platform → **Use** platform-specific endpoint | Medium freedom
- Instagram: `/stats/instagram/posts`, `/stats/instagram/reels`, `/stats/instagram/stories`
- Facebook: `/stats/facebook/posts`
- TikTok: `/stats/tiktok/videos`
- YouTube: `/stats/youtube/videos`
- See: [references/ENDPOINTS-ANALYTICS.md](references/ENDPOINTS-ANALYTICS.md)

**If** comparing metrics across multiple platforms → **Use** `/stats/aggregations/{category}` or `/stats/timeline/{metric}` | High freedom
- Category-based aggregation for cross-platform comparison
- Time series data for trends
- See: [references/ENDPOINTS-ANALYTICS.md](references/ENDPOINTS-ANALYTICS.md)

**If** managing ad campaigns → **Use** ads endpoints by platform | Low freedom
- Facebook Ads: `/stats/facebookads/campaigns`
- Google Ads: `/stats/adwords/campaigns`
- TikTok Ads: `/stats/tiktokads/campaigns`
- See: [references/ENDPOINTS-ADS.md](references/ENDPOINTS-ADS.md)

**If** scheduling posts or finding best times → **Use** `/actions/*` endpoints | Medium freedom
- Hashtag suggestions: `/actions/instagram/suggestions/hashtags`
- Account suggestions: `/actions/{platform}/suggestions`
- Timezone: `/actions/setTimeZone`
- See: [references/ENDPOINTS-SCHEDULING.md](references/ENDPOINTS-SCHEDULING.md)

**If** building automated workflows → **Use** [scripts/](scripts/) | Low freedom
- Pre-built bash scripts for common operations
- Deterministic execution with error handling
- See: [scripts/](scripts/)

## Real-World Scenarios

### Scenario 1: Instagram Performance Report
**Input:** "Get my Instagram post performance for January 2024"
**Process:**
  1. Convert dates to Unix timestamps (Jan 1 = 1704067200, Jan 31 = 1706745600)
  2. Call `/stats/instagram/posts` with date range
  3. Parse response for key metrics (likes, comments, saves, reach)
**Output:** JSON array of posts with engagement metrics
**Resources used:** [ENDPOINTS-ANALYTICS.md](references/ENDPOINTS-ANALYTICS.md), [metricool-request.sh](scripts/metricool-request.sh)

### Scenario 2: Cross-Platform Ad Campaign Analysis
**Input:** "Compare my Facebook and TikTok ad performance this month"
**Process:**
  1. Call `/stats/facebookads/campaigns` for Facebook data
  2. Call `/stats/tiktokads/campaigns` for TikTok data
  3. Compare metrics (spend, impressions, clicks, conversions)
**Output:** Comparative analysis of ad performance across platforms
**Resources used:** [ENDPOINTS-ADS.md](references/ENDPOINTS-ADS.md), [get-analytics.sh](scripts/get-analytics.sh)

### Scenario 3: Schedule Post with Best Time
**Input:** "When's the best time to post on Instagram this week?"
**Process:**
  1. Analyze historical engagement patterns
  2. Call `/actions/instagram/suggestions/hashtags` for relevant tags
  3. Check `/stats/instagram/posts` for past high-performing post times
**Output:** Recommended posting times with hashtag suggestions
**Resources used:** [ENDPOINTS-SCHEDULING.md](references/ENDPOINTS-SCHEDULING.md), [schedule-post.sh](scripts/schedule-post.sh)

## Error Handling

| Error Code | Description | Solution |
|------------|-------------|----------|
| 401 | Unauthorized | Verify METRICOOL_USER_TOKEN is correct |
| 403 | Forbidden | Check API access (Advanced/Custom plan required) |
| 404 | Not Found | Verify userId and blogId are correct |
| 429 | Rate Limited | Implement exponential backoff |
| 500 | Server Error | Retry with backoff, check Metricool status |

**→ Full error codes: [references/ERROR-CODES.md](references/ERROR-CODES.md)**
**→ Troubleshooting: [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)**

## Resilience Features

This skill implements production-grade resilience:

| Feature | Description |
|---------|-------------|
| **Automatic Retries** | Exponential backoff (1s → 60s) for transient failures |
| **Rate Limit Handling** | Proactive waiting based on `X-RateLimit-*` headers |
| **Circuit Breaker** | Fail fast after 5 consecutive failures, auto-recovery |
| **Response Caching** | 30s-24h TTL based on data type |
| **Error Recovery** | Graceful degradation with detailed error types |

### Python Client (Recommended)

```python
from metricool_client import MetricoolClient

client = MetricoolClient(
    user_token="...",
    user_id="...",
    blog_id="..."
)

# Automatic retries, caching, circuit breaker built-in
posts = client.instagram.get_posts(start=1704067200, end=1706745600)

# Check client health
stats = client.get_stats()
print(f"Requests: {stats['requests']}, Cache hits: {stats['cache_hits']}")
```

**→ Full resilience guide: [references/RESILIENCE.md](references/RESILIENCE.md)**

### Bash Wrapper (Resilient)

```bash
# Uses built-in retries, caching, circuit breaker
./scripts/metricool-resilient.sh get "stats/instagram/posts" "start=1704067200&end=1706745600"

# Check client statistics
./scripts/metricool-resilient.sh stats

# Clear cache
./scripts/metricool-resilient.sh clear-cache
```

**→ Complete endpoint reference: [references/ENDPOINTS-COMPLETE.md](references/ENDPOINTS-COMPLETE.md)**

## Rate Limits

- API access requires Advanced or Custom plan
- Rate limits visible in Account Settings → API tab
- Client automatically handles `429` responses with `Retry-After`

**→ Rate limit details: [references/RATE-LIMITS.md](references/RATE-LIMITS.md)**

## Scripts

| Script | Purpose | Resilience |
|--------|---------|------------|
| [metricool-resilient.sh](scripts/metricool-resilient.sh) | Production API wrapper | ✓ Retries, cache, circuit breaker |
| [metricool_client.py](scripts/metricool_client.py) | Python client library | ✓ Full resilience |
| [metricool-request.sh](scripts/metricool-request.sh) | Basic request wrapper | Basic retry |
| [get-brands.sh](scripts/get-brands.sh) | List all user brands | ✓ |
| [get-analytics.sh](scripts/get-analytics.sh) | Fetch analytics by platform | ✓ |

## Assets

| Asset | Purpose |
|-------|---------|
| [curl-collection.json](assets/curl-collection.json) | Importable Postman/Insomnia collection |
| [config-template.yaml](assets/config-template.yaml) | Environment configuration template |
| [response-schemas.json](assets/schemas/response-schemas.json) | Response structure documentation |

## Resource Reference Map

| Situation | Reference | Purpose |
|-----------|-----------|---------|
| Setting up authentication | [API-AUTHENTICATION.md](references/API-AUTHENTICATION.md) | Token setup, required params |
| Complete endpoint list | [ENDPOINTS-COMPLETE.md](references/ENDPOINTS-COMPLETE.md) | All 100+ endpoints with retry/cache |
| Admin/profile management | [ENDPOINTS-ADMIN.md](references/ENDPOINTS-ADMIN.md) | Brand CRUD operations |
| Social media analytics | [ENDPOINTS-ANALYTICS.md](references/ENDPOINTS-ANALYTICS.md) | All analytics endpoints |
| Ad campaign data | [ENDPOINTS-ADS.md](references/ENDPOINTS-ADS.md) | Facebook/Google/TikTok ads |
| Content management | [ENDPOINTS-CONTENT.md](references/ENDPOINTS-CONTENT.md) | Posts, comments, engagement |
| Scheduling/planning | [ENDPOINTS-SCHEDULING.md](references/ENDPOINTS-SCHEDULING.md) | Post scheduling, suggestions |
| Report generation | [ENDPOINTS-REPORTS.md](references/ENDPOINTS-REPORTS.md) | Templates, logos, PDF |
| Link in Bio management | [ENDPOINTS-LINKINBIO.md](references/ENDPOINTS-LINKINBIO.md) | Instagram bio toolkit |
| Real-time data | [ENDPOINTS-REALTIME.md](references/ENDPOINTS-REALTIME.md) | Live visitor tracking |
| Google My Business | [ENDPOINTS-GMB.md](references/ENDPOINTS-GMB.md) | Reviews, media, replies |
| Platform capabilities | [PLATFORM-SUPPORT.md](references/PLATFORM-SUPPORT.md) | Platform support matrix |
| Resilience patterns | [RESILIENCE.md](references/RESILIENCE.md) | Retries, caching, circuit breaker |
| Debugging issues | [TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) | Common problems & fixes |
| Error codes | [ERROR-CODES.md](references/ERROR-CODES.md) | All error codes & meanings |
| Rate limiting | [RATE-LIMITS.md](references/RATE-LIMITS.md) | Limits & backoff strategies |
| Python client | [metricool_client.py](scripts/metricool_client.py) | Production-grade client |
| Bash wrapper | [metricool-resilient.sh](scripts/metricool-resilient.sh) | Resilient API wrapper |
| Importing to API client | [curl-collection.json](assets/curl-collection.json) | Postman/Insomnia collection |
