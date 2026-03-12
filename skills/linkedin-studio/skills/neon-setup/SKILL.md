---
name: ls:neon-setup
description: >
  PROACTIVELY sets up and validates the Neon PostgreSQL database for LinkedIn Studio.
  Runs migrations, seeds data, validates connection, and reports table status.
  Triggers on requests like 'set up the database', 'run migrations', 'initialize Neon',
  'check database status', or 'seed the AI phrases'.
model: haiku
context: fork
allowed-tools: Bash Read
metadata:
  version: "2.0.0"
---

# ls:neon-setup

Database setup and validation for LinkedIn Studio.

## Phase 1: Validate Connection
1. Check NEON_DATABASE_URL is set
2. Source `database/neon-utils.sh`
3. Run `neon_test` — if fails, show connection troubleshooting guide
4. Show connection info (host, database name, SSL status)

## Phase 2: Run Migrations
1. Check which migrations have been applied (query pg_tables for ls_ prefixed tables)
2. If no ls_ tables exist: run `neon_migrate database/migrations/001_initial.sql` then `neon_migrate database/migrations/002_schema_alignment.sql`
3. If tables exist without ls_ prefix: run only 002_schema_alignment.sql
4. If ls_ tables already exist: report "migrations already applied"
5. Show migration results

## Phase 3: Seed Data
1. Check if ls_ai_phrases_blocklist has data: `neon_query "SELECT COUNT(*) FROM ls_ai_phrases_blocklist"`
2. If empty: run `neon_migrate database/seed-data/ai-phrases.sql`
3. If populated: report count and skip

## Phase 4: Validate Schema
1. Query all ls_ tables: `neon_query "SELECT tablename FROM pg_tables WHERE tablename LIKE 'ls_%' ORDER BY tablename"`
2. For each table: count rows
3. Report summary table: table name, row count, status (OK/EMPTY)

## Phase 5: Report
Show summary:
- Connection: OK/FAIL
- Migrations: X of 2 applied
- Tables: X of 10 created
- Seed data: X rows in ai_phrases_blocklist
- Brand voice: configured/not configured (check ls_brand_voice_profile)

## Error Handling
| Error | Recovery |
|-------|---------|
| NEON_DATABASE_URL not set | Show setup instructions pointing to INTEGRATION-GUIDE.md |
| psql not installed | Show `brew install libpq` instructions |
| Connection refused | Show Neon dashboard link, check IP allowlist |
| Migration already applied | Skip, report as already applied |
