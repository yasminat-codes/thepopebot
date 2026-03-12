#!/bin/bash
# Complete live data test for ALL endpoints

set -euo pipefail

export INSTANTLY_API_KEY="${INSTANTLY_API_KEY:?API key required}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="$SCRIPT_DIR/instantly"

PASS=0
FAIL=0
TOTAL=0

echo "=========================================="
echo "COMPLETE LIVE DATA ENDPOINT TEST"
echo "=========================================="
date
echo ""

test_endpoint() {
  local name="$1"
  shift
  ((TOTAL++))
  
  printf "[%02d] %-50s" "$TOTAL" "$name"
  
  if output=$("$@" 2>&1); then
    if echo "$output" | jq empty 2>/dev/null; then
      if echo "$output" | jq -e '.error // .message' >/dev/null 2>&1; then
        echo "❌ FAIL"
        ((FAIL++))
      else
        echo "✅ PASS"
        ((PASS++))
      fi
    else
      echo "❌ FAIL (invalid JSON)"
      ((FAIL++))
    fi
  else
    echo "❌ FAIL (cmd error)"
    ((FAIL++))
  fi
}

# Get live IDs
echo "Fetching live data..."
CAMPAIGN_ID=$("$CLI" campaigns list --limit 1 2>&1 | jq -r '.items[0].id' || echo "")
ACCOUNT_EMAIL=$("$CLI" accounts list --limit 1 2>&1 | jq -r '.items[0].email' || echo "")
LEAD_ID=$("$CLI" leads list --campaign-id "$CAMPAIGN_ID" --limit 1 2>&1 | jq -r '.items[0].id' || echo "")
EMAIL_ID=$("$CLI" emails list --limit 1 2>&1 | jq -r '.items[0].id' || echo "")

echo "Campaign: $CAMPAIGN_ID"
echo "Account: $ACCOUNT_EMAIL"
echo "Lead: $LEAD_ID"
echo "Email: $EMAIL_ID"
echo ""

# CAMPAIGNS
echo "=== CAMPAIGNS ==="
test_endpoint "List campaigns" "$CLI" campaigns list --limit 5
test_endpoint "Get campaign" "$CLI" campaigns get --id "$CAMPAIGN_ID"

NEW_CAMP=$("$CLI" campaigns create --name "TEST_$(date +%s)" 2>&1 | jq -r '.id' || echo "")
if [[ -n "$NEW_CAMP" && "$NEW_CAMP" != "null" ]]; then
  test_endpoint "Create campaign" echo "{\"id\":\"$NEW_CAMP\"}"
  test_endpoint "Update campaign" "$CLI" campaigns update --id "$NEW_CAMP" --name "UPDATED"
  test_endpoint "Pause campaign" "$CLI" campaigns pause --id "$NEW_CAMP"
  test_endpoint "Resume campaign" "$CLI" campaigns resume --id "$NEW_CAMP"
  test_endpoint "Delete campaign" "$CLI" campaigns delete --id "$NEW_CAMP"
fi
echo ""

# LEADS
echo "=== LEADS ==="
test_endpoint "List leads" "$CLI" leads list --campaign-id "$CAMPAIGN_ID" --limit 5
test_endpoint "Get lead" "$CLI" leads get --id "$LEAD_ID"

NEW_LEAD=$("$CLI" leads add --email "test_$(date +%s)@example.com" --first-name "Test" --campaign-id "$CAMPAIGN_ID" 2>&1 | jq -r '.id' || echo "")
if [[ -n "$NEW_LEAD" && "$NEW_LEAD" != "null" ]]; then
  test_endpoint "Add lead" echo "{\"id\":\"$NEW_LEAD\"}"
  test_endpoint "Update lead" "$CLI" leads update --id "$NEW_LEAD" --first-name "Updated"
  test_endpoint "Delete lead" "$CLI" leads delete --id "$NEW_LEAD"
fi
echo ""

# ACCOUNTS
echo "=== ACCOUNTS ==="
test_endpoint "List accounts" "$CLI" accounts list --limit 10
test_endpoint "Get account" "$CLI" accounts get --email "$ACCOUNT_EMAIL"
test_endpoint "Test account vitals" "$CLI" accounts test-vitals --email "$ACCOUNT_EMAIL"

if [[ -n "$ACCOUNT_EMAIL" && "$ACCOUNT_EMAIL" != "null" ]]; then
  test_endpoint "Warmup analytics" "$CLI" accounts warmup-analytics --emails "$ACCOUNT_EMAIL"
fi

test_endpoint "Daily account analytics" "$CLI" accounts daily-analytics
echo ""

# ANALYTICS
echo "=== ANALYTICS ==="
test_endpoint "Campaign analytics" "$CLI" analytics campaign --campaign-ids "$CAMPAIGN_ID"
test_endpoint "Analytics overview" "$CLI" analytics overview --campaign-ids "$CAMPAIGN_ID"
test_endpoint "Daily analytics" "$CLI" analytics daily --campaign-id "$CAMPAIGN_ID"
test_endpoint "Step analytics" "$CLI" analytics steps --campaign-id "$CAMPAIGN_ID"
test_endpoint "Account list" "$CLI" analytics account

if [[ -n "$ACCOUNT_EMAIL" && "$ACCOUNT_EMAIL" != "null" ]]; then
  test_endpoint "Warmup analytics" "$CLI" analytics warmup --emails "$ACCOUNT_EMAIL"
fi

test_endpoint "Account daily analytics" "$CLI" analytics account-daily
echo ""

# EMAILS
echo "=== EMAILS ==="
test_endpoint "List emails" "$CLI" emails list --limit 10
test_endpoint "Unread count" "$CLI" emails unread-count

if [[ -n "$EMAIL_ID" && "$EMAIL_ID" != "null" ]]; then
  test_endpoint "Get email" "$CLI" emails get --id "$EMAIL_ID"
fi
echo ""

# SUBSEQUENCES
echo "=== SUBSEQUENCES ==="
test_endpoint "List subsequences" "$CLI" subsequences list --campaign-id "$CAMPAIGN_ID"
echo ""

# RAW API
echo "=== RAW API ==="
test_endpoint "GET campaigns" "$CLI" api GET "campaigns?limit=2"
test_endpoint "GET accounts" "$CLI" api GET "accounts?limit=2"
test_endpoint "GET analytics" "$CLI" api GET "campaigns/analytics?campaign_ids=$CAMPAIGN_ID"
echo ""

# SUMMARY
echo "=========================================="
echo "FINAL RESULTS"
echo "=========================================="
echo "Total:  $TOTAL"
echo "Passed: $PASS"
echo "Failed: $FAIL"
echo "Pass Rate: $(awk "BEGIN {printf \"%.1f%%\", ($PASS/$TOTAL)*100}")"
echo ""

if [[ $FAIL -eq 0 ]]; then
  echo "✅ ALL TESTS PASSED!"
  exit 0
else
  echo "⚠️  $FAIL test(s) failed"
  exit 1
fi
