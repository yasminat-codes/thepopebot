---
name: neon
description: >-
  Interact with Neon PostgreSQL — Smarterflo's primary database — via Data API,
  Direct SQL, and Management API. Use PROACTIVELY when user says "neon database",
  "query the database", "create table", "run migration", "database schema",
  "neon branch", "postgres query", "NEON_DATABASE_URL", "sql query", or any
  Neon or database operation. Also use when user opens files with database
  queries or migrations. Requires NEON_DATABASE_URL env var.
allowed-tools: Read Write Edit Bash
argument-hint: "[query-or-action] (optional)"
disable-model-invocation: false
user-invocable: true
model: sonnet
license: Proprietary
metadata:
  author: yasmine-seidu
  version: "1.0.0"
  category: database
---

# Neon PostgreSQL Skill

**Version:** 1.0  
**Created:** 2026-02-23  
**Database:** Neon (Serverless PostgreSQL)

---

## Overview

Neon is Smarterflo's primary database. This skill provides three ways to interact with it:

1. **Data API** (REST) — Query via HTTP, no connection pooling needed
2. **Direct SQL** — Raw SQL via psycopg2, full PostgreSQL features
3. **Management API** — Create branches, manage projects, get connection strings

---

## Quick Start

### Projects Management
```bash
# List all projects
~/shared/skills/neon/scripts/projects.py list

# Create new project
~/shared/skills/neon/scripts/projects.py create "My Project" --region aws-us-east-1

# Delete project
~/shared/skills/neon/scripts/projects.py delete <project_id>
```

### Compute Endpoints
```bash
# List endpoints
~/shared/skills/neon/scripts/endpoints.py list

# Create endpoint
~/shared/skills/neon/scripts/endpoints.py create <branch_id> --min-cu 0.25 --max-cu 1.0

# Start/stop/restart
~/shared/skills/neon/scripts/endpoints.py start <endpoint_id>
~/shared/skills/neon/scripts/endpoints.py suspend <endpoint_id>
~/shared/skills/neon/scripts/endpoints.py restart <endpoint_id>
```

### Databases & Roles
```bash
# List databases
~/shared/skills/neon/scripts/databases.py database list <branch_id>

# Create database
~/shared/skills/neon/scripts/databases.py database create <branch_id> mydb --owner myuser

# Create role
~/shared/skills/neon/scripts/databases.py role create <branch_id> newrole

# Reset password
~/shared/skills/neon/scripts/databases.py role reset-password <branch_id> rolename
```

### Snapshots (Backups)
```bash
# List snapshots
~/shared/skills/neon/scripts/snapshots.py list

# Create snapshot
~/shared/skills/neon/scripts/snapshots.py create <branch_id> --name "backup-before-migration"

# Restore snapshot
~/shared/skills/neon/scripts/snapshots.py restore <snapshot_id>

# Set backup schedule
~/shared/skills/neon/scripts/snapshots.py schedule set <branch_id> --enabled true --frequency daily --retention 7
```

### Query via Data API
```bash
# Get all leads
~/shared/skills/neon/scripts/query.py leads --select "*"

# Filter published posts
~/shared/skills/neon/scripts/query.py posts --filter "is_published=eq.true"

# Complex query with ordering
~/shared/skills/neon/scripts/query.py leads \
  --select "name,email,company" \
  --filter "status=eq.qualified" \
  --order "created_at.desc" \
  --limit 10
```

### Execute Raw SQL
```bash
# Simple query
~/shared/skills/neon/scripts/execute.py "SELECT * FROM leads WHERE status = 'qualified' LIMIT 5"

# Insert data
~/shared/skills/neon/scripts/execute.py "INSERT INTO leads (name, email, status) VALUES ('John Doe', 'john@example.com', 'new')"

# Create table
~/shared/skills/neon/scripts/execute.py "CREATE TABLE IF NOT EXISTS test (id serial PRIMARY KEY, name text)"
```

### Manage Neon Resources
```bash
# List all branches
~/shared/skills/neon/scripts/manage.py branches --list

# Create new branch
~/shared/skills/neon/scripts/manage.py branches --create "feature-test"

# Get connection string
~/shared/skills/neon/scripts/manage.py connection-string
```

