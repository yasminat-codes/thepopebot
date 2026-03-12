# Memory Integration and Creation Logging

Memory integration patterns for skills-architect — loading preferences, saving logs, learning from corrections, and tracking audit history.

---

## Three-Tier Memory System

Skills-architect reads from and writes to three memory locations, each with a different scope.

```
Tier 1 — Project memory:   .claude/memory/MEMORY.md
  Scope:  This project only
  Use:    Project-specific skill preferences and overrides

Tier 2 — Global memory:    ~/.claude/projects/-Users-yasmineseidu/memory/MEMORY.md
  Scope:  All projects on this machine
  Use:    Cross-project defaults and learned user preferences

Tier 3 — Skill memory:     .claude/memory/skills-architect.md
  Scope:  This skill's execution log for this project
  Use:    Creation log, audit history, correction tracking
```

**Priority rule:** Project memory overrides global memory. Both override built-in defaults. When a setting exists in multiple tiers, the narrowest scope wins.

---

## Loading Preferences (Phase 0)

Run before any user interaction. Loading preferences ensures the skill presents correct defaults on first question.

**Procedure:**

1. Attempt to read `.claude/memory/skills-architect.md` (Tier 3)
   - If exists: extract `## preferences` section
   - If not exists: skip silently

2. Attempt to read `.claude/memory/MEMORY.md` (Tier 1)
   - If exists: look for `## skills-architect` section
   - If not exists: skip silently

3. Attempt to read `~/.claude/projects/-Users-yasmineseidu/memory/MEMORY.md` (Tier 2)
   - If exists: look for `## skills-architect` section
   - If not exists: skip silently

4. Merge preferences with priority: Tier 3 > Tier 1 > Tier 2 > built-in defaults

5. Apply merged preferences as defaults for Phase 1 questions

**What to look for in memory files:**

```markdown
## skills-architect

### preferences
- default_tier: 4
- preferred_cso_elements: [PROACTIVELY, triggers, extensions, output_artifact]
- skip_suggestions: [memory_integration]
- always_generate_tests: true
- preferred_test_count: 5
- audit_format: compact

### corrections
- 2026-02-28: User prefers Tier 4 over auto-detect for workflow orchestrators
- 2026-02-20: User skips circuit breaker suggestion for internal-only skills
```

**Applying loaded preferences:**

| Preference key | Effect |
|---|---|
| `default_tier` | Pre-select tier in Phase 2 instead of asking |
| `preferred_cso_elements` | Pre-check these in CSO builder |
| `skip_suggestions` | Remove from suggestion multiSelect |
| `always_generate_tests` | Auto-include testing without asking |
| `preferred_test_count` | Override tier-based default test count |
| `audit_format` | Use compact or verbose audit report |

---

## Saving Creation Log (Phase 10)

After successful skill creation, write a log entry to the skill memory file.

**Target file:** `.claude/memory/skills-architect.md`

**Log entry format:**
```markdown
## skills-architect

### creation-log
- 2026-02-28: Created `my-skill` (Tier 4, 6 tools, 4 refs, 380 lines, CSO 9/10)
- 2026-02-27: Migrated `old-skill` (v1.0→v2.0, decomposed 800→350 lines)
- 2026-02-26: Audited 15 skills (avg health: 72/100, 3 critical)
- 2026-02-25: Created `deploy-helper` (Tier 3, 4 tools, 2 refs, 220 lines, CSO 10/10)
```

**Log entry schema:**

For creation:
```
- {date}: Created `{skill-name}` (Tier {N}, {N} tools, {N} refs, {N} lines, CSO {N}/10)
```

For migration:
```
- {date}: Migrated `{skill-name}` ({old-version}→{new-version}, {description of change})
```

For audit:
```
- {date}: Audited {N} skills (avg health: {N}/100, {N} critical)
```

For single-skill audit:
```
- {date}: Audited `{skill-name}` (health: {N}/100, issues: {list or "none"})
```

**Write procedure:**
1. Read existing `.claude/memory/skills-architect.md` if it exists
2. Find or create `### creation-log` section under `## skills-architect`
3. Prepend new entry (most recent first)
4. Write file back

