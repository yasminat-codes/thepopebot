#!/bin/bash
# accounts.sh - Email sending accounts endpoint handlers

handle_accounts() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    list)
      accounts_list "$@"
      ;;
    get)
      accounts_get "$@"
      ;;
    create)
      accounts_create "$@"
      ;;
    update)
      accounts_update "$@"
      ;;
    delete)
      accounts_delete "$@"
      ;;
    pause)
      accounts_pause "$@"
      ;;
    resume)
      accounts_resume "$@"
      ;;
    warmup-enable)
      accounts_warmup_enable "$@"
      ;;
    warmup-disable)
      accounts_warmup_disable "$@"
      ;;
    warmup-analytics)
      accounts_warmup_analytics "$@"
      ;;
    daily-analytics)
      accounts_daily_analytics "$@"
      ;;
    test-vitals)
      accounts_test_vitals "$@"
      ;;
    -h|--help|help|"")
      accounts_help
      ;;
    *)
      echo "Unknown accounts subcommand: $subcmd"
      accounts_help
      exit 1
      ;;
  esac
}

accounts_help() {
  cat << EOF
Usage: instantly accounts <subcommand> [options]

Subcommands:
  list              List all email sending accounts
  get               Get specific account details
  create            Create a new sending account
  update            Update account settings
  delete            Delete an account
  pause             Pause an account
  resume            Resume a paused account
  warmup-enable     Enable warmup for accounts
  warmup-disable    Disable warmup for accounts
  warmup-analytics  Get warmup analytics
  daily-analytics   Get daily account analytics
  test-vitals       Test account connection vitals

Examples:
  instantly accounts list
  instantly accounts get --email john@example.com
  instantly accounts pause --email john@example.com
  instantly accounts resume --email john@example.com
  instantly accounts warmup-enable --emails john@example.com,jane@example.com
  instantly accounts warmup-analytics --emails john@example.com
  instantly accounts daily-analytics
  instantly accounts test-vitals --email john@example.com
EOF
}

accounts_list() {
  local limit=100
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  api_request GET "accounts?limit=$limit" | pretty_json
}

accounts_get() {
  local email=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --email) email="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email" ]]; then
    echo "Error: --email required"
    exit 1
  fi
  
  api_request GET "accounts/${email}" | pretty_json
}

accounts_create() {
  echo "Note: Account creation requires IMAP/SMTP credentials"
  echo "Use OAuth endpoints for Google/Microsoft accounts"
  echo "For manual account setup, use the Instantly dashboard"
  echo ""
  echo "Example raw API call for custom IMAP/SMTP:"
  echo "instantly api POST accounts '{
    \"email\": \"user@example.com\",
    \"first_name\": \"John\",
    \"last_name\": \"Doe\",
    \"provider_code\": 1,
    \"imap_username\": \"user\",
    \"imap_password\": \"pass\",
    \"imap_host\": \"imap.example.com\",
    \"imap_port\": 993,
    \"smtp_username\": \"user\",
    \"smtp_password\": \"pass\",
    \"smtp_host\": \"smtp.example.com\",
    \"smtp_port\": 587
  }'"
}

accounts_update() {
  local email="" daily_limit="" sending_gap="" signature=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --email) email="$2"; shift 2 ;;
      --daily-limit) daily_limit="$2"; shift 2 ;;
      --sending-gap) sending_gap="$2"; shift 2 ;;
      --signature) signature="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email" ]]; then
    echo "Error: --email required"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg daily_limit "$daily_limit" \
    --arg sending_gap "$sending_gap" \
    --arg signature "$signature" \
    '{
      daily_limit: (if $daily_limit != "" then ($daily_limit | tonumber) else null end),
      sending_gap: (if $sending_gap != "" then ($sending_gap | tonumber) else null end),
      signature: (if $signature != "" then $signature else null end)
    }')
  
  api_request PATCH "accounts/${email}" "$data" | pretty_json
}

accounts_delete() {
  local email=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --email) email="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email" ]]; then
    echo "Error: --email required"
    exit 1
  fi
  
  api_request DELETE "accounts/${email}" | pretty_json
}

accounts_pause() {
  local email=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --email) email="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email" ]]; then
    echo "Error: --email required"
    exit 1
  fi
  
  api_request POST "accounts/${email}" "{\"type\":\"pause\"}" | pretty_json
}

accounts_resume() {
  local email=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --email) email="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email" ]]; then
    echo "Error: --email required"
    exit 1
  fi
  
  api_request POST "accounts/${email}" "{\"type\":\"resume\"}" | pretty_json
}

accounts_warmup_enable() {
  local emails=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --emails|--email) emails="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$emails" ]]; then
    echo "Error: --emails required (comma-separated)"
    exit 1
  fi
  
  # Convert comma-separated to JSON array
  local email_array=$(echo "$emails" | jq -R 'split(",")')
  local data=$(jq -n --argjson emails "$email_array" '{emails: $emails}')
  
  api_request POST "accounts/warmup/enable" "$data" | pretty_json
}

accounts_warmup_disable() {
  local emails=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --emails|--email) emails="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$emails" ]]; then
    echo "Error: --emails required (comma-separated)"
    exit 1
  fi
  
  local email_array=$(echo "$emails" | jq -R 'split(",")')
  local data=$(jq -n --argjson emails "$email_array" '{emails: $emails}')
  
  api_request POST "accounts/warmup/disable" "$data" | pretty_json
}

accounts_warmup_analytics() {
  local emails=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --emails|--email) emails="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$emails" ]]; then
    echo "Error: --emails required (comma-separated)"
    exit 1
  fi
  
  local email_array=$(echo "$emails" | jq -R 'split(",")')
  local data=$(jq -n --argjson emails "$email_array" '{emails: $emails}')
  
  api_request POST "accounts/warmup-analytics" "$data" | pretty_json
}

accounts_daily_analytics() {
  local start_date="" end_date=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --start-date) start_date="$2"; shift 2 ;;
      --end-date) end_date="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  local data=$(jq -n \
    --arg start "$start_date" \
    --arg end "$end_date" \
    '{
      start_date: (if $start != "" then $start else null end),
      end_date: (if $end != "" then $end else null end)
    }')
  
  api_request POST "accounts/analytics/daily" "$data" | pretty_json
}

accounts_test_vitals() {
  local email=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --email) email="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; accounts_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email" ]]; then
    echo "Error: --email required"
    exit 1
  fi
  
  api_request GET "accounts/test/vitals?email=${email}" | pretty_json
}
