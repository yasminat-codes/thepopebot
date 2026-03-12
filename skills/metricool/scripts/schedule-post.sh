#!/bin/bash
# Schedule a Post
#
# Schedule a post to be published later
#
# Usage: ./schedule-post.sh <platform> <message> <scheduled_time> [image_url]
#   platform: instagram, facebook, twitter, linkedin
#   message: Post caption/text
#   scheduled_time: ISO 8601 datetime or Unix timestamp
#   image_url: Optional image URL

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly BASE_URL="https://app.metricool.com/api"

# Check environment
if [ -z "${METRICOOL_USER_TOKEN:-}" ] || [ -z "${METRICOOL_USER_ID:-}" ] || [ -z "${METRICOOL_BLOG_ID:-}" ]; then
  echo "Error: Set METRICOOL_USER_TOKEN, METRICOOL_USER_ID, and METRICOOL_BLOG_ID"
  exit 1
fi

# Convert time to Unix timestamp
to_timestamp() {
  local time_input="$1"

  # If already a number, return it
  if [[ "$time_input" =~ ^[0-9]+$ ]]; then
    echo "$time_input"
    return
  fi

  # Try to parse as ISO 8601
  date -d "$time_input" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "$time_input" +%s 2>/dev/null || {
    echo "Error: Could not parse time: $time_input" >&2
    exit 1
  }
}

# Main
main() {
  if [ $# -lt 3 ]; then
    echo "Usage: $0 <platform> <message> <scheduled_time> [image_url]" >&2
    echo "" >&2
    echo "Platforms: instagram, facebook, twitter, linkedin" >&2
    echo "" >&2
    echo "Scheduled time formats:" >&2
    echo "  Unix timestamp: 1704067200" >&2
    echo "  ISO 8601: 2024-01-01T12:00:00" >&2
    echo "  Relative: 'tomorrow 10:00'" >&2
    echo "" >&2
    echo "Examples:" >&2
    echo "  $0 instagram 'Hello world!' '2024-01-15T10:00:00'" >&2
    echo "  $0 facebook 'Check this out!' 'tomorrow 14:00' 'https://example.com/image.jpg'" >&2
    exit 1
  fi

  local platform="$1"
  local message="$2"
  local scheduled_time="$3"
  local image_url="${4:-}"

  # Convert time
  local timestamp
  timestamp=$(to_timestamp "$scheduled_time")

  echo "Platform: $platform" >&2
  echo "Message: $message" >&2
  echo "Scheduled: $(date -d "@$timestamp" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r "$timestamp" '+%Y-%m-%d %H:%M:%S')" >&2
  [ -n "$image_url" ] && echo "Image: $image_url" >&2
  echo "" >&2

  # Build JSON payload
  local json_payload
  json_payload=$(cat <<EOF
{
  "platform": "$platform",
  "text": "$message",
  "scheduledAt": $timestamp
  ${image_url:+, "mediaUrl": "$image_url"}
}
EOF
)

  # Make request
  echo "Scheduling post..." >&2

  curl -s -X POST \
    -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$json_payload" \
    "${BASE_URL}/stats/schedule_post?blogId=${METRICOOL_BLOG_ID}&userId=${METRICOOL_USER_ID}" | \
    jq '.'
}

main "$@"
