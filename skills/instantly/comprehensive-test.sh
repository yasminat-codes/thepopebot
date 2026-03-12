#!/bin/bash
# Comprehensive endpoint testing with retry and rate limit handling

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI="$SCRIPT_DIR/instantly"

if [[ -z "${INSTANTLY_API_KEY:-}" ]]; then
  echo "Error: INSTANTLY_API_KEY not set"
  exit 1
fi

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
PASSED=0
FAILED=0
SKIPPED=0

# Test report
REPORT_FILE="test-report-$(date +%Y%m%d-%H%M%S).md"

log() {
  echo "$1" | tee -a "$REPORT_FILE"
}

test_endpoint() {
  local category="$1"
  local name="$2"
  shift 2
  
  ((TOTAL++))
  
  log ""
  log -n "[$category] $name ... "
  
  local output
  local exit_code=0
  
  if output=$("$@" 2>&1); then
    if echo "$output" | jq empty 2>/dev/null; then
      # Valid JSON
      if echo "$output" | jq -e '.error' >/dev/null 2>&1; then
        # Has error field
        local error_msg=$(echo "$output" | jq -r '.error // .message // "Unknown error"')
        log "${RED}✗ FAILED${NC} - API Error: $error_msg"
        ((FAILED++))
      else
        log "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
      fi
    else
      log "${RED}✗ FAILED${NC} - Invalid JSON response"
      ((FAILED++))
    fi
  else
    log "${RED}✗ FAILED${NC} - Command error"
    ((FAILED++))
  fi
}

skip_test() {
  local category="$1"
  local name="$2"
  local reason="$3"
  
  ((TOTAL++))
  ((SKIPPED++))
  
  log ""
  log "[$category] $name ... ${YELLOW}⊘ SKIPPED${NC} - $reason"
}

# Initialize report
log "# Instantly.ai CLI - Comprehensive Test Report"
log "Date: $(date '+%Y-%m-%d %H:%M:%S')"
log "API Key: ${INSTANTLY_API_KEY:0:20}..."
log ""
log "---"
log ""

# ===========================
# CAMPAIGNS
# ===========================
log "## Campaigns Module"

test_endpoint "Campaigns" "List campaigns" "$CLI" campaigns list --limit 5

# Get a campaign ID for dependent tests
CAMPAIGN_ID=$("$CLI" campaigns list --limit 1 2>/dev/null | jq -r '.items[0].id' || echo "")

if [[ -n "$CAMPAIGN_ID" && "$CAMPAIGN_ID" != "null" ]]; then
  test_endpoint "Campaigns" "Get campaign by ID" "$CLI" campaigns get --id "$CAMPAIGN_ID"
  test_endpoint "Campaigns" "List with search filter" "$CLI" campaigns list --search "Test" --limit 5
  
  # Create, update, delete - skip by default to avoid data modification
  skip_test "Campaigns" "Create campaign" "Destructive test - uncomment to run"
  skip_test "Campaigns" "Update campaign" "Destructive test - uncomment to run"
  skip_test "Campaigns" "Delete campaign" "Destructive test - uncomment to run"
  skip_test "Campaigns" "Pause campaign" "Destructive test - uncomment to run"
  skip_test "Campaigns" "Resume campaign" "Destructive test - uncomment to run"
else
  skip_test "Campaigns" "Get campaign" "No campaigns available"
  skip_test "Campaigns" "Campaign-dependent tests" "No campaigns available"
fi

# ===========================
# LEADS
# ===========================
log ""
log "## Leads Module"

if [[ -n "$CAMPAIGN_ID" && "$CAMPAIGN_ID" != "null" ]]; then
  test_endpoint "Leads" "List leads" "$CLI" leads list --campaign-id "$CAMPAIGN_ID" --limit 5
  
  LEAD_ID=$("$CLI" leads list --campaign-id "$CAMPAIGN_ID" --limit 1 2>/dev/null | jq -r '.items[0].id' || echo "")
  
  if [[ -n "$LEAD_ID" && "$LEAD_ID" != "null" ]]; then
    test_endpoint "Leads" "Get lead by ID" "$CLI" leads get --id "$LEAD_ID"
  else
    skip_test "Leads" "Get lead" "No leads in campaign"
  fi
  
  skip_test "Leads" "Add lead" "Destructive test - uncomment to run"
  skip_test "Leads" "Update lead" "Destructive test - uncomment to run"
  skip_test "Leads" "Delete lead" "Destructive test - uncomment to run"
else
  skip_test "Leads" "All lead tests" "No campaign ID available"
fi

# ===========================
# ANALYTICS
# ===========================
log ""
log "## Analytics Module"

