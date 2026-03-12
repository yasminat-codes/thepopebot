# Tier Structures

Complete folder structures for all 7 tiers with file descriptions and line estimates.

---

## Tier 1: Simple Knowledge

**Profile:** Pure reference material. No execution, no tools. The skill is the document.

```
my-skill/
├── SKILL.md                     (~50-150 lines)
└── references/                  (optional, 0-1 files)
    └── GLOSSARY.md              (~30-80 lines)
```

### File Descriptions

| File | Lines | Purpose |
|---|---|---|
| SKILL.md | 50-150 | The entire skill: frontmatter, description, and static reference content |
| references/GLOSSARY.md | 30-80 | Optional supporting definitions, lookup tables, or examples |

### When to Add `references/`

Add it only if the SKILL.md would exceed 150 lines without it. Otherwise everything lives in SKILL.md.

### Example Tier 1 SKILL.md Structure

```markdown
---
name: naming-conventions
description: Project naming conventions reference
tier: 1
---

# Naming Conventions

## Files
- snake_case for Python files
- kebab-case for frontend files

## Variables
- SCREAMING_SNAKE for constants
...
```

---

## Tier 2: Basic Workflow

**Profile:** Linear execution with 2-3 tools. No branching, no agents, no parallel calls.

```
my-skill/
├── SKILL.md                     (~100-200 lines)
├── references/                  (0-1 files)
│   └── EXAMPLES.md              (~50-100 lines)
└── tests/
    └── test-cases.md            (~30-60 lines)
```

### File Descriptions

| File | Lines | Purpose |
|---|---|---|
| SKILL.md | 100-200 | Frontmatter + step-by-step execution instructions for 2-3 tools |
| references/EXAMPLES.md | 50-100 | Concrete examples of inputs/outputs to guide execution |
| tests/test-cases.md | 30-60 | 2-3 test scenarios with expected behavior |

### When to Add `tests/`

Add `tests/` when the skill produces output that can be verified — a file, a report, a formatted result. Skip it for pure lookup skills.

### Example Tier 2 SKILL.md Structure

```markdown
---
name: file-generator
description: Reads a template and writes a new file
tier: 2
tools: [Read, Bash]
---

# File Generator

## Phase 1: Read Template
1. Use Read to load the template from references/EXAMPLES.md
2. Extract the relevant section for the requested type

## Phase 2: Write Output
1. Use Bash to write the populated template to the target path
2. Confirm the file was written successfully
```

---

## Tier 3: Intermediate

**Profile:** 3-5 tools, 3-5 phases, 1-2 reference files. Introduces conditional logic and structured output.

```
my-skill/
├── SKILL.md                     (~150-300 lines)
├── references/
│   ├── REF-1.md                 (~80-150 lines)
│   └── REF-2.md                 (~60-120 lines)
├── tests/
│   ├── test-cases.md            (~60-100 lines)
│   └── fixtures/                (optional)
│       └── sample-input.json
└── docs/                        (optional)
    └── USAGE.md                 (~40-80 lines)
```

### File Descriptions

| File | Lines | Purpose |
|---|---|---|
| SKILL.md | 150-300 | Full workflow with conditional paths, 3-5 phases, tool usage instructions |
| references/REF-1.md | 80-150 | Primary domain reference (patterns, rules, schemas) |
| references/REF-2.md | 60-120 | Secondary reference (examples, edge cases, lookup tables) |
| tests/test-cases.md | 60-100 | 4-6 test scenarios including one edge case |
| tests/fixtures/ | varies | Sample inputs for reproducible test runs |
| docs/USAGE.md | 40-80 | User-facing usage guide (when the skill is shared) |

### When to Add `fixtures/`

Add `fixtures/` when test scenarios require specific input files — JSON, YAML, or markdown that the skill will process. Without fixtures, tests are harder to reproduce.

### When to Add `docs/`

Add `docs/` only when the skill will be shared with others or published. Internal-only skills skip it.

---

## Tier 4: Advanced

