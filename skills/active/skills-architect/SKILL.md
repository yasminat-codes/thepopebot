---
name: skills-architect
description: >-
  Design, create, migrate, and audit production-ready Claude Code skills with expert-guided
  interviews, auto-detected tiers, and enforced progressive disclosure.
  Use PROACTIVELY when user says "create a skill", "build a skill", "make a skill",
  "design a skill", "write a skill", "architect a skill", "new skill for", "skill that does",
  "upgrade a skill", "migrate a skill", "improve a skill", "fix my skill", "decompose a skill",
  "audit my skills", "skill health check", "score my skills", "skill quality",
  or mentions SKILL.md, skill creation, skill development, skill engineering, skill system,
  skill pipeline, multi-skill workflow.
  Also use when user opens SKILL.md files or works in .claude/skills/ directories.
  Part of the yasmine-os skill development system.
allowed-tools: Read Write Edit Bash Grep Glob Task TodoWrite AskQuestion WebSearch WebFetch
metadata:
  author: yasmine
  version: 1.1.0
  category: meta-skill
  tier: 6
---

# Skills Architect v1.0.0
<!-- ultrathink -->

> The definitive Claude Code skill creation engine. Expert-guided interviews,
> auto-detected tiers, enforced progressive disclosure, and production-grade validation.

## The Iron Law

```
SKILL.md LINE LIMITS (NON-NEGOTIABLE):
├── Tier 1-5: Maximum 500 lines
├── Tier 6 Orchestrators: Maximum 600 lines
├── Over limit: VALIDATION FAILURE → auto-refactor into references/
└── SKILL.md = navigation hub ONLY. Content lives in references/

PROGRESSIVE DISCLOSURE (NON-NEGOTIABLE):
├── Every references/ file needs a → See directive in SKILL.md
├── Every scripts/ file needs a Run: directive with trigger condition
├── More references = BETTER (10 small files > 3 large ones)
└── Reference files: 100-400 lines each (max 400)
```

## Modes

Detect mode from $ARGUMENTS or first AskUserQuestion:

| Mode | Triggers | Description |
|------|----------|-------------|
| **CREATE** | "create", "build", "new", "make", "design" | Full 10-phase interview → skill |
| **MIGRATE** | "migrate", "upgrade", "improve", "fix", "decompose" | Upgrade existing skill to best practices |
| **AUDIT** | "audit", "check", "health", "score", "review" | Batch quality report for all skills |
| **SYSTEM** | "system", "pipeline", "chain", "multi-skill" | Multi-skill pipeline design |

→ See references/MIGRATION-MODE.md when MIGRATE mode is detected
→ See references/AUDIT-MODE.md when AUDIT mode is detected
→ See references/SKILL-SYSTEMS.md when SYSTEM mode is detected

If mode is not CREATE, follow the referenced document. Below is the CREATE workflow.

---

## Quality Gates

| Phase | Gate | Blocker? |
|-------|------|----------|
| 0. Initialize | Codebase scan complete | YES |
| 1-5. Interview | All rounds answered via AskUserQuestion | YES |
| 6. Tier Detection | User confirms auto-detected tier | YES |
| 7. Architecture | Approval gate passed | YES |
| 8. Generation | All files written (dry-run or final) | YES |
| 9. Validation | 5/5 checks pass | YES |
| 10. Delivery | Creation log saved | NO |

**IF ANY GATE FAILS → STOP → FIX → RE-RUN → CONTINUE**

---

## Phase 0: Initialize, Research & Codebase Scan

→ See references/PHASE-0-CODEBASE-SCAN.md for detailed scan procedures
→ See references/SKILLS-SPECIFICATION-RESEARCH.md for docs loading and live fetch procedures

1. **TodoWrite:** Initialize ALL phases (0-10) as pending
2. **Load memory:** Read ~/.claude/projects/-Users-yasmineseidu/memory/MEMORY.md
   - Look for `## skills-architect` section for past preferences
   - Apply saved preferences as defaults in upcoming questions
3. **Load skills specification docs** (MANDATORY — do this BEFORE any interview):
   - Read files in `docs/claude-skills/` directory if present in project
   - Key files: `00-overview.md`, `01-frontmatter-complete.md`, `02-description-engineering.md`,
     `03-tools-and-permissions.md`, `07-folder-structure.md`, `08-orchestrator-skills.md`
   - These contain the LATEST spec — they override any stale knowledge
4. **Web-fetch latest Anthropic skill docs** (for framework-specific skills):
   - WebFetch `https://docs.anthropic.com/en/docs/claude-code/skills` → extract current spec
   - WebFetch `https://docs.anthropic.com/en/docs/claude-code/hooks` → extract hook events
   - Store any spec changes or new fields discovered
