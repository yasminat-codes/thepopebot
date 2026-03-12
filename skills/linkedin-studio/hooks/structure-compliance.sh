#!/bin/bash
# =============================================================================
# structure-compliance.sh
# LinkedIn Studio Quality Gate — Structure Compliance Checker
#
# Validates that the post's formatting and structure follow LinkedIn best
# practices for readability and engagement.
#
# Checks performed:
#   1. No paragraph longer than 3 lines without a line break
#   2. No sentence longer than 25 words (warn at 20, block at 25)
#   3. Hashtags are at the END of the post, not embedded in the body
#   4. Post does not start with "I" (weak opener for LinkedIn)
#   5. Last line does not end with a period (should be CTA or hashtags)
#
# Usage:
#   POST_TEXT="..." ./structure-compliance.sh
#
# Exit codes:
#   0 — All structure checks passed
#   1 — One or more blocking violations found
#
# chmod +x structure-compliance.sh
# =============================================================================

set -uo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SENTENCE_WARN_WORDS=20
SENTENCE_BLOCK_WORDS=25
MAX_PARAGRAPH_LINES=3

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
# State tracking
# -----------------------------------------------------------------------------
VIOLATIONS=()       # Blocking violations
WARNINGS=()         # Non-blocking warnings
FAILED=0

violation() {
    FAILED=1
    VIOLATIONS+=("$1")
    echo "  [VIOLATION] $1" >&2
}

warning() {
    WARNINGS+=("$1")
    echo "  [WARNING]   $1" >&2
}

ok() {
    echo "  [OK]        $1" >&2
}

echo "" >&2
echo "=== STRUCTURE COMPLIANCE CHECKER ===" >&2
echo "" >&2

# -----------------------------------------------------------------------------
# Check 1: No paragraph longer than 3 consecutive non-empty lines
# A paragraph ends when we hit a blank line. Count runs of non-blank lines.
# -----------------------------------------------------------------------------
echo "--- Check 1: Paragraph length ---" >&2

PARA_FAIL=0
CURRENT_PARA_START=0
CURRENT_PARA_LEN=0
LINE_NUM=0

while IFS= read -r line; do
    LINE_NUM=$((LINE_NUM + 1))
    if [ -z "$(echo "$line" | tr -d '[:space:]')" ]; then
        # Blank line: end of paragraph
        CURRENT_PARA_LEN=0
        CURRENT_PARA_START=$LINE_NUM
    else
        CURRENT_PARA_LEN=$((CURRENT_PARA_LEN + 1))
        if [ $CURRENT_PARA_LEN -eq 1 ]; then
            CURRENT_PARA_START=$LINE_NUM
        fi
        if [ $CURRENT_PARA_LEN -gt $MAX_PARAGRAPH_LINES ]; then
            if [ $PARA_FAIL -eq 0 ]; then
                violation "Paragraph starting at line $CURRENT_PARA_START exceeds $MAX_PARAGRAPH_LINES lines without a break. Long dense paragraphs kill scroll-through rates on LinkedIn. Add a blank line every 2–3 lines."
                PARA_FAIL=1
            fi
        fi
    fi
done <<< "$POST_TEXT"

if [ $PARA_FAIL -eq 0 ]; then
    ok "All paragraphs are 3 lines or fewer."
fi

# -----------------------------------------------------------------------------
# Check 2: Sentence length (warn at 20 words, block at 25)
# Split body text into sentences by ., !, ? followed by space or end of string
# -----------------------------------------------------------------------------
echo "" >&2
echo "--- Check 2: Sentence length ---" >&2

SENTENCE_WARN_FOUND=0
SENTENCE_BLOCK_FOUND=0

# Preprocess: remove hashtag lines (they skew word counts)
BODY_ONLY=$(echo "$POST_TEXT" | grep -v '^[[:space:]]*#')

