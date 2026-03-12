# Resilience Patterns — Advanced Patterns & Decision Guide

> Continuation of RESILIENCE-PATTERNS.md. Covers timeouts, dead letters,
> health checks, idempotency, monitoring, decision trees, and common mistakes.

---

## Pattern 6: Timeout Strategies

### What it is
Setting explicit time limits on operations so a slow dependency can't block your system indefinitely.

### Timeout Hierarchy

**Per-request timeout:** How long to wait for a single HTTP request.
```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(url, ...)
```

**Per-operation timeout:** How long a business operation (which may involve retries) can take.
```python
async with asyncio.timeout(120):  # 2 minutes for entire operation including retries
    result = await retry_with_backoff(func, max_retries=3)
```

**Per-pipeline timeout:** How long an entire background task can run before being killed.
Set in ARQ worker configuration.

### Recommended Timeouts by Operation Type

| Operation | Per-Request | Per-Operation | Notes |
|-----------|------------|---------------|-------|
| LLM API call | 120s | 5 min | LLMs can be very slow |
| External REST API | 30s | 2 min | Include retry time |
| Reddit JSON fetch | 15s | 1 min | Simple HTTP |
| Slack delivery | 10s | 30s | Should be fast |
| Google Drive upload | 60s | 5 min | File size dependent |
| Database query | 10s | 30s | Indicates a bad query if slow |
| Redis operation | 5s | 15s | Redis should be very fast |

### Timeout Anti-Patterns

**No timeout:** The default for `httpx.AsyncClient` is 5 seconds for connect, 5 for read.
This is too short for LLM calls. Always set explicit timeouts.

**Too short for LLMs:** Claude Opus generating a long report can take 60+ seconds.
Set LLM timeouts to 120s minimum.

**Ignoring cascade:** A slow database query timeouts, but the transaction is left open.
Always ensure cleanup in timeout handlers.

---

## Pattern 7: Dead Letter Queues

### What it is
A holding area for messages or jobs that have failed all retry attempts.
Allows manual inspection, debugging, and reprocessing without losing work.

### When to use
- Background job processing (ARQ tasks)
- Webhook event processing
- Any batch operation where individual item failures must be preserved

### Implementation in This Codebase

Instead of a message queue DLQ, use a database-backed approach:

```python
# In the model for the operation
status: Mapped[str]  # 'pending' | 'processing' | 'complete' | 'failed' | 'dead_letter'
error_message: Mapped[str | None]
failed_at: Mapped[datetime | None]
retry_count: Mapped[int] = mapped_column(default=0)
```

```python
async def process_with_dlq(item_id: UUID, session: AsyncSession) -> None:
    item = await session.get(Item, item_id)
    if item.retry_count >= MAX_RETRIES:
        item.status = 'dead_letter'
        item.failed_at = datetime.utcnow()
        await session.commit()
        logger.error(f"Item {item_id} moved to dead letter after {MAX_RETRIES} attempts")
        return
    try:
        await process(item)
        item.status = 'complete'
    except Exception as e:
        item.retry_count += 1
        item.error_message = str(e)
        item.status = 'failed'
    await session.commit()
```

---

## Pattern 8: Health Checks

### Liveness Probe
"Is this process alive?"
- Returns 200 if the process is running and responsive
- Does NOT check external dependencies
- Failure causes the container to restart

```python
@router.get("/health")
async def health():
    return {"status": "healthy"}
```

### Readiness Probe
"Is this process ready to serve traffic?"
- Checks database connectivity, Redis, external dependencies
- Failure causes the load balancer to stop sending traffic

```python
@router.get("/health/ready")
async def ready(session: AsyncSession = Depends(get_async_session)):
    checks = {}
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = str(e)
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = str(e)
    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ready" if all_ok else "degraded", "checks": checks}
```

### Startup Probe
"Has this process finished initializing?"
Allows longer startup time. Different from liveness: tolerates failure during startup.

---

## Pattern 9: Idempotency

### What it is
Designing operations so they can safely run multiple times with the same result.

### Why it matters
- Webhooks may be delivered multiple times
- Background tasks may run concurrently if a worker restarts mid-job
- Network retries may cause the same request to reach the server twice

### Implementation Strategies

