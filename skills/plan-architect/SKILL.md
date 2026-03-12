---
name: plan-architect
description: >-
  Architect intelligent, actionable implementation plans for features,
  automations, and system integrations with expert-level systems thinking
  and deep codebase awareness. Use PROACTIVELY when user says "plan this",
  "build an automation", "design a feature", "architect this system",
  "create a plan", "I want to automate", "help me think through", or
  mentions planning, system design, feature architecture, integration
  mapping, or automation logic. Also use when user says "revamp this
  plan", "update the plan", "improve this plan", "revisit", or "redo".
  Use when user describes a feature idea, automation concept, or
  integration need and wants a thorough, battle-tested plan. Also use
  when user opens or references files in the plans/ directory. Entry
  point in pipeline: plan-architect → /extract-tasks → /specs-to-commit.
allowed-tools: >-
  Read Write Edit Bash Task TodoWrite AskUserQuestion Grep Glob
  WebSearch WebFetch
  mcp__plugin_claude-mem_mcp-search__search
  mcp__plugin_claude-mem_mcp-search__timeline
  mcp__plugin_claude-mem_mcp-search__get_observations
license: MIT
metadata:
  author: yasmine
  version: "1.2.0"
  category: planning
  tier: 5
  pipeline-position: entry-point
disable-model-invocation: true
user-invocable: true
model: opus
argument-hint: "[feature-or-automation-description]"
---

# Plan Architect v1.2.0
<!-- ultrathink -->

> Intelligent systems architect that takes your ideas from 3/10 to 10/10.
> Probes, asks expert questions, fills gaps from expertise, connects dots,
> and creates battle-tested, actionable implementation plans.

## The Iron Law

SKILL.md = navigation hub ONLY. Content lives in references/.
SKILL.md line limit: 500 lines MAX.
Reference files: 100-400 lines each.
Every reference needs a → See directive.
Every script needs a → Run directive.

## ⛔ ABSOLUTE RULE: AskUserQuestion — No Exceptions, Ever

Every single question asked to the user — from the first word to the last — MUST go through the `AskUserQuestion` tool.
This applies to: discovery, clarification, approval gates, expert suggestions, round check-ins, and handoff.

**SELF-CHECK: If you are about to type a question mark (`?`) anywhere in your text output, STOP. You are violating this skill. Call `AskUserQuestion` instead.**

| Correct | Wrong |
|---------|-------|
| `AskUserQuestion({ questions: [...] })` | Typing "What approach do you prefer?" |
| Tool call with selectable options | Asking open-ended questions in chat |
| Offering expert suggestions inside a question's description | Writing suggestions in text then asking |
| Checking in after each round via tool | Typing "Ready to move on?" in text |

Violating this rule invalidates the entire session. If you catch yourself violating it mid-session, stop immediately, reframe as a tool call, and continue.

**There is no scenario where typing a question to the user in chat text is acceptable. None.**

---

## Navigation — Read Before Executing

→ See references/CODEBASE-ANALYSIS.md when scanning and understanding the project (Phase 1)
→ See references/INTERVIEW-ENGINE.md when conducting expert interview (Phase 2)
→ See references/RESEARCH-STRATEGY.md when dispatching research agents (Phase 3)
→ See references/SYNTHESIS-ENGINE.md when merging research and scoring complexity (Phase 4)
→ See references/ANTI-PATTERNS.md when reviewing plan for common mistakes (Phase 4)
→ See references/PLAN-TEMPLATE.md when structuring the plan output (Phase 5-7)
→ See references/RESILIENCE-PATTERNS.md when adding fallbacks and resilience to plan (Phase 5)
→ See references/RESILIENCE-ADVANCED.md when adding timeouts, idempotency, health checks, or monitoring (Phase 5)
→ See references/PLAN-QUALITY.md when reviewing plan quality before user approval (Phase 6)
→ See references/DATABASE-PLANNING.md when any database changes are involved — Phase 1.5, Phase 2 DB questions, Phase 5 SQL generation (MANDATORY when feature touches schema)
→ See references/REVAMP-MODE.md when user wants to update, revamp, or improve an existing plan
→ See references/TESTING.md when running pressure tests on the skill itself
→ Run scripts/validate-prerequisites.sh before Phase 1 to check environment (exit 0 = pass)
→ Run scripts/validate-plan-output.sh after Phase 7 to verify plan completeness (exit 0 = pass)
→ Run scripts/grep-enforce.sh to verify MCP grep was used during research (exit 0 = pass)

