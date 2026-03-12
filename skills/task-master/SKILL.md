---
name: task-master
description: >
  Converts implementation plans from plan/ into atomic, dependency-ordered task files
  for skills, agents, reference files, and hooks. Enforces success criteria, validation
  testing, and GREP MCP research on every task. Use PROACTIVELY when user says "generate
  tasks", "create task files", "break plan into tasks", "extract tasks from plan", "build
  task list", or mentions tasks/_pending/ being empty. Use when plan-architect output needs
  tasks extracted. Also use when user opens any .md file in plan/ or plans/ directories.
  Part of the implementation pipeline with plan-architect and specs-to-commit.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Write
  - Edit
  - Bash
  - Task
  - WebFetch
  - WebSearch
model: claude-opus-4-6
argument-hint: "path/to/plan (optional, defaults to interactive selection)"
context:
  - .claude/context/PROJECT_CONTEXT.md
  - .claude/context/CODE_QUALITY_RULES.md
  - .claude/context/TESTING_RULES.md
  - .claude/MISTAKES.md
hooks:
  post-invoke: .claude/skills/task-master/hooks/post-tool.sh
metadata:
  version: "1.0.0"
  author: yasmine
  tags: [task-generation, planning, pipeline, testing]
  category: planning
  stability: stable
  tier: 6
  created: "2026-03-02"
  updated: "2026-03-02"
license: MIT
---

# task-master v1.0.0

> Converts plans into atomic, dependency-ordered task files with full testing standards.
> Step 2 of 3 in the pipeline: **plan-architect → task-master → specs-to-commit**

## The Iron Law

```
SKILL.md LINE LIMIT: 600 lines (Tier 6, NON-NEGOTIABLE)
├── SKILL.md = navigation hub ONLY
├── All content lives in references/
├── Every references/ file needs a → See directive here
└── TASK FILE OUTPUT STANDARD = NON-NEGOTIABLE (see TASK-TEMPLATE.md)

TASK FILE OUTPUT STANDARD (every generated task MUST have):
├── 001, 002, ... numbering
├── Files to read section with explicit paths
├── Success criteria (measurable, specific)
├── Full testing section (unit + integration + live API where applicable)
├── Start-to-finish checklist with success criteria per item
├── Dependency relationships (blockedBy: [002, 003])
├── TaskCreate invocation at task start
├── TaskUpdate invocation at task complete
├── 100% test pass requirement
└── Thorough yet non-verbose (every line earns its place)
```

## ORCHESTRATOR LAW (NON-NEGOTIABLE)

```
task-master is a PURE ORCHESTRATOR. It NEVER:
  ✗ Writes application code (no new .py, .ts, .sql files)
  ✗ Edits existing source files
  ✗ Runs application tests (uv run pytest is for agents only)
  ✗ Implements any checklist item from any task file
  ✗ "Helps" an agent by writing even one line of implementation

task-master ONLY:
  ✓ Reads plan files
  ✓ Asks the user questions (AskUserQuestion)
  ✓ Writes task files to tasks/_pending/
  ✓ Writes TASK-LOG.md
  ✓ Runs validate-tasks.sh (the pipeline health check script, not app tests)
  ✓ Dispatches agents via Task tool
  ✓ Monitors _completed/ via Glob to verify wave completion
  ✓ Reports status to the user

If you feel the urge to write code → STOP → dispatch an agent instead.
This law has no exceptions. Not for "small tasks". Not for "quick fixes".
```

---

## Reference Files Manifest

→ See references/TASK-TEMPLATE.md — Non-negotiable task file template with all required sections
→ See references/PLAN-ANALYSIS.md — How to parse plan files and extract implementation sections
→ See references/DEPENDENCY-ENGINE.md — How to order tasks by dependency and write blockedBy chains
→ See references/TESTING-STANDARDS.md — Full testing section requirements including live API testing
→ See references/CONTEXT-INJECTION.md — How to add file paths and codebase context to tasks
→ See references/PIPELINE-CONTRACT.md — Input/output contracts with plan-architect and specs-to-commit
→ See references/EDGE-CASES.md — Pressure test scenarios and edge case handling
→ See references/QUALITY-GATES.md — Per-task validation rules and section completeness checks
→ See references/CIRCUIT-BREAKER.md — GREP MCP circuit breaker pattern and fallback strategy
→ See references/LEARNING-PATTERNS.md — How to save and load task depth corrections from memory
→ See references/RULES-INJECTION.md — .claude/rules/ discovery, matching matrix, and per-task injection format

