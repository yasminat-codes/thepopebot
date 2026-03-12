# Progressive Disclosure Reference

Directive generation rules and line budget allocation for skills-architect.

---

## The Progressive Disclosure Law

**SKILL.md is a navigation hub, not a knowledge base.**

| Location | Purpose |
|----------|---------|
| SKILL.md | Phases, directives, entry conditions, exit criteria |
| references/ | ALL detailed content, tables, schemas, examples |
| scripts/ | ALL shell scripts, validators, test runners |

The more reference files a skill has, the better it ages. Details in SKILL.md rot. Details in references/ can be updated independently without restructuring the skill.

**Three rules that are never optional (Tier 3+):**
1. If content exceeds 30 lines in SKILL.md, it belongs in references/
2. Every shell script goes in scripts/, never inline in SKILL.md
3. Every reference file must have exactly one directive pointing to it

---

## Directive Syntax

### For Reference Files

```
→ See references/FILE.md [trigger condition]
```

**Full format:**
```
→ See references/FILE.md when [trigger condition] — [one-line description]
```

**Examples:**
```
→ See references/TOOLS-REFERENCE.md when selecting tools for any tier
→ See references/MIGRATION-GUIDE.md when MIGRATE mode is detected
→ See references/ERROR-CATALOG.md when a phase exits with non-zero status
→ See references/HOOK-PATTERNS.md when hooks are needed (Tier 4+)
→ See references/VALIDATION-RULES.md when Phase 5 begins
```

### For Scripts

```
→ Run: scripts/FILE.sh [trigger condition] (exit 0 = pass)
```

**Full format:**
```
→ Run: scripts/FILE.sh when [trigger condition] (exit 0 = [pass meaning], exit 1 = [fail meaning])
```

**Examples:**
```
→ Run: scripts/validate-structure.sh when Phase 1 completes (exit 0 = structure valid, exit 1 = missing dirs)
→ Run: scripts/run-tests.sh when Phase 4 completes (exit 0 = all pass, exit 1 = failures found)
→ Run: scripts/check-deps.sh before Phase 1 begins (exit 0 = deps present, exit 1 = install required)
→ Run: scripts/lint-skill.sh when SKILL.md is written (exit 0 = compliant, exit 1 = violations found)
```

---

## Trigger Condition Patterns

Use these patterns consistently across all skill directives. Consistent language makes directives scannable.

### Phase-Based Triggers

```
when Phase N begins
when Phase N completes
when Phase N fails
before Phase N starts
after Phase N succeeds
```

Use for: scripts that gate phase transitions, references that define phase-specific rules.

### Conditional Triggers

```
when [feature] is needed
when [situation] is detected
when [mode] is active
when [error type] occurs
```

**Examples:**
```
when hooks are needed
when database migrations are detected
when an import error occurs
when MCP dependencies are present
when user requests AUDIT mode
```

Use for: optional references that apply only in certain scenarios.

### Mode-Based Triggers

```
when [MODE] mode is detected
when running in [mode] context
```

**Examples:**
```
when MIGRATE mode is detected
when CREATE mode is active
when AUDIT mode is requested
when DEBUG mode is enabled
```

Use for: skills with multiple operational modes (CREATE, MIGRATE, AUDIT, REPAIR).

### Tier-Based Triggers

```
for Tier N+ skills
when skill tier is N or above
```

**Examples:**
```
for Tier 5+ skills
when skill tier is 4 or above
for all Tier 6 skills
```

Use for: references that only apply at higher complexity levels.

### Always-On Triggers

```
always
on every invocation
before any phase begins
```

