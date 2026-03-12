#!/bin/bash
# leads.sh - Complete leads endpoint handlers with BULK operations

handle_leads() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    list)
      leads_list "$@"
      ;;
    get)
      leads_get "$@"
      ;;
    add)
      leads_add "$@"
      ;;
    bulk-add)
      leads_bulk_add "$@"
      ;;
    bulk-delete)
      leads_bulk_delete "$@"
      ;;
    bulk-assign)
      leads_bulk_assign "$@"
      ;;
    update)
      leads_update "$@"
      ;;
    delete)
      leads_delete "$@"
      ;;
    move)
      leads_move "$@"
      ;;
    move-to-subsequence)
      leads_move_to_subsequence "$@"
      ;;
    remove-from-subsequence)
      leads_remove_from_subsequence "$@"
      ;;
    update-interest)
      leads_update_interest "$@"
      ;;
    merge)
      leads_merge "$@"
      ;;
    -h|--help|help|"")
      leads_help
      ;;
    *)
      echo "Unknown leads subcommand: $subcmd"
      leads_help
      exit 1
      ;;
  esac
}

leads_help() {
  cat << EOF
Usage: instantly leads <subcommand> [options]

Subcommands:
  list                      List leads in a campaign or lead list
  get                       Get specific lead details
  add                       Add a single lead
  bulk-add                  Add multiple leads from CSV or JSON (RECOMMENDED)
  bulk-delete               Delete multiple leads at once
  bulk-assign               Assign multiple leads to users
  update                    Update lead information
  delete                    Delete a single lead
  move                      Move leads to another campaign/list
  move-to-subsequence       Move a lead to a subsequence
  remove-from-subsequence   Remove a lead from subsequence
  update-interest           Update lead interest status
  merge                     Merge two duplicate leads

Examples:
  # List leads
  instantly leads list --campaign-id abc123 --limit 100
  
  # Bulk add from CSV (RECOMMENDED for multiple leads)
  instantly leads bulk-add --csv leads.csv --campaign-id abc123
  
  # Bulk add from JSON
  instantly leads bulk-add --json '[{"email":"test@example.com","first_name":"John"}]' --campaign-id abc123
  
  # Single add
  instantly leads add --email test@example.com --first-name John --campaign-id abc123
  
  # Bulk delete
  instantly leads bulk-delete --emails "email1@example.com,email2@example.com"
  
  # Update interest status
  instantly leads update-interest --id lead-id --status 1
  
  # Move leads to another campaign
  instantly leads move --from-campaign old-id --to-campaign new-id
EOF
}

leads_list() {
  local campaign_id="" lead_list_id="" limit=100 search="" skip=0
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --campaign-id) campaign_id="$2"; shift 2 ;;
      --lead-list-id|--list-id) lead_list_id="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      --skip) skip="$2"; shift 2 ;;
      --search) search="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  local data=$(jq -n \
    --arg campaign_id "$campaign_id" \
    --arg lead_list_id "$lead_list_id" \
    --argjson limit "$limit" \
    --argjson skip "$skip" \
    --arg search "$search" \
    '{
      campaign_id: (if $campaign_id != "" then $campaign_id else null end),
      lead_list_id: (if $lead_list_id != "" then $lead_list_id else null end),
      limit: $limit,
      skip: $skip,
      search: (if $search != "" then $search else null end)
    }')
  
  api_request POST "leads/list" "$data" | pretty_json
}

leads_get() {
  local lead_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) lead_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "leads/${lead_id}" | pretty_json
}

