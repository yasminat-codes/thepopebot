# Migration Mode - Upgrading Existing Skills to Best Practices

## Overview

Migration mode takes an existing skill and upgrades it to current best practices without breaking its behavior.
Run when a skill fails audit, has low health score, or was written before current standards.

---

## Migration Workflow

### Step 1: Read Existing SKILL.md

Load the full content of the target SKILL.md. Extract:
- Current line count
- Frontmatter fields present/missing
- Whether references/ directory exists
- Phase structure (numbered phases or flat prose)
- Any existing hooks or quality gates
- Current version (if any)

### Step 2: Analyze Against Best Practices

Run the 5-point check against the current skill:

**a. Line Count**
- Tier 1-3: max 50 lines
- Tier 4-5: max 150 lines
- Tier 6+: max 350 lines
- Flag every phase or section over 30 lines as an extraction candidate

**b. CSO Score (0-10)**
Score the skill's description section:
- Does it have a PROACTIVELY trigger? (+3)
- Does it name input/output clearly? (+2)
- Does it describe what changes in the world? (+2)
- Does it reference related skills? (+1)
- Is it under 5 sentences? (+1)
- Does it use active voice? (+1)

**c. Frontmatter Completeness**
Required fields: `name`, `description`, `version`, `tier`, `inputs`, `outputs`
Optional but scored: `hooks`, `tags`, `requires`

**d. Progressive Disclosure Compliance**
Check if long phases are inline vs. extracted to references/.
Any phase >30 lines that is inline is a progressive disclosure violation.

**e. Orphan Reference Check**
If references/ exists, verify every file in references/ is linked from SKILL.md.
Unlinked files are orphans.

### Step 3: Generate Migration Plan

Produce a structured plan before touching any files:

```
MIGRATION PLAN: [skill-name]
Current version: 1.0 → Target version: 1.1

ISSUES FOUND:
1. [CRITICAL] Line count: 480 lines (limit: 350) — extract 3 phases
2. [HIGH] CSO score: 4/10 — missing PROACTIVELY trigger, no output description
3. [MEDIUM] No version field in frontmatter
4. [LOW] Phase 3 (45 lines) can be extracted to references/PHASE-3.md

PLANNED CHANGES:
- Extract Phase 2 → references/PHASE-2.md (saves ~60 lines)
- Extract Phase 4 → references/PHASE-4.md (saves ~80 lines)
- Rewrite description with PROACTIVELY trigger
- Add version: "1.1" to frontmatter
- Add CHANGELOG entry
```

### Step 4: Present Plan With Before/After Comparison

Show the user what will change before writing any files.

Before (CSO example):
```
This skill builds API integrations.
```

After (CSO example):
```
PROACTIVELY invoke this skill when the user asks to connect to an external API,
add a third-party service, or build an integration layer. Takes an API name and
target codebase as input. Produces a working integration module with error handling,
rate limiting, and tests. Part of the build-pipeline with spec-writer and test-generator.
```

**Do not proceed until the user approves the plan.**

### Step 5: Execute Migration

On approval, apply changes in this order:

1. Create references/ directory if it does not exist
2. Extract identified phases to references/PHASE-N.md files
3. Extract scripts to scripts/
4. Extract examples to examples/
5. Replace extracted content in SKILL.md with `Read: references/PHASE-N.md`
6. Rewrite description section with improved CSO
7. Add or fix all frontmatter fields
8. Add skill-scoped hooks if missing
9. Add quality gates where appropriate

### Step 6: Bump Version and Update CHANGELOG

Apply version bump according to rules below, then append to CHANGELOG:

```markdown
## CHANGELOG

### v1.1 (2026-02-28)
- Extracted Phase 2 and Phase 4 to references/ (progressive disclosure)
- Rewrote description with PROACTIVELY trigger and output description
- Added version field to frontmatter
- Added hooks: pre-execution validation

### v1.0 (original)
- Initial skill
```

