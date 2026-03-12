# task-master — Test Cases
Version: 1.0.0 | Last updated: 2026-03-02
Tests: 5 scenarios (4 pressure + 1 happy path)

---

## Test 1: Happy Path — Simple Service Plan

**Category:** Happy Path
**Priority:** P0 (must always pass)

### Setup

`plan/` contains a single 80-line plan file for adding a rate limiter service. File:
`tests/fixtures/sample-plan-simple/plan.md`. The `.env` file contains `REDIS_URL=redis://localhost:6379`.

### Invocation

```
/task-master tests/fixtures/sample-plan-simple/plan.md
```

### Expected Behavior

1. Phase 0: Plan discovered, REDIS_URL found in .env.
2. Phase 1: No clarification questions needed — plan is unambiguous.
3. Phase 2: Both research agents dispatched and complete.
4. Phase 3: Plan parsed into 3 tasks. Preview table shown. User approves.
5. Phase 4: 3 task files written to `tasks/_pending/`.
6. Phase 5: `validate-tasks.sh` exits 0. TASK-LOG.md written.

### Task files expected

| # | File | Depends On |
|---|------|------------|
| 001 | `001-rate-limiter-models.md` | — |
| 002 | `002-rate-limiter-service.md` | [001] |
| 003 | `003-rate-limiter-tests.md` | [002] |

### Pass Criteria

- [ ] Exactly 3 files created in `tasks/_pending/`
- [ ] `validate-tasks.sh tasks/_pending/` exits 0
- [ ] `002-rate-limiter-service.md` contains `BlockedBy: [001]`
- [ ] `003-rate-limiter-tests.md` contains `BlockedBy: [002]`
- [ ] Task 003 Testing section includes a full `@pytest.mark.live` test (not a stub) because REDIS_URL is in .env
- [ ] TASK-LOG.md written to `tasks/TASK-LOG.md`
- [ ] Delivery report shows: "3 tasks generated", "Pipeline validation: PASS"

### Failure Signals

- Fewer or more than 3 task files → plan parsing is wrong
- REDIS_URL present but task 003 has a BLOCKED stub → live test detection is broken
- validate-tasks.sh exits non-zero → a task file is missing a required section

---

## Test 2: Pressure — Empty Plan Folder

**Category:** Pressure
**Priority:** P0 (must halt gracefully, never crash)

### Setup

`plan/` directory exists but is empty. `plans/` directory does not exist. No argument passed.

```bash
mkdir -p plan/
# (no files placed inside)
```

### Invocation

```
/task-master
```

### Expected Behavior

Phase 0 discovers 0 plan files across both `plan/` and `plans/`. Halts immediately with a
user-facing message. No task files are created. No exceptions, no stack traces, no partial output.

### Pass Criteria

- [ ] No files created in `tasks/_pending/`
- [ ] Output includes: "No plans found. Run `/plan-architect` first."
- [ ] Output does NOT mention an error, exception, or traceback
- [ ] Skill terminates at Phase 0 — does not proceed to Phase 1

### Failure Signals

- Any file written to `tasks/_pending/` → gate logic is not enforced
- Error message mentions `/task-master` instead of `/plan-architect` → wrong recovery hint
- Skill reaches Phase 1 before halting → Phase 0 gate is bypassed

---

## Test 3: Pressure — Large Plan (25 Sections)

**Category:** Pressure
**Priority:** P1 (important resilience scenario)

### Setup

`plan/` contains a single 600-line plan file with 25 distinct implementation sections.
File: `tests/fixtures/sample-plan-large/plan.md`. No `.env` keys present except `DATABASE_URL`.

### Invocation

```
/task-master tests/fixtures/sample-plan-large/plan.md
```

### Expected Behavior

1. Phase 3: task count estimated at 25 — exceeds 15 threshold.
2. Large-plan warning shown: "This plan has 25 sections. Plans over 15 sections may produce
   tasks that are too large for a single context window. I'll split oversized sections."
3. Sections with > ~100 lines of implementation content are split into sub-tasks.
4. **Preview table shown before any files are written.** User must approve before Phase 4 begins.
5. Approximately 28–32 task files generated (25 original + splits).
6. Sub-numbered tasks use format: `005a`, `005b` (not `005-1`, `005-2`).
7. No individual task file exceeds 120 lines.
8. `validate-tasks.sh` exits 0.

### Pass Criteria

