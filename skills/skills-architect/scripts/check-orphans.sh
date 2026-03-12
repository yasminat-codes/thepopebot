#!/bin/bash
set -euo pipefail

# check-orphans.sh — Check for orphaned references in a skill directory
#
# Orphan type A: A file in the skill directory that is not referenced anywhere in SKILL.md
# Orphan type B: A reference in SKILL.md that points to a file that does not exist
#
# Usage: check-orphans.sh <skill-directory-path>
#
# Exit codes:
#   0 = no orphans found
#   1 = orphans detected (details on stdout)

SKILL_DIR="${1:?Usage: check-orphans.sh <skill-directory-path>}"
SKILL_FILE="$SKILL_DIR/SKILL.md"
ORPHANS=0

if [ ! -f "$SKILL_FILE" ]; then
    echo "ERROR: SKILL.md not found at $SKILL_FILE" >&2
    exit 1
fi

echo "Checking orphans in: $SKILL_DIR"
echo ""

# ─── Type A: Files on disk not referenced in SKILL.md ───────────────────────

echo "Type A — Files not referenced in SKILL.md:"
FOUND_A=0

while IFS= read -r -d '' candidate; do
    # Skip SKILL.md itself and hidden files
    basename_file=$(basename "$candidate")
    [[ "$basename_file" == "SKILL.md" ]] && continue
    [[ "$basename_file" == .* ]] && continue

    # Build relative path from skill dir for the grep pattern
    rel_path="${candidate#$SKILL_DIR/}"

    # Check if any form of this path appears in SKILL.md
    if ! grep -qF "$rel_path" "$SKILL_FILE" 2>/dev/null && \
       ! grep -qF "$basename_file" "$SKILL_FILE" 2>/dev/null; then
        echo "  ORPHAN: $rel_path (exists on disk, not referenced in SKILL.md)"
        ORPHANS=$((ORPHANS + 1))
        FOUND_A=$((FOUND_A + 1))
    fi
done < <(find "$SKILL_DIR" -type f -not -name "SKILL.md" -print0 2>/dev/null)

[ "$FOUND_A" -eq 0 ] && echo "  none"

echo ""

# ─── Type B: References in SKILL.md pointing to non-existent files ──────────

echo "Type B — References in SKILL.md with no matching file:"
FOUND_B=0

# Extract markdown links: [text](path)
while IFS= read -r ref; do
    path=$(echo "$ref" | sed 's/.*](\(.*\))/\1/')
    # Skip external URLs and anchor links
    [[ "$path" == http* ]] && continue
    [[ "$path" == "#"* ]] && continue
    [[ -z "$path" ]] && continue

    # Resolve relative path from skill dir
    resolved="$SKILL_DIR/$path"
    # Normalize double slashes and ./
    resolved=$(echo "$resolved" | sed 's|/\./|/|g' | sed 's|//|/|g')

    if [ ! -e "$resolved" ]; then
        echo "  ORPHAN: $path (referenced in SKILL.md, file not found)"
        ORPHANS=$((ORPHANS + 1))
        FOUND_B=$((FOUND_B + 1))
    fi
done < <(grep -oE '\[[^]]*\]\([^)]+\)' "$SKILL_FILE" 2>/dev/null || true)

[ "$FOUND_B" -eq 0 ] && echo "  none"

echo ""

# ─── Summary ─────────────────────────────────────────────────────────────────

echo "Total orphans found: $ORPHANS"
[ "$ORPHANS" -eq 0 ] && exit 0 || exit 1