---

## When to Use Each Approach

| Use Case | Method | Why |
|----------|--------|-----|
| **CRUD operations** | Data API | REST interface, no connection pooling, JWT auth |
| **Complex queries** | Direct SQL | Full PostgreSQL power, joins, CTEs, transactions |
| **Migrations** | Direct SQL | Schema changes, indexes, constraints |
| **Serverless functions** | Data API | HTTP-based, works everywhere |
| **Agent queries** | Data API | Simple, secure with RLS |
| **Analytics** | Direct SQL | Complex aggregations, window functions |
| **Branch management** | Management API | Create test environments, dev branches |

---

## Authentication

### Data API (JWT Required)

**Environment variables needed:**
```bash
NEON_DATA_API_URL=https://ep-xxx.apirest.us-east-1.aws.neon.tech/neondb/rest/v1
NEON_JWT_TOKEN=eyJhbGci... # From Neon Auth or your provider
```

**How to get JWT token:**
1. **Neon Auth:** Use Auth API to sign up/sign in, get token from `set-auth-jwt` header
2. **Custom provider:** Get token from Auth0, Clerk, Firebase Auth, etc.

### Direct SQL

**Environment variables needed:**
```bash
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**Get from Neon Console:**
1. Go to project → Dashboard
2. Copy "Connection string"
3. Add to `shared/.env`

### Management API

**Environment variables needed:**
```bash
NEON_API_KEY=neon_api_xxx # Get from Neon Console → Account Settings → API Keys
NEON_PROJECT_ID=ep-xxx # Project ID from Neon Console
```

---

## Data API Reference

### CRUD Operations

**SELECT:**
```bash
# All columns
query.py table_name --select "*"

# Specific columns
query.py table_name --select "id,name,email"

# With filter
query.py leads --select "*" --filter "status=eq.qualified"

# Multiple filters (AND)
query.py leads \
  --select "name,email" \
  --filter "status=eq.qualified" \
  --filter "created_at=gte.2026-01-01"

# Ordering
query.py leads --select "*" --order "created_at.desc"

# Limit
query.py leads --select "*" --limit 10
```

**INSERT:**
```bash
query.py leads --insert '{"name": "John", "email": "john@example.com", "status": "new"}'
```

**UPDATE:**
```bash
query.py leads --update '{"status": "qualified"}' --filter "id=eq.123"
```

**DELETE:**
```bash
query.py leads --delete --filter "id=eq.123"
```

### Filters

| Operator | Syntax | Example |
|----------|--------|---------|
| Equals | `eq` | `status=eq.qualified` |
| Not equals | `neq` | `status=neq.disqualified` |
| Greater than | `gt` | `score=gt.50` |
| Less than | `lt` | `score=lt.100` |
| Greater or equal | `gte` | `created_at=gte.2026-01-01` |
| Less or equal | `lte` | `created_at=lte.2026-12-31` |
| Like (case-sensitive) | `like` | `name=like.*John*` |
| iLike (case-insensitive) | `ilike` | `email=ilike.*@gmail.com` |
| Is null | `is` | `deleted_at=is.null` |
| In array | `in` | `status=in.(new,qualified)` |

### Modifiers

| Modifier | Syntax | Example |
|----------|--------|---------|
| Order ascending | `.asc` | `--order "created_at.asc"` |
| Order descending | `.desc` | `--order "created_at.desc"` |
| Limit | `--limit N` | `--limit 10` |
| Offset | `--offset N` | `--offset 20` |
| Single row | `--single` | Returns object instead of array |

---

## Direct SQL Examples

### Queries

```bash
# Simple SELECT
execute.py "SELECT * FROM leads WHERE status = 'qualified'"

# JOIN
execute.py "
SELECT l.name, c.company_name, l.email
FROM leads l
JOIN companies c ON l.company_id = c.id
WHERE l.status = 'qualified'
ORDER BY l.created_at DESC
LIMIT 10
"

