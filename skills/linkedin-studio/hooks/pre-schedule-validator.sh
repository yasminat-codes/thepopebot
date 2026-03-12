#!/bin/bash
# =============================================================================
# pre-schedule-validator.sh
# LinkedIn Studio Quality Gate — Pre-Schedule Validation
#
# Runs BEFORE any post is sent to Metricool. Validates that post content
# meets minimum quality and readiness standards before scheduling.
#
# Usage:
#   POST_TEXT="..."  \
#   POST_STATUS="approved" \
#   METRICOOL_ID="" \
#   IS_CAROUSEL_SLIDE="false" \
#   ./pre-schedule-validator.sh
#
# Exit codes:
#   0 — All checks passed, safe to schedule
#   1 — One or more checks failed, post blocked
#
# chmod +x pre-schedule-validator.sh
# =============================================================================

set -uo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
MIN_WORDS_STANDARD=150
MAX_WORDS_STANDARD=300
MIN_WORDS_CAROUSEL=50
MAX_WORDS_CAROUSEL=150
MIN_HASHTAGS=3
MAX_HASHTAGS=5

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
FAILED=0
ERRORS=()

fail() {
    FAILED=1
    ERRORS+=("FAIL: $1")
    echo "[FAIL] $1" >&2
}

pass() {
    echo "[PASS] $1" >&2
}

warn() {
    echo "[WARN] $1" >&2
}

count_words() {
    echo "$1" | wc -w | tr -d ' '
}

# -----------------------------------------------------------------------------
# Read inputs from environment variables (safe defaults)
# -----------------------------------------------------------------------------
POST_TEXT="${POST_TEXT:-}"
POST_STATUS="${POST_STATUS:-draft}"
METRICOOL_ID="${METRICOOL_ID:-}"
IS_CAROUSEL_SLIDE="${IS_CAROUSEL_SLIDE:-false}"

# -----------------------------------------------------------------------------
# Check 1: Post text must not be empty
# -----------------------------------------------------------------------------
if [ -z "$POST_TEXT" ]; then
    fail "Post text is empty. Cannot schedule an empty post."
else
    pass "Post text is present."
fi

# If empty, no point continuing further checks
if [ $FAILED -eq 1 ]; then
    echo "" >&2
    echo "=== PRE-SCHEDULE VALIDATION FAILED ===" >&2
    echo "Errors:" >&2
    for err in "${ERRORS[@]}"; do
        echo "  - $err" >&2
    done
    echo "BLOCKED"
    exit 1
fi

# -----------------------------------------------------------------------------
# Check 2: Post length (word count)
# -----------------------------------------------------------------------------
WORD_COUNT=$(count_words "$POST_TEXT")

if [ "$IS_CAROUSEL_SLIDE" = "true" ]; then
    MIN_WORDS=$MIN_WORDS_CAROUSEL
    MAX_WORDS=$MAX_WORDS_CAROUSEL
    CONTENT_TYPE="carousel slide"
else
    MIN_WORDS=$MIN_WORDS_STANDARD
    MAX_WORDS=$MAX_WORDS_STANDARD
    CONTENT_TYPE="standard post"
fi

if [ "$WORD_COUNT" -lt "$MIN_WORDS" ]; then
    fail "Post is too short for a $CONTENT_TYPE: $WORD_COUNT words (minimum: $MIN_WORDS). Add more substance to the content."
elif [ "$WORD_COUNT" -gt "$MAX_WORDS" ]; then
    fail "Post is too long for a $CONTENT_TYPE: $WORD_COUNT words (maximum: $MAX_WORDS). Trim the content or split into a carousel."
else
    pass "Word count is acceptable: $WORD_COUNT words (${MIN_WORDS}–${MAX_WORDS} for $CONTENT_TYPE)."
fi

# -----------------------------------------------------------------------------
# Check 3: CTA must be present
# Heuristic: last non-hashtag line ends with '?' or looks like an imperative verb
# -----------------------------------------------------------------------------

