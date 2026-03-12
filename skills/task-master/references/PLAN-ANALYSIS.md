# PLAN-ANALYSIS.md — How task-master Parses Plan Files

This document defines the rules for discovering plan files, recognizing their structure,
and extracting implementation sections to convert into atomic task files.

---

## Section 1: Plan File Discovery

### Glob Patterns

Search for plan files in this priority order. Use the first directory that exists and
contains `.md` files:

```
plan/**/*.md
plans/**/*.md
plans/{system}/**/*.md
```

If none of those directories exist, fall back to:

```
**/*plan*.md        # any markdown file with "plan" in the name
**/*PLAN*.md
**/*spec*.md
```

### Sorting

When multiple plan files are found, sort by modification time descending (most recently
modified file first). This is the default candidate for extraction.

Command equivalent:

```bash
ls -lt plan/**/*.md | head -5
```

### Multi-Plan Disambiguation

When 2 or more plan files are found, do NOT auto-select. Use AskUserQuestion with
the following format:

```
Found multiple plan files. Which one should I extract tasks from?

1. plan/agents/openrouter-client.md  (modified 2026-03-01, ~4 impl sections, est. 4–6 tasks)
2. plan/agents/rate-limiter.md       (modified 2026-02-28, ~2 impl sections, est. 2–3 tasks)
3. plans/niche-scout/OVERVIEW.md     (modified 2026-02-25, ~6 impl sections, est. 6–10 tasks)

Enter a number, or type a path to a file not listed above.
```

The estimated task count shown to the user is based on Section 3 logic below — run
section detection before presenting the disambiguation prompt.

---

## Section 2: Plan Structure Recognition

### Patterns That Indicate an Implementation Section (Become Tasks)

These patterns identify content that should become one or more task files.

**Heading-based signals:**

```
## Phase 1:        → implementation section
## Phase 2:        → implementation section
## Step 1:         → implementation section
## Step N:         → implementation section
## Implementation  → implementation section (entire section)
### {Component}:   → implementation section (e.g., ### RateLimiterService:)
```

**Line-level signals (within a section):**

Lines beginning with any of these words (case-insensitive) are implementation steps:

```
Build ...
Implement ...
Create ...
Add ...
Modify ...
Extend ...
Write ...
Integrate ...
Refactor ...
```

**Code block signals:**

A fenced code block (``` ``` ```) containing a file path pattern is a strong signal that
a file is being created or modified:

```
# app/services/rate_limiter.py    ← file path comment = create/modify signal
from app.models import ...        ← import from project = dependency signal
```

Any code block with a shebang, `from app.`, `import app.`, or a file path comment
signals a task that involves that file.

### Patterns to SKIP (Not Tasks)

These are informational — do not generate task files from them.

**Heading-level skips:**

```
## Overview
## Architecture
## Background
## Goals
## Context
## Why
## Decision
## Motivation
## Appendix
```

**Line-level skips:**

Lines that start with these words are descriptive, not actionable:

```
Consider ...
Note: ...
TODO: ...     (plan-level TODOs, not implementation steps)
This ...
The system ...
Currently ...
```

**Bullet point skips:**

A bullet point is a description (not a task) when:
- It contains no verb in imperative mood
- It reads as a characteristic ("the service is stateless") rather than an action
- It is nested under a heading in the SKIP list above

---

## Section 3: Section Selection Logic

### Plans with Explicit Phases

When the plan uses `## Phase N:` or `## Step N:` headings:

- Each phase maps to **1 task by default**
- A phase maps to **2–3 tasks** when it contains more than 3 sub-bullets that each
  describe a distinct file or component

Detection rule for phase-to-task expansion:

```
count = number of sub-bullets under the phase heading
if count <= 3:   → 1 task for this phase
if count == 4-6: → 2 tasks (split at natural boundary: models/config first, logic second)
if count > 6:    → 3 tasks (infrastructure, core logic, integration/wiring)
```

Naming convention for split phases:

```
003a-phase-2-models.md
003b-phase-2-service.md
003c-phase-2-routes.md
```

### Plans with Component Sections

When the plan uses component headings (`### ServiceName:`, `### Models:`, `### Routes:`):

- Each top-level component heading = **1 task**
- Exception: if a component heading has its own sub-headings (nested `####`), treat
  each sub-heading as a separate task

Example:

```markdown
### Data Models         → 1 task (simple, no sub-headings)
### RateLimiterService  → 1 task (single class)
### API Routes          → 1 task (single router)
### Authentication
    #### JWT Middleware  → 1 task (sub-heading = separate)
    #### API Key Auth   → 1 task (sub-heading = separate)
```

---

## Section 4: Estimation

Use line count and sub-bullet depth to estimate the task file size category before writing.
This estimate also feeds into the `EstimatedContextWindow` frontmatter field.

### Size Categories

**Small (~40–60 lines of task content):**
- Single function or method implementation
- Simple data model with 2–4 fields
- Config change (add an env var, update a setting)
- Example: "Add `REDIS_URL` to `Settings`" or "Write `generate_uuid()` helper"

**Medium (~60–90 lines of task content):**
- A service class with 3–5 methods
- A route group (3–5 endpoints)
- A data model with relationships
- Example: "Implement `RateLimiterService`" or "Add Stripe webhook route"

**Large (~90–100 lines of task content):**
- A multi-file feature touching 3+ files
- A service with external dependencies (DB + Redis + HTTP client)
- An agent implementation end-to-end
- Example: "Implement NicheScout agent with DB persistence and OpenRouter calls"

**Warning trigger:**

If your task file draft reaches 95 lines and is not yet complete, emit this warning
before continuing:

```
WARNING: Task is approaching the 100-line limit (~95 lines so far).
Consider splitting into sub-tasks before proceeding.
Suggested split point: after [current checklist step description].
```

Do not exceed 100 lines. Split proactively.
