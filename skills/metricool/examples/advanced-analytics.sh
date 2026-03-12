#!/bin/bash
# Advanced Analytics Example
#
# Demonstrates cross-platform analytics comparison and export

set -euo pipefail

# Configuration
OUTPUT_DIR="./analytics-export"
mkdir -p "$OUTPUT_DIR"

# Date range
end_ts=$(date +%s)
start_ts=$(date -d '30 days ago' +%s 2>/dev/null || date -v-30d +%s)
start_date=$(date -d "@$start_ts" '+%Y-%m-%d' 2>/dev/null || date -r "$start_ts" '+%Y-%m-%d')
end_date=$(date '+%Y-%m-%d')

echo "=== Advanced Analytics Export ==="
echo "Date Range: $start_date to $end_date"
echo ""

# Platform list
platforms=("instagram" "facebook" "tiktok" "youtube" "linkedin")

# Fetch analytics for each platform
for platform in "${platforms[@]}"; do
  echo "Fetching $platform analytics..."

  endpoint=""
  case "$platform" in
    instagram) endpoint="stats/instagram/posts" ;;
    facebook) endpoint="stats/facebook/posts" ;;
    tiktok) endpoint="stats/tiktok/videos" ;;
    youtube) endpoint="stats/youtube/videos" ;;
    linkedin) endpoint="stats/linkedin/posts" ;;
  esac

  curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
    "https://app.metricool.com/api/${endpoint}?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=$start_ts&end=$end_ts" \
    > "${OUTPUT_DIR}/${platform}.json"

  # Count posts
  count=$(jq 'length' "${OUTPUT_DIR}/${platform}.json" 2>/dev/null || echo "0")
  echo "  Found $count posts"
done

echo ""

# Calculate summary stats
echo "=== Summary Statistics ==="
echo ""

for platform in "${platforms[@]}"; do
  if [ -f "${OUTPUT_DIR}/${platform}.json" ]; then
    echo "$platform:"
    jq -r '
      if type == "array" and length > 0 then
        "  Total posts: \(length)"
      else
        "  No data"
      end
    ' "${OUTPUT_DIR}/${platform}.json" 2>/dev/null || echo "  Error parsing"
  fi
done

echo ""

# Get Facebook Ads if available
echo "=== Ads Performance ==="
curl -s -H "X-Mc-Auth: $METRICOOL_USER_TOKEN" \
  "https://app.metricool.com/api/stats/facebookads/campaigns?blogId=$METRICOOL_BLOG_ID&userId=$METRICOOL_USER_ID&start=$start_ts&end=$end_ts" \
  > "${OUTPUT_DIR}/facebook_ads.json"

jq '
  if type == "array" then
    {
      total_campaigns: length,
      total_spent: [.[] | .spent // 0] | add // 0,
      total_impressions: [.[] | .impressions // 0] | add // 0,
      total_clicks: [.[] | .clicks // 0] | add // 0
    }
  else
    .
  end
' "${OUTPUT_DIR}/facebook_ads.json" 2>/dev/null

echo ""

# Export combined report
echo "=== Exporting Combined Report ==="
cat <<EOF > "${OUTPUT_DIR}/report.json"
{
  "date_range": {
    "start": "$start_date",
    "end": "$end_date"
  },
  "platforms": {
EOF

first=true
for platform in "${platforms[@]}"; do
  if [ -f "${OUTPUT_DIR}/${platform}.json" ]; then
    if [ "$first" = true ]; then
      first=false
    else
      echo "," >> "${OUTPUT_DIR}/report.json"
    fi
    echo "    \"$platform\": $(jq '.' "${OUTPUT_DIR}/${platform}.json")" >> "${OUTPUT_DIR}/report.json"
  fi
done

cat <<EOF >> "${OUTPUT_DIR}/report.json"
  }
}
EOF

echo "Report saved to: ${OUTPUT_DIR}/report.json"
echo ""
echo "=== Done ==="
