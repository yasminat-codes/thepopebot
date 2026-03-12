# Anti-Patterns Reference

> Used in Phase 4 (Synthesis). Scan user's description and codebase findings against
> every category below. Surface warnings before the plan is written — not after.
> For each: check description for signal words, grep codebase, surface warning, insert fix.

---

## Architecture Anti-Patterns

### AP-A1: Over-Engineering
**What it is:** Adding abstractions, layers, or infrastructure the project does not currently need. Building for 10x scale when you have 10 users.

**Look for in user description:**
- "microservices", "event-driven", "CQRS", "event sourcing" for a small feature
- "abstract base class for every service"
- "plugin architecture" for a one-time script
- "distributed" anything when the system is a single-server monolith

**Check codebase:**
```
# Is the existing codebase a monolith? If yes, microservices are over-engineering.
Glob: docker-compose.yml, k8s/, Makefile
Grep: "services:" in docker-compose.yml  → count services
```

**Say this:**
> "Warning: This plan introduces [X] which is significant architectural complexity for the current scale. The codebase is a [monolith/small service]. Consider a simpler approach first: [Y]. You can evolve to [X] when [measurable trigger]."

**Fix:** Replace with the simplest thing that could work. Add a note: "Evolve to [complex approach] when [metric] is reached."

---

### AP-A2: Under-Engineering
**What it is:** Shipping something with no error handling, no logging, no monitoring, no tests — treating a production feature like a prototype.

**Look for in user description:**
- No mention of what happens when it fails
- No mention of logging or observability
- No mention of tests
- "quick script", "just a simple thing", "temporary solution"

**Check codebase:**
```
Grep: "try" / "except" / ".catch" / "error" in existing similar files
Grep: "logger" / "logging" / "console.log" in existing similar files
Grep: "test_" / ".spec." / "describe(" in tests/ directory
```

**Say this:**
> "Warning: The current plan has no error handling for [X], no logging for [Y], and no test coverage. In production, silent failures in this path will be invisible. Let me add the minimum viable reliability layer."

**Fix:** Add to plan: error handling section, logging strategy, and at least a smoke test for the critical path.

---

### AP-A3: Tight Coupling
**What it is:** Two systems that must succeed or fail together, with no ability to degrade gracefully. One service down brings everything down.

**Look for in user description:**
- Direct function calls across service boundaries instead of async handoffs
- Synchronous chain: A calls B calls C calls D — any break cascades
- Shared databases between unrelated services

**Check codebase:**
```
Grep: "import" across service directories (e.g., from workers import services)
Grep: direct database model imports in route handlers
Grep: synchronous HTTP calls inside database transactions
```

**Say this:**
> "Warning: [Component A] is directly coupled to [Component B]. If [B] goes down, [A] fails too. Consider: [async queue / event emission / circuit breaker] to allow independent failure."

**Fix:** Introduce an async handoff (queue, event, or background task) between the coupled components.

---

### AP-A4: Missing Contracts
**What it is:** No documented API contracts between components — data formats undocumented, field names assumed, schema changes break silently.

**Look for in user description:**
- "the frontend will just call the backend"
- "the worker reads from the database"
- No mention of data models, schemas, or validation

**Check codebase:**
```
Grep: "Pydantic" / "zod" / "joi" / "schema" → are contracts already in use?
Grep: "TypedDict" / "dataclass" / "interface" / "type " for typed contracts
Grep: "Any" in Python type hints → untyped danger zones
```

**Say this:**
> "Warning: There's no data contract between [A] and [B]. A schema change in [A] will silently break [B]. Add a Pydantic model / Zod schema / TypeScript interface to formalize this contract."

**Fix:** Add explicit data models at every system boundary in the plan.

---

### AP-A5: Ignoring Existing Patterns
**What it is:** Building a new solution from scratch when the codebase already has a working pattern for it. Creates inconsistency and maintenance burden.

**Look for in user description:**
- Building a new auth system when JWT middleware already exists
- Creating a new HTTP client when there's already a service layer
- New database access pattern when repositories are established

**Check codebase:**
```
Grep: existing service classes, repository patterns, base classes
Grep: existing utility modules in utils/, helpers/, lib/
Grep: existing middleware, decorators, hooks that solve the same problem
```

**Say this:**
> "The codebase already has [X] which does 80% of what you're describing. Extending [X] will take 2 hours. Building from scratch will take 2 days and create a second pattern to maintain. Plan updated to reuse [X]."

**Fix:** Reference the existing pattern in the plan. Add a "Reuse" section pointing to the file.

---

## Integration Anti-Patterns

### AP-I1: Ignoring Rate Limits
**What it is:** Planning an integration without checking the API's documented rate limits, then getting throttled in production.

**Look for in user description:**
- Any third-party API (Stripe, Twilio, OpenAI, SendGrid, etc.)
- "for each user, call the API" (N users = N calls)
- "sync every record" (bulk operations)
- No mention of batching or queuing