**Profile:** 5-7 tools, 4-6 phases, parallel research, 3-5 reference files. Produces multi-part output.

```
my-skill/
├── SKILL.md                     (~200-400 lines)
├── references/
│   ├── REF-1.md                 (~100-200 lines)
│   ├── REF-2.md                 (~80-150 lines)
│   ├── REF-3.md                 (~80-150 lines)
│   ├── REF-4.md                 (~60-100 lines)
│   └── REF-5.md                 (~60-100 lines, optional)
├── tests/
│   ├── test-cases.md            (~80-150 lines)
│   ├── fixtures/
│   │   ├── sample-a.json
│   │   └── sample-b.yaml
│   └── expected-outputs/        (optional)
│       └── expected-report.md
├── docs/
│   ├── USAGE.md                 (~60-100 lines)
│   └── EXAMPLES.md              (~80-150 lines)
└── scripts/                     (optional)
    └── validate.sh              (~20-50 lines)
```

### File Descriptions

| File | Lines | Purpose |
|---|---|---|
| SKILL.md | 200-400 | Full workflow, parallel tool calls, output format specs, error handling |
| references/REF-*.md | 60-200 each | Domain knowledge, patterns, API references, decision matrices |
| tests/test-cases.md | 80-150 | 6-10 test cases, parallel execution tests, edge cases |
| tests/fixtures/ | varies | All input files needed for test reproduction |
| tests/expected-outputs/ | varies | Golden outputs for automated comparison |
| docs/USAGE.md | 60-100 | How to invoke the skill, required arguments |
| docs/EXAMPLES.md | 80-150 | Real worked examples with full inputs and outputs |
| scripts/validate.sh | 20-50 | Optional: pre/post validation hook for the skill |

### When to Add `scripts/`

Add `scripts/` when the skill needs to validate environment state before running (e.g., checking that a required CLI tool is installed) or needs a cleanup step after execution.

### When to Add `expected-outputs/`

Add `expected-outputs/` when test cases have known correct outputs that can be diffed. Especially useful for code generators or report producers.

---

## Tier 5: Very Advanced

**Profile:** 6-9 tools, 5-8 phases, 1+ agents, external scripts, 5-10 reference files. Requires orchestration of sub-processes.

```
my-skill/
├── SKILL.md                     (~300-500 lines)
├── references/
│   ├── ARCHITECTURE.md          (~150-250 lines)
│   ├── API-REFERENCE.md         (~120-200 lines)
│   ├── PATTERNS.md              (~100-180 lines)
│   ├── EDGE-CASES.md            (~80-150 lines)
│   ├── ERROR-HANDLING.md        (~80-150 lines)
│   ├── EXAMPLES.md              (~100-180 lines)
│   └── [additional refs...]     (~60-100 lines each)
├── agents/
│   ├── sub-agent-a.md           (~80-150 lines)
│   └── sub-agent-b.md           (~80-150 lines, optional)
├── scripts/
│   ├── setup.sh                 (~30-60 lines)
│   ├── validate.sh              (~30-60 lines)
│   └── cleanup.sh               (~20-40 lines)
├── tests/
│   ├── test-cases.md            (~120-200 lines)
│   ├── fixtures/
│   │   ├── input-a.json
│   │   ├── input-b.yaml
│   │   └── input-c.md
│   └── expected-outputs/
│       ├── report-a.md
│       └── report-b.json
├── docs/
│   ├── USAGE.md                 (~80-150 lines)
│   ├── EXAMPLES.md              (~100-200 lines)
│   └── TROUBLESHOOTING.md       (~60-120 lines)
└── plans/                       (optional)
    └── IMPLEMENTATION.md        (~80-150 lines)
```

### File Descriptions

