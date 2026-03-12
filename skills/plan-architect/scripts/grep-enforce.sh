#!/bin/bash
set -euo pipefail

# Plan Architect — Grep Enforcement
# Verifies that codebase grep was actually performed during the research phase.
# Exit 0 = grep evidence found, Exit 1 = grep was NOT used (warning)

RESEARCH_FILE=".claude/plan-architect/codebase-research.md"
MIN_FILE_REFS=3
ERRORS=0

echo "=== Plan Architect Grep Enforcement ==="

# Check 1: Research output file exists
if [ ! -f "$RESEARCH_FILE" ]; then
    echo "  [FAIL] Codebase research file not found: $RESEARCH_FILE"
    echo "         This file should be written by the Parallel Research phase."
    echo "         Ensure Phase 3 (Parallel Research) ran codebase grep before completing."
    exit 1
fi

FILE_SIZE=$(wc -c < "$RESEARCH_FILE")
if [ "$FILE_SIZE" -eq 0 ]; then
    echo "  [FAIL] Codebase research file is empty: $RESEARCH_FILE"
    echo "         Phase 3 must populate this file with actual grep findings."
    exit 1
fi

echo "  [OK] Research file found ($FILE_SIZE bytes)"

# Check 2: File contains evidence of grep usage
# Look for file paths (e.g., src/foo.py, app/bar.ts), line numbers (line 42:), or code snippets
echo ""
echo "  Checking for grep evidence..."

EVIDENCE_COUNT=0

# Pattern A: Unix-style file paths with extensions
FILE_PATH_COUNT=$(grep -cE '(src|app|lib|tests?|pkg|cmd|internal|api|services?|agents?|workers?|routes?|models?|schemas?|utils?|helpers?|handlers?|controllers?|components?)/[a-zA-Z0-9_/-]+\.(py|ts|js|go|rs|java|rb|tsx|jsx)' "$RESEARCH_FILE" 2>/dev/null || true)
if [ "$FILE_PATH_COUNT" -gt 0 ]; then
    echo "    [OK] Found $FILE_PATH_COUNT file path reference(s) (src/app/lib patterns)"
    EVIDENCE_COUNT=$((EVIDENCE_COUNT + FILE_PATH_COUNT))
fi

# Pattern B: Line number references (e.g., "line 42", ":42:", "L42")
LINE_NUM_COUNT=$(grep -cE '(line [0-9]+|:[0-9]+:|L[0-9]+\b|#L[0-9]+)' "$RESEARCH_FILE" 2>/dev/null || true)
if [ "$LINE_NUM_COUNT" -gt 0 ]; then
    echo "    [OK] Found $LINE_NUM_COUNT line number reference(s)"
    EVIDENCE_COUNT=$((EVIDENCE_COUNT + LINE_NUM_COUNT))
fi

# Pattern C: Code block fences (indicating actual code snippets were captured)
CODE_BLOCK_COUNT=$(grep -cE '^\s*```' "$RESEARCH_FILE" 2>/dev/null || true)
# Divide by 2 since blocks come in pairs
CODE_SNIPPET_COUNT=$((CODE_BLOCK_COUNT / 2))
if [ "$CODE_SNIPPET_COUNT" -gt 0 ]; then
    echo "    [OK] Found $CODE_SNIPPET_COUNT code snippet(s) captured"
    EVIDENCE_COUNT=$((EVIDENCE_COUNT + CODE_SNIPPET_COUNT))
fi

# Pattern D: Grep command output style (filename:linenum:content)
GREP_OUTPUT_COUNT=$(grep -cE '^[a-zA-Z0-9_./-]+\.[a-z]+:[0-9]+:' "$RESEARCH_FILE" 2>/dev/null || true)
if [ "$GREP_OUTPUT_COUNT" -gt 0 ]; then
    echo "    [OK] Found $GREP_OUTPUT_COUNT grep-style output line(s) (file:line:content)"
    EVIDENCE_COUNT=$((EVIDENCE_COUNT + GREP_OUTPUT_COUNT))
fi

# Pattern E: Explicit mentions of grep/search being performed
GREP_MENTION_COUNT=$(grep -ciE '\bgrep\b|\bripgrep\b|\brg\b|\bsearched?\b|\bscanned?\b|\bfound in\b|\boccurs? in\b' "$RESEARCH_FILE" 2>/dev/null || true)
if [ "$GREP_MENTION_COUNT" -gt 0 ]; then
    echo "    [OK] Found $GREP_MENTION_COUNT grep/search mention(s)"
    EVIDENCE_COUNT=$((EVIDENCE_COUNT + GREP_MENTION_COUNT))
fi

echo ""
echo "  Total grep evidence signals: $EVIDENCE_COUNT"

if [ "$EVIDENCE_COUNT" -eq 0 ]; then
    echo "  [FAIL] No evidence of codebase grep found in research output"
    echo "         The research file appears to contain no actual codebase findings."
    echo "         Phase 3 must use grep/search tools on the actual codebase."
    ERRORS=$((ERRORS + 1))
fi

# Check 3: At least MIN_FILE_REFS distinct codebase file references
echo ""
echo "  Counting distinct codebase file references..."

# Extract all file-path-like strings (any/path/file.ext pattern)
DISTINCT_FILES=$(grep -oE '[a-zA-Z0-9_./%-]+(src|app|lib|tests?|pkg|cmd|api|services?|agents?|workers?|routes?|models?|schemas?|utils?|helpers?|handlers?|controllers?|components?)[a-zA-Z0-9_/.-]*\.(py|ts|js|go|rs|java|rb|tsx|jsx|yaml|yml|toml|cfg|ini|json)' "$RESEARCH_FILE" 2>/dev/null | sort -u | wc -l || true)

# Fallback: count any *.ext references
if [ "$DISTINCT_FILES" -eq 0 ]; then
    DISTINCT_FILES=$(grep -oE '[a-zA-Z0-9_/-]+\.(py|ts|js|go|rs|java|rb|tsx|jsx|yaml|yml|toml)' "$RESEARCH_FILE" 2>/dev/null | sort -u | wc -l || true)
fi

if [ "$DISTINCT_FILES" -lt "$MIN_FILE_REFS" ]; then
    echo "  [FAIL] Only $DISTINCT_FILES distinct codebase file reference(s) found (minimum: $MIN_FILE_REFS)"
    echo "         Plan-architect requires at least $MIN_FILE_REFS file references to confirm"
    echo "         that actual codebase patterns were searched, not just invented."
    ERRORS=$((ERRORS + 1))
else
    echo "  [OK] Found $DISTINCT_FILES distinct file reference(s) (minimum: $MIN_FILE_REFS)"
fi

# Summary
echo ""
if [ "$ERRORS" -gt 0 ]; then
    echo "GREP ENFORCEMENT FAILED: $ERRORS check(s) failed"
    echo ""
    echo "Required actions:"
    echo "  1. Re-run Phase 3 (Parallel Research) with actual grep/search tool calls"
    echo "  2. Write findings to: $RESEARCH_FILE"
    echo "  3. Include at least $MIN_FILE_REFS real file paths from this codebase"
    exit 1
fi

echo "GREP ENFORCEMENT PASSED — codebase was actually searched before planning"
exit 0
