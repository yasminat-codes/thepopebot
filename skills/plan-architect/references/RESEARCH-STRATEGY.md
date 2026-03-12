# Research Strategy — How to Dispatch and Merge the 3 Research Agents

Plan-architect dispatches 3 parallel research agents before writing the plan.
This file governs what each agent searches for, where, and how to merge findings.

---

## The 3 Research Agents

### Agent 1: Codebase Agent
**Mission:** Find everything in the codebase that's relevant to the plan.
**Priority:** Highest. Codebase is the ground truth.
**Tools:** Grep, Read, Bash (ls, find), Glob

### Agent 2: MCP Grep Agent
**Mission:** Deep-search the codebase for patterns that a surface scan misses.
**Priority:** High. Finds buried dependencies and anti-patterns.
**Tools:** Grep with regex, Bash for complex find operations

### Agent 3: Web Agent
**Mission:** Find current best practices, API documentation, and known issues.
**Priority:** Lower. Only fills gaps the codebase doesn't answer.
**Tools:** WebSearch, WebFetch

---

## Priority Order for Research Sources

1. **Codebase first** — if the codebase already solves the problem, there's no decision to make
2. **MCP grep second** — find the non-obvious connections (what imports what, what calls what)
3. **Web third** — only for information the codebase can't provide (API docs, rate limits, known issues)

Never cite a web source for something the codebase already answers. The codebase is always more authoritative
than a blog post.

---

## Agent 1: Codebase Research

### What to Search For

**Layer 1: Existing solutions (30% of search effort)**
The most important question is "does this already exist?"

```bash
# Find files by name similarity
find app/ -name "*[keyword]*" -type f

# Find files containing similar functionality
grep -r "[domain keyword]" app/ --include="*.py" -l

# Find similar service classes
grep -r "class.*[Domain].*Service\|class.*[Domain].*Client\|class.*[Domain].*Manager" app/ --include="*.py" -n
```

**Layer 2: Integration points (30% of search effort)**
Where does the new code need to plug in?

```bash
# Find the entry points (routers, workers, orchestrators)
find app/ -name "worker.py" -o -name "orchestrator.py" -o -name "main.py" | xargs grep -l "def\|class"

# Find existing ARQ task registration
grep -r "on_startup\|cron_jobs\|arq_queue" app/ --include="*.py" -n

# Find existing imports that the new code will likely need
grep -r "from app.services\|from app.models\|from app.config" app/ --include="*.py" -l | head -10
```

**Layer 3: Patterns to follow (20% of search effort)**
What's the established way to do things in this codebase?

```bash
# Find how existing services handle errors
grep -r "except\|raise\|logger.error\|logger.warning" app/services/ --include="*.py" -n | head -30

# Find how existing services are instantiated (singleton? per-request?)
grep -r "= OpenRouterClient\|= PromptManager\|= RateLimiter" app/ --include="*.py" -n

# Find how async sessions are used
grep -r "get_async_session\|async_session\|AsyncSession" app/ --include="*.py" -n | head -20
```

**Layer 4: Configuration patterns (10% of search effort)**
What env vars exist? What's the config structure?

```bash
# Find all settings fields
grep -r "class Settings\|: str\|: int\|: bool\|: float" app/config.py

# Find all env var references
grep -r "settings\." app/ --include="*.py" -n | grep -v "test_" | head -30
```

**Layer 5: Test patterns (10% of search effort)**
What's the testing convention?

```bash
# Find test fixtures
find tests/ -name "conftest.py" | xargs cat

# Find how external services are mocked
grep -r "mock\|patch\|MagicMock\|AsyncMock" tests/ --include="*.py" -l

# Find test file naming convention
ls tests/unit/ tests/integration/ 2>/dev/null
```

---

### Codebase Search Patterns by Plan Type

#### API Integration Plans
When the user wants to integrate with an external API:

```bash
# Find existing API clients
grep -r "httpx\|aiohttp\|requests" app/ --include="*.py" -l
grep -r "class.*Client\|class.*API\|async def.*_call\|async def.*_request" app/ --include="*.py" -n

# Find auth patterns
grep -r "Authorization\|Bearer\|api_key\|API_KEY\|X-API-Key" app/ --include="*.py" -n

# Find how rate limiting is applied to existing integrations
grep -r "rate_limit\|RateLimiter\|await.*limit" app/ --include="*.py" -n

# Find existing retry patterns
grep -r "max_retries\|retry\|backoff\|asyncio.sleep" app/ --include="*.py" -n
```

