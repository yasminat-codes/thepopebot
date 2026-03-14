#!/bin/bash
set -euo pipefail

# count-lines.sh — Count lines in SKILL.md and report status against tier limits
#
# Usage: count-lines.sh <skill-directory-path>
#
# Exit codes:
#   0 = within limit
#   1 = over limit or SKILL.md not found

SKILL_DIR="${1:?Usage: count-lines.sh <skill-directory-path>}"
SKILL_FILE="$SKILL_DIR/SKILL.md"

if [ ! -f "$SKILL_FILE" ]; then
    echo "ERROR: SKILL.md not found at $SKILL_FILE" >&2
    exit 1
fi

LINE_COUNT=$(wc -l < "$SKILL_FILE")

# Detect tier from frontmatter
TIER=$(grep "^tier:" "$SKILL_FILE" 2>/dev/null | head -1 | sed 's/tier:[[:space:]]*//' | tr -d '"' | xargs || echo "")

case "$TIER" in
    "1"|"starter"|"Starter")           LIMIT=300 ;;
    "2"|"intermediate"|"Intermediate") LIMIT=400 ;;
    "3"|"advanced"|"Advanced")         LIMIT=500 ;;
    "4"|"expert"|"Expert")             LIMIT=600 ;;
    *)                                  LIMIT=500 ;;
esac

REMAINING=$((LIMIT - LINE_COUNT))

echo "File:      $SKILL_FILE"
echo "Tier:      ${TIER:-not detected}"
echo "Limit:     $LIMIT lines"
echo "Count:     $LINE_COUNT lines"

if [ "$LINE_COUNT" -gt "$LIMIT" ]; then
    echo "Status:    OVER by $((LINE_COUNT - LIMIT)) lines — must trim before publishing"
    exit 1
elif [ "$REMAINING" -le 30 ]; then
    echo "Status:    WARNING — only $REMAINING lines remaining"
    exit 0
else
    echo "Status:    OK — $REMAINING lines remaining"
    exit 0
fi
