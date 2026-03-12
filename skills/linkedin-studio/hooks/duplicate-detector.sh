#!/bin/bash
# =============================================================================
# duplicate-detector.sh
# LinkedIn Studio Quality Gate — Duplicate Content Detector
#
# Detects whether a new post is too similar to content posted in the last 30
# days, preventing content recycling and protecting LinkedIn algorithm health.
#
# Similarity method: trigram overlap
#   - Splits post text into 3-word sequences (trigrams)
#   - Counts how many trigrams the new post shares with each recent post
#   - Reports overlap percentage
#
# Thresholds:
#   >= 60%  →  BLOCK   (too similar — would look like repost)
#   40–59%  →  WARNING (noticeable overlap — review suggested)
#   < 40%   →  PASS    (sufficiently unique)
#
# Data sources (in priority order):
#   1. Neon database via NEON_DATABASE_URL env var (queries content_queue table)
#   2. Local cache file: .linkedin-studio-cache/recent-posts.txt
#      Format: one post per line, encoded as base64 (to handle newlines)
#
# Usage:
#   POST_TEXT="..." NEON_DATABASE_URL="postgresql://..." ./duplicate-detector.sh
#
# Exit codes:
#   0 — Post is unique enough (or WARNING only)
#   1 — Post is too similar to a recent post (BLOCKED)
#
# chmod +x duplicate-detector.sh
# =============================================================================

set -uo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
WARN_THRESHOLD=40
BLOCK_THRESHOLD=60
LOOKBACK_DAYS=30
CACHE_DIR="${HOME}/.linkedin-studio-cache"
CACHE_FILE="${CACHE_DIR}/recent-posts.txt"

# -----------------------------------------------------------------------------
# Input
# -----------------------------------------------------------------------------
POST_TEXT="${POST_TEXT:-}"
NEON_DATABASE_URL="${NEON_DATABASE_URL:-}"

if [ -z "$POST_TEXT" ]; then
    echo "[ERROR] POST_TEXT environment variable is not set." >&2
    echo "BLOCKED"
    exit 1
fi

echo "" >&2
echo "=== DUPLICATE CONTENT DETECTOR ===" >&2
echo "" >&2

# -----------------------------------------------------------------------------
# Trigram computation helper (requires Python 3)
# Returns sorted list of trigrams, one per line
# -----------------------------------------------------------------------------
compute_trigrams() {
    local text="$1"
    python3 - "$text" <<'PYEOF'
import sys, re

text = sys.argv[1] if len(sys.argv) > 1 else ""
# Normalise: lowercase, remove punctuation, collapse whitespace
text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
words = text.split()

trigrams = set()
for i in range(len(words) - 2):
    trigrams.add(f"{words[i]} {words[i+1]} {words[i+2]}")

for t in sorted(trigrams):
    print(t)
PYEOF
}

# -----------------------------------------------------------------------------
# Similarity calculation
# Returns an integer percentage 0–100
# -----------------------------------------------------------------------------
similarity_percent() {
    local text_a="$1"
    local text_b="$2"

    python3 - "$text_a" "$text_b" <<'PYEOF'
import sys, re

def trigrams(text):
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text.lower())
    words = text.split()
    return set(f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words)-2)) if len(words) >= 3 else set()

a = trigrams(sys.argv[1]) if len(sys.argv) > 1 else set()
b = trigrams(sys.argv[2]) if len(sys.argv) > 2 else set()

if not a or not b:
    print(0)
else:
    overlap = len(a & b)
    # Use Jaccard overlap relative to the SMALLER set (favours catching near-copies)
    denominator = min(len(a), len(b))
    score = round((overlap / denominator) * 100) if denominator > 0 else 0
    print(score)
PYEOF
}

# Verify Python 3 is available (required for trigram logic)
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] python3 is required for trigram similarity calculation but was not found." >&2
    echo "[ERROR] Install Python 3 and re-run this hook." >&2
    echo "BLOCKED"
    exit 1
fi

# -----------------------------------------------------------------------------
# Load recent posts
# Priority 1: Neon database
# Priority 2: Local cache file
# -----------------------------------------------------------------------------
RECENT_POSTS=()
DATA_SOURCE="none"

# --- Priority 1: Database ---
if [ -n "$NEON_DATABASE_URL" ]; then
    echo "--- Data source: Neon database ---" >&2

    # Check psql is available
    if command -v psql &>/dev/null; then
        DB_QUERY="SELECT encode(post_text::bytea, 'base64') FROM content_queue WHERE created_at >= NOW() - INTERVAL '${LOOKBACK_DAYS} days' AND post_text IS NOT NULL AND post_text != '' LIMIT 100;"

        # Execute query safely, capture output, suppress psql noise
        DB_RESULT=$(PGPASSWORD="" psql "$NEON_DATABASE_URL" -t -A -c "$DB_QUERY" 2>/dev/null || echo "")

        if [ -n "$DB_RESULT" ]; then
            while IFS= read -r encoded_post; do
                [ -z "$encoded_post" ] && continue
                # Decode base64 back to text
                DECODED=$(echo "$encoded_post" | base64 -d 2>/dev/null || echo "")
                [ -n "$DECODED" ] && RECENT_POSTS+=("$DECODED")
            done <<< "$DB_RESULT"
            DATA_SOURCE="database"
            echo "  Loaded ${#RECENT_POSTS[@]} posts from database (last $LOOKBACK_DAYS days)." >&2
        else
            echo "  Database query returned no results or failed. Falling back to local cache." >&2
        fi
    else
        echo "  psql not found. Cannot query database. Falling back to local cache." >&2
    fi
