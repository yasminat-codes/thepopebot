#!/bin/bash
set -euo pipefail

# Plan Architect — Plan Output Validation (v2.0 — folder structure)
# Usage: validate-plan-output.sh <path-to-plan-folder>
# Exit 0 = valid plan, Exit 1 = invalid plan

PLAN_DIR="${1:-}"
ERRORS=0
WARNINGS=0

echo "=== Plan Architect Output Validation ==="

# Argument check
if [ -z "$PLAN_DIR" ]; then
    echo "  [ERROR] No plan folder path provided"
    echo "  Usage: $0 <path-to-plan-folder>"
    exit 1
fi

# Normalize: strip trailing slash
PLAN_DIR="${PLAN_DIR%/}"

# Check 1: Plan folder exists
if [ ! -d "$PLAN_DIR" ]; then
    echo "  [FAIL] Plan folder not found: $PLAN_DIR"
    echo "  Expected a folder like plans/my-feature/, not a .md file"
    exit 1
else
    echo "  [OK] Plan folder exists: $PLAN_DIR"
fi

# Check 2: Required files present
echo ""
echo "  Checking required files..."

check_file() {
    local label="$1"
    local path="$2"
    local required="${3:-yes}"

    if [ -f "$path" ]; then
        local lines
        lines=$(wc -l < "$path")
        if [ "$lines" -lt 10 ]; then
            echo "    [FAIL] $label exists but is only $lines lines — appears to be a stub"
            ERRORS=$((ERRORS + 1))
        else
            echo "    [OK] $label ($lines lines)"
        fi
        echo "$path"  # return path for further checks
    else
        if [ "$required" = "yes" ]; then
            echo "    [FAIL] Missing required file: $label at $path"
            ERRORS=$((ERRORS + 1))
        else
            echo "    [SKIP] Optional file not present: $label"
        fi
        echo ""
    fi
}

PLAN_MD=$(check_file "PLAN.md (index)"          "$PLAN_DIR/PLAN.md"              "yes")
OVERVIEW=$(check_file "01-overview.md"           "$PLAN_DIR/01-overview.md"       "yes")
DB_FILE=$(check_file  "02-database.md"           "$PLAN_DIR/02-database.md"       "no")
IMPL_MD=$(check_file  "03-implementation.md"     "$PLAN_DIR/03-implementation.md" "yes")
RESIL_MD=$(check_file "04-resilience.md"         "$PLAN_DIR/04-resilience.md"     "yes")
TEST_MD=$(check_file  "05-testing.md"            "$PLAN_DIR/05-testing.md"        "yes")
CTX_MD=$(check_file   "06-context.md"            "$PLAN_DIR/06-context.md"        "yes")

# Check 3: Required section content in key files
echo ""
echo "  Checking required sections..."

check_section() {
    local file="$1"
    local label="$2"
    shift 2
    local patterns=("$@")

    if [ -z "$file" ] || [ ! -f "$file" ]; then
        return
    fi

    local found=0
    for pattern in "${patterns[@]}"; do
        if grep -qi "$pattern" "$file" 2>/dev/null; then
            found=1
            break
        fi
    done

    if [ "$found" -eq 1 ]; then
        echo "    [OK] $file: $label"
    else
        echo "    [FAIL] $file missing section: $label (searched: ${patterns[*]})"
        ERRORS=$((ERRORS + 1))
    fi
}

# PLAN.md checks
if [ -n "$PLAN_MD" ] && [ -f "$PLAN_MD" ]; then
    check_section "$PLAN_MD" "Version metadata"     "Version" "version:"
    check_section "$PLAN_MD" "Complexity scores"    "Complexity" "Score"
    check_section "$PLAN_MD" "Pipeline reference"   "pipeline" "extract-tasks" "specs-to-commit"
fi

# Overview checks
if [ -n "$OVERVIEW" ] && [ -f "$OVERVIEW" ]; then
    check_section "$OVERVIEW" "Success Criteria"    "Success Criteria" "Acceptance Criteria"
    check_section "$OVERVIEW" "Architecture diagram" '```' "Component" "Diagram" "Architecture"
    check_section "$OVERVIEW" "Data flow"            "Data Flow" "flow" "Step"
fi

# Implementation checks
if [ -n "$IMPL_MD" ] && [ -f "$IMPL_MD" ]; then
    check_section "$IMPL_MD" "Phase 1 (Foundation)" "Phase 1" "Foundation"
    check_section "$IMPL_MD" "Verify commands"      "Verify:" "verify:" "uv run"
    GATE_COUNT=$(grep -ci "Gate:" "$IMPL_MD" 2>/dev/null || true)
    if [ "$GATE_COUNT" -lt 1 ]; then
        echo "    [FAIL] 03-implementation.md: no Gate: entries found (each phase needs a gate)"
        ERRORS=$((ERRORS + 1))
    else
        echo "    [OK] 03-implementation.md: $GATE_COUNT gate(s) found"
    fi
fi

# Resilience checks
if [ -n "$RESIL_MD" ] && [ -f "$RESIL_MD" ]; then
    check_section "$RESIL_MD" "Error scenarios table"  "Error" "Detection" "Recovery" "Fallback"
    check_section "$RESIL_MD" "Retry policy"           "Retry" "retry" "backoff" "Backoff"
fi

# Testing checks
if [ -n "$TEST_MD" ] && [ -f "$TEST_MD" ]; then
    check_section "$TEST_MD" "Coverage requirements" "coverage" "Coverage" "90%" "85%"
fi

