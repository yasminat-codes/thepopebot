# Metricool Schedule API Reference

## Base URL

```
https://app.metricool.com/api/v2
```

## Authentication

All requests require a Bearer token passed via the `METRICOOL_API_KEY` header:

```
Authorization: Bearer {METRICOOL_API_KEY}
```

---

## Endpoints

### POST /social/metricool/post

Schedule a new LinkedIn post.

**Required Fields**

| Field          | Type   | Description                                      |
|----------------|--------|--------------------------------------------------|
| content        | string | Post body text                                   |
| scheduled_at   | string | ISO 8601 datetime (e.g. `2026-03-10T09:00:00Z`) |
| platform       | string | Must be `"linkedin"`                             |
| user_id        | string | Value of `METRICOOL_USER_ID` env var             |

**Optional Fields**

| Field            | Type            | Description                              |
|------------------|-----------------|------------------------------------------|
| media_urls       | array of strings | Direct URLs to image/video assets       |
| link             | string          | URL to generate a link preview           |

**Success Response** `200 OK`

```json
{
  "id": "mct_abc123",
  "status": "scheduled",
  "scheduled_at": "2026-03-10T09:00:00Z"
}
```

**Error Responses**

| Code | Meaning                                          |
|------|--------------------------------------------------|
| 400  | Bad payload — missing required fields or malformed JSON |
| 401  | Invalid or expired `METRICOOL_API_KEY`           |
| 422  | Validation error — content fails platform rules  |
| 429  | Rate limit exceeded (see limits below)           |
| 500+ | Server-side error — retry with exponential backoff |

---

### GET /social/metricool/posts

List all scheduled posts.

**Query Parameters**

| Param      | Type   | Description                         |
|------------|--------|-------------------------------------|
| platform   | string | Filter by platform (e.g. `linkedin`)|
| from       | string | ISO 8601 start date                 |
| to         | string | ISO 8601 end date                   |

**Response** `200 OK`

```json
{
  "posts": [
    {
      "id": "mct_abc123",
      "status": "scheduled",
      "scheduled_at": "2026-03-10T09:00:00Z",
      "platform": "linkedin"
    }
  ]
}
```

---

### DELETE /social/metricool/posts/{id}

Cancel a scheduled post by its Metricool ID.

**Path Parameter**

| Param | Type   | Description               |
|-------|--------|---------------------------|
| id    | string | Metricool post ID         |

**Response** `200 OK`

```json
{ "deleted": true }
```

---

### GET /analytics/linkedin

Retrieve LinkedIn performance data. Used by the `analytics-dashboard` skill.

**Query Parameters**

| Param    | Type   | Description                         |
|----------|--------|-------------------------------------|
| user_id  | string | `METRICOOL_USER_ID`                 |
| from     | string | ISO 8601 start date                 |
| to       | string | ISO 8601 end date                   |

**Response** `200 OK`

```json
{
  "impressions": 4200,
  "clicks": 315,
  "reactions": 87,
  "comments": 22,
  "shares": 14,
  "engagement_rate": 0.074
}
```

---

## Rate Limits

| Window | Limit              |
|--------|--------------------|
| Hourly | 100 requests/hour  |
| Daily  | 1000 requests/day  |

When the limit is exceeded the API returns `429` with a `Retry-After` header indicating seconds to wait.

---

## Testing — cURL Example

Schedule a test post to verify credentials and connectivity:

```bash
curl -X POST https://app.metricool.com/api/v2/social/metricool/post \
  -H "Authorization: Bearer $METRICOOL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Test post from batch-scheduler skill. Will delete.",
    "scheduled_at": "2026-12-31T23:00:00Z",
    "platform": "linkedin",
    "user_id": "'"$METRICOOL_USER_ID"'"
  }'
```

Expected response:

```json
{ "id": "mct_test001", "status": "scheduled", "scheduled_at": "2026-12-31T23:00:00Z" }
```

After confirming success, cancel the test post:

```bash
curl -X DELETE https://app.metricool.com/api/v2/social/metricool/posts/mct_test001 \
  -H "Authorization: Bearer $METRICOOL_API_KEY"
```
