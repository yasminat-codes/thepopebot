#!/usr/bin/env bash
# validate-tasks.sh — task-master pipeline handoff validator
# Usage: bash validate-tasks.sh [tasks-dir]
# Validates all task files before handing off to specs-to-commit
# Exit 0 = all valid, Exit 1 = validation failures found

set -euo pipefail

TASKS_DIR="${1:-tasks/_pending}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARNINGS=0

echo "Validating task files in: $TASKS_DIR"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [[ ! -d "$TASKS_DIR" ]]; then
  echo -e "${RED}✗ Directory not found: $TASKS_DIR${NC}"
  exit 1
fi

TASK_FILES=("$TASKS_DIR"/*.md)
if [[ ${#TASK_FILES[@]} -eq 0 ]] || [[ ! -f "${TASK_FILES[0]}" ]]; then
  echo -e "${RED}✗ No .md files found in $TASKS_DIR${NC}"
  exit 1
fi

for task_file in "${TASK_FILES[@]}"; do
  [[ -f "$task_file" ]] || continue
  filename=$(basename "$task_file")
  issues=()

  # 1. Filename format check: NNN-title.md
  if ! echo "$filename" | grep -qE "^[0-9]{3}(-[a-z0-9]+)+\.md$"; then
    issues+=("Filename must match NNN-kebab-title.md")
  fi

  # 2. Required sections (11 sections — Relevant Rules added 2026-03-02)
  required_patterns=(
    "^# Task [0-9]" "^\*\*Status:\*\*" "^\*\*BlockedBy:\*\*"
    "^## Summary" "^## Files to Read" "^## Relevant Rules"
    "^## Implementation Checklist"
    "^## Success Criteria" "^## Testing" "^## Task Management"
    "^## Definition of Done"
  )
  section_names=(
    "Task title NNN:" "Status field" "BlockedBy field"
    "Summary" "Files to Read" "Relevant Rules"
    "Implementation Checklist"
    "Success Criteria" "Testing" "Task Management"
    "Definition of Done"
  )

  for i in "${!required_patterns[@]}"; do
    if ! grep -qE "${required_patterns[$i]}" "$task_file" 2>/dev/null; then
      issues+=("Missing: ${section_names[$i]}")
    fi
  done

  # 3. BlockedBy syntax check
  # Valid formats: "—" (no deps), "[001]" (single), "[001, 002]" (multiple)
  blocked_line=$(grep -E "^\*\*BlockedBy:\*\*" "$task_file" 2>/dev/null || echo "")
  if [[ -n "$blocked_line" ]]; then
    if ! echo "$blocked_line" | grep -qE "\*\*BlockedBy:\*\* (—|\[([0-9]+(, ?[0-9]+)*)?\])"; then
      issues+=("Invalid BlockedBy syntax — expected — (no deps) or [NNN, NNN]")
    fi
  fi

  # 4. Dependency resolution check
  blocked_refs=$(grep -oE "\*\*BlockedBy:\*\* \[([0-9, ]+)\]" "$task_file" 2>/dev/null | grep -oE "[0-9]+" || echo "")
  for ref in $blocked_refs; do
    if ! ls "$TASKS_DIR"/"$ref"-*.md 2>/dev/null | grep -q .; then
      issues+=("Broken dependency: references task $ref which doesn't exist")
    fi
  done

  # 5. Testing section has content
  # Use flag-based awk to avoid range bug where ## Testing matches both start/end patterns
  testing_lines=$(awk 'BEGIN{p=0} /^## Testing/{p=1;next} p && /^## [A-Z]/{exit} p' "$task_file" | wc -l)
  if [[ "$testing_lines" -lt 5 ]]; then
    issues+=("Testing section too sparse (< 5 lines)")
  fi

  # Report
  if [[ ${#issues[@]} -eq 0 ]]; then
    echo -e "  ${GREEN}✓${NC} $filename"
    ((PASS++))
  else
    echo -e "  ${RED}✗${NC} $filename"
    for issue in "${issues[@]}"; do
      echo -e "    ${RED}→${NC} $issue"
    done
    ((FAIL++))
  fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC}"

if [[ $FAIL -gt 0 ]]; then
  echo -e "${RED}✗ Pipeline validation FAILED. Fix issues before running /specs-to-commit.${NC}"
  exit 1
else
  echo -e "${GREEN}✓ All tasks valid. Ready for /specs-to-commit.${NC}"
  exit 0
fi
