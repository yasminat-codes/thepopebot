#!/usr/bin/env bash
# =============================================================================
# stop-final-validation.sh — Claude Code Stop Hook
# LinkedIn Studio Plugin
#
# Runs at session end. Checks for unscheduled drafts, unresolved issues.
# Non-blocking — shows warnings but never prevents session exit.
# =============================================================================

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$HOOKS_DIR")"

# Source neon-utils if available
if [[ -f "${PLUGIN_DIR}/database/neon-utils.sh" ]]; then
  source "${PLUGIN_DIR}/database/neon-utils.sh" 2>/dev/null
fi

# Only check if Neon is configured
if [[ -z "${NEON_DATABASE_URL:-}" ]]; then
  exit 0
fi

echo ""
echo "══════════════════════════════════════════"
echo "  LinkedIn Studio — Session Summary"
echo "══════════════════════════════════════════"

# Check for orphaned drafts (status = draft, created today)
ORPHANED=$(neon_query "SELECT COUNT(*) FROM ls_content_queue WHERE status = 'draft' AND created_at >= CURRENT_DATE" 2>/dev/null || echo "0")
ORPHANED=$(echo "$ORPHANED" | tr -d '[:space:]')

if [[ "$ORPHANED" -gt 0 ]] 2>/dev/null; then
  echo "  WARNING: ${ORPHANED} draft(s) created today are unscheduled."
  echo "  Run /ls:pipeline with resume mode to continue."
fi

# Check for approved but unscheduled posts
APPROVED=$(neon_query "SELECT COUNT(*) FROM ls_content_queue WHERE status = 'approved' AND scheduled_at IS NULL" 2>/dev/null || echo "0")
APPROVED=$(echo "$APPROVED" | tr -d '[:space:]')

if [[ "$APPROVED" -gt 0 ]] 2>/dev/null; then
  echo "  NOTE: ${APPROVED} approved post(s) waiting to be scheduled."
  echo "  Run /ls:schedule-batch to submit them."
fi

# Check for failed posts
FAILED=$(neon_query "SELECT COUNT(*) FROM ls_content_queue WHERE status = 'failed'" 2>/dev/null || echo "0")
FAILED=$(echo "$FAILED" | tr -d '[:space:]')

if [[ "$FAILED" -gt 0 ]] 2>/dev/null; then
  echo "  ALERT: ${FAILED} post(s) in failed state."
  echo "  Review and fix, then re-run through pipeline."
fi

if [[ "${ORPHANED:-0}" -eq 0 && "${APPROVED:-0}" -eq 0 && "${FAILED:-0}" -eq 0 ]] 2>/dev/null; then
  echo "  All clear — no pending items."
fi

echo "══════════════════════════════════════════"
echo ""

# Always exit 0 — never block session exit
exit 0
