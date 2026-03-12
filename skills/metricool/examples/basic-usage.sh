#!/bin/bash
# Basic Metricool API Usage Examples
#
# Demonstrates common operations with the Metricool API

set -euo pipefail

# Ensure environment variables are set
if [ -z "${METRICOOL_USER_TOKEN:-}" ]; then
  echo "Set METRICOOL_USER_TOKEN first"
  exit 1
fi

echo "=== Metricool API Examples ==="
echo ""

# 1. Health Check
echo "1. Health Check"
echo "---"
curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/mtr/ping?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID"
echo ""
echo ""

# 2. List All Brands
echo "2. List All Brands"
echo "---"
curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/admin/simpleProfiles?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | \
  jq '.[].name'
echo ""
echo ""

# 3. Get Instagram Posts (Last 7 Days)
echo "3. Instagram Posts (Last 7 Days)"
echo "---"
end_ts=$(date +%s)
start_ts=$(date -d '7 days ago' +%s 2>/dev/null || date -v-7d +%s)

curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/instagram/posts?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=$start_ts&end=$end_ts" | \
  jq '.[0:3] | .[] | {id, likes, comments, caption: .caption[0:50]}'
echo ""
echo ""

# 4. Get Real-Time Stats
echo "4. Real-Time Stats"
echo "---"
curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/rt/values?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | \
  jq '.'
echo ""
echo ""

# 5. Get Demographics
echo "5. Instagram Demographics"
echo "---"
curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/gender/instagram?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID" | \
  jq '.'
echo ""
echo ""

# 6. Get Best Time to Post
echo "6. Best Time to Post"
echo "---"
curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/best_time_to_post?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&platform=instagram" | \
  jq '.'
echo ""

echo "=== Done ==="
