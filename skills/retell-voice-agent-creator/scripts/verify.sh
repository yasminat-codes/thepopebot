#!/usr/bin/env bash
set -euo pipefail

# Pre-flight verification for Retell AI Voice Agent Creator
# Checks: required tools, environment variables, API connectivity

PASS=0
WARN=0
FAIL=0

pass() { echo "  [PASS] $1"; PASS=$((PASS + 1)); }
warn() { echo "  [WARN] $1"; WARN=$((WARN + 1)); }
fail() { echo "  [FAIL] $1"; FAIL=$((FAIL + 1)); }

echo "=== Retell AI Voice Agent Creator — Pre-Flight Check ==="
echo ""

# --- Required Tools ---
echo "Checking required tools..."

if command -v curl &>/dev/null; then
    pass "curl is installed ($(curl --version | head -1 | cut -d' ' -f1-2))"
else
    fail "curl is not installed. Install with: sudo apt install curl"
fi

if command -v jq &>/dev/null; then
    pass "jq is installed ($(jq --version))"
else
    fail "jq is not installed. Install with: sudo apt install jq"
fi

if command -v python3 &>/dev/null; then
    pass "python3 is installed ($(python3 --version))"
else
    fail "python3 is not installed. Install with: sudo apt install python3"
fi

echo ""

# --- Required Environment Variables ---
echo "Checking environment variables..."

if [ -n "${RETELL_API_KEY:-}" ]; then
    if [[ "$RETELL_API_KEY" == key_* ]]; then
        pass "RETELL_API_KEY is set and has correct format (key_...)"
    else
        warn "RETELL_API_KEY is set but does not start with 'key_'. Verify it is correct."
    fi
else
    fail "RETELL_API_KEY is not set. Export it or add to /home/clawdbot/shared/.env"
fi

# --- Optional Environment Variables ---
if [ -n "${ELEVENLABS_API_KEY:-}" ]; then
    pass "ELEVENLABS_API_KEY is set (optional — enables ElevenLabs voices)"
else
    warn "ELEVENLABS_API_KEY is not set (optional — needed for ElevenLabs voice cloning)"
fi

if [ -n "${TWILIO_ACCOUNT_SID:-}" ] && [ -n "${TWILIO_AUTH_TOKEN:-}" ]; then
    pass "Twilio credentials are set (optional — enables phone number assignment)"
else
    warn "Twilio credentials not set (optional — needed for phone number assignment)"
fi

echo ""

# --- API Connectivity ---
echo "Checking Retell API connectivity..."

if [ -n "${RETELL_API_KEY:-}" ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $RETELL_API_KEY" \
        "https://api.retellai.com/list-agents" 2>/dev/null || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        pass "Retell API is reachable and key is valid (HTTP 200)"
    elif [ "$HTTP_CODE" = "401" ]; then
        fail "Retell API returned 401 Unauthorized. Check your API key."
    elif [ "$HTTP_CODE" = "000" ]; then
        fail "Could not reach Retell API. Check network connectivity."
    else
        warn "Retell API returned HTTP $HTTP_CODE. May indicate an issue."
    fi
else
    warn "Skipping API connectivity check (RETELL_API_KEY not set)"
fi

echo ""

# --- Summary ---
echo "=== Summary ==="
echo "  Passed: $PASS"
echo "  Warnings: $WARN"
echo "  Failed: $FAIL"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "RESULT: Pre-flight check FAILED. Fix the above issues before deploying."
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo "RESULT: Pre-flight check PASSED with warnings. Core features will work."
    exit 0
else
    echo "RESULT: Pre-flight check PASSED. All systems ready."
    exit 0
fi
