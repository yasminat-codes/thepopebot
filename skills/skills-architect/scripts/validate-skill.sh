#!/bin/bash
set -euo pipefail

# validate-skill.sh — Check a skill directory for correctness
#
# Usage: validate-skill.sh <skill-directory-path>
#
# Exit codes:
#   0 = all checks pass (warnings are allowed)
#   1 = one or more FAIL checks found

SKILL_DIR="${1:?Usage: validate-skill.sh <skill-directory-path>}"
SKILL_FILE="$SKILL_DIR/SKILL.md"
ERRORS=0
WARNINGS=0

# ─── Helper functions ───────────────────────────────────────────────────────

pass() { echo "  PASS: $1"; }
warn() { echo "  WARN: $1" >&2; WARNINGS=$((WARNINGS + 1)); }
fail() { echo "  FAIL: $1" >&2; ERRORS=$((ERRORS + 1)); }

# ─── Pre-flight: SKILL.md must exist ────────────────────────────────────────

if [ ! -f "$SKILL_FILE" ]; then
    echo "FAIL: SKILL.md not found at $SKILL_FILE" >&2
    exit 1
fi

echo "Validating: $SKILL_FILE"
echo ""

# ─── Check 1: Line count vs tier limit ──────────────────────────────────────

LINE_COUNT=$(wc -l < "$SKILL_FILE")

# Detect tier from frontmatter
TIER=""
if grep -q "tier:" "$SKILL_FILE" 2>/dev/null; then
    TIER=$(grep "tier:" "$SKILL_FILE" | head -1 | sed 's/.*tier:[[:space:]]*//' | tr -d '"' | tr -d "'" | xargs)
fi

# Set line limit based on tier
case "$TIER" in
    "1"|"starter"|"Starter")       LIMIT=300 ;;
    "2"|"intermediate"|"Intermediate") LIMIT=400 ;;
    "3"|"advanced"|"Advanced")     LIMIT=500 ;;
    "4"|"expert"|"Expert")         LIMIT=600 ;;
    *)
        # No tier detected — warn and apply default limit
        warn "No tier detected in frontmatter. Applying default limit of 500 lines."
        LIMIT=500
        ;;
esac

if [ "$LINE_COUNT" -gt "$LIMIT" ]; then
    fail "Line count $LINE_COUNT exceeds tier limit of $LIMIT (tier: ${TIER:-unknown})"
elif [ "$LINE_COUNT" -gt $((LIMIT - 30)) ]; then
    warn "Line count $LINE_COUNT is close to tier limit of $LIMIT — consider trimming"
    pass "Line count check (within 30 lines of limit)"
else
    pass "Line count $LINE_COUNT is within tier limit of $LIMIT"
fi

# ─── Check 2: Frontmatter exists and is valid ────────────────────────────────

FIRST_LINE=$(head -1 "$SKILL_FILE")
if [ "$FIRST_LINE" != "---" ]; then
    fail "Frontmatter missing — file must start with '---'"
else
    # Check frontmatter closes
    if ! awk '/^---/{count++; if(count==2){found=1; exit}} END{exit !found}' "$SKILL_FILE"; then
        fail "Frontmatter block not closed — missing second '---'"
    else
        # Check required frontmatter fields
        REQUIRED_FIELDS=("name:" "description:" "trigger:" "version:")
        for field in "${REQUIRED_FIELDS[@]}"; do
            if ! grep -q "^$field" "$SKILL_FILE"; then
                fail "Frontmatter missing required field: $field"
            fi
        done
        pass "Frontmatter present with required fields"
    fi
fi

# ─── Check 3: Orphan check — references without directives ──────────────────

# Look for markdown links to files in the skill directory (e.g., [text](./references/FILE.md))
ORPHAN_ERRORS=0

# Find all relative file references in the SKILL.md
while IFS= read -r ref; do
    # Strip markdown link syntax to get just the path
    filepath=$(echo "$ref" | sed 's/.*](\(.*\))/\1/' | sed 's/^[[:space:]]*//')
    # Only check relative paths (starting with ./ or no protocol)
    if [[ "$filepath" != http* ]] && [[ "$filepath" != "#"* ]]; then
        # Resolve relative to skill directory
        resolved="$SKILL_DIR/$filepath"
        # Normalize (remove ./)
        resolved=$(echo "$resolved" | sed 's|/\./|/|g')
        if [ ! -e "$resolved" ]; then
            fail "Orphaned reference: '$filepath' referenced in SKILL.md but file does not exist"
            ORPHAN_ERRORS=$((ORPHAN_ERRORS + 1))
        fi
    fi
done < <(grep -oE '\[.+\]\([^)]+\)' "$SKILL_FILE" 2>/dev/null || true)

if [ "$ORPHAN_ERRORS" -eq 0 ]; then
    pass "No orphaned file references found"
fi

# Check directives reference files that exist (e.g., <!-- include: ./path -->)
while IFS= read -r directive_path; do
    resolved="$SKILL_DIR/$directive_path"
    resolved=$(echo "$resolved" | sed 's|/\./|/|g')
    if [ ! -e "$resolved" ]; then
        fail "Orphaned directive: '$directive_path' referenced in directive but file does not exist"
    fi
done < <(grep -oE 'include:[[:space:]]*[^[:space:]>]+' "$SKILL_FILE" 2>/dev/null | sed 's/include:[[:space:]]*//' || true)

# ─── Check 4: CSO keywords present ──────────────────────────────────────────

# Skills must contain trigger language that activates them proactively
CSO_FOUND=0

if grep -qi "PROACTIVELY" "$SKILL_FILE" 2>/dev/null; then
    CSO_FOUND=$((CSO_FOUND + 1))
fi

if grep -qi "trigger" "$SKILL_FILE" 2>/dev/null; then
    CSO_FOUND=$((CSO_FOUND + 1))
fi

if grep -qi "when to use\|use when\|invoke when\|activate when" "$SKILL_FILE" 2>/dev/null; then
    CSO_FOUND=$((CSO_FOUND + 1))
fi

if [ "$CSO_FOUND" -ge 2 ]; then
    pass "CSO trigger keywords present (PROACTIVELY + trigger context)"
elif [ "$CSO_FOUND" -eq 1 ]; then
    warn "Only partial CSO trigger language found — add both 'PROACTIVELY' and 'when to use' context"
else
    fail "No CSO trigger keywords found — skill will not activate. Add 'PROACTIVELY', trigger phrases, and 'when to use' section"
fi

# ─── Check 5: version field has valid format ─────────────────────────────────

if grep -q "^version:" "$SKILL_FILE"; then
    VERSION=$(grep "^version:" "$SKILL_FILE" | head -1 | sed 's/version:[[:space:]]*//' | tr -d '"' | xargs)
    if echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
        pass "Version format valid: $VERSION"
    else
        warn "Version '$VERSION' does not follow semver (x.y.z) — consider updating"
    fi
else
    warn "No version field in frontmatter — add 'version: 1.0.0'"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo "Validation Results:"
echo "  File:     $SKILL_FILE"
echo "  Lines:    $LINE_COUNT (limit: ${LIMIT})"
echo "  Tier:     ${TIER:-not detected}"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"

if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
    echo ""
    echo "  All checks passed."
elif [ "$ERRORS" -eq 0 ]; then
    echo ""
    echo "  Passed with $WARNINGS warning(s)."
else
    echo ""
    echo "  $ERRORS error(s) must be fixed before this skill is considered valid." >&2
fi

[ "$ERRORS" -eq 0 ] && exit 0 || exit 1
