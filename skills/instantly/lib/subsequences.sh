#!/bin/bash
# subsequences.sh - Campaign subsequence endpoint handlers

handle_subsequences() {
  local subcmd="${1:-}"
  shift || true
  
  case "$subcmd" in
    list)
      subsequences_list "$@"
      ;;
    get)
      subsequences_get "$@"
      ;;
    create)
      subsequences_create "$@"
      ;;
    update)
      subsequences_update "$@"
      ;;
    delete)
      subsequences_delete "$@"
      ;;
    duplicate)
      subsequences_duplicate "$@"
      ;;
    pause)
      subsequences_pause "$@"
      ;;
    resume)
      subsequences_resume "$@"
      ;;
    status)
      subsequences_status "$@"
      ;;
    -h|--help|help|"")
      subsequences_help
      ;;
    *)
      echo "Unknown subsequences subcommand: $subcmd"
      subsequences_help
      exit 1
      ;;
  esac
}

subsequences_help() {
  cat << EOF
Usage: instantly subsequences <subcommand> [options]

Subcommands:
  list       List subsequences for a campaign
  get        Get subsequence details
  create     Create a new subsequence
  update     Update subsequence
  delete     Delete a subsequence
  duplicate  Duplicate a subsequence
  pause      Pause a subsequence
  resume     Resume a paused subsequence
  status     Get subsequence sending status

Examples:
  instantly subsequences list --campaign-id abc123
  instantly subsequences get --id xyz789
  instantly subsequences create --campaign-id abc123 --name "Follow-up Day 3"
  instantly subsequences pause --id xyz789
  instantly subsequences status --id xyz789
EOF
}

subsequences_list() {
  local parent_campaign="" limit=100
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --campaign-id|--parent-campaign) parent_campaign="$2"; shift 2 ;;
      --limit) limit="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$parent_campaign" ]]; then
    echo "Error: --campaign-id required"
    exit 1
  fi
  
  local url="subsequences?parent_campaign=$parent_campaign&limit=$limit"
  
  api_request GET "$url" | pretty_json
}

subsequences_get() {
  local subseq_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) subseq_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$subseq_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "subsequences/${subseq_id}" | pretty_json
}

subsequences_create() {
  local campaign_id="" name="" interval_days="1" timezone="America/New_York"
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --campaign-id) campaign_id="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --interval-days|--delay-days) interval_days="$2"; shift 2 ;;
      --timezone) timezone="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$campaign_id" || -z "$name" ]]; then
    echo "Error: --campaign-id and --name required"
    exit 1
  fi
  
  # Get timezone from parent campaign if not specified
  if [[ "$timezone" == "America/New_York" ]]; then
    timezone=$(api_request GET "campaigns/${campaign_id}" | jq -r '.campaign_schedule.schedules[0].timezone // "America/New_York"')
  fi
  
  # Build minimal valid subsequence with required schema
  local data=$(jq -n \
    --arg campaign_id "$campaign_id" \
    --arg name "$name" \
    --argjson interval "$interval_days" \
    --arg tz "$timezone" \
    '{
      parent_campaign: $campaign_id,
      name: $name,
      interval_days: $interval,
      conditions: {
        type: "all",
        conditions: []
      },
      subsequence_schedule: {
        schedules: [
          {
            name: "Default Schedule",
            timing: {
              from: "09:00",
              to: "17:00"
            },
            days: {
              "1": true,
              "2": true,
              "3": true,
              "4": true,
              "5": true,
              "6": false,
              "7": false
            },
            timezone: $tz
          }
        ]
      },
      sequences: []
    }')
  
  api_request POST "subsequences" "$data" | pretty_json
}

subsequences_update() {
  local subseq_id="" name="" interval_days=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) subseq_id="$2"; shift 2 ;;
      --name) name="$2"; shift 2 ;;
      --interval-days) interval_days="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$subseq_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  local data=$(jq -n \
    --arg name "$name" \
    --arg interval "$interval_days" \
    '{
      name: (if $name != "" then $name else null end),
      interval_days: (if $interval != "" then ($interval | tonumber) else null end)
    }')
  
  api_request PATCH "subsequences/${subseq_id}" "$data" | pretty_json
}

subsequences_delete() {
  local subseq_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) subseq_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$subseq_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request DELETE "subsequences/${subseq_id}" | pretty_json
}

subsequences_duplicate() {
  local subseq_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) subseq_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$subseq_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request POST "subsequences/${subseq_id}/duplicate" "{}" | pretty_json
}

subsequences_pause() {
  local subseq_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) subseq_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$subseq_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request POST "subsequences/${subseq_id}/pause" "{}" | pretty_json
}

subsequences_resume() {
  local subseq_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) subseq_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$subseq_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request POST "subsequences/${subseq_id}/resume" "{}" | pretty_json
}

subsequences_status() {
  local subseq_id=""
  
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --id) subseq_id="$2"; shift 2 ;;
      *) echo "Unknown option: $1"; subsequences_help; exit 1 ;;
    esac
  done
  
  if [[ -z "$subseq_id" ]]; then
    echo "Error: --id required"
    exit 1
  fi
  
  api_request GET "subsequences/${subseq_id}/sending-status" | pretty_json
}
