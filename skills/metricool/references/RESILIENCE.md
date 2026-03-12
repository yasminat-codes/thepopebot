# Resilience Patterns

Production-grade error handling, retries, rate limiting, and caching for Metricool API.

## Overview

This skill implements multiple resilience patterns to ensure reliable API access:

1. **Automatic Retries** - Exponential backoff for transient failures
2. **Rate Limit Handling** - Proactive and reactive rate limit management
3. **Circuit Breaker** - Fail fast when API is unhealthy
4. **Response Caching** - Reduce API calls for repeated data
5. **Request Queuing** - Smooth traffic spikes

---

## Retry Strategy

### When to Retry

| Status Code | Retry? | Reason |
|-------------|--------|--------|
| 408 | ✓ | Request timeout |
| 429 | ✓ | Rate limited |
| 500 | ✓ | Server error |
| 502 | ✓ | Bad gateway |
| 503 | ✓ | Service unavailable |
| 504 | ✓ | Gateway timeout |
| 400 | ✗ | Bad request (fix your code) |
| 401 | ✗ | Unauthorized (fix credentials) |
| 403 | ✗ | Forbidden (check plan/access) |
| 404 | ✗ | Not found (check resource) |

### Exponential Backoff

```
Delay = base_delay * (exponential_base ^ attempt)
       + jitter

base_delay = 1 second
exponential_base = 2
max_delay = 60 seconds
jitter = ±25% of calculated delay
```

**Example delays:**
- Attempt 1: 1.2s
- Attempt 2: 2.5s
- Attempt 3: 4.8s
- Attempt 4: 9.1s
- Attempt 5: 18.3s

### Implementation

```python
from metricool_client import MetricoolClient, RetryPolicy

# Custom retry policy
policy = RetryPolicy(
    max_retries=5,
    base_delay=1.0,
    max_delay=120.0,
    exponential_base=2.0
)

client = MetricoolClient(
    user_token="...",
    user_id="...",
    blog_id="...",
    retry_policy=policy
)
```

---

## Rate Limit Handling

### Header-Based Limits

Metricool returns rate limit info in response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1704067200
```

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Total requests per window |
| `X-RateLimit-Remaining` | Requests left in current window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |

### Proactive Management

```python
# Client automatically:
# 1. Parses rate limit headers from every response
# 2. Tracks remaining requests
# 3. Waits before reset if approaching limit

# Check current status
stats = client.get_stats()
print(f"Remaining: {stats['rate_limit']['remaining']}")
print(f"Exhausted: {stats['rate_limit']['exhausted']}")
```

### Reactive Handling (429)

When rate limited (HTTP 429):

```python
try:
    result = client.instagram.get_posts(start, end)
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
    # Client automatically waited and retried
    # This exception only raised if retries exhausted
```

### Bash Implementation

```bash
# Using the resilient script
./scripts/metricool-resilient.sh get "stats/instagram/posts" "start=1704067200&end=1706745600"
```

---

## Circuit Breaker

Prevents cascade failures when API is unhealthy.

### States

| State | Behavior |
|-------|----------|
| **CLOSED** | Normal operation, all requests pass |
| **OPEN** | Requests fail immediately without calling API |
| **HALF_OPEN** | One test request allowed to check recovery |

### Configuration

```python
client = MetricoolClient(
    # ...credentials...
    circuit_breaker_threshold=5  # Open after 5 failures
)

# Check circuit breaker state
stats = client.get_stats()
print(f"State: {stats['circuit_breaker']['state']}")
print(f"Failures: {stats['circuit_breaker']['failures']}")
```

### Recovery

- Circuit opens after `threshold` consecutive failures
- After `recovery_timeout` (60s), enters HALF_OPEN
- Single successful request closes the circuit
- Failed request in HALF_OPEN reopens circuit

---

## Response Caching

Reduces API calls for frequently requested data.

### Cache Keys

Keys are generated from:
```
MD5(method + endpoint + sorted_params)
```

### TTL by Data Type

| Data Type | Default TTL | Reasoning |
|-----------|-------------|-----------|
| Real-time stats | 30s | High frequency updates |
| Post/video analytics | 300s | 5 min staleness OK |
| Demographics | 3600s | Slow-changing data |
| Suggestions | 3600s | Hourly refresh sufficient |
| Static config | 86400s | Rarely changes |

### Usage

```python
# Cache enabled by default
client = MetricoolClient(enable_cache=True, cache_ttl=300)

# Bypass cache for specific request
result = client.get('stats/instagram/posts', params, use_cache=False)

# Clear cache
client.clear_cache()

# Disable cache entirely
client = MetricoolClient(enable_cache=False)
```

---

## Error Hierarchy

```
MetricoolError (base)
├── RateLimitError (429)
├── AuthenticationError (401)
├── NotFoundError (404)
├── ServerError (5xx)
└── ValidationError (400)
```

### Handling Errors

```python
from metricool_client import (
    MetricoolClient,
    MetricoolError,
    RateLimitError,
    AuthenticationError,
    NotFoundError,
    ServerError
)

client = MetricoolClient(...)

try:
    posts = client.instagram.get_posts(start, end)
except RateLimitError as e:
    # Rate limited after retries exhausted
    logger.warning(f"Rate limited, retry after {e.retry_after}s")
    time.sleep(e.retry_after)
    # Retry manually or queue for later
