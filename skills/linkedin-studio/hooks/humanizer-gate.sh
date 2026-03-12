#!/bin/bash
# =============================================================================
# humanizer-gate.sh
# LinkedIn Studio Quality Gate — AI Detection Gate
#
# Runs AFTER content-writer, BEFORE structure-reviewer.
# Scans post text for common AI-generated phrases and structural giveaways
# that the humanizer agent may have missed.
#
# Usage:
#   POST_TEXT="..." ./humanizer-gate.sh
#
# Exit codes:
#   0 — Clean (or only 1–2 phrases found, WARNING issued but not blocked)
#   1 — 3+ AI phrases found, post is BLOCKED for re-humanization
#
# chmod +x humanizer-gate.sh
# =============================================================================

set -uo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
WARN_THRESHOLD=1     # 1–2 matches → WARNING
BLOCK_THRESHOLD=3    # 3+ matches  → BLOCK

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
# Phase 1: Banned phrase matching
# Each pattern is a grep-compatible extended regex (case-insensitive)
# -----------------------------------------------------------------------------

# Array of phrase patterns known to be AI giveaways
AI_PHRASES=(
    "leverage"
    "utilize"
    "it'?s important to note"
    "in today'?s (world|landscape|digital|fast)"
    "game.changer"
    "delve into"
    "dive deep"
    "unpack"
    "multifaceted"
    "let'?s explore"
    "in conclusion"
    "furthermore"
    "moreover"
    "nevertheless"
    "it is worth noting"
    "from a [a-z]+ perspective"
    "in the realm of"
    "it'?s no secret"
    "at the end of the day"
    "the fact of the matter"
    "needless to say"
    "as we navigate"
    "in an ever.changing"
    "the bottom line"
    "it goes without saying"
)

PHRASE_MATCHES=()
PHRASE_MATCH_COUNT=0

echo "" >&2
echo "=== AI DETECTION GATE ===" >&2
echo "" >&2
echo "--- Phase 1: Banned phrase scan ---" >&2

for pattern in "${AI_PHRASES[@]}"; do
    # Use grep -iE (POSIX extended regex, case insensitive) — compatible with macOS grep
    if echo "$POST_TEXT" | grep -qiE "$pattern" 2>/dev/null; then
        # Extract the actual matched text for the report
        MATCHED=$(echo "$POST_TEXT" | grep -ioE "$pattern" 2>/dev/null | head -1)
        PHRASE_MATCHES+=("\"$MATCHED\" (pattern: $pattern)")
        PHRASE_MATCH_COUNT=$((PHRASE_MATCH_COUNT + 1))
        echo "  [FOUND] $MATCHED" >&2
    fi
done

if [ $PHRASE_MATCH_COUNT -eq 0 ]; then
    echo "  [CLEAN] No banned AI phrases detected." >&2
fi

# -----------------------------------------------------------------------------
# Phase 2: Overly parallel sentence structure
# Checks if 3+ sentences in a row begin with the same word
# -----------------------------------------------------------------------------

echo "" >&2
echo "--- Phase 2: Parallel sentence structure ---" >&2

PARALLEL_VIOLATIONS=0

# Extract sentences that start each line (simple heuristic: capitalised line starts)
# Build a list of first words of non-empty lines
FIRST_WORDS=$(echo "$POST_TEXT" | grep -v '^[[:space:]]*$' | grep -v '^#' | \
    sed 's/^[[:space:]]*//' | \
    grep -E '^[A-Z]' | \
    awk '{print tolower($1)}')