Expected findings: `app/services/openrouter.py` shows the full pattern. New API clients should match this structure.

#### Automation Plans (Scheduled Tasks)
When the user wants a new cron job or background task:

```bash
# Find how existing tasks are registered
grep -r "cron_jobs\|on_startup\|scheduled_job" app/ --include="*.py" -n
cat app/tasks/worker.py 2>/dev/null || find app/ -name "worker.py" | xargs cat

# Find existing task orchestrators
find app/tasks/ -name "orchestrator.py" | xargs cat 2>/dev/null | head -80

# Find how phases are structured
find app/tasks/ -name "phase*.py" -type f

# Find how existing tasks handle partial failures
grep -r "research_run\|status.*failed\|status.*complete\|mark_as\|update_status" app/ --include="*.py" -n
```

Expected findings: Scout and Deep Dive orchestrators show the phase pipeline pattern.
New automations should use the same structure.

#### Feature Plans (New Endpoints)
When the user wants new API endpoints:

```bash
# Find existing route files
find app/api/ -name "*.py" | xargs ls -la

# Find how existing routes are registered
grep -r "include_router\|APIRouter" app/ --include="*.py" -n

# Find existing middleware and dependencies
grep -r "Depends\|HTTPBearer\|OAuth2\|middleware" app/ --include="*.py" -n | head -20

# Find existing response models and schemas
grep -r "class.*Response\|class.*Schema\|BaseModel" app/ --include="*.py" -n | head -30
```

Expected findings: `app/api/webhooks.py` and `app/api/health.py` show the route structure.

#### Data Pipeline Plans
When the user wants ETL or data processing:

```bash
# Find existing data models
find app/models/ -name "*.py" | xargs grep "class.*Base\|__tablename__"

# Find existing database operations
grep -r "session.execute\|session.add\|session.commit\|select(\|insert(\|update(" app/ --include="*.py" -n | head -30

# Find existing query patterns
grep -r "scalars\|scalar_one\|fetchall\|paginate\|offset\|limit" app/ --include="*.py" -n | head -20

# Find bulk insert patterns (important for pipelines)
grep -r "execute_many\|bulk_insert\|insert.*values" app/ --include="*.py" -n
```

---

## Agent 2: MCP Grep (Deep Pattern Search)

MCP grep is for finding non-obvious connections. Use it when:
- A simple name search doesn't find anything
- You suspect something exists but don't know what it's called
- You need to find all callers of a function to understand impact
- You need to find all places a pattern is used to understand convention

### High-Value MCP Grep Patterns

**Finding all usages of a module:**
```
pattern: "from app\.[module_name]"
context: 3 lines after match
```

**Finding all places where a specific function is called:**
```
pattern: "await [function_name]\(|[function_name]\("
context: 2 lines before and after
```

**Finding all error-handling patterns:**
```
pattern: "except (Exception|httpx\.|SQLAlchemy|json\.)"
context: 5 lines after match
```

**Finding all places a database model is created/updated:**
```
pattern: "[ModelName]\("
glob: "app/**/*.py"
context: 3 lines after match
```

**Finding circular import risks:**
```
pattern: "from app\.[module] import"
glob: "app/[module]/**/*.py"
```

**Finding all TODO/FIXME/HACK:**
```
pattern: "TODO|FIXME|HACK|XXX"
context: 1 line after match
```

### When MCP Grep Reveals Something Unexpected

If MCP grep finds:
- A module you didn't know existed → read it fully before proceeding
- Multiple implementations of the same thing → note duplication in the plan's "Design Decisions" section
- A TODO near the area you're working → check if it's related to your plan
- An import that suggests a dependency you didn't account for → add it to the integration map

---

## Agent 3: Web Research

### When to Use Web Research

Use web research ONLY for:
1. **Rate limit documentation** — official per-API limits not in the codebase
2. **Error code definitions** — what HTTP errors a specific API returns
3. **Authentication flow details** — OAuth steps, token formats
4. **Known bugs or issues** — StackOverflow, GitHub issues for libraries in use
5. **Current library versions** — is the version in requirements.txt current?
6. **Webhook payload schemas** — what fields a webhook actually sends

Do NOT use web research for:
- General best practices (check the codebase instead)
- Generic architecture patterns (the codebase already has established patterns)
- Library usage examples (read the code that already uses the library)

### Search Strategy by Domain

#### External API Research
Priority searches:
1. `[API name] rate limits 2026` — get current, specific rate limits
2. `[API name] webhook payload format` — get the exact JSON shape
3. `[API name] error codes list` — understand all possible errors
4. `[library name] changelog 2025 2026` — check for breaking changes

