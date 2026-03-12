#!/usr/bin/env bash
set -euo pipefail

# =============================================================================
# deploy-agent.sh — Full Retell AI agent deployment
#
# Usage:
#   ./deploy-agent.sh --llm-config llm-config.json --agent-config agent-config.json
#   ./deploy-agent.sh --api-key "$CLIENT_KEY" --llm-config llm.json --agent-config agent.json
#
# Steps:
#   1. Validate config files
#   2. Create LLM (capture llm_id)
#   3. Create Agent with llm_id (capture agent_id)
#   4. Verify agent exists
#   5. Output deployment receipt
# =============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RETELL_BASE_URL="https://api.retellai.com"

# Defaults
API_KEY="${RETELL_API_KEY:-}"
LLM_CONFIG=""
AGENT_CONFIG=""
MAX_RETRIES=3

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --api-key)     API_KEY="$2";      shift 2 ;;
    --llm-config)  LLM_CONFIG="$2";   shift 2 ;;
    --agent-config) AGENT_CONFIG="$2"; shift 2 ;;
    *) echo "Unknown flag: $1" >&2; exit 1 ;;
  esac
done

# ---------------------------------------------------------------------------
# Validate inputs
# ---------------------------------------------------------------------------
if [[ -z "$API_KEY" ]]; then
  echo "ERROR: No API key. Set RETELL_API_KEY or pass --api-key." >&2
  exit 1
fi

if [[ -z "$LLM_CONFIG" || ! -f "$LLM_CONFIG" ]]; then
  echo "ERROR: --llm-config file required and must exist." >&2
  exit 1
fi

if [[ -z "$AGENT_CONFIG" || ! -f "$AGENT_CONFIG" ]]; then
  echo "ERROR: --agent-config file required and must exist." >&2
  exit 1
fi

# Validate JSON syntax
if ! jq empty "$LLM_CONFIG" 2>/dev/null; then
  echo "ERROR: $LLM_CONFIG is not valid JSON." >&2
  exit 1
fi
if ! jq empty "$AGENT_CONFIG" 2>/dev/null; then
  echo "ERROR: $AGENT_CONFIG is not valid JSON." >&2
  exit 1
fi

# Validate required LLM field
if ! jq -e '.start_speaker' "$LLM_CONFIG" > /dev/null 2>&1; then
  echo "ERROR: start_speaker is required in $LLM_CONFIG." >&2
  exit 1
fi

# Validate required agent field
if ! jq -e '.voice_id' "$AGENT_CONFIG" > /dev/null 2>&1; then
  echo "ERROR: voice_id is required in $AGENT_CONFIG." >&2
  exit 1
fi

echo "=== Retell Agent Deployment ==="
echo "LLM config:   $LLM_CONFIG"
echo "Agent config:  $AGENT_CONFIG"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Create LLM
# ---------------------------------------------------------------------------
echo "Step 1: Creating LLM..."
LLM_BODY=$(cat "$LLM_CONFIG")
LLM_RESPONSE=""
LLM_ID=""

for attempt in $(seq 1 $MAX_RETRIES); do
  LLM_RESULT=$(curl -s -w "\n%{http_code}" -X POST "$RETELL_BASE_URL/create-retell-llm" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$LLM_BODY" 2>/dev/null) || true

  HTTP_CODE=$(echo "$LLM_RESULT" | tail -1)
  LLM_RESPONSE=$(echo "$LLM_RESULT" | head -n -1)

  if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    LLM_ID=$(echo "$LLM_RESPONSE" | jq -r '.llm_id')
    echo "  LLM created: $LLM_ID"
    break
  elif [[ "$HTTP_CODE" -ge 400 && "$HTTP_CODE" -lt 500 ]]; then
    echo "ERROR: HTTP $HTTP_CODE creating LLM — $LLM_RESPONSE" >&2
    exit 1
  else
    echo "  Attempt $attempt/$MAX_RETRIES failed (HTTP $HTTP_CODE). Retrying..." >&2
    sleep $((2 ** attempt))
  fi
done

if [[ -z "$LLM_ID" ]]; then
  echo "ERROR: Failed to create LLM after $MAX_RETRIES attempts." >&2
  echo "Saving config for manual retry: failed-llm-config.json"
  cp "$LLM_CONFIG" "failed-llm-config.json"
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 2: Create Agent
# ---------------------------------------------------------------------------
echo "Step 2: Creating Agent..."
AGENT_BODY=$(cat "$AGENT_CONFIG" | jq --arg llm_id "$LLM_ID" \
  '.response_engine = {"type": "retell-llm", "llm_id": $llm_id}')
AGENT_RESPONSE=""
AGENT_ID=""

for attempt in $(seq 1 $MAX_RETRIES); do
  AGENT_RESULT=$(curl -s -w "\n%{http_code}" -X POST "$RETELL_BASE_URL/create-agent" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$AGENT_BODY" 2>/dev/null) || true

  HTTP_CODE=$(echo "$AGENT_RESULT" | tail -1)
  AGENT_RESPONSE=$(echo "$AGENT_RESULT" | head -n -1)

  if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r '.agent_id')
    echo "  Agent created: $AGENT_ID"
    break
  elif [[ "$HTTP_CODE" -ge 400 && "$HTTP_CODE" -lt 500 ]]; then
    echo "ERROR: HTTP $HTTP_CODE creating agent — $AGENT_RESPONSE" >&2
    exit 1
  else
    echo "  Attempt $attempt/$MAX_RETRIES failed (HTTP $HTTP_CODE). Retrying..." >&2
    sleep $((2 ** attempt))
  fi
done

if [[ -z "$AGENT_ID" ]]; then
  echo "ERROR: Failed to create agent after $MAX_RETRIES attempts." >&2
  echo "LLM was created ($LLM_ID) but agent failed."
  echo "Saving config for manual retry: failed-agent-config.json"
  echo "$AGENT_BODY" > "failed-agent-config.json"
  exit 1
fi

# ---------------------------------------------------------------------------
# Step 3: Verify Agent
# ---------------------------------------------------------------------------
echo "Step 3: Verifying agent..."
VERIFY=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $API_KEY" \
  "$RETELL_BASE_URL/get-agent/$AGENT_ID" 2>/dev/null) || true

if [[ "$VERIFY" == "200" ]]; then
  echo "  Agent verified successfully."
else
  echo "WARNING: Agent verification returned HTTP $VERIFY. Agent may need manual check." >&2
fi

# ---------------------------------------------------------------------------
# Step 4: Output Results
# ---------------------------------------------------------------------------
RECEIPT_FILE="deployment-receipt-$(date +%Y%m%d-%H%M%S).json"
jq -n \
  --arg agent_id "$AGENT_ID" \
  --arg llm_id "$LLM_ID" \
  --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg llm_config "$LLM_CONFIG" \
  --arg agent_config "$AGENT_CONFIG" \
  '{
    agent_id: $agent_id,
    llm_id: $llm_id,
    deployed_at: $timestamp,
    llm_config_file: $llm_config,
    agent_config_file: $agent_config,
    dashboard_url: ("https://www.retellai.com/dashboard/agent/" + $agent_id)
  }' > "$RECEIPT_FILE"

echo ""
echo "=== Deployment Complete ==="
echo "Agent ID:   $AGENT_ID"
echo "LLM ID:     $LLM_ID"
echo "Dashboard:  https://www.retellai.com/dashboard/agent/$AGENT_ID"
echo "Receipt:    $RECEIPT_FILE"
