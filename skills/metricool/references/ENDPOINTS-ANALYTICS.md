# Analytics Endpoints

Multi-platform analytics for Instagram, Facebook, TikTok, YouTube, LinkedIn, X, Pinterest, Twitch, Bluesky, and Threads.

## Base URL

```
https://app.metricool.com/api
```

## Date Parameters

Most analytics endpoints use Unix timestamps:

| Parameter | Type | Description |
|-----------|------|-------------|
| `start` | integer | Start date (Unix timestamp) |
| `end` | integer | End date (Unix timestamp) |
| `sortcolumn` | string | Column to sort by (optional) |

```bash
# Current timestamp
date +%s

# 30 days ago
date -d '30 days ago' +%s

# January 1, 2024
date -d '2024-01-01' +%s  # 1704067200
```

---

## Instagram Analytics

### GET /stats/instagram/posts

Get Instagram posts with metrics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| sortcolumn | string | No | Sort column (e.g., "likes") |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

**Response:**
```json
[
  {
    "id": "post_id",
    "caption": "Post caption...",
    "mediaType": "IMAGE",
    "mediaUrl": "https://...",
    "timestamp": 1704067200,
    "likes": 150,
    "comments": 12,
    "saves": 25,
    "reach": 5000,
    "impressions": 7500
  }
]
```

---

### GET /stats/instagram/reels

Get Instagram Reels with metrics.

**Parameters:** Same as posts

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/reels?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/instagram/stories

Get Instagram Stories with metrics.

**Parameters:** Same as posts

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/stories?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

## Facebook Analytics

### GET /stats/facebook/posts

Get Facebook page posts with metrics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | string | Yes | Start timestamp |
| end | string | Yes | End timestamp |
| sortcolumn | string | No | Sort column |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebook/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/fbgroup/posts

Get Facebook group posts with metrics.

**Parameters:** Same as Facebook posts

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/fbgroup/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/facebook/reels

Get Facebook Reels with metrics.

**Parameters:** Same as posts

---

### GET /stats/facebook/stories

Get Facebook Stories with metrics.

**Parameters:** Same as posts

---

## TikTok Analytics

### GET /stats/tiktok/videos

Get TikTok videos with metrics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| sortcolumn | string | No | Sort column |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/tiktok/videos?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

## YouTube Analytics

### GET /stats/youtube/videos

Get YouTube videos with metrics.

**Metrics:** views, watch time, subscribers, likes, dislikes, estimated revenue

**Parameters:** Same as TikTok

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/youtube/videos?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

## LinkedIn Analytics

### GET /stats/linkedin/posts

Get LinkedIn posts with metrics.

**Metrics:** impressions, clicks, engagement rate

**Parameters:** Same as Facebook

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/linkedin/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/linkedin/stories

Get LinkedIn stories with metrics.

**Parameters:** Same as posts

---

## X (Twitter) Analytics

### GET /stats/twitter/posts

Get X/Twitter posts with metrics. (Deprecated)

**Metrics:** impressions, retweets, likes, replies

**Parameters:** Same as TikTok

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/twitter/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/twEvents/{type}

Get Twitter follow/unfollow events.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | Yes | Path param: "follow" or "unfollow" |
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/twEvents/follow?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

## Pinterest Analytics

Pinterest metrics available via `/stats/timeline/{metric}` with `pinterestEngagement` metric.

---

## Twitch Analytics

### GET /stats/twitch/videos

Get Twitch videos with metrics.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/twitch/videos?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/twitch/clips

Get Twitch clips from a specific video.

**Parameters:** start, end, sortcolumn

---

### GET /stats/twitch/video/clips

Get clips from a Twitch channel.

---

### GET /stats/twitch/subscriptions

Get Twitch channel subscriptions.

**Parameters:** start, end, sortcolumn

---

### GET /stats/twitch/subscriptions/doughnut

Get subscriber distribution by type.

---

## Bluesky Analytics

Available via `/stats/bluesky/posts` with standard parameters.

---

## Threads Analytics

Available via `/stats/threads/posts` with standard parameters.

---

## Demographics

### GET /stats/gender/{provider}

Get followers distribution by gender.

**Path param:** provider (instagram, facebook, etc.)

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gender/instagram?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### GET /stats/gender-age/{provider}

Get followers by gender and age.

---

### GET /stats/age/{provider}

Get age distribution.

---

### GET /stats/country/{provider}

Get country distribution.

---

### GET /stats/city/{provider}

Get city distribution.

---

## Aggregated Metrics

### GET /stats/values/{category}

Get metrics for a specific category and date.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| category | string | Yes | Path param: metric category |
| date | string | Yes | Date string |

---

### GET /stats/timeline/{metric}

Get time series data for a metric.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| metric | string | Yes | Path param: metric name |
| start | string | Yes | Start timestamp |
| end | string | Yes | End timestamp |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/timeline/instagramEngagement?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

### GET /stats/aggregation/{metric}

Get aggregated engagement metric.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| metric | string | Yes | Path param: metric name |
| start | string | Yes | Start timestamp |
| end | string | Yes | End timestamp |
| igcompetitorid | string | No | Competitor ID for comparison |

---

### GET /stats/aggregations/{category}

Get aggregated metrics by category.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| category | string | Yes | Path param: category name |
| start | string | Yes | Start timestamp |
| end | string | Yes | End timestamp |
| campaignid | string | No | Campaign ID filter |

---

### GET /stats/distribution/{type}

Get visit distribution by geography/referrer.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | Yes | Path param: distribution type |
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |

---

## Traffic Sources

### GET /stats/trafficsource/{provider}

Get traffic source distribution.

**Path param:** provider (instagram, facebook, etc.)

---

## Post Types

### GET /stats/{provider}/posts/types

Get posts grouped by type.

**Path param:** provider (instagram, facebook, etc.)

**Parameters:** start, end

---

## Website Posts

### GET /stats/posts

Get website posts published during period.

**Parameters:** start, end