### Step 7: Validate Migrated Skill

Run 5-point check again. All items must pass:
- Line count within tier limit
- CSO score >= 7/10
- All required frontmatter fields present
- No inline phases over 30 lines
- No orphan references

Report pass/fail for each check. If any fail, loop back to Step 5.

---

## Common Migration Patterns

### Monolithic to Progressive Disclosure

**Problem:** Everything is in SKILL.md, file is 400+ lines.

**Fix:**
1. Identify phases that are self-contained chunks of instructions
2. Move each phase >30 lines to `references/PHASE-N.md`
3. Replace with a single line: `Read: references/PHASE-N.md`
4. Repeat for error handling, scripts, examples

**Result:** SKILL.md drops to under 150 lines; all content preserved in references/

---

### Missing CSO to PROACTIVELY Triggers

**Problem:** Description is a single flat sentence. Claude does not know when to invoke the skill.

**Fix:** Rewrite description using the CSO formula:
- **C**ontext: When does this apply? (PROACTIVELY invoke when...)
- **S**tate change: What does it do? (Produces X from Y)
- **O**rchestration: How does it relate to others? (Part of X pipeline with skill-a, skill-b)

---

### No Hooks to Skill-Scoped Hooks

**Problem:** Skill has no pre/post execution validation. Bad inputs cause confusing failures.

**Fix:** Add a `hooks` section to frontmatter and a Hooks section to the skill body:

```yaml
hooks:
  pre_execution:
    - validate_inputs
  post_execution:
    - verify_outputs_exist
```

Then document what each hook checks in a Hooks section of SKILL.md.

---

### Missing Quality Gates to Blocking Gates

**Problem:** Skill proceeds even when outputs are missing or tests fail.

**Fix:** Add explicit STOP instructions:

```
QUALITY GATE — BLOCKING:
- Run: pytest tests/ -q
- If any tests fail: STOP. Do not proceed to next phase. Report failures to user.
- Only continue when all tests pass.
```

---

### No Versioning to Metadata + CHANGELOG

**Problem:** No version field, no change history.

**Fix:**
1. Add `version: "1.0"` to frontmatter (treat current state as 1.0)
2. Create CHANGELOG section at bottom of SKILL.md
3. Document current state as the 1.0 baseline entry

---

## Line Count Reduction Strategies

| Content Type | Extraction Target | Trigger |
|---|---|---|
| Phase instructions | references/PHASE-N.md | Phase >30 lines |
| Bash/Python scripts | scripts/script-name.sh | Any inline script |
| Example outputs | examples/example-N.md | Examples >15 lines |
| Error handling | references/ERROR-HANDLING.md | Error section >20 lines |
| Reference tables | references/TABLE-NAME.md | Table >10 rows |

---

## Version Bumping Rules

| Change Type | Rule | Example |
|---|---|---|
| Adding references/, extracting phases | Minor bump | 1.0 → 1.1 |
| CSO rewrite, description change | Patch bump | 1.0 → 1.0.1 |
| Renamed skill, restructured phases | Major bump | 1.0 → 2.0 |
| Added hooks or quality gates | Patch bump | 1.1 → 1.1.1 |
| Breaking input/output change | Major bump | 1.1 → 2.0 |

---

## Migration Report Template

After migration is complete, output this report:

```
MIGRATION COMPLETE: [skill-name]
Version: [old] → [new]
Date: [date]

CHANGES APPLIED:
- [list each change]

BEFORE:
  Lines: [N]
  CSO score: [N]/10
  Health score: [N]/100

AFTER:
  Lines: [N]
  CSO score: [N]/10
  Health score: [N]/100

FILES CREATED:
- references/PHASE-2.md
- references/ERROR-HANDLING.md
- CHANGELOG (appended)

VALIDATION: [PASS / FAIL]
[If FAIL: list remaining issues]
```
