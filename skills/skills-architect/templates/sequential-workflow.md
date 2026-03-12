---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
version: {{VERSION}}
author: {{AUTHOR}}
category: {{CATEGORY}}
allowed-tools: {{TOOLS}} Bash Read Write Edit Glob Grep TodoWrite
---

# {{SKILL_NAME}}

{{DESCRIPTION}}

## Overview

This is a strict sequential workflow skill. Each phase produces output that the next phase
depends on. No phase may be skipped. No phase may begin until the preceding phase has passed
its quality gate. This structure is appropriate when ordering matters and partial completion
is worse than no completion.

**Phases:** N (replace with actual count)
**Strict sequencing:** Yes — each phase gates the next
**Rollback:** Phase-level checkpoints enable partial recovery
**Typical runtime:** 30-90 minutes

---

## Workflow Initialization

Before starting any phase:

1. Record the start state (current git status, file checksums, etc.)
2. Initialize the progress tracker
3. Confirm the user understands this is a multi-phase operation

```bash
# Capture baseline state
git status --short 2>/dev/null || echo "Not a git repo"
git log --oneline -1 2>/dev/null || echo "No commits"
date -u +"%Y-%m-%dT%H:%M:%SZ"
```

Initialize todo list:

```
TodoWrite:
- [ ] Phase 1: {name}
- [ ] Phase 2: {name}
- [ ] Phase 3: {name}
- [ ] Phase 4: {name}
- [ ] Phase 5: {name}
- [ ] Final: Verification and completion
```

---

## Phase 1: {Phase Name}

{{PHASES}}

**Purpose:** {What this phase accomplishes and why it must come first}

**Inputs:**
- {Input 1}: {where it comes from}
- {Input 2}: {where it comes from}

**Actions:**

```
Step 1.1: {specific action}
- Tool: {tool to use}
- What to look for: {expected content or pattern}
- What to do with it: {next step}

Step 1.2: {specific action}
- Tool: {tool to use}
- Parameters: {key parameters}
- Success indicator: {what success looks like}

Step 1.3: {specific action}
- Creates/modifies: {file or output}
- Format: {expected format}
```

**Phase 1 Quality Gate:**

| Check | Command/Method | Pass Condition | Fail Action |
|-------|---------------|----------------|-------------|
| {Check 1} | {how to verify} | {condition} | {what to do on fail} |
| {Check 2} | {how to verify} | {condition} | {what to do on fail} |
| {Check 3} | {how to verify} | {condition} | {what to do on fail} |

**Gate result:** All checks must pass. If any check fails:
1. Document exactly which check failed
2. Document the actual vs expected value
3. Attempt one remediation
4. If remediation fails, halt and surface the error to the user

**On pass:** Update todo list, proceed to Phase 2.

---

## Phase 2: {Phase Name}

**Purpose:** {What this phase accomplishes, why it depends on Phase 1}

**Inputs from Phase 1:**
- {What Phase 1 produced that Phase 2 needs}

**Actions:**

```
Step 2.1: {specific action}
Step 2.2: {specific action}
Step 2.3: {specific action}
```

**Phase 2 Quality Gate:**

| Check | Method | Pass Condition | Fail Action |
|-------|--------|----------------|-------------|
| {Check 1} | {how} | {condition} | {action} |
| {Check 2} | {how} | {condition} | {action} |

**On pass:** Update todo list, proceed to Phase 3.

---

## Phase 3: {Phase Name}

**Purpose:** {What this phase accomplishes}

**Inputs from Phase 2:**
- {Dependencies}

**Actions:**

```
Step 3.1: {specific action}
Step 3.2: {specific action}
Step 3.3: {specific action}
Step 3.4: {specific action}
```

**Phase 3 Quality Gate:**

| Check | Method | Pass Condition | Fail Action |
|-------|--------|----------------|-------------|
| {Check 1} | {how} | {condition} | {action} |
| {Check 2} | {how} | {condition} | {action} |
| {Check 3} | {how} | {condition} | {action} |

**On pass:** Update todo list, proceed to Phase 4.

---

## Phase 4: {Phase Name}

**Purpose:** {What this phase accomplishes}

**Inputs from Phase 3:**
- {Dependencies}

**Actions:**

```
Step 4.1: {specific action}
Step 4.2: {specific action}
Step 4.3: {specific action}
```

**Phase 4 Quality Gate:**

{{QUALITY_GATES}}

| Check | Method | Pass Condition | Fail Action |
|-------|--------|----------------|-------------|
| {Check 1} | {how} | {condition} | {action} |
| {Check 2} | {how} | {condition} | {action} |

**On pass:** Update todo list, proceed to Phase 5.

---

## Phase 5: {Phase Name — Usually Integration/Finalization}

**Purpose:** Integrate all phase outputs into the final deliverable.

**Actions:**

```
Step 5.1: Collect all phase outputs
Step 5.2: Verify they are mutually consistent
Step 5.3: Produce the final integrated output
Step 5.4: Run end-to-end validation
```

**Phase 5 Quality Gate (Final):**

```bash
# End-to-end validation
# Replace with actual validation commands for {{SKILL_NAME}}
echo "Running final validation..."
```

| Check | Method | Pass Condition |
|-------|--------|----------------|
| All phases complete | Todo list | All items checked |
| Integration test | {command} | Exit code 0 |
| Output format | {validator} | {condition} |
| No regressions | {comparison} | {condition} |

---

## Checkpoint and Recovery

At the end of each phase, record a checkpoint:

```
CHECKPOINT: Phase N complete
Timestamp: {ISO 8601}
Output files: {list}
Key values: {any values needed to resume from this point}
```

**Recovery procedure:**
If the workflow is interrupted mid-phase, check the last successful checkpoint and resume
from the beginning of the incomplete phase. Never resume from the middle of a phase.

---

## Completion Report

```markdown
# {{SKILL_NAME}} Complete

**Status:** SUCCESS | PARTIAL | FAILED
**Phases completed:** N/N
**Total time:** {duration}

## Phase Summary

| Phase | Status | Time | Notes |
|-------|--------|------|-------|
| Phase 1 | PASS | {Xs} | {note} |
| Phase 2 | PASS | {Xs} | {note} |
| Phase 3 | PASS | {Xs} | {note} |
| Phase 4 | PASS | {Xs} | {note} |
| Phase 5 | PASS | {Xs} | {note} |

## Outputs Produced

{list of files created, modified, or returned}

## Quality Gate Results

{summary of all gate results}

## Next Steps

{What the user should do next}
```

---

## References

{{REFERENCES}}

---

*Tier 4-5 sequential workflow. Each phase gates the next. No skipping. For parallel dispatch
of independent work, see orchestrator template.*
