# Resilience Patterns — Production-Grade Failure Handling

This file is a reference for choosing and implementing resilience patterns in implementation plans.
Each pattern includes: what it is, when to use it, implementation guidance, and common mistakes.

---

## The Core Principle

Every external call will fail. The question is not if but when.
Resilience is not a feature you add at the end — it is built into the design from the start.

A system without resilience patterns fails completely when a dependency is slow.
A system with resilience patterns degrades gracefully and recovers automatically.

---

## Pattern 1: Retry with Exponential Backoff and Jitter

### What it is
Automatically retry failed operations, waiting progressively longer between each attempt.
Jitter (randomness) prevents the "thundering herd" problem where many clients retry simultaneously.

### When to use
- Rate-limited APIs (HTTP 429)
- Transient server errors (HTTP 500, 502, 503, 504)
- Network timeouts
- Database connection failures

### When NOT to use
- Client errors (HTTP 400, 404, 422) — these won't succeed on retry
- Auth failures (HTTP 401, 403) — retry won't fix a bad token
- Business logic errors — a validation failure needs a code fix, not a retry

### Implementation Pattern

```python
import asyncio
import random

async def retry_with_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 2.0,
    max_delay: float = 30.0,
    jitter: float = 0.2,
    retryable_exceptions: tuple = (Exception,),
):
    """
    Retry with exponential backoff and jitter.

    Wait times: 2s, 4s, 8s (±20%)
    After max_retries exhausted, raises the last exception.
    """
    last_error = None

    for attempt in range(1, max_retries + 1):
        try:
            return await func()
        except retryable_exceptions as e:
            last_error = e
            if attempt == max_retries:
                raise

            # Exponential backoff with jitter
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            jitter_amount = delay * jitter * (2 * random.random() - 1)
            actual_delay = delay + jitter_amount

            await asyncio.sleep(actual_delay)

    raise last_error
```

### Retry Policy by Operation Type

| Operation | Max Retries | Base Delay | Max Delay | Jitter |
|-----------|-------------|------------|-----------|--------|
| LLM API call | 3 | 2.0s | 30s | ±20% |
| External REST API | 3 | 2.0s | 30s | ±20% |
| Database write | 2 | 1.0s | 5s | ±10% |
| Redis operation | 3 | 0.5s | 5s | ±20% |
| Webhook delivery | Not applicable | — | — | — |
| File upload (S3, Drive) | 3 | 3.0s | 60s | ±30% |

### This Codebase's Pattern
`app/services/openrouter.py` implements this pattern with `_RetryableError` and `_FailoverError`
exception types. New services should:
1. Import or recreate the `_RetryableError` / `_FailoverError` pattern
2. Use the same base delay (2.0s) for consistency
3. Never hard-code sleep values — pull from `settings`

---

## Pattern 2: Circuit Breaker

### What it is
A state machine that stops sending requests to a failing dependency for a period of time.
Prevents cascading failures where a slow dependency blocks your entire system.

Three states:
- **Closed** — normal operation, requests flow through
- **Open** — dependency is failing, reject requests immediately (fast fail)
- **Half-Open** — testing if dependency recovered, allow one probe request

### When to use
- High-volume calls to external services (thousands per hour)
- Services with variable availability (external APIs, third-party services)
- When one service failing could exhaust your thread pool or connection pool
- When fast failure is better than waiting for a timeout

### When NOT to use
- Low-volume one-off calls (the overhead isn't worth it)
- Internal database calls with a healthy connection pool (use retries instead)
- Calls where every request matters and you can't afford to skip any

### Thresholds by Service Type

| Service Type | Failure Threshold | Open Duration | Half-Open Probe |
|--------------|-------------------|---------------|-----------------|
| LLM provider | 5 failures in 60s | 30s | 1 request |
| External REST API | 5 failures in 60s | 60s | 1 request |
| External scraper | 3 failures in 60s | 120s | 1 request |
| Notification service (Slack) | 3 failures in 60s | 60s | 1 request |
| File storage (Drive, S3) | 5 failures in 60s | 60s | 1 request |

### Implementation Note
For this codebase, the `openrouter.py` client implements a simpler but equally effective
pattern: provider failover rather than circuit breaking. This is appropriate here because:
1. There are multiple providers (OpenRouter, Z.ai, OpenAI, Moonshot, Google)
2. Provider-level failover handles the "one provider is down" case that circuit breakers address
3. Adding a full circuit breaker on top would be over-engineering

Use circuit breakers when: you have ONE external service with no failover option.

---

## Pattern 3: Fallback Strategies

### What it is
Defining a degraded-but-functional response when the primary operation fails completely.

### Fallback Hierarchy
1. **Cached response** — return the last successful response
2. **Default value** — return a safe, reasonable default
3. **Partial result** — return what succeeded, skip what failed
4. **Queue for retry** — store the work for later, continue processing other items
5. **Fast fail** — fail loudly and immediately (when degraded behavior is worse than no behavior)

### When to Use Each Fallback

**Cached response:** Read operations where staleness is acceptable.
- Example: If subreddit scoring API is down, use scores from last run
- Implementation: Redis with TTL matching acceptable staleness window

**Default value:** Low-stakes operations where zero/empty is safe.
- Example: If keyword suggestions fail, continue with existing keywords
- Implementation: `result = await get_suggestions() or []`

**Partial result:** Batch operations where individual item failure is acceptable.
- Example: If one Reddit post analysis fails, continue with others
- Implementation: Collect errors, process successful items, log failures

**Queue for retry:** Operations that must eventually succeed but tolerate delay.
- Example: Failed Slack delivery → retry queue, deliver on next run
- Implementation: Store in database with `status = 'pending_delivery'`

**Fast fail:** Operations where partial state is dangerous.
- Example: Multi-step transaction where step 2 failing leaves step 1's data orphaned
- Implementation: Transaction with explicit rollback on any failure

### Fallback Anti-Pattern: Silent Degradation
The worst fallback is returning wrong data without indication.
Every fallback must either:
a) Log the degradation at WARNING level
b) Record the failure in the database
c) Alert if the fallback is being used repeatedly