# Split into sentences using Python if available, else use awk fallback
if command -v python3 &>/dev/null; then
    SENTENCES=$(python3 -c "
import sys, re
text = sys.stdin.read()
# Split on sentence-ending punctuation followed by space or newline
sentences = re.split(r'(?<=[.!?])\s+', text.strip())
for s in sentences:
    s = s.strip()
    if s:
        print(s)
" <<< "$BODY_ONLY")
else
    # Fallback: treat each line as a sentence
    SENTENCES="$BODY_ONLY"
fi

SENT_NUM=0
while IFS= read -r sentence; do
    [ -z "$sentence" ] && continue
    SENT_NUM=$((SENT_NUM + 1))
    WCOUNT=$(echo "$sentence" | wc -w | tr -d ' ')

    if [ "$WCOUNT" -ge "$SENTENCE_BLOCK_WORDS" ]; then
        violation "Sentence $SENT_NUM is $WCOUNT words (exceeds hard limit of $SENTENCE_BLOCK_WORDS). Rewrite as two shorter sentences. Sentence: \"$(echo "$sentence" | cut -c1-80)...\""
        SENTENCE_BLOCK_FOUND=1
    elif [ "$WCOUNT" -ge "$SENTENCE_WARN_WORDS" ]; then
        warning "Sentence $SENT_NUM is $WCOUNT words (over soft limit of $SENTENCE_WARN_WORDS). Consider splitting. Sentence: \"$(echo "$sentence" | cut -c1-80)...\""
        SENTENCE_WARN_FOUND=1
    fi
done <<< "$SENTENCES"

if [ $SENTENCE_WARN_FOUND -eq 0 ] && [ $SENTENCE_BLOCK_FOUND -eq 0 ]; then
    ok "All sentences are under $SENTENCE_WARN_WORDS words."
fi

# -----------------------------------------------------------------------------
# Check 3: Hashtags must appear only at the end of the post
# "End" = last contiguous block of hashtag lines before EOF
# Violation: hashtag found embedded in body paragraphs above the final block
# -----------------------------------------------------------------------------
echo "" >&2
echo "--- Check 3: Hashtag placement ---" >&2

# Find line number of first hashtag and of last non-hashtag content line
FIRST_HASHTAG_LINE=0
LAST_BODY_LINE=0
CURRENT_LINE=0

while IFS= read -r line; do
    CURRENT_LINE=$((CURRENT_LINE + 1))
    # Skip blank lines
    [ -z "$(echo "$line" | tr -d '[:space:]')" ] && continue

    if echo "$line" | grep -qE '(^|[^a-zA-Z0-9])#[a-zA-Z][a-zA-Z0-9_]*'; then
        # This line contains a hashtag
        if [ $FIRST_HASHTAG_LINE -eq 0 ]; then
            FIRST_HASHTAG_LINE=$CURRENT_LINE
        fi
    else
        # This is a body line (no hashtag)
        LAST_BODY_LINE=$CURRENT_LINE
    fi
done <<< "$POST_TEXT"

# Embedded hashtag = a hashtag appears BEFORE the last body line
if [ $FIRST_HASHTAG_LINE -gt 0 ] && [ $LAST_BODY_LINE -gt $FIRST_HASHTAG_LINE ]; then
    violation "Hashtag found at line $FIRST_HASHTAG_LINE, but body text continues until line $LAST_BODY_LINE. Hashtags must appear only at the end of the post, not embedded in the content. Embedded hashtags look unprofessional and disrupt reading flow."
else
    ok "Hashtags are correctly placed at the end of the post."
fi

# -----------------------------------------------------------------------------
# Check 4: Post must not start with "I"
# Starting with "I" is a weak LinkedIn opener — it centres the story before
# hooking the reader
# -----------------------------------------------------------------------------
echo "" >&2
echo "--- Check 4: Opening word ---" >&2

# head -1 isolates the first line before awk processes it, avoiding multi-line collapse
FIRST_WORD=$(echo "$POST_TEXT" | head -1 | sed 's/^[[:space:]]*//' | awk '{print $1}')

if [ "$FIRST_WORD" = "I" ]; then
    violation "Post starts with 'I'. Starting with 'I' is a weak LinkedIn opener — it leads with yourself rather than the reader's interest. Start with your hook, a number, a bold claim, or 'My' instead."
else
    ok "Post does not start with 'I'. First word: \"$FIRST_WORD\"."
fi

# -----------------------------------------------------------------------------
# Check 5: Last line must not end with a period
# The final line should be a CTA or hashtags, not a closed declarative sentence
# -----------------------------------------------------------------------------
echo "" >&2
echo "--- Check 5: Post ending ---" >&2

# Get the last non-empty line
LAST_LINE=$(echo "$POST_TEXT" | sed '/^[[:space:]]*$/d' | tail -1)

if echo "$LAST_LINE" | grep -qE '\.[[:space:]]*$'; then
    # Allow URLs ending in a domain (.com etc.) to pass
    if echo "$LAST_LINE" | grep -qE '\.(com|io|org|net|co|ai|app)[[:space:]]*$'; then
        ok "Last line ends with a URL domain — acceptable."
    else
        violation "Post ends with a period on the last line: \"$LAST_LINE\". The final line should be a CTA (question or imperative) or hashtags — not a closed sentence. A period signals 'done reading' and discourages engagement."
    fi
else
    ok "Post does not end with a period. Last line: \"$LAST_LINE\"."
fi

# -----------------------------------------------------------------------------
# Final report
# -----------------------------------------------------------------------------
echo "" >&2
echo "--- Summary ---" >&2
echo "  Violations (blocking): ${#VIOLATIONS[@]}" >&2
echo "  Warnings (non-blocking): ${#WARNINGS[@]}" >&2
echo "" >&2

if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo "Warnings:" >&2
    for w in "${WARNINGS[@]}"; do
        echo "  - $w" >&2
    done
    echo "" >&2
fi

if [ $FAILED -eq 1 ]; then
    echo "=== STRUCTURE COMPLIANCE: BLOCKED ===" >&2
    echo "" >&2
    echo "Violations to fix:" >&2
    for v in "${VIOLATIONS[@]}"; do
        echo "  - $v" >&2
    done
    echo "" >&2
    echo "Fix all violations and re-run before proceeding." >&2
    echo "BLOCKED"
    exit 1
else
    echo "=== STRUCTURE COMPLIANCE: PASSED ===" >&2
    echo "All structural checks passed. Post is correctly formatted for LinkedIn." >&2
    echo "PASSED"
    exit 0
fi