# Strip hashtag lines from end to find the last content line
BODY_LINES=$(echo "$POST_TEXT" | grep -v '^#' | sed '/^[[:space:]]*$/d')
LAST_CONTENT_LINE=$(echo "$BODY_LINES" | tail -1)

HAS_CTA=0

# Check for question mark (grep -F is literal; use -E for pattern match)
if echo "$LAST_CONTENT_LINE" | grep -qE '\?'; then
    HAS_CTA=1
fi

# Check for common imperative starters (comment on, share, follow, tag, click, read, join, drop, tell, let)
if echo "$LAST_CONTENT_LINE" | grep -qiE '^(comment|share|follow|tag|click|read|join|drop|tell|let me know|save|repost|dm|connect|subscribe|visit|check out|try|start|grab)'; then
    HAS_CTA=1
fi

if [ $HAS_CTA -eq 1 ]; then
    pass "CTA detected in the final content line."
else
    fail "No CTA found. The last content line must end with a question (?) or start with an imperative verb (e.g., 'Share this if...', 'Comment below', 'Follow for more')."
fi

# -----------------------------------------------------------------------------
# Check 4: Hashtags present (3–5 hashtags starting with #)
# -----------------------------------------------------------------------------
# Count hashtags: words starting with # that are preceded by space/start-of-line
# Use python3 for reliable lookbehind; fall back to simpler grep -oE on word boundaries
if command -v python3 &>/dev/null; then
    HASHTAG_COUNT=$(echo "$POST_TEXT" | python3 -c "
import sys, re
text = sys.stdin.read()
matches = re.findall(r'(?<![a-zA-Z0-9])#[a-zA-Z][a-zA-Z0-9_]*', text)
print(len(matches))
")
else
    HASHTAG_COUNT=$(echo "$POST_TEXT" | grep -oE '(^|[^a-zA-Z0-9])#[a-zA-Z][a-zA-Z0-9_]*' | wc -l | tr -d ' ')
fi

if [ "$HASHTAG_COUNT" -lt "$MIN_HASHTAGS" ]; then
    fail "Too few hashtags: found $HASHTAG_COUNT (minimum: $MIN_HASHTAGS). Add relevant hashtags to extend reach."
elif [ "$HASHTAG_COUNT" -gt "$MAX_HASHTAGS" ]; then
    fail "Too many hashtags: found $HASHTAG_COUNT (maximum: $MAX_HASHTAGS). LinkedIn penalises posts that look spammy."
else
    pass "Hashtag count acceptable: $HASHTAG_COUNT hashtags found."
fi

# -----------------------------------------------------------------------------
# Check 5: Content queue status must be 'approved', not 'draft'
# -----------------------------------------------------------------------------
if [ "$POST_STATUS" = "approved" ]; then
    pass "Content status is 'approved'."
elif [ "$POST_STATUS" = "draft" ]; then
    fail "Post is still in 'draft' status. Move it to 'approved' before scheduling."
else
    fail "Unknown post status: '$POST_STATUS'. Expected 'approved'."
fi

# -----------------------------------------------------------------------------
# Check 6: Post must not already be scheduled (no metricool_id)
# -----------------------------------------------------------------------------
if [ -n "$METRICOOL_ID" ]; then
    fail "Post already has a Metricool ID ($METRICOOL_ID), meaning it is already scheduled. Unschedule first before rescheduling."
else
    pass "No existing Metricool ID — post is not yet scheduled."
fi

# -----------------------------------------------------------------------------
# Final result
# -----------------------------------------------------------------------------
echo "" >&2

if [ $FAILED -eq 1 ]; then
    echo "=== PRE-SCHEDULE VALIDATION FAILED ===" >&2
    echo "" >&2
    echo "The following checks did not pass:" >&2
    for err in "${ERRORS[@]}"; do
        echo "  $err" >&2
    done
    echo "" >&2
    echo "Fix the above issues and re-run validation before scheduling." >&2
    echo "BLOCKED"
    exit 1
else
    echo "=== PRE-SCHEDULE VALIDATION PASSED ===" >&2
    echo "All 6 checks passed. Post is cleared for scheduling via Metricool." >&2
    echo "PASSED"
    exit 0
fi
