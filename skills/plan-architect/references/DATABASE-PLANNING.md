# Database Planning — Neon Integration Protocol

This reference governs all database design in plan-architect.
New tables are never designed in isolation. Every table must be planned
with full awareness of the live schema, and every new table must connect
to the existing system via foreign keys or a documented structural role.

---

## Phase 1.5: Neon Database Introspection

Run this phase immediately after Phase 1 (Context Loading) whenever any of
these are true:
- The feature description mentions "store", "save", "track", "record", "log"
- The user mentions tables, schema, database, or data model
- The plan template Section 4 would have content

**Do not guess the schema. Introspect it.**

### Step 1: Resolve Database URL

```bash
# Check env for DATABASE_URL
echo $DATABASE_URL
# If not set, check .env file:
grep DATABASE_URL .env 2>/dev/null || grep DATABASE_URL app/config.py 2>/dev/null
```

If DATABASE_URL is not available → skip to Step 4 (Migration History fallback).

### Step 2: Run Introspection (psql — preferred)

```bash
# Tables overview
psql "$DATABASE_URL" -c "
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;"

# Full column map
psql "$DATABASE_URL" -c "
SELECT
  table_name,
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_schema = 'public'
ORDER BY table_name, ordinal_position;" > .claude/plan-architect/db-schema.txt

# Foreign key relationships
psql "$DATABASE_URL" -c "
SELECT
  tc.table_name AS source_table,
  kcu.column_name AS source_column,
  ccu.table_name AS target_table,
  ccu.column_name AS target_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;" >> .claude/plan-architect/db-schema.txt

# Existing indexes
psql "$DATABASE_URL" -c "
SELECT tablename, indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;" >> .claude/plan-architect/db-schema.txt
```

### Step 3: Python Fallback (if psql unavailable)

```bash
uv run python -c "
import asyncio, asyncpg, os

async def introspect():
    url = os.environ['DATABASE_URL']
    conn = await asyncpg.connect(url)

    tables = await conn.fetch('''
        SELECT table_name FROM information_schema.tables
        WHERE table_schema='public' AND table_type='BASE TABLE'
        ORDER BY table_name
    ''')

    cols = await conn.fetch('''
        SELECT table_name, column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema='public'
        ORDER BY table_name, ordinal_position
    ''')

    fks = await conn.fetch('''
        SELECT tc.table_name AS src, kcu.column_name AS src_col,
               ccu.table_name AS tgt, ccu.column_name AS tgt_col
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu
          ON ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type='FOREIGN KEY' AND tc.table_schema='public'
    ''')

    print('=== TABLES ===')
    for t in tables:
        print(t['table_name'])

    print('\n=== COLUMNS ===')
    for c in cols:
        nullable = '' if c['is_nullable'] == 'NO' else '?'
        print(f\"{c['table_name']}.{c['column_name']}: {c['data_type']}{nullable}\")

    print('\n=== FOREIGN KEYS ===')
    for fk in fks:
        print(f\"{fk['src']}.{fk['src_col']} -> {fk['tgt']}.{fk['tgt_col']}\")

    await conn.close()

asyncio.run(introspect())
" > .claude/plan-architect/db-schema.txt
```

### Step 4: Migration History Fallback

If DATABASE_URL is not available, read Alembic migration files instead.

```bash
ls -la alembic/versions/ | tail -20
# Read the most recent 3 migrations to understand current schema state
```

### Step 5: Build the Schema Map

After introspection, write a summary table to use during planning:

```
Current tables:
| Table | Key Columns | Links To |
|-------|-------------|----------|
| users | id, email, created_at | — (root table) |
| industries | id, name, user_id | users.id |
| research_reports | id, industry_id, content | industries.id |
```

This table becomes the "Current Schema Context" in Section 4 of the plan.

---

## The No Orphan Tables Rule

**Every new table must satisfy at least one of these:**

1. **FK to an existing table** — Has a foreign key pointing to a table that already exists
2. **FK from an existing table** — An existing table will gain a FK pointing to this new table
3. **Junction table** — Explicitly resolves a many-to-many relationship between two existing tables
4. **Root system table** — Is a top-level entity with documented reason for having no parent (rare — requires explicit justification in Design Decisions)

**Enforcement during planning:**
Before finalizing any new table in the plan, check:
- "Which existing table does this table belong to or extend?"
- "If this table were deleted, what existing queries or features would break?"
- "Can I draw a path from this table to an anchor table (users, orgs, workspaces) in ≤ 3 FK hops?"

If the answer to all three is "nothing / no / no" → the table is an orphan → redesign it.

---

## Relationship Map Format

When adding Section 4 to a plan, always include an ASCII relationship diagram
that shows both **existing** and **new** tables together.

```
Legend: [EXISTING] = already in production  [NEW] = this plan adds it

[EXISTING: users]
    |
    +── id ──> [EXISTING: industries]
                    |
                    +── id ──> [NEW: industry_snapshots]   ← new table anchored here
                    |              |
                    |              +── snapshot_id ──> [NEW: snapshot_metrics]  ← new table
                    |
                    +── id ──> [EXISTING: research_reports]
```

Rules for the diagram:
- Every [NEW] table must have at least one arrow connecting it to an [EXISTING] table
- Arrows show direction of the FK (the table that holds the FK points to the table that has the PK)
- If a new table creates a many-to-many, show both ends

---

## SQL Generation Standards

All SQL in plans follows these conventions. These match the existing codebase UUID/timestamp pattern.

### New Table Template

