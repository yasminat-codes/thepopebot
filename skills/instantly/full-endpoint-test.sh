#!/bin/bash
# Full endpoint testing - including destructive operations with cleanup

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
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL=0
PASSED=0
FAILED=0

# Cleanup tracking
CREATED_CAMPAIGNS=()
CREATED_LEADS=()
CREATED_SUBSEQUENCES=()

cleanup() {
  echo ""
  echo -e "${BLUE}=== Cleanup ===${NC}"
  
  # Delete created subsequences
  for id in "${CREATED_SUBSEQUENCES[@]}"; do
    echo -n "Deleting subsequence $id... "
    if "$CLI" subsequences delete --id "$id" >/dev/null 2>&1; then
      echo -e "${GREEN}✓${NC}"
    else
      echo -e "${YELLOW}⚠ (may already be deleted)${NC}"
    fi
  done
  
  # Delete created leads
  for id in "${CREATED_LEADS[@]}"; do
    echo -n "Deleting lead $id... "
    if "$CLI" leads delete --id "$id" >/dev/null 2>&1; then
      echo -e "${GREEN}✓${NC}"
    else
      echo -e "${YELLOW}⚠ (may already be deleted)${NC}"
    fi
  done
  
  # Delete created campaigns
  for id in "${CREATED_CAMPAIGNS[@]}"; do
    echo -n "Deleting campaign $id... "
    if "$CLI" campaigns delete --id "$id" >/dev/null 2>&1; then
      echo -e "${GREEN}✓${NC}"
    else
      echo -e "${YELLOW}⚠ (may already be deleted)${NC}"
    fi
  done
}

trap cleanup EXIT

test_endpoint() {
  local name="$1"
  shift
  
  ((TOTAL++))
  echo -n "$name... "
  
  local output
  if output=$("$@" 2>&1); then
    if echo "$output" | jq empty 2>/dev/null; then
      if echo "$output" | jq -e '.error // .message' >/dev/null 2>&1; then
        local error=$(echo "$output" | jq -r '.error // .message')
        echo -e "${RED}✗ FAILED${NC} - $error"
        ((FAILED++))
        return 1
      else
        echo -e "${GREEN}✓ PASSED${NC}"
        ((PASSED++))
        echo "$output"
        return 0
      fi
    else
      echo -e "${RED}✗ FAILED${NC} - Invalid JSON"
      ((FAILED++))
      return 1
    fi
  else
    echo -e "${RED}✗ FAILED${NC} - Command error"
    ((FAILED++))
    return 1
  fi
}

echo "========================================"
echo "FULL ENDPOINT TEST - INSTANTLY.AI CLI"
echo "========================================"
echo ""

# ===========================
# CAMPAIGNS - FULL TEST
# ===========================
echo -e "${BLUE}=== CAMPAIGNS ===${NC}"

# 1. List
test_endpoint "[List] List campaigns" "$CLI" campaigns list --limit 5 >/dev/null

# 2. Create
echo -n "[Create] Create test campaign... "
CAMPAIGN_OUTPUT=$(test_endpoint "[Create]" "$CLI" campaigns create --name "CLI_TEST_$(date +%s)")
if CREATED_CAMPAIGN_ID=$(echo "$CAMPAIGN_OUTPUT" | jq -r '.id' 2>/dev/null); then
  if [[ -n "$CREATED_CAMPAIGN_ID" && "$CREATED_CAMPAIGN_ID" != "null" ]]; then
    CREATED_CAMPAIGNS+=("$CREATED_CAMPAIGN_ID")
    echo "  Created ID: $CREATED_CAMPAIGN_ID"
  fi
fi

# 3. Get existing campaign
EXISTING_CAMPAIGN=$("$CLI" campaigns list --limit 1 2>/dev/null | jq -r '.items[0].id' || echo "")
if [[ -n "$EXISTING_CAMPAIGN" && "$EXISTING_CAMPAIGN" != "null" ]]; then
  test_endpoint "[Get] Get campaign by ID" "$CLI" campaigns get --id "$EXISTING_CAMPAIGN" >/dev/null
  
  # 4. Update (if we created one)
  if [[ -n "$CREATED_CAMPAIGN_ID" && "$CREATED_CAMPAIGN_ID" != "null" ]]; then
    test_endpoint "[Update] Update campaign name" "$CLI" campaigns update --id "$CREATED_CAMPAIGN_ID" --name "CLI_TEST_UPDATED_$(date +%s)" >/dev/null
    
    # 5. Pause
    test_endpoint "[Pause] Pause campaign" "$CLI" campaigns pause --id "$CREATED_CAMPAIGN_ID" >/dev/null
    
    # 6. Resume
    test_endpoint "[Resume] Resume campaign" "$CLI" campaigns resume --id "$CREATED_CAMPAIGN_ID" >/dev/null
  fi
