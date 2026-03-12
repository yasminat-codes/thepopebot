#!/bin/bash
# analytics.sh - Analytics and reporting endpoint handlers

handle_analytics() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    campaign)
      analytics_campaign "$@"
      ;;
    overview)
      analytics_overview "$@"
      ;;
    daily)
      analytics_daily "$@"
      ;;
    steps)
      analytics_steps "$@"
      ;;
    account)
      analytics_account "$@"
      ;;
    warmup)
      analytics_warmup "$@"
      ;;
    account-daily)
      analytics_account_daily "$@"
      ;;
    -h|--help|help|"")
      analytics_help
      ;;
    *)
      echo "Unknown analytics subcommand: $subcmd"
      analytics_help
      exit 1
      ;;
  esac
}

analytics_help() {
  cat << EOF
Usage: instantly analytics <subcommand> [options]

Subcommands:
  campaign        Get campaign-specific analytics
  overview        Get campaign analytics overview
  daily           Get daily campaign analytics
  steps           Get campaign step analytics
  account         List accounts (for account management use 'instantly accounts')
  warmup          Get warmup analytics for accounts
  account-daily   Get daily account analytics

Examples:
  instantly analytics campaign --campaign-ids abc123,xyz789
  instantly analytics overview --campaign-ids abc123
  instantly analytics daily --campaign-id abc123
  instantly analytics steps --campaign-id abc123
  instantly analytics warmup --emails john@example.com
  instantly analytics account-daily --start-date 2025-01-01
EOF
}

analytics_campaign() {
  local campaign_ids="" start_date="" end_date=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --campaign-ids|--id) campaign_ids="$2"; shift 2 ;;
      --start-date) start_date="$2"; shift 2 ;;
      --end-date) end_date="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; analytics_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_ids" ]]; then
    echo "Error: --campaign-ids required"
    exit 1
  fi
  
  local url="campaigns/analytics?campaign_ids=$campaign_ids"
  [[ -n "$start_date" ]] && url="${url}&start_date=$start_date"
  [[ -n "$end_date" ]] && url="${url}&end_date=$end_date"
  
  api_request GET "$url" | pretty_json
}

analytics_overview() {
  local campaign_ids="" start_date="" end_date=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --campaign-ids|--id) campaign_ids="$2"; shift 2 ;;
      --start-date) start_date="$2"; shift 2 ;;
      --end-date) end_date="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; analytics_help; exit 1 ;;
    esac
  done
  
  local url="campaigns/analytics/overview"
  local params=""
  [[ -n "$campaign_ids" ]] && params="${params}&campaign_ids=$campaign_ids"
  [[ -n "$start_date" ]] && params="${params}&start_date=$start_date"
  [[ -n "$end_date" ]] && params="${params}&end_date=$end_date"
  
  if [[ -n "$params" ]]; then
    url="${url}?${params#&}"
  fi
  
  api_request GET "$url" | pretty_json
}

analytics_daily() {
  local campaign_id="" start_date="" end_date=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --campaign-id|--id) campaign_id="$2"; shift 2 ;;
      --start-date) start_date="$2"; shift 2 ;;
      --end-date) end_date="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; analytics_help; exit 1 ;;
    esac
  done
  
  local url="campaigns/analytics/daily"
  local params=""
  [[ -n "$campaign_id" ]] && params="${params}&campaign_id=$campaign_id"
  [[ -n "$start_date" ]] && params="${params}&start_date=$start_date"
  [[ -n "$end_date" ]] && params="${params}&end_date=$end_date"
  
  if [[ -n "$params" ]]; then
    url="${url}?${params#&}"
  fi
  
  api_request GET "$url" | pretty_json
}

analytics_steps() {
  local campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --campaign-id|--id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; analytics_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --campaign-id required"
    exit 1
  fi
  
  api_request GET "campaigns/analytics/steps?campaign_id=${campaign_id}" | pretty_json
}

analytics_account() {
  # List accounts (for full account management use 'instantly accounts')
  api_request GET "accounts?limit=100" | pretty_json
}

analytics_warmup() {
  local emails=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --emails|--email) emails="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; analytics_help; exit 1 ;;
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

analytics_account_daily() {
  local start_date="" end_date=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --start-date) start_date="$2"; shift 2 ;;
      --end-date) end_date="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; analytics_help; exit 1 ;;
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
