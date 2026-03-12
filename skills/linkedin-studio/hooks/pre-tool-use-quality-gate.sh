#!/usr/bin/env bash
# =============================================================================
# pre-tool-use-quality-gate.sh — Claude Code PreToolUse Hook
# LinkedIn Studio Plugin
#
# Runs before ls:batch-scheduler and ls:content-calendar to validate post quality.
# Composes: humanizer-gate.sh + hook-strength.sh + duplicate-detector.sh
# =============================================================================

set -euo pipefail

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PASS=0
FAIL=1

# Expect POST_TEXT in environment (set by the calling skill)
if [[ -z "${POST_TEXT:-}" ]]; then
  echo "[quality-gate] No POST_TEXT provided — skipping validation" >&2
  exit $PASS
fi

FAILURES=0
WARNINGS=0

echo "══════════════════════════════════════════"
echo "  QUALITY GATE — Pre-Schedule Validation"
echo "══════════════════════════════════════════"

# Gate 1: Humanizer gate (AI detection)
echo ""
echo "── Gate 1: AI Detection ──"
if bash "${HOOKS_DIR}/humanizer-gate.sh" 2>&1; then
  echo "  Result: PASS"
else
  echo "  Result: FAIL — AI patterns detected"
  FAILURES=$((FAILURES + 1))
fi

# Gate 2: Hook strength
echo ""
echo "── Gate 2: Hook Strength ──"
if bash "${HOOKS_DIR}/hook-strength.sh" 2>&1; then
  echo "  Result: PASS"
else
  echo "  Result: FAIL — Hook score below 70"
  FAILURES=$((FAILURES + 1))
fi

# Gate 3: Duplicate detection
echo ""
echo "── Gate 3: Duplicate Detection ──"
if bash "${HOOKS_DIR}/duplicate-detector.sh" 2>&1; then
  echo "  Result: PASS"
else
  echo "  Result: FAIL — Content too similar to recent posts"
  FAILURES=$((FAILURES + 1))
fi

# Gate 4: Structure compliance
echo ""
echo "── Gate 4: Structure Compliance ──"
if bash "${HOOKS_DIR}/structure-compliance.sh" 2>&1; then
  echo "  Result: PASS"
else
  echo "  Result: FAIL — Structural violations found"
  FAILURES=$((FAILURES + 1))
fi

echo ""
echo "══════════════════════════════════════════"
if [[ $FAILURES -eq 0 ]]; then
  echo "  ALL GATES PASSED — ready to schedule"
  echo "══════════════════════════════════════════"
  exit $PASS
else
  echo "  ${FAILURES} GATE(S) FAILED — scheduling blocked"
  echo "  Fix issues above and retry."
  echo "══════════════════════════════════════════"
  exit $FAIL
fi
