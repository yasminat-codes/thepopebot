#!/bin/bash
# Comprehensive endpoint test for Instantly.ai CLI

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="$SCRIPT_DIR/instantly"

# Check API key
if [[ -z "${INSTANTLY_API_KEY:-}" ]]; then
  echo "Error: INSTANTLY_API_KEY not set"
  echo "Set it with: export INSTANTLY_API_KEY='your_api_key'"
  exit 1
fi

echo "=========================================="
echo "INSTANTLY.AI CLI - ENDPOINT TESTS"
echo "=========================================="
echo ""

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
  local name="$1"
  shift
  echo -n "Testing $name... "
  
  if output=$("$@" 2>&1); then
    if echo "$output" | jq '.' > /dev/null 2>&1; then
      echo "✓ PASSED"
      ((PASSED++))
      return 0
    else
      echo "✗ FAILED (invalid JSON)"
      echo "  Output: $output" | head -3
      ((FAILED++))
      return 1
    fi
  else
    echo "✗ FAILED (command error)"
    echo "  Error: $output" | head -3
    ((FAILED++))
    return 1
  fi
}

echo "=== CAMPAIGNS ==="
test_endpoint "campaigns list" "$CLI" campaigns list --limit 5
test_endpoint "campaigns list with search" "$CLI" campaigns list --limit 5 --search "Test"

# Get a campaign ID for further tests
CAMPAIGN_ID=$("$CLI" campaigns list --limit 1 | jq -r '.items[0].id' 2>/dev/null || echo "")

if [[ -n "$CAMPAIGN_ID" && "$CAMPAIGN_ID" != "null" ]]; then
  test_endpoint "campaigns get" "$CLI" campaigns get --id "$CAMPAIGN_ID"
  echo ""
  
  echo "=== LEADS ==="
  test_endpoint "leads list" "$CLI" leads list --campaign-id "$CAMPAIGN_ID" --limit 5
  
  # Get a lead ID if available
  LEAD_ID=$("$CLI" leads list --campaign-id "$CAMPAIGN_ID" --limit 1 | jq -r '.items[0].id' 2>/dev/null || echo "")
  
  if [[ -n "$LEAD_ID" && "$LEAD_ID" != "null" ]]; then
    test_endpoint "leads get" "$CLI" leads get --id "$LEAD_ID"
  else
    echo "Skipping leads get (no leads found)"
    ((FAILED++))
  fi
  echo ""
  
  echo "=== ANALYTICS ==="
  test_endpoint "analytics campaign" "$CLI" analytics campaign --campaign-ids "$CAMPAIGN_ID"
  test_endpoint "analytics overview" "$CLI" analytics overview --campaign-ids "$CAMPAIGN_ID"
  test_endpoint "analytics daily" "$CLI" analytics daily --campaign-id "$CAMPAIGN_ID"
  test_endpoint "analytics account warmup" "$CLI" analytics account
  echo ""
else
  echo "Skipping campaign-dependent tests (no campaigns found)"
  FAILED=$((FAILED + 5))
fi

echo "=== RAW API ACCESS ==="
test_endpoint "raw API: GET campaigns" "$CLI" api GET "campaigns?limit=3"
test_endpoint "raw API: GET accounts warmup analytics" "$CLI" api GET "accounts/warmup-analytics"
echo ""

echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo "Total:  $((PASSED + FAILED))"
echo ""

if [[ $FAILED -eq 0 ]]; then
  echo "✓ All tests passed!"
  exit 0
else
  echo "✗ Some tests failed"
  exit 1
fi
