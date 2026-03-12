# Context Injection Reference

This file defines how task-master adds file-path context to every generated task file.

---

## Section 1: Why Context Injection Matters

When a task file lists no specific file paths, the implementer (or Claude acting as the implementer)
must search the codebase to find relevant files before writing a single line of code. On a moderately
sized project this costs 5-15 minutes of manual search and burns 10,000-30,000 context window tokens
on discovery work that task-master already did.

Context injection solves this: task-master runs discovery once during generation and encodes
the results directly into the task file. The implementer opens the task, reads the file list,
loads those files, and starts writing immediately.

Every task file MUST contain two context sections:

```markdown
## Files to Read Before Starting
- `.claude/skills/{name}/SKILL.md` — tier, existing directives, line budget
- `.claude/skills/{name}/references/{RELATED}.md` — most related existing reference (pattern to follow)
- `.claude/MISTAKES.md` — grep for "{keyword}" before starting
- `.claude/context/CODE_QUALITY_RULES.md` — style conventions for skill/reference files

## Files to Create or Modify
- `.claude/skills/{name}/references/{FILE}.md` (create) — new reference file
- `.claude/skills/{name}/SKILL.md` (modify) — add → See directive
- `.claude/skills/{name}/README.md` (modify) — add row to Reference Files table
```

---

## Section 2: Context Discovery Protocol

During Phase 2 (file discovery), task-master MUST find these categories of files
for every task it generates. Run discovery in parallel where possible.

### 1. Files to create or modify
Source: the plan section for this task. Extract any file paths mentioned explicitly.
If no paths are explicit, infer from the feature name:
- New reference file → `.claude/skills/{name}/references/{FEATURE}.md`
- New agent → `.claude/skills/{name}/agents/{agent-name}.md`
- New script → `.claude/skills/{name}/scripts/{script-name}.sh`
- New hook → `.claude/skills/{name}/hooks/{hook-name}.sh`
- New test cases → `.claude/skills/{name}/tests/test-cases.md`

### 2. Peer reference (pattern reference)
When creating a new reference file, include one existing reference file from the same skill
as a reading reference so the implementer follows the established structure.

Discovery approach:
```
glob_pattern = ".claude/skills/{name}/references/*.md"  # → pick the most relevant existing file
```

Include the most closely related peer file, not just any file from the directory.

### 3. The test-cases file
- If `tests/test-cases.md` already exists: include it in "Files to Read Before Starting"
  (so the implementer extends rather than overwrites it)
- If it does not exist: include target path in "Files to Create or Modify" with `(create)`

Discovery approach:
```
glob_pattern = ".claude/skills/{name}/tests/test-cases.md"
```

### 4. SKILL.md (always required)
Always include `.claude/skills/{name}/SKILL.md`.
Reason: the tier limit (600 lines), existing directives, and line budget must be checked
before adding any new reference or modifying the file.

Discovery approach:
```
glob_pattern = ".claude/skills/{name}/SKILL.md"
```

### 5. Related skills or hooks
When the plan section names another skill or hook the new code will call, find and list it.

Discovery approach:
```
grep_pattern = "{skill_name}" in ".claude/skills/"
```

Example: plan mentions "dispatch testing-skills-with-subagents" → grep for that skill name
→ include its SKILL.md in "Files to Read Before Starting".

---

## Section 3: File Path Format Rules

- Always use paths relative to the skill root: `.claude/skills/{name}/references/EXTRACTION-PATTERNS.md`
- Never use `./` prefix: not `./references/EXTRACTION-PATTERNS.md`
- Never use absolute paths: not `/Users/yasmineseidu/coding/yasmine-os/.claude/skills/...`
- For files that do not yet exist: append `(create)` after the path
- For files that exist and will be changed: append `(modify)` after the path
- For files that are read-only context: no label needed

### Correct format

```markdown
## Files to Read Before Starting
- `.claude/skills/email-parser/SKILL.md` — skill tier, existing directives, line budget
- `.claude/skills/email-parser/references/OUTPUT-SCHEMA.md` — existing reference to follow as pattern
- `.claude/MISTAKES.md` — grep for "email-parser" before starting
- `.claude/context/CODE_QUALITY_RULES.md` — style conventions for skill/reference files

## Files to Create or Modify
- `.claude/skills/email-parser/references/EXTRACTION-PATTERNS.md` (create)
- `.claude/skills/email-parser/SKILL.md` (modify) — add → See directive
- `.claude/skills/email-parser/README.md` (modify) — add row to Reference Files table
```

---

## Section 4: Context Sizing Guide

Use the task's complexity (estimated by number of files to create/modify) to determine
how many context files to include in "Read Before Starting."

| Task Size | Files to Create/Modify | Files to Read | Approx. Context Impact |
|-----------|------------------------|---------------|------------------------|
| Small     | 1-2 files              | 3-5 files     | ~20-30k tokens         |
| Medium    | 3-4 files              | 5-8 files     | ~40-60k tokens         |
| Large     | 5+ files               | 8-12 files    | ~60-80k tokens         |

**Warning threshold:** If the "Read Before Starting" section would list more than 12 files,
the task is too large. Split it into two tasks. Add a note in the original task:
```markdown
> Note: This task was split from a larger unit. See task NNN-{sibling-title}.md for the
> other half. Complete this task first; the sibling has a `BlockedBy: [NNN]` dependency.
```

---

## Section 5: Files to Always Include

These files appear in the "Files to Read Before Starting" section of EVERY task file task-master
generates, regardless of what the task builds. They are non-negotiable.

| File                                     | Why always included                                                           |
|------------------------------------------|-------------------------------------------------------------------------------|
| `.claude/skills/{name}/SKILL.md`         | Tier limit, existing directives, line budget must be checked before editing   |
| `.claude/MISTAKES.md`                    | Past mistakes in this workspace that the implementer must not repeat          |
| `.claude/context/CODE_QUALITY_RULES.md`  | Style conventions for skill and reference files                               |

### How to reference MISTAKES.md in a task file

Do not tell the implementer to read the whole file. Point them to the relevant section:

```markdown
- `.claude/MISTAKES.md` — grep for `{relevant_keyword}` before starting
  (e.g., grep for "directive", "reference", "tier limit", or the skill name)
```

Replace `{relevant_keyword}` with the most specific term from the task's subject matter.

---

## Section 6: Rules Injection

→ See references/RULES-INJECTION.md for the full rules matching matrix and injection format

During Phase 0, task-master discovers all files in `.claude/rules/` and `~/.claude/rules/`.
During Phase 4, for each task, it selects relevant rules and adds a `## Relevant Rules` section.

### Where rules go in the task file

Insert `## Relevant Rules` immediately after `## Files to Read Before Starting`, before
`## Files to Modify or Create`. This ensures the implementer sees rules before touching code.

### Always-include rules (if files exist on disk)

```markdown
## Relevant Rules

- `.claude/rules/task-management.md` — task lifecycle: pending → in-progress → completed
- `.claude/rules/code-quality.md` — async I/O, ruff, mypy, 120 char limit, no print()
- `.claude/rules/context-loading.md` — read the file fully before editing; check MISTAKES.md
```

### Adding conditional rules

Append to the always-include list based on task keywords:

```markdown
- `.claude/rules/research-first.md` — search codebase + GREP MCP before writing new service
- `.claude/rules/fastapi-coolify-rules.md` — health endpoint, Pydantic Settings, Dockerfile
```

### If `.claude/rules/` does not exist

Skip the `## Relevant Rules` section entirely. Do not add an empty heading.
