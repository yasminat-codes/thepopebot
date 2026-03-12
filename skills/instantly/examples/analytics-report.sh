#!/bin/bash
# Example: Generate a formatted analytics report for a campaign

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANTLY_CLI="$SCRIPT_DIR/../instantly"

if [[ $# -lt 1 ]]; then
  cat << EOF
Usage: $0 <campaign_id> [start_date] [end_date]

Generate analytics report for a campaign.

Examples:
  $0 abc123
  $0 abc123 2025-01-01 2025-01-31
EOF
  exit 1
fi

CAMPAIGN_ID="$1"
START_DATE="${2:-}"
END_DATE="${3:-}"

echo "================================"
echo "Campaign Analytics Report"
echo "================================"
echo

# Get campaign details
echo "Campaign: $CAMPAIGN_ID"
echo

# Build command
cmd="$INSTANTLY_CLI analytics campaign --id $CAMPAIGN_ID"
[[ -n "$START_DATE" ]] && cmd="$cmd --start-date $START_DATE"
[[ -n "$END_DATE" ]] && cmd="$cmd --end-date $END_DATE"

# Fetch analytics
analytics=$($cmd 2>/dev/null || echo '{}')

if [[ "$analytics" == "{}" ]]; then
  echo "Error: Could not fetch analytics"
  exit 1
fi

# Parse and display key metrics
echo "📊 Key Metrics:"
echo "$analytics" | jq -r '
  "  Emails Sent:     \(.emails_sent // 0)",
  "  Delivered:       \(.delivered // 0)",
  "  Opened:          \(.opened // 0) (\(.open_rate // 0)%)",
  "  Clicked:         \(.clicked // 0) (\(.click_rate // 0)%)",
  "  Replied:         \(.replied // 0) (\(.reply_rate // 0)%)",
  "  Bounced:         \(.bounced // 0)",
  "  Unsubscribed:    \(.unsubscribed // 0)"
'

echo
echo "📈 Engagement:"
echo "$analytics" | jq -r '
  "  Positive Replies: \(.positive_replies // 0)",
  "  Neutral Replies:  \(.neutral_replies // 0)",
  "  Negative Replies: \(.negative_replies // 0)"
'

echo
echo "💰 Conversion:"
echo "$analytics" | jq -r '
  "  Meetings Booked:  \(.meetings_booked // 0)",
  "  Deals Created:    \(.deals_created // 0)",
  "  Revenue:          $\(.revenue // 0)"
'

echo
echo "================================"
echo "Full JSON response saved to: campaign_${CAMPAIGN_ID}_analytics.json"
echo "$analytics" | jq '.' > "campaign_${CAMPAIGN_ID}_analytics.json"
