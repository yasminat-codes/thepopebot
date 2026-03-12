#!/bin/bash
# Install cron job for meeting prep auto-trigger
# Runs every 30 minutes to check for new discovery calls

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
AUTO_TRIGGER_SCRIPT="$SCRIPT_DIR/scripts/auto_trigger.py"

# Make sure auto_trigger.py is executable
chmod +x "$AUTO_TRIGGER_SCRIPT"

# Create cron job entry
CRON_JOB="*/30 * * * * cd $SCRIPT_DIR && /usr/bin/uv run $AUTO_TRIGGER_SCRIPT >> /home/clawdbot/clawd/skills/meeting-prep/logs/auto_trigger.log 2>&1"

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Add to crontab (remove old entry first if exists)
(crontab -l 2>/dev/null | grep -v "auto_trigger.py"; echo "$CRON_JOB") | crontab -

echo "✅ Cron job installed!"
echo "   Runs every 30 minutes"
echo "   Logs: $SCRIPT_DIR/logs/auto_trigger.log"
echo ""
echo "To view current crontab:"
echo "   crontab -l"
echo ""
echo "To test manually:"
echo "   uv run $AUTO_TRIGGER_SCRIPT --dry-run"