---

## Learning From Corrections

When a user overrides a recommendation during skill creation, save the override so it becomes the new default on the next run.

**Detecting overrides:**

An override occurs when:
- User selects a different tier than the one recommended
- User deselects a suggested enhancement that was pre-selected
- User modifies a generated CSO description rather than accepting it
- User changes a directive's trigger condition after it was auto-generated
- User sets a different test count than the tier-based default

**Logging corrections:**

Append to `### corrections` section in `.claude/memory/skills-architect.md`:
```markdown
### corrections
- {date}: User prefers {override} over {default} for {context}
```

**Examples of correction log entries:**
```markdown
- 2026-02-28: User prefers Tier 3 over Tier 4 for single-tool wrapper skills
- 2026-02-27: User prefers 5 pressure tests over 3 for all Tier 3+ skills
- 2026-02-26: User skips circuit-breaker suggestion for internal-network-only skills
- 2026-02-25: User prefers manual CSO writing over auto-generated description
```

**Applying corrections on next run:**

During Phase 0 loading:
1. Read `### corrections` section
2. For each correction, map to the relevant default:
   - "User prefers Tier 3 over Tier 4 for single-tool wrapper skills" → if skill has 1 tool, default tier = 3
   - "User skips circuit-breaker suggestion for internal-network-only skills" → remove from suggestion list if no external URLs detected
3. Inform user at start: "Applied 2 saved preferences from previous sessions."

---

## Audit History Tracking

When running an audit (health check on existing skills), save results for trend analysis.

**Target file:** `.claude/memory/skills-architect.md`

**Audit history format:**
```markdown
### audit-history

#### 2026-02-28
- Total skills audited: 15
- Average health score: 72/100
- Critical (below 50): data-fetcher, old-deployer, legacy-util
- Improved since last audit: my-skill (60→85), deploy-helper (55→90)
- Regressed since last audit: none

#### 2026-02-20
- Total skills audited: 12
- Average health score: 65/100
- Critical (below 50): data-fetcher, old-deployer, legacy-util, another-skill
- Improved since last audit: N/A (first audit)
```

**Comparing current vs previous audit:**

When a new audit completes:
1. Read the most recent `#### {date}` block from `### audit-history`
2. For each skill in both audits, compare health scores
3. Flag improvements (score increased by 10+) and regressions (score decreased by 10+)
4. Include comparison in audit report:
   ```
   TREND: Average health improved from 65 → 72 (+7) since 2026-02-20
   IMPROVED: my-skill (60→85), deploy-helper (55→90)
   REGRESSED: none
   ```

**Tracking improvement trends:**

Over time, the audit history reveals whether the skill ecosystem is improving. Surface this in the audit summary:
- 3 audits trending up → "Ecosystem health improving consistently"
- Flat or declining → "No improvement trend — consider allocating time to skill maintenance"

---

## File Creation

If `.claude/memory/skills-architect.md` does not exist, create it with this initial structure before writing the first entry:

```markdown
# Skills-Architect Memory

Automatically maintained by the skills-architect skill.
Do not edit `creation-log` or `audit-history` manually — they are append-only logs.
The `preferences` and `corrections` sections can be edited manually to override behavior.

## skills-architect

### preferences
# Add preference overrides here (see MEMORY-INTEGRATION.md for keys)

### corrections
# Automatically populated when you override a recommendation

### creation-log
# Automatically populated after each skill creation or migration

### audit-history
# Automatically populated after each audit run
```

---

## Memory File Locations Reference

| File | When to read | When to write |
|---|---|---|
| `.claude/memory/skills-architect.md` | Phase 0 | Phase 10 (completion) |
| `.claude/memory/MEMORY.md` | Phase 0 | Never (read-only from this skill) |
| `~/.claude/projects/-Users-yasmineseidu/memory/MEMORY.md` | Phase 0 | Never (read-only from this skill) |

Skills-architect only writes to its own skill memory file. It reads from project and global memory but does not write to them — those are managed by the user or other memory systems.