## Agent Definitions

→ See agents/codebase-scanner.md — Explore/sonnet agent for parallel codebase research
→ See agents/grep-mcp-researcher.md — general-purpose/haiku agent for GREP MCP pattern research

## Scripts

→ Run: scripts/validate-tasks.sh $TASKS_DIR — Validate all task files before pipeline handoff (exit 0 = pass)

## Hooks

→ hooks/post-tool.sh — PostToolUse: validates task file sections, logs audit trail (warn-only)

---

## Quality Gates

| Phase | Gate | Blocker? | Command |
|-------|------|----------|---------|
| 0. Initialize | Memory loaded, plan folder found | YES | Glob plans/ |
| 1. Interview | Plan selected, integrations mapped | YES | AskUserQuestion |
| 2. Research | Both agents returned results | NO | Task (parallel) |
| 3. Analysis | Plan parsed, task count estimated | YES | AskUserQuestion (preview) |
| 4. Task generation | Each task passes 10-section check | YES | hooks/post-tool.sh |
| 5. Finalization | validate-tasks.sh exits 0 | YES | Bash scripts/validate-tasks.sh |

**IF ANY GATE FAILS → STOP → FIX → RE-RUN → CONTINUE**

---

## Phase 0: Initialize

→ See references/PIPELINE-CONTRACT.md §input for expected plan file locations

1. **TodoWrite:** Initialize phases 0-5 as pending. Mark phase 0 in_progress.
2. **Load memory:** Read `.claude/memory/task-master.md` if exists.
   - Apply saved task depth preferences as defaults.
   - Note any past "too detailed" / "too atomic" corrections.
3. **Load MISTAKES.md:** Grep for past mistakes in plan parsing or task generation.
4. **Load context files** (if not pre-loaded by `context:` frontmatter):
   - `.claude/context/PROJECT_CONTEXT.md` — tech stack, directory structure
   - `.claude/context/TESTING_RULES.md` — test patterns, coverage requirements
   - `.claude/context/CODE_QUALITY_RULES.md` — lint, type checks, commands
5. **Load .env keys:** `Bash: grep -E "^[A-Z_]+=.+" .env 2>/dev/null | cut -d= -f1` → list available API keys for live testing detection
6. **Discover rules:**
   → See references/RULES-INJECTION.md §discovery for rules map format
   - `Glob: .claude/rules/*.md` and `~/.claude/rules/*.md`
   - Build rules map: `{path, scope: always|conditional, keywords}` — store for Phase 4 injection
7. **Discover plans:**
   - Glob `plan/` for `*.md` files
   - Glob `plans/` for `*.md` files (plan-architect output)
   - If 0 plans found → **HALT**: "No plans found. Run `/plan-architect` first."
   - If 1 plan found → auto-select, confirm to user
   - If 2+ plans found → proceed to Phase 1 interview

**Gate:** Plans found. Proceed to Phase 1.

---

## Phase 1: Interview

→ See references/PLAN-ANALYSIS.md §selection for multi-plan disambiguation logic

**If multiple plans found, ask via AskUserQuestion:**
- List all plans with title, file size, and modification date
- Allow user to select one (or "all — generate tasks for every plan")

**Clarification questions (ask if genuinely unclear — do not assume):**
- If plan references an external service with no .env key found → "I see this plan uses {service}. I didn't find {KEY} in .env. Should tasks include a BLOCKED note for live testing?"
- If plan has sections with no clear implementation scope → describe the section, ask if it should be one task or multiple
- If plan mentions a framework or pattern not seen in the codebase → "I don't see {pattern} in this codebase. Is this a new integration or should tasks reference an existing approach?"

**Do NOT ask about:**
- Things clearly documented in the plan
- Standard patterns already in the codebase
- Test commands already defined in CODE_QUALITY_RULES.md

**Gate:** Plan selected. Ambiguities resolved. Proceed to Phase 2.

---

## Phase 2: Parallel Codebase Research [PARALLEL]

→ See agents/codebase-scanner.md for codebase research agent prompt
→ See agents/grep-mcp-researcher.md for GREP MCP research agent prompt
→ See references/CIRCUIT-BREAKER.md for GREP MCP failure handling

Dispatch BOTH agents in ONE message (true parallel):

