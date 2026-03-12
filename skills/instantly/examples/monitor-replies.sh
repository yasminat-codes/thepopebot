#!/bin/bash
# Example: Monitor inbox for new replies and send notifications

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTANTLY_CLI="$SCRIPT_DIR/../instantly"
CHECK_INTERVAL=300  # 5 minutes

echo "Monitoring Instantly inbox for new replies..."
echo "Checking every $CHECK_INTERVAL seconds. Press Ctrl+C to stop."
echo

while true; do
  timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  
  # Get unread messages
  unread=$("$INSTANTLY_CLI" inbox list --unread 2>/dev/null || echo '{"messages":[]}')
  
  # Count unread
  count=$(echo "$unread" | jq '.messages | length' 2>/dev/null || echo "0")
  
  if [[ "$count" -gt 0 ]]; then
    echo "[$timestamp] 📬 $count new reply(s)!"
    
    # Display details
    echo "$unread" | jq -r '.messages[] | "  • \(.from) - \(.subject)"'
    
    # You could add notification here:
    # - Send Telegram message
    # - Slack notification
    # - Desktop notification
    # - Email alert
    
  else
    echo "[$timestamp] No new replies"
  fi
  
  sleep "$CHECK_INTERVAL"
done
