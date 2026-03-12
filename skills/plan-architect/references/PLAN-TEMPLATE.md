# Plan Template — Folder Structure and Per-File Content

Every plan is a folder, never a single file. Non-verbose: tables and checklists over prose.
Every line earns its place. Comprehensive does not mean long — it means nothing is missing.

---

## Folder Structure

```
plans/{topic-kebab}/
├── PLAN.md              ← Index + metadata + navigation links
├── 01-overview.md       ← System overview, architecture, success criteria
├── 02-database.md       ← DB design: schema context, SQL, Alembic stub (omit if no DB)
├── 03-implementation.md ← Phased steps with file paths and verify commands
├── 04-resilience.md     ← Error scenarios, retry policy, circuit breakers
├── 05-testing.md        ← Coverage requirements, test tables, manual steps
└── 06-context.md        ← Context load order + grep patterns
```

Archive: `plans/archive/{topic}-v{N}/` for previous versions.

---

## PLAN.md — Index

```markdown
# {Title} — Plan

| Key | Value |
|-----|-------|
| Version | 1 |
| Date | YYYY-MM-DD |
| Author | plan-architect |
| Status | Draft |
| Complexity | [1-5 overall] |
| Est. Build Time | [N hours / N days] |
| Pipeline | plan-architect → /extract-tasks → /specs-to-commit |

## Files
- [01-overview.md](./01-overview.md) — System overview, architecture, success criteria
- [02-database.md](./02-database.md) — Database design and migration SQL
- [03-implementation.md](./03-implementation.md) — Phased implementation steps
- [04-resilience.md](./04-resilience.md) — Error handling and resilience strategy
- [05-testing.md](./05-testing.md) — Test coverage requirements
- [06-context.md](./06-context.md) — Context loading order and grep patterns

## Complexity Scores
| Section | Score | Justification |
|---------|-------|---------------|
| Database | [1-5] | [reason] |
| Core logic | [1-5] | [reason] |
| External integrations | [1-5] | [reason] |
| Error handling | [1-5] | [reason] |
| Testing | [1-5] | [reason] |
| **Overall** | **[1-5]** | [weighted summary] |

## Start Here
1. Read all 6 files in order — each one builds on the last
2. Start implementation with `03-implementation.md Phase 1`
3. Run grep patterns in `06-context.md` before writing any code
```

---

## 01-overview.md

```markdown
# Overview

## What
[One paragraph, plain language. What this does. Hand-to-stakeholder quality.]

## Why
[One paragraph. What problem it solves. Cost of not building it.]

## Who
| Role | Entity |
|------|--------|
| Triggered by | [person / schedule / event] |
| Consumes from | [upstream systems, APIs, tables] |
| Produces for | [downstream systems, users, tables] |
| Breaks if... | [stakeholders who care] |

## Success Criteria
Binary pass/fail. If you can't test it, it's not a criterion.

- [ ] [Criterion — specific, measurable]
- [ ] [Criterion — specific, measurable]
- [ ] [Criterion — specific, measurable]

## Architecture

### Component Diagram
ASCII only. Every component. Every arrow labelled.

```
[Trigger]
    |
    v
[Orchestrator] ──── reads ──── [existing_table]
    |
    v
[Service A] ──── calls ──── [External API]
    |
    +── on error ──── [retry / DLQ / skip]
    v
[new_table]
```

### Data Flow
| Step | Action | Source | Destination |
|------|--------|--------|-------------|
| 1 | [Trigger / input] | [source] | [destination] |
| 2 | [Transform / call] | [source] | [destination] |
| N | [Persist / deliver] | [source] | [destination] |

### Technology Choices
| Component | Technology | Justification |
|-----------|-----------|---------------|
| [component] | [lib/service] | [reference to existing pattern or specific technical reason] |

Never write "best practice" as justification. Always reference codebase or technical specifics.
```

---

## 02-database.md

Only exists when the feature requires schema changes.
→ See references/DATABASE-PLANNING.md for introspection commands and SQL standards.

