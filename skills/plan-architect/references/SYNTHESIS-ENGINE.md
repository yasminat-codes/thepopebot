# Synthesis Engine Reference

> Used in Phase 4 (Synthesis & Connection).
> How to merge research from 3 parallel agents, connect dots, enhance ideas, score complexity,
> and detect gaps before writing the plan.

---

## Step 1: Read All 3 Research Outputs

Before doing anything, read all 3 files in parallel:

```
Read: .claude/plan-architect/codebase-research.md    (Agent A output)
Read: .claude/plan-architect/web-research.md         (Agent B output)
Read: .claude/plan-architect/mcp-research.md         (Agent C output)
```

If any file is missing or empty, that research agent failed. Do NOT proceed.
Ask the user if you should re-run the missing agent or proceed with reduced confidence.

---

## Step 2: Identify Signal Types

Classify each finding from all 3 outputs into one of these signal types:

| Signal Type | Definition | Weight |
|-------------|-----------|--------|
| Confirmed | Found in codebase AND validated by web best practice | High — use it |
| Novel | In web research but not in codebase | Medium — plan new implementation |
| Outdated | In MCP past decisions but codebase has since changed | Low — verify before using |
| Conflict | Codebase pattern contradicts web best practice | Requires decision |
| Gap | Needed for the plan but found nowhere | Must flag |

---

## Step 3: Resolve Conflicts

When a codebase pattern conflicts with a web best practice:

**Do NOT silently pick one.** Surface the conflict to the user with a recommendation:

> "There's a conflict: the codebase uses [sync SQLAlchemy], but the standard for this stack
> is [async SQLAlchemy with asyncpg]. Migrating would improve performance but requires
> refactoring [N] files. Recommendation: keep sync for this feature, create a migration plan
> as a separate task. Confirm?"

When multiple approaches exist in web research:

Present a trade-off table, then make a recommendation:

```
| Approach | Pros | Cons | Best for |
|----------|------|------|---------|
| Option A | ...  | ...  | ...     |
| Option B | ...  | ...  | ...     |

Recommendation: Option A — because [specific reason relevant to this codebase].
```

---

## Step 4: Connect the Dots

This is the highest-value step. Synthesize across all sources to surface non-obvious connections.

### Connection Patterns

**Pattern 1: Requirement + Existing Solution**
> "You want [X]. Agent A found that `app/services/notification_service.py` already handles 80%
> of this. Plan updated to extend that service instead of building from scratch."

Signal: User describes a feature. Codebase has a closely related existing implementation.

**Pattern 2: Integration + Rate Limit**
> "You're integrating with [API]. Agent B found the rate limit is 100 req/min. At your
> described volume of 500 events/hour (~8/min), you're within limits. But during peak (burst),
> add a queue with max 90 req/min enforcement."

Signal: API integration + volume mentioned in interview + rate limit from web research.

**Pattern 3: Data Flow + Missing Validation**
> "Data enters from the webhook, goes to the database. Agent A found no Pydantic validation
> model at this boundary. Agent B confirms this is a common attack vector. Adding validation
> step to the plan."

Signal: External data source + database write + no validation pattern in codebase.

**Pattern 4: Feature + Security Gap**
> "This endpoint processes payments. Agent A found the existing auth pattern in
> `app/api/deps.py:get_current_user`. The plan must add this dependency to the payment
> route — it's not currently included."

Signal: Sensitive operation + existing auth mechanism + planned endpoint missing auth.

**Pattern 5: Automation + Silent Failure**
> "This job runs every hour. Agent A found the scheduler at `app/workers/scheduler.py`.
> There's no alert when scheduled jobs fail. Agent B confirms this is a standard monitoring
> gap. Adding: failure alerting, health check endpoint, and dead letter queue for failed jobs."

Signal: Scheduled/background process + no monitoring found in codebase.

**Pattern 6: State Management + Missing Idempotency**
> "This webhook handler processes payment events. If [Stripe] retries a delivery, the handler
> will run twice and charge the user twice. Adding: idempotency key check using
> `stripe_event_id` before processing."

Signal: Webhook handler + financial/state-mutating operation + no deduplication pattern.

**Pattern 7: Scale + Architecture Mismatch**
> "You're describing processing 10,000 records at once. The current synchronous approach will
> block for [estimated X minutes]. This exceeds acceptable response time. Plan updated to
> use batch processing with progress tracking."

Signal: Bulk operation + synchronous execution + no queue/batch pattern in codebase.

---

## Step 5: Enhance Ideas from 3/10 to 10/10

For every feature or automation in the user's description, apply this enhancement checklist:

| User says | What the plan MUST add |
|-----------|----------------------|
| "I want to do X" | Error handling paths, monitoring, rollback strategy |
| "Connect to [API]" | Rate limit enforcement, circuit breaker, retry with backoff, timeout |
| "Store data in [table]" | Indexing strategy, migration script, backup consideration |
| "Run this every [interval]" | Failure alerting, catch-up logic, idempotency key, max retries |
| "Send notifications" | Delivery guarantees, template versioning, opt-out/unsubscribe |
| "Add authentication" | Token expiry, refresh flow, revocation, audit logging |
| "Process a file/upload" | Size limits, type validation, virus scanning consideration, cleanup |
| "Cache this data" | Cache invalidation strategy, TTL, stale-while-revalidate |
| "Accept payments" | Idempotency keys, webhook verification, refund flow, audit trail |
| "Import/export data" | Progress tracking, partial failure handling, rollback, format validation |

The user described a 3/10 plan. Your job is to return a 10/10 plan.

---

## Step 6: Complexity Scoring

Score EVERY section of the plan individually before writing it.

### Scoring Rubric

| Score | Label | Definition | Examples |
|-------|-------|-----------|---------|
| 1 | Trivial | Single config change or 5-line addition. No tests needed. | Add env var, update constant, add one field to existing model |
| 2 | Simple | Single-file change, well-understood pattern, 30 min to implement | New CRUD endpoint following existing pattern, add validation to form |
| 3 | Moderate | Multi-file change, some integration work, 2-4 hours | New service + routes + DB model + basic tests |
| 4 | Complex | Multi-system, state management, significant testing needed, 1-2 days | Saga across 3+ services, retry logic, webhook + queue + worker |
| 5 | Very Complex | New architectural component, high risk, needs review, 3+ days | New message queue infrastructure, real-time pipeline, auth system rewrite |

### Section Scoring Format

```markdown
### [Section Name] — Complexity: [1-5] ([Label])
**Why:** [1 sentence explaining the score]
**Estimate:** [X hours / X days]
**Risk:** [Low / Medium / High] — [brief reason]
```

### Weighted Average

At the end of complexity scoring:
```
Total sections: N
Scores: [list each section score]
Weighted average: [sum / N]
Implementation estimate: [derived from average]
  - Solo dev: [X days]
  - Pair: [X days]
```

---

## Step 7: Gap Detection

After all dot-connecting and scoring, run through this gap checklist. Flag every gap as a
warning in the plan's "Open Questions" section:

**External Calls**
- [ ] Every external HTTP call has: timeout, retry, error handling
- [ ] Every API integration has: rate limit enforcement, 429 handling
- [ ] Every webhook handler has: signature verification, idempotency

**Background Processes**
- [ ] Every scheduled job has: failure alerting, max retry limit
- [ ] Every queue consumer has: dead letter queue, visibility timeout
- [ ] Every background task has: health check visibility

**Data Boundaries**
- [ ] Every external data input has: Pydantic/Zod validation
- [ ] Every new table has: migration script, indexes, rollback SQL
- [ ] Every destructive operation has: audit log, rollback plan

**Security**
- [ ] Every new endpoint has: authentication check
- [ ] Every sensitive operation has: authorization check (not just auth)
- [ ] Every user input has: sanitization consideration

**Observability**
- [ ] Every new service has: structured logging
- [ ] Every background process has: metric emission
- [ ] Every critical path has: distributed tracing consideration

**Implementation Support**
- [ ] Context loading suggestions included (what files to read before implementing)
- [ ] Grep patterns included (patterns to search during implementation)
- [ ] Rollback section included

---

## Step 8: Write the Synthesis Summary

Before generating the plan, produce an internal synthesis summary:

```markdown
## Synthesis Summary

**Core Insight:** [The single most important connection made across all research]

**Reuse Opportunities:** [Existing code that should be leveraged]

**New Implementations Required:** [Things not in codebase, must be built]

**Anti-Patterns Detected:** [List by ID, e.g., AP-I1: Ignoring Rate Limits]

**Conflicts to Resolve:** [List conflicts and recommended resolution]

**Gaps Flagged:** [List all gaps from checklist]

**Complexity Overview:**
  - Highest complexity section: [name] ([score])
  - Lowest complexity section: [name] ([score])
  - Weighted average: [X/5]
  - Total estimate: [X days]
```

This summary drives the plan structure — not the other way around.

---

## Synthesis Quality Checks

Before proceeding to Phase 5 (Plan Architecture), verify:

| Check | Pass Condition |
|-------|--------------|
| All 3 research files read | Yes / fallback documented |
| Conflicts surfaced | All conflicts listed or "none found" |
| Dot-connecting performed | At least 1 non-obvious connection made |
| Enhancement checklist applied | Every feature checked against the table |
| Complexity scored | Every planned section has a score |
| Gap checklist run | All 14 gaps checked |
| Synthesis summary written | Present and complete |

If any check fails, do not proceed to Phase 5.
