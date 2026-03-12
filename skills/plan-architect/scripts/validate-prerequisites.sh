#!/bin/bash
set -euo pipefail

# Plan Architect — Prerequisites Validation
# Exit 0 = all checks pass, Exit 1 = failure

PLANS_DIR="plans"
TEMP_DIR=".claude/plan-architect"
ERRORS=0

echo "=== Plan Architect Prerequisites ==="

# Check 1: plans/ directory
if [ ! -d "$PLANS_DIR" ]; then
    echo "  [CREATE] plans/ directory not found — creating..."
    mkdir -p "$PLANS_DIR"
    echo "  [OK] plans/ created"
else
    echo "  [OK] plans/ exists"
fi

# Check 2: temp directory for research outputs
if [ ! -d "$TEMP_DIR" ]; then
    echo "  [CREATE] .claude/plan-architect/ temp directory — creating..."
    mkdir -p "$TEMP_DIR"
    echo "  [OK] .claude/plan-architect/ created"
else
    echo "  [OK] .claude/plan-architect/ exists"
fi

# Check 3: Project has source files
SOURCE_COUNT=$(find . -maxdepth 3 -type f \( -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.go" -o -name "*.rs" -o -name "*.java" -o -name "*.rb" \) -not -path "./.venv/*" -not -path "./node_modules/*" -not -path "./.git/*" 2>/dev/null | head -20 | wc -l)
if [ "$SOURCE_COUNT" -eq 0 ]; then
    echo "  [WARN] No source files found in project (checked .py, .ts, .js, .go, .rs, .java, .rb)"
    echo "         Plan-architect works best with an existing codebase to analyze."
else
    echo "  [OK] Found $SOURCE_COUNT+ source files"
fi

# Check 4: CLAUDE.md exists
if [ -f "CLAUDE.md" ] || [ -f ".claude/CLAUDE.md" ]; then
    echo "  [OK] CLAUDE.md found"
else
    echo "  [WARN] No CLAUDE.md found — plan will have less project context"
fi

# Summary
if [ "$ERRORS" -gt 0 ]; then
    echo ""
    echo "FAILED: $ERRORS prerequisite(s) failed"
    exit 1
fi

echo ""
echo "All prerequisites passed"
exit 0