**Check codebase:**
```
Grep: existing API client files for rate limit handling
Grep: "sleep", "retry", "backoff", "rate_limit" near API calls
Grep: "429" (Too Many Requests) error handling
```

**Say this:**
> "Warning: [API name] has a limit of [X] requests per [timeframe] (source: official docs). At your planned volume of [Y], you will hit this limit [in Z minutes/on day 1]. Plan updated to add: request queuing with rate limit enforcement."

**Fix:** Add to plan: a queue or batch processor with rate limit enforcement, exponential backoff on 429 responses.

---

### AP-I2: No Webhook Verification
**What it is:** Accepting webhook payloads from external services without verifying the cryptographic signature. Anyone can POST fake events.

**Look for in user description:**
- "receive webhooks from [Stripe/GitHub/Twilio/etc.]"
- No mention of signature verification
- No mention of secret keys for webhooks

**Check codebase:**
```
Grep: "hmac" / "signature" / "webhook_secret" near existing webhook handlers
Grep: "stripe-signature" / "X-Hub-Signature" / "twilio-signature"
Grep: existing webhook endpoints for verification pattern
```

**Say this:**
> "Warning: Accepting [service] webhooks without signature verification is a security vulnerability. Anyone can send fake events to your endpoint. Add HMAC verification using the webhook secret [service] provides."

**Fix:** Add webhook signature verification step as the first action in every webhook handler.

---

### AP-I3: Synchronous Everything
**What it is:** Every external call is made synchronously, blocking the request thread and creating tight coupling between the response time and external service latency.

**Look for in user description:**
- "when X happens, immediately call the external API"
- Long chains of operations in a single request handler
- No mention of background tasks, queues, or workers

**Check codebase:**
```
Grep: "requests.post" / "httpx.post" (sync) vs "await httpx.post" (async)
Grep: "BackgroundTasks" / "celery" / "arq" / "rq" → existing async patterns
Grep: "await" near external calls → already async?
```

**Say this:**
> "Warning: [Operation X] is planned as a synchronous call inside [handler/request]. If [external service] takes 3 seconds, your user waits 3 seconds. Plan updated to offload [X] to a background task and return immediately."

**Fix:** Move slow operations to background tasks. Return 202 Accepted + job ID immediately.

---

### AP-I4: No Timeout
**What it is:** Making external API calls with no timeout configured. One hung connection can exhaust the thread pool.

**Look for in user description:**
- Any external HTTP call
- Database queries without timeout
- No mention of timeout values

**Check codebase:**
```
Grep: "timeout=" near httpx, requests, aiohttp calls
Grep: "connect_timeout" / "read_timeout" / "timeout"
Grep: database connection pool settings
```

**Say this:**
> "Warning: [External call X] has no timeout configured. A slow or hung connection will block a worker thread indefinitely. Add: connect_timeout=5, read_timeout=30 as a minimum."

**Fix:** Add explicit timeout to every external call. Document the expected p99 latency of the service.

---

### AP-I5: Hardcoded URLs and Credentials
**What it is:** Service endpoints, API keys, or secrets embedded in source code instead of environment variables.

**Look for in user description:**
- "I'll put the API key in the config file"
- Specific URLs mentioned as constants
- No mention of environment variables

**Check codebase:**
```
Grep: "http://" / "https://" as string literals in non-config files
Grep: "api_key = " / "secret = " as string literals
Grep: "os.environ" / "process.env" → confirm env var pattern exists
```

**Say this:**
> "Warning: [API key / URL] must never be hardcoded. The codebase uses [pydantic Settings / dotenv / process.env]. Add [VARIABLE_NAME] to .env.example and load it through the existing config pattern."

**Fix:** Add environment variable to .env.example with documentation. Load through existing config module.

---

## Data Anti-Patterns

### AP-D1: N+1 Queries
**What it is:** Fetching a list of records, then querying for related data for each record individually. 100 users = 101 queries instead of 2.

**Look for in user description:**
- "for each [user/order/record], get the [related data]"
- Looping over database results and making additional queries inside
- No mention of joins, eager loading, or batching

**Check codebase:**
```
Grep: "for " near database query calls (e.g., for user in users: db.query())
Grep: ".all()" or ".first()" inside loops
Grep: "select_related" / "joinedload" / "prefetch_related" → existing mitigation
```

**Say this:**
> "Warning: The planned loop over [records] with per-record queries is an N+1 pattern. At 1000 records this is 1001 database queries. Use [joinedload / prefetch / batch query] instead. Plan updated with efficient query strategy."

**Fix:** Replace the loop+query pattern with a single query using JOINs or a batch fetch.

---

### AP-D2: No Indexing Strategy
**What it is:** Planning a database schema without considering which columns will be queried and therefore need indexes.

**Look for in user description:**
- New database tables being introduced
- "query by [foreign key / email / status / date]"
- Filter or sort operations without mentioning indexes

**Check codebase:**
```
Grep: "Index(" / "index=True" / "CREATE INDEX" in migration files
Grep: existing models for index patterns
Grep: slow query patterns in existing code
```