5. **Mandatory codebase scan:**
   - Glob for `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml` → detect language/framework
   - Glob for `.claude/skills/` or `~/.claude/skills/` → count existing skills, note naming patterns
   - Read `CLAUDE.md` if exists → extract conventions, tool preferences
   - Glob for test files (`**/test_*.py`, `**/*.test.ts`) → detect test framework
   - Read `tsconfig.json` or `ruff.toml` if exists → detect style preferences
6. **Store all findings** (docs spec + web fetch + codebase scan) as internal context

**Gate:** Docs loaded + scan complete. Proceed to Phase 1.

---

## Phase 1: Interview Round 1 — Identity (4-6 questions)

→ See references/QUESTION-BANK.md §1 for Round 1 question specifications

All questions MUST use the AskUserQuestion tool. Every question has a (Recommended) first option
with expert reasoning. Provide 2-4 options per question plus "Other" (automatic).

**Round 1 covers:** What the skill does, who it's for, what triggers it, naming.

Question selection logic:
- **Always ask:** Q1.1 (purpose/problem), Q1.2 (skill name), Q1.3 (trigger context), Q1.4 (target users)
- **If codebase scan found frameworks:** Add Q1.5 (framework-specific behavior?)
- **If existing skills found:** Add Q1.6 (relationship to existing skills?)

After Round 1, you should know: the skill's purpose, name, primary triggers, and audience.

---

## Phase 2: Interview Round 2 — Behavior (6-8 questions)

→ See references/QUESTION-BANK.md §2 for Round 2 question specifications

**Round 2 covers:** Workflow shape, tool needs, parallelism, outputs, user interaction.

Question selection logic:
- **Always ask:** Q2.1 (workflow type: linear/branching/interview/orchestrator), Q2.2 (tools needed),
  Q2.3 (user interaction style: silent/guided/interview), Q2.4 (output artifacts)
- **If workflow has 3+ phases:** Add Q2.5 (phase dependencies), Q2.6 (parallel opportunities)
- **If tool list includes Bash:** Add Q2.7 (script needs: validation/deployment/CI)
- **If tool list includes Task:** Add Q2.8 (subagent design: types, models, parallelism)

After Round 2, you should know: workflow shape, tools, phases, and interaction model.

---

## Phase 3: Interview Round 3 — Architecture (4-6 questions)

→ See references/QUESTION-BANK.md §3 for Round 3 question specifications

**Round 3 covers:** Context isolation, model selection, hooks, progressive disclosure depth.

Question selection logic:
- **Always ask:** Q3.1 (context: fork vs inline), Q3.2 (model override), Q3.3 (hooks needed?)
- **If hooks needed:** Add Q3.4 (which hook events), Q3.5 (blockOnFailure decisions)
- **If tier likely 5+:** Add Q3.6 (custom agents needed?)

After Round 3, you should know: context mode, model, hook strategy, agent needs.

---

## Phase 4: Interview Round 4 — Quality (3-5 questions)

→ See references/QUESTION-BANK.md §4 for Round 4 question specifications

**Round 4 covers:** Quality gates, error handling, validation, approval gates.

Question selection logic:
- **Always ask:** Q4.1 (quality gates: which phases block?), Q4.2 (error recovery strategy),
  Q4.3 (approval gates: before side effects?)
- **If tier 4+:** Add Q4.4 (circuit breaker patterns), Q4.5 (retry with backoff?)

After Round 4, you should know: gate strategy, error handling, approval workflow.

---

## Phase 5: Interview Round 5 — Polish (3-4 questions)

→ See references/QUESTION-BANK.md §5 for Round 5 question specifications

**Round 5 covers:** Memory integration, learning, complementary skills, testing.

Question selection logic:
- **Always ask:** Q5.1 (memory: save preferences between runs?), Q5.2 (complementary skills?)
- **If tier 3+:** Add Q5.3 (pressure test scenarios: what should the skill resist?)
- **If skill system:** Add Q5.4 (pipeline position: step N of M)
- **If framework-specific:** Auto-fetch current docs via WebFetch (references/LIVE-DOCS.md pattern)

After Round 5, you should know: memory strategy, testing approach, ecosystem position.

---

## Phase 6: Tier Detection & CSO Engineering

→ See references/TIER-DETECTION.md for the complete auto-detection algorithm
→ See references/CSO-ENGINE.md for description generation and 10-point scoring rubric

1. **Auto-detect tier** from accumulated interview answers:

| Signal | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
|--------|----|----|----|----|----|----|-----|
| Tools | 0 | 2-3 | 3-5 | 5+ | 5++ | 8+ | per-skill |
| Phases | 1 | 1-2 | 2-4 | 5+ | 5++ | 8+ | N×skills |
| Parallel | — | — | — | some | heavy | heavy | cross-skill |
| Hooks | — | — | — | basic | complex | complex | shared |
| Agents | — | — | — | — | yes | yes | per-skill |
| References | 0 | 0 | 1-2 | 3-5 | 5-10 | 10-15 | per-skill |

   Present: "Based on your answers, this is a **Tier N** skill. Here's why: [reasoning]"
   Use AskUserQuestion to confirm or override.

2. **Generate CSO description** (target 10/10):
   → See references/CSO-ENGINE.md for the formula, rubric, and iteration procedure
   - Apply CSO formula: `[Action verb] [what] with [tech]. Use PROACTIVELY when [5+ triggers]...`
   - Score against 10-point rubric (each point documented in CSO-ENGINE.md)
   - Iterate until 9+/10
   - Present score breakdown to user for approval

3. **Auto-decide frontmatter** (10 fields automatic, 4 asked):
   → See references/FRONTMATTER-REFERENCE.md for complete field specifications
   → See references/TOOLS-REFERENCE.md for tier-based tool patterns
   - Auto-set: name, description, allowed-tools, metadata, license, compatibility,
     user-invocable, argument-hint, agent type (if fork)
   - Ask via AskUserQuestion: context (fork/inline), model override,
     disable-model-invocation, hooks configuration

**Gate:** User confirms tier + approves CSO description (9+/10).

---

## Phase 7: Expert Suggestions & Architecture Design

→ See references/PROACTIVE-SUGGESTIONS.md for the complete suggestion engine
→ See references/TIER-STRUCTURES.md for all 7 tier folder structures with examples
→ See references/FRONTMATTER-REFERENCE.md for field specifications
→ See references/HOOKS-PATTERNS.md for hook pattern recommendations
→ See references/AGENT-GENERATION.md for custom agent design patterns

1. **Generate proactive expert suggestions** (minimum 5 categories):
   - Hooks the user didn't ask for but should have
   - Pressure test scenarios they haven't considered
   - Memory integration patterns that fit their use case
   - CSO anti-patterns to avoid in their description
   - Complementary skills that would pair well with this one
   - Circuit breakers (if external services detected)
   - Approval gates (if side effects detected)
   - Learning patterns (if the skill will be used repeatedly)

   Present suggestions via AskUserQuestion (multiSelect: true) — user picks which to include.

2. **Design folder structure:**
   - Select tier-appropriate structure from references/TIER-STRUCTURES.md
   - Calculate complete file list with estimated line counts per file
   - Generate tree diagram showing every file that will be created

3. **Generate dependency analysis:**
   → See references/SKILL-SYSTEMS.md §dependencies for dependency wiring
   - Detect dependencies from interview answers
   - Check if dependencies exist in target directory
   - Warn if missing, suggest creation order

4. **APPROVAL GATE:**
   Use AskUserQuestion to present the complete architecture:
   - Detected tier + reasoning
   - CSO description + score breakdown
   - Complete frontmatter (all fields)
   - Folder tree with line estimates
   - Expert suggestions (accepted ones)
   - Dependencies (if any)
   Options: **Approve** / **Modify** / **Cancel**
   If Modify → ask what to change → revise → re-present

**Gate:** Architecture approved. Proceed to generation.

---

## Phase 8: File Generation — Agent Team Deployment

→ See references/AGENT-TEAM-DEPLOYMENT.md for fan-out parallel agent coordination
→ See references/TEMPLATES-INDEX.md for template selection logic
→ See references/PROGRESSIVE-DISCLOSURE.md for directive generation rules
→ See references/HOOKS-PATTERNS.md when generating hook scripts
→ See references/AGENT-GENERATION.md when generating custom agent YAML
→ See references/ORCHESTRATION-PATTERNS.md when creating orchestrator skills

1. **Determine output path:**
   - Check for `.claude/skills/` in project → use if exists
   - Check for `~/.claude/skills/` → use if project path doesn't exist
   - If ambiguous (both exist or neither), ask via AskUserQuestion
   - Write to `.claude/preview/skills-architect/` first (dry-run)

2. **Create skill directory** and all subdirectories (references/, scripts/, templates/)