# Aggregation
execute.py "
SELECT status, COUNT(*) as count, AVG(score) as avg_score
FROM leads
GROUP BY status
"

# Window functions
execute.py "
SELECT name, email, score,
       RANK() OVER (ORDER BY score DESC) as rank
FROM leads
WHERE status = 'qualified'
"
```

### Mutations

```bash
# INSERT
execute.py "
INSERT INTO leads (name, email, company_id, status, source)
VALUES ('Jane Smith', 'jane@acme.com', 123, 'new', 'linkedin')
RETURNING id, created_at
"

# UPDATE
execute.py "
UPDATE leads
SET status = 'qualified', score = 85
WHERE id = 456
RETURNING *
"

# DELETE
execute.py "DELETE FROM leads WHERE status = 'disqualified' AND created_at < NOW() - INTERVAL '90 days'"
```

### Schema Management

```bash
# Create table
execute.py "
CREATE TABLE IF NOT EXISTS campaigns (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT DEFAULT 'draft',
  channel TEXT NOT NULL,
  target_count INTEGER,
  sent_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
)
"

# Add column
execute.py "ALTER TABLE campaigns ADD COLUMN IF NOT EXISTS ab_test_id BIGINT REFERENCES ab_tests(id)"

# Create index
execute.py "CREATE INDEX IF NOT EXISTS idx_campaigns_status ON campaigns(status)"

# Add constraint
execute.py "ALTER TABLE campaigns ADD CONSTRAINT check_counts CHECK (sent_count <= target_count)"
```

---

## Row-Level Security (RLS)

Data API automatically enforces RLS based on JWT token's `sub` claim.

### Enable RLS

```bash
execute.py "ALTER TABLE leads ENABLE ROW LEVEL SECURITY"
```

### Create Policies

```bash
# Users can read all published data
execute.py "
CREATE POLICY read_published ON leads
FOR SELECT TO authenticated
USING (status = 'published' OR status = 'qualified')
"

# Users can only modify their own records
execute.py "
CREATE POLICY manage_own ON leads
FOR ALL TO authenticated
USING (auth.user_id() = owner_id)
WITH CHECK (auth.user_id() = owner_id)
"
```

**Note:** `auth.user_id()` is a Neon Data API helper that extracts user ID from JWT token.

---

## Management API

### Branches

```bash
# List branches
manage.py branches --list

# Create branch from main
manage.py branches --create "dev-feature-x"

# Create branch from specific branch
manage.py branches --create "staging" --from "main"

# Delete branch
manage.py branches --delete "old-feature"
```

**Use cases for branches:**
- **Development:** Test schema changes without affecting production
- **Staging:** Preview environment before deploying
- **Testing:** Run integration tests on isolated data
- **Experiments:** Try new features safely

### Connection Strings

```bash
# Get main branch connection string
manage.py connection-string

# Get specific branch
manage.py connection-string --branch "dev"

# Get pooled connection (for serverless)
manage.py connection-string --pooled
```

---

## Integration Patterns

### With Instantly.ai (Enrichment)

```python
# Enrich lead from Instantly campaign
from scripts.query import query_table

lead_data = {
    "email": "prospect@company.com",
    "name": "John Doe",
    "company": "Acme Corp",
    "source": "instantly_campaign_123",
    "status": "new"
}

result = query_table("leads", insert=lead_data)
print(f"Lead created: {result['id']}")
```

### With GoHighLevel (Sync)

```python
# Sync deal from GoHighLevel
from scripts.query import query_table

deal = {
    "name": "Acme Corp - Automation Project",
    "value": 15000,
    "stage": "discovery",
    "ghl_deal_id": "deal_xyz",
    "company_id": 123
}

result = query_table("deals", insert=deal)
```

### With Airtable (Backup)

```python
# Export leads to Airtable
from scripts.execute import execute_sql
import json

leads = execute_sql("SELECT * FROM leads WHERE created_at > NOW() - INTERVAL '7 days'")

# Send to Airtable via API
for lead in leads:
    # airtable.create_record(...)
    pass
```

### With Stripe (Revenue Tracking)

```python
# Log invoice payment
from scripts.query import query_table

