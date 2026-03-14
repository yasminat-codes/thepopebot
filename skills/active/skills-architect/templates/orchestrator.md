---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
version: {{VERSION}}
author: {{AUTHOR}}
category: {{CATEGORY}}
allowed-tools: {{TOOLS}} Task TodoWrite Bash Read Glob Grep
context: fork
model: claude-opus-4-5
---

# {{SKILL_NAME}}

{{DESCRIPTION}}

## Overview

This is a Tier 6 orchestrator skill. It does not do the work itself — it plans, dispatches,
monitors, and gates other skills and agents. All heavy lifting is delegated to specialized
sub-skills via Task tool dispatch or sequential skill invocations.

**Model:** claude-opus-4-5 (orchestration requires strong reasoning)
**Context:** Forked (orchestration state isolated from main conversation)
**Tools:** Task (parallel dispatch), TodoWrite (progress tracking), read-only filesystem tools
**Typical runtime:** 15-45 minutes

---

## Orchestration Principles

1. **Delegate, never duplicate** — If a skill exists for a sub-task, use it. Do not reimplement.
2. **Gate aggressively** — Each phase must meet quality criteria before the next begins.
3. **Parallelize safely** — Run independent tasks in parallel. Serialize dependent tasks.
4. **Fail loudly** — A failed phase surfaces immediately. Never silently skip a phase.
5. **Approval before irreversible actions** — Ask the user before modifying production systems.

---

## Pre-Flight Checklist

Before dispatching any sub-tasks, verify the environment is ready:

```
[ ] Required skills are available (list them explicitly)
[ ] Target directory / repository exists and is accessible
[ ] Required permissions granted (git write, file write, etc.)
[ ] No in-progress work that would conflict
[ ] User has approved the plan (for destructive operations)
```

If any pre-flight check fails, halt and explain what is needed. Do not proceed partially.

---

## Progress Tracking

Initialize the todo list at the start. Update after each phase completes or fails.

```
TodoWrite:
- [ ] Phase 1: {name} — {description}
- [ ] Phase 2: {name} — {description}
- [ ] Phase 3: {name} — {description}
- [ ] Phase 4: {name} — {description}
- [ ] Phase 5: {name} — {description}
- [ ] Quality Gate: Final validation
- [ ] Completion: Report and handoff
```

Mark items complete as they finish. Mark failed items as `[BLOCKED]` with the reason.

---

## Phase 1: Discovery and Planning

{{PHASES}}

Before dispatching any work, build a complete picture of what needs to happen.

**Discovery tasks (run in parallel):**

```
Task 1: Codebase scan
- Use Glob/Grep/Read to map the existing state
- Identify what already exists vs what needs to be created
- Note any conflicts or blockers

Task 2: Dependency check
- Identify which sub-skills are needed
- Verify each required skill exists
- Identify any missing prerequisites

Task 3: Impact analysis
- Identify files that will be modified or created
- Flag any operations that are irreversible
- Estimate total scope (small / medium / large)
```

**Gate:** All three discovery tasks must complete before Phase 2 begins.
**Output:** A written plan that the user can review before execution begins.

---

## Phase 2: User Approval Gate

**REQUIRED for destructive or large-scope operations.**

Present the plan to the user:

```markdown
## {{SKILL_NAME}} Execution Plan

**Scope:** {N files to modify, N files to create}
**Estimated time:** {X-Y minutes}
**Irreversible operations:** {list them or "none"}

### What will happen:
1. Phase 1: {brief description}
2. Phase 2: {brief description}
3. Phase 3: {brief description}

### What will NOT happen:
- {important limitation 1}
- {important limitation 2}

**Proceed?** (yes/no — or modify the plan above)
```

**Gate:** User must explicitly confirm before Phase 3 begins.
Do not infer consent from context. Ask directly.

---

## Phase 3: Parallel Dispatch

Dispatch all independent work simultaneously using the Task tool.

### Dispatch Group A (independent tasks, run in parallel)