**Say this:**
> "Warning: The plan adds a query on [column X] but no index is planned for that column. At scale, this becomes a full table scan. Plan updated to include: CREATE INDEX ix_{table}_{column} ON {table}({column})."

**Fix:** Add explicit index creation to the migration plan for every column used in WHERE, ORDER BY, or JOIN.

---

### AP-D3: Missing Migrations
**What it is:** Planning schema changes without migration scripts. Direct schema alterations in production are catastrophic.

**Look for in user description:**
- New tables, columns, or relationships
- No mention of Alembic, Flyway, Prisma migrate, or similar
- "just add a column to the table"

**Check codebase:**
```
Glob: alembic/, migrations/, prisma/migrations/
Grep: "alembic" / "migrate" in existing commands / Makefile / README
Grep: existing migration file naming conventions
```

**Say this:**
> "Warning: The plan modifies the database schema but includes no migration script. Schema changes must go through [Alembic/Prisma migrate/Flyway]. Plan updated to include a migration file with up/down (rollback) steps."

**Fix:** Add migration creation as an explicit step. Include both forward migration and rollback SQL.

---

### AP-D4: No Data Validation at Boundaries
**What it is:** Trusting data from external sources (webhooks, APIs, user input) without validation. One malformed payload corrupts the database.

**Look for in user description:**
- Data coming from external APIs or webhooks
- No mention of Pydantic models, Zod schemas, or validation
- Direct insertion of external data into database

**Check codebase:**
```
Grep: "Pydantic" / "BaseModel" / "Field" → validation pattern established
Grep: "zod" / "yup" / "joi" → frontend validation
Grep: "validate" / ".parse(" / "model_validate" near boundary code
```

**Say this:**
> "Warning: Data from [external source] enters the system without validation. One unexpected field or type mismatch will crash the pipeline or corrupt the database. Add a [Pydantic model / Zod schema] at this boundary."

**Fix:** Add explicit validation model at every system boundary where external data enters.

---

## Planning Anti-Patterns

### AP-P1: Vague Success Criteria
**What it is:** "It should work" or "users should be happy" — criteria that cannot be measured or tested.

**Look for in user description:**
- "it should be fast"
- "it should be reliable"
- "users should see their data"
- No specific numbers, thresholds, or test conditions

**Say this:**
> "The success criteria are currently unmeasurable. Let me convert them: 'fast' → p95 response time < 500ms. 'reliable' → 99.9% uptime, <0.1% error rate. 'users see data' → data visible within 30 seconds of event. Confirm these targets or adjust."

**Fix:** Convert every success criterion to a measurable outcome: metric + threshold + timeframe.

---

### AP-P2: Missing Rollback Plan
**What it is:** A deployment plan with no strategy for what to do when the deployment fails or the feature causes production issues.

**Look for in user description:**
- No mention of rollback, revert, or feature flags
- Database migrations with no down() function
- Tight coupling between new code and new schema

**Say this:**
> "Warning: There's no rollback plan. If this deployment fails in production, what's the recovery path? Plan updated to include: rollback steps, migration down() script, and estimated recovery time."

**Fix:** Add a Rollback section to the plan with specific commands and estimated time to recover.

---

### AP-P3: Scope Creep in Plans
**What it is:** A plan that starts as "add email notifications" and grows to include "full notification center, user preferences, digest scheduling, and analytics dashboard."

**Look for in user description:**
- Multiple distinct features bundled together
- "and also", "while we're at it", "it would be nice if"
- Plan sections that address different user needs

**Say this:**
> "Warning: This plan now covers [N] distinct features. The critical path is [core feature]. The rest are enhancements. Splitting into phases: Phase 1 (critical path, 1 week), Phase 2 (enhancements, TBD). Confirm scope or proceed with full plan."

**Fix:** Identify the critical path. Separate into phases. Phase 1 must be deployable on its own.

---

### AP-P4: Ignoring the Existing Codebase
**What it is:** Planning as if starting from scratch when significant relevant code already exists.

**Look for:** Plan references no existing files, no existing patterns, no reuse of anything.

**Check:** Did Phase 1 (Context Loading) find relevant patterns? If yes, are they referenced in the plan?

**Say this:**
> "Warning: This plan reinvents several patterns that already exist in the codebase. Found: [list of relevant existing files]. Plan updated to reference and reuse these instead of rebuilding from scratch."

**Fix:** Add a "Reuse" section at the top of the plan listing all existing code that should be leveraged.

---

### AP-P5: No Complexity Scores
**What it is:** A plan with no effort estimation, making it impossible to prioritize or schedule work.

**Check:** After plan is drafted — does every section have a complexity score (1-5)?

**Say this:**
> "Each section scored for complexity (1=trivial, 5=very complex). Total weighted: [X/5]. Estimated time: [Y-Z days]."

**Fix:** Score every section before presenting the plan. Include a total and estimated timeline.
