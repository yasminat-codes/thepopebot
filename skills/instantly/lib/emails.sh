#!/bin/bash
# emails.sh - Complete email/inbox endpoint handlers (Reply Inbox - when leads reply)

handle_emails() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    list)
      emails_list "$@"
      ;;
    get)
      emails_get "$@"
      ;;
    reply)
      emails_reply "$@"
      ;;
    forward)
      emails_forward "$@"
      ;;
    mark-read)
      emails_mark_read "$@"
      ;;
    unread-count)
      emails_unread_count "$@"
      ;;
    update)
      emails_update "$@"
      ;;
    delete)
      emails_delete "$@"
      ;;
    list-replies)
      emails_list_replies "$@"
      ;;
    list-unread)
      emails_list_unread "$@"
      ;;
    -h|--help|help|"")
      emails_help
      ;;
    *)
      echo "Unknown emails subcommand: $subcmd"
      emails_help
      exit 1
      ;;
  esac
}

emails_help() {
  cat << EOF
Usage: instantly emails <subcommand> [options]

Subcommands:
  list           List all emails (inbox - includes replies from leads)
  list-replies   List only replies from leads
  list-unread    List only unread emails
  get            Get specific email by ID
  reply          Reply to an email from a lead
  forward        Forward an email
  mark-read      Mark thread as read
  unread-count   Get count of unread emails
  update         Update email properties (focused, status)
  delete         Delete an email

THE REPLY INBOX - When leads reply to your campaigns:
  The inbox shows ALL emails including:
  - Campaign emails you sent (ue_type=1)
  - REPLIES from leads (ue_type=2) ← This is the reply inbox!
  - Manually sent emails (ue_type=3)
  
Examples:
  # List all inbox emails (includes lead replies)
  instantly emails list --limit 50
  
  # List only replies from leads
  instantly emails list-replies --limit 20
  
  # List unread emails (new lead responses)
  instantly emails list-unread
  
  # Get specific email details
  instantly emails get --id abc123
  
  # Reply to a lead
  instantly emails reply --id reply-to-email-id --account your@email.com --subject "Re: Question" --body "Thanks for your interest!"
  
  # Mark thread as read
  instantly emails mark-read --thread-id thread-id
  
  # Count unread (new lead responses)
  instantly emails unread-count
EOF
}

emails_list() {
  local limit=50 campaign_id="" lead_email="" ue_type="" is_unread="" skip=0
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      --skip) skip="$2"; shift 2 ;;
      --campaign-id) campaign_id="$2"; shift 2 ;;
      --lead-email) lead_email="$2"; shift 2 ;;
      --type) ue_type="$2"; shift 2 ;;
      --unread) is_unread="1"; shift ;;
      *) echo "Unknown option: $1"; emails_help; exit 1 ;;
    esac
  done
  
  local url="emails?limit=$limit&skip=$skip"
  [[ -n "$campaign_id" ]] && url="${url}&campaign_id=$campaign_id"
  [[ -n "$lead_email" ]] && url="${url}&lead=$lead_email"
  [[ -n "$ue_type" ]] && url="${url}&ue_type=$ue_type"
  [[ -n "$is_unread" ]] && url="${url}&is_unread=1"
  
  api_request GET "$url" | pretty_json
}

emails_list_replies() {
  # List only emails that are replies from leads (ue_type=2)
  local limit="${1:-50}"
  
  echo "=== REPLY INBOX - Emails where leads replied to you ==="
  api_request GET "emails?limit=$limit&ue_type=2" | pretty_json
}

emails_list_unread() {
  # List only unread emails (includes new lead responses)
  local limit="${1:-50}"
  
  echo "=== UNREAD EMAILS - New responses from leads ==="
  api_request GET "emails?limit=$limit&is_unread=1" | pretty_json
}

emails_get() {
  local email_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) email_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; emails_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "emails/${email_id}" | pretty_json
}

