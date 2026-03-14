# Templates Index and Selection Logic

This file documents the 9 skill templates available in `templates/`, explains how to select the right one, and defines rules for filling and customizing them.

---

## Template Selection Flowchart

Work through these questions in order. Stop at the first match.

```
1. Does the skill only teach conventions, rules, or reference knowledge
   with no tool calls?
   YES → simple-knowledge

2. Does the skill wrap a single external tool, API, or service
   (one primary integration)?
   YES → mid-tool

3. Does the skill primarily invoke bash commands, curl calls,
   or CLI tools (scripts over reasoning)?
   YES → scripts-cli

4. Does the skill coordinate multiple tools in parallel,
   gathering information from several sources simultaneously?
   YES → advanced-multi-tool

5. Does the skill need to behave differently based on detected
   language, platform, or OS (conditional branches)?
   YES → branching-workflow

6. Must the skill work identically on any codebase with zero
   project-specific assumptions?
   YES → codebase-agnostic

7. Does the skill call other existing skills and combine their
   outputs (meta-skill that coordinates skills)?
   YES → orchestrator

8. Does the skill have strict sequential phases where each phase
   MUST complete before the next begins (no parallelism)?
   YES → sequential-workflow

9. Does the skill require deep upfront requirement gathering
   before any implementation work (5+ interview questions)?
   YES → question-heavy-interview
```

If no match, default to `mid-tool` and adjust from there.

---

## Template Entries

### 1. simple-knowledge

| Field | Value |
|-------|-------|
| File | `templates/simple-knowledge.md` |
| Best For | Convention guides, cheat sheets, naming rules, style references |
| Tier Match | Tier 1 (Starter) |
| Line Limit | 300 lines |
| Key Features | No tool calls, pure instruction blocks, direct prose |

**When to use:** The skill tells Claude how to behave rather than directing Claude to take actions. Examples: "always use snake_case", "follow these API versioning rules", "apply these commit message patterns".

**What to fill:**
- `name`, `description`, `trigger`
- Convention blocks (numbered or bulleted lists)
- Examples section with good/bad comparisons

**What to remove:** All tool call directives, all bash blocks, phase structure.

---

### 2. mid-tool

| Field | Value |
|-------|-------|
| File | `templates/mid-tool.md` |
| Best For | Single API integrations, one-service wrappers, focused tool use |
| Tier Match | Tier 2 (Intermediate) |
| Line Limit | 400 lines |
| Key Features | One primary tool type, linear flow, clear input/output contract |

**When to use:** The skill revolves around one integration — calling a specific API, reading from one database, or interacting with one external service. Examples: "fetch Stripe invoice", "query PostgreSQL schema", "call OpenAI embeddings".

**What to fill:**
- Tool configuration section (API keys, endpoints)
- Input validation block
- Single tool invocation pattern
- Output parsing and error handling

**What to remove:** Parallel tool blocks, branching logic sections.

---

### 3. scripts-cli

| Field | Value |
|-------|-------|
| File | `templates/scripts-cli.md` |
| Best For | Shell scripts, CLI tools, system commands, file operations |
| Tier Match | Tier 2 (Intermediate) |
| Line Limit | 400 lines |
| Key Features | Bash-heavy, stdout parsing, exit code handling, piped commands |

**When to use:** The skill's core logic is in bash — running linters, invoking compilers, calling CLI tools, parsing command output. Examples: "run ruff and parse violations", "invoke docker build", "run database migrations".

**What to fill:**
- Command templates with variable substitution
- Exit code handling table (0 = success, 1 = X, 2 = Y)
- stdout/stderr parsing patterns
- Rollback or cleanup commands on failure

**What to remove:** Multi-step interview sections, parallel Read/Glob blocks.

---

### 4. advanced-multi-tool

| Field | Value |
|-------|-------|
| File | `templates/advanced-multi-tool.md` |
| Best For | Research-heavy skills, parallel information gathering, synthesis tasks |
| Tier Match | Tier 3 (Advanced) |
| Line Limit | 500 lines |
| Key Features | Parallel tool calls, result synthesis, conflict resolution |

**When to use:** The skill must gather information from many sources simultaneously before it can reason. Examples: "scan all API endpoints and all database tables and synthesize gaps", "read 5 config files in parallel and detect inconsistencies".

**What to fill:**
- Parallel scan block (list all simultaneous tool calls)
- Synthesis rules (how to combine results when they conflict)
- Output format for combined findings

**What to remove:** Sequential phase gates, single-tool patterns.

---

### 5. branching-workflow

| Field | Value |
|-------|-------|
| File | `templates/branching-workflow.md` |
| Best For | Language adapters, platform-specific logic, OS-conditional behavior |
| Tier Match | Tier 3 (Advanced) |
| Line Limit | 500 lines |
| Key Features | Explicit if/else branches, per-platform instruction blocks |

