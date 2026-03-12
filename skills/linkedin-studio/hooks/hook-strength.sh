#!/bin/bash
# =============================================================================
# hook-strength.sh
# LinkedIn Studio Quality Gate — Hook Quality Scorer
#
# Extracts the first line of the LinkedIn post (everything before the first
# blank line) and scores it against proven hook criteria.
#
# Scoring rubric (max 100 pts):
#   +20  Contains a number or statistic
#   +20  Contains a question mark
#   +15  Under 12 words
#   +20  Contains a power word (see list below)
#   +15  Personal story opener (I / My / We)
#   +10  Ends with "..." or ":"
#
# Threshold: 70+ to pass.
#
# Usage:
#   POST_TEXT="..." ./hook-strength.sh
#
# Exit codes:
#   0 — Hook scored 70+, passes
#   1 — Hook scored below 70, blocked with score and improvement suggestions
#
# chmod +x hook-strength.sh
# =============================================================================

set -uo pipefail

# -----------------------------------------------------------------------------
# Input
# -----------------------------------------------------------------------------
POST_TEXT="${POST_TEXT:-}"

if [ -z "$POST_TEXT" ]; then
    echo "[ERROR] POST_TEXT environment variable is not set." >&2
    echo "BLOCKED"
    exit 1
fi

# -----------------------------------------------------------------------------
# Extract the hook (first paragraph = everything before first blank line)
# -----------------------------------------------------------------------------
# Use awk to capture lines until the first empty line
HOOK=$(echo "$POST_TEXT" | awk '/^[[:space:]]*$/ { exit } { print }')

# Fallback: if no blank line found, use the very first line
if [ -z "$HOOK" ]; then
    HOOK=$(echo "$POST_TEXT" | head -1)
fi