Use sparingly. Reserved for truly universal references (e.g., a skill's core schema definition).

---

## Auto-Generation Algorithm

When building or auditing directives for a SKILL.md, follow this process exactly.

**Step 1: List all files**
```
Glob("references/*.md") → list of reference files
Glob("scripts/*.sh") → list of script files
```

**Step 2: Determine primary trigger for each file**

For each file, read its first 20 lines to identify:
- What phase it serves (look for "Phase N" in title or h2)
- What mode it serves (look for "MODE" or "when" in title)
- What condition activates it (look for conditional keywords)

If no clear trigger is found, assign: `when [filename-topic] is relevant`

**Step 3: Generate directive**

Template:
```
→ See references/[filename] when [trigger] — [h1 title of file as description]
```

For scripts:
```
→ Run: scripts/[filename] when [trigger] (exit 0 = [meaning], exit 1 = [meaning])
```

**Step 4: Group by phase**

In SKILL.md, organize directives under the phase where they are first needed:

```markdown
## Phase 1: Discovery
→ See references/DISCOVERY-RULES.md when Phase 1 begins

## Phase 2: Design
→ See references/TIER-GUIDE.md when determining skill tier
→ See references/TOOLS-REFERENCE.md when selecting tools

## Phase 3: Implementation
→ Run: scripts/validate-structure.sh when Phase 3 completes (exit 0 = pass)
→ See references/HOOK-PATTERNS.md when hooks are needed
```

**Step 5: Orphan check**

Run orphan detection before finalizing (see section below).

---

## Orphan Detection

An orphan is any file without a directive, or any directive without a file.

### File Orphan (file exists, no directive points to it)

**Detection:**
```
Glob("references/*.md") → file_list
Grep("references/", "SKILL.md") → directive_targets
diff(file_list, directive_targets) → orphaned_files
```

**Fix:** Generate a directive for every orphaned file using the auto-generation algorithm above.

**Severity:** High. Orphaned files are unreachable dead weight. Either add a directive or delete the file.

### Directive Orphan (directive exists, file does not)

**Detection:**
```
Grep("→ See references/", "SKILL.md") → directive_paths
Glob("references/*.md") → actual_files
diff(directive_paths, actual_files) → broken_directives
```

**Fix:** Either create the missing file or remove the directive.

**Severity:** Critical. Broken directives cause skill failures at runtime.

### Script Orphan

Same logic applied to scripts/:
```
Glob("scripts/*.sh") vs Grep("→ Run: scripts/", "SKILL.md")
```

---

## Line Budget Allocation by Tier

| Tier | SKILL.md lines | Ref files | Lines per ref file |
|------|----------------|-----------|-------------------|
| 1 | 50-150 | 0 | - |
| 2 | 100-200 | 0 | - |
| 3 | 150-300 | 1-2 | 100-300 |
| 4 | 200-400 | 3-5 | 100-400 |
| 5 | 300-500 | 5-10 | 100-400 |
| 6 | 400-600 | 10-15 | 100-400 |
| 7 | per-skill | per-skill | 100-400 |

### Tier 1-2: No References Needed

Tier 1 and 2 skills are short enough that SKILL.md can hold all content. No references/ directory required.

If a Tier 2 skill grows to need detailed examples, consider promoting it to Tier 3 rather than adding references.

### Tier 3: Minimal References

1-2 reference files maximum. Typical content:
- One reference for detailed phase instructions
- One reference for configuration schema or patterns

If a Tier 3 skill needs more than 2 references, it may need a tier upgrade.

### Tier 4: Standard References

3-5 reference files. Typical distribution:
- Phase instruction references (1-2 files)
- Tool or pattern reference (1 file)
- Error handling or validation reference (1 file)
- Configuration schema (optional, 1 file)

### Tier 5: Rich References

5-10 reference files. Typical additions beyond Tier 4:
- Mode-specific references (1 per mode)
- Integration patterns (1 file)
- Web research templates (1 file)
- Subagent coordination guide (1 file)

### Tier 6: Comprehensive References

10-15 reference files. No single reference should exceed 400 lines. If a reference is growing past 300 lines, split it.

### Tier 7: Custom Allocation

Tier 7 skills define their own budget based on actual complexity. The per-ref-file max of 400 lines still applies.

---

## What Must Never Live in SKILL.md (Tier 3+)

The following content types always belong in references/ or scripts/, never inline in SKILL.md.

### Long Scripts

**Never:**
```markdown
## Phase 3
Run this to validate:
```bash
#!/bin/bash
set -e
# 40 lines of bash...
```
```

**Always:**
```markdown
## Phase 3
→ Run: scripts/validate.sh when Phase 3 completes (exit 0 = valid)
```

### Detailed Phase Instructions Over 30 Lines

**Never:** A Phase section in SKILL.md with 50+ lines of sub-steps, decision trees, and examples.

**Always:** Summarize in 5-10 lines in SKILL.md. Move details to `references/PHASE-N-GUIDE.md`.

### Code Examples

**Never:** Inline code blocks showing implementation patterns, especially multi-language examples.

**Always:** Move to `references/EXAMPLES.md` or `references/PATTERNS.md`.

### Error Handling Tables

**Never:** A 20-row error code table inside SKILL.md.

**Always:** `references/ERROR-CATALOG.md` with a single directive in the relevant phase.

### Configuration Schemas

**Never:** Full JSON/YAML schema definitions inline in SKILL.md.

**Always:** `references/CONFIG-SCHEMA.md` or `references/SKILL-SCHEMA.md`.

### Comparison Tables Over 10 Rows

**Never:** Large comparison or decision tables inline in SKILL.md.

**Always:** Move to a dedicated reference file with a scoped trigger directive.

---

## Directive Quality Checklist

Before finalizing any SKILL.md, verify each directive against this checklist.

- [ ] Every reference file has exactly one directive in SKILL.md
- [ ] Every script file has exactly one directive in SKILL.md
- [ ] No directive points to a non-existent file
- [ ] Each directive has a clear trigger condition (not just "always")
- [ ] Directives are grouped under the phase where they are first needed
- [ ] Script directives specify both exit 0 and exit 1 meanings
- [ ] No long scripts, code examples, or schemas remain inline in SKILL.md
- [ ] SKILL.md line count is within tier budget
- [ ] No reference file exceeds 400 lines
