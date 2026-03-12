---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
version: {{VERSION}}
author: {{AUTHOR}}
category: {{CATEGORY}}
allowed-tools: {{TOOLS}} Bash
---

# {{SKILL_NAME}}

{{DESCRIPTION}}

## Overview

This skill relies heavily on shell commands, CLI tools, and scripts to accomplish its goal.
All scripts live in `scripts/` and are invoked via Bash. Results are parsed and presented
in a structured report.

**Tools used:** {{TOOLS}} Bash

**Typical runtime:** 1-5 minutes depending on target size

**Prerequisites:**
- Required CLIs must be installed (see Prerequisites section)
- Appropriate permissions on the target directory/system
- Network access (if remote targets are involved)

---

## Prerequisites Check

Run this first to confirm the environment is ready:

```bash
# Check required tools
command -v git >/dev/null 2>&1 && echo "git: OK" || echo "git: MISSING"
command -v curl >/dev/null 2>&1 && echo "curl: OK" || echo "curl: MISSING"
# Add checks for any additional tools {{SKILL_NAME}} requires
```

If any tool is missing, surface a clear installation instruction before proceeding.

---

## Phase 1: Environment Discovery

{{PHASES}}

Detect and validate the target environment before running any scripts.

```bash
# Discover working directory
pwd

# Check target exists
ls -la /path/to/target 2>/dev/null || echo "Target not found"

# Detect OS and shell
uname -s
echo $SHELL
```

Parse the output to determine:
- Operating system (Linux / macOS / Windows WSL)
- Shell version and compatibility
- Presence of required dependencies
- Current user permissions

**Decision point:** If environment is unsupported, explain why and stop. Do not proceed
with partial support.

---

## Phase 2: Configuration Loading

Load configuration from the closest `.{{SKILL_NAME}}rc` or fall back to defaults.

```bash
# Look for config file in standard locations
CONFIG_LOCATIONS=(
    "./.{{SKILL_NAME}}rc"
    "$HOME/.{{SKILL_NAME}}rc"
    "/etc/{{SKILL_NAME}}/config"
)

for loc in "${CONFIG_LOCATIONS[@]}"; do
    if [ -f "$loc" ]; then
        echo "Using config: $loc"
        source "$loc"
        break
    fi
done
```

**Default configuration values:**

| Key | Default | Description |
|-----|---------|-------------|
| `TARGET_DIR` | `.` | Directory to process |
| `OUTPUT_FORMAT` | `markdown` | Report format |
| `VERBOSE` | `false` | Enable verbose output |
| `DRY_RUN` | `false` | Preview without making changes |
| `MAX_DEPTH` | `5` | Maximum directory recursion depth |

---

## Phase 3: Core Script Execution

{{SCRIPTS}}

### Primary Script

The main operation is defined in `scripts/run.sh`:

```bash
#!/usr/bin/env bash
# scripts/run.sh — Primary {{SKILL_NAME}} operation
set -euo pipefail

TARGET_DIR="${1:-.}"
OUTPUT_FORMAT="${2:-markdown}"
VERBOSE="${3:-false}"

echo "[{{SKILL_NAME}}] Starting on: $TARGET_DIR"

# --- Main logic here ---
# Replace with actual implementation for {{SKILL_NAME}}

RESULT=0
ERROR_COUNT=0

process_item() {
    local item="$1"
    echo "Processing: $item"
    # item-level logic
}

# Walk target directory
find "$TARGET_DIR" -maxdepth 5 -type f | while read -r file; do
    process_item "$file" || ((ERROR_COUNT++)) || true
done

echo "[{{SKILL_NAME}}] Complete. Errors: $ERROR_COUNT"
exit $RESULT
```

### Utility Scripts

```bash
# scripts/check-prereqs.sh — Validate environment
#!/usr/bin/env bash
set -euo pipefail

REQUIRED_TOOLS=("git" "curl" "jq")
MISSING=()

for tool in "${REQUIRED_TOOLS[@]}"; do
    command -v "$tool" >/dev/null 2>&1 || MISSING+=("$tool")
done

if [ ${#MISSING[@]} -gt 0 ]; then
    echo "MISSING: ${MISSING[*]}"
    exit 1
fi

echo "All prerequisites satisfied."
```

```bash
# scripts/format-output.sh — Format raw results into report
#!/usr/bin/env bash
set -euo pipefail

INPUT_FILE="$1"
FORMAT="${2:-markdown}"

case "$FORMAT" in
    markdown)
        echo "## {{SKILL_NAME}} Report"
        echo ""
        cat "$INPUT_FILE"
        ;;
    json)
        jq -n --rawfile content "$INPUT_FILE" '{"result": $content}'
        ;;
    plain)
        cat "$INPUT_FILE"
        ;;
    *)
        echo "Unknown format: $FORMAT" >&2
        exit 1
        ;;
esac
```

---

## Phase 4: Output Parsing

Capture and parse script output into structured results.

```bash
# Capture output with error handling
OUTPUT=$(bash scripts/run.sh "$TARGET" "$FORMAT" "$VERBOSE" 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "Script failed with exit code: $EXIT_CODE"
    echo "Output: $OUTPUT"
    # Surface actionable error
fi
```

Parse key metrics from output:
- Total items processed
- Success / failure counts
- Any warnings or notices
- Time elapsed

---

## Phase 5: Report Generation

{{QUALITY_GATES}}

Structure the final report:

```markdown
# {{SKILL_NAME}} Report

**Target:** {target}
**Timestamp:** {timestamp}
**Duration:** {duration}s

## Summary

| Metric | Value |
|--------|-------|
| Items Processed | N |
| Passed | N |
| Failed | N |
| Warnings | N |

## Details

{per-item results}

## Recommendations

{actionable next steps based on results}
```

---

## Error Handling Reference

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | Success | Present report |
| 1 | General error | Show error and stop |
| 2 | Missing prerequisite | Guide installation |
| 3 | Permission denied | Explain permission needed |
| 127 | Command not found | Identify missing CLI |

---

## Security Considerations

- Never run scripts as root unless explicitly required
- Validate all user-supplied paths before using in shell expansions
- Use `set -euo pipefail` in all scripts
- Quote all variables: `"$VAR"` not `$VAR`
- Avoid `eval` and dynamic command construction from user input

---

## Script Directory Layout

```
.claude/skills/{{SKILL_NAME}}/
├── SKILL.md                    # This file
└── scripts/
    ├── run.sh                  # Primary operation
    ├── check-prereqs.sh        # Environment validation
    ├── format-output.sh        # Output formatting
    └── lib/
        ├── common.sh           # Shared functions
        └── logging.sh          # Logging helpers
```

---

## References

{{REFERENCES}}

---

*Tier 3 skill — heavy bash/CLI usage. Scripts live in `scripts/`. For pure logic without
shell, see mid-tool template. For parallel multi-tool research, see advanced-multi-tool template.*