# Trim leading/trailing whitespace
HOOK=$(echo "$HOOK" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

HOOK_WORD_COUNT=$(echo "$HOOK" | wc -w | tr -d ' ')

echo "" >&2
echo "=== HOOK STRENGTH CHECKER ===" >&2
echo "" >&2
echo "Hook extracted:" >&2
echo "  \"$HOOK\"" >&2
echo "  (${HOOK_WORD_COUNT} words)" >&2
echo "" >&2
echo "--- Scoring ---" >&2

SCORE=0
SUGGESTIONS=()

# -----------------------------------------------------------------------------
# Criterion 1: Contains a number or statistic (+20)
# Matches digits, percentages, currency amounts, ordinals
# Use grep -E pattern: \b not available on all macOS greps, so use [^a-zA-Z] boundary trick
# -----------------------------------------------------------------------------
if echo "$HOOK" | grep -qE '[0-9]+(%|k|K|M|B|st|nd|rd|th)?|\$[0-9]'; then
    SCORE=$((SCORE + 20))
    echo "  +20  Number/statistic detected" >&2
else
    SUGGESTIONS+=("Add a specific number or stat to the hook. Numbers create immediate credibility and stop the scroll (e.g., '3 years', '47%', '\$10k').")
    echo "  +0   No number or statistic found" >&2
fi

# -----------------------------------------------------------------------------
# Criterion 2: Contains a question mark (+20)
# -----------------------------------------------------------------------------
if echo "$HOOK" | grep -qF '?'; then
    SCORE=$((SCORE + 20))
    echo "  +20  Question detected" >&2
else
    SUGGESTIONS+=("Consider turning the hook into a question. Questions create an open loop that readers feel compelled to close.")
    echo "  +0   No question mark found" >&2
fi

# -----------------------------------------------------------------------------
# Criterion 3: Under 12 words (+15)
# Short hooks are punchier and perform better in LinkedIn's truncated preview
# -----------------------------------------------------------------------------
if [ "$HOOK_WORD_COUNT" -le 12 ]; then
    SCORE=$((SCORE + 15))
    echo "  +15  Hook is concise (${HOOK_WORD_COUNT} words, threshold: 12)" >&2
else
    SUGGESTIONS+=("Shorten the hook to under 12 words. LinkedIn shows ~1–2 lines before 'see more' — make every word earn its place. Current: ${HOOK_WORD_COUNT} words.")
    echo "  +0   Hook is too long (${HOOK_WORD_COUNT} words, threshold: 12)" >&2
fi

# -----------------------------------------------------------------------------
# Criterion 4: Contains a power word (+20)
# These words trigger emotional or curiosity responses
# -----------------------------------------------------------------------------
# Power words — allow common inflections (plural -s, past -ed, -ing) by using partial stem match
# Pattern: word boundary approximated by [^a-zA-Z] or start/end of string
POWER_PATTERN="mistakes?|secrets?|truths?|never|always|warnings?|stop(ped|ping)?|failed?|earned?|lost|changed?|regrets?|shocking|wrong|exposed?|revealed?|brutal|honest|real|hard"

# Use grep -iE with word-boundary approximation
if echo "$HOOK" | grep -qiE "(^|[^a-zA-Z])($POWER_PATTERN)([^a-zA-Z]|$)"; then
    MATCHED_WORD=$(echo "$HOOK" | grep -ioE "($POWER_PATTERN)" | head -1)
    SCORE=$((SCORE + 20))
    echo "  +20  Power word detected: \"$MATCHED_WORD\"" >&2
else
    SUGGESTIONS+=("Add a power word to trigger an emotional response. Try: mistake, secret, truth, warning, failed, earned, lost, changed, or brutal.")
    echo "  +0   No power word found" >&2
fi

# -----------------------------------------------------------------------------
# Criterion 5: Personal story opener — starts with "I ", "My ", or "We " (+15)
# First-person hooks outperform third-person on LinkedIn
# -----------------------------------------------------------------------------
if echo "$HOOK" | grep -qE '^(I |My |We )'; then
    SCORE=$((SCORE + 15))
    echo "  +15  Personal story opener detected (I / My / We)" >&2
else
    SUGGESTIONS+=("Open with 'I', 'My', or 'We' to ground the post in personal experience. First-person hooks feel authentic and relatable.")
    echo "  +0   No personal opener (I / My / We)" >&2
fi

# -----------------------------------------------------------------------------
# Criterion 6: Ends with "..." or ":" (+10)
# Creates an open loop / curiosity gap that drives clicks on "see more"
# -----------------------------------------------------------------------------
if echo "$HOOK" | grep -qE '(\.\.\.|:)[[:space:]]*$'; then
    SCORE=$((SCORE + 10))
    echo "  +10  Hook ends with '...' or ':' (curiosity gap)" >&2
else
    SUGGESTIONS+=("End the hook with '...' or ':' to create a curiosity gap — readers will click 'see more' to resolve the open loop.")
    echo "  +0   Hook does not end with '...' or ':'" >&2
fi

# -----------------------------------------------------------------------------
# Final result
# -----------------------------------------------------------------------------
echo "" >&2
echo "--- Result ---" >&2
echo "  Score: $SCORE / 100  (passing threshold: 70)" >&2
echo "" >&2

if [ $SCORE -ge 70 ]; then
    echo "=== HOOK STRENGTH: PASSED ===" >&2
    echo "Hook score $SCORE/100. Cleared for the next stage." >&2
    echo "PASSED (score: $SCORE/100)"
    exit 0
else
    echo "=== HOOK STRENGTH: BLOCKED ===" >&2
    echo "Hook score $SCORE/100 is below the 70-point threshold." >&2
    echo "" >&2
    echo "Improvements needed:" >&2
    IDX=1
    for suggestion in "${SUGGESTIONS[@]}"; do
        echo "  $IDX. $suggestion" >&2
        IDX=$((IDX + 1))
    done
    echo "" >&2
    echo "Revise the hook and re-run this gate." >&2
    echo "BLOCKED (score: $SCORE/100)"
    exit 1
fi