---

## Quality Gate Table

| Phase | Gate | Blocker? |
|-------|------|----------|
| 0. Initialize | Prerequisites pass | YES |
| 1. Context Loading | Project understood | YES |
| 1.5. DB Introspection | Live schema loaded or migration history read | YES if DB involved |
| 2. Expert Interview | All questions answered | YES |
| 3. Parallel Research | All 3 agents complete | YES |
| 4. Synthesis | Connections mapped, anti-patterns checked | YES |
| 5. Plan Architecture | Draft plan created | YES |
| 6. Review & Approval | User approves plan | BLOCK |
| 7. Write Plan | Plan file written | YES |
| 8. Handoff | Preferences saved | NO |

**IF ANY GATE FAILS → STOP → ESCALATE TO USER → FIX → CONTINUE**

---

## Phase 0: Initialize

### STEP 0 — MANDATORY FIRST ACTION (before ANYTHING else)

Before TodoWrite. Before reading files. Before running scripts. Before mode detection.
The very first thing you do is call AskUserQuestion to find out what we are planning.

```
AskUserQuestion([{
  question: "What would you like to plan today?",
  header: "Planning goal",
  multiSelect: false,
  options: [
    { label: "New feature", description: "A new capability added to the existing system" },
    { label: "New automation / workflow", description: "A pipeline, scheduled job, or triggered process" },
    { label: "New integration", description: "Connecting to an external API or service" },
    { label: "Database / schema change", description: "New tables, migrations, or data model changes" },
    { label: "Improve or revamp an existing plan", description: "Update, revisit, or strengthen a plan already written" }
  ]
}])
```

If the user selects "Improve or revamp an existing plan" → **REVAMP mode** (see references/REVAMP-MODE.md).
Otherwise → **CREATE mode**.

Do NOT assume what we are building from prior conversation context. Even if the topic was discussed earlier,
you must ask. The user may want to plan something different. Always ask. Always.

### STEP 1 — Prerequisites and setup

TodoWrite: Set up all 9 phases as pending (see TodoWrite Phase Tracker section below).

Run scripts/validate-prerequisites.sh — if it fails, create the plans/ directory and retry.

### STEP 2 — Mode Detection (refine from Step 0 answer)

- If $ARGUMENTS is a path to an existing plan file → **REVAMP mode** (overrides Step 0)
- If user said "revamp", "update", "improve", "revisit", "redo" → **REVAMP mode**
- Otherwise → **CREATE mode**

In REVAMP mode: → See references/REVAMP-MODE.md for the complete revamp workflow.
Follow Phases 0R-8R instead of the standard phases below.

In CREATE mode, check for existing plans for the same topic:
- Glob for `plans/**/*.md` matching $ARGUMENTS or Step 0 keywords
- If match found: use AskUserQuestion — "An existing plan was found. Revamp it or create new?"

