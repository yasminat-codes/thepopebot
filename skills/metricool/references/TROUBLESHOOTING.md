# Troubleshooting Guide

Common issues and solutions when using the Metricool API.

## Authentication Issues

### 401 Unauthorized

**Symptoms:**
- API returns 401 status code
- Response: "Unauthorized" or "Invalid token"

**Causes:**
1. Missing or incorrect `X-Mc-Auth` header
2. Expired token
3. Token belongs to different account

**Solutions:**
```bash
# Verify token format
echo "Token: $METRICOOL_USER_TOKEN"

# Check header is correct
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/mtr/ping?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# Regenerate token in Metricool
# Account Settings → API → Generate new token
```

---

### 403 Forbidden

**Symptoms:**
- API returns 403 status code
- Response: "Forbidden" or "Access denied"

**Causes:**
1. API not enabled for your plan
2. Token lacks required permissions

**Solutions:**
```bash
# Verify plan has API access
# Requires Advanced or Custom plan

# Check subscription
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/profile/subscription?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### 404 Not Found

**Symptoms:**
- API returns 404 status code
- Response: "Not found" or "Resource not found"

**Causes:**
1. Invalid `userId`
2. Invalid `blogId`
3. Wrong endpoint path

**Solutions:**
```bash
# Verify userId and blogId
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# If this returns data, your credentials are correct
# If not, check your IDs in Account Settings
```

---

## Rate Limiting

### 429 Too Many Requests

**Symptoms:**
- API returns 429 status code
- Response: "Rate limit exceeded"

**Causes:**
- Too many requests in a short time
- Concurrent request limit exceeded

**Solutions:**
```bash
# Implement exponential backoff
MAX_RETRIES=5
RETRY_DELAY=1

for i in $(seq 1 $MAX_RETRIES); do
  response=$(curl -s -w "%{http_code}" -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
    "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600")

  http_code="${response: -3}"

  if [ "$http_code" != "429" ]; then
    echo "${response%???}"
    break
  fi

  echo "Rate limited, retrying in $RETRY_DELAY seconds..."
  sleep $RETRY_DELAY
  RETRY_DELAY=$((RETRY_DELAY * 2))
done
```

---

## Data Issues

### Empty Results

**Symptoms:**
- API returns empty array `[]`
- No data for specified date range

**Causes:**
1. No content in the date range
2. Date format incorrect
3. Platform not connected

**Solutions:**
```bash
# Verify date format (Unix timestamp)
date -d '2024-01-01' +%s  # Should output: 1704067200

# Check if platform is connected
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### Invalid Date Format

**Symptoms:**
- Unexpected results
- Wrong date range data

**Causes:**
- Using date string instead of Unix timestamp
- Using milliseconds instead of seconds

**Solutions:**
```bash
# Correct: Unix timestamp in seconds
start=$(date -d '2024-01-01' +%s)  # 1704067200

# Wrong: Date string
start="2024-01-01"  # Will not work

# Wrong: Milliseconds
start=$(($(date -d '2024-01-01' +%s) * 1000))  # Too large
```

---

## Platform-Specific Issues

### Instagram Scopes

**Symptoms:**
- Cannot post to Instagram
- Error: "Insufficient permissions"

**Causes:**
- Missing Instagram permissions

**Solutions:**
```bash
# Check required scopes
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/actions/instagram/required-scopes-to-post?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"

# Reconnect Instagram in Metricool dashboard
# Account Settings → Connected Accounts → Reconnect Instagram
```

---

### Facebook Ads Access

**Symptoms:**
- Cannot access Facebook Ads data
- Empty campaigns list

**Causes:**
- Facebook Ads account not connected
- Missing ad account permissions

**Solutions:**
```bash
# Verify Facebook Ads connection
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebookads/campaigns?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"

# If empty, reconnect Facebook Ads in Metricool
# Account Settings → Connected Accounts → Facebook Ads
```

---

## Connection Issues

### Timeout Errors

**Symptoms:**
- Request hangs indefinitely
- Connection timeout

**Causes:**
- Network issues
- Firewall blocking
- Metricool API down

**Solutions:**
```bash
# Add timeout to curl
curl --connect-timeout 30 --max-time 60 \
  -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=1704067200&end=1706745600"

# Check API status
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/mtr/ping?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

### SSL Certificate Errors

**Symptoms:**
- SSL certificate verification failed
- Error: "SSL certificate problem"

**Causes:**
- Outdated CA certificates
- Proxy interference

**Solutions:**
```bash
# Update CA certificates (macOS)
brew install ca-certificates

# Update CA certificates (Ubuntu)
sudo apt-get update && sudo apt-get install ca-certificates

# Temporary workaround (not recommended for production)
curl -k -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/..."
```

---

## Debug Checklist

- [ ] Token is correct and not expired
- [ ] userId matches your account
- [ ] blogId matches an existing brand
- [ ] Date parameters are Unix timestamps in seconds
- [ ] Rate limits are not exceeded
- [ ] Platform is connected in Metricool dashboard
- [ ] API access is enabled (Advanced/Custom plan)
- [ ] Request format is correct (GET vs POST)
- [ ] All required parameters are included
