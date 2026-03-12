# Plan: Rate Limiter Service
**Date:** 2026-03-02
**Status:** APPROVED
**Complexity:** 2/5

---

## Overview

This plan adds a Redis-backed rate limiter service to the FastAPI application.
The rate limiter uses a sliding window algorithm to track request counts per key
over a configurable time window. It is designed to protect high-traffic API routes
from abuse and ensure fair usage across clients.

The sliding window implementation uses Redis sorted sets: each request is recorded
as a score (Unix timestamp in milliseconds), old entries outside the window are
pruned on each check, and the count of remaining entries determines whether the
limit is breached. This approach is exact (not approximate like token buckets) and
handles clock skew tolerantly.

Architecture reference: `app/services/openrouter.py` for async client pattern.
Existing rate limiter pattern: none — this is a new service.

---

## Section 1: Database / Models Setup

Add the `RateLimitConfig` table to store configurable rate limit settings per route.
This allows per-route limits to be adjusted at runtime without code changes.

**What to build:**
- `app/models/rate_limit_config.py` — SQLAlchemy model with: `id` (UUID), `route_key` (str),
  `limit` (int), `window_seconds` (int), `created_at`, `updated_at`
- Alembic migration: `alembic/versions/XXXX_add_rate_limit_config.py`
- Register model in `app/models/__init__.py`

**Why this comes first:** The service layer reads limits from this table. The model
must exist before the service can query it.

**Grep patterns to search:**
- `grep -rn "TimestampMixin" app/models/` — confirm base mixin pattern
- `grep -rn "generate_uuid" app/models/base.py` — confirm UUID generation function
- `grep -rn "class.*Base" alembic/versions/` — confirm migration pattern

---

## Section 2: Rate Limiter Service Implementation

Implement the `RateLimiterService` class in `app/services/rate_limiter.py` using
the Redis sliding window algorithm.

**What to build:**
- `app/services/rate_limiter.py`:
  - `RateLimitExceeded(Exception)` — raised when limit is breached
  - `RateLimiterService.__init__(redis_url: str)` — connects using `get_settings().REDIS_URL`
  - `async def check_limit(key: str, limit: int, window_seconds: int) -> None`
    — ZADD current timestamp, ZREMRANGEBYSCORE to prune old entries, ZCARD to count,
    raise `RateLimitExceeded` if count > limit
- `app/api/routes/rate_limiter.py` — FastAPI dependency `require_rate_limit(key, limit, window)`
- Register dependency in `app/api/deps.py`
- `app/config.py` — confirm `REDIS_URL: str` field exists, add if missing

**Sliding window implementation detail:**
```
score = time.time() * 1000  # milliseconds
pipe.zadd(key, {str(score): score})
pipe.zremrangebyscore(key, 0, score - (window_seconds * 1000))
pipe.expire(key, window_seconds + 1)
count = pipe.zcard(key)
if count > limit:
    raise RateLimitExceeded(f"Rate limit exceeded: {count}/{limit} in {window_seconds}s")
```

**Grep patterns to search:**
- `grep -rn "async def" app/services/openrouter.py` — confirm async client pattern
- `grep -rn "AsyncClient\|aioredis\|redis.asyncio" app/` — find existing Redis usage if any
- `grep -rn "REDIS_URL" app/config.py` — confirm config field

---

## Section 3: Tests

Write complete test coverage for the rate limiter service and its database model.

**What to build:**
- `tests/unit/test_rate_limiter.py` — unit tests with mocked Redis
  - `test_check_limit_allows_under_limit`
  - `test_check_limit_raises_at_limit`
  - `test_check_limit_raises_over_limit`
  - `test_window_cleanup_called` — assert `zremrangebyscore` called
  - `test_zadd_called_with_timestamp`
  - `test_redis_unavailable_raises_service_error`
- `tests/unit/test_rate_limit_config_model.py` — model instantiation, field defaults, UUID generation
- `tests/integration/test_rate_limiter_integration.py` — real Redis tests
  - `test_allows_requests_under_limit`
  - `test_blocks_at_limit`
  - `test_window_resets_after_expiry`
- `tests/live/test_rate_limiter_live.py` — live Redis test using `REDIS_URL` from `.env`

**Coverage target:** 100% line coverage on `app/services/rate_limiter.py`

---

## Non-Implementation Sections (Skip — do not generate tasks)

### Environment Setup

Set in `.env` (not tracked in git):
```
REDIS_URL=redis://localhost:6379
```

### Deployment Notes

Rate limiter keys are scoped per-route and per-IP. In production, ensure Redis maxmemory
policy is set to `allkeys-lru` to prevent unbounded key accumulation.
