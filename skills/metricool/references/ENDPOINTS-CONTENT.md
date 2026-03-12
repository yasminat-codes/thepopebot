# Content & Engagement Endpoints

Post management, comments, likes, and competitor analysis.

## Base URL

```
https://app.metricool.com/api
```

---

## Posting & Comments

### GET /stats/postmessage/{provider}

Post a message or comment in response to another.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| provider | string | Yes | Path param: facebook, instagram |
| conversationid | string | Yes | Conversation/thread ID |
| text | string | Yes | Message text |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/postmessage/facebook?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&conversationid=123456&text=Thanks%20for%20your%20comment!"
```

---

### GET /stats/deletecomment/{provider}

Delete a Facebook comment.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| provider | string | Yes | Path param: facebook |
| commentid | string | Yes | Comment ID to delete |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/deletecomment/facebook?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&commentid=123456"
```

---

### GET /stats/postlike/{provider}

Like or unlike a comment.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| provider | string | Yes | Path param: facebook |
| objectid | string | Yes | Object/comment ID |
| isLiked | string | Yes | "true" or "false" |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/postlike/facebook?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&objectid=123456&isLiked=true"
```

---

## Competitor Analysis

### GET /stats/network_competitors

Get list of competitors for the brand.

**Platforms:** Instagram, Facebook, X, Bluesky, YouTube, Twitch

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/network_competitors?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
[
  {
    "id": "competitor_id",
    "username": "competitor_handle",
    "platform": "instagram",
    "followers": 50000,
    "following": 500,
    "posts": 1200
  }
]
```

---

### GET /stats/network_competitors_posts

Analyze competitor posts across platforms.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| platform | string | No | Filter by platform |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/network_competitors_posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

---

## X (Twitter) Actions

### GET /stats/twitter/follow

Follow a Twitter account.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| userid | string | Yes | Twitter user ID |
| screenname | string | Yes | Twitter screen name |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/twitter/follow?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&userid=123456&screenname=username"
```

---

### GET /stats/twitter/unfollow

Unfollow a Twitter account.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| userid | string | Yes | Twitter user ID |
| screenname | string | Yes | Twitter screen name |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/twitter/unfollow?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&userid=123456&screenname=username"
```

---

## Real-Time Twitter

### GET /stats/rt/twitter/tweets/{type}

Get last tweets or mentions in real-time.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | Yes | Path param: "tweets" or "mentions" |
| screenname | string | Yes | Twitter screen name |
| timezone | string | No | Timezone |
| from | string | No | Start date |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/twitter/tweets/tweets?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&screenname=myhandle"
```

---

### GET /stats/rt/twitterProfile

Get real-time Twitter profile data.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/twitterProfile?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## Media Upload

### POST /media/upload

Upload media files directly to S3.

**Content-Type:** `multipart/form-data`

**Example:**
```bash
curl -X POST -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  -F "file=@image.jpg" \
  "https://app.metricool.com/api/media/upload?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## Post Types

### GET /stats/{provider}/posts/types

Get posts grouped by type.

**Path param:** provider (instagram, facebook, etc.)

**Parameters:** start, end

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts/types?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

**Response:**
```json
{
  "IMAGE": 45,
  "VIDEO": 12,
  "CAROUSEL": 23,
  "REEL": 8
}
```
