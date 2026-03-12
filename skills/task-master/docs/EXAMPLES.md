# task-master — Worked Examples
Version: 1.0.0 | Last updated: 2026-03-02

---

## Example 1: Simple 3-Task Feature

### Input: Plan Summary

Plan file: `plan/rate-limiter.md` (80 lines)
Topic: Adding a Redis-backed rate limiter service to a FastAPI app
Sections: models setup, service implementation, tests
REDIS_URL: present in `.env`

### Phase 0-1 Transcript (condensed)

```
[Phase 0] Loading memory... no saved preferences found.
[Phase 0] Scanning .env... found keys: DATABASE_URL, REDIS_URL, OPENAI_API_KEY
[Phase 0] Discovered 1 plan: plan/rate-limiter.md (80 lines)
[Phase 0] Auto-selected: plan/rate-limiter.md

[Phase 1] Reading plan... no ambiguous sections found.
          REDIS_URL found in .env — live tests will be written (not stubbed).
          No clarification questions needed.

[Phase 2] Dispatching codebase-scanner (sonnet)... dispatching grep-mcp-researcher (haiku)...
          [35s] Both agents returned results.
          Codebase: found TimestampMixin in app/models/base.py, async client pattern in openrouter.py
          GREP MCP: found redis sliding window patterns from 3 GitHub repos

[Phase 3] Parsing plan... identified 3 implementation sections.
          Building dependency graph: 001 → 002 → 003
```

### Preview Table (shown before any files written)

```
| # | Task Title | Est. Lines | Depends On | Has Live API Test? |
|---|-----------|-----------|-----------|-------------------|
| 001 | Rate Limiter Models | ~55 | — | No |
| 002 | Rate Limiter Service | ~90 | 001 | Yes (REDIS_URL ✓) |
| 003 | Rate Limiter Tests | ~75 | 002 | Yes (REDIS_URL ✓) |

3 tasks total. Ready to generate?
Options: [Proceed] [Modify task list] [Cancel]
```

User selects: **Proceed**

### Generated Task File: 001-rate-limiter-models.md (full example)

```markdown
# Task 001: Rate Limiter Models
**Status:** PENDING
**BlockedBy:** []
**EstimatedContextWindow:** small

---

## Summary

Create `RateLimitConfig` SQLAlchemy model in `app/models/rate_limit_config.py` with UUID
primary key, route_key, limit, and window_seconds fields. Write and run an Alembic migration
to create the corresponding `rate_limit_config` table.

---

## Files to Read Before Starting

- `app/models/base.py` — TimestampMixin fields and generate_uuid function before writing model
- `app/models/__init__.py` — Registration pattern; add new model here after creating it
- `alembic/versions/` — Read one existing migration to confirm the file format and import style
- `app/config.py` — Confirm DATABASE_URL is set (required for migration to run)

---

## Files to Modify or Create

| Action | Path | What Changes |
|--------|------|--------------|
| CREATE | `app/models/rate_limit_config.py` | New RateLimitConfig model |
| MODIFY | `app/models/__init__.py` | Import and register RateLimitConfig |
| CREATE | `alembic/versions/XXXX_add_rate_limit_config.py` | Migration: CREATE TABLE rate_limit_config |
| CREATE | `tests/unit/test_rate_limit_config_model.py` | Unit tests for model instantiation |

---

## Implementation Checklist

- [ ] Read `app/models/base.py` — confirm TimestampMixin fields and generate_uuid signature
      — Success: `grep "TimestampMixin\|generate_uuid" app/models/base.py` returns both
- [ ] Create `app/models/rate_limit_config.py` with RateLimitConfig class
      — Success: `uv run python -c "from app.models.rate_limit_config import RateLimitConfig"` exits 0
- [ ] Register model in `app/models/__init__.py`
      — Success: `grep "RateLimitConfig" app/models/__init__.py` returns the import line
- [ ] Generate Alembic migration: `uv run alembic revision --autogenerate -m "add_rate_limit_config"`
      — Success: new file appears in `alembic/versions/`
- [ ] Run migration: `uv run alembic upgrade head`
      — Success: `uv run alembic current` shows the new revision
- [ ] Write unit tests in `tests/unit/test_rate_limit_config_model.py`
      — Success: `uv run pytest tests/unit/test_rate_limit_config_model.py -v` exits 0
- [ ] Run lint on new model file
      — Success: `uv run ruff check --fix app/models/rate_limit_config.py` exits 0
- [ ] Verify type hints
      — Success: `uv run mypy app/models/rate_limit_config.py` exits 0

---

## Success Criteria

1. Model importable: `uv run python -c "from app.models.rate_limit_config import RateLimitConfig"` exits 0
2. Unit tests pass: `uv run pytest tests/unit/test_rate_limit_config_model.py -v --tb=short` exits 0
3. All tests pass: `uv run pytest tests/ -v --tb=short` exits 0
4. No lint errors: `uv run ruff check app/models/rate_limit_config.py` exits 0
5. Migration applied: `uv run alembic current` shows migration as current head

---

## Testing

### Unit Tests

File: `tests/unit/test_rate_limit_config_model.py`

- `test_model_instantiation_with_defaults` — create RateLimitConfig with required fields, assert id is UUID
- `test_timestamp_mixin_fields` — assert created_at and updated_at are set on instantiation
- `test_route_key_field` — assert route_key accepts string values
- `test_limit_and_window_fields` — assert limit and window_seconds accept int values

### Integration Tests

No integration tests for this task — model-only change. Covered by migration smoke test
and the service integration tests in task 003.

### Live API Tests

No external API involved. Migration runs against the local test database.

---

## Task Management

At task start, run:
```bash
mv tasks/_pending/001-rate-limiter-models.md tasks/_in-progress/001-rate-limiter-models.md
```

At task complete (all tests pass), run:
```bash
mv tasks/_in-progress/001-rate-limiter-models.md tasks/_completed/001-rate-limiter-models.md
```

---

## Definition of Done

- [ ] All Implementation Checklist items checked
- [ ] All 5 Success Criteria met
- [ ] `uv run pytest tests/ -v --tb=short` exits 0
- [ ] `uv run ruff check --fix app/models/rate_limit_config.py` exits 0
- [ ] `uv run mypy app/models/rate_limit_config.py` exits 0
- [ ] Migration applied and `alembic current` is up to date
- [ ] No `print()` in production code
- [ ] Task file moved to `tasks/_completed/`
```