```markdown
# Database Design

## Current Schema Context
Populated from Phase 1.5 introspection. Summary of relevant existing tables.

| Table | Key Columns | FK Relationships |
|-------|-------------|-----------------|
| [existing_table] | id, name, created_at | → users.id |
| [existing_table_2] | id, table1_id, data | → existing_table.id |

## Relationship Map
ASCII diagram showing new tables (marked [NEW]) alongside existing (marked [EXISTING]).
Every [NEW] table must have at least one arrow to an [EXISTING] table.

```
[EXISTING: users]
    |
    +── id ──> [EXISTING: industries]
                   |
                   +── id ──> [NEW: industry_snapshots]
                                  |
                                  +── snapshot_id ──> [NEW: snapshot_metrics]
```

## New Tables

### table_name
Purpose: [one sentence]
Linked to: [parent_table.id via table_name.parent_table_id FK]

```sql
-- table_name: [purpose]
-- Linked to: parent_table.id via parent_table_id FK
CREATE TABLE table_name (
    id                VARCHAR(36)   DEFAULT gen_random_uuid()::text PRIMARY KEY,
    parent_table_id   VARCHAR(36)   NOT NULL REFERENCES parent_table(id) ON DELETE CASCADE,
    name              VARCHAR(255)  NOT NULL,
    status            VARCHAR(50)   NOT NULL DEFAULT 'pending',
    -- valid statuses: pending | active | completed | failed
    data              JSONB,
    created_at        TIMESTAMPTZ   DEFAULT NOW() NOT NULL,
    updated_at        TIMESTAMPTZ   DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_table_name_parent_table_id ON table_name(parent_table_id);
CREATE INDEX idx_table_name_status ON table_name(status);
```

No Orphan Tables Checklist:
- [ ] FK column present — `parent_table_id REFERENCES parent_table(id)`
- [ ] Index on FK column — `CREATE INDEX idx_..._parent_table_id`
- [ ] `ON DELETE` behavior explicit — `CASCADE` / `SET NULL` / `RESTRICT`
- [ ] `created_at` / `updated_at` present
- [ ] Status values documented in SQL comment

## Modified Tables
| Table | Change | SQL | Reason |
|-------|--------|-----|--------|
| [existing_table] | ADD COLUMN | `ALTER TABLE existing_table ADD COLUMN col VARCHAR(255);` | [why] |

## Migration

Alembic migration file: `alembic/versions/[timestamp]_[description].py`

```python
"""[Short description]

Revision ID: FILL_IN
Revises: FILL_IN_PREVIOUS
Create Date: YYYY-MM-DD

Creates: table_name
Modifies: [existing_table if any]
Rollback safe: YES
"""
from alembic import op
import sqlalchemy as sa

revision = 'FILL_IN'
down_revision = 'FILL_IN_PREVIOUS'


def upgrade() -> None:
    op.create_table(
        'table_name',
        sa.Column('id', sa.String(36), nullable=False, server_default=sa.text("gen_random_uuid()::text")),
        sa.Column('parent_table_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['parent_table_id'], ['parent_table.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_table_name_parent_table_id', 'table_name', ['parent_table_id'])


def downgrade() -> None:
    op.drop_index('idx_table_name_parent_table_id', table_name='table_name')
    op.drop_table('table_name')
```

Migration checklist:
- [ ] `upgrade()` creates tables in dependency order (parent before child)
- [ ] `downgrade()` drops in reverse order (child before parent)
- [ ] Backward compatible: old code can run against new schema
- [ ] Rollback verified: `downgrade()` leaves DB in prior state
```

---

## 03-implementation.md

```markdown
# Implementation

## Phase 1: Foundation — Database + Configuration
Purpose: All schema, config, and skeleton code. Later phases depend on this.

- [ ] Step 1.1: [Task title]
  - File: `app/[path/to/file.py]`
  - What: [specific description]
  - Verify: `uv run python -c "from app.[module] import [symbol]; print('ok')"`

- [ ] Step 1.2: Run migration
  - File: `alembic/versions/[timestamp]_[description].py`
  - What: Copy migration stub from 02-database.md, fill in revision IDs
  - Verify: `uv run alembic upgrade head && uv run alembic current`

Complexity: [1-5]
Gate: Migration applied. All imports resolve. Tests pass.

## Phase 2: Core Logic
Purpose: [What this builds]

- [ ] Step 2.1: [Task]
  - File: `app/[path]`
  - What: [description]
  - Verify: `[command]`

Complexity: [1-5]
Gate: [What must be true]

## Phase N: Integration / Delivery
...

Complexity: [1-5]
Gate: All tests pass. `uv run pytest tests/ -v --tb=short`
```

---

## 04-resilience.md

```markdown
# Resilience Strategy

## Error Scenarios
| Error | Detection | Recovery | Fallback |
|-------|-----------|----------|----------|
| [External API down] | HTTP 5xx / timeout | Retry 3x with exp. backoff | Skip record, mark failed in DB |
| [Rate limit hit] | HTTP 429, Retry-After header | Honor Retry-After | Queue for next run |
| [LLM invalid JSON] | json.JSONDecodeError | Retry with lower temp | Store raw, flag for review |
| [DB unavailable] | SQLAlchemy connection error | Retry 3x with backoff | Fail fast, alert |

## Retry Policy
| Operation | Max Retries | Backoff | Jitter |
|-----------|-------------|---------|--------|
| LLM API call | 3 | Exponential (2s, 4s, 8s) | ±20% |
| External API | 3 | Exponential (2s, 4s, 8s) | ±20% |
| DB write | 2 | Linear (1s, 2s) | None |

## Circuit Breakers (if high-volume external calls)
| Service | Threshold | Open Duration | Half-Open Test |
|---------|-----------|--------------|----------------|
| [service] | 5 failures / 60s | 30s | 1 probe |

## Dead Letter Handling (if queue/batch)
- Failed records stored in: [table.column / queue name]
- Retention: [N days]
- Replay: [command / endpoint]
```

---

## 05-testing.md

```markdown
# Testing Strategy

## Coverage Requirements
| Layer | Minimum |
|-------|---------|
| Tools / services | > 90% |
| Agents / orchestrators | > 85% |
| API endpoints (happy path) | 100% |
| API endpoints (error paths) | > 80% |

## Unit Tests
| Module | Test File | Mock | Key Scenarios |
|--------|-----------|------|---------------|
| `app/services/[module].py` | `tests/unit/test_[module].py` | [external calls] | [3-5 scenarios] |

## Integration Tests
| Scenario | Setup | Assertion |
|----------|-------|-----------|
| [scenario] | [fixtures] | [expected result] |

## Manual Verification
After deploying:
1. [Step — exact action + expected result]
2. [Step]
3. [Step]
```

---

## 06-context.md

```markdown
# Context Loading and Grep Patterns

## Read These Files First (in order)
| File | Why |
|------|-----|
| `app/config.py` | All env vars and their defaults |
| `app/database.py` | Async session factory — do not reinvent |
| `app/services/openrouter.py` | LLM client with retry — reuse it |
| `[relevant existing module]` | [specific reason] |

## Do Not Reinvent
| File | What It Solves |
|------|----------------|
| `app/services/openrouter.py` | All LLM calls |
| `app/services/rate_limiter.py` | All rate limiting |
| `app/database.py` | Async DB sessions |

## Grep Patterns
Run before writing any code. Each reveals existing code to reuse or be aware of.

```bash
# Find existing similar implementations
grep -r "[pattern]" app/ --include="*.py" -l

# Find the model/table pattern we're extending
grep -r "class [RelatedModel]" app/ --include="*.py" -n

# Find all places that import the module we're building near
grep -r "from app.[module]" app/ --include="*.py" -n

# Find existing error handling pattern
grep -r "RetryableError\|_FailoverError" app/ --include="*.py" -n

# Find DB session usage pattern
grep -r "get_async_session\|async_session" app/ --include="*.py" -n

# Find existing tests for related module
find tests/ -name "test_[module]*.py"
```

Expected findings: [What you expect to find and what it means for implementation]
```

---

## Writing Quality Rules

These apply to every file in the plan folder:

| Rule | What it means |
|------|---------------|
| Non-verbose | Every line earns its place. Delete filler sentences. |
| Tables over prose | If it can be a table, it should be a table. |
| Checklists over paragraphs | Steps are checkboxes, not numbered paragraphs. |
| Verify commands are real | Every step's `Verify:` runs and returns a pass/fail. |
| No vague justifications | "best practice" is not allowed. Reference codebase or specifics. |
| SQL is production-quality | Copy-paste ready. Not pseudocode. |
| Migration is copy-paste ready | Fill in revision IDs, done. No manual writing required. |
| Architecture diagram has labels | Every arrow has a label. No unlabelled flows. |

→ See references/PLAN-QUALITY.md for good vs bad plan characteristics and the final review checklist.
