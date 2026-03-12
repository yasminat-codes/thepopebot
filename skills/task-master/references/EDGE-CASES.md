# EDGE-CASES.md — Pressure Test Scenarios for task-master

Four scenarios where task-master can produce wrong output or halt incorrectly.
Each entry defines the trigger, detection logic, and the required handling behavior.

---

## Pressure Test 1: Empty or Missing Plan Folder

### Trigger
User invokes task-master but `plan/` and `plans/` don't exist or contain no `.md` files.

### Detection
```
Glob "plan/**/*.md"   → 0 results
Glob "plans/**/*.md"  → 0 results
```
Both globs return empty. No fallback glob is attempted.

### Required Handling

**DO NOT fabricate tasks.** A task list invented without a source plan is meaningless and will
contradict the eventual real plan. It is better to halt cleanly than to produce noise.

Halt immediately with this exact message structure:

```
ERROR: No plans found.

task-master requires at least one .md file in plan/ or plans/ to generate tasks.

Recovery steps:
  1. Run /plan-architect first to generate a plan.
     Example: /plan-architect niche-scout

  2. If you already have a plan file elsewhere, move it into plans/:
     mv path/to/my-plan.md plans/my-plan.md

  3. Then re-run task-master.
```

Do not proceed past Phase 0 if this condition is met. Do not ask the user a Phase 1 interview
question before confirming a source plan exists.

---

## Pressure Test 2: Large Plan (20+ Implementation Phases)

### Trigger
A plan file is so detailed that naive extraction would produce an unmanageable task set.

### Signals — check all three

| Signal | Threshold | How to Detect |
|--------|-----------|---------------|
| File length | > 500 lines | `wc -l` on the plan file |
| Section count | > 20 distinct `##` or `###` implementation sections | Grep for heading markers |
| Section size | Any single section > 150 lines | Measure line span between headings |

### Required Handling

**Before generating any task file**, show a summary to the user:

```
LARGE PLAN DETECTED: plans/niche-scout.md
  Sections found: 24
  Estimated tasks: 24 (before splits)
  Oversized sections: 3 (each > 150 lines, will be split)

Proceeding with generation. Large sections will be split into sub-tasks.
```

**Split rule:** When a single plan section would produce a task file > 100 lines, split it
into 2–3 sub-tasks. Sub-tasks use alphabetic suffixes: `001a`, `001b`, `001c`.
Do not burn sequential numbers on sub-tasks (avoids gaps when sub-tasks are recombined later).

**Notify the user for each split performed:**

```
Split "Phase 4: LLM Pipeline Integration" → 3 sub-tasks
  → tasks/_pending/004a-llm-pipeline-client.md
  → tasks/_pending/004b-llm-pipeline-retry.md
  → tasks/_pending/004c-llm-pipeline-tests.md
  Reason: Section was 187 lines — exceeded 100-line task limit.
```

Sub-task `BlockedBy` logic: `004b` is blocked by `004a`; `004c` is blocked by `004b`.
The original parent number (004) is not used for any standalone task file.

**After generation, issue a final warning if total tasks > 20:**

```
WARNING: Large task set generated (28 tasks across 3 sub-task groups).
Recommend reviewing dependency ordering in tasks/_pending/ before running /specs-to-commit.
Check that no task has a BlockedBy pointing to a non-existent task number.
```

---

## Pressure Test 3: Conflicting User Input During Interview

### Trigger
The user's answers to Phase 1 interview questions contradict each other or contradict the
content detected in the plan file.

### Examples of Conflicting Input

- User says "generate all tasks" after previously saying "only Phase 1 tasks"
- User approves a task list of 5 tasks, then immediately asks to add a task for something
  that was not present anywhere in the source plan
- User says "skip testing tasks" but the plan has one or more sections explicitly titled
  "Testing", "Test Suite", or "Phase N: Tests"
- User changes the output directory mid-interview after having already confirmed the default

### Detection Logic

During Phase 1 interview, maintain an interview state record:
```
{
  "scope": null,       # "all" | "phase_N" | list of sections
  "task_list": null,   # confirmed list shown to user
  "output_dir": null,  # confirmed output path
  "skip_testing": null # true | false
}
```

Before writing any task file, compare each field against:
1. The current user instruction
2. The plan content (sections present in the source file)