Gate: Step 0 complete (user has answered what we're building). Prerequisites pass. Mode determined. plans/ directory confirmed to exist.

---

## Phase 1: Context Loading

→ See references/CODEBASE-ANALYSIS.md when executing detailed scanning procedures

1. Read .claude/CLAUDE.md and all .claude/context/*.md files
2. Read existing plans/ directory (understand what's already planned)
3. Scan project structure:
   - Glob for key files (package.json, pyproject.toml, etc.)
   - Grep for imports, dependencies, patterns
   - Use MCP search for past context about this topic
4. Build a mental model of: tech stack, existing patterns, architecture, integrations

Gate: You understand the project well enough to ask intelligent questions.

---

## Phase 1.5: Neon Database Introspection

→ See references/DATABASE-PLANNING.md for introspection commands and schema map format

**Run this phase when the feature description mentions** storing, saving, tracking, recording,
or logging anything — or when the user mentions tables, schema, or data model.
Skip cleanly if the feature has zero database involvement.

1. Resolve DATABASE_URL from environment or .env
2. Run introspection queries (psql preferred, asyncpg fallback) → write to .claude/plan-architect/db-schema.txt
3. If DATABASE_URL unavailable → read alembic/versions/ to reconstruct schema from migrations
4. Build a Current Schema Map: table names, key columns, and FK relationships
5. Identify **anchor tables** (users, orgs, workspaces) — all new tables must FK-chain back to one

**Output for Phase 2 and Phase 5:** You now know exactly what exists. Every DB question
in the interview and every table in the plan references the live schema.

Gate: db-schema.txt exists with content OR Alembic migration files read. Schema map built.

---

## Phase 2: Expert Interview

→ See references/INTERVIEW-ENGINE.md when selecting questions and probing strategies

This is the CORE of plan-architect. The interview has NO fixed number of rounds.
Continue as many rounds as it takes to build a tight, well-connected plan. 3 rounds minimum.
10 or 20 rounds is fine. The goal is a plan with zero ambiguity — keep going until you get there.

### Interview Protocol — Follow Exactly

**Every round MUST use AskUserQuestion. No exceptions.**

**After receiving each answer:**
1. Surface expert insights, suggestions, and gaps the user hasn't considered — include these as rich
   `description` text inside the next round's question options. Do NOT write suggestions as chat text.
2. Build the next round's questions based on what you now know. Go deeper, not broader.
3. Always offer to continue at the end of each round (see check-in format below).

**Expert suggestions DURING questions — format:**
Use the `description` field of each option to inject expert context:
```
{
  label: "Webhook-based (real-time)",
  description: "Recommended for your use case. Your codebase already has an HMAC webhook
                pattern in app/api/webhooks.py — reuse it. Slack's documented retry policy
                is 3 attempts with exponential backoff, so your handler must be idempotent."
}
```
This is how you surface opinions, recommendations, and gap flags — inside the tool, not in chat text.

### Round Structure

**Round 1 — Core Discovery (3-4 questions)**
Topics: What are we building exactly? What triggers it? Who consumes the output? What does success look like?

**Round 2 — Architecture & Integration (3-4 questions)**
Topics: How does it connect to existing systems? What data flows in/out? What third-party APIs? What codebase patterns should we reuse?

**Round 2b — Database Design (run if Phase 1.5 found relevant tables)**
→ See references/DATABASE-PLANNING.md — "Database Domain Interview Questions" section
Reference live schema tables by name. Ask about ownership, volume, query patterns, FK relationships.

**Round 3 — Resilience & Edge Cases (3-4 questions)**
Topics: What happens when X fails? Rate limits and quotas? Security considerations? What should NOT happen?

**Round 4+ — Depth Drilling (as many rounds as needed)**
Topics: Anything ambiguous from prior rounds. Performance requirements. Rollback strategy.
Cost implications. Monitoring and alerting needs. Specific user experience decisions.

Keep drilling until you can answer: "Could I hand this plan to a developer with zero additional context
and have them build exactly what the user needs?" If no → another round.

### Round Check-In (after each round, including round 3+)

After every round, use AskUserQuestion:
```
{
  question: "I have [N] areas I want to probe deeper on. Want to continue, or do you feel
             we have enough to move into research and planning?",
  header: "Continue interview?",
  options: [
    { label: "Keep going — ask more", description: "I want more questions. There's more to explore." },
    { label: "Move to research", description: "I feel confident. Proceed to Phase 3." }
  ]
}
```
If user says "keep going" → run another round. Never stop unless user says to move on.

Gate: User explicitly chooses "Move to research". Minimum 3 rounds completed.

---

## Phase 3: Parallel Research

→ See references/RESEARCH-STRATEGY.md when choosing search strategies and source priorities

**MANDATORY: Dispatch ALL 3 agents in a SINGLE message for true parallelism.**

### Agent A: Codebase Pattern Analyzer
```
Task({
  subagent_type: "Explore",
  model: "sonnet",
  description: "Analyze codebase patterns",
  prompt: "Scan the codebase for patterns relevant to [topic]. Use Grep extensively.
  Find: existing similar implementations, reusable utilities, database patterns,
  API patterns, error handling approaches. Write findings to
  .claude/plan-architect/codebase-research.md"
})
```

### Agent B: Web Researcher
```
Task({
  subagent_type: "general-purpose",
  model: "sonnet",
  description: "Research web APIs and patterns",
  prompt: "Research [topic] best practices, API documentation, integration patterns.
  Search for: official docs, rate limits, authentication methods, common pitfalls.
  Write findings to .claude/plan-architect/web-research.md"
})
```

### Agent C: MCP Pattern Searcher (MANDATORY - grep enforcement)
```
Task({
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Search MCP for past context",
  prompt: "Use MCP search tools to find past decisions, patterns, and context
  related to [topic]. Search for relevant observations.
  Write findings to .claude/plan-architect/mcp-research.md"
})
```

Wait for all 3 to complete. Read all 3 result files.
Run scripts/grep-enforce.sh to verify grep was used.

Gate: All 3 agents completed and returned useful findings.

---

## Phase 4: Synthesis & Connection

→ See references/SYNTHESIS-ENGINE.md when merging research and scoring complexity
→ See references/ANTI-PATTERNS.md for common planning mistakes to catch

1. Read all 3 research outputs from Phase 3
2. Merge findings into a unified understanding
3. Connect dots between:
   - User requirements (from interview)
   - Codebase patterns (from Agent A)
   - Best practices (from Agent B)
   - Past decisions (from Agent C)
4. Apply anti-pattern detection — warn about:
   - Over-engineering
   - Missing error handling
   - Ignoring rate limits
   - Coupling too tightly
   - Reinventing existing patterns
5. Score each section for implementation complexity (1-5)
6. **Database Compatibility Check** (if Phase 1.5 ran):
   → See references/DATABASE-PLANNING.md — "No Orphan Tables Rule" section
   - For every planned new table: verify it has a documented FK path to an anchor table
   - For every planned modification: verify backward compatibility with existing queries
   - Flag any table that has no relationship to the existing schema — redesign before proceeding

Gate: Synthesis is complete. All dots connected. Anti-patterns identified. No orphan tables.

---

## Phase 5: Plan Architecture

→ See references/PLAN-TEMPLATE.md when building the complete plan structure
→ See references/RESILIENCE-PATTERNS.md when selecting fallback and recovery patterns

→ See references/PLAN-TEMPLATE.md for the canonical folder structure and per-file content
→ See references/DATABASE-PLANNING.md for SQL generation and migration format (if DB involved)

Build the plan as a **folder** `plans/{topic-kebab}/` with separate files per section.
Non-verbose: every line earns its place. No filler. Dense, actionable content only.

File structure:
```
plans/{topic}/
├── PLAN.md             # Index: metadata + navigation links to all files below
├── 01-overview.md      # System overview, architecture diagram, success criteria
├── 02-database.md      # DB design: current schema context + new SQL + Alembic migration
├── 03-implementation.md # Phased implementation: steps, files, verify commands
├── 04-resilience.md    # Error scenarios, retry policy, circuit breakers
├── 05-testing.md       # Coverage requirements, unit/integration/manual tests
└── 06-context.md       # Context loading order + grep patterns
```

Omit `02-database.md` only if zero database changes are involved.

Gate: Draft plan folder created with all required files having substantive content.

---

## Phase 6: Review & Approval

Present the complete plan for approval.

If an existing plan was found in Phase 0:
- Show a DIFF of what changed
- Highlight new sections, removed sections, and modified sections

Use AskUserQuestion:
- "Approve — Save this plan"
- "Modify — I want changes" → ask what to change → revise → re-present
- "Cancel — Discard"

**BLOCK: Do not write the plan until user approves.**

---

## Phase 7: Write Plan

Create the plan folder and write all files:

```
mkdir -p plans/{topic-kebab}/
```

Write each file independently. Every file: comprehensive, actionable, zero filler.
Dense tables and checklists over prose wherever possible.

If versioning mode (existing plan found):
- Archive entire previous folder: `plans/archive/{name}-v{N}/`
- Write new folder, increment version in PLAN.md

Run scripts/validate-plan-output.sh plans/{topic-kebab}/ — if it fails, fix and retry.

Gate: Plan folder exists with all required files, each passing content checks.

---

## Phase 8: Handoff

1. Save user preferences to .claude/skills/plan-architect/prefs.json:
   - Preferred plan sections
   - Common integrations
   - Standard approaches

2. Present next steps:
   - "Run /extract-tasks plans/{name}.md to generate implementation tasks"
   - "Run /specs-to-commit to create specs from the plan"

3. Clean up temporary research files in .claude/plan-architect/

---

## TodoWrite Phase Tracker

At Phase 0 Initialize, write ALL phases at once using a single TodoWrite call.
Never write phases one at a time — batch them.

```
TodoWrite([
  { id: "p0",  content: "Phase 0: Initialize — validate prerequisites + detect mode", status: "in_progress" },
  { id: "p1",  content: "Phase 1: Context Loading — read CLAUDE.md + scan project", status: "pending" },
  { id: "p1b", content: "Phase 1.5: DB Introspection — psql/asyncpg schema + build schema map", status: "pending" },
  { id: "p2",  content: "Phase 2: Expert Interview — 3 rounds + DB questions + gap filling", status: "pending" },
  { id: "p3",  content: "Phase 3: Parallel Research — dispatch 3 agents simultaneously", status: "pending" },
  { id: "p4",  content: "Phase 4: Synthesis — merge findings + anti-patterns + orphan table check", status: "pending" },
  { id: "p5",  content: "Phase 5: Plan Architecture — build folder with 6 focused .md files", status: "pending" },
  { id: "p6",  content: "Phase 6: Review & Approval — present plan folder + await user approval", status: "pending" },
  { id: "p7",  content: "Phase 7: Write Plan — write folder + all files + run validation script", status: "pending" },
  { id: "p8",  content: "Phase 8: Handoff — save prefs + present next steps + cleanup", status: "pending" }
])
```

Update each phase to `in_progress` when starting, `completed` when its gate passes.

---

## Output Contract

The plan file written in Phase 7 MUST satisfy all of these:

| Requirement | Check |
|-------------|-------|
| Folder exists at plans/{topic-kebab}/ | Script checks directory |
| PLAN.md (index) with metadata + links | Script checks PLAN.md exists, has version/date |
| 01-overview.md: overview + architecture diagram + success criteria | Script grep-checks headings |
| 03-implementation.md: phased steps with file paths and verify commands | Script checks for "Verify:" pattern |
| 04-resilience.md: error table + retry policy | Script checks for fallback/retry/circuit keywords |
| 05-testing.md: coverage requirements + test table | Script checks for "coverage" |
| 06-context.md: file load order + grep patterns (≥2) | Script checks grep pattern count |
| 02-database.md present if DB changes planned | Script checks: if "CREATE TABLE" in any file, 02-database.md must exist |
| 02-database.md: current schema context + SQL + Alembic stub | Script checks for CREATE TABLE + def upgrade |
| No orphan tables (every new table has FK to existing) | Script checks for REFERENCES keyword in all CREATE TABLEs |
| No unfilled placeholders in any file | Script scans all files for TODO/PLACEHOLDER/TBD |

If ANY requirement fails → scripts/validate-plan-output.sh exits non-zero → fix and retry.

---

## Reference Files Manifest

All 8 reference files are REQUIRED. If any are missing, create stubs with placeholders.

| File | Purpose | Trigger Phase | Lines (target) |
|------|---------|---------------|----------------|
| references/CODEBASE-ANALYSIS.md | Detailed scanning procedures and file patterns | Phase 1 | 150-200 |
| references/INTERVIEW-ENGINE.md | Full question bank across all domains | Phase 2 | 200-300 |
| references/RESEARCH-STRATEGY.md | Search strategies and source priorities per domain | Phase 3 | 150-200 |
| references/SYNTHESIS-ENGINE.md | Merging logic and complexity scoring rubric | Phase 4 | 100-150 |
| references/ANTI-PATTERNS.md | Common planning mistakes by category | Phase 4 | 150-250 |
| references/PLAN-TEMPLATE.md | Complete 9-section template with examples | Phase 5-7 | 200-400 |
| references/RESILIENCE-PATTERNS.md | Core patterns: retry, circuit breaker, saga, fallback, rate limiting | Phase 5 | 150-280 |
| references/RESILIENCE-ADVANCED.md | Advanced: timeouts, dead letters, health checks, idempotency, monitoring | Phase 5 | 200-300 |
| references/PLAN-QUALITY.md | Good vs bad plan characteristics, forgotten sections, review checklist | Phase 6 | 60-100 |
| references/DATABASE-PLANNING.md | Neon introspection, no-orphan-tables rule, SQL generation, Alembic migration format | Phase 1.5, 2, 4, 5 | 200-350 |
| references/REVAMP-MODE.md | Complete revamp workflow: delta analysis, focused interview, diff display | Phase 0 (mode) | 150-250 |
| references/TESTING.md | Skill pressure test scenarios and validation | On demand | 100-200 |

All 3 scripts are REQUIRED. If missing, create them as executable bash scripts.

| Script | Purpose | When to Run | Expected Exit |
|--------|---------|-------------|---------------|
| scripts/validate-prerequisites.sh | Check plans/ dir, .claude/ context | Phase 0 start | 0 = pass |
| scripts/validate-plan-output.sh | Verify 9-section completeness, front matter | Phase 7 end | 0 = pass |
| scripts/grep-enforce.sh | Confirm Grep was called during research | After Phase 3 | 0 = pass |

---

## Error Recovery Guide

### If Phase 0 fails (missing plans/ directory)
```
mkdir -p plans/archive
```
Then rerun scripts/validate-prerequisites.sh.

### If Phase 1 fails (no context files found)
Run /generate-project-context to create .claude/context/ files, then retry Phase 1.

### If Phase 2 stalls (user gives one-word answers)
Switch to yes/no questions. Offer concrete options instead of open-ended prompts.
Example: "Should this use webhooks (real-time) or polling (scheduled)? Pick one."

### If Phase 3 fails (agent returns empty findings)
- Agent A empty: Grep for broader terms, check if project has source code at all.
- Agent B empty: Retry with more specific search terms, check internet connectivity.
- Agent C empty: Use different MCP search terms, check if MCP plugin is active.
Do NOT proceed to Phase 4 with fewer than 2 agents having useful output.

### If Phase 6 user chooses "Modify"
1. Ask: "What specifically needs to change?"
2. Make targeted edits — do NOT regenerate the entire plan.
3. Re-present only the modified sections.
4. Ask for approval again.

### If scripts/validate-plan-output.sh fails
Read the script output carefully — it will identify which section is missing.
Add the missing section to the plan file and rerun the script.
Never skip the script or declare success without exit code 0.

---

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I know enough to skip the interview" | The interview IS the value. Never skip Phase 2. |
| "Web research isn't needed for this" | You're wrong. Always research. Phase 3 is mandatory. |
| "MCP grep search returned nothing" | Search harder. Use different terms. Retry. |
| "This plan is good enough without resilience" | No plan is complete without fallback strategies. |
| "The user didn't ask for complexity scores" | They need them. Always include. |
| "Skip the anti-pattern check, it's fine" | Anti-patterns hide in confidence. Always check. |
| "I'll just use one research agent" | All 3 agents are mandatory. Dispatch in parallel. |
| "The validate script is failing but the plan looks fine" | Exit code 0 is truth. Your eyes are not. Fix it. |
| "I'll clean up temp files later" | Clean up in Phase 8, every time, without exception. |
| "I'll just rewrite the whole plan" | If <7 sections need changes, use REVAMP mode. Only full rewrite if 7+. |
| "I know what tables the project has" | You don't. Run Phase 1.5. Introspect the live schema. |
| "This table doesn't need a FK" | Every table needs a documented relationship. No exceptions. |
| "I'll add the migration later" | Migration SQL is part of the plan. Write it in 02-database.md now. |
| "A single .md file is fine for a small plan" | Plans are always a folder. No exceptions. |
| "I already know what we're building from the conversation" | You don't get to decide that. Ask via AskUserQuestion. Always. |
| "I'll just ask in chat text, it's faster" | It is never faster. It breaks the skill. Use AskUserQuestion. |
| "I have enough after 3 rounds, I'll move on" | Only the user decides when to move on. Always offer to continue. |
| "I'll put my suggestions in chat text, then ask the question" | No. Embed suggestions in option descriptions inside the tool call. |
| "The user seems ready to move on, so I'll skip the check-in" | Ask the check-in question every single round. Never assume. |
| "I know what they mean, I don't need to ask for clarification" | Assumptions kill plans. Ask. AskUserQuestion. |
