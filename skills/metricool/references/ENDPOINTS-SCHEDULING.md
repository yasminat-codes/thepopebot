# Scheduling & Planner Endpoints

Post scheduling, hashtag suggestions, best time analysis, and account suggestions.

## Base URL

```
https://app.metricool.com/api
```

---

## Timezone

### GET /actions/setTimeZone

Define the user timezone.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| timezone | string | Yes | Timezone string (e.g., "America/New_York") |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/setTimeZone?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&timezone=America/New_York"
```

---

## Hashtag Suggestions

### GET /actions/instagram/suggestions/hashtags

Get Instagram hashtag suggestions.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | Yes | Search query |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/instagram/suggestions/hashtags?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&q=marketing"
```

**Response:**
```json
{
  "hashtags": [
    {"tag": "#marketing", "posts": 50000000},
    {"tag": "#digitalmarketing", "posts": 25000000},
    {"tag": "#marketingtips", "posts": 10000000}
  ]
}
```

---

## Account Suggestions

### GET /actions/twitter/suggestions

Get Twitter account suggestions.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | Yes | Search query |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/twitter/suggestions?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&q=marketing"
```

---

### GET /actions/facebook/suggestions

Get Facebook page suggestions.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | Yes | Search query |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/facebook/suggestions?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&q=marketing"
```

---

### GET /actions/linkedin/suggestions

Get LinkedIn company suggestions.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | Yes | Search query |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/linkedin/suggestions?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&q=marketing"
```

---

### GET /actions/bluesky/suggestions

Get Bluesky account suggestions.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| q | string | Yes | Search query |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/bluesky/suggestions?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&q=marketing"
```

---

## Instagram Posting

### GET /actions/instagram/required-scopes-to-post

Check required Instagram scopes for posting.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/instagram/required-scopes-to-post?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
["instagram_basic", "instagram_content_publish", "instagram_manage_comments"]
```

---

### GET /actions/instagram/auto-candidate-posts-count-for-automation

Get count of posts eligible for automation.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/instagram/auto-candidate-posts-count-for-automation?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## Image Validation

### GET /actions/normalize/image/url

Validate and normalize an image URL.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| url | string | Yes | Image URL to validate |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/normalize/image/url?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&url=https://example.com/image.jpg"
```

---

## Location Search

### GET /actions/facebook/search-location

Search Facebook locations for targeting.

**Parameters:** (varies)

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/facebook/search-location?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&q=New%20York"
```

---

## Scheduled Posts

### GET /stats/scheduled_posts

Get scheduled posts from brand account.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/scheduled_posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### POST /stats/schedule_post

Schedule a new post.

**Body:** JSON with post details

**Example:**
```bash
curl -X POST -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"platform":"instagram","text":"Post caption","mediaUrl":"https://...","scheduledAt":1704067200}' \
  "https://app.metricool.com/api/stats/schedule_post?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### GET /stats/update_schedule_post

Update a scheduled post.

**Parameters:** Post ID and new values

---

## Best Time to Post

### GET /stats/best_time_to_post

Get optimal posting times by day/hour with engagement scoring.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/best_time_to_post?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&platform=instagram"
```

**Response:**
```json
{
  "monday": {
    "09:00": 85,
    "12:00": 92,
    "18:00": 78
  },
  "tuesday": {
    "10:00": 88,
    "14:00": 95,
    "19:00": 82
  }
}
```
