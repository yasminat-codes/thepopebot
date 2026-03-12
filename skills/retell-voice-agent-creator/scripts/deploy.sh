#!/usr/bin/env bash
set -euo pipefail

# Full deployment script for Retell AI Voice Agent Creator
# Creates Retell LLM from llm-config.json, then creates agent from agent-config.json
# Supports --api-key flag for client deployments
# Retries 3x on failure, saves config locally on final failure

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$BASE_DIR/output"
MAX_RETRIES=3
RETRY_DELAY=2

# --- Parse Arguments ---
API_KEY="${RETELL_API_KEY:-}"

while [[ $# -gt 0 ]]; do
    case $1 in
        --api-key)
            API_KEY="$2"
            echo "Using provided API key (client deployment mode)"
            shift 2
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: deploy.sh [--api-key KEY] [--output-dir DIR]"
            echo ""
            echo "Options:"
            echo "  --api-key KEY      Use a specific API key (for client deployments)"
            echo "  --output-dir DIR   Path to output directory (default: ../output)"
            echo ""
            echo "Reads llm-config.json and agent-config.json from the output directory."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# --- Validate ---
if [ -z "$API_KEY" ]; then
    echo "ERROR: No API key available."
    echo "Set RETELL_API_KEY environment variable or use --api-key flag."
    exit 1
fi

if [ ! -f "$OUTPUT_DIR/llm-config.json" ]; then
    echo "ERROR: $OUTPUT_DIR/llm-config.json not found."
    echo "Run the agent-config-builder sub-skill first to generate config files."
    exit 1
fi

if [ ! -f "$OUTPUT_DIR/agent-config.json" ]; then
    echo "ERROR: $OUTPUT_DIR/agent-config.json not found."
    echo "Run the agent-config-builder sub-skill first to generate config files."
    exit 1
fi

# Validate JSON
if ! jq empty "$OUTPUT_DIR/llm-config.json" 2>/dev/null; then
    echo "ERROR: llm-config.json is not valid JSON."
    exit 1
fi

if ! jq empty "$OUTPUT_DIR/agent-config.json" 2>/dev/null; then
    echo "ERROR: agent-config.json is not valid JSON."
    exit 1
fi

echo "=== Retell AI Voice Agent Deployment ==="
echo "Output directory: $OUTPUT_DIR"
echo ""

# --- Helper: API call with retry ---
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    local attempt=1
    local response=""
    local http_code=""

    while [ $attempt -le $MAX_RETRIES ]; do
        if [ -n "$data" ]; then
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                "https://api.retellai.com$endpoint" \
                -H "Authorization: Bearer $API_KEY" \
                -H "Content-Type: application/json" \
                -d "$data" 2>/dev/null || echo -e "\n000")
        else
            response=$(curl -s -w "\n%{http_code}" -X "$method" \
                "https://api.retellai.com$endpoint" \
                -H "Authorization: Bearer $API_KEY" \
                -H "Content-Type: application/json" 2>/dev/null || echo -e "\n000")
        fi

        http_code=$(echo "$response" | tail -1)
        local body
        body=$(echo "$response" | sed '$d')

        if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
            echo "$body"
            return 0
        fi

        echo "  Attempt $attempt/$MAX_RETRIES failed (HTTP $http_code)" >&2
        if [ $attempt -lt $MAX_RETRIES ]; then
            echo "  Retrying in ${RETRY_DELAY}s..." >&2
            sleep $RETRY_DELAY
        fi
        attempt=$((attempt + 1))
    done

    echo "  API call failed after $MAX_RETRIES attempts." >&2
    echo "  Last response: $body" >&2
    return 1
}

# --- Step 1: Create Retell LLM ---
echo "Step 1: Creating Retell LLM..."
LLM_DATA=$(cat "$OUTPUT_DIR/llm-config.json")

LLM_RESPONSE=$(api_call POST "/create-retell-llm" "$LLM_DATA") || {
    echo ""
    echo "FAILED: Could not create Retell LLM after $MAX_RETRIES attempts."
    echo "Config files saved in $OUTPUT_DIR/ for manual retry."
    echo "Manual command:"
    echo "  curl -X POST https://api.retellai.com/create-retell-llm \\"
    echo "    -H 'Authorization: Bearer \$RETELL_API_KEY' \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d @$OUTPUT_DIR/llm-config.json"
    exit 1
}

LLM_ID=$(echo "$LLM_RESPONSE" | jq -r '.llm_id')
echo "  LLM created: $LLM_ID"
echo ""

# --- Step 2: Inject LLM ID into agent config ---
echo "Step 2: Preparing agent config with LLM ID..."
AGENT_DATA=$(cat "$OUTPUT_DIR/agent-config.json" | jq --arg llm_id "$LLM_ID" \
    '.response_engine.llm_id = $llm_id')
echo "  Agent config prepared with llm_id: $LLM_ID"
echo ""

# --- Step 3: Create Agent ---
echo "Step 3: Creating Retell Agent..."
AGENT_RESPONSE=$(api_call POST "/create-agent" "$AGENT_DATA") || {
    echo ""
    echo "FAILED: Could not create agent after $MAX_RETRIES attempts."
    echo "LLM was created successfully: $LLM_ID"
    echo "Config files saved in $OUTPUT_DIR/ for manual retry."
    exit 1
}

AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r '.agent_id')
AGENT_NAME=$(echo "$AGENT_RESPONSE" | jq -r '.agent_name // "Unnamed"')
echo "  Agent created: $AGENT_ID ($AGENT_NAME)"
echo ""

# --- Step 4: Verify Agent ---
echo "Step 4: Verifying agent exists..."
VERIFY_RESPONSE=$(api_call GET "/get-agent/$AGENT_ID") || {
    echo "  WARNING: Could not verify agent, but creation succeeded."
    echo "  Agent ID: $AGENT_ID"
}

if [ -n "${VERIFY_RESPONSE:-}" ]; then
    VERIFIED_ID=$(echo "$VERIFY_RESPONSE" | jq -r '.agent_id')
    if [ "$VERIFIED_ID" = "$AGENT_ID" ]; then
        echo "  Agent verified successfully."
    else
        echo "  WARNING: Verification returned unexpected agent ID."
    fi
fi
echo ""

# --- Step 5: Save Deployment Receipt ---
echo "Step 5: Saving deployment receipt..."
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

cat > "$OUTPUT_DIR/deployment-receipt.json" << EOF
{
  "agent_id": "$AGENT_ID",
  "agent_name": "$AGENT_NAME",
  "llm_id": "$LLM_ID",
  "deployed_at": "$TIMESTAMP",
  "deployment_mode": "$([ "$API_KEY" = "${RETELL_API_KEY:-}" ] && echo 'internal' || echo 'client')",
  "status": "success"
}
EOF

echo "  Receipt saved to $OUTPUT_DIR/deployment-receipt.json"
echo ""

# --- Summary ---
echo "=== Deployment Complete ==="
echo "  Agent ID:   $AGENT_ID"
echo "  Agent Name: $AGENT_NAME"
echo "  LLM ID:     $LLM_ID"
echo "  Deployed:   $TIMESTAMP"
echo ""
echo "To test: ./scripts/test-agent.sh --agent-id $AGENT_ID"
echo "To view: https://dashboard.retellai.com/"
