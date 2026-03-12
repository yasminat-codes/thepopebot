#!/usr/bin/env bash
set -euo pipefail

# Test a deployed Retell AI agent by triggering a phone call
# and retrieving the transcript afterward.
# Usage: test-agent.sh --agent-id AGENT_ID [--from NUMBER] [--to NUMBER]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$BASE_DIR/output"
API_KEY="${RETELL_API_KEY:-}"

AGENT_ID=""
FROM_NUMBER=""
TO_NUMBER=""
POLL_INTERVAL=5
MAX_POLL=60

# --- Parse Arguments ---
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent-id)
            AGENT_ID="$2"
            shift 2
            ;;
        --from)
            FROM_NUMBER="$2"
            shift 2
            ;;
        --to)
            TO_NUMBER="$2"
            shift 2
            ;;
        --api-key)
            API_KEY="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: test-agent.sh --agent-id AGENT_ID [--from NUMBER] [--to NUMBER] [--api-key KEY]"
            echo ""
            echo "Options:"
            echo "  --agent-id ID    Agent ID to test (required)"
            echo "  --from NUMBER    From phone number (E.164 format, e.g., +14155551234)"
            echo "  --to NUMBER      To phone number (E.164 format)"
            echo "  --api-key KEY    API key override (for client deployments)"
            echo ""
            echo "If --from and --to are not provided, creates a web call instead."
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
    echo "ERROR: No API key available. Set RETELL_API_KEY or use --api-key."
    exit 1
fi

if [ -z "$AGENT_ID" ]; then
    echo "ERROR: --agent-id is required."
    echo "Usage: test-agent.sh --agent-id AGENT_ID"
    exit 1
fi

echo "=== Retell AI Agent Test Call ==="
echo "Agent ID: $AGENT_ID"
echo ""

# --- Verify agent exists ---
echo "Verifying agent exists..."
AGENT_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET \
    "https://api.retellai.com/get-agent/$AGENT_ID" \
    -H "Authorization: Bearer $API_KEY" 2>/dev/null)

AGENT_HTTP=$(echo "$AGENT_RESPONSE" | tail -1)
AGENT_BODY=$(echo "$AGENT_RESPONSE" | sed '$d')

if [ "$AGENT_HTTP" != "200" ]; then
    echo "ERROR: Agent $AGENT_ID not found (HTTP $AGENT_HTTP)."
    echo "Response: $AGENT_BODY"
    exit 1
fi

AGENT_NAME=$(echo "$AGENT_BODY" | jq -r '.agent_name // "Unnamed"')
echo "  Found agent: $AGENT_NAME ($AGENT_ID)"
echo ""

# --- Trigger call ---
if [ -n "$FROM_NUMBER" ] && [ -n "$TO_NUMBER" ]; then
    echo "Triggering phone call..."
    echo "  From: $FROM_NUMBER"
    echo "  To:   $TO_NUMBER"

    CALL_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
        "https://api.retellai.com/v2/create-phone-call" \
        -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"from_number\": \"$FROM_NUMBER\",
            \"to_number\": \"$TO_NUMBER\",
            \"agent_id\": \"$AGENT_ID\"
        }" 2>/dev/null)

    CALL_HTTP=$(echo "$CALL_RESPONSE" | tail -1)
    CALL_BODY=$(echo "$CALL_RESPONSE" | sed '$d')

    if [ "$CALL_HTTP" != "200" ] && [ "$CALL_HTTP" != "201" ]; then
        echo "ERROR: Failed to create phone call (HTTP $CALL_HTTP)."
        echo "Response: $CALL_BODY"
        exit 1
    fi

    CALL_ID=$(echo "$CALL_BODY" | jq -r '.call_id')
    echo "  Call initiated: $CALL_ID"
    echo ""

    # --- Poll for call completion ---
    echo "Waiting for call to complete (polling every ${POLL_INTERVAL}s, max ${MAX_POLL}s)..."
    ELAPSED=0

    while [ $ELAPSED -lt $MAX_POLL ]; do
        sleep $POLL_INTERVAL
        ELAPSED=$((ELAPSED + POLL_INTERVAL))

        STATUS_RESPONSE=$(curl -s -X GET \
            "https://api.retellai.com/v2/get-call/$CALL_ID" \
            -H "Authorization: Bearer $API_KEY" 2>/dev/null)

        CALL_STATUS=$(echo "$STATUS_RESPONSE" | jq -r '.call_status // "unknown"')
        echo "  [$ELAPSED s] Status: $CALL_STATUS"

        if [ "$CALL_STATUS" = "ended" ] || [ "$CALL_STATUS" = "error" ]; then
            break
        fi
    done

    if [ "$CALL_STATUS" != "ended" ]; then
        echo ""
        echo "WARNING: Call did not complete within ${MAX_POLL}s."
        echo "Call ID: $CALL_ID"
        echo "Check status manually: curl -H 'Authorization: Bearer \$RETELL_API_KEY' https://api.retellai.com/v2/get-call/$CALL_ID"
        exit 1
    fi

    # --- Retrieve transcript ---
    echo ""
    echo "Retrieving call details..."

    CALL_DETAILS=$(curl -s -X GET \
        "https://api.retellai.com/v2/get-call/$CALL_ID" \
        -H "Authorization: Bearer $API_KEY" 2>/dev/null)

    TRANSCRIPT=$(echo "$CALL_DETAILS" | jq -r '.transcript // "No transcript available"')
    DURATION_MS=$(echo "$CALL_DETAILS" | jq -r '.end_timestamp - .start_timestamp // 0')
    DURATION_S=$((DURATION_MS / 1000))
    CALL_SUMMARY=$(echo "$CALL_DETAILS" | jq -r '.call_analysis.call_summary // "No summary"')
    CALL_ERRORS=$(echo "$CALL_DETAILS" | jq -r '.call_analysis.call_successful // true')

    # Save transcript
    mkdir -p "$OUTPUT_DIR"
    echo "$TRANSCRIPT" > "$OUTPUT_DIR/test-call-transcript.txt"

    echo ""
    echo "=== Test Call Results ==="
    echo "  Call ID:       $CALL_ID"
    echo "  Duration:      ${DURATION_S}s"
    echo "  Successful:    $CALL_ERRORS"
    echo "  Summary:       $CALL_SUMMARY"
    echo "  Transcript:    saved to $OUTPUT_DIR/test-call-transcript.txt"
    echo ""
    echo "Full transcript:"
    echo "---"
    echo "$TRANSCRIPT"
    echo "---"
else
    echo "No phone numbers provided. To test via phone call, use:"
    echo "  $0 --agent-id $AGENT_ID --from +14155551234 --to +14155555678"
    echo ""
    echo "Alternatively, test via the Retell Dashboard:"
    echo "  https://dashboard.retellai.com/"
    echo ""
    echo "Or use the web call widget for agent: $AGENT_ID"
fi