```
Task A1: {Skill: skill-name-1}
Prompt: {exact prompt to pass to the skill}
Expected output: {what a successful result looks like}

Task A2: {Skill: skill-name-2}
Prompt: {exact prompt to pass to the skill}
Expected output: {what a successful result looks like}

Task A3: {Skill: skill-name-3}
Prompt: {exact prompt to pass to the skill}
Expected output: {what a successful result looks like}
```

Wait for all Group A tasks to complete before proceeding to Group B.

### Dispatch Group B (depends on Group A outputs)

```
Task B1: {Skill: skill-name-4}
Prompt: {prompt incorporating outputs from A1 and A2}
Expected output: {what a successful result looks like}

Task B2: {Skill: skill-name-5}
Prompt: {prompt incorporating output from A3}
Expected output: {what a successful result looks like}
```

### Dispatch Group C (final integration, depends on Group B)

```
Task C1: {Skill: skill-name-6}
Prompt: {integration prompt using all prior outputs}
Expected output: {final integrated result}
```

---

## Phase 4: Quality Gates

{{QUALITY_GATES}}

Run all quality gates after Phase 3 completes. Gates are non-negotiable.

### Gate 1: Completeness

```bash
# Verify all expected outputs exist
```

| Expected Output | Check Command | Pass Condition |
|----------------|---------------|----------------|
| {output 1} | {command} | {condition} |
| {output 2} | {command} | {condition} |
| {output 3} | {command} | {condition} |

**Failure action:** Identify which sub-task failed, re-run that task only, re-check.

### Gate 2: Correctness

```bash
# Run tests / validators on the produced outputs
```

**Required passing rate:** 100% of critical checks, >90% of non-critical checks.

**Failure action:** Surface exact failures. Do not proceed to Phase 5 until resolved.

### Gate 3: Integration

Verify that outputs from different tasks work together correctly:

```bash
# Integration verification commands
```

**Failure action:** Flag integration issues specifically. These are often harder to fix
than individual task failures.

---

## Phase 5: Final Review and Handoff

Present a comprehensive completion report:

```markdown
# {{SKILL_NAME}} Complete

**Status:** SUCCESS / PARTIAL / FAILED
**Duration:** {actual time}
**Tasks completed:** {N}/{total}

## What Was Done

### Phase 1 — Discovery
{summary of findings}

### Phase 2 — {work description}
{summary of changes}

### Phase 3 — {work description}
{summary of changes}

## Quality Gate Results

| Gate | Status | Notes |
|------|--------|-------|
| Completeness | PASS | All N outputs present |
| Correctness | PASS | All checks passing |
| Integration | PASS | End-to-end verified |

## Files Modified

{list of files created or modified with one-line description each}

## Files Created

{list of new files}

## Next Steps

{What the user should do next — be specific}

## Known Limitations

{Anything not covered, edge cases not handled, follow-up work suggested}
```

---

## Error Recovery Playbook

| Failure Scenario | Detection | Recovery |
|------------------|-----------|----------|
| Sub-skill timeout | Task returns no output after 10 min | Re-run with simplified scope |
| Sub-skill error | Task returns error message | Fix input, re-run that task only |
| Gate failure | Gate check returns failures | Do not proceed, surface failures |
| Partial completion | Some tasks succeed, some fail | Report what completed, what remains |
| User cancels mid-run | Interrupt signal | Report state, list what was partially done |

---

## References

{{REFERENCES}}

---

## Sub-Skill Registry

Document all skills this orchestrator can dispatch:

| Skill Name | Purpose | Input | Output |
|-----------|---------|-------|--------|
| {skill-1} | {what it does} | {what to pass} | {what it returns} |
| {skill-2} | {what it does} | {what to pass} | {what it returns} |
| {skill-3} | {what it does} | {what to pass} | {what it returns} |

---

*Tier 6 orchestrator skill — delegates to sub-skills via Task tool. For a single sequential
workflow, see sequential-workflow template. For a single skill with phases, see advanced-multi-tool.*
