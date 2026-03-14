# Skill Systems - Multi-Skill Pipeline Design

## What Is a Skill System

A Skill System is two or more skills designed to work as a sequential pipeline, where the output of
one skill becomes the input of the next. Skills in a system are not standalone — they are wired
together through shared outputs, description references, and explicit handoff instructions.

Example: A cold email system with four skills in sequence:
```
cold-email-research-validator
        ↓
cold-email-copywriter
        ↓
cold-email-copy-critic
        ↓
cold-email-humanizer
```

Each skill knows it is part of this pipeline. Each description tells the user what to invoke next.
The output of each skill is the input contract of the next.

---

## System Design Workflow

### Step 1: Define the Pipeline

Write out the full sequence before creating any files:
- What is the starting trigger?
- What is the final output?
- What are the intermediate steps?
- What order must they run in? (some steps may be optional or conditional)

Name the system. The system name is used in folder structure, README, and skill descriptions.

Example pipeline definition:
```
System: cold-email
Steps:
  1. cold-email-research-validator — validate niche + pain points
  2. cold-email-copywriter — write first draft
  3. cold-email-copy-critic — score and flag issues
  4. cold-email-humanizer — rewrite to sound human
Input (Step 1): niche, target role, company size
Output (Step 4): final cold email copy
```

### Step 2: Identify Per-Skill Tiers

Each skill in the pipeline gets its own tier. Skills in the same system can have different tiers.

Common pattern: early-stage research skills are Tier 4-5; later-stage generation skills are Tier 5-6.
Assign tier based on the individual skill's complexity, not the system's.

### Step 3: Design Data Flow Between Skills

Define the exact file or data format passed between skills:

```
Step 1 Output → Step 2 Input:
  File: research-output.md
  Contains: niche summary, pain points (bulleted), 3 sample prospects

Step 2 Output → Step 3 Input:
  File: email-draft.md
  Contains: subject line, body (200-300 words), CTA

Step 3 Output → Step 4 Input:
  File: email-critique.md
  Contains: scored draft, flagged lines, rewrite suggestions

Step 4 Output:
  File: email-final.md
  Contains: final subject line, final body, usage notes
```

Document this in a shared data contract section of the system README.

### Step 4: Wire Descriptions

Every skill in a system must reference the system in its description. Use this pattern:

```
Step [N] of [total] in the [system-name] pipeline.
Part of [system-name] with [list all other skills in the pipeline].
Invoke this skill [when / after what condition].
Pass the output to [next-skill-name].
```

This wiring ensures Claude can navigate the pipeline without explicit user instructions.

### Step 5: Create Each Skill Individually

Create skills one at a time using the standard creation workflow. Do not batch-create; each skill
needs its own SKILL.md, references/, and validation.

Use the system name as a prefix in the skill folder name:
```
.claude/skills/
  cold-email-research-validator/
  cold-email-copywriter/
  cold-email-copy-critic/
  cold-email-humanizer/
```

### Step 6: Generate System README

After all individual skills are created, generate a system-level README at:
```
.claude/skills/[system-name]/README.md
```

Read: SKILL-SYSTEMS.md#system-readme-template

### Step 7: Validate Cross-Skill References

After all skills are written, run a cross-reference check:
- Every skill's description mentions the system name
- Every skill except the last names the next skill to invoke
- Every skill except the first names the prerequisite skill
- Output files named in Step 3 are referenced in both the producing and consuming skill
- No circular references (skill A → skill B → skill A)

Report any broken references as validation failures before marking the system complete.

---

## Description Wiring Pattern

Use this exact template in every skill's description that is part of a system:

```
PROACTIVELY invoke this skill when the user asks to [do X].
Step [N] of [total] in the [system-name] pipeline.
Part of [system-name] with [skill-1], [skill-2], [skill-3].
Takes [input description] as input.
Produces [output description].
Invoke this skill [first / after [prerequisite-skill]], then invoke [next-skill] with the output.
```

If it is the last skill in the pipeline:
```
This is the final step. Output is ready for direct use.
```

---

## Shared References Pattern

When multiple skills in a system share the same reference content (e.g., tone guidelines,
format standards, domain vocabulary), create a shared references directory:

```
.claude/skills/[system-name]/
  shared/
    TONE-GUIDELINES.md
    TARGET-PERSONA.md
    FORMAT-STANDARDS.md
  cold-email-copywriter/
    SKILL.md       # reads: ../shared/TONE-GUIDELINES.md
  cold-email-humanizer/
    SKILL.md       # reads: ../shared/TONE-GUIDELINES.md
```