| File | Lines | Purpose |
|---|---|---|
| SKILL.md | 300-500 | Full orchestration logic, agent invocation, error recovery, phase contracts |
| references/ARCHITECTURE.md | 150-250 | System design, data flow diagrams, component relationships |
| references/API-REFERENCE.md | 120-200 | External APIs used, endpoints, payloads, auth patterns |
| references/PATTERNS.md | 100-180 | Reusable code patterns, templates, decision trees |
| references/EDGE-CASES.md | 80-150 | Known failure modes and how to handle them |
| references/ERROR-HANDLING.md | 80-150 | Error taxonomy, recovery strategies, fallback logic |
| agents/sub-agent-a.md | 80-150 | Instructions for the sub-agent (system prompt, tools, constraints) |
| scripts/setup.sh | 30-60 | Environment preparation before skill runs |
| scripts/validate.sh | 30-60 | Post-run validation of outputs |
| scripts/cleanup.sh | 20-40 | Teardown and temp file removal |
| plans/IMPLEMENTATION.md | 80-150 | Optional: design rationale, alternative approaches considered |

### When to Add `agents/`

Add `agents/` when the skill spawns a Claude sub-agent with its own system prompt, tool access, or conversation loop. Each agent file defines one agent's behavior.

### When to Add `plans/`

Add `plans/` when the skill is complex enough that future maintainers will need context about why design decisions were made. Skip it for straightforward skills.

---

## Tier 6: Ultra-Advanced Orchestrator

**Profile:** 8-12 tools, 7-12 phases, multiple agents, 10-15 reference files, hooks, full enterprise patterns.

```
my-skill/
├── SKILL.md                     (~400-600 lines)
├── references/
│   ├── ARCHITECTURE.md          (~200-350 lines)
│   ├── API-REFERENCE.md         (~150-250 lines)
│   ├── PATTERNS.md              (~150-250 lines)
│   ├── EDGE-CASES.md            (~100-200 lines)
│   ├── ERROR-HANDLING.md        (~100-200 lines)
│   ├── EXAMPLES.md              (~150-250 lines)
│   ├── DATA-MODELS.md           (~100-180 lines)
│   ├── INTEGRATION-GUIDE.md     (~120-200 lines)
│   ├── PERFORMANCE.md           (~80-150 lines)
│   ├── SECURITY.md              (~80-150 lines)
│   └── [additional refs...]     (~60-120 lines each)
├── agents/
│   ├── orchestrator.md          (~150-250 lines)
│   ├── sub-agent-a.md           (~100-180 lines)
│   ├── sub-agent-b.md           (~100-180 lines)
│   └── sub-agent-c.md           (~100-180 lines, optional)
├── scripts/
│   ├── setup.sh                 (~50-100 lines)
│   ├── validate.sh              (~50-100 lines)
│   ├── cleanup.sh               (~30-60 lines)
│   ├── pre-run-checks.sh        (~40-80 lines)
│   └── post-run-report.sh       (~40-80 lines)
├── hooks/
│   ├── pre-tool.sh              (~30-60 lines)
│   └── post-tool.sh             (~30-60 lines)
├── tests/
│   ├── test-cases.md            (~200-350 lines)
│   ├── integration-tests.md     (~100-200 lines)
│   ├── fixtures/
│   │   ├── scenario-a/
│   │   │   ├── input.json
│   │   │   └── expected.md
│   │   └── scenario-b/
│   │       ├── input.yaml
│   │       └── expected.json
│   └── expected-outputs/
│       ├── full-report.md
│       └── summary.json
├── docs/
│   ├── USAGE.md                 (~100-200 lines)
│   ├── EXAMPLES.md              (~150-300 lines)
│   ├── TROUBLESHOOTING.md       (~100-200 lines)
│   ├── CHANGELOG.md             (~50-100 lines)
│   └── CONTRIBUTING.md          (~60-120 lines)
└── plans/
    ├── IMPLEMENTATION.md        (~100-200 lines)
    └── DECISIONS.md             (~80-150 lines)
```

### File Descriptions

