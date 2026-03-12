#!/usr/bin/env bash
# post-tool.sh — task-master PostToolUse hook
# Validates task files have all required sections + logs audit trail
# Invoked automatically after every Write/Edit tool call
# Exit behavior: warn-only (always exits 0 — never blocks the skill)
#
# NOTE: -e intentionally omitted from set flags — this hook must never
# crash or block Claude. Bash 3.2-compatible (no declare -A).

set -uo pipefail

# Only process task files in tasks/_pending/
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
FILE_PATH="${CLAUDE_FILE_PATH:-unknown}"

# Skip if not a Write/Edit on a task file
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" ]]; then
  exit 0
fi

if [[ "$FILE_PATH" != tasks/_pending/*.md ]]; then
  exit 0
fi

# Setup audit log directory
AUDIT_LOG=".claude/logs/task-master-audit.log"
mkdir -p ".claude/logs" 2>/dev/null || true

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "unknown")
LINE_COUNT=$(wc -l < "$FILE_PATH" 2>/dev/null | tr -d ' ' || echo "0")
WARNINGS=()
MISSING=()

# Required section checks — parallel indexed arrays (bash 3.2 compatible)
SECTION_NAMES=(
  "task_number"
  "status"
  "blocked_by"
  "summary"
  "files_to_read"
  "relevant_rules"
  "checklist"
  "success_criteria"
  "testing"
  "task_management"
  "definition_of_done"
)
SECTION_PATTERNS=(
  "^# Task [0-9]"
  "^\*\*Status:\*\*"
  "^\*\*BlockedBy:\*\*"
  "^## Summary"
  "^## Files to Read"
  "^## Relevant Rules"
  "^## Implementation Checklist"
  "^## Success Criteria"
  "^## Testing"
  "^## Task Management"
  "^## Definition of Done"
)

for i in "${!SECTION_NAMES[@]}"; do
  if ! grep -qE "${SECTION_PATTERNS[$i]}" "$FILE_PATH" 2>/dev/null; then
    MISSING+=("${SECTION_NAMES[$i]}")
  fi
done

# Line count check
if [[ "$LINE_COUNT" -gt 120 ]]; then
  WARNINGS+=("OVERSIZED: $LINE_COUNT lines (limit: 120 — split this task)")
elif [[ "$LINE_COUNT" -gt 90 ]]; then
  WARNINGS+=("LARGE: $LINE_COUNT lines (consider splitting)")
fi

# Compose audit log entry
SECTIONS_STATUS="ALL_PRESENT"
MISSING_STR="—"
if [[ ${#MISSING[@]} -gt 0 ]]; then
  SECTIONS_STATUS="MISSING_SECTIONS"
  MISSING_STR="${MISSING[*]}"
fi

echo "$TIMESTAMP | WRITTEN | $FILE_PATH | $LINE_COUNT lines | $SECTIONS_STATUS | $MISSING_STR" >> "$AUDIT_LOG" 2>/dev/null || true

# Report missing sections as warnings (to stdout, not stderr)
if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "task-master hook: Missing sections in $FILE_PATH: ${MISSING[*]}"
  echo "  Fix these sections before this task file is usable by specs-to-commit."
fi

for warning in "${WARNINGS[@]}"; do
  echo "task-master hook: $warning in $FILE_PATH"
done

# Always exit 0 — observation hooks never block
exit 0
