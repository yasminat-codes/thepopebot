# Changelog

## [1.2.0] — 2026-03-02

### Added
- **Phase 1.5: Neon Database Introspection** — Live schema inspection via psql or asyncpg before any planning begins. Falls back to Alembic migration history if DATABASE_URL unavailable.
- **`references/DATABASE-PLANNING.md`** — Complete database planning protocol: introspection commands, No Orphan Tables Rule, SQL generation standards, Alembic migration format, database interview questions, and DB anti-patterns.
- **`02-database.md` plan file** — New per-plan file for database design containing current schema context, relationship map (ASCII showing [EXISTING] + [NEW] tables), full SQL DDL with FK constraints and indexes, modified tables, and copy-paste Alembic migration stub.
- **No Orphan Tables enforcement** — Phase 4 and Phase 7 validation both verify every new table has a documented FK path to an anchor table. SQL without `REFERENCES` fails validation.
- **Round 2b interview questions** — Database-specific interview questions triggered when Phase 1.5 runs. Questions reference live table names from introspection.
- **Folder output format** — Plans are now a folder `plans/{topic}/` with 6 focused `.md` files instead of a single file. PLAN.md is the index; each concern has its own file.

### Changed
- **PLAN-TEMPLATE.md** — Rewritten to define the folder structure and per-file content contract for all 6 plan files. Each file template uses tables/checklists over prose.
- **SKILL.md Phase 5** — Now builds a 6-file folder, not a single .md file. References DATABASE-PLANNING.md for SQL generation.
- **SKILL.md Phase 7** — Writes folder to `plans/{topic}/`, archives previous to `plans/archive/{name}-v{N}/`.
- **validate-plan-output.sh** — Rewritten for folder structure. Checks: all 6 required files exist with content, `02-database.md` present if CREATE TABLE detected, no orphan tables (REFERENCES keyword), Alembic migration stub, ≥2 grep patterns, phase gates present, no stray placeholders.
- **Output Contract** — Updated to reflect folder structure and DB SQL requirements.
- **Quality Gate Table** — Phase 1.5 added as conditional blocker gate.
- **TodoWrite** — Added `p1b` task for Phase 1.5.
- **Anti-Rationalization Table** — Added 4 DB/folder rows.
- **Version** — Bumped to v1.2.0.

## [1.1.0] — 2026-03-01

### Added
- **Revamp Mode**: Dual-mode skill (CREATE vs REVAMP) for updating existing plans
- `references/REVAMP-MODE.md` — Complete revamp workflow with Phases 0R-8R
- Mode detection in Phase 0: auto-detects revamp triggers ("revamp", "update", "improve", "revisit", "redo")
- Focused interview (2 rounds instead of 3) for targeted updates
- Targeted research dispatch (only agents needed for changed sections)
- Semantic diff synthesis (Added/Modified/Removed/Unchanged)
- Plan archiving with version history (`plans/archive/{name}-v{N}.md`)
- Revamp anti-patterns and quick reference interview templates
- `references/RESILIENCE-ADVANCED.md` — Advanced resilience patterns (timeouts, dead letters, health checks, idempotency, monitoring)
- `references/PLAN-QUALITY.md` — Good vs bad plan characteristics and review checklist

### Changed
- CSO description updated with revamp trigger words
- Phase 0 now includes mode detection block
- Anti-Rationalization Table expanded with revamp vs rewrite decision rule
- RESILIENCE-PATTERNS.md split: core patterns 1-5 stay, advanced patterns 6-10 moved to RESILIENCE-ADVANCED.md
- PLAN-TEMPLATE.md trimmed: quality guide extracted to PLAN-QUALITY.md
- Reference Files Manifest updated to 11 entries (was 8)
- Total skill: 17 files, ~4,100 lines

## [1.0.0] — 2026-03-01

### Added
- Initial release
- 9-phase planning workflow (Initialize → Context → Interview → Research → Synthesis → Architecture → Review → Write → Handoff)
- Expert interview engine with 4 domain question banks (Automation, Integration, Data Pipeline, Feature)
- 3 parallel research agents (codebase patterns, web APIs, MCP context)
- Anti-pattern detection with 20+ documented anti-patterns
- Implementation complexity scoring (1-5 scale)
- Plan versioning and diffing
- Context loading intelligence (reads CLAUDE.md, context files, existing plans)
- Grep enforcement for battle-tested codebase searching
- Resilience pattern library (retry, circuit breaker, fallback, saga)
- Validation scripts (prerequisites, plan output, grep enforcement)
- Plan template with 10 required sections
- Pressure test scenarios (5 adversarial scenarios)
- Preference persistence between runs