fi

# --- Priority 2: Local cache file ---
if [ "$DATA_SOURCE" = "none" ]; then
    echo "--- Data source: Local cache file ---" >&2

    if [ -f "$CACHE_FILE" ]; then
        while IFS= read -r encoded_post; do
            [ -z "$encoded_post" ] && continue
            # Posts in the cache are stored as base64 to handle multi-line posts
            DECODED=$(echo "$encoded_post" | base64 -d 2>/dev/null || echo "")
            [ -n "$DECODED" ] && RECENT_POSTS+=("$DECODED")
        done < "$CACHE_FILE"
        DATA_SOURCE="cache"
        echo "  Loaded ${#RECENT_POSTS[@]} posts from $CACHE_FILE" >&2
    else
        echo "  Cache file not found at $CACHE_FILE" >&2
        echo "  No recent post history available. Skipping duplicate check." >&2
        echo "" >&2
        echo "=== DUPLICATE DETECTOR: SKIPPED ===" >&2
        echo "No post history source available. Run with NEON_DATABASE_URL set, or seed the cache file." >&2
        echo "PASSED (no history)"
        exit 0
    fi
fi

# -----------------------------------------------------------------------------
# No posts loaded at all
# -----------------------------------------------------------------------------
if [ ${#RECENT_POSTS[@]} -eq 0 ]; then
    echo "  No recent posts found. Post is unique by default." >&2
    echo "" >&2
    echo "=== DUPLICATE DETECTOR: PASSED ===" >&2
    echo "No post history to compare against." >&2
    echo "PASSED (no history)"
    exit 0
fi

echo "  Comparing against ${#RECENT_POSTS[@]} recent posts..." >&2

# -----------------------------------------------------------------------------
# Compute similarity against each recent post
# -----------------------------------------------------------------------------
HIGHEST_SIMILARITY=0
HIGHEST_INDEX=0
IDX=0

for recent_post in "${RECENT_POSTS[@]}"; do
    IDX=$((IDX + 1))
    SIM=$(similarity_percent "$POST_TEXT" "$recent_post")

    if [ "$SIM" -gt "$HIGHEST_SIMILARITY" ]; then
        HIGHEST_SIMILARITY=$SIM
        HIGHEST_INDEX=$IDX
    fi

    # Early exit if already at maximum overlap — no need to continue
    if [ "$SIM" -ge 100 ]; then
        break
    fi
done

# -----------------------------------------------------------------------------
# Report
# -----------------------------------------------------------------------------
echo "" >&2
echo "--- Similarity results ---" >&2
echo "  Highest overlap: ${HIGHEST_SIMILARITY}% (post #${HIGHEST_INDEX} in history)" >&2
echo "  Block threshold: ${BLOCK_THRESHOLD}%" >&2
echo "  Warn threshold:  ${WARN_THRESHOLD}%" >&2
echo "" >&2

if [ "$HIGHEST_SIMILARITY" -ge "$BLOCK_THRESHOLD" ]; then
    # Show a preview of the matching post
    MATCHING_POST="${RECENT_POSTS[$((HIGHEST_INDEX - 1))]}"
    PREVIEW=$(echo "$MATCHING_POST" | head -c 200 | tr '\n' ' ')

    echo "=== DUPLICATE DETECTOR: BLOCKED ===" >&2
    echo "" >&2
    echo "Post is $HIGHEST_SIMILARITY% similar to a post from the last $LOOKBACK_DAYS days." >&2
    echo "" >&2
    echo "Matching post preview:" >&2
    echo "  \"${PREVIEW}...\"" >&2
    echo "" >&2
    echo "Action required: Significantly rewrite the post, change the angle, or wait until the original post is older than $LOOKBACK_DAYS days before re-using similar content." >&2
    echo "BLOCKED (${HIGHEST_SIMILARITY}% similarity)"
    exit 1

elif [ "$HIGHEST_SIMILARITY" -ge "$WARN_THRESHOLD" ]; then
    MATCHING_POST="${RECENT_POSTS[$((HIGHEST_INDEX - 1))]}"
    PREVIEW=$(echo "$MATCHING_POST" | head -c 150 | tr '\n' ' ')

    echo "=== DUPLICATE DETECTOR: WARNING ===" >&2
    echo "" >&2
    echo "Post is $HIGHEST_SIMILARITY% similar to a post from the last $LOOKBACK_DAYS days (warning threshold: $WARN_THRESHOLD%)." >&2
    echo "" >&2
    echo "Closest match preview:" >&2
    echo "  \"${PREVIEW}...\"" >&2
    echo "" >&2
    echo "The post is not blocked, but consider differentiating the angle, examples, or framing to avoid audience fatigue." >&2
    echo "WARNING (${HIGHEST_SIMILARITY}% similarity)"
    exit 0

else
    echo "=== DUPLICATE DETECTOR: PASSED ===" >&2
    echo "Highest similarity to any recent post: ${HIGHEST_SIMILARITY}%. Content is sufficiently unique." >&2
    echo "PASSED (${HIGHEST_SIMILARITY}% similarity)"
    exit 0
fi
