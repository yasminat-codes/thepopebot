# LEARNING-PATTERNS.md — Task Depth Corrections and Persistent Preferences

task-master persists user corrections and preferences across sessions.
This file defines what gets saved, the storage format, and the exact load/save procedures
for Phase 0 and Phase 5.

---

## Section 1: What Gets Saved

task-master writes to `.claude/memory/task-master.md` when the user provides any of
the following signals during a session:

### Depth corrections
- "these tasks are too detailed" or "too granular" → record: `task_depth: lean`
- "these tasks are too vague" or "not enough detail" → record: `task_depth: rich`
- No explicit feedback → `task_depth` stays at its last recorded value

### Merge signals
- "merge these two tasks" or "combine X and Y" → record the two task titles and the reason
- "this doesn't need its own task" → record the removed task title and reason

### Split signals
- "split this task further" → record the task title and reason for splitting
- "this task is too large" → record as split signal even if no explicit split is requested

### Directory overrides
- User specifies a non-default output directory during Phase 1 interview
  (e.g., "put tasks in work/_pending/" instead of `tasks/_pending/`)
  → record: `output_dir: work/_pending/`
- User specifies a non-default plan source directory → record: `plan_dir`

### Custom rules derived from feedback
When a merge or split occurs, derive a one-sentence rule that generalizes the pattern.
The rule is what prevents the same mistake on the next plan.

---

## Section 2: Memory File Format

### File path
```
.claude/memory/task-master.md
```

The directory `.claude/memory/` is created on first write if it does not exist.
If the file does not exist, treat all preferences as defaults (see Phase 0 procedure).

### Schema

```markdown
# task-master Memory

## Preferences
last_updated: 2026-03-02
task_depth: standard  # lean | standard | rich
output_dir: tasks/_pending/
plan_dir: plans/

## Corrections Log
### 2026-03-02: Too Detailed
Plan: niche-scout
Feedback: Tasks were too granular — merged 003 and 004 into one task
Rule: Combine service + its helper into one task when helper is < 30 lines

### 2026-03-02: Missing Live Test
Plan: deep-dive
Feedback: Forgot to include OPENROUTER_API_KEY live test in task 002
Rule: Always check for OPENROUTER_API_KEY when plan mentions LLM calls
```

### Field definitions

**Preferences block:**

| Field | Default | Valid Values |
|-------|---------|-------------|
| `last_updated` | today's date | ISO date `YYYY-MM-DD` |
| `task_depth` | `standard` | `lean`, `standard`, `rich` |
| `output_dir` | `tasks/_pending/` | any valid relative path |
| `plan_dir` | `plans/` | any valid relative path |

**Depth definitions:**
- `lean` — fewer checklist items, shorter success criteria, combine closely related steps
- `standard` — default; follows TASK-TEMPLATE.md exactly as specified
- `rich` — more granular checklist items, additional "Before You Start" notes, expanded test coverage descriptions

**Corrections Log block:**

Each entry uses this structure:
```markdown
### {YYYY-MM-DD}: {Short Label}
Plan: {plan name (slug, no path)}
Feedback: {one sentence describing what happened}
Rule: {one imperative sentence to prevent recurrence}
```

The "Rule" line is the actionable output. It is extracted and applied during Phase 0 (see Section 3).

---

## Section 3: Load Procedure (Phase 0)

Execute at the very start of Phase 0, before reading the plan file or running the Phase 1 interview.

### Step 1: Attempt to read the memory file
```
Read .claude/memory/task-master.md
```
If the file does not exist: use all defaults. Skip to Phase 1 interview with defaults applied.
Do not create the file during load — only create during save.

### Step 2: Extract preferences
Parse the `## Preferences` block and extract:
- `task_depth` → apply as default depth for this session
- `output_dir` → use as the default output path in Phase 1 interview question
- `plan_dir` → use as the default plan source path in Phase 1 interview question

If any preference field is missing from the file, fall back to the default for that field only.

### Step 3: Extract and apply correction rules
Parse every entry in the `## Corrections Log` block.
From each entry, extract only the `Rule:` line.
Collect all Rule lines into a list: `LEARNED_RULES`.

Apply `LEARNED_RULES` as additional constraints during Phase 3 (task generation), alongside
the rules from TASK-TEMPLATE.md. These are not displayed to the user during the interview —
they are applied silently during generation.

Example learned rules that would be applied automatically:
```
- Combine service + its helper into one task when helper is < 30 lines
- Always check for OPENROUTER_API_KEY when plan mentions LLM calls
- Split database migration tasks from model tasks when migration > 5 tables
```

### Step 4: Show loaded state to user (brief)
At the start of Phase 1, show one line summarizing loaded preferences:
```
[Memory] Loaded preferences: depth=lean, output=tasks/_pending/ (2 learned rules applied)
```
Do not print all the corrections — just the summary line. The user can ask to see corrections
if they want. This keeps Phase 1 interview focused.

---

## Section 4: Save Procedure (Phase 5)

Execute after task delivery, only if the user made at least one correction during the session.

### Trigger: when to save
Save if any of the following occurred:
- User explicitly changed task depth ("too detailed", "too vague")
- User merged two tasks
- User split a task
- User changed the output or plan directory from the default

Do NOT save if no corrections were made. An unchanged session leaves the memory file unmodified.

### Step 1: Read current file state
Read `.claude/memory/task-master.md` to get the current content.
If the file does not exist, start from the default template (see Section 2 schema).

### Step 2: Update Preferences block
If `task_depth` changed: update the `task_depth` line.
If `output_dir` changed: update the `output_dir` line.
If `plan_dir` changed: update the `plan_dir` line.
Update `last_updated` to today's date.

Do NOT remove or alter fields that were not changed.

### Step 3: Append new corrections
For each correction made this session, append a new entry to the bottom of the
`## Corrections Log` block. New entries go AFTER all existing entries — never before,
never replacing.

Format each new entry exactly as:
```markdown
### {YYYY-MM-DD}: {Short Label}
Plan: {plan slug}
Feedback: {one sentence}
Rule: {one imperative sentence}
```

The Short Label is a 2–4 word summary of the correction type. Examples:
- `Too Detailed`
- `Missing Live Test`
- `Wrong Directory`
- `Split Required`
- `Merged Helpers`

### Step 4: Write the updated file
Write the complete updated file back to `.claude/memory/task-master.md`.
The write is a full replacement — not an append. Construct the full file content and write once.

### Step 5: Confirm to user
After writing, print one line:
```
[Memory] Saved 2 corrections to .claude/memory/task-master.md
```

Do NOT overwrite previous corrections. The Corrections Log is a permanent, append-only
historical record. Every entry that was there before the save must still be there after.