fi

echo ""

# ===========================
# LEADS - FULL TEST
# ===========================
echo -e "${BLUE}=== LEADS ===${NC}"

# 1. List
if [[ -n "$EXISTING_CAMPAIGN" && "$EXISTING_CAMPAIGN" != "null" ]]; then
  test_endpoint "[List] List leads" "$CLI" leads list --campaign-id "$EXISTING_CAMPAIGN" --limit 5 >/dev/null
  
  # 2. Add (use created or existing campaign)
  TEST_CAMPAIGN="${CREATED_CAMPAIGN_ID:-$EXISTING_CAMPAIGN}"
  echo -n "[Add] Add test lead... "
  LEAD_OUTPUT=$(test_endpoint "[Add]" "$CLI" leads add \
    --email "test_$(date +%s)@clitestdomain.example" \
    --first-name "CLI" \
    --last-name "Test" \
    --company "Test Co" \
    --campaign-id "$TEST_CAMPAIGN")
  
  if CREATED_LEAD_ID=$(echo "$LEAD_OUTPUT" | jq -r '.id' 2>/dev/null); then
    if [[ -n "$CREATED_LEAD_ID" && "$CREATED_LEAD_ID" != "null" ]]; then
      CREATED_LEADS+=("$CREATED_LEAD_ID")
      echo "  Created ID: $CREATED_LEAD_ID"
      
      # 3. Get
      test_endpoint "[Get] Get lead by ID" "$CLI" leads get --id "$CREATED_LEAD_ID" >/dev/null
      
      # 4. Update
      test_endpoint "[Update] Update lead" "$CLI" leads update \
        --id "$CREATED_LEAD_ID" \
        --first-name "Updated" \
        --last-name "Lead" >/dev/null
    fi
  fi
  
  # Get existing lead
  EXISTING_LEAD=$("$CLI" leads list --campaign-id "$EXISTING_CAMPAIGN" --limit 1 2>/dev/null | jq -r '.items[0].id' || echo "")
  if [[ -n "$EXISTING_LEAD" && "$EXISTING_LEAD" != "null" ]]; then
    test_endpoint "[Get] Get existing lead" "$CLI" leads get --id "$EXISTING_LEAD" >/dev/null
  fi
fi

echo ""

# ===========================
# ANALYTICS - FULL TEST
# ===========================
echo -e "${BLUE}=== ANALYTICS ===${NC}"

if [[ -n "$EXISTING_CAMPAIGN" && "$EXISTING_CAMPAIGN" != "null" ]]; then
  test_endpoint "[Campaign] Campaign analytics" "$CLI" analytics campaign --campaign-ids "$EXISTING_CAMPAIGN" >/dev/null
  test_endpoint "[Overview] Analytics overview" "$CLI" analytics overview --campaign-ids "$EXISTING_CAMPAIGN" >/dev/null
  test_endpoint "[Daily] Daily analytics" "$CLI" analytics daily --campaign-id "$EXISTING_CAMPAIGN" >/dev/null
fi

test_endpoint "[Account] Account warmup analytics" "$CLI" analytics account >/dev/null

echo ""

# ===========================
# EMAILS - FULL TEST
# ===========================
echo -e "${BLUE}=== EMAILS ===${NC}"

test_endpoint "[List] List emails" "$CLI" emails list --limit 5 >/dev/null
test_endpoint "[Unread] Unread count" "$CLI" emails unread-count >/dev/null

EXISTING_EMAIL=$("$CLI" emails list --limit 1 2>/dev/null | jq -r '.items[0].id' || echo "")
if [[ -n "$EXISTING_EMAIL" && "$EXISTING_EMAIL" != "null" ]]; then
  test_endpoint "[Get] Get email by ID" "$CLI" emails get --id "$EXISTING_EMAIL" >/dev/null