URLs to prioritize:
- Official API documentation (always first)
- GitHub repository for the API client library (issues + releases)
- status.io pages for the service (know its reliability track record)

#### Library Research
Priority searches:
1. `[library] asyncio integration` — confirm async compatibility
2. `[library] Python 3.12 issues` — check for version conflicts
3. `[library] memory leak` / `[library] connection pool` — known operational issues

#### Security Research
When implementing auth or webhooks:
1. `[API name] webhook signature verification Python`
2. `[OAuth provider] PKCE flow`
3. `HMAC-SHA256 timing attack constant time compare`

### How to Evaluate Web Sources

**Trust hierarchy:**
1. Official API documentation (api.stripe.com/docs, etc.)
2. Official library GitHub repository (README, CHANGELOG)
3. GitHub issues on the library (other users hitting the same problem)
4. Recent StackOverflow answers (check date — anything pre-2023 may be stale)
5. Blog posts and tutorials (lowest trust, often outdated)

**Staleness check:**
Any information about specific API limits, authentication flows, or library APIs should be
verified against a source from 2025 or later. APIs change; old tutorials lie.

---

## Merging Findings from 3 Agents

### Step 1: Prioritize by source
Always prefer codebase findings over web findings.
If the codebase shows X and the web suggests Y, X wins unless there's a clear deficiency.

### Step 2: Resolve conflicts
If Agent 1 (codebase) and Agent 3 (web) conflict:
- Document both in the plan's "Design Decisions" section
- State which was chosen and why
- Example: "Codebase uses sliding-window Redis rate limiting. Web docs suggest token bucket. We use sliding-window for consistency with existing code."

If Agent 1 and Agent 2 (MCP grep) conflict:
- MCP grep usually wins because it's more thorough
- Example: Agent 1 found one usage of a pattern; Agent 2 found 5 — use the pattern seen in all 5

### Step 3: Fill gaps
After merging:
- Items where only Agent 3 (web) has answers → flag as "external dependency, no codebase precedent"
- Items where only Agent 2 (MCP) has answers → investigate the context before including
- Items with no answers from any agent → add to "Open Questions" in the plan

### Step 4: Synthesize into plan sections
| Finding Type | Goes Into |
|-------------|-----------|
| Existing implementations to reuse | Context Loading Suggestions, Grep Patterns |
| Integration points discovered | Architecture Diagram, Component Diagram |
| Rate limits from web research | Integration Map |
| Authentication details | Integration Map |
| Error codes from API docs | Resilience Strategy |
| Library version issues | Design Decisions |
| Testing patterns from codebase | Testing Strategy |

---

## What Constitutes "Enough" Research

Research is complete when you can answer all of these without guessing:

**From codebase:**
- [ ] I know which existing modules this plan touches
- [ ] I know the established error-handling pattern in this codebase
- [ ] I know the established async session pattern for database access
- [ ] I know if a similar feature already exists (partially or fully)
- [ ] I know the test file structure and mocking conventions

**From MCP grep:**
- [ ] I know all the callers of any function I'm changing
- [ ] I know if any TODO/FIXMEs are relevant to this plan
- [ ] I know if there are duplicate implementations I should be aware of

**From web:**
- [ ] I know the rate limits for every external API in the plan
- [ ] I know the exact error format each external API returns
- [ ] I know if the library versions in requirements.txt have known issues

If any of these are unknown and can't be inferred, add them to "Open Questions" in the plan.
Do not invent answers. An honest unknown is better than a confident wrong answer.

---

## Research Anti-Patterns

**Anti-Pattern: Research theater**
Doing extensive web research to avoid looking at the codebase. The codebase is always the first
stop. If you haven't fully read the relevant service files, you haven't done research.

**Anti-Pattern: Premature convergence**
Stopping research after the first positive hit. If you find one implementation of a pattern,
search for all of them — there may be a better or more complete example elsewhere.

**Anti-Pattern: Trusting the function name**
A function named `rate_limit()` might implement token bucket, sliding window, or just sleep.
Read the implementation, not just the name.

**Anti-Pattern: Ignoring test files**
Test files contain examples of how code is meant to be used. They're often more readable than
the implementation itself. Always check `tests/` for usage examples.

**Anti-Pattern: Only reading happy paths**
Read the error handling in existing services. That's where the institutional knowledge lives.
`app/services/openrouter.py`'s retry logic tells you more about the system's reliability
posture than the happy-path call does.
