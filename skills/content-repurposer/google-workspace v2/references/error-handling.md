# Google Workspace — Error Handling

## Auth Failures

### 401 Unauthorized
**Symptom:** `{"error": {"code": 401, "message": "Request had invalid authentication credentials"}}`

**Causes and fixes:**
1. Token expired → credentials file is valid but access token needs refresh
   ```bash
   # gws handles token refresh automatically — if still failing:
   gws gmail users getProfile --params '{"userId":"me"}'  # forces token refresh
   ```
2. Wrong credentials file path
   ```bash
   echo $GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE
   # Should be: /Users/yasmineseidu/coding/google.json
   # If empty: source ~/.zshrc
   ```
3. Credentials file corrupted
   ```bash
   cat /Users/yasmineseidu/coding/google.json | jq '.type'
   # Should return: "service_account"
   ```

---

### `unauthorized_client` or `invalid_grant`
**Symptom:** `{"error": "unauthorized_client", "error_description": "Client is unauthorized to retrieve access tokens..."}`

**Cause:** Service account domain-wide delegation not enabled, or delegated user not in workspace.

**Fix steps:**
1. Go to Google Admin: admin.google.com → Security → API controls → Domain-wide delegation
2. Verify service account client ID is listed with correct scopes
3. Verify `yasmine@smarterflo.com` exists in the Smarterflo workspace
4. If scopes were recently changed, wait up to 15 minutes for propagation

**Check service account client ID:**
```bash
cat /Users/yasmineseidu/coding/google.json | jq '.client_id'
```

---

## Permission Errors

### 403 Forbidden — Insufficient Scope
**Symptom:** `{"error": {"code": 403, "message": "Request had insufficient authentication scopes"}}`

**Cause:** The API scope required isn't included in the domain-wide delegation config.

**Fix:**
1. Check which scope is needed: `gws schema <service>.<resource>.<method>` — look for `scopes` field
2. Add missing scope in Google Admin → Security → API controls → Domain-wide delegation
3. Common missing scopes:
   - Gmail send: `https://mail.google.com/`
   - Calendar: `https://www.googleapis.com/auth/calendar`
   - Drive: `https://www.googleapis.com/auth/drive`
   - Admin Reports: `https://www.googleapis.com/auth/admin.reports.audit.readonly`

---

### 403 accessNotConfigured
**Symptom:** `{"error": {"code": 403, "message": "Access Not Configured. ... API has not been used in project..."}}`

**Fix:**
1. Go to Google Cloud Console: console.cloud.google.com
2. Project: `clawdbot-484604`
3. APIs & Services → Enable APIs
4. Search for and enable the specific API (e.g., "Google Calendar API")
5. Wait ~2 minutes after enabling

---

## Rate Limiting

### 429 Too Many Requests / 403 rateLimitExceeded
**Symptom:** `{"error": {"code": 429}}` or `{"error": {"errors": [{"reason": "rateLimitExceeded"}]}}`

**Exponential backoff pattern:**
```bash
# Single retry with backoff
run_with_backoff() {
  local max_attempts=6
  local attempt=1
  local delay=1

  while [ $attempt -le $max_attempts ]; do
    "$@" && return 0
    echo "Attempt $attempt failed. Retrying in ${delay}s..."
    sleep $delay
    delay=$((delay * 2))
    attempt=$((attempt + 1))
  done
  echo "All $max_attempts attempts failed."
  return 1
}

# Usage:
run_with_backoff gws gmail users messages list --params '{"userId":"me","maxResults":100}'
```

**For bulk loops — add delay between requests:**
```bash
for ID in $IDS; do
  gws gmail users messages get --params '{"userId":"me","id":"'"$ID"'"}'
  sleep 0.1  # 100ms delay keeps under per-second limits
done
```

---

## Not Found Errors

### 404 Not Found
**Symptom:** `{"error": {"code": 404, "message": "Requested entity was not found"}}`

**Common causes:**
- Event ID is for a different calendar (not `primary`)
- File was deleted or moved to Trash
- Message ID is stale (message was deleted)
- Wrong user context (operation on wrong account)

**Fix pattern:**
```bash
# Re-query for the correct ID instead of assuming
# For events: search by title or date
gws calendar events list --params '{"calendarId":"primary","q":"Meeting Title","singleEvents":true}'

# For files: search by name
gws drive files list --params '{"q":"name='\''filename.pdf'\'' and trashed=false"}'

# For messages: search by query
gws gmail users messages list --params '{"userId":"me","q":"subject:\"Subject Line\""}'
```

---

## Server Errors

### 500 Internal Server Error / 503 Service Unavailable
**Symptom:** Unexpected 5xx responses from Google

**These are transient.** Retry with backoff — same pattern as 429 above.
- 500: retry after 1s
- 503: respect `Retry-After` header if present, otherwise retry after 5s

---

## gws CLI Issues

### `gws: command not found`
```bash
# Check if installed
which gws || npm list -g gws

# Reinstall
npm install -g @google-workspace/gws-cli

# Add to PATH if needed
echo 'export PATH="$PATH:$(npm root -g)/.bin"' >> ~/.zshrc
source ~/.zshrc
```

### `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE is not set`
```bash
source ~/.zshrc
# Or set directly:
export GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/Users/yasmineseidu/coding/google.json
```

### gws returns empty results but data exists
```bash
# Try paginating — default maxResults is often 10 or 25
gws gmail users messages list --params '{"userId":"me","maxResults":100}' --page-all

# For Drive
gws drive files list --params '{"pageSize":100}' --page-all
```

### `gws schema` — how to read it
```bash
# Get full API schema for any method
gws schema gmail.users.messages.list

# Output shows:
# - httpMethod: GET/POST/PATCH/DELETE
# - path: the URL template
# - parameters: what goes in --params '{}' (query string params)
# - request: what goes in --json '{}' (request body)
# - scopes: OAuth scopes required
# Use "parameters" fields → --params, "request" fields → --json
```

---

## Quick Diagnostic Checklist

When something fails, run in order:

```bash
# 1. Verify gws CLI works at all
gws --version

# 2. Verify credentials env var is set
echo $GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE

# 3. Verify credentials file exists and is valid
ls -la /Users/yasmineseidu/coding/google.json
cat /Users/yasmineseidu/coding/google.json | jq '.type, .client_email, .project_id'

# 4. Verify delegation works
gws gmail users getProfile --params '{"userId":"me"}'

# 5. If 403 scope error — check which scope is needed
gws schema <service>.<resource>.<method> | grep -A 10 '"scopes"'
```