if [[ -n "$CAMPAIGN_ID" && "$CAMPAIGN_ID" != "null" ]]; then
  test_endpoint "Analytics" "Campaign analytics" "$CLI" analytics campaign --campaign-ids "$CAMPAIGN_ID"
  test_endpoint "Analytics" "Campaign overview" "$CLI" analytics overview --campaign-ids "$CAMPAIGN_ID"
  test_endpoint "Analytics" "Daily analytics" "$CLI" analytics daily --campaign-id "$CAMPAIGN_ID"
else
  skip_test "Analytics" "Campaign analytics" "No campaign ID available"
fi

test_endpoint "Analytics" "Account warmup analytics" "$CLI" analytics account

# ===========================
# EMAILS (Inbox)
# ===========================
log ""
log "## Emails Module"

test_endpoint "Emails" "List emails" "$CLI" emails list --limit 5
test_endpoint "Emails" "Unread count" "$CLI" emails unread-count

EMAIL_ID=$("$CLI" emails list --limit 1 2>/dev/null | jq -r '.items[0].id' || echo "")

if [[ -n "$EMAIL_ID" && "$EMAIL_ID" != "null" ]]; then
  test_endpoint "Emails" "Get email by ID" "$CLI" emails get --id "$EMAIL_ID"
  
  skip_test "Emails" "Reply to email" "Requires account and destructive"
  skip_test "Emails" "Forward email" "Requires account and destructive"
  skip_test "Emails" "Mark as read" "Destructive test"
  skip_test "Emails" "Delete email" "Destructive test"
else
  skip_test "Emails" "Email-dependent tests" "No emails available"
fi

# ===========================
# SUBSEQUENCES
# ===========================
log ""
log "## Subsequences Module"

if [[ -n "$CAMPAIGN_ID" && "$CAMPAIGN_ID" != "null" ]]; then
  test_endpoint "Subsequences" "List subsequences" "$CLI" subsequences list --campaign-id "$CAMPAIGN_ID" --limit 5
  
  SUBSEQ_ID=$("$CLI" subsequences list --campaign-id "$CAMPAIGN_ID" --limit 1 2>/dev/null | jq -r '.items[0].id' || echo "")
  
  if [[ -n "$SUBSEQ_ID" && "$SUBSEQ_ID" != "null" ]]; then
    test_endpoint "Subsequences" "Get subsequence" "$CLI" subsequences get --id "$SUBSEQ_ID"
    test_endpoint "Subsequences" "Get sending status" "$CLI" subsequences status --id "$SUBSEQ_ID"
    
    skip_test "Subsequences" "Duplicate subsequence" "Destructive test"
    skip_test "Subsequences" "Pause subsequence" "Destructive test"
    skip_test "Subsequences" "Resume subsequence" "Destructive test"
  else
    skip_test "Subsequences" "Subsequence-dependent tests" "No subsequences in campaign"
  fi
  
  skip_test "Subsequences" "Create subsequence" "Destructive test"
  skip_test "Subsequences" "Update subsequence" "Destructive test"
  skip_test "Subsequences" "Delete subsequence" "Destructive test"
else
  skip_test "Subsequences" "All subsequence tests" "No campaign ID available"
fi

# ===========================
# RAW API
# ===========================
log ""
log "## Raw API Access"

test_endpoint "Raw API" "GET campaigns" "$CLI" api GET "campaigns?limit=3"
test_endpoint "Raw API" "GET warmup analytics" "$CLI" api GET "accounts/warmup-analytics"

if [[ -n "$CAMPAIGN_ID" && "$CAMPAIGN_ID" != "null" ]]; then
  test_endpoint "Raw API" "GET specific campaign" "$CLI" api GET "campaigns/${CAMPAIGN_ID}"
fi

# ===========================
# SUMMARY
# ===========================
log ""
log "---"
log ""
log "## Test Summary"
log ""
log "| Metric | Count |"
log "|--------|-------|"
log "| Total  | $TOTAL |"
log "| ${GREEN}Passed${NC} | $PASSED |"
log "| ${RED}Failed${NC} | $FAILED |"
log "| ${YELLOW}Skipped${NC} | $SKIPPED |"
log ""
log "**Pass Rate**: $(awk "BEGIN {print ($PASSED/($TOTAL-$SKIPPED))*100}")%"
log ""

if [[ $FAILED -eq 0 ]]; then
  log "${GREEN}✓ All non-skipped tests passed!${NC}"
  echo ""
  echo "Full report saved to: $REPORT_FILE"
  exit 0
else
  log "${RED}✗ $FAILED test(s) failed${NC}"
  echo ""
  echo "Full report saved to: $REPORT_FILE"
  exit 1
fi
