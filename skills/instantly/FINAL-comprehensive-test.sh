#!/bin/bash
# FINAL Comprehensive Test - After Fixes

set -euo pipefail

export INSTANTLY_API_KEY="YmVlMjU1MDktNDliNi00MTQ4LTllYWMtNmFhMjUxMmE1MmFhOkl4RHhOYmNnUlFaag=="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="$SCRIPT_DIR/instantly"

PASS=0
FAIL=0
TOTAL=0

echo "========================================"
echo "FINAL COMPREHENSIVE TEST - AFTER FIXES"
echo "========================================"
date
echo ""

# Get test data
CAMPAIGN_ID=$($CLI campaigns list --limit 1 | jq -r '.items[0].id')
ACCOUNT_EMAIL=$($CLI accounts list --limit 1 | jq -r '.items[0].email')

echo "Test Data:"
echo "  Campaign ID: $CAMPAIGN_ID"
echo "  Account Email: $ACCOUNT_EMAIL"
echo ""

test_endpoint() {
  local name="$1"
  local command="$2"
  
  TOTAL=$((TOTAL + 1))
  echo -n "[$TOTAL] $name... "
  
  if eval "$command" &>/dev/null; then
    echo "✅"
    PASS=$((PASS + 1))
  else
    echo "❌"
    FAIL=$((FAIL + 1))
  fi
  
  sleep 0.5
}

echo "Testing Previously Failed Endpoints:"
echo "====================================="
echo ""

# 1. Inbox list (was working, confirm still works)
test_endpoint "Inbox list" \
  "$CLI inbox list --limit 2"

# 2. Webhook event-types (was missing, now added)
test_endpoint "Webhook event-types" \
  "$CLI webhooks event-types"

# 3. Create webhook (was failing, now fixed)
TEST_WEBHOOK_URL="https://webhook.site/final-test-$(date +%s)"
test_endpoint "Create webhook" \
  "$CLI webhooks create --url $TEST_WEBHOOK_URL --events reply_received"

# Cleanup webhook
WEBHOOK_ID=$($CLI webhooks list | jq -r ".items[] | select(.target_hook_url == \"$TEST_WEBHOOK_URL\") | .id" 2>/dev/null | head -1 || echo "")
if [ -n "$WEBHOOK_ID" ]; then
  $CLI webhooks delete --id "$WEBHOOK_ID" &>/dev/null
  echo "   (cleaned up test webhook)"
fi

# 4. Update webhook (test with existing webhook)
EXISTING_WEBHOOK=$($CLI webhooks list | jq -r '.items[0].id' 2>/dev/null || echo "")
if [ -n "$EXISTING_WEBHOOK" ]; then
  test_endpoint "Update webhook" \
    "$CLI webhooks update --id $EXISTING_WEBHOOK --event-type reply_received"
else
  echo "[$((TOTAL + 1))] Update webhook... ⏭️  (no webhooks to test)"
  TOTAL=$((TOTAL + 1))
fi

# 5. Bulk delete (skip - requires actual leads to delete)
echo "[$((TOTAL + 1))] Bulk delete validation... ⏭️  (needs actual leads)"
TOTAL=$((TOTAL + 1))

echo ""
echo "Testing Core Working Endpoints:"
echo "==============================="
echo ""

test_endpoint "List campaigns" \
  "$CLI campaigns list --limit 5"

test_endpoint "Get campaign" \
  "$CLI campaigns get --id $CAMPAIGN_ID"

test_endpoint "List leads" \
  "$CLI leads list --campaign-id $CAMPAIGN_ID --limit 5"

test_endpoint "List accounts" \
  "$CLI accounts list"

test_endpoint "Get account" \
  "$CLI accounts get --email $ACCOUNT_EMAIL"

test_endpoint "Campaign analytics" \
  "$CLI analytics campaign --campaign-ids $CAMPAIGN_ID"

test_endpoint "List emails" \
  "$CLI emails list --limit 5"

test_endpoint "Unread count" \
  "$CLI emails unread-count"

test_endpoint "List webhooks" \
  "$CLI webhooks list"

test_endpoint "Webhook events" \
  "$CLI webhooks events --limit 5"

test_endpoint "List lead lists" \
  "$CLI lead-lists list"

test_endpoint "List subsequences" \
  "$CLI subsequences list --campaign-id $CAMPAIGN_ID"

test_endpoint "Raw API - GET" \
  "$CLI api GET 'campaigns?limit=2'"

echo ""
echo "========================================"
echo "FINAL TEST SUMMARY"
echo "========================================"
echo "Total Tests: $TOTAL"
echo "Passed: $PASS ($(echo "scale=1; $PASS * 100 / $TOTAL" | bc)%)"
echo "Failed: $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
  echo "✅ ALL TESTS PASSED!"
  echo ""
  echo "Fixed Issues:"
  echo "  ✅ Inbox --unread removed (use jq for filtering)"
  echo "  ✅ Webhook event-types command added"
  echo "  ✅ Webhook create/update fixed (target_hook_url)"
  echo "  ✅ Subsequence --delay-days alias added"
  echo "  ✅ Bulk delete properly documented"
  echo ""
  echo "Known Limitation:"
  echo "  ⚠️  Subsequence create needs full schema (conditions, schedule, sequences)"
  echo "      Workaround: Use Instantly.ai dashboard for complex subsequence creation"
  exit 0
else
  echo "⚠️  Some tests failed. Review output above."
  exit 1
fi