### Delivery Report

```
✓ 3 tasks generated in tasks/_pending/
✓ Dependency chain: 001 → 002 → 003
✓ Live API tests: 2 tasks require REDIS_URL (002, 003) — key found in .env, tests written fully
✓ TASK-LOG.md written to tasks/TASK-LOG.md
✓ Pipeline validation: PASS (validate-tasks.sh exited 0)
Next step: Run /specs-to-commit to begin implementation
```

---

## Example 2: Large Plan with Sub-Tasks

### Input: Large Plan Excerpt

Plan file: `plans/niche-scout/PLAN.md` (600 lines, 20 implementation sections)
Topic: Niche Scout Agent System
REDDIT_CLIENT_ID: NOT in .env
REDDIT_CLIENT_SECRET: NOT in .env
DATABASE_URL, REDIS_URL: present in .env

### Preview Table (20+ tasks shown before writing)

```
⚠ Large plan detected: 20 sections found. Plans over 15 sections may produce tasks
  too large for a single context window. I'll split sections over ~100 lines.
  Sections 9 (Reddit Scraper) and 12 (Pipeline Orchestrator) will be split.

| # | Task Title | Est. Lines | Depends On | Has Live API Test? |
|---|-----------|-----------|-----------|-------------------|
| 001 | Database Migrations | ~70 | — | No |
| 002 | NicheResearchRun Model | ~55 | 001 | No |
| 003 | SubredditScraped Model | ~50 | 001 | No |
| 004 | NicheOpportunity Model | ~50 | 001 | No |
| 005 | NicheKeyword Model | ~45 | 004 | No |
| 006 | ScoutReport Model | ~50 | 001 | No |
| 007 | OpenRouter LLM Integration | ~85 | 002 | No |
| 008 | Reddit Rate Limiter | ~70 | — | No |
| 009a | Reddit Scraper — Auth & Headers | ~80 | 008 | BLOCKED (REDDIT_CLIENT_ID) |
| 009b | Reddit Scraper — Post Fetching | ~75 | 009a | BLOCKED (REDDIT_CLIENT_ID) |
| 010 | Opportunity Scorer Agent | ~80 | 007, 003 | No |
| 011 | Report Generator Agent | ~75 | 007, 010 | No |
| 012a | Pipeline Orchestrator — Phases 1-3 | ~85 | 009b, 010 | No |
| 012b | Pipeline Orchestrator — Phases 4-6 | ~80 | 012a | No |
| 013 | Webhook Handler Routes | ~70 | 012b | No |
| 014 | Background Job Scheduler | ~60 | 013 | No |
| 015 | Unit Tests — Models | ~65 | 006 | No |
| 016 | Unit Tests — Services | ~80 | 009b, 007 | No |
| 017 | Unit Tests — Agents | ~70 | 011 | No |
| 018 | Integration Tests | ~85 | 012b | No |
| 019 | Live API Tests — Reddit | ~60 | 009b | BLOCKED (REDDIT_CLIENT_ID) |
| 020 | Deployment Config | ~55 | 018 | No |

22 tasks total (2 splits from sections 9 and 12).
Ready to generate?
Options: [Proceed] [Modify task list] [Cancel]
```

### How a Split Task Looks

Task `009a` (Reddit Scraper — Auth & Headers) and `009b` (Reddit Scraper — Post Fetching)
each reference each other in their summaries:

```markdown
# Task 009a: Reddit Scraper — Auth & Headers
**Status:** PENDING
**BlockedBy:** [008]
**EstimatedContextWindow:** medium

## Summary

Implement `RedditScraperService.__init__` and `_build_reddit_headers()` in
`app/services/reddit_scraper.py`. Sets up OAuth2 client credentials flow and
Redis-cached token management. Part 1 of 2 — see task 009b for post fetching.

...

## Testing

### Live API Tests

```python
# tests/live/test_reddit_scraper_live.py
# BLOCKED: REDDIT_CLIENT_ID not found in .env
# Uncomment and run manually once key is available.

# import pytest
# from app.services.reddit_scraper import RedditScraperService
#
# @pytest.mark.live
# async def test_live_oauth_token_fetch():
#     scraper = RedditScraperService()
#     token = await scraper._get_oauth_token()
#     assert token is not None
```
```

### Delivery Report (large plan)

```
✓ 22 tasks generated in tasks/_pending/
  (20 plan sections, 2 split into sub-tasks: 009a/009b, 012a/012b)
✓ Dependency chain: 001 → 002,003,004,006 → ... → 020
✓ Live API tests:
  - 2 tasks have BLOCKED live tests (009a, 019): REDDIT_CLIENT_ID not found in .env
  - 0 tasks have fully written live tests (no other external API keys found)
⚠ 2 tasks have BLOCKED live tests — add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET to .env to unlock
✓ TASK-LOG.md written to tasks/TASK-LOG.md
✓ Pipeline validation: PASS (validate-tasks.sh exited 0)
Next step: Run /specs-to-commit to begin implementation (start with task 001)
```
