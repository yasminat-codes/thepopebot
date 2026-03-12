# Real-Time Analytics Endpoints

Live visitor tracking, current session data, and real-time distributions.

## Base URL

```
https://app.metricool.com/api
```

---

## Real-Time Stats

### GET /stats/rt/values

Get today's page views, visits, and visitors.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/values?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
{
  "pageViews": 1523,
  "visits": 892,
  "visitors": 756,
  "timestamp": 1704067200
}
```

---

### GET /stats/rt/pvperhour

Get page views per hour distribution for a website.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/pvperhour?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
{
  "00:00": 45,
  "01:00": 32,
  "02:00": 18,
  "03:00": 12,
  "04:00": 8,
  "05:00": 15,
  "06:00": 28,
  "07:00": 52,
  "08:00": 89,
  "09:00": 145,
  "10:00": 178,
  "11:00": 198,
  "12:00": 167,
  "13:00": 145,
  "14:00": 156,
  "15:00": 134,
  "16:00": 112,
  "17:00": 98,
  "18:00": 87,
  "19:00": 76,
  "20:00": 65,
  "21:00": 54,
  "22:00": 43,
  "23:00": 38
}
```

---

### GET /stats/rt/sessions

Get real-time visit list for a website.

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/sessions?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
{
  "sessions": [
    {
      "id": "session_123",
      "ip": "192.168.1.1",
      "country": "United States",
      "city": "New York",
      "browser": "Chrome",
      "os": "Windows",
      "device": "Desktop",
      "landingPage": "/blog/post-1",
      "duration": 45,
      "pagesViewed": 3
    }
  ],
  "total": 45,
  "activeNow": 12
}
```

---

### GET /stats/rt/distribution/{type}

Get real-time visit distribution by type.

**Path param:** type (country, city, browser, os, device, source)

**Example:**
```bash
# Distribution by country
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/distribution/country?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

**Response:**
```json
{
  "United States": 456,
  "United Kingdom": 123,
  "Germany": 89,
  "France": 67,
  "Canada": 54
}
```

---

## Distribution Types

| Type | Description |
|------|-------------|
| `country` | Visitors by country |
| `city` | Visitors by city |
| `browser` | Visitors by browser |
| `os` | Visitors by operating system |
| `device` | Visitors by device type |
| `source` | Traffic sources |

---

## Link Distribution

### GET /stats/link/distribution/{type}

Get link click distribution.

**Path param:** type (source, page)

**Example:**
```bash
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/link/distribution/source?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
```

---

## Real-Time Dashboard

Create a real-time dashboard:

```bash
# Get all real-time data
curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/values?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | jq '.' > rt-values.json

curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/pvperhour?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | jq '.' > rt-hourly.json

curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/sessions?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | jq '.' > rt-sessions.json

curl -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/distribution/country?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | jq '.' > rt-countries.json
```

---

## Polling for Updates

For real-time monitoring, poll the endpoints:

```bash
# Poll every 30 seconds
watch -n 30 'curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/values?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | jq'
```
