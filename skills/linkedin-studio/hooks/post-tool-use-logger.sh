#!/usr/bin/env bash
# =============================================================================
# post-tool-use-logger.sh — Claude Code PostToolUse Hook
# LinkedIn Studio Plugin
#
# Logs skill invocations to Neon ls_audit_log after content creation events.
# Non-blocking — failures are logged but don't halt execution.
# =============================================================================

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$HOOKS_DIR")"

# Source neon-utils if available
if [[ -f "${PLUGIN_DIR}/database/neon-utils.sh" ]]; then
  source "${PLUGIN_DIR}/database/neon-utils.sh" 2>/dev/null
fi

SKILL_NAME="${SKILL_NAME:-unknown}"
ACTION="${ACTION:-invocation}"
POST_ID="${POST_ID:-}"
QUALITY_SCORE="${QUALITY_SCORE:-}"
AI_SCORE="${AI_SCORE:-}"
STATUS="${STATUS:-completed}"
ERROR_MSG="${ERROR_MSG:-}"

# Only log if Neon is configured
if [[ -z "${NEON_DATABASE_URL:-}" ]]; then
  echo "[audit-logger] NEON_DATABASE_URL not set — skipping audit log" >&2
  exit 0
fi

# Check if ls_audit_log table exists (it was in 001 migration description but not DDL)
# We'll create it if it doesn't exist
ENSURE_TABLE="CREATE TABLE IF NOT EXISTS ls_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  skill_name VARCHAR(100) NOT NULL,
  action VARCHAR(100) DEFAULT 'invocation',
  post_id UUID,
  quality_score INTEGER,
  ai_score INTEGER,
  status VARCHAR(30) DEFAULT 'completed',
  error_message TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);"

neon_exec "$ENSURE_TABLE" 2>/dev/null || true

# Log the event
SQL="INSERT INTO ls_audit_log (skill_name, action, post_id, quality_score, ai_score, status, error_message)
VALUES (
  '${SKILL_NAME//\'/\'\'}',
  '${ACTION//\'/\'\'}',
  $(if [[ -n "$POST_ID" ]]; then echo "'${POST_ID}'"; else echo "NULL"; fi),
  $(if [[ -n "$QUALITY_SCORE" ]]; then echo "$QUALITY_SCORE"; else echo "NULL"; fi),
  $(if [[ -n "$AI_SCORE" ]]; then echo "$AI_SCORE"; else echo "NULL"; fi),
  '${STATUS//\'/\'\'}',
  $(if [[ -n "$ERROR_MSG" ]]; then echo "'${ERROR_MSG//\'/\'\'}'"; else echo "NULL"; fi)
);"

if neon_exec "$SQL" 2>/dev/null; then
  echo "[audit-logger] Logged: ${SKILL_NAME} / ${ACTION}" >&2
else
  echo "[audit-logger] Failed to log — continuing anyway" >&2
fi

# Always exit 0 (non-blocking hook)
exit 0
