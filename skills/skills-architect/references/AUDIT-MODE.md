# Audit Mode - Batch Skill Health Analysis

## Overview

Audit mode scans every SKILL.md in a target directory, scores each skill against a 100-point rubric,
and produces a prioritized report with fix recommendations. Run before any major refactor or after
importing skills from an external source.

---

## Audit Workflow

### Step 1: Glob for All SKILL.md Files

Search the target directory recursively:

```
Pattern: **/SKILL.md
Scope: [target-directory] (default: .claude/skills/)
```

Collect all matches into an ordered list. Record:
- Skill name (parent directory name)
- Absolute path to SKILL.md
- Last modified date (for change detection)

### Step 2: Run 5-Point Check on Each Skill

For each SKILL.md found, evaluate all five checks in parallel:

#### a. Line Count Check

Count total lines in SKILL.md (excluding blank lines for tier determination).

Determine tier from frontmatter `tier` field, or infer from line count if missing.

| Tier | Max Lines | Pass Threshold |
|---|---|---|
| 1-3 | 50 | <=50 = PASS |
| 4-5 | 150 | <=150 = PASS, 151-200 = WARNING |
| 6+ | 350 | <=350 = PASS, 351-400 = WARNING, >400 = FAIL |

Score: 20 points if PASS, 10 points if WARNING, 0 points if FAIL.

#### b. CSO Score (0-10)

Read the description section and score each dimension:

| Dimension | Points | Check |
|---|---|---|
| PROACTIVELY trigger present | 3 | String "PROACTIVELY" in description |
| Input named clearly | 2 | "Takes X as input" or similar |
| Output described | 2 | "Produces X" or "Returns X" or similar |
| Related skills referenced | 1 | Mentions another skill by name |
| Under 5 sentences | 1 | Count sentences in description block |
| Active voice | 1 | No passive constructions ("is done", "will be") |

Total CSO raw score: 0-10. Multiply by 3 for health score contribution (max 30 points).

#### c. Frontmatter Completeness

Required fields (4 points each, max 20):
- `name` present
- `description` present
- `version` present
- `tier` present
- `inputs` present

Score: Count present fields x 4. Max 20 points.

#### d. Progressive Disclosure Compliance

Check inline content density:

1. Identify all phase blocks or major sections in SKILL.md
2. Count lines per section
3. Flag any section exceeding 30 lines that is not a `Read: references/...` pointer

Scoring:
- 0 violations: 20 points
- 1 violation: 12 points
- 2 violations: 6 points
- 3+ violations: 0 points

#### e. Orphan Reference Check

If a references/ directory exists alongside SKILL.md:
1. List all files in references/
2. Search SKILL.md for each filename
3. Flag any file not mentioned in SKILL.md

Scoring:
- No references/ directory: 10 points (not applicable)
- references/ exists, no orphans: 10 points
- 1-2 orphans: 5 points
- 3+ orphans: 0 points

### Step 3: Generate Health Report

Aggregate all scores into a markdown table sorted by health score ascending (worst first):

```markdown
## Skill Health Report
Generated: [date]
Directory: [path]
Skills scanned: [N]

| Skill | Tier | Lines | CSO | Frontmatter | Prog.Disc | Orphans | Health | Status |
|-------|------|-------|-----|-------------|-----------|---------|--------|--------|
| old-skill | ? | 520 | 3/10 | 8/20 | 0/20 | 10/10 | 30/100 | CRITICAL |
| basic-skill | 3 | 180 | 5/10 | 16/20 | 12/20 | 10/10 | 68/100 | WARNING |
| decent-skill | 4 | 140 | 7/10 | 20/20 | 20/20 | 10/10 | 80/100 | GOOD |
| polished-skill | 5 | 120 | 9/10 | 20/20 | 20/20 | 10/10 | 97/100 | EXCELLENT |
```

### Step 4: Rank Skills by Health Score

After the table, group skills into severity bands:

**CRITICAL (0-49 points) — Immediate action required**
List skill names and primary failure reason.

**WARNING (50-69 points) — Should fix this sprint**
List skill names and top 2 issues.

**GOOD (70-84 points) — Minor improvements available**
List skill names and single improvement opportunity.

**EXCELLENT (85-100 points) — No action needed**
List skill names. Celebrate.

### Step 5: Generate Fix Recommendations

For each skill below GOOD threshold, generate a numbered fix list ordered by impact:

```
SKILL: old-skill (30/100 — CRITICAL)
Fix 1 [+20 pts]: Reduce line count — extract Phase 2, Phase 3, Phase 4 to references/
Fix 2 [+18 pts]: Improve CSO — add PROACTIVELY trigger, describe outputs
Fix 3 [+12 pts]: Add missing frontmatter — version, tier, inputs fields missing
Fix 4 [+6 pts]: Extract Phase 2 (45 lines) — progressive disclosure violation

Estimated health after fixes: 86/100 (EXCELLENT)
Recommended command: Run migration mode on this skill.
```

---

## Health Score Calculation Reference

| Dimension | Max Points | How Calculated |
|---|---|---|
| Line count | 20 | PASS=20, WARNING=10, FAIL=0 |
| CSO score | 30 | Raw score (0-10) x 3 |
| Frontmatter | 20 | Required fields present x 4 |
| Progressive disclosure | 20 | Violation count penalty |
| Orphan check | 10 | No orphans = 10, scaled down |
| **Total** | **100** | |

---

## Severity Classification

| Score | Status | Action |
|---|---|---|
| 85-100 | EXCELLENT | No action needed |
| 70-84 | GOOD | Minor improvements available |
| 50-69 | WARNING | Fix this sprint |
| 0-49 | CRITICAL | Immediate action required |

---

## Health Report Template

Output this full report structure after every audit:

```markdown
# Skill Health Report

**Generated:** [ISO date]
**Directory:** [absolute path]
**Skills Scanned:** [N]
**Average Health:** [N]/100

---

## Summary Table

| Skill | Tier | Lines | CSO | Health | Status | Top Issue |
|-------|------|-------|-----|--------|--------|-----------|
[rows]

---

## By Severity

### CRITICAL ([N] skills)
[skill-name] — [primary issue]

### WARNING ([N] skills)
[skill-name] — [top issue]

### GOOD ([N] skills)
[skill-name] — [optional improvement]

### EXCELLENT ([N] skills)
[skill-name]

---

## Fix Recommendations (Priority Order)

### 1. [skill-name] — [N]/100
[numbered fix list with point gains]

### 2. [skill-name] — [N]/100
[numbered fix list with point gains]

---

## Previous Audit Comparison

[If memory exists from last audit:]
Last audit: [date]
Average health then: [N]/100
Average health now: [N]/100
Change: [+N/-N] ([improved/declined])

Skills improved: [list]
Skills declined: [list]
New skills added: [list]
```

---

## Comparison With Previous Audit

If a previous audit result exists in memory or at `.claude/skills-architect/audit-history/`:

1. Load the previous report
2. Compare average health scores
3. Identify which skills improved, declined, or were added/removed
4. Flag any skill that declined since last audit (regression alert)

Regression alert format:
```
REGRESSION ALERT: [skill-name]
Previous health: [N]/100
Current health: [N]/100
Decline: -[N] points
Likely cause: [line count grew / frontmatter field removed / etc.]
```

Store current audit result to `.claude/skills-architect/audit-history/[date]-audit.md` for future comparison.

---

## Running a Scoped Audit

The audit can be scoped to a subset of skills:

- Full directory: `audit .claude/skills/`
- Single namespace: `audit .claude/skills/sdk-agent-*/`
- Single skill: `audit .claude/skills/my-skill/SKILL.md`
- By tier: Filter results to show only Tier 4+ skills

When scoped, the report header shows the scope and notes that percentages are relative to the scoped set only.