```
Agent A (codebase-scanner):
  subagent_type: Explore
  model: sonnet
  run_in_background: true
  prompt: [See agents/codebase-scanner.md §prompt-template]

Agent B (grep-mcp-researcher):
  subagent_type: general-purpose
  model: haiku
  run_in_background: true
  prompt: [See agents/grep-mcp-researcher.md §prompt-template]
```

**Circuit breaker:** Check `.claude/circuit-breakers/grep-mcp.json` before dispatching Agent B.
If state = "open" and cooldown not expired → skip Agent B, use local research only.

**Wait** for both agents. Merge results:
- Agent A results → list of related files, existing patterns, project conventions
- Agent B results → battle-tested implementations from GitHub, API usage patterns

**Gate:** At least Agent A completed (Agent B optional if circuit broken). Proceed to Phase 3.

---

## Phase 3: Plan Analysis

→ See references/PLAN-ANALYSIS.md for plan parsing procedure
→ See references/DEPENDENCY-ENGINE.md for dependency detection algorithm

1. **Parse the selected plan:**
   - Identify implementation sections (skip overview, architecture descriptions)
   - Extract: what to build, what files to modify, what tests to write
   - Detect integration services referenced (cross-check with .env keys found in Phase 0)
   - Estimate task count (1 task per atomic buildable unit)

2. **Check for large plans:**
   → See references/EDGE-CASES.md §large-plan if task count > 15
   - Flag plan sections too large for one context window (> ~100 lines of implementation)
   - Split those sections into sub-tasks

3. **Build dependency graph:**
   → See references/DEPENDENCY-ENGINE.md §graph-builder
   - Identify which tasks must complete before others can start
   - Assign tentative numbers (001, 002...) in dependency order

4. **Approval gate — show preview table before writing:**

   Present to user via AskUserQuestion:
   ```
   | # | Task Title | Est. Lines | Depends On | Has Live API Test? |
   |---|-----------|-----------|-----------|-------------------|
   | 001 | ... | ~80 | — | No |
   | 002 | ... | ~90 | 001 | Yes (STRIPE_API_KEY) |
   ```
   Options: **Proceed** / **Modify task list** / **Cancel**

**Gate:** User approves task list. Proceed to Phase 4.

---

## Phase 4: Task Generation Loop

→ See references/TASK-TEMPLATE.md for the mandatory task file format
→ See references/TESTING-STANDARDS.md for the full testing section requirements
→ See references/CONTEXT-INJECTION.md for how to add file paths and context
→ See references/QUALITY-GATES.md for the per-task section completeness check

**For each task in dependency order:**

1. **Write task file** to `tasks/_pending/{NNN}-{kebab-title}.md`
   - Follow TASK-TEMPLATE.md exactly — no section may be omitted
   - Fill TESTING-STANDARDS.md §live-api for any integration services
   - Inject file paths per CONTEXT-INJECTION.md §path-injection
   - Set `blockedBy:` per DEPENDENCY-ENGINE.md §blockedBy-syntax
   - Inject relevant rules per RULES-INJECTION.md §matching-matrix into `## Relevant Rules`

2. **Quality gate (post-write):**
   - hooks/post-tool.sh validates the file automatically
   - If any required section is missing → HALT, fix the file, re-validate
   - Required sections checked: Summary, Files to Read, Success Criteria, Checklist, Testing Section, Dependencies

3. **On ambiguity during generation:**
   - If a task section is genuinely unclear → AskUserQuestion with specific options
   - Never fabricate implementation details; ask or skip with a TODO note

4. **Track via TaskCreate:**
   ```
   TaskCreate(subject: "NNN: {task title}", description: "...", activeForm: "Implementing...")
   ```

5. **Error recovery:**
   - Network errors on WebFetch/GREP MCP → see CIRCUIT-BREAKER.md §fallback
   - Plan ambiguity → AskUserQuestion (escalate, do not skip or fabricate)
   - File write failure → Halt immediately, report the path and error

**Gate:** All task files written and validated. Proceed to Phase 5.

---

## Phase 5: Finalization

→ See references/PIPELINE-CONTRACT.md §output for TASK-LOG.md format
→ See references/LEARNING-PATTERNS.md for saving corrections to memory
→ Run: scripts/validate-tasks.sh tasks/_pending — Must exit 0 before completion

1. **Write TASK-LOG.md** to `tasks/TASK-LOG.md`:
   - Table: task number, title, plan source, created timestamp, estimated context windows, live API required
   - Pipeline info: "Generated by task-master v1.0.0 from {plan-file} on {date}"

2. **Run pipeline validation:**
   ```
   Bash: bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending
   ```
   - If exit non-zero → report which tasks failed which checks → fix → re-run

