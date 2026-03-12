# Google My Business Endpoints

GMB reviews, media, and reply management.

## Base URL

```
https://app.metricool.com/api
```

---

## Reviews

### GET /stats/gmb/review

Get GMB reviews with metrics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| sortcolumn | string | No | Sort column |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gmb/review?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

**Response:**
```json
[
  {
    "name": "accounts/123/locations/456/reviews/abc",
    "reviewId": "abc",
    "reviewer": {
      "profilePhotoUrl": "https://...",
      "displayName": "John Doe"
    },
    "starRating": "FIVE",
    "comment": "Great service!",
    "createTime": "2024-01-15T10:30:00Z",
    "updateTime": "2024-01-15T10:30:00Z",
    "reply": {
      "comment": "Thank you!",
      "updateTime": "2024-01-15T11:00:00Z"
    }
  }
]
```

---

### GET /stats/gmb/reviewbyid

Get a specific GMB review.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| reviewname | string | Yes | Review name/ID |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gmb/reviewbyid?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&reviewname=accounts/123/locations/456/reviews/abc"
```

---

### GET /stats/gmb/review/reply

Reply to a GMB review.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| reviewname | string | Yes | Review name/ID |
| text | string | Yes | Reply text |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gmb/review/reply?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&reviewname=accounts/123/locations/456/reviews/abc&text=Thank%20you%20for%20your%20review!"
```

---

### GET /stats/gmb/review/reply/remove

Remove a GMB review reply.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| reviewname | string | Yes | Review name/ID |

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gmb/review/reply/remove?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&reviewname=accounts/123/locations/456/reviews/abc"
```

---

## Media

### GET /stats/gmb/media/{type}

Get GMB media with engagement metrics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | string | Yes | Path param: media type |
| start | integer | Yes | Start timestamp |
| end | integer | Yes | End timestamp |
| sortcolumn | string | No | Sort column |

**Media Types:**
- `photos` - Photo media
- `videos` - Video media

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gmb/media/photos?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

**Response:**
```json
[
  {
    "name": "accounts/123/locations/456/media/xyz",
    "mediaUrl": "https://...",
    "thumbnailUrl": "https://...",
    "createTime": "2024-01-15T10:30:00Z",
    "viewCount": 1250,
    "insights": {
      "views": 1250,
      "interactions": 45
    }
  }
]
```

---

## Star Ratings

GMB uses the following star rating values:

| Value | Stars |
|-------|-------|
| `ONE` | 1 star |
| `TWO` | 2 stars |
| `THREE` | 3 stars |
| `FOUR` | 4 stars |
| `FIVE` | 5 stars |

---

## Workflow Examples

### Get All Reviews and Reply

```bash
# Get all reviews
REVIEWS=$(curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gmb/review?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600")

# Find reviews without replies and respond
echo "$REVIEWS" | jq -r '.[] | select(.reply == null) | .name' | while read review_name; do
  curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
    "https://app.metricool.com/api/stats/gmb/review/reply?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&reviewname=$review_name&text=Thank%20you%20for%20your%20feedback!"
done
```

### Track Review Metrics

```bash
# Get reviews and calculate average rating
curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gmb/review?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600" | \
  jq '[.[].starRating | {"ONE":1,"TWO":2,"THREE":3,"FOUR":4,"FIVE":5}[.]] | add / length'
```
