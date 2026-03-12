---
name: instantly
description: >-
  Manage Instantly.ai email campaigns via the full v2 API CLI. Use PROACTIVELY
  when user says "instantly", "cold email campaign", "email sequence", "campaign
  analytics", "lead list", "warmup", "inbox rotation", "email deliverability",
  "create campaign", or "Instantly API". Use when building or managing outbound
  email sequences or cold outreach campaigns. Requires INSTANTLY_API_KEY env var.
allowed-tools: Read Write Edit Bash Task
argument-hint: "[campaign-name-or-action] (optional)"
disable-model-invocation: false
user-invocable: true
model: sonnet
license: Proprietary
metadata:
  author: yasmine-seidu
  version: "1.0.0"
  category: email-marketing
---

# Instantly.ai API Skill

Complete CLI for Instantly.ai v2 API with modular structure and raw endpoint access.

## Setup

1. Get your API key from Instantly.ai dashboard
2. Set environment variable:
```bash
export INSTANTLY_API_KEY="your_api_key_here"
```

Add to `~/.bashrc` or `~/.zshrc` to persist.

## Architecture

```
instantly/
├── instantly              # Main CLI entry point
├── lib/
│   ├── config.sh         # API configuration
│   ├── http.sh           # HTTP helpers + raw API caller
│   ├── leads.sh          # Leads endpoints
│   ├── campaigns.sh      # Campaign endpoints
│   ├── inbox.sh          # Inbox/reply endpoints
│   ├── subsequences.sh   # Subsequence endpoints
│   └── analytics.sh      # Analytics endpoints
└── examples/
    └── sample-responses/ # Example API responses
```

## Usage

### Main Commands

```bash
instantly <command> [subcommand] [options]
```

**Commands:**
- `leads` - Manage leads
- `campaigns` - Manage campaigns
- `inbox` - Manage inbox and replies
- `subsequences` - Manage email subsequences
- `analytics` - Get analytics and stats
- `api` - Raw API call to any endpoint

### Leads

```bash
# List leads in a campaign
instantly leads list --campaign-id abc123

# Add a new lead
instantly leads add \
  --email john@example.com \
  --first-name John \
  --last-name Doe \
  --company "Acme Corp" \
  --campaign-id abc123

# Add lead with custom variables
instantly leads add \
  --email jane@example.com \
  --campaign-id abc123 \
  --custom '{"role":"CEO","industry":"SaaS"}'

# Delete a lead
instantly leads delete --email john@example.com

# Update lead info
instantly leads update \
  --email john@example.com \
  --first-name Jonathan \
  --company "New Company Inc"

# Get specific lead
instantly leads get --email john@example.com

# List with pagination
instantly leads list --campaign-id abc123 --limit 50 --skip 100
```

### Campaigns

```bash
# List all campaigns
instantly campaigns list

# Get specific campaign
instantly campaigns get --id abc123

# Create new campaign
instantly campaigns create --name "Q1 2025 Outreach"

# Update campaign
instantly campaigns update --id abc123 --name "Q1 Updated"

# Pause campaign
instantly campaigns pause --id abc123

# Resume campaign
instantly campaigns resume --id abc123

# Delete campaign
instantly campaigns delete --id abc123
```

### Inbox

```bash
# List inbox messages
instantly inbox list --campaign-id abc123

# List only unread
instantly inbox list --unread

# Get specific thread
instantly inbox get --thread-id xyz789

# Reply to a lead
instantly inbox reply \
  --lead-email prospect@example.com \
  --message "Thanks for your interest! Let's schedule a call." \
  --campaign-id abc123

# Mark as read
instantly inbox mark-read --thread-id xyz789

# Pagination
instantly inbox list --limit 50 --skip 0
```

### Subsequences

```bash
# List subsequences for campaign
instantly subsequences list --campaign-id abc123

# Get specific subsequence
instantly subsequences get --id xyz789

# Create new subsequence
instantly subsequences create \
  --campaign-id abc123 \
  --name "Follow-up Day 3" \
  --delay-days 3

# Update subsequence
instantly subsequences update \
  --id xyz789 \
  --name "Updated Name" \
  --delay-days 5

# Delete subsequence
instantly subsequences delete --id xyz789
```

### Analytics