**Idempotency keys:**
```python
existing = await session.execute(
    select(WebhookEvent).where(WebhookEvent.event_id == event_id)
)
if existing.scalar_one_or_none():
    return  # Already processed
```

**Upsert instead of insert:**
```python
stmt = insert(Industry).values(**data)
stmt = stmt.on_conflict_do_update(
    index_elements=["name"],
    set_={"last_updated": datetime.utcnow()}
)
await session.execute(stmt)
```

**Check-then-act:**
```python
run = await session.get(ResearchRun, run_id)
if run.status != "pending":
    return  # Already processed or in progress
```

### Idempotency Decision Table

| Operation | Strategy | Reason |
|-----------|---------|--------|
| Webhook receipt | Idempotency key in DB | Webhooks guaranteed-at-least-once |
| Cron task | Status check at start | Prevent concurrent runs |
| Seeding DB | Upsert with conflict resolution | Safe for repeated deploys |
| Sending Slack | Log delivery with dedup key | Prevent duplicate notifications |
| Writing reports | Check if report exists for run_id | One report per run |

---

## Pattern 10: Monitoring and Observability

### SLIs (Service Level Indicators)
- Request success rate (% that succeed)
- Request latency (p50, p95, p99)
- Pipeline completion rate (% of scheduled runs that complete)
- Error rate by type (rate limit, timeout, server error, client error)

### SLOs (Service Level Objectives)
- Scout pipeline success rate: > 95%
- Scout pipeline completion time: < 15 minutes
- API endpoint latency p95: < 500ms
- Webhook processing time: < 2 seconds

### Logging Strategy
```python
logger.info("pipeline_phase_complete", extra={
    "run_id": str(run_id), "phase": "phase3_research",
    "duration_seconds": elapsed, "posts_processed": count, "errors": error_count,
})
logger.error("pipeline_phase_failed", extra={
    "run_id": str(run_id), "phase": "phase3_research",
    "error_type": type(e).__name__, "error_message": str(e), "attempt": attempt,
})
```

Every operation should log: Start (with inputs), Success (with outputs and duration), Failure (with error type, message, and context).

---

## Decision Tree: Which Pattern to Use

```
Is this an external API call?
├─ YES, high volume (>100/hour)
│   └─ Use: Retry + Circuit Breaker + Rate Limiter
├─ YES, low volume (<100/hour)
│   └─ Use: Retry + Provider Failover (like openrouter.py)
└─ NO

Is this a multi-step workflow?
├─ YES, steps are independent
│   └─ Use: Per-step Retry + Dead Letter for failed items
├─ YES, steps are interdependent
│   └─ Use: Saga Pattern with compensation actions
└─ NO

Is this a scheduled/background task?
├─ YES → Use: Idempotency check at start + Status tracking in DB
└─ NO

Is this receiving webhooks?
├─ YES → Use: Idempotency key + Background task offload + ACK within 3s
└─ NO

Is this a read operation?
├─ Staleness acceptable → Use: Cache with TTL + Fallback to cached value
└─ Must be fresh → Use: Retry only, no cache fallback
```

---

## Common Mistakes in Resilience Design

1. **Retrying non-retryable errors:** Retrying a 400 Bad Request wastes time. Classify errors: me problem (don't retry) or them problem (retry).
2. **No jitter in backoff:** Without jitter, all clients retry simultaneously (thundering herd). Always add ±10-30% random jitter.
3. **Infinite retries:** Always set a maximum. 3 attempts is almost always enough.
4. **Retrying without logging:** Silent retries make debugging impossible. Log each retry with attempt number, delay, and error.
5. **Missing Retry-After header:** When an API returns 429, honor the Retry-After header. Ignoring it may get you banned.
6. **Circuit breaker threshold too low:** Set threshold to 5+ failures in a time window, not 1 or 2.
7. **No fallback for circuit-open state:** Define what happens when circuit is open: return default, use cache, queue for later.
8. **Forgetting idempotency for webhooks:** Every webhook system can re-deliver. Check for duplicates.
9. **Timeouts too short for LLMs:** Claude Opus needs 60+ seconds. Set LLM timeouts to 120s minimum.
10. **Resilience without observability:** Retries and fallbacks that don't emit logs are invisible. Always log at WARNING level.