leads_add() {
  local email="" first_name="" last_name="" company="" campaign_id="" list_id=""
  local phone="" website="" personalization="" skip_if_in_workspace="" skip_if_in_campaign=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --email) email="$2"; shift 2 ;;
      --first-name) first_name="$2"; shift 2 ;;
      --last-name) last_name="$2"; shift 2 ;;
      --company) company="$2"; shift 2 ;;
      --phone) phone="$2"; shift 2 ;;
      --website) website="$2"; shift 2 ;;
      --personalization) personalization="$2"; shift 2 ;;
      --campaign-id) campaign_id="$2"; shift 2 ;;
      --list-id) list_id="$2"; shift 2 ;;
      --skip-if-in-workspace) skip_if_in_workspace="true"; shift ;;
      --skip-if-in-campaign) skip_if_in_campaign="true"; shift ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email" ]]; then
    echo "Error: --email required"
    exit 1
  fi
  
  if [[ -z "$campaign_id" && -z "$list_id" ]]; then
    echo "Error: either --campaign-id or --list-id required"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg email "$email" \
    --arg first_name "$first_name" \
    --arg last_name "$last_name" \
    --arg company "$company" \
    --arg phone "$phone" \
    --arg website "$website" \
    --arg personalization "$personalization" \
    --arg campaign_id "$campaign_id" \
    --arg list_id "$list_id" \
    --arg skip_workspace "$skip_if_in_workspace" \
    --arg skip_campaign "$skip_if_in_campaign" \
    '{
      email: $email,
      first_name: (if $first_name != "" then $first_name else null end),
      last_name: (if $last_name != "" then $last_name else null end),
      company_name: (if $company != "" then $company else null end),
      phone: (if $phone != "" then $phone else null end),
      website: (if $website != "" then $website else null end),
      personalization: (if $personalization != "" then $personalization else null end),
      campaign: (if $campaign_id != "" then $campaign_id else null end),
      list_id: (if $list_id != "" then $list_id else null end),
      skip_if_in_workspace: ($skip_workspace == "true"),
      skip_if_in_campaign: ($skip_campaign == "true")
    }')
  
  api_request POST "leads" "$data" | pretty_json
}

leads_bulk_add() {
  local csv_file="" json_data="" campaign_id="" list_id="" skip_workspace="" skip_campaign=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --csv) csv_file="$2"; shift 2 ;;
      --json) json_data="$2"; shift 2 ;;
      --campaign-id) campaign_id="$2"; shift 2 ;;
      --list-id) list_id="$2"; shift 2 ;;
      --skip-if-in-workspace) skip_workspace="true"; shift ;;
      --skip-if-in-campaign) skip_campaign="true"; shift ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" && -z "$list_id" ]]; then
    echo "Error: either --campaign-id or --list-id required"
    exit 1
  fi
  
  local leads_array=""
  
  if [[ -n "$csv_file" ]]; then
    if [[ ! -f "$csv_file" ]]; then
      echo "Error: CSV file not found: $csv_file"
      exit 1
    fi
    
    # Convert CSV to JSON array
    leads_array=$(awk -F',' 'NR>1 && NF>=1 {
      gsub(/"/, "", $0);
      printf "{\"email\":\"%s\",\"first_name\":\"%s\",\"last_name\":\"%s\",\"company_name\":\"%s\",\"phone\":\"%s\",\"website\":\"%s\"},", $1, $2, $3, $4, $5, $6
    }' "$csv_file" | sed 's/,$//' | jq -s '.')
    
  elif [[ -n "$json_data" ]]; then
    leads_array="$json_data"
  else
    echo "Error: either --csv or --json required"
    exit 1
  fi
  
  # Build payload
  local data=$(jq -n \
    --arg campaign_id "$campaign_id" \
    --arg list_id "$list_id" \
    --argjson leads "$leads_array" \
    --arg skip_workspace "$skip_workspace" \
    --arg skip_campaign "$skip_campaign" \
    '{
      campaign_id: (if $campaign_id != "" then $campaign_id else null end),
      list_id: (if $list_id != "" then $list_id else null end),
      leads: $leads,
      skip_if_in_workspace: ($skip_workspace == "true"),
      skip_if_in_campaign: ($skip_campaign == "true")
    }')
  
  # Call REAL bulk endpoint: POST /api/v2/leads/bulk
  api_request POST "leads/bulk" "$data" | pretty_json
}

leads_bulk_delete() {
  local emails="" campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --emails) emails="$2"; shift 2 ;;
      --campaign-id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$emails" ]]; then
    echo "Error: --emails required (comma-separated)"
    exit 1
  fi
  
  local email_array=$(echo "$emails" | jq -R 'split(",")')
  local data=$(jq -n \
    --argjson emails "$email_array" \
    --arg campaign_id "$campaign_id" \
    '{
      emails: $emails,
      campaign_id: (if $campaign_id != "" then $campaign_id else null end)
    }')
  
  api_request DELETE "leads" "$data" | pretty_json
}