**When to use:** The skill must take completely different actions depending on detected context. Examples: "generate Dockerfile for Python OR Node based on detected language", "apply ESLint config if JS, Ruff config if Python".

**What to fill:**
- Detection block (how to identify which branch to take)
- One labeled section per branch (## If Python, ## If Node.js, etc.)
- Shared post-branch steps (if any)

**What to remove:** Parallel research blocks that apply universally.

---

### 6. codebase-agnostic

| Field | Value |
|-------|-------|
| File | `templates/codebase-agnostic.md` |
| Best For | Universal patterns, cross-project tools, portable analyzers |
| Tier Match | Tier 2 (Intermediate) |
| Line Limit | 400 lines |
| Key Features | Zero language assumptions, universal Glob patterns, language-neutral output |

**When to use:** The skill must work without knowing anything about the project language. Examples: "find all TODO comments across any codebase", "count lines in every source file", "detect files over 500 lines".

**What to fill:**
- Universal Glob patterns (avoid language-specific extensions)
- Language-neutral analysis steps
- Output format with no language-specific fields

**What to remove:** Any framework-specific tool calls, language-specific linting steps.

---

### 7. orchestrator

| Field | Value |
|-------|-------|
| File | `templates/orchestrator.md` |
| Best For | Meta-skills, skill coordinators, pipeline builders |
| Tier Match | Tier 4 (Expert) |
| Line Limit | 600 lines |
| Key Features | Skill tool invocations, result chaining, handoff contracts |

**When to use:** The skill's job is to invoke other skills in sequence or parallel and combine their outputs. Examples: "run tech-stack-researcher THEN dependency-updater THEN deploy-readiness-validator".

**What to fill:**
- Skill invocation order (numbered list)
- Data passed between skills (handoff contract)
- Fallback if a sub-skill fails
- Final synthesis step

**What to remove:** Raw tool calls (Glob, Read, Bash) — delegate those to sub-skills.

---

### 8. sequential-workflow

| Field | Value |
|-------|-------|
| File | `templates/sequential-workflow.md` |
| Best For | Strict phase workflows, quality-gated processes, approval chains |
| Tier Match | Tier 3 (Advanced) or Tier 4 (Expert) |
| Line Limit | 550 lines |
| Key Features | Numbered phases, explicit gate conditions, rollback steps |

**When to use:** Each phase produces output that the next phase requires. No phase can be skipped or parallelized. Examples: "plan THEN validate plan THEN implement THEN test THEN deploy".

**What to fill:**
- Phase number, name, and gate condition for each phase
- What output each phase produces
- Rollback instructions if gate fails

**What to remove:** Parallel tool call blocks within phases.

---

### 9. question-heavy-interview

| Field | Value |
|-------|-------|
| File | `templates/question-heavy-interview.md` |
| Best For | Skills that cannot proceed without user input, discovery-first flows |
| Tier Match | Tier 2–4 depending on post-interview complexity |
| Line Limit | 500 lines |
| Key Features | Structured interview block (5–10 questions), answer-dependent branching |

**When to use:** The skill's behavior changes dramatically based on user answers. Examples: "new agent designer", "project setup wizard", "schema refiner". Cannot default-fill answers from codebase scan alone.

**What to fill:**
- Interview question list (numbered, with accepted answer types)
- Answer parsing rules (what each answer unlocks)
- Post-interview action blocks keyed to answers

**What to remove:** Upfront tool calls that assume knowledge the interview will gather.

---

## How to Fill Templates from Interview Data

After the interview completes, map answers to template fields:

| Interview Answer | Template Field to Fill |
|-----------------|----------------------|
| Skill name | `name:` in frontmatter, H1 heading |
| One-line purpose | `description:` in frontmatter |
| Trigger phrases | `trigger:` list in frontmatter |
| Target language | Branch labels (## If Python), detection block |
| Tool types needed | Tool call blocks (Read, Write, Bash, Glob, Grep) |
| Existing skills to call | Skill tool invocation blocks (orchestrator only) |
| Test framework | Test section (what commands to run, what output to check) |
| Coverage minimum | Acceptance criteria section |
| Phase count | Phase headers (## Phase 1, ## Phase 2, ...) |

---

## Template Customization Rules

**What to add freely:**
- Domain-specific examples
- Project-detected patterns (from Phase 0 scan)
- Error messages with specific fix instructions
- Output format tables

**What to remove when customizing:**
- Placeholder comment blocks (lines starting with `# TODO:`)
- Template-tier labels (remove the tier annotation from the final file)
- Sections that do not apply to this skill's scope

**What must never be changed:**
- Frontmatter field names (`name`, `description`, `trigger`, `version`)
- CSO trigger block structure (PROACTIVELY, trigger phrases)
- Line limit for the chosen tier (enforce via validate-skill.sh)
