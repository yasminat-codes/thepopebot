#!/bin/bash
# Metricool API Request Wrapper
#
# Generic request wrapper with authentication and error handling
#
# Usage: ./metricool-request.sh <endpoint> [additional_params...]

set -euo pipefail

# Configuration
readonly BASE_URL="https://app.metricool.com/api"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check environment variables
check_env() {
  local missing=()

  [ -z "${METRICOOL_USER_TOKEN:-}" ] && missing+=("METRICOOL_USER_TOKEN")
  [ -z "${METRICOOL_USER_ID:-}" ] && missing+=("METRICOOL_USER_ID")
  [ -z "${METRICOOL_BLOG_ID:-}" ] && missing+=("METRICOOL_BLOG_ID")

  if [ ${#missing[@]} -gt 0 ]; then
    echo "Error: Missing environment variables: ${missing[*]}" >&2
    echo "" >&2
    echo "Set them with:" >&2
    echo "  export METRICOOL_USER_TOKEN=your-token" >&2
    echo "  export METRICOOL_USER_ID=your-user-id" >&2
    echo "  export METRICOOL_BLOG_ID=your-brand-id" >&2
    exit 1
  fi
}

# Make API request with retry logic
api_request() {
  local endpoint="$1"
  shift
  local params="$*"

  local max_retries=3
  local retry_delay=1

  for attempt in $(seq 1 $max_retries); do
    local response
    local http_code

    response=$(curl -s -w "\n%{http_code}" \
      -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
      "${BASE_URL}/${endpoint}?blogId=${METRICOOL_BLOG_ID}&userId=${METRICOOL_USER_ID}${params:+&$params}")

    http_code=$(echo "$response" | tail -n 1)
    local body
    body=$(echo "$response" | sed '$d')

    case "$http_code" in
      200)
        echo "$body"
        return 0
        ;;
      429)
        echo "Rate limited. Waiting ${retry_delay}s before retry..." >&2
        sleep $retry_delay
        retry_delay=$((retry_delay * 2))
        ;;
      401)
        echo "Error: Unauthorized. Check your METRICOOL_USER_TOKEN." >&2
        exit 1
        ;;
      403)
        echo "Error: Forbidden. API access requires Advanced or Custom plan." >&2
        exit 1
        ;;
      404)
        echo "Error: Not found. Check your userId and blogId." >&2
        exit 1
        ;;
      *)
        echo "Error: HTTP $http_code" >&2
        echo "$body" >&2
        return 1
        ;;
    esac
  done

  echo "Error: Max retries exceeded" >&2
  return 1
}

# Main
main() {
  check_env

  if [ $# -lt 1 ]; then
    echo "Usage: $0 <endpoint> [params...]" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 admin/simpleProfiles" >&2
    echo "  $0 stats/instagram/posts 'start=1704067200&end=1706745600'" >&2
    echo "  $0 stats/rt/values" >&2
    exit 1
  fi

  local endpoint="$1"
  shift
  local params="${*:-}"

  api_request "$endpoint" "$params"
}

main "$@"