Each skill that uses a shared reference must include it in its SKILL.md:
```
Read: ../shared/TONE-GUIDELINES.md
```

Do not duplicate shared content in individual skill references. Single source of truth.

---

## Dependency Detection and Validation

Before marking a system complete, verify:

1. All skills listed in a pipeline description actually exist as SKILL.md files
2. All output files named in data contracts are written in the producing skill
3. All input files named in data contracts are read in the consuming skill
4. No skill in the pipeline depends on a skill not in the pipeline (hidden dependencies)
5. The pipeline has exactly one entry point (no ambiguous starting skills)
6. The pipeline has exactly one terminal point (unless it has a conditional branch)

---

## System-Level README Template

```markdown
# [System Name] — [N]-Skill Pipeline

## What This System Does
[1-2 sentence description of the end-to-end outcome]

## Pipeline

[skill-1] → [skill-2] → [skill-3] → [skill-4]

## Skills

| Step | Skill | Tier | Input | Output |
|------|-------|------|-------|--------|
| 1 | [skill-1] | 4 | [what] | [what] |
| 2 | [skill-2] | 5 | [what] | [what] |
| 3 | [skill-3] | 5 | [what] | [what] |
| 4 | [skill-4] | 4 | [what] | [what] |

## Data Contracts

### Step 1 → Step 2
File: `research-output.md`
Contains: [list fields]

### Step 2 → Step 3
File: `email-draft.md`
Contains: [list fields]

### Step 3 → Step 4
File: `email-critique.md`
Contains: [list fields]

## Shared References
- `shared/TONE-GUIDELINES.md` — used by Step 2, Step 4
- `shared/TARGET-PERSONA.md` — used by Step 1, Step 2

## Usage
Start with: `/[skill-1]`
Follow the INVOKE NEXT instructions in each skill.
```

---

## Real-World System Examples

### Cold Email System (4 Skills)
```
cold-email-research-validator → cold-email-copywriter → cold-email-copy-critic → cold-email-humanizer
```
Input: niche + target role. Output: polished cold email copy.
Shared: tone guidelines, persona definition.

### SDK Agent Build (10 Skills)
```
sdk-agent-researcher → sdk-agent-requirements-brainstormer → sdk-agent-architecture-designer
  → sdk-agent-tool-builder → sdk-agent-implementer → sdk-agent-api-builder
  → sdk-agent-tester-validator → sdk-agent-security-reviewer
  → sdk-agent-production-builder → sdk-agent-documentation-generator
```
Input: agent concept. Output: production-deployed agent with full documentation.

### Deploy Pipeline (3 Skills)
```
deploy-docker-configurator → deploy-cicd-pipeline-builder → deploy-readiness-validator
```
Input: project root path. Output: Docker + CI/CD config, validated and ready to ship.

### Reddit Research (4 Skills)
```
reddit-niche-finder → reddit-pain-extractor → niche-validator → niche-offer-architect
```
Input: broad niche topic. Output: validated offer built from real Reddit pain points.

---

## Skill System Folder Structure (Tier 7)

When a system has 4+ skills and shared references, use the Tier 7 folder layout:

```
.claude/skills/[system-name]/
  README.md                     # System overview and pipeline diagram
  shared/
    TONE-GUIDELINES.md
    DATA-CONTRACTS.md
  [skill-1]/
    SKILL.md
    references/
  [skill-2]/
    SKILL.md
    references/
  [skill-3]/
    SKILL.md
    references/
  [skill-4]/
    SKILL.md
    references/
```

For systems with fewer than 4 skills or no shared content, keep skills as independent folders.
The system README is optional for 2-skill pipelines but required for 4+.

---

## Anti-Patterns

**Circular dependencies**
Skill A's description says "invoke skill B next." Skill B's description says "invoke skill A next."
Never create loops. Pipelines are directional only.

**Missing handoffs**
A skill produces output but the next skill does not reference what to read. The user is left
guessing what to pass. Every skill except the terminal one must name the next skill explicitly.

**Inconsistent naming**
Skills in the same system use different naming conventions: `email-writer`, `EmailCritic`,
`humanize-emails`. Use one consistent prefix for all skills in a system.

**Hidden dependencies**
A skill in the pipeline silently requires a file or context that is not produced by the preceding
skill. All dependencies must be named in the data contracts.

**God skill**
One skill tries to do everything the pipeline should do. If a skill is over 350 lines and covers
multiple distinct phases, it should be split into separate pipeline steps.
