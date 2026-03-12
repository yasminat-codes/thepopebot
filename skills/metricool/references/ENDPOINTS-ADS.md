# Ads Endpoints

Campaign performance for Facebook Ads, Google Ads, and TikTok Ads.

## Base URL

```
https://app.metricool.com/api
```

---

## Facebook Ads

### GET /stats/facebookads/campaigns

Get Facebook Ads campaigns with metrics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| sortcolumn | string | No | Column to sort by |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebookads/campaigns?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

**Response:**
```json
[
  {
    "id": "campaign_id",
    "name": "Campaign Name",
    "status": "active",
    "budget": 100.00,
    "spent": 85.50,
    "impressions": 50000,
    "clicks": 2500,
    "conversions": 125,
    "ctr": 5.0,
    "cpc": 0.034,
    "cpm": 1.71
  }
]
```

---

### GET /stats/facebookads/metricvalue

Get specific Facebook Ads metric value.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| metric | string | Yes | Metric name |
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| timezone | string | No | Timezone |
| idCampaign | string | No | Campaign ID filter |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebookads/metricvalue?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&metric=impressions&start=1704067200&end=1706745600"
```

---

### GET /stats/facebook/boost/{postId}

Boost a published Facebook post (create paid campaign).

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| postId | string | Yes | Path param: Post ID |
| budget | integer | Yes | Boost budget in cents |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebook/boost/123456789?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&budget=1000"
```

---

### GET /stats/facebook/boost/pending/{postId}

Add boost budget for a scheduled Facebook post.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| postId | string | Yes | Path param: Post ID |
| budget | integer | Yes | Boost budget |

---

### GET /stats/facebook/getvalue

Get boost budget for a scheduled post.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| postId | string | Yes | Post ID |

---

## Google Ads

### GET /stats/adwords/campaigns

Get Google Ads campaigns with metrics. (Deprecated — use `/stats/ads`)

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| sortcolumn | string | No | Column to sort by |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/adwords/campaigns?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/adwords/keywords

Get Google Ads keyword performance.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| sortcolumn | string | No | Column to sort by |
| CAMPAIGN | string | No | Campaign filter |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/adwords/keywords?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/ads

Get Google Ads list with metrics.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/ads?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## TikTok Ads

### GET /stats/tiktokads/campaigns

Get TikTok Ads campaigns with metrics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/tiktokads/campaigns?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

**Response:**
```json
[
  {
    "id": "campaign_id",
    "name": "Campaign Name",
    "status": "active",
    "budget": 100.00,
    "spent": 75.25,
    "impressions": 100000,
    "clicks": 5000,
    "conversions": 200
  }
]
```

---

## Common Metrics

| Metric | Description |
|--------|-------------|
| `impressions` | Number of times ads were shown |
| `clicks` | Number of clicks |
| `spent` | Amount spent |
| `budget` | Campaign budget |
| `ctr` | Click-through rate |
| `cpc` | Cost per click |
| `cpm` | Cost per 1000 impressions |
| `conversions` | Number of conversions |
| `roas` | Return on ad spend |

## Comparing Platforms

```bash
# Get Facebook Ads
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebookads/campaigns?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600" > fb_ads.json

# Get TikTok Ads
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/tiktokads/campaigns?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600" > tiktok_ads.json

# Compare
jq -s '.[0] + .[1]' fb_ads.json tiktok_ads.json
```
