# QUALITY-GATES.md — Per-Task Validation Rules

Defines what the `post-tool.sh` hook validates after each task file is written.
Every rule here runs automatically. Violations are logged; structural violations block delivery.

---

## Section 1: 11-Section Completeness Check

Every task file must contain ALL 11 of these structural markers.
The hook greps for each pattern immediately after the Write tool call completes.

| # | Required Marker | Grep Pattern | Failure Message |
|---|----------------|--------------|-----------------|
| 1 | Task number in title | `^# Task [0-9]{3}` | "Task title missing NNN: format" |
| 2 | Status field | `\*\*Status:\*\*` | "Missing **Status:** field" |
| 3 | BlockedBy field | `\*\*BlockedBy:\*\*` | "Missing **BlockedBy:** field" |
| 4 | Summary section | `^## Summary` | "Missing ## Summary section" |
| 5 | Files to Read | `^## Files to Read` | "Missing ## Files to Read Before Starting" |
| 6 | Relevant Rules | `^## Relevant Rules` | "Missing ## Relevant Rules section" |
| 7 | Implementation Checklist | `^## Implementation Checklist` | "Missing ## Implementation Checklist" |
| 8 | Success Criteria | `^## Success Criteria` | "Missing ## Success Criteria section" |
| 9 | Testing section | `^## Testing` | "Missing ## Testing section" |
| 10 | Task Management | `^## Task Management` | "Missing ## Task Management section (TaskCreate/TaskUpdate)" |
| 11 | Definition of Done | `^## Definition of Done` | "Missing ## Definition of Done section" |

Note: `## Relevant Rules` may be omitted ONLY if `.claude/rules/` does not exist on disk.
If the directory exists, the section is mandatory.

### Failure behavior for missing sections

If 1–3 sections are missing: **block delivery** of that task file. Log the failure and halt
before writing the file. Ask the user whether to skip or fix before continuing.

If all sections are present but contain only empty or placeholder content (e.g., heading with
no body text): treat as a content failure (see Section 2) and log a warning.

---

## Section 2: Content Quality Rules

Presence of a section heading is necessary but not sufficient. These content rules apply
to the body of each section.

### Success Criteria
- Must contain **at least 2 items**. A single-item Success Criteria section is a defect.
- Each item must end with a verifiable form: a runnable shell command or a specific observable
  state. Examples of acceptable endings:
  - `exits 0`
  - `returns the field definition`
  - `assert verified in test_{name}`
- "It should work" or "functions correctly" are NOT acceptable. Log as content warning.

### Testing Section
- Must contain at least one `uv run pytest` command.
- Cannot be prose only (e.g., "Tests will be written later" is a blocking defect).
- Must contain at least one named test function or test case description per subsection.

### Implementation Checklist
- Every item must use `- [ ]` format.
- Every item must have non-empty content after the checkbox character.
- Empty checklist items (`- [ ]` with no text after) are a content defect.
- At minimum: one lint step (`uv run ruff check --fix`) and one mypy step must appear.

### Files to Read
- Must contain at least one file path in relative format.
- Valid format examples: `app/services/foo.py`, `tests/conftest.py`, `app/config.py`
- Invalid format: `./app/foo.py` (leading `./`), absolute paths, or bare filenames
  without a directory prefix.

### BlockedBy
- Canonical no-dependency format: `—` (em dash, matches wave_0 detection algorithm)
- Dependency formats: `[001]` (single), `[001, 002]` (multiple)
- `[]` is accepted as an alias for `—` but `—` is preferred for consistency
- Prose in BlockedBy (e.g., `[depends on auth task]`) is a structural defect.
- A sub-task suffix is valid: `[001a, 001b]`.

---

## Section 3: Line Count Check

Line count is checked after each Write. The hook uses `wc -l` on the written file.

| Count | Severity | Behavior |
|-------|----------|----------|
| <= 90 | OK | No action |
| 91–120 | Warning | Log to audit file: "Task is large. Consider splitting." |
| > 120 | Error | Log to audit file: "Task exceeds 120-line limit. Split required." Prompt user to confirm or split before continuing to the next task. |

Line count errors are **not hard blocks** — they are logged and the user is prompted once.
If the user confirms "proceed anyway", the task file is written and the error is logged.
The error appears in the final delivery report summary.

Sub-tasks produced by splitting (e.g., `001a`, `001b`) each have their own independent
line count check. Splitting into sub-tasks that are themselves oversized is still a defect.

---

## Section 4: Audit Log Format

After each Write tool call completes, the hook appends one line to the audit log.

### Log file location
```
.claude/logs/task-master-audit.log
```
The directory `.claude/logs/` is created by the hook on first run if it does not exist.

### Log line format
```
{ISO_TIMESTAMP} | {OUTCOME} | {task_file} | {line_count} lines | {sections_status} | {detail}
```

Field definitions:
- `ISO_TIMESTAMP` — UTC, format `2026-03-02T01:05:00Z`
- `OUTCOME` — one of: `WRITTEN`, `BLOCKED`, `WARNING`
- `task_file` — path relative to project root, e.g., `tasks/_pending/001-rate-limiter.md`
- `line_count` — integer from `wc -l`
- `sections_status` — `ALL_PRESENT` or `MISSING`
- `detail` — `—` if nothing to report; otherwise the missing section names or warning message

### Example log entries

```
2026-03-02T01:05:00Z | WRITTEN  | tasks/_pending/001-rate-limiter.md    | 87 lines  | ALL_PRESENT | —
2026-03-02T01:06:00Z | WRITTEN  | tasks/_pending/002-migration.md       | 45 lines  | MISSING     | Testing
2026-03-02T01:07:00Z | WARNING  | tasks/_pending/003-openai-client.md   | 94 lines  | ALL_PRESENT | Task is large. Consider splitting.
2026-03-02T01:08:00Z | BLOCKED  | tasks/_pending/004-webhook-handler.md | 0 lines   | MISSING     | Summary, Testing, Definition of Done
```

### End-of-run summary

At the end of Phase 5 (delivery), the hook reads the audit log and prints a summary:

```
TASK-MASTER AUDIT SUMMARY
  Tasks written:  8
  Tasks blocked:  1  (fix before proceeding)
  Warnings:       2  (review recommended)
  Audit log:      .claude/logs/task-master-audit.log
```

The audit log is append-only. Previous runs are not overwritten. Each line is a permanent
record of what was generated and when.
