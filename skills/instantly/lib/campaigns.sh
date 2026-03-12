#!/bin/bash
# campaigns.sh - Campaign endpoint handlers

handle_campaigns() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    list)
      campaigns_list "$@"
      ;;
    get)
      campaigns_get "$@"
      ;;
    create)
      campaigns_create "$@"
      ;;
    update)
      campaigns_update "$@"
      ;;
    delete)
      campaigns_delete "$@"
      ;;
    pause)
      campaigns_pause "$@"
      ;;
    resume)
      campaigns_resume "$@"
      ;;
    search-by-contact)
      campaigns_search_by_contact "$@"
      ;;
    share)
      campaigns_share "$@"
      ;;
    create-from-export)
      campaigns_create_from_export "$@"
      ;;
    export)
      campaigns_export "$@"
      ;;
    duplicate)
      campaigns_duplicate "$@"
      ;;
    count-launched)
      campaigns_count_launched "$@"
      ;;
    add-variables)
      campaigns_add_variables "$@"
      ;;
    sending-status)
      campaigns_sending_status "$@"
      ;;
    -h|--help|help|"")
      campaigns_help
      ;;
    *)
      echo "Unknown campaigns subcommand: $subcmd"
      campaigns_help
      exit 1
      ;;
  esac
}

campaigns_help() {
  cat << EOF
Usage: instantly campaigns <subcommand> [options]

Subcommands:
  list                List all campaigns
  get                 Get campaign details
  create              Create a new campaign
  update              Update campaign settings
  delete              Delete a campaign
  pause               Pause a campaign
  resume              Resume a campaign
  search-by-contact   Search campaigns by lead email
  share               Share a campaign
  create-from-export  Create campaign from shared export
  export              Export campaign to JSON
  duplicate           Duplicate a campaign
  count-launched      Get count of launched campaigns
  add-variables       Add variables to campaign
  sending-status      Get campaign sending status

Examples:
  instantly campaigns list
  instantly campaigns get --id abc123
  instantly campaigns search-by-contact --email john@example.com
  instantly campaigns duplicate --id abc123
  instantly campaigns sending-status --id abc123
EOF
}

campaigns_list() {
  local limit=100
  local search="" status=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      --search) search="$2"; shift 2 ;;
      --status) status="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  local url="campaigns?limit=$limit"
  [[ -n "$search" ]] && url="${url}&search=$search"
  [[ -n "$status" ]] && url="${url}&status=$status"
  
  api_request GET "$url" | pretty_json
}

campaigns_get() {
  local campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "campaigns/${campaign_id}" | pretty_json
}

campaigns_create() {
  local name=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name) name="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$name" ]]; then
    echo "Error: --name required"
    exit 1
  fi
  
  # Minimal campaign with required fields
  local data=$(jq -n --arg name "$name" '{
    name: $name,
    campaign_schedule: {
      schedules: [{
        name: "Default Schedule",
        timing: {from: "09:00", to: "17:00"},
        days: {"1": true, "2": true, "3": true, "4": true, "5": true},
        timezone: "America/Detroit"
      }]
    }
  }')
  api_request POST "campaigns" "$data" | pretty_json
}

campaigns_update() {
  local campaign_id="" name=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  local data=$(jq -n --arg name "$name" '{name: $name}')
  api_request PATCH "campaigns/${campaign_id}" "$data" | pretty_json
}

campaigns_delete() {
  local campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request DELETE "campaigns/${campaign_id}" | pretty_json
}

campaigns_pause() {
  local campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request POST "campaigns/${campaign_id}/pause" "{}" | pretty_json
}

campaigns_resume() {
  local campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request POST "campaigns/${campaign_id}/activate" "{}" | pretty_json
}

campaigns_search_by_contact() {
  local email=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --email) email="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$email" ]]; then
    echo "Error: --email required"
    exit 1
  fi
  
  api_request GET "campaigns/search-by-contact?email=${email}" | pretty_json
}

campaigns_share() {
  local campaign_id="" user_ids=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      --user-ids) user_ids="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  local user_array=$(echo "$user_ids" | jq -R 'split(",")')
  local data=$(jq -n --argjson users "$user_array" '{user_ids: $users}')
  
  api_request POST "campaigns/${campaign_id}/share" "$data" | pretty_json
}

campaigns_create_from_export() {
  local export_data=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --data) export_data="$2"; shift 2 ;;
      --file) export_data=$(cat "$2"); shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$export_data" ]]; then
    echo "Error: --data or --file required"
    exit 1
  fi
  
  api_request POST "campaigns/create-from-export" "$export_data" | pretty_json
}

campaigns_export() {
  local campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request POST "campaigns/${campaign_id}/export" "{}" | pretty_json
}

campaigns_duplicate() {
  local campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request POST "campaigns/${campaign_id}/duplicate" "{}" | pretty_json
}

campaigns_count_launched() {
  api_request GET "campaigns/count-launched" | pretty_json
}

campaigns_add_variables() {
  local campaign_id="" variables=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      --variables) variables="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" || -z "$variables" ]]; then
    echo "Error: --id and --variables required"
    echo "Example: --variables '{\"custom_var\":\"value\"}'"
    exit 1
  fi
  
  api_request POST "campaigns/${campaign_id}/variables" "$variables" | pretty_json
}

campaigns_sending_status() {
  local campaign_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) campaign_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; campaigns_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "campaigns/${campaign_id}/sending-status" | pretty_json
}
