# Error Handling Reference

Comprehensive guide to Retell AI API error codes, common causes, and resolution
strategies.

---

## Error Code Reference

### 400 Bad Request

The request body is malformed or missing required fields.

**Common causes:**
- Invalid JSON syntax (missing comma, unclosed brace)
- Missing `response_engine` when creating agent
- Missing `start_speaker` when creating LLM
- Missing `voice_id` when creating agent
- Missing `from_number` or `to_number` when creating phone call

**Resolution:**
1. Validate JSON with `echo "$BODY" | jq .` before sending
2. Check required fields for the endpoint you are calling
3. Review the request body structure in the API reference

**Example error response:**
```json
{
  "error": "Bad Request",
  "message": "Invalid JSON in request body"
}
```

### 401 Unauthorized

The API key is missing, invalid, or expired.

**Common causes:**
- Typo in `RETELL_API_KEY`
- Key was rotated or revoked
- Missing `Authorization` header entirely
- Using `Bearer` prefix twice (e.g., "Bearer Bearer ret_...")

**Resolution:**
1. Verify key in Retell dashboard under Settings > API Keys
2. Check header format: `Authorization: Bearer <key>`
3. Test with a simple `GET /list-agents` call
4. Generate a new key if the current one was compromised

### 422 Unprocessable Content

The JSON is valid but one or more field values are invalid.

**Common causes and fixes:**

| Field | Error | Valid Range | Fix |
|-------|-------|-------------|-----|
| `voice_temperature` | Out of range | 0 to 2 | Clamp to valid range |
| `voice_speed` | Out of range | 0.5 to 2 | Clamp to valid range |
| `responsiveness` | Out of range | 0 to 1 | Clamp to valid range |
| `interruption_sensitivity` | Out of range | 0 to 1 | Clamp to valid range |
| `backchannel_frequency` | Out of range | 0 to 1 | Clamp to valid range |
| `ambient_sound_volume` | Out of range | 0 to 2 | Clamp to valid range |
| `volume` | Out of range | 0 to 2 | Clamp to valid range |
| `voice_id` | Not found | — | Verify with `/list-voices` |
| `response_engine.type` | Invalid | "retell-llm" | Use exact string |
| `response_engine.llm_id` | Not found | — | Verify LLM exists first |
| `ambient_sound` | Invalid value | See allowed values | Use exact enum string |
| `denoising_mode` | Invalid value | See allowed values | Use exact enum string |
| `max_call_duration_ms` | Out of range | 60000-7200000 | Clamp to valid range |
| `states[].edges[].destination_state_name` | Not found | — | Must match a state name |

**Example error response:**
```json
{
  "error": "Unprocessable Content",
  "message": "voice_temperature must be between 0 and 2",
  "field": "voice_temperature"
}
```

### 500 Internal Server Error

Server-side issue at Retell.

**Resolution:**
- Retry with exponential backoff
- If persistent (3+ failures), check Retell status page
- Contact Retell support if issue continues

---

## Retry Strategy

Implement exponential backoff for 500 errors and network failures.

```bash
retry_request() {
  local max_attempts=3
  local attempt=1
  local delay=2

  while [ $attempt -le $max_attempts ]; do
    response=$(curl -s -w "\n%{http_code}" "$@")
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | head -n -1)

    if [ "$http_code" -lt 500 ]; then
      echo "$body"
      return 0
    fi

    echo "Attempt $attempt failed with $http_code. Retrying in ${delay}s..." >&2
    sleep $delay
    attempt=$((attempt + 1))
    delay=$((delay * 2))
  done

  echo "ERROR: All $max_attempts attempts failed" >&2
  echo "$body"
  return 1
}
```

### Retry Schedule

| Attempt | Delay | Total Elapsed |
|---------|-------|---------------|
| 1 | 0s | 0s |
| 2 | 2s | 2s |
| 3 | 4s | 6s |
| Fail | — | 6s |

### What to Retry

| Error | Retry? | Reason |
|-------|--------|--------|
| 400 | No | Fix the request body |
| 401 | No | Fix the API key |
| 422 | No | Fix the field values |
| 500 | Yes | Transient server error |
| Network timeout | Yes | Transient network issue |
| Connection refused | Yes | Transient network issue |

---

## Debugging Checklist

When an API call fails, work through this checklist:

1. **Check HTTP status code** — tells you the error category
2. **Read response body** — often contains the specific field and reason
3. **Validate JSON** — `echo "$BODY" | jq .` to catch syntax errors
4. **Check required fields** — refer to the endpoint's API reference
5. **Check value ranges** — see the table above
6. **Verify referenced resources** — ensure LLM and voice IDs exist
7. **Test authentication** — simple `GET /list-agents` call
8. **Check Retell status** — for 500 errors, check if Retell is down
