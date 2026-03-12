# task-master — Usage Guide
Version: 1.0.0 | Last updated: 2026-03-02

---

## Quick Start

```bash
# Step 1: Generate a plan (if you haven't already)
/plan-architect build a rate limiter service

# Step 2: Convert the plan into task files
/task-master

# Step 3: Implement from the generated tasks
/specs-to-commit
```

That's the full pipeline. task-master is Step 2 of 3.

---

## Invocation Options

```
/task-master [path/to/plan]
```

The `argument-hint` is: `path/to/plan (optional, defaults to interactive selection)`

| Invocation | Behavior |
|------------|----------|
| `/task-master` | Searches `plan/` and `plans/` for plan files. If 1 found, auto-selects. If 2+, prompts you to choose. |
| `/task-master plan/my-feature.md` | Uses the specified plan file directly. Skips selection step. |
| `/task-master plans/niche-scout/PLAN.md` | Uses the plan-architect folder output. Reads PLAN.md as the index. |

**If no plan is found:** task-master halts immediately with the message:
`No plans found. Run /plan-architect first.`

---

## What Happens in Each Phase

| Phase | What It Does | You Need To |
|-------|-------------|-------------|
| 0: Initialize | Loads memory preferences, reads .env keys, discovers plan files | Nothing — automatic |
| 1: Interview | Asks clarifying questions about ambiguous sections or missing .env keys | Answer 0-3 questions |
| 2: Research | Dispatches codebase-scanner and grep-mcp-researcher agents in parallel | Nothing — wait ~30s |
| 3: Analysis | Parses the plan, builds dependency graph, shows you a preview table | Approve or modify the task list |
| 4: Generation | Writes each task file in dependency order, validates each one | Answer occasional questions if ambiguous |
| 5: Finalization | Runs validate-tasks.sh, writes TASK-LOG.md, shows delivery report | Review the delivery report |

Total time: 2-5 minutes for a typical 10-task plan.

---

## Output Locations

| Output | Location | Notes |
|--------|----------|-------|
| Task files | `tasks/_pending/NNN-kebab-title.md` | Ready for implementation |
| Task log | `tasks/TASK-LOG.md` | Registry of all generated tasks |
| Memory preferences | `.claude/memory/task-master.md` | Auto-updated when you give feedback |
| Circuit breaker state | `.claude/circuit-breakers/grep-mcp.json` | Auto-managed |

**Task file naming:**
- Format: `001-rate-limiter-service.md`, `002-rate-limiter-tests.md`
- Sub-tasks (from large plan splits): `005a-oauth-client.md`, `005b-oauth-token-cache.md`
- Numbers start at 001 and are zero-padded to 3 digits

---

## Pipeline Context

```
/plan-architect  →  /task-master  →  /specs-to-commit
    (Step 1)            (Step 2)          (Step 3)
    Creates plans/      Creates tasks/    Implements tasks
    NNN-*.md files      _pending/*.md     one at a time
```

**Input:** One or more `.md` plan files in `plan/` or `plans/`
**Output:** Numbered, dependency-ordered task files in `tasks/_pending/`
**Consumed by:** `/specs-to-commit`, which reads `BlockedBy` fields to determine implementation order

---

## Common Workflows

| Goal | Command |
|------|---------|
| Generate tasks from latest plan | `/task-master` |
| Generate from a specific plan file | `/task-master plans/niche-scout/PLAN.md` |
| Re-run after plan update | `/task-master` (will ask about overwriting existing tasks) |
| Validate existing tasks without regenerating | `bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending/` |
| Reset circuit breaker (GREP MCP) | `rm .claude/circuit-breakers/grep-mcp.json` |
| Check saved preferences | `cat .claude/memory/task-master.md` |
| Clear saved preferences (start fresh) | `rm .claude/memory/task-master.md` |

---

## Giving Feedback

task-master saves preferences between runs. After the delivery report, you can say:

- **"Too detailed"** — Next run: fewer checklist items (task_depth=lean)
- **"Too vague"** — Next run: more checklist items with verifiable commands (task_depth=thorough)
- **"Too many tasks"** — Note is saved; you'll be prompted before the next large plan
- **"Split this task"** — Immediately splits the current task into sub-tasks (NNNa, NNNb)

These corrections persist in `.claude/memory/task-master.md` and are applied automatically
on the next invocation.

---

## Preview Table

Before writing any files, task-master shows you a preview table:

```
| # | Task Title | Est. Lines | Depends On | Has Live API Test? |
|---|-----------|-----------|-----------|-------------------|
| 001 | Rate Limiter Models | ~60 | — | No |
| 002 | Rate Limiter Service | ~90 | 001 | Yes (REDIS_URL) |
| 003 | Rate Limiter Tests | ~80 | 002 | Yes (REDIS_URL) |
```

Options presented: **Proceed** / **Modify task list** / **Cancel**

No files are written until you approve. If you choose "Modify task list", task-master
will ask what to change (remove tasks, merge tasks, add tasks) before re-showing the table.
