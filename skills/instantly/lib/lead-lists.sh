#!/bin/bash
# lead-lists.sh - Lead lists management (separate from campaigns)

handle_lead_lists() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    list)
      lead_lists_list "$@"
      ;;
    get)
      lead_lists_get "$@"
      ;;
    create)
      lead_lists_create "$@"
      ;;
    update)
      lead_lists_update "$@"
      ;;
    delete)
      lead_lists_delete "$@"
      ;;
    verification-stats)
      lead_lists_verification_stats "$@"
      ;;
    -h|--help|help|"")
      lead_lists_help
      ;;
    *)
      echo "Unknown lead-lists subcommand: $subcmd"
      lead_lists_help
      exit 1
      ;;
  esac
}

lead_lists_help() {
  cat << EOF
Usage: instantly lead-lists <subcommand> [options]

Lead Lists are separate from campaigns - they're used to organize and store leads
before adding them to campaigns.

Subcommands:
  list                List all lead lists
  get                 Get specific lead list
  create              Create a new lead list
  update              Update lead list
  delete              Delete a lead list
  verification-stats  Get email verification stats for a list

Examples:
  instantly lead-lists list
  instantly lead-lists create --name "Q1 Prospects"
  instantly lead-lists get --id list-id
  instantly lead-lists verification-stats --id list-id
EOF
}

lead_lists_list() {
  local limit=100 skip=0
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit) limit="$2"; shift 2 ;;
      --skip) skip="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; lead_lists_help; exit 1 ;;
    esac
  done
  
  api_request GET "lead-lists?limit=$limit&skip=$skip" | pretty_json
}

lead_lists_get() {
  local list_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) list_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; lead_lists_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$list_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "lead-lists/${list_id}" | pretty_json
}

lead_lists_create() {
  local name=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name) name="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; lead_lists_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$name" ]]; then
    echo "Error: --name required"
    exit 1
  fi
  
  local data=$(jq -n --arg name "$name" '{name: $name}')
  api_request POST "lead-lists" "$data" | pretty_json
}

lead_lists_update() {
  local list_id="" name=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) list_id="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; lead_lists_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$list_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  local data=$(jq -n --arg name "$name" '{name: $name}')
  api_request PATCH "lead-lists/${list_id}" "$data" | pretty_json
}

lead_lists_delete() {
  local list_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) list_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; lead_lists_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$list_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request DELETE "lead-lists/${list_id}" | pretty_json
}

lead_lists_verification_stats() {
  local list_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) list_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; lead_lists_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$list_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "lead-lists/${list_id}/verification-stats" | pretty_json
}
