# task-master

Converts implementation plans into atomic, dependency-ordered task files.
**Tier:** 6 (Ultra-Advanced) | **Pipeline position:** Step 2 of 3

---

## Pipeline

```
plan-architect  →  task-master  →  specs-to-commit
   (Step 1)          (Step 2)         (Step 3)
   Creates plans/     Creates tasks/   Implements each
   *.md files        _pending/*.md    task in order
```

---

## Quick Start

```bash
# Step 1: Write or generate a plan
/plan-architect add a new reference file to my email-parser skill

# Step 2: Convert plan to tasks
/task-master

# Step 3: Implement (optional — can do manually)
/specs-to-commit
```

Or with an explicit plan path:

```bash
/task-master plans/email-parser/PLAN.md
```

---

## What It Generates

Task files in `tasks/_pending/NNN-title.md` with:

- `001`, `002`, `003` zero-padded dependency ordering
- **Files to Read** — explicit paths to load context before starting
- **Success Criteria** — 5 measurable, runnable verification commands
- **Full Testing section** — skill validation checks + manual invocation test + live API stub (if applicable)
- **mv commands** — ready-to-run task lifecycle management
- **BlockedBy** — dependency chain for specs-to-commit pipeline consumption
- **validate-tasks.sh gate** — `bash scripts/validate-tasks.sh` exits 0 on every task

---

## Quality Enforcement

| Mechanism | What It Checks | When It Runs |
|-----------|---------------|--------------|
| `hooks/post-tool.sh` | Each task file has all 10 required sections | After every Write call in Phase 4 |
| `scripts/validate-tasks.sh` | Dependency references valid, no orphan BlockedBy | Phase 5, before delivery report |
| Phase 3 preview gate | User approves task list before any files written | Phase 3 (AskUserQuestion) |
| Memory system | Saved depth preferences applied on next run | Phase 0 startup |
| Circuit breaker | GREP MCP failure tracking with local fallback | Phase 2 (checked before dispatch) |

---

## Reference Files

| File | Purpose | Lines |
|------|---------|-------|
| `references/TASK-TEMPLATE.md` | Non-negotiable task file format with all 10 sections | ~316 |
| `references/PLAN-ANALYSIS.md` | How to parse plan files, skip non-implementation sections | ~100 |
| `references/DEPENDENCY-ENGINE.md` | Topological sort algorithm, BlockedBy chain building | ~120 |
| `references/TESTING-STANDARDS.md` | Full testing section requirements, live API test logic | ~130 |
| `references/CONTEXT-INJECTION.md` | How to add codebase file paths to task files | ~90 |
| `references/PIPELINE-CONTRACT.md` | Input/output contracts with plan-architect and specs-to-commit | ~110 |
| `references/EDGE-CASES.md` | Large plan handling, empty plan, conflicting user input | ~100 |
| `references/QUALITY-GATES.md` | Per-task section completeness rules | ~80 |
| `references/CIRCUIT-BREAKER.md` | GREP MCP circuit breaker pattern and fallback strategy | ~90 |
| `references/LEARNING-PATTERNS.md` | Memory save/load for task depth preferences | ~80 |

---

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `agents/codebase-scanner.md` | Explore/sonnet | Scans project for related files and existing patterns |
| `agents/grep-mcp-researcher.md` | general-purpose/haiku | Searches GitHub for battle-tested implementations |

---

## Scripts

| Script | Usage | Purpose |
|--------|-------|---------|
| `scripts/validate-tasks.sh` | `bash scripts/validate-tasks.sh tasks/_pending/` | Validates all task files, exits 0 if clean |

---

## Key Behaviors

- **Preview before write:** No task files are created until the user approves the preview table
- **Large plan detection:** Plans with 15+ sections trigger a split warning and auto-split at 100 lines
- **BLOCKED live tests:** Missing .env keys produce stub tests, never skipped tasks
- **Conflict detection:** Contradictory user instructions trigger AskUserQuestion (no silent overrides)
- **Memory persistence:** "Too detailed" or "too vague" feedback saved to `.claude/memory/task-master.md`

---

## Versions

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-02 | Initial release |
