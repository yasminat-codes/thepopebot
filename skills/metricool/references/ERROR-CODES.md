# Error Codes

Complete reference of Metricool API error codes and their meanings.

## HTTP Status Codes

| Code | Name | Description |
|------|------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Success with no response body |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Access denied (plan limitation) |
| 404 | Not Found | Resource or endpoint not found |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 502 | Bad Gateway | Upstream server error |
| 503 | Service Unavailable | Service temporarily unavailable |
| 504 | Gateway Timeout | Request timeout |

---

## 400 Bad Request

### Causes
- Missing required parameters
- Invalid parameter format
- Invalid parameter values

### Example Response
```json
{
  "error": "bad_request",
  "message": "Missing required parameter: start",
  "details": {
    "parameter": "start",
    "required": true
  }
}
```

### Solutions
```bash
# Verify all required parameters
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"

# Check parameter format
# start and end must be Unix timestamps (seconds, not milliseconds)
date -d '2024-01-01' +%s  # Correct: 1704067200
```

---

## 401 Unauthorized

### Causes
- Missing `X-Mc-Auth` header
- Invalid token
- Expired token
- Token from different account

### Example Response
```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

### Solutions
```bash
# Verify header format
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/mtr/ping?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# Regenerate token
# Go to: Account Settings → API → Generate new token
```

---

## 403 Forbidden

### Causes
- API access not enabled (requires Advanced/Custom plan)
- Token lacks required permissions
- Resource access denied

### Example Response
```json
{
  "error": "forbidden",
  "message": "API access requires Advanced or Custom plan"
}
```

### Solutions
```bash
# Check subscription
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/profile/subscription?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# Upgrade plan if needed
# Contact Metricool support
```

---

## 404 Not Found

### Causes
- Invalid endpoint path
- Invalid `userId`
- Invalid `blogId`
- Resource doesn't exist

### Example Response
```json
{
  "error": "not_found",
  "message": "Brand not found"
}
```

### Solutions
```bash
# Verify credentials
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# Check endpoint spelling
# Use exact paths from documentation
```

---

## 429 Too Many Requests

### Causes
- Rate limit exceeded
- Too many concurrent requests

### Example Response
```json
{
  "error": "rate_limited",
  "message": "Rate limit exceeded. Retry after 60 seconds.",
  "retryAfter": 60
}
```

### Solutions
```bash
# Wait and retry
sleep 60

# Implement exponential backoff
backoff() {
  local max_attempts=5
  local attempt=1
  local delay=1

  while [ $attempt -le $max_attempts ]; do
    response=$(curl -s -w "\n%{http_code}" "$@")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" != "429" ]; then
      echo "$body"
      return 0
    fi

    echo "Rate limited, attempt $attempt of $max_attempts. Waiting ${delay}s..." >&2
    sleep $delay
    delay=$((delay * 2))
    attempt=$((attempt + 1))
  done

  return 1
}
```

---

## 500 Internal Server Error

### Causes
- Metricool server error
- Temporary outage
- Unexpected error condition

### Example Response
```json
{
  "error": "internal_error",
  "message": "An unexpected error occurred"
}
```

### Solutions
```bash
# Retry with backoff
# Check Metricool status page

# If persistent, contact Metricool support with:
# - Timestamp of error
# - Endpoint called
# - Request parameters
# - Response body
```

---

## Platform-Specific Errors

### Instagram Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `instagram_not_connected` | Instagram account not linked | Connect in Metricool dashboard |
| `insufficient_scopes` | Missing permissions | Reconnect Instagram with correct scopes |
| `media_not_found` | Media ID doesn't exist | Verify media ID |

### Facebook Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `facebook_not_connected` | Facebook account not linked | Connect in Metricool dashboard |
| `ad_account_not_found` | Ad account not linked | Connect Facebook Ads account |
| `page_not_admin` | Not admin of page | Use admin account |

### TikTok Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `tiktok_not_connected` | TikTok not linked | Connect in Metricool dashboard |
| `video_not_found` | Video ID invalid | Verify video exists |

---

## Error Response Format

Standard error response:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "field_name",
    "value": "invalid_value",
    "expected": "expected_format"
  },
  "requestId": "req_abc123",
  "timestamp": 1704067200
}
```

---

## Debugging Tips

```bash
# Enable verbose output
curl -v -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"

# Get response headers
curl -i -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"

# Time the request
curl -w "\nTime: %{time_total}s\n" -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```