| File | Lines | Purpose |
|---|---|---|
| SKILL.md | 400-600 | Full orchestration, circuit breakers, retry logic, handoff contracts |
| references/ARCHITECTURE.md | 200-350 | Full system diagram, component topology, data flows |
| references/DATA-MODELS.md | 100-180 | All data structures, schemas, type definitions |
| references/INTEGRATION-GUIDE.md | 120-200 | How this skill connects to external systems |
| references/SECURITY.md | 80-150 | Auth patterns, secret handling, access control |
| agents/orchestrator.md | 150-250 | Top-level orchestrator agent with full routing logic |
| hooks/pre-tool.sh | 30-60 | Validation before any tool call |
| hooks/post-tool.sh | 30-60 | Logging or side effects after tool calls |
| tests/integration-tests.md | 100-200 | End-to-end tests with real-world scenarios |
| docs/CHANGELOG.md | 50-100 | Version history and breaking changes |
| docs/CONTRIBUTING.md | 60-120 | Guidelines for modifying or extending the skill |
| plans/DECISIONS.md | 80-150 | Architecture decision records (ADRs) |

### When to Add `hooks/`

Add `hooks/` when the skill needs to intercept tool calls for logging, validation, rate limiting, or side effects. Hooks are distinct from scripts — scripts run at setup/teardown, hooks run around every tool call.

### When to Add `integration-tests.md`

Add `integration-tests.md` when the skill touches external APIs, databases, or other skills. Unit tests (test-cases.md) cover logic; integration tests cover wiring.

---

## Tier 7: Skill System

**Profile:** A coordinated pipeline of multiple skills, each with its own tier. One skill calls another. No single SKILL.md at the top level — instead, a README.md describes the system.

```
my-skill-system/
├── README.md                    (~100-200 lines, system overview)
├── skill-a/
│   ├── SKILL.md                 (Tier 2-4 skill)
│   └── references/
│       └── REF-1.md
├── skill-b/
│   ├── SKILL.md                 (Tier 3-5 skill)
│   ├── references/
│   │   ├── REF-1.md
│   │   └── REF-2.md
│   └── scripts/
│       └── process.sh
└── skill-c/
    ├── SKILL.md                 (Tier 4-6 skill)
    ├── references/
    │   ├── ARCHITECTURE.md
    │   └── PATTERNS.md
    ├── scripts/
    │   ├── setup.sh
    │   └── validate.sh
    └── agents/
        └── processor.md
```

### Example: Three-Skill Pipeline

```
content-pipeline/
├── README.md                    (pipeline overview, data flow diagram)
├── skill-a-researcher/
│   ├── SKILL.md                 (Tier 3: web research, 3 tools)
│   └── references/
│       └── SEARCH-PATTERNS.md
├── skill-b-writer/
│   ├── SKILL.md                 (Tier 4: content generation, 5 tools)
│   ├── references/
│   │   ├── STYLE-GUIDE.md
│   │   └── TONE-RULES.md
│   └── scripts/
│       └── format.sh
└── skill-c-publisher/
    ├── SKILL.md                 (Tier 5: multi-platform publish, 7 tools)
    ├── references/
    │   ├── PLATFORM-APIS.md
    │   └── ERROR-HANDLING.md
    ├── scripts/
    │   ├── setup.sh
    │   └── validate.sh
    └── agents/
        └── publisher-agent.md
```

### README.md Structure for Tier 7

```markdown
---
system: content-pipeline
tier: 7
skills: [skill-a-researcher, skill-b-writer, skill-c-publisher]
---

# Content Pipeline System

## Overview
Three-skill pipeline: research → write → publish.

## Data Flow
skill-a-researcher → [research-output.md] → skill-b-writer → [draft.md] → skill-c-publisher

## Skill Tiers
| Skill | Tier | Tools | Purpose |
|---|---|---|---|
| skill-a-researcher | 3 | 3 | Gathers research from web |
| skill-b-writer | 4 | 5 | Writes content from research |
| skill-c-publisher | 5 | 7 | Publishes to multiple platforms |

## Invocation Order
1. Run skill-a-researcher with topic input
2. Pass output to skill-b-writer
3. Pass draft to skill-c-publisher

## Shared State
All skills read/write from shared output/ directory.
```

---

## Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Skill directory | kebab-case | `content-pipeline`, `file-generator` |
| SKILL.md | Always uppercase | `SKILL.md` |
| README.md (Tier 7 only) | Always uppercase | `README.md` |
| Reference files | SCREAMING-KEBAB.md | `API-REFERENCE.md`, `ERROR-HANDLING.md` |
| Script files | kebab-case.sh | `setup.sh`, `pre-run-checks.sh` |
| Agent files | kebab-case.md | `orchestrator.md`, `sub-agent-a.md` |
| Test files | kebab-case.md | `test-cases.md`, `integration-tests.md` |
| Fixture directories | kebab-case | `scenario-a/`, `sample-inputs/` |
| Fixture files | kebab-case with extension | `input.json`, `expected-output.md` |
| Plans files | SCREAMING-KEBAB.md | `IMPLEMENTATION.md`, `DECISIONS.md` |
| Hook scripts | action-timing.sh | `pre-tool.sh`, `post-run-report.sh` |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| All logic in one 800-line SKILL.md | Unreadable, hard to maintain | Split into references/ and phases |
| No tests/ directory for Tier 3+ | Can't verify behavior | Add test-cases.md with 4+ scenarios |
| Fixtures checked in but not referenced | Clutters repo | Either reference them in tests or delete them |
| agents/ with no system prompt | Agent has no guidance | Each agent file must define role, tools, constraints |
| scripts/ as .py files | Shell portability assumed | Use .sh or explicitly document the interpreter |
| references/ files that duplicate SKILL.md | Redundant content | References extend SKILL.md, not repeat it |
| Tier 7 system with no README.md | No entry point | Always write README.md for multi-skill systems |
| Hook scripts that exit 1 on warnings | Blocks valid runs | Hooks should exit 1 only on hard failures |
| plans/ that describe implementation steps | That belongs in tasks/ | plans/ = rationale and decisions only |
| SKILL.md with no frontmatter | No machine-readable metadata | Always include frontmatter with name, tier, tools |

---

## Decision Tree: When to Add Each Directory

```
references/
  Add if:   SKILL.md exceeds 150 lines OR skill needs reusable lookup tables
  Skip if:  Tier 1 with under 100 lines of static content

tests/
  Add if:   Tier 2+ and skill produces verifiable output
  Skip if:  Pure reference skill (Tier 1) with no execution

tests/fixtures/
  Add if:   Test cases require specific input files to reproduce
  Skip if:  Tests can be described without needing sample files

tests/expected-outputs/
  Add if:   Skill produces structured output (reports, code, JSON)
  Skip if:  Output is conversational or unpredictable

scripts/
  Add if:   Skill needs setup, validation, or cleanup steps
  Skip if:  Tier 1-3 with no external dependencies

hooks/
  Add if:   Tier 6 skill needing per-tool-call interception
  Skip if:  Any tier below 6 (use scripts/ for setup/teardown instead)

agents/
  Add if:   Tier 5+ skill delegates work to a sub-agent with its own prompt
  Skip if:  Skill uses tools directly without spawning sub-agents

docs/
  Add if:   Skill will be shared, published, or used by others
  Skip if:  Internal-only skill used by one team

plans/
  Add if:   Tier 5+ skill with non-obvious architecture decisions
  Skip if:  Straightforward skills where the code explains itself

README.md (root)
  Add if:   Tier 7 system with multiple sub-skills
  Never add to single-skill directories (use SKILL.md instead)
```

---

## Quick Tier Reference

| Tier | Name | Lines | Key Files |
|---|---|---|---|
| 1 | Simple Knowledge | 50-150 | SKILL.md only |
| 2 | Basic Workflow | 100-200 | SKILL.md, tests/ |
| 3 | Intermediate | 150-300 | SKILL.md, references/ (1-2), tests/ |
| 4 | Advanced | 200-400 | SKILL.md, references/ (3-5), tests/, docs/ |
| 5 | Very Advanced | 300-500 | + agents/, scripts/, plans/ |
| 6 | Ultra-Advanced | 400-600 | + hooks/, integration-tests/, full docs/ |
| 7 | Skill System | varies | README.md + sub-skill directories |