```sql
-- table_name: one-sentence description of what this table holds
-- Linked to: existing_table.id via table_name.existing_table_id FK
CREATE TABLE table_name (
    id              VARCHAR(36)     DEFAULT gen_random_uuid()::text PRIMARY KEY,
    -- FK to anchor table (REQUIRED for non-root tables)
    existing_table_id  VARCHAR(36)  NOT NULL REFERENCES existing_table(id) ON DELETE CASCADE,
    -- Domain columns
    name            VARCHAR(255)    NOT NULL,
    status          VARCHAR(50)     NOT NULL DEFAULT 'pending',
    data            JSONB,
    -- Audit columns (always last, always present)
    created_at      TIMESTAMPTZ     DEFAULT NOW() NOT NULL,
    updated_at      TIMESTAMPTZ     DEFAULT NOW() NOT NULL
);

-- Index on every FK column (non-negotiable)
CREATE INDEX idx_table_name_existing_table_id ON table_name(existing_table_id);
-- Index on any column used in WHERE clauses
CREATE INDEX idx_table_name_status ON table_name(status);
-- Composite index if queried together
CREATE INDEX idx_table_name_existing_table_id_status ON table_name(existing_table_id, status);
```

### Modify Existing Table

```sql
-- Add column to existing table
ALTER TABLE existing_table
ADD COLUMN new_column VARCHAR(255);

-- Add FK to existing table pointing at a new table
ALTER TABLE existing_table
ADD COLUMN new_table_id VARCHAR(36) REFERENCES new_table(id) ON DELETE SET NULL;

CREATE INDEX idx_existing_table_new_table_id ON existing_table(new_table_id);
```

### Constraints Checklist

Before finalizing SQL, verify:
- [ ] Every FK column has a corresponding `CREATE INDEX`
- [ ] Varchar columns have explicit length limits (not VARCHAR without length)
- [ ] NOT NULL is set on required columns — don't let nullable sneak in as default
- [ ] `ON DELETE` behavior is explicit: `CASCADE`, `SET NULL`, or `RESTRICT` (not implicit)
- [ ] `created_at` and `updated_at` present on every table
- [ ] `status` columns use VARCHAR with a documented enum of valid values in a comment

---

## Alembic Migration Format

Every database plan must include a migration file stub.
This goes directly in the plan under "Migration Strategy" and is ready to drop into `alembic/versions/`.

```python
"""[Short description of what this migration does]

Revision ID: [leave as placeholder — Alembic generates on creation]
Revises: [leave as placeholder — fill in during implementation]
Create Date: [YYYY-MM-DD]

What this migration does:
- Creates: table_a, table_b
- Modifies: existing_table (adds column new_column)
- Indexes added: idx_table_a_fk_id, idx_table_b_fk_id

Rollback safety: YES — downgrade() drops only what upgrade() creates
"""
from alembic import op
import sqlalchemy as sa

revision = 'FILL_IN'
down_revision = 'FILL_IN_PREVIOUS'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'table_a',
        sa.Column('id', sa.String(36), nullable=False, server_default=sa.text("gen_random_uuid()::text")),
        sa.Column('existing_table_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()'), nullable=False),
        sa.ForeignKeyConstraint(['existing_table_id'], ['existing_table.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_table_a_existing_table_id', 'table_a', ['existing_table_id'])

    # Modify existing table
    op.add_column('existing_table', sa.Column('new_column', sa.String(255)))


def downgrade() -> None:
    op.drop_column('existing_table', 'new_column')
    op.drop_index('idx_table_a_existing_table_id', table_name='table_a')
    op.drop_table('table_a')
```

---

## Database Domain Interview Questions (Phase 2 Supplement)

Add these to Round 2 when the feature involves database changes.

**Schema Design:**
- What existing tables will this feature read from most heavily?
- Will new records be owned by a specific user, org, or other root entity?
- Should old records be soft-deleted (status flag) or hard-deleted?
- Is this data append-only (event log pattern) or mutable (update-in-place)?

**Query Patterns:**
- What are the 2-3 most common read queries? (This determines index strategy.)
- Will there be any queries that filter by date range or status? (Composite index needed.)
- Will this table ever be joined to other tables in a single query? (Which ones?)

**Volume & Growth:**
- How many rows will this table have in 30 days? In 1 year?
- Are there rows that expire or become stale? What's the cleanup strategy?
- Is there a tenant/isolation concern — does each user see only their own rows?

**Gap fills to apply (no question needed — add silently to plan):**
- Any FK column → add index automatically
- Any status column → document valid enum values in SQL comment
- Any table without soft-delete → note in Design Decisions: "hard-delete chosen; revisit if audit trail needed"

---

## Database Anti-Patterns

Catch these before the plan leaves Phase 5.

| Anti-Pattern | What to Do Instead |
|---|---|
| Table with no FK to any existing table | Apply No Orphan Tables Rule — find the anchor |
| VARCHAR column without length | Always specify: VARCHAR(50), VARCHAR(255), TEXT for unbounded |
| Missing index on FK column | Every FK column gets an index. No exceptions. |
| Missing `ON DELETE` behavior | Always explicit: CASCADE, SET NULL, or RESTRICT |
| No `created_at` / `updated_at` | Always present on every table — non-negotiable |
| Migration with no `downgrade()` | Every migration needs a working rollback |
| Planning new tables without checking existing ones | Phase 1.5 is mandatory — introspect first |
| Status column without documented valid values | Add a SQL comment listing valid statuses |
| Designing schema from memory | Read .claude/plan-architect/db-schema.txt after introspection |
| Skipping Phase 1.5 because "it's a small table" | No table is too small to need a relationship |