A contradiction exists when the current instruction cannot be satisfied without ignoring a
prior confirmed instruction or fabricating content absent from the plan.

### Required Handling

**DO NOT silently resolve the contradiction.** Do not pick one side and proceed without
telling the user. Do not fabricate plan content to satisfy an additive request.

Halt the current phase and surface the conflict with an AskUserQuestion call:

```
CONFLICT DETECTED

You asked to: add a task for "authentication"
The plan contains: no section referencing authentication, login, JWT, or session

Which should I do?
  A) Follow the plan — generate only what the plan describes (no auth task added)
  B) Follow your instruction — add an auth task stub (note: no plan content to base it on)
  C) Pause — I'll re-read the plan and tell you which option is correct

Reply with A, B, or C.
```

If the user selects option B, add a clearly marked stub task:
```markdown
# Task {NNN}: {User-Requested Title} [NOT IN PLAN]
**Status:** PENDING
**BlockedBy:** []
**Note:** This task was added by user instruction. No plan content exists for it.
         Contents are a stub — fill in implementation details before starting.
```

Never silently proceed. Never pick a side without telling the user.

---

## Pressure Test 4: Integration Service with Missing .env Key

### Trigger
The plan references a third-party service (Stripe, OpenAI, Twilio, Google Drive, SendGrid,
Slack, etc.) but the expected `.env` key for that service is absent from the loaded `.env` file.

### Detection

During Phase 0, load and record which keys are present in `.env`:
```
LOADED_ENV_KEYS = {OPENROUTER_API_KEY, DATABASE_URL, REDIS_URL, ...}
```

During Phase 3 (plan analysis), detect integration services from plan text. Common signals:
- Service name in a section title or body ("Stripe webhook", "OpenAI call", "Twilio SMS")
- Import statements shown in plan code blocks (`import stripe`, `import openai`)
- Environment variable names mentioned inline (`STRIPE_SECRET_KEY`, `OPENAI_API_KEY`)

Cross-check each detected service against the expected key:

| Service Detected | Expected Key |
|-----------------|-------------|
| Stripe | STRIPE_SECRET_KEY or STRIPE_WEBHOOK_SECRET |
| OpenAI | OPENAI_API_KEY |
| OpenRouter | OPENROUTER_API_KEY |
| Twilio | TWILIO_AUTH_TOKEN |
| SendGrid | SENDGRID_API_KEY |
| Google Drive | GOOGLE_SERVICE_ACCOUNT_JSON |
| Slack | SLACK_BOT_TOKEN |

If expected key is NOT in `LOADED_ENV_KEYS` → the service has a missing key.

### Required Handling

**DO NOT skip the live testing section.** A missing key is a temporary blocker, not a reason
to omit the live test entirely. Future engineers need to know the test exists and what it needs.

**DO** include a stubbed live test with a `pytest.mark.skip` annotation and a BLOCKED label:

```python
# tests/live/test_stripe_live.py

import pytest

@pytest.mark.skip(reason="BLOCKED: STRIPE_SECRET_KEY not found in .env — add key to run live tests")
async def test_live_stripe_webhook():
    """
    Live test: POST a test webhook event to the Stripe handler and verify the
    event is processed and persisted to the database.

    Requires: STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET in .env
    """
    ...
```

**DO** add to the task's Success Criteria a conditional item:

```
5. If STRIPE_SECRET_KEY is available in .env: live webhook test passes:
   `uv run pytest tests/live/test_stripe_live.py -v -m live` exits 0
```

**DO** add to the task's Definition of Done a conditional checkbox:

```
- [ ] Live API test (requires STRIPE_SECRET_KEY in .env) — skip if key unavailable
```

**DO** log to the delivery report at the end of Phase 5:

```
DELIVERY REPORT — BLOCKED LIVE TESTS

  Task 004: Stripe webhook handler
    BLOCKED: STRIPE_SECRET_KEY not found in .env
    Test stub written to: tests/live/test_stripe_webhook_live.py
    Action needed: Add STRIPE_SECRET_KEY to .env, then run:
      uv run pytest tests/live/test_stripe_webhook_live.py -v -m live

  1 task has BLOCKED live tests. Add missing keys to .env to enable.
```

The stub must be a real `.py` file at the correct path — not a note in a markdown task file.
The test body can be minimal, but the decorator and docstring must be present.
