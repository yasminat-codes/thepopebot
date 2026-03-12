# Rate Limits

Understanding and handling Metricool API rate limits.

## Plan-Based Limits

| Plan | API Access | Rate Limit |
|------|------------|------------|
| Free | ❌ No | N/A |
| Basic | ❌ No | N/A |
| Advanced | ✅ Yes | Check dashboard |
| Custom | ✅ Yes | Negotiated |

**Note:** Exact rate limits are visible in Account Settings → API tab.

---

## Rate Limit Headers

API responses include rate limit headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1704067200
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Total requests allowed per window |
| `X-RateLimit-Remaining` | Requests remaining in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

---

## Checking Your Limits

```bash
# Get rate limit info from headers
curl -i -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/mtr/ping?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" 2>&1 | grep -i "X-RateLimit"
```

---

## Handling Rate Limits

### Exponential Backoff

```bash
#!/bin/bash

api_request() {
  local url="$1"
  local max_retries=5
  local retry_delay=1

  for i in $(seq 1 $max_retries); do
    response=$(curl -s -w "\n%{http_code}" -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" "$url")
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ]; then
      echo "$body"
      return 0
    elif [ "$http_code" = "429" ]; then
      echo "Rate limited. Waiting ${retry_delay}s before retry..." >&2
      sleep $retry_delay
      retry_delay=$((retry_delay * 2))
    else
      echo "Error: HTTP $http_code" >&2
      echo "$body" >&2
      return 1
    fi
  done

  echo "Max retries exceeded" >&2
  return 1
}

# Usage
api_request "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"
```

### Python Implementation

```python
import requests
import time
import os

def metricool_request(endpoint, params, max_retries=5):
    headers = {"X-Mc-Auth": os.environ["METRICOOL_USER_TOKEN"]}
    params["blogId"] = os.environ["METRICOOL_BLOG_ID"]
    params["userId"] = os.environ["METRICOOL_USER_ID"]

    base_url = "https://app.metricool.com/api"
    url = f"{base_url}/{endpoint}"

    retry_delay = 1

    for attempt in range(max_retries):
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", retry_delay))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
            retry_delay *= 2
        else:
            response.raise_for_status()

    raise Exception("Max retries exceeded")
```

---

## Best Practices

### 1. Batch Requests

Group related requests together:

```bash
# Get multiple platforms in parallel
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600" &
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebook/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600" &
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/tiktok/videos?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600" &
wait
```

### 2. Cache Responses

Cache responses locally:

```bash
# Cache with timestamp
cache_file="cache_instagram_$(date +%Y%m%d).json"

if [ -f "$cache_file" ]; then
  # Check if cache is less than 1 hour old
  if [ $(($(date +%s) - $(stat -c %Y "$cache_file"))) -lt 3600 ]; then
    cat "$cache_file"
    exit 0
  fi
fi

# Fetch and cache
curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600" \
  > "$cache_file"

cat "$cache_file"
```

### 3. Respect Rate Limits

```bash
# Add delay between requests
for platform in instagram facebook tiktok youtube; do
  curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
    "https://app.metricool.com/api/stats/${platform}/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600" \
    > "${platform}_posts.json"

  # Wait 1 second between requests
  sleep 1
done
```

### 4. Monitor Usage

```bash
# Log API calls with timestamps
log_api_call() {
  local endpoint="$1"
  local timestamp=$(date -Iseconds)
  local remaining=$(curl -s -I -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
    "https://app.metricool.com/api/mtr/ping?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | \
    grep -i "X-RateLimit-Remaining" | tr -d '\r' | awk '{print $2}')

  echo "[$timestamp] $endpoint - Remaining: $remaining" >> api_usage.log
}
```

---

## When to Contact Support

If you consistently hit rate limits:

1. Check your usage patterns for optimization opportunities
2. Implement caching for frequently accessed data
3. Contact Metricool support for limit increase:
   - Current plan level
   - Expected request volume
   - Use case description
