#!/bin/bash
# Test all the fixes

set -euo pipefail

export INSTANTLY_API_KEY="YmVlMjU1MDktNDliNi00MTQ4LTllYWMtNmFhMjUxMmE1MmFhOkl4RHhOYmNnUlFaag=="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="$SCRIPT_DIR/instantly"

PASS=0
FAIL=0

# Get test campaign
CAMPAIGN_ID=$($CLI campaigns list --limit 1 | jq -r '.items[0].id')
echo "Using Campaign ID: $CAMPAIGN_ID"
echo ""

# Test 1: Inbox list (without --unread since it's removed)
echo "Test 1: Inbox list (basic)"
if $CLI inbox list --limit 2 &>/dev/null; then
  echo "✅ PASS"
  PASS=$((PASS + 1))
else
  echo "❌ FAIL"
  FAIL=$((FAIL + 1))
fi
sleep 0.5

# Test 2: Subsequence create with --delay-days
echo ""
echo "Test 2: Create subsequence with --delay-days"
if $CLI subsequences create --campaign-id "$CAMPAIGN_ID" --name "Fix Test Subseq" --delay-days 3 &>/dev/null; then
  echo "✅ PASS"
  PASS=$((PASS + 1))
  # Get and delete the created subsequence
  SUBSEQ_ID=$($CLI subsequences list --campaign-id "$CAMPAIGN_ID" | jq -r '.items[] | select(.name == "Fix Test Subseq") | .id' | head -1)
  if [ -n "$SUBSEQ_ID" ]; then
    $CLI subsequences delete --id "$SUBSEQ_ID" &>/dev/null
    echo "   (cleaned up test subsequence)"
  fi
else
  echo "❌ FAIL"
  FAIL=$((FAIL + 1))
fi
sleep 0.5

# Test 3: Webhook event-types
echo ""
echo "Test 3: Webhook event-types"
if $CLI webhooks event-types &>/dev/null; then
  echo "✅ PASS"
  PASS=$((PASS + 1))
else
  echo "❌ FAIL"
  FAIL=$((FAIL + 1))
fi
sleep 0.5

# Test 4: Create webhook with correct parameters
echo ""
echo "Test 4: Create webhook with target_hook_url"
TEST_URL="https://webhook.site/test-fix-$(date +%s)"
if $CLI webhooks create --url "$TEST_URL" --events "reply_received" &>/dev/null; then
  echo "✅ PASS"
  PASS=$((PASS + 1))
  # Get and delete the created webhook
  WEBHOOK_ID=$($CLI webhooks list | jq -r ".items[] | select(.target_hook_url == \"$TEST_URL\") | .id" | head -1)
  if [ -n "$WEBHOOK_ID" ]; then
    $CLI webhooks delete --id "$WEBHOOK_ID" &>/dev/null
    echo "   (cleaned up test webhook)"
  fi
else
  echo "❌ FAIL"
  FAIL=$((FAIL + 1))
fi
sleep 0.5

# Test 5: Bulk delete with proper parameters
echo ""
echo "Test 5: Bulk delete leads (with campaign_id)"
# We won't actually delete anything, just test the parameter validation
OUTPUT=$($CLI leads bulk-delete --emails "" --campaign-id "$CAMPAIGN_ID" 2>&1 || true)
if echo "$OUTPUT" | grep -q "Error: --emails required"; then
  echo "✅ PASS (proper validation)"
  PASS=$((PASS + 1))
else
  echo "❌ FAIL"
  FAIL=$((FAIL + 1))
fi

echo ""
echo "===================="
echo "FIXES TEST SUMMARY"
echo "===================="
echo "Passed: $PASS/5"
echo "Failed: $FAIL/5"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "✅ ALL FIXES WORKING!"
  exit 0
else
  echo "⚠️  Some fixes still need work"
  exit 1
fi