leads_bulk_assign() {
  local lead_ids="" user_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --lead-ids) lead_ids="$2"; shift 2 ;;
      --user-id) user_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_ids" || -z "$user_id" ]]; then
    echo "Error: --lead-ids and --user-id required"
    exit 1
  fi
  
  local id_array=$(echo "$lead_ids" | jq -R 'split(",")')
  local data=$(jq -n \
    --argjson ids "$id_array" \
    --arg user "$user_id" \
    '{lead_ids: $ids, user_id: $user}')
  
  api_request POST "leads/bulk-assign" "$data" | pretty_json
}

leads_update() {
  local lead_id="" first_name="" last_name="" company="" phone="" website=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) lead_id="$2"; shift 2 ;;
      --first-name) first_name="$2"; shift 2 ;;
      --last-name) last_name="$2"; shift 2 ;;
      --company) company="$2"; shift 2 ;;
      --phone) phone="$2"; shift 2 ;;
      --website) website="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg first_name "$first_name" \
    --arg last_name "$last_name" \
    --arg company "$company" \
    --arg phone "$phone" \
    --arg website "$website" \
    '{
      first_name: (if $first_name != "" then $first_name else null end),
      last_name: (if $last_name != "" then $last_name else null end),
      company_name: (if $company != "" then $company else null end),
      phone: (if $phone != "" then $phone else null end),
      website: (if $website != "" then $website else null end)
    }')
  
  api_request PATCH "leads/${lead_id}" "$data" | pretty_json
}

leads_delete() {
  local lead_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) lead_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request DELETE "leads/${lead_id}" | pretty_json
}

leads_move() {
  local from_campaign="" from_list="" to_campaign="" to_list="" lead_ids=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --from-campaign) from_campaign="$2"; shift 2 ;;
      --from-list) from_list="$2"; shift 2 ;;
      --to-campaign) to_campaign="$2"; shift 2 ;;
      --to-list) to_list="$2"; shift 2 ;;
      --lead-ids) lead_ids="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  local data=$(jq -n \
    --arg from_campaign "$from_campaign" \
    --arg from_list "$from_list" \
    --arg to_campaign "$to_campaign" \
    --arg to_list "$to_list" \
    --arg lead_ids "$lead_ids" \
    '{
      from_campaign_id: (if $from_campaign != "" then $from_campaign else null end),
      from_list_id: (if $from_list != "" then $from_list else null end),
      to_campaign_id: (if $to_campaign != "" then $to_campaign else null end),
      to_list_id: (if $to_list != "" then $to_list else null end),
      lead_ids: (if $lead_ids != "" then ($lead_ids | split(",")) else null end)
    }')
  
  api_request POST "leads/move" "$data" | pretty_json
}

leads_move_to_subsequence() {
  local lead_id="" subsequence_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id|--lead-id) lead_id="$2"; shift 2 ;;
      --subsequence-id) subsequence_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_id" || -z "$subsequence_id" ]]; then
    echo "Error: --id and --subsequence-id required"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg lead "$lead_id" \
    --arg subseq "$subsequence_id" \
    '{lead_id: $lead, subsequence_id: $subseq}')
  
  api_request POST "leads/move-to-subsequence" "$data" | pretty_json
}

leads_remove_from_subsequence() {
  local lead_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id|--lead-id) lead_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  local data=$(jq -n --arg id "$lead_id" '{lead_id: $id}')
  api_request POST "leads/remove-from-subsequence" "$data" | pretty_json
}

leads_update_interest() {
  local lead_id="" status=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id|--lead-id) lead_id="$2"; shift 2 ;;
      --status) status="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_id" || -z "$status" ]]; then
    echo "Error: --id and --status required"
    echo "Status values: 0=Out of Office, 1=Interested, 2=Meeting Booked, 3=Meeting Completed, 4=Closed"
    echo "              -1=Not Interested, -2=Wrong Person, -3=Lost, -4=No Show"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg id "$lead_id" \
    --argjson status "$status" \
    '{lead_id: $id, lt_interest_status: $status}')
  
  api_request POST "leads/update-interest-status" "$data" | pretty_json
}

leads_merge() {
  local lead_id_1="" lead_id_2=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --lead-1) lead_id_1="$2"; shift 2 ;;
      --lead-2) lead_id_2="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; leads_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$lead_id_1" || -z "$lead_id_2" ]]; then
    echo "Error: --lead-1 and --lead-2 required"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg id1 "$lead_id_1" \
    --arg id2 "$lead_id_2" \
    '{lead_id_1: $id1, lead_id_2: $id2}')
  
  api_request POST "leads/merge" "$data" | pretty_json
}