# Use awk to detect 3+ consecutive identical first words
PARALLEL_HIT=$(echo "$FIRST_WORDS" | awk '
{
    if ($0 == prev) {
        run++
        if (run >= 2) { found=1; print "Detected 3+ sentences starting with: \"" $0 "\"" }
    } else {
        run=1
    }
    prev=$0
}
' | head -1)

if [ -n "$PARALLEL_HIT" ]; then
    PARALLEL_VIOLATIONS=1
    echo "  [FOUND] $PARALLEL_HIT" >&2
    echo "  Overly parallel sentence structure is a strong AI signal. Vary your sentence openers." >&2
else
    echo "  [CLEAN] No over-parallel sentence structures detected." >&2
fi

# -----------------------------------------------------------------------------
# Phase 3: Excessive em-dashes or bullet points (AI formatting signals)
# -----------------------------------------------------------------------------

echo "" >&2
echo "--- Phase 3: AI formatting signals ---" >&2

FORMATTING_ISSUES=0

# Count em-dashes (— or --)
EM_DASH_COUNT=$(echo "$POST_TEXT" | grep -oE '(—|–|--)' | wc -l | tr -d ' ')
if [ "$EM_DASH_COUNT" -gt 3 ]; then
    FORMATTING_ISSUES=1
    echo "  [FOUND] Excessive em-dashes: $EM_DASH_COUNT found (threshold: 3). Heavy em-dash usage is a known AI tell." >&2
else
    echo "  [CLEAN] Em-dash count acceptable: $EM_DASH_COUNT" >&2
fi

# Count bullet/list lines (lines starting with -, *, or numbered list markers)
# Use python3 for reliable counting, grep as fallback — avoids grep -c returning "0\n" artifacts
if command -v python3 &>/dev/null; then
    BULLET_COUNT=$(echo "$POST_TEXT" | python3 -c "
import sys, re
lines = sys.stdin.readlines()
count = sum(1 for l in lines if re.match(r'^\s*[-*]|^\s*[0-9]+\.', l))
print(count)
")
else
    BULLET_COUNT=0
    while IFS= read -r bline; do
        echo "$bline" | grep -qE '^[[:space:]]*[-*]|^[[:space:]]*[0-9]+\.' && BULLET_COUNT=$((BULLET_COUNT + 1))
    done <<< "$POST_TEXT"
fi
BULLET_COUNT=${BULLET_COUNT:-0}
if [ "$BULLET_COUNT" -gt 5 ]; then
    FORMATTING_ISSUES=1
    echo "  [FOUND] Excessive bullet points: $BULLET_COUNT lines. LinkedIn posts with heavy lists feel AI-generated. Prose reads better." >&2
else
    echo "  [CLEAN] Bullet point count acceptable: $BULLET_COUNT" >&2
fi

# -----------------------------------------------------------------------------
# Final scoring and decision
# -----------------------------------------------------------------------------

# Add structural violation penalty to phrase count for decision
TOTAL_ISSUES=$PHRASE_MATCH_COUNT
[ $PARALLEL_VIOLATIONS -gt 0 ] && TOTAL_ISSUES=$((TOTAL_ISSUES + 1))
[ $FORMATTING_ISSUES -gt 0 ]   && TOTAL_ISSUES=$((TOTAL_ISSUES + 1))

echo "" >&2
echo "--- Summary ---" >&2
echo "  Banned phrases:         $PHRASE_MATCH_COUNT" >&2
echo "  Parallel structure:     $PARALLEL_VIOLATIONS" >&2
echo "  Formatting signals:     $FORMATTING_ISSUES" >&2
echo "  Total issues:           $TOTAL_ISSUES" >&2
echo "" >&2

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo "=== AI DETECTION GATE: PASSED ===" >&2
    echo "Content reads as authentically human. No AI markers detected." >&2
    echo "PASSED"
    exit 0

elif [ $TOTAL_ISSUES -le $WARN_THRESHOLD ]; then
    echo "=== AI DETECTION GATE: WARNING ===" >&2
    echo "Minor AI signals detected ($TOTAL_ISSUES issue(s)). Post is not blocked, but review the flagged items before scheduling." >&2
    if [ ${#PHRASE_MATCHES[@]} -gt 0 ]; then
        echo "Flagged phrases:" >&2
        for match in "${PHRASE_MATCHES[@]}"; do
            echo "  - $match" >&2
        done
    fi
    echo "WARNING"
    exit 0

else
    echo "=== AI DETECTION GATE: BLOCKED ===" >&2
    echo "Too many AI signals found ($TOTAL_ISSUES issues — threshold for block: $BLOCK_THRESHOLD)." >&2
    echo "Return this post to the humanizer agent for another pass." >&2
    echo "" >&2
    if [ ${#PHRASE_MATCHES[@]} -gt 0 ]; then
        echo "Phrases to replace:" >&2
        for match in "${PHRASE_MATCHES[@]}"; do
            echo "  - $match" >&2
        done
    fi
    echo "BLOCKED"
    exit 1
fi