```bash
# Overall summary
instantly analytics summary

# Summary for date range
instantly analytics summary \
  --start-date 2025-01-01 \
  --end-date 2025-01-31

# Campaign analytics
instantly analytics campaign --id abc123

# Campaign analytics with date range
instantly analytics campaign \
  --id abc123 \
  --start-date 2025-01-01 \
  --end-date 2025-01-31

# Account-level analytics
instantly analytics account

# Lead statistics
instantly analytics leads --campaign-id abc123

# Lead stats by status
instantly analytics leads \
  --campaign-id abc123 \
  --status "replied"

# Email performance
instantly analytics emails --campaign-id abc123
```

### Raw API Access

Call **any** Instantly.ai v2 endpoint directly:

```bash
# GET request
instantly api GET /campaign/list

# POST with JSON data
instantly api POST /lead/add '{
  "email": "test@example.com",
  "campaign_id": "abc123",
  "first_name": "Test"
}'

# DELETE request
instantly api DELETE /lead/delete '{
  "email": "test@example.com"
}'

# Any undocumented or new endpoint
instantly api GET /new/endpoint/path
instantly api POST /custom/action '{"custom": "data"}'
```

**When to use raw API:**
- New endpoints not yet added to modules
- Custom/advanced endpoints
- Testing API responses
- Endpoints with complex parameters

## Response Format

All commands return JSON responses from the API, automatically formatted with `jq`.

## Error Handling

- Missing API key: Clear error message with setup instructions
- Invalid parameters: Shows command help
- API errors: Passes through API error responses

## Extension

### Adding New Module

Create `lib/new-module.sh`:

```bash
#!/bin/bash
# new-module.sh - Description

handle_new_module() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    action1) module_action1 "$@" ;;
    action2) module_action2 "$@" ;;
    -h|--help|help|"") module_help ;;
    *) echo "Unknown subcommand: $subcmd"; module_help; exit 1 ;;
  esac
}

module_help() {
  cat << EOF
Usage: instantly new-module <subcommand> [options]
...
EOF
}

module_action1() {
  # Implementation
  api_request GET "endpoint/path" | pretty_json
}
```

Update main `instantly` script to include it:

```bash
new-module)
  source "$SCRIPT_DIR/lib/new-module.sh"
  handle_new_module "$@"
  ;;
```

### Common Patterns

**GET with query params:**
```bash
api_request GET "endpoint?param1=value1&param2=value2"
```

**POST with JSON body:**
```bash
local data=$(jq -n \
  --arg key1 "$value1" \
  --arg key2 "$value2" \
  '{key1: $key1, key2: $key2}')
api_request POST "endpoint/path" "$data"
```

**Building dynamic query strings:**
```bash
local url="base/endpoint"
[[ -n "$param1" ]] && url="${url}?param1=$param1"
[[ -n "$param2" ]] && url="${url}&param2=$param2"
api_request GET "$url"
```

## API Key Authentication

Instantly.ai v2 uses API key authentication:
- GET requests: API key added as query parameter
- POST/PUT/DELETE: API key merged into JSON body

This is handled automatically by `lib/http.sh`.

## Dependencies

- `bash` 4.0+
- `curl`
- `jq`

## Tips

1. **Check API docs**: Instantly.ai v2 API documentation for endpoint specifics
2. **Use raw API for exploration**: Test new endpoints with `instantly api`
3. **Build modules incrementally**: Add commonly-used endpoints to modules
4. **Leverage jq**: Pipe output to jq for filtering: `instantly campaigns list | jq '.campaigns[] | select(.status=="active")'`

## Examples

### Bulk Add Leads from CSV

```bash
while IFS=, read -r email first_name last_name company; do
  instantly leads add \
    --email "$email" \
    --first-name "$first_name" \
    --last-name "$last_name" \
    --company "$company" \
    --campaign-id "your-campaign-id"
done < leads.csv
```

### Get All Active Campaign IDs

```bash
instantly campaigns list | jq -r '.campaigns[] | select(.status=="active") | .id'
```

### Monitor Inbox Replies

```bash
#!/bin/bash
while true; do
  instantly inbox list --unread | jq '.messages[] | {from: .from, subject: .subject}'
  sleep 300  # Check every 5 minutes
done
```

## Support

For API-specific questions, refer to [Instantly.ai API Documentation](https://developer.instantly.ai).

For this CLI tool: check `instantly <command> --help` or read the source in `lib/`.