---

## Pattern 4: Saga Pattern (Compensation for Multi-Step Workflows)

### What it is
For workflows spanning multiple services or steps, each step must have a defined compensation
(undo) action. If any step fails, execute compensations in reverse order.

### When to use
- Multi-step pipelines where partial completion leaves the system in an invalid state
- Operations that touch multiple systems (database + external API + file storage)
- Background tasks where you can't use database transactions

### When NOT to use
- Simple CRUD operations (database transactions handle this)
- Idempotent operations (just retry, no compensation needed)
- Operations where partial state is acceptable

### Saga Pattern for This Codebase

The Scout and Deep Dive pipelines are implicit sagas. Each phase has a compensation:

| Phase | Action | Compensation |
|-------|--------|--------------|
| research_run created | INSERT research_run | UPDATE status='failed' |
| subreddits discovered | INSERT subreddits | mark as stale or delete |
| posts fetched | INSERT reddit_posts | mark run as failed (posts stay for audit) |
| analyses generated | INSERT post_analyses | mark run as failed |
| report generated | INSERT research_report | mark as draft, don't deliver |
| Slack delivery | POST to Slack | — (delivery is terminal, log failure) |

### Implementation Pattern

```python
async def run_pipeline(run_id: UUID, session: AsyncSession) -> None:
    """Saga-pattern pipeline. Each phase records its completion."""

    # Phase 1
    try:
        await phase1_execute(run_id, session)
        await mark_phase_complete(run_id, "phase1", session)
    except Exception as e:
        await compensate_phase1(run_id, session)
        await mark_run_failed(run_id, str(e), session)
        raise

    # Phase 2
    try:
        await phase2_execute(run_id, session)
        await mark_phase_complete(run_id, "phase2", session)
    except Exception as e:
        await compensate_phase2(run_id, session)  # Undo phase 2
        await compensate_phase1(run_id, session)  # Undo phase 1
        await mark_run_failed(run_id, str(e), session)
        raise
```

---

## Pattern 5: Rate Limit Handling

### What it is
Controlling the rate of outbound requests to respect external API limits.

### Rate Limiting Strategies

**Token Bucket:** Requests are allowed at a steady rate with some bursting allowed.
- Good for: APIs with burst + sustained rate limits (e.g., "60 requests/minute, max 10/second")
- Implementation: Track tokens, refill at steady rate, consume per request

**Sliding Window:** Count requests in the last N seconds, enforce a maximum.
- Good for: Simple per-minute or per-second limits
- Implementation: Redis sorted set with timestamp as score, trim old entries
- This codebase uses this approach in `app/services/rate_limiter.py`

**Fixed Window:** Count requests in a fixed time period (e.g., per minute).
- Simpler but has burst problem at window boundaries
- Not recommended for new implementations

**Queue-Based:** Queue requests and drain at the allowed rate.
- Good for: High-volume fire-and-forget operations
- Implementation: ARQ queue with a rate-limited worker

### Rate Limits for Common Services

| Service | Rate Limit | Notes |
|---------|-----------|-------|
| Reddit JSON endpoints | ~60 req/min | Unofficial, varies |
| OpenRouter | Depends on model/tier | Check response headers |
| Slack API | 1 req/sec for Web API | Burst allowed, check headers |
| Google Drive API | 1000 req/100sec per user | Per-service-account |
| Stripe webhooks | Not rate-limited (receiving) | — |

### Handling Rate Limit Responses
```python
if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", 60))
    await asyncio.sleep(retry_after + 1)  # +1 for safety margin
    # Then retry
```



→ See references/RESILIENCE-ADVANCED.md for patterns 6-10 (timeouts, dead letters, health checks, idempotency, monitoring), decision tree, and common mistakes.