fi

echo ""

# ===========================
# SUBSEQUENCES - FULL TEST
# ===========================
echo -e "${BLUE}=== SUBSEQUENCES ===${NC}"

# 1. List
test_endpoint "[List] List subsequences" "$CLI" subsequences list --limit 5 >/dev/null

if [[ -n "$EXISTING_CAMPAIGN" && "$EXISTING_CAMPAIGN" != "null" ]]; then
  # 2. Create
  echo -n "[Create] Create test subsequence... "
  SUBSEQ_OUTPUT=$(test_endpoint "[Create]" "$CLI" subsequences create \
    --campaign-id "$EXISTING_CAMPAIGN" \
    --name "CLI_TEST_SUBSEQ_$(date +%s)" \
    --interval-days 2)
  
  if CREATED_SUBSEQ_ID=$(echo "$SUBSEQ_OUTPUT" | jq -r '.id' 2>/dev/null); then
    if [[ -n "$CREATED_SUBSEQ_ID" && "$CREATED_SUBSEQ_ID" != "null" ]]; then
      CREATED_SUBSEQUENCES+=("$CREATED_SUBSEQ_ID")
      echo "  Created ID: $CREATED_SUBSEQ_ID"
      
      # 3. Get
      test_endpoint "[Get] Get subsequence" "$CLI" subsequences get --id "$CREATED_SUBSEQ_ID" >/dev/null
      
      # 4. Update
      test_endpoint "[Update] Update subsequence" "$CLI" subsequences update \
        --id "$CREATED_SUBSEQ_ID" \
        --name "CLI_TEST_UPDATED_$(date +%s)" >/dev/null
      
      # 5. Status
      test_endpoint "[Status] Get sending status" "$CLI" subsequences status --id "$CREATED_SUBSEQ_ID" >/dev/null
      
      # 6. Pause
      test_endpoint "[Pause] Pause subsequence" "$CLI" subsequences pause --id "$CREATED_SUBSEQ_ID" >/dev/null
      
      # 7. Resume
      test_endpoint "[Resume] Resume subsequence" "$CLI" subsequences resume --id "$CREATED_SUBSEQ_ID" >/dev/null
      
      # 8. Duplicate
      echo -n "[Duplicate] Duplicate subsequence... "
      DUP_OUTPUT=$(test_endpoint "[Duplicate]" "$CLI" subsequences duplicate --id "$CREATED_SUBSEQ_ID")
      if DUP_ID=$(echo "$DUP_OUTPUT" | jq -r '.id' 2>/dev/null); then
        if [[ -n "$DUP_ID" && "$DUP_ID" != "null" ]]; then
          CREATED_SUBSEQUENCES+=("$DUP_ID")
          echo "  Duplicated ID: $DUP_ID"
        fi
      fi
    fi
  fi
  
  # Test on existing subsequence if available
  EXISTING_SUBSEQ=$("$CLI" subsequences list --limit 1 2>/dev/null | jq -r '.items[0].id' || echo "")
  if [[ -n "$EXISTING_SUBSEQ" && "$EXISTING_SUBSEQ" != "null" ]]; then
    test_endpoint "[Get] Get existing subsequence" "$CLI" subsequences get --id "$EXISTING_SUBSEQ" >/dev/null
  fi
fi

echo ""

# ===========================
# RAW API
# ===========================
echo -e "${BLUE}=== RAW API ===${NC}"

test_endpoint "[GET] Raw API - campaigns" "$CLI" api GET "campaigns?limit=3" >/dev/null
test_endpoint "[GET] Raw API - warmup analytics" "$CLI" api GET "accounts/warmup-analytics" >/dev/null

echo ""

# ===========================
# SUMMARY
# ===========================
echo "========================================"
echo -e "${BLUE}TEST SUMMARY${NC}"
echo "========================================"
echo "Total:  $TOTAL"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED/$TOTAL)*100}")
echo "Pass Rate: ${PASS_RATE}%"

echo ""
if [[ $FAILED -eq 0 ]]; then
  echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
  exit 0
else
  echo -e "${RED}✗ $FAILED TEST(S) FAILED${NC}"
  exit 1
fi