3. **Save learning corrections** (if user made corrections during generation):
   → See references/LEARNING-PATTERNS.md §save-procedure
   - Save to `.claude/memory/task-master.md`

4. **Mark all tasks as in_progress via TaskUpdate:**
   - Actually, task files are created, NOT yet in progress — they live in `_pending/`
   - TaskUpdate marks task-master's own generation task as completed

5. **Confirm deployment with user (MANDATORY — no skipping):**

   Use AskUserQuestion with this exact information before dispatching a single agent:
   ```
   Task generation complete. Ready to deploy agents.

   Wave plan:
     Wave 0 (immediate): tasks {NNN, NNN, ...} — no dependencies
     Wave 1 (after wave 0): tasks {NNN, ...}
     Wave 2 (after wave 1): tasks {NNN, ...}

   Total: {N} tasks across {K} waves.
   Live API required: {list tasks with keys needed, or "none"}

   Deploy agents now?
   ```
   Options: **Yes, deploy** / **No, I'll implement tasks manually** / **Cancel**

   If user selects "No" or "Cancel" → stop here. Deliver the task files only.
   If user selects "Yes, deploy" → proceed to wave execution below.

6. **Deploy parallel agent team (only if user confirmed above):**
   → See references/PIPELINE-CONTRACT.md §parallel-deployment for agent prompt template and wave algorithm
   - ORCHESTRATOR LAW REMINDER: You dispatch. Agents implement. Never cross this line.
   - Build dependency waves from TASK-LOG.md (wave 0 = tasks with `BlockedBy: —`)
   - Dispatch wave 0: ALL agents in ONE message (`run_in_background: true`)
   - Wait for wave N completion (Glob `tasks/_completed/` to verify, not just agent messages)
   - Dispatch wave N+1: tasks whose full `BlockedBy` list is now in `_completed/`
   - Continue until all task files are in `tasks/_completed/`
   - On agent failure: halt that wave, report to user, ask: retry / skip / cancel

7. **Delivery report:**
   ```
   ✓ {N} tasks generated in tasks/_pending/
   ✓ Dependency chain: 001 → 002 → ... → {N}
   ✓ Live API tests: {count} tasks require .env keys ({list keys})
   ✓ TASK-LOG.md written
   ✓ Pipeline validation: PASS
   Next step: Pick up tasks from tasks/_pending/ — implement manually or run /specs-to-commit
   ```

---

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "This task is simple, I'll just implement it directly" | **NEVER.** You are an orchestrator. Deploy an agent. Full stop. |
| "I'll write a quick helper function while I'm here" | No. That is implementation. Dispatch an agent. |
| "The agent might get confused, I'll implement this one part" | The agent's confusion is an agent problem. Your job is dispatch + monitor. |
| "I'll just run the tests to see if the code is correct" | Agents run tests. You only run `validate-tasks.sh`. |
| "The user is waiting, I should show progress by building" | Report wave status. Show _completed/ counts. Never touch source files. |
| "I'll implement the boilerplate and let the agent do the logic" | No. Zero lines of application code. Dispatch immediately. |
| "I should confirm the approach works before deploying agents" | Write thorough task files. Trust them. That is your quality control. |
| "This task is simple, skip the testing section" | Every task has a testing section. No exceptions. |
| "I can infer the file paths without searching" | Use Grep/codebase-scanner. Wrong paths waste context windows. |
| "The user didn't mention live API testing for this" | Check .env keys. If the service is in .env, include live test steps. |
| "This plan section is clear, no need to ask" | If unclear to implement, ask. Fabricated steps create broken code. |
| "I'll write TASK-LOG.md later" | Write it in Phase 5 before the delivery report. |
| "validate-tasks.sh is optional for simple tasks" | It runs on every generation. Non-negotiable. |
| "These two tasks can share a context window" | Each task is atomic. If it needs another task's context, it's blocked. |
| "GREP MCP is unavailable, skip external research" | Check circuit breaker. Degrade to local only. Never skip research entirely. |
| "The dependency is implied, I don't need to write blockedBy" | Write blockedBy explicitly. specs-to-commit reads it programmatically. |
| "100% test pass is aspirational, not literal" | It is literal. Every task ends with `bash scripts/validate-tasks.sh` and manual skill validation. |
| "I'll skip the deployment confirmation since the user said go" | Phase 5 step 5 AskUserQuestion is mandatory. Always show the wave plan first. |
