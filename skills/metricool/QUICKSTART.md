# Metricool API Quick Start

Get up and running with Metricool API in 5 minutes.

## Step 1: Get Your Credentials

1. Log into Metricool
2. Go to **Account Settings → API tab**
3. Copy your:
   - **User Token** (API key)
   - **User ID**
   - **Blog ID** (brand ID, visible in browser URL when viewing a brand)

**Note:** API access requires Advanced or Custom plan.

## Step 2: Set Environment Variables

```bash
export METRICOOL_USER_TOKEN="your-token-from-settings"
export METRICOOL_USER_ID="your-user-id"
export METRICOOL_BLOG_ID="your-brand-id"
```

## Step 3: Test Your Setup

```bash
# Health check
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/mtr/ping"

# List all your brands
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

## Step 4: Get Analytics

```bash
# Instagram posts (last 30 days)
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=$(date -d '30 days ago' +%s)&end=$(date +%s)"

# Facebook posts
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebook/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=$(date -d '30 days ago' +%s)&end=$(date +%s)"

# Real-time stats
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/values?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

## Common Endpoints

| Task | Endpoint |
|------|----------|
| List brands | `/admin/simpleProfiles` |
| Instagram posts | `/stats/instagram/posts` |
| Instagram reels | `/stats/instagram/reels` |
| Facebook posts | `/stats/facebook/posts` |
| TikTok videos | `/stats/tiktok/videos` |
| YouTube videos | `/stats/youtube/videos` |
| LinkedIn posts | `/stats/linkedin/posts` |
| X posts | `/stats/twitter/posts` |
| Facebook Ads | `/stats/facebookads/campaigns` |
| Google Ads | `/stats/adwords/campaigns` |
| Real-time stats | `/stats/rt/values` |

## Date Format

All date parameters use **Unix timestamps** (seconds since epoch):

```bash
# Current timestamp
date +%s

# 30 days ago
date -d '30 days ago' +%s

# January 1, 2024
date -d '2024-01-01' +%s  # 1704067200
```

## Next Steps

- [Full endpoint documentation](references/ENDPOINTS-ANALYTICS.md)
- [Platform support matrix](references/PLATFORM-SUPPORT.md)
- [Ready-to-use scripts](scripts/)
