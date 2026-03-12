#!/bin/bash
# Get Analytics for a Platform
#
# Fetches analytics for a specific platform with date range
#
# Usage: ./get-analytics.sh <platform> [days]
#   platform: instagram, facebook, tiktok, youtube, linkedin, twitter
#   days: number of days to look back (default: 30)

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly BASE_URL="https://app.metricool.com/api"

# Check environment
if [ -z "${METRICOOL_USER_TOKEN:-}" ] || [ -z "${METRICOOL_USER_ID:-}" ] || [ -z "${METRICOOL_BLOG_ID:-}" ]; then
  echo "Error: Set METRICOOL_USER_TOKEN, METRICOOL_USER_ID, and METRICOOL_BLOG_ID"
  exit 1
fi

# Get platform endpoints
get_endpoint() {
  local platform="$1"

  case "$platform" in
    instagram)
      echo "stats/instagram/posts"
      ;;
    instagram-reels)
      echo "stats/instagram/reels"
      ;;
    instagram-stories)
      echo "stats/instagram/stories"
      ;;
    facebook)
      echo "stats/facebook/posts"
      ;;
    facebook-reels)
      echo "stats/facebook/reels"
      ;;
    facebook-stories)
      echo "stats/facebook/stories"
      ;;
    tiktok)
      echo "stats/tiktok/videos"
      ;;
    youtube)
      echo "stats/youtube/videos"
      ;;
    linkedin)
      echo "stats/linkedin/posts"
      ;;
    twitter|x)
      echo "stats/twitter/posts"
      ;;
    twitch)
      echo "stats/twitch/videos"
      ;;
    *)
      echo "Unknown platform: $platform" >&2
      return 1
      ;;
  esac
}

# Main
main() {
  if [ $# -lt 1 ]; then
    echo "Usage: $0 <platform> [days]" >&2
    echo "" >&2
    echo "Platforms:" >&2
    echo "  instagram, instagram-reels, instagram-stories" >&2
    echo "  facebook, facebook-reels, facebook-stories" >&2
    echo "  tiktok, youtube, linkedin, twitter, twitch" >&2
    echo "" >&2
    echo "Days: Number of days to look back (default: 30)" >&2
    exit 1
  fi

  local platform="$1"
  local days="${2:-30}"

  # Get endpoint
  local endpoint
  endpoint=$(get_endpoint "$platform") || exit 1

  # Calculate timestamps
  local end_ts
  end_ts=$(date +%s)
  local start_ts
  start_ts=$(date -d "${days} days ago" +%s 2>/dev/null || date -v-${days}d +%s)

  echo "Fetching $platform analytics for last $days days..." >&2
  echo "Start: $(date -d "@$start_ts" '+%Y-%m-%d' 2>/dev/null || date -r "$start_ts" '+%Y-%m-%d')" >&2
  echo "End: $(date '+%Y-%m-%d')" >&2
  echo "" >&2

  # Make request
  curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
    "${BASE_URL}/${endpoint}?blogId=${METRICOOL_BLOG_ID}&userId=${METRICOOL_USER_ID}&start=${start_ts}&end=${end_ts}" | \
    jq '.'
}

main "$@"