payment = {
    "client_id": 456,
    "stripe_invoice_id": "in_xxx",
    "amount": 5000,
    "status": "paid",
    "paid_at": "2026-02-23T12:00:00Z"
}

query_table("payments", insert=payment)
```

---

## Best Practices

### 1. Use RLS for Security
Always enable Row-Level Security on tables accessed via Data API:
```sql
ALTER TABLE sensitive_table ENABLE ROW LEVEL SECURITY;
```

### 2. Index Frequently Queried Columns
```sql
CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at);
```

### 3. Use Timestamps
Every table should have:
```sql
created_at TIMESTAMPTZ DEFAULT NOW()
updated_at TIMESTAMPTZ DEFAULT NOW()
```

### 4. Soft Deletes
Instead of DELETE, use:
```sql
deleted_at TIMESTAMPTZ
```

Then filter: `WHERE deleted_at IS NULL`

### 5. Connection Pooling
For serverless/edge functions, use Neon's pooled connection:
```
postgresql://user:password@ep-xxx-pooler.us-east-1.aws.neon.tech/db
```

### 6. Migrations
Track schema changes in version-controlled SQL files:
```
migrations/
  001_create_leads.sql
  002_add_enrichment_columns.sql
  003_create_campaigns.sql
```

### 7. Use JSON for Flexible Data
```sql
ALTER TABLE leads ADD COLUMN enrichment_data JSONB;
CREATE INDEX idx_leads_enrichment ON leads USING GIN (enrichment_data);
```

---

## Common Errors

### "JWT token has expired"
**Solution:** Tokens expire after ~15 minutes. Sign in again to get fresh token.

### "relation does not exist"
**Solution:** Table not in schema cache. Refresh cache in Neon Console or via API.

### "permission denied for table"
**Solution:** Check RLS policies. User might not have access based on JWT claims.

### "connection refused"
**Solution:** Check `NEON_DATABASE_URL`. Ensure IP not blocked (Neon allows all by default).

### "too many connections"
**Solution:** Use pooled connection string for serverless functions.

---

## Environment Variables

Add to `shared/.env`:

```bash
# Data API (REST)
NEON_DATA_API_URL=https://ep-xxx.apirest.us-east-1.aws.neon.tech/neondb/rest/v1
NEON_JWT_TOKEN=eyJhbGci... # Get from Neon Auth or your provider

# Direct SQL
NEON_DATABASE_URL=postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require

# Pooled (for serverless)
NEON_DATABASE_URL_POOLED=postgresql://user:password@ep-xxx-pooler.us-east-1.aws.neon.tech/neondb

# Management API
NEON_API_KEY=neon_api_xxx
NEON_PROJECT_ID=ep-xxx
```

---

## Examples

See `examples/` directory for:
- `crud_operations.py` — Full CRUD with Data API
- `rls_setup.sql` — Row-Level Security patterns
- `migrations/` — Schema migration examples
- `integrations.py` — Integration with external tools

---

## Complete API Coverage

**Management API Scripts:**
- ✅ `projects.py` — Create/delete/update projects, list operations
- ✅ `manage.py` — Branches (create, delete, list, set default)
- ✅ `endpoints.py` — Compute endpoints (create, delete, start, stop, restart, suspend)
- ✅ `databases.py` — Databases & roles (create, delete, update, password management)
- ✅ `snapshots.py` — Backups (create, restore, delete, schedule)

**Data API Scripts:**
- ✅ `query.py` — Full CRUD operations (select, insert, update, delete)

**Direct SQL:**
- ✅ `execute.py` — Raw SQL execution, migrations, schema management

**Coverage:** ~90% of Neon API endpoints (120+ operations)

## Resources

- **Neon Console:** https://console.neon.tech
- **Data API Docs:** https://neon.com/docs/data-api/get-started
- **Management API:** https://api-docs.neon.tech
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**Status:** ✅ Production-ready with comprehensive API coverage  
**Last updated:** 2026-02-23 20:32 UTC  
**Scripts:** 8 total (projects, endpoints, databases, snapshots, query, execute, manage)