# Context/Grep checks
if [ -n "$CTX_MD" ] && [ -f "$CTX_MD" ]; then
    GREP_COUNT=$(grep -cE '`grep|grep -|```grep|\bgrep\b' "$CTX_MD" 2>/dev/null || true)
    if [ "$GREP_COUNT" -lt 2 ]; then
        GREP_COUNT=$(grep -cE '^\s*[-*]\s+`|```bash' "$CTX_MD" 2>/dev/null || true)
    fi
    if [ "$GREP_COUNT" -lt 2 ]; then
        echo "    [FAIL] 06-context.md: fewer than 2 grep patterns (found: $GREP_COUNT)"
        ERRORS=$((ERRORS + 1))
    else
        echo "    [OK] 06-context.md: $GREP_COUNT+ grep pattern(s)"
    fi
fi

# Check 4: Database file presence/SQL validation
echo ""
echo "  Checking database requirements..."

# Detect if any file mentions CREATE TABLE
HAS_CREATE_TABLE=0
for f in "$PLAN_DIR"/*.md; do
    if grep -qi "CREATE TABLE" "$f" 2>/dev/null; then
        HAS_CREATE_TABLE=1
        break
    fi
done

if [ "$HAS_CREATE_TABLE" -eq 1 ]; then
    if [ -z "$DB_FILE" ] || [ ! -f "$PLAN_DIR/02-database.md" ]; then
        echo "    [FAIL] CREATE TABLE found in plan files but 02-database.md is missing"
        ERRORS=$((ERRORS + 1))
    else
        echo "    [OK] CREATE TABLE present and 02-database.md exists"

        # Check SQL has REFERENCES (no orphan tables)
        CREATE_COUNT=$(grep -ci "CREATE TABLE" "$PLAN_DIR/02-database.md" 2>/dev/null || true)
        REF_COUNT=$(grep -ci "REFERENCES" "$PLAN_DIR/02-database.md" 2>/dev/null || true)

        if [ "$CREATE_COUNT" -gt 0 ] && [ "$REF_COUNT" -eq 0 ]; then
            echo "    [FAIL] 02-database.md has CREATE TABLE but no REFERENCES — potential orphan tables"
            ERRORS=$((ERRORS + 1))
        elif [ "$CREATE_COUNT" -gt 0 ]; then
            echo "    [OK] 02-database.md: $CREATE_COUNT table(s), $REF_COUNT FK reference(s)"
        fi

        # Check Alembic migration stub present
        if grep -q "def upgrade" "$PLAN_DIR/02-database.md" 2>/dev/null; then
            echo "    [OK] 02-database.md: Alembic migration stub present"
        else
            echo "    [WARN] 02-database.md: no Alembic migration stub (def upgrade not found)"
            WARNINGS=$((WARNINGS + 1))
        fi

        # Check indexes for FK columns
        if grep -q "REFERENCES" "$PLAN_DIR/02-database.md" 2>/dev/null; then
            if grep -q "CREATE INDEX" "$PLAN_DIR/02-database.md" 2>/dev/null; then
                echo "    [OK] 02-database.md: indexes present for FK columns"
            else
                echo "    [WARN] 02-database.md: REFERENCES found but no CREATE INDEX — FK indexes may be missing"
                WARNINGS=$((WARNINGS + 1))
            fi
        fi
    fi
else
    echo "    [OK] No database changes detected — 02-database.md not required"
fi

# Check 5: No unfilled placeholders in any file
echo ""
echo "  Checking for unfilled placeholders..."
TOTAL_PLACEHOLDERS=0
for f in "$PLAN_DIR"/*.md; do
    COUNT=$(grep -cE "\[INSERT|TODO|PLACEHOLDER|TBD|FIXME|\[YOUR|<YOUR|\{YOUR|FILL_IN\b" "$f" 2>/dev/null || true)
    if [ "$COUNT" -gt 0 ]; then
        echo "    [FAIL] $f: $COUNT unfilled placeholder(s)"
        grep -nE "\[INSERT|TODO|PLACEHOLDER|TBD|FIXME|\[YOUR|<YOUR|\{YOUR|FILL_IN\b" "$f" | head -5 | sed 's/^/      /'
        TOTAL_PLACEHOLDERS=$((TOTAL_PLACEHOLDERS + COUNT))
    fi
done
# FILL_IN is expected in the migration stub template — don't fail for that
# Only check non-database files for stray FILLs
if [ "$TOTAL_PLACEHOLDERS" -gt 5 ]; then
    echo "    [FAIL] Too many unfilled placeholders across plan files: $TOTAL_PLACEHOLDERS"
    ERRORS=$((ERRORS + 1))
elif [ "$TOTAL_PLACEHOLDERS" -gt 0 ]; then
    echo "    [WARN] $TOTAL_PLACEHOLDERS placeholder(s) remain — verify they are intentional (e.g. migration revision IDs)"
    WARNINGS=$((WARNINGS + 1))
else
    echo "    [OK] No unfilled placeholders"
fi

# Summary
echo ""
echo "  Plan folder: $PLAN_DIR"
echo "  Files checked: $(ls "$PLAN_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')"

if [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo "FAILED: $ERRORS error(s) — fix and rerun before proceeding"
    [ "$WARNINGS" -gt 0 ] && echo "WARNINGS: $WARNINGS warning(s)"
    exit 1
fi

if [ "$WARNINGS" -gt 0 ]; then
    echo ""
    echo "PASSED with $WARNINGS warning(s) — review warnings above"
else
    echo ""
    echo "PASSED — plan folder is complete and well-structured"
fi

exit 0