except AuthenticationError as e:
    # Invalid credentials
    logger.error(f"Auth failed: {e}")
    raise
except NotFoundError as e:
    # Resource doesn't exist
    logger.warning(f"Not found: {e}")
    return None
except ServerError as e:
    # API is down
    logger.error(f"Server error: {e}")
    # Check circuit breaker state
    if client.circuit_breaker.state == CircuitState.OPEN:
        logger.critical("Circuit breaker OPEN - API unhealthy")
    raise
except MetricoolError as e:
    # Generic API error
    logger.error(f"API error: {e.status_code} - {e}")
    raise
```

---

## Monitoring & Observability

### Client Statistics

```python
stats = client.get_stats()

# Request metrics
print(f"Total requests: {stats['requests']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Cache misses: {stats['cache_misses']}")
print(f"Retries: {stats['retries']}")
print(f"Errors: {stats['errors']}")

# Cache hit rate
hit_rate = stats['cache_hits'] / max(stats['cache_hits'] + stats['cache_misses'], 1)
print(f"Cache hit rate: {hit_rate:.1%}")
```

### Logging

```python
import logging

# Enable debug logging
logging.getLogger('metricool').setLevel(logging.DEBUG)

# See all API calls
# 2024-01-15 10:30:00 - metricool - DEBUG - Cache HIT for stats/instagram/posts?...
# 2024-01-15 10:30:01 - metricool - INFO - Request: GET stats/instagram/posts (200)
# 2024-01-15 10:30:02 - metricool - WARNING - Rate limited, waiting 60s (attempt 1)
```

---

## Bash Resilience

### Basic Retry Wrapper

```bash
#!/bin/bash
# metricool-resilient.sh - Resilient API wrapper

set -euo pipefail

# Retry configuration
MAX_RETRIES=3
BASE_DELAY=1
MAX_DELAY=60

api_request() {
    local endpoint="$1"
    local params="$2"
    local attempt=0
    local delay=$BASE_DELAY

    while [ $attempt -lt $MAX_RETRIES ]; do
        # Make request
        response=$(curl -s -w "\n%{http_code}" \
            -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
            "https://app.metricool.com/api/${endpoint}?blogId=${METRICOOL_BLOG_ID}&userId=${METRICOOL_USER_ID}&${params}" \
            2>&1)

        http_code=$(echo "$response" | tail -n 1)
        body=$(echo "$response" | sed '$d')

        case "$http_code" in
            200)
                echo "$body"
                return 0
                ;;
            429)
                # Rate limited - get retry-after or use delay
                retry_after=$(echo "$body" | jq -r '.retryAfter // empty' 2>/dev/null || echo "$delay")
                echo "Rate limited, waiting ${retry_after}s..." >&2
                sleep "$retry_after"
                ;;
            500|502|503|504)
                # Server error - retry with backoff
                echo "Server error ($http_code), retrying in ${delay}s..." >&2
                sleep "$delay"
                delay=$((delay * 2))
                [ $delay -gt $MAX_DELAY ] && delay=$MAX_DELAY
                ;;
            401)
                echo "Authentication failed" >&2
                return 1
                ;;
            *)
                echo "Error: HTTP $http_code" >&2
                echo "$body" >&2
                return 1
                ;;
        esac

        attempt=$((attempt + 1))
    done

    echo "Max retries exceeded" >&2
    return 1
}

# Usage
api_request "stats/instagram/posts" "start=1704067200&end=1706745600"
```

---

## Best Practices

### 1. Use Cached Data

```python
# GOOD: Cache enabled, one API call per 5 minutes
posts = client.instagram.get_posts(start, end)

# BAD: Cache disabled, many API calls
client = MetricoolClient(enable_cache=False)
for day in days:
    posts = client.instagram.get_posts(day.start, day.end)
```

### 2. Batch Requests

```python
# GOOD: Parallel requests
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(client.instagram.get_posts, start, end): 'instagram',
        executor.submit(client.facebook.get_posts, start, end): 'facebook',
        executor.submit(client.tiktok.get_videos, start, end): 'tiktok',
    }
    results = {}
    for future in concurrent.futures.as_completed(futures):
        platform = futures[future]
        results[platform] = future.result()
```

### 3. Handle Errors Gracefully

```python
# GOOD: Graceful degradation
def get_analytics_with_fallback(client, platform, start, end):
    try:
        return client.get_analytics(platform, start, end)
    except (ServerError, RateLimitError) as e:
        logger.warning(f"{platform} analytics unavailable: {e}")
        return None  # Return None, don't crash

# BAD: Unhandled exceptions crash the app
posts = client.instagram.get_posts(start, end)  # May crash
```

### 4. Respect Rate Limits

```python
# GOOD: Check rate limit before bulk operations
stats = client.get_stats()
if stats['rate_limit']['remaining'] < 100:
    wait_time = stats['rate_limit']['reset_at'] - datetime.now()
    logger.info(f"Approaching rate limit, waiting {wait_time}s")
    time.sleep(wait_time.total_seconds())

# Process bulk data
for brand in brands:
    client.admin.get_brand(brand['id'])
```

### 5. Use Health Checks

```python
# GOOD: Check API health before operations
if not client.ping():
    logger.warning("API not responding, queuing operation")
    queue_for_later(operation)
    return

# Proceed with API calls
result = operation()
```
