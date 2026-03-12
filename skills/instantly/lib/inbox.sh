#!/bin/bash
# inbox.sh - Inbox and reply endpoint handlers

handle_inbox() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    list)
      inbox_list "$@"
      ;;
    get)
      inbox_get "$@"
      ;;
    reply)
      inbox_reply "$@"
      ;;
    mark-read)
      inbox_mark_read "$@"
      ;;
    -h|--help|help|"")
      inbox_help
      ;;
    *)
      echo "Unknown inbox subcommand: $subcmd"
      inbox_help
      exit 1
      ;;
  esac
}

inbox_help() {
  cat << EOF
Usage: instantly inbox <subcommand> [options]

Subcommands:
  list        List inbox messages
  get         Get specific message thread
  reply       Send a reply to a lead
  mark-read   Mark message as read

Examples:
  instantly inbox list --campaign-id abc123
  instantly inbox get --thread-id xyz789
  instantly inbox reply --lead-email test@example.com --message "Thanks for your interest"
  instantly inbox mark-read --thread-id xyz789
EOF
}

inbox_list() {
  local campaign_id="" limit=50 skip=0
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --campaign-id) campaign_id="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      --skip) skip="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; inbox_help; exit 1 ;;
    esac
  done
  
  local url="emails?limit=$limit&skip=$skip"
  [[ -n "$campaign_id" ]] && url="${url}&campaign_id=$campaign_id"
  
  # Note: To filter unread, pipe to: jq '.items[] | select(.is_unread == 1)'
  api_request GET "$url" | pretty_json
}

inbox_get() {
  local thread_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --thread-id) thread_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; inbox_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$thread_id" ]]; then
    echo "Error: --thread-id required"
    exit 1
  fi
  
  api_request GET "inbox/get?thread_id=$thread_id" | pretty_json
}

inbox_reply() {
  local lead_email="" message="" campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --lead-email) lead_email="$2"; shift 2 ;;
      --message) message="$2"; shift 2 ;;
      --campaign-id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; inbox_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_email" || -z "$message" ]]; then
    echo "Error: --lead-email and --message required"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg email "$lead_email" \
    --arg msg "$message" \
    --arg campaign_id "$campaign_id" \
    '{lead_email: $email, message: $msg, campaign_id: $campaign_id}')
  
  api_request POST "inbox/reply" "$data" | pretty_json
}

inbox_mark_read() {
  local thread_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --thread-id) thread_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; inbox_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$thread_id" ]]; then
    echo "Error: --thread-id required"
    exit 1
  fi
  
  local data=$(jq -n --arg id "$thread_id" '{thread_id: $id}')
  api_request POST "inbox/mark-read" "$data" | pretty_json
}