emails_reply() {
  local reply_to_uuid="" account="" subject="" body_text="" body_html=""
  local cc="" bcc="" reminder_ts="" assigned_to=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id|--reply-to) reply_to_uuid="$2"; shift 2 ;;
      --account|--eaccount) account="$2"; shift 2 ;;
      --subject) subject="$2"; shift 2 ;;
      --body) body_text="$2"; shift 2 ;;
      --html) body_html="$2"; shift 2 ;;
      --cc) cc="$2"; shift 2 ;;
      --bcc) bcc="$2"; shift 2 ;;
      --reminder) reminder_ts="$2"; shift 2 ;;
      --assign-to) assigned_to="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; emails_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$reply_to_uuid" || -z "$account" || -z "$subject" ]]; then
    echo "Error: --id, --account, and --subject required"
    exit 1
  fi
  
  if [[ -z "$body_text" && -z "$body_html" ]]; then
    echo "Error: either --body or --html required"
    exit 1
  fi
  
  local body_obj=$(jq -n \
    --arg text "$body_text" \
    --arg html "$body_html" \
    '{
      text: (if $text != "" then $text else null end),
      html: (if $html != "" then $html else null end)
    }')
  
  local data=$(jq -n \
    --arg reply_to "$reply_to_uuid" \
    --arg eaccount "$account" \
    --arg subject "$subject" \
    --argjson body "$body_obj" \
    --arg cc "$cc" \
    --arg bcc "$bcc" \
    --arg reminder "$reminder_ts" \
    --arg assigned "$assigned_to" \
    '{
      reply_to_uuid: $reply_to,
      eaccount: $eaccount,
      subject: $subject,
      body: $body,
      cc_address_email_list: (if $cc != "" then $cc else null end),
      bcc_address_email_list: (if $bcc != "" then $bcc else null end),
      reminder_ts: (if $reminder != "" then $reminder else null end),
      assigned_to: (if $assigned != "" then $assigned else null end)
    }')
  
  api_request POST "emails/reply" "$data" | pretty_json
}

emails_forward() {
  local email_id="" to="" account="" subject="" body_text="" cc="" bcc=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) email_id="$2"; shift 2 ;;
      --to) to="$2"; shift 2 ;;
      --account|--eaccount) account="$2"; shift 2 ;;
      --subject) subject="$2"; shift 2 ;;
      --body) body_text="$2"; shift 2 ;;
      --cc) cc="$2"; shift 2 ;;
      --bcc) bcc="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; emails_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email_id" || -z "$to" || -z "$account" ]]; then
    echo "Error: --id, --to, and --account required"
    exit 1
  fi
  
  local body_obj=$(jq -n --arg text "$body_text" '{text: $text}')
  
  local data=$(jq -n \
    --arg id "$email_id" \
    --arg to "$to" \
    --arg eaccount "$account" \
    --arg subject "$subject" \
    --argjson body "$body_obj" \
    --arg cc "$cc" \
    --arg bcc "$bcc" \
    '{
      email_id: $id,
      to_address_email_list: $to,
      eaccount: $eaccount,
      subject: (if $subject != "" then $subject else null end),
      body: $body,
      cc_address_email_list: (if $cc != "" then $cc else null end),
      bcc_address_email_list: (if $bcc != "" then $bcc else null end)
    }')
  
  api_request POST "emails/forward" "$data" | pretty_json
}

emails_mark_read() {
  local thread_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --thread-id) thread_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; emails_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$thread_id" ]]; then
    echo "Error: --thread-id required"
    exit 1
  fi
  
  api_request POST "emails/threads/${thread_id}/mark-as-read" "{}" | pretty_json
}

emails_unread_count() {
  api_request GET "emails/unread/count" | pretty_json
}

emails_update() {
  local email_id="" is_focused="" i_status=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) email_id="$2"; shift 2 ;;
      --focused) is_focused="$2"; shift 2 ;;
      --status) i_status="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; emails_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg focused "$is_focused" \
    --arg status "$i_status" \
    '{
      is_focused: (if $focused != "" then ($focused | tonumber) else null end),
      i_status: (if $status != "" then ($status | tonumber) else null end)
    }')
  
  api_request PATCH "emails/${email_id}" "$data" | pretty_json
}

emails_delete() {
  local email_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) email_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; emails_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request DELETE "emails/${email_id}" | pretty_json
}
