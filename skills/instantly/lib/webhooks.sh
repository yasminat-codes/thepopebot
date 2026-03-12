#!/bin/bash
# webhooks.sh - Webhook management for automation

handle_webhooks() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    list)
      webhooks_list "$@"
      ;;
    get)
      webhooks_get "$@"
      ;;
    create)
      webhooks_create "$@"
      ;;
    update)
      webhooks_update "$@"
      ;;
    delete)
      webhooks_delete "$@"
      ;;
    test)
      webhooks_test "$@"
      ;;
    events)
      webhooks_events "$@"
      ;;
    events-summary)
      webhooks_events_summary "$@"
      ;;
    event-types)
      webhooks_event_types "$@"
      ;;
    -h|--help|help|"")
      webhooks_help
      ;;
    *)
      echo "Unknown webhooks subcommand: $subcmd"
      webhooks_help
      exit 1
      ;;
  esac
}

webhooks_help() {
  cat << EOF
Usage: instantly webhooks <subcommand> [options]

Webhooks allow you to receive real-time notifications for events like:
- lead.replied - When a lead replies to your email
- lead.clicked - When a lead clicks a link
- lead.opened - When a lead opens an email
- campaign.completed - When a campaign finishes
- And more...

Subcommands:
  list             List all webhooks
  get              Get specific webhook
  create           Create a new webhook
  update           Update webhook
  delete           Delete webhook
  test             Test webhook delivery
  events           List webhook events (delivery history)
  events-summary   Get webhook events summary

Examples:
  # Create webhook for lead replies
  instantly webhooks create \
    --url "https://your-app.com/webhook" \
    --events "lead.replied,lead.clicked"
  
  # List all webhooks
  instantly webhooks list
  
  # Check webhook delivery history
  instantly webhooks events --webhook-id abc123
  
  # Test webhook
  instantly webhooks test --id abc123
EOF
}

webhooks_list() {
  local limit=100
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; webhooks_help; exit 1 ;;
    esac
  done
  
  api_request GET "webhooks?limit=$limit" | pretty_json
}

webhooks_get() {
  local webhook_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) webhook_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; webhooks_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$webhook_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "webhooks/${webhook_id}" | pretty_json
}

webhooks_create() {
  local url="" event_type="" secret=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --url) url="$2"; shift 2 ;;
      --events|--event|--event-type) event_type="$2"; shift 2 ;;
      --secret) secret="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; webhooks_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$url" || -z "$event_type" ]]; then
    echo "Error: --url and --events required"
    echo ""
    echo "Available event types (use one per webhook):"
    echo "  - reply_received"
    echo "  - link_clicked"
    echo "  - email_opened"
    echo "  - email_bounced"
    echo "  - campaign_completed"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg url "$url" \
    --arg event "$event_type" \
    --arg secret "$secret" \
    '{
      target_hook_url: $url,
      event_type: $event,
      secret: (if $secret != "" then $secret else null end)
    }')
  
  api_request POST "webhooks" "$data" | pretty_json
}

webhooks_update() {
  local webhook_id="" url="" event_type="" is_active=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) webhook_id="$2"; shift 2 ;;
      --url) url="$2"; shift 2 ;;
      --events|--event|--event-type) event_type="$2"; shift 2 ;;
      --active) is_active="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; webhooks_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$webhook_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  # Build data object with only non-empty fields
  local data="{"
  local needs_comma=false
  
  if [[ -n "$url" ]]; then
    data="$data\"target_hook_url\":\"$url\""
    needs_comma=true
  fi
  
  if [[ -n "$event_type" ]]; then
    [[ "$needs_comma" == "true" ]] && data="$data,"
    data="$data\"event_type\":\"$event_type\""
    needs_comma=true
  fi
  
  if [[ -n "$is_active" ]]; then
    [[ "$needs_comma" == "true" ]] && data="$data,"
    if [[ "$is_active" == "true" ]]; then
      data="$data\"is_active\":true"
    else
      data="$data\"is_active\":false"
    fi
  fi
  
  data="$data}"
  
  api_request PATCH "webhooks/${webhook_id}" "$data" | pretty_json
}

webhooks_delete() {
  local webhook_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) webhook_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; webhooks_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$webhook_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request DELETE "webhooks/${webhook_id}" | pretty_json
}

webhooks_test() {
  local webhook_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) webhook_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; webhooks_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$webhook_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request POST "webhooks/${webhook_id}/test" "{}" | pretty_json
}

webhooks_events() {
  local webhook_id="" limit=50
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --webhook-id|--id) webhook_id="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; webhooks_help; exit 1 ;;
    esac
  done
  
  local url="webhook-events?limit=$limit"
  [[ -n "$webhook_id" ]] && url="${url}&webhook_id=$webhook_id"
  
  api_request GET "$url" | pretty_json
}

webhooks_events_summary() {
  api_request GET "webhook-events/summary" | pretty_json
}

webhooks_event_types() {
  cat << EOF
Available Webhook Event Types:

  reply_received       - Triggered when a lead replies to your email
  link_clicked         - Triggered when a lead clicks a link in your email
  email_opened         - Triggered when a lead opens your email
  email_bounced        - Triggered when an email bounces
  campaign_completed   - Triggered when a campaign completes
  campaign_started     - Triggered when a campaign starts

Usage:
  instantly webhooks create --url "https://your-app.com/webhook" --events "reply_received"

Note: Create one webhook per event type.
EOF
}