3. **Deploy agent team (fan-out parallel)** — dispatch ALL writing agents in ONE message:

   For **Tier 1-3** (simple skills, few files):
   - Agent A: Write SKILL.md (from template + interview data)
   - Agent B: Write README.md + CHANGELOG.md
   - (2 agents, fast completion)

   For **Tier 4-5** (advanced skills, multiple references):
   - Agent A: Write SKILL.md (from template + interview data + all directives)
   - Agent B: Write references batch 1 (first half of reference files)
   - Agent C: Write references batch 2 (second half of reference files)
   - Agent D: Write scripts + README.md + CHANGELOG.md
   - (4 agents, parallel completion)

   For **Tier 6-7** (orchestrators + systems, many files):
   - Agent A: Write SKILL.md (orchestrator template + directives)
   - Agent B: Write references batch 1 (phase/workflow references)
   - Agent C: Write references batch 2 (patterns/quality references)
   - Agent D: Write references batch 3 (advanced/integration references)
   - Agent E: Write scripts (validation, hooks, utilities) + chmod +x
   - Agent F: Write agent YAML files + README.md + CHANGELOG.md
   - (6 agents, maximum parallelism)

   Each agent receives:
   - Complete interview data (all 5 rounds)
   - Detected tier + CSO description + frontmatter
   - Folder structure plan with line estimates
   - Template to use (from templates/ directory)
   - Specific files assigned to this agent
   - Progressive disclosure directives relevant to its files

   Use `Task(subagent_type: "general-purpose", model: "sonnet", run_in_background: true)`
   for all agents. Dispatch ALL in ONE message for true parallel execution.

4. **Wait for all agents to complete**, collect results
5. **Interactive preview** (Tier 5+ only):
   - Present file-by-file summary with line counts
   - For each file, show first 10-15 lines as preview
   - AskUserQuestion: Approve all / Review specific files / Regenerate specific files
6. **On approval:** Move from preview to final location, chmod +x scripts

**Gate:** All files written successfully.

---

## Phase 9: Validation & Self-Audit

→ See references/VALIDATION-ENGINE.md for 5-point validation procedures
→ See references/AUDIT-MODE.md for the self-audit procedure
→ Run: scripts/validate-skill.sh $SKILL_PATH (exit 0 = all checks pass)

**Step 1 — 5-point validation** (ALL must pass):

| # | Check | Pass Criteria | Auto-Fix |
|---|-------|--------------|----------|
| 1 | Line count | SKILL.md ≤ 500 (600 for T6) | Move excess to references/ |
| 2 | YAML parse | Frontmatter parses cleanly | Fix syntax |
| 3 | Orphan check | Every reference has a directive | Add missing directives |
| 4 | Directive completeness | Every directive has trigger condition | Add conditions |
| 5 | CSO score | Description ≥ 9/10 | Iterate description |

If any check fails → auto-fix → re-validate → present fix report.

**Step 2 — Post-creation self-audit** (run AUDIT mode on own output):
- Run the same audit scoring from references/AUDIT-MODE.md on the just-created skill
- Calculate 100-point health score (line count 20 + CSO 30 + frontmatter 20 + disclosure 20 + orphans 10)
- Target: 85+ (Excellent). If below 85, identify and fix the weakest areas.
- Present health score to user in delivery report

**Gate:** 5/5 validation checks pass AND health score ≥ 85.

---

## Phase 10: Testing & Delivery

→ See references/TESTING-GENERATION.md for pressure test patterns and templates
→ See references/MEMORY-INTEGRATION.md for creation logging procedures

1. **Generate pressure tests** (Tier 3+):
   - 3-5 scenarios in the created skill's references/TESTING.md
   - Each scenario: setup description, pressure type (time/sunk-cost/authority),
     expected correct behavior, pass/fail criteria
   - Can be run later with writing-skills or testing-skills-with-subagents

2. **Versioning:**
   - Set metadata.version: 1.0.0 in created skill
   - Create CHANGELOG.md with initial entry
   - If migration: bump version, document changes

3. **Save creation log to memory:**
   Append to ~/.claude/projects/-Users-yasmineseidu/memory/MEMORY.md under `## skills-architect`:
   ```
   - [date]: Created [name] (Tier [N], [X] tools, [Y] refs, [Z] lines, CSO [score]/10)
   ```

4. **Delivery report:**
   - Files created with line counts
   - CSO description + score
   - Validation results (5/5)
   - Expert suggestions included
   - Next steps: test with writing-skills, iterate, share

---

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "SKILL.md is only 520 lines, close enough" | 500 is the limit. Move 20 lines to references/. |
| "This reference is only used once, inline it" | Progressive disclosure. Even once-used content belongs in references/. |
| "The description is good enough at 7/10" | 9+ minimum. Iterate. Activation rates drop 40% below 8. |
| "Skip the codebase scan, user told me what they need" | Scan catches what users forget. Always scan. |
| "This skill is simple, skip the approval gate" | Every skill gets an approval gate. Non-negotiable. |
| "Tests can come later" | Generate test scenarios now. Testing later means testing never. |
