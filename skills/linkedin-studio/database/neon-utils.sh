#!/usr/bin/env bash
# =============================================================================
# neon-utils.sh — Bash utility for running SQL against Neon PostgreSQL
# LinkedIn Studio Plugin
#
# Usage:
#   source /path/to/neon-utils.sh
#   neon_test
#   neon_query "SELECT * FROM ls_topic_bank LIMIT 5"
#   neon_exec "INSERT INTO ls_topic_bank (title) VALUES ('test')"
#   neon_migrate /path/to/migration.sql
#
# Requires: psql (PostgreSQL client), NEON_DATABASE_URL env var
# =============================================================================

set -euo pipefail

NEON_UTILS_VERSION="1.0.0"
NEON_STATEMENT_TIMEOUT="${NEON_STATEMENT_TIMEOUT:-30000}"
NEON_CONNECT_TIMEOUT="${NEON_CONNECT_TIMEOUT:-10}"

_neon_log() {
  echo "[neon-utils] $*" >&2
}

_neon_error() {
  echo "[neon-utils][ERROR] $*" >&2
}

_neon_check_prereqs() {
  if ! command -v psql &>/dev/null; then
    _neon_error "psql not found. Install PostgreSQL client: brew install libpq"
    return 1
  fi
  if [[ -z "${NEON_DATABASE_URL:-}" ]]; then
    _neon_error "NEON_DATABASE_URL is not set. Set it in your environment or Claude Code settings."
    return 1
  fi
}

# Test connection to Neon
# Returns: 0 on success, 1 on failure
neon_test() {
  _neon_check_prereqs || return 1

  if psql "${NEON_DATABASE_URL}" \
    -c "SELECT 1 AS connection_test;" \
    --no-psqlrc \
    --quiet \
    --tuples-only \
    -v "ON_ERROR_STOP=1" \
    -v "statement_timeout=${NEON_STATEMENT_TIMEOUT}" \
    --connect-timeout="${NEON_CONNECT_TIMEOUT}" \
    &>/dev/null; then
    _neon_log "Connection OK"
    return 0
  else
    _neon_error "Connection failed. Check NEON_DATABASE_URL."
    return 1
  fi
}

# Run a SELECT query and return results
# Usage: neon_query "SELECT ..." [format]
#   format: csv (default), json, table
neon_query() {
  local sql="${1:?Usage: neon_query \"SELECT ...\" [csv|json|table]}"
  local format="${2:-csv}"

  _neon_check_prereqs || return 1

  local psql_flags=(
    --no-psqlrc
    --quiet
    --tuples-only
    -v "ON_ERROR_STOP=1"
    -v "statement_timeout=${NEON_STATEMENT_TIMEOUT}"
    --connect-timeout="${NEON_CONNECT_TIMEOUT}"
  )

  case "$format" in
    csv)
      psql_flags+=(--csv)
      ;;
    json)
      # Wrap query to return JSON
      sql="SELECT json_agg(t) FROM (${sql}) t;"
      psql_flags+=(--tuples-only)
      ;;
    table)
      # Remove --tuples-only for formatted table output
      psql_flags=(
        --no-psqlrc
        -v "ON_ERROR_STOP=1"
        -v "statement_timeout=${NEON_STATEMENT_TIMEOUT}"
        --connect-timeout="${NEON_CONNECT_TIMEOUT}"
      )
      ;;
    *)
      _neon_error "Unknown format: $format. Use csv, json, or table."
      return 1
      ;;
  esac

  psql "${NEON_DATABASE_URL}" "${psql_flags[@]}" -c "${sql}" 2>&1
  local exit_code=$?

  if [[ $exit_code -ne 0 ]]; then
    _neon_error "Query failed (exit $exit_code)"
    return $exit_code
  fi
}

# Run an INSERT/UPDATE/DELETE and return affected row count
# Usage: neon_exec "INSERT INTO ..."
neon_exec() {
  local sql="${1:?Usage: neon_exec \"INSERT/UPDATE/DELETE ...\"}"

  _neon_check_prereqs || return 1

  local output
  output=$(psql "${NEON_DATABASE_URL}" \
    --no-psqlrc \
    --quiet \
    -v "ON_ERROR_STOP=1" \
    -v "statement_timeout=${NEON_STATEMENT_TIMEOUT}" \
    --connect-timeout="${NEON_CONNECT_TIMEOUT}" \
    -c "${sql}" 2>&1)
  local exit_code=$?

  if [[ $exit_code -ne 0 ]]; then
    _neon_error "Exec failed: ${output}"
    return $exit_code
  fi

  # Extract row count from output like "INSERT 0 1" or "UPDATE 3"
  local count
  count=$(echo "$output" | grep -oE '[0-9]+$' | tail -1)
  echo "${count:-0}"
}

# Run a migration SQL file
# Usage: neon_migrate /path/to/migration.sql
neon_migrate() {
  local file="${1:?Usage: neon_migrate /path/to/migration.sql}"

  _neon_check_prereqs || return 1

  if [[ ! -f "$file" ]]; then
    _neon_error "Migration file not found: $file"
    return 1
  fi

  _neon_log "Running migration: $(basename "$file")"

  psql "${NEON_DATABASE_URL}" \
    --no-psqlrc \
    -v "ON_ERROR_STOP=1" \
    -v "statement_timeout=120000" \
    --connect-timeout="${NEON_CONNECT_TIMEOUT}" \
    -f "$file" 2>&1
  local exit_code=$?

  if [[ $exit_code -eq 0 ]]; then
    _neon_log "Migration complete: $(basename "$file")"
  else
    _neon_error "Migration failed: $(basename "$file")"
    return $exit_code
  fi
}

# Show help
neon_help() {
  cat <<'HELP'
neon-utils.sh — Bash utility for Neon PostgreSQL

Functions:
  neon_test                          Test database connection
  neon_query "SQL" [csv|json|table]  Run SELECT, return results
  neon_exec "SQL"                    Run INSERT/UPDATE/DELETE, return row count
  neon_migrate /path/to/file.sql     Run a migration file
  neon_help                          Show this help

Environment:
  NEON_DATABASE_URL        (required) PostgreSQL connection string
  NEON_STATEMENT_TIMEOUT   Query timeout in ms (default: 30000)
  NEON_CONNECT_TIMEOUT     Connection timeout in seconds (default: 10)

Examples:
  source ./database/neon-utils.sh
  neon_test
  neon_query "SELECT id, title FROM ls_topic_bank WHERE status = 'new' LIMIT 10"
  neon_query "SELECT * FROM ls_brand_voice_profile" json
  neon_exec "UPDATE ls_topic_bank SET status = 'archived' WHERE trend_score < 20"
  neon_migrate ./database/migrations/001_initial.sql
HELP
}

# If run directly (not sourced), parse arguments
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-}" in
    --help|-h)
      neon_help
      ;;
    --version|-v)
      echo "neon-utils.sh v${NEON_UTILS_VERSION}"
      ;;
    test)
      neon_test
      ;;
    query)
      shift
      neon_query "$@"
      ;;
    exec)
      shift
      neon_exec "$@"
      ;;
    migrate)
      shift
      neon_migrate "$@"
      ;;
    *)
      neon_help
      ;;
  esac
fi