- [ ] Preview table shown via AskUserQuestion before any files written
- [ ] Sub-numbered tasks exist (at least 3 files with `a`/`b` suffix in filename)
- [ ] Zero task files exceed 120 lines (checked by `wc -l tasks/_pending/*.md`)
- [ ] `validate-tasks.sh tasks/_pending/` exits 0
- [ ] Delivery report shows total task count (not just 25)

### Verification Commands

```bash
# Count task files
ls tasks/_pending/*.md | wc -l

# Check no file exceeds 120 lines
for f in tasks/_pending/*.md; do
  lines=$(wc -l < "$f")
  if [ "$lines" -gt 120 ]; then
    echo "FAIL: $f has $lines lines"
  fi
done

# Check sub-tasks exist
ls tasks/_pending/ | grep -E '[0-9]{3}[ab]'
```

### Failure Signals

- Files written before preview table shown → approval gate bypassed
- All 25 tasks are exactly 25 files with no splits → large-plan logic not triggered
- Any file over 120 lines → task too large, splitting did not fire

---

## Test 4: Pressure — Missing .env Key for Integration

**Category:** Pressure
**Priority:** P1 (critical for correct live-test behavior)

### Setup

Plan references Stripe webhook handling. `.env` file does NOT contain `STRIPE_SECRET_KEY`.
All other common keys are present (DATABASE_URL, REDIS_URL).

Plan file contains a section titled "Stripe Webhook Handler" with implementation details
for verifying webhook signatures and processing payment events.

### Invocation

```
/task-master plan/stripe-webhook-plan.md
```

### Expected Behavior

1. Phase 0: `.env` keys loaded. `STRIPE_SECRET_KEY` is NOT found.
2. Phase 1: task-master asks: "I see this plan uses Stripe. I didn't find STRIPE_SECRET_KEY
   in .env. Should tasks include a BLOCKED note for live testing?"
3. Phase 4: Stripe webhook task is generated. Testing section includes a stub block.
4. Phase 5: Delivery report warns about blocked live test.

### Pass Criteria

- [ ] Stripe task file contains exactly:
  ```python
  # BLOCKED: STRIPE_SECRET_KEY not found in .env
  ```
- [ ] Delivery report includes: "1 task has BLOCKED live tests"
- [ ] The Stripe task is NOT skipped — it is fully generated with all 10 sections present
- [ ] Delivery report lists which key is missing: "STRIPE_SECRET_KEY"

### Distinction

Task is generated. Only the live test is blocked. The task file is complete and valid.
`validate-tasks.sh` must exit 0 — BLOCKED stubs are valid task content.

### Failure Signals

- Stripe task file missing from `tasks/_pending/` → task was wrongly skipped
- Delivery report shows no warning → BLOCKED detection is not working
- Live test is written as a real test (not stubbed) despite key being absent → key detection is broken

---

## Test 5: Pressure — Conflicting User Input

**Category:** Pressure
**Priority:** P1 (prevents silent overrides)

### Setup

Plan has 8 implementation sections mapping to 8 tasks (001–008). Tasks 004 and 005 are API
route handlers; tasks 001–003 are database models; tasks 006–008 are tests.

### Invocation Sequence

1. User runs `/task-master` on the plan.
2. Phase 1: User says "generate all tasks" when asked about scope.
3. Phase 3: Preview table shown with all 8 tasks. User approves.
4. *During Phase 4 generation*, user interrupts and says:
   "Actually, remove task 004 and 005, I only want the database tasks."

### Expected Behavior

task-master detects a contradiction between the earlier instruction ("generate all tasks",
"approved the preview table with all 8") and the new instruction ("remove 004 and 005").

Rather than silently overriding, task-master presents a clarifying question:

```
You asked to generate all tasks earlier and approved the 8-task preview.
Should I:
  A) Remove 004 and 005 as now requested (database tasks only remain)
  B) Keep all 8 tasks as originally approved
  C) Let me re-review the full list before deciding
```

task-master waits for the user's choice. Executes the clarified instruction.

### Pass Criteria

- [ ] AskUserQuestion shown — task-master does NOT silently remove 004 and 005
- [ ] Question body references both the original instruction and the new one
- [ ] Result matches user's clarified choice (whichever option they select)
- [ ] No task files written from the conflicting interpretation
- [ ] If user selects A: only tasks 001, 002, 003, 006, 007, 008 exist in `tasks/_pending/`
- [ ] If user selects B: all 8 tasks exist in `tasks/_pending/`

### Failure Signals

- Tasks 004 and 005 silently removed without asking → conflict detection not working
- Question asked but all 8 tasks written anyway → response not respected
- AskUserQuestion shows only the new instruction without context → contradiction not surfaced
