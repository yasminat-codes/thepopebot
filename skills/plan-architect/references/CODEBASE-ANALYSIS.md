# Codebase Analysis Reference

> Used in Phase 1 (Context Loading) and Phase 3 (Agent A: Codebase Pattern Analyzer).
> Provides scan strategies for understanding any codebase before creating a plan.

---

## Scanning Order

Always scan in this sequence — from broad to specific:

1. Project metadata (what is this project)
2. Architecture (how is it structured)
3. Patterns (how does it do things)
4. Integration map (what external systems)
5. Existing plans (what's already been decided)

Do NOT attempt to read every file. Use targeted Glob and Grep. Read only files that are likely
to contain signal.

---

## Step 1: Project Metadata Scan

### Dependency Files (read ALL that exist)
```
Glob: package.json, pyproject.toml, requirements.txt, go.mod, Cargo.toml, Gemfile, composer.json, pubspec.yaml
```

For each found dependency file:
- Read the full file
- Extract: framework name + version, key dependencies, dev dependencies
- Note: test framework, ORM/database driver, HTTP client, queue system

### README and Config
```
Glob: README.md, README.rst, CLAUDE.md, .claude/CLAUDE.md, .claude/context/*.md
```

Read these in full. They contain the authoritative description of the project's purpose,
tech stack, and conventions.

### Docker / Deployment Config
```
Glob: Dockerfile, Dockerfile.*, docker-compose.yml, docker-compose.*.yml
Glob: .github/workflows/*.yml, .gitlab-ci.yml, Makefile
```

Skim these for: service names, port numbers, environment variable names, deployment approach.

---

## Step 2: Architecture Map

### Directory Structure
```bash
# Run: ls -la at project root, then ls -la at each top-level directory
# Look for: app/, src/, backend/, frontend/, workers/, agents/, lib/, services/
```

Map the directory tree to an architecture pattern. Common patterns:

| Directory Pattern | Architecture |
|------------------|-------------|
| app/api/ + app/models/ + app/services/ | Layered FastAPI / Django |
| src/pages/ + src/components/ + src/lib/ | Next.js / React |
| cmd/ + internal/ + pkg/ | Go standard layout |
| controllers/ + models/ + views/ | MVC (Rails, Laravel) |
| agents/ + tools/ + workers/ | Multi-agent system |

### Key Files to Always Read
```
Glob: app/main.py, src/main.py, src/app/layout.tsx, main.go, index.js, server.js
Glob: app/core/config.py, src/lib/config.ts, config/settings.py
Glob: alembic/env.py, prisma/schema.prisma, db/schema.rb
```

---

## Step 3: Pattern Discovery

### Python/FastAPI Patterns
```
# Routes
Grep: "@router\.(get|post|put|delete|patch)" → API endpoint definitions
Grep: "APIRouter()" → router modules
Grep: "include_router" → how routers are registered

# Models
Grep: "class.*\(Base\)" → SQLAlchemy models
Grep: "class.*\(BaseModel\)" → Pydantic models
Grep: "class.*\(BaseSettings\)" → Settings/config models

# Services and dependencies
Grep: "Depends\(" → FastAPI dependency injection
Grep: "async def get_db" → database session pattern
Grep: "class.*Service" → service layer classes
Grep: "class.*Repository" → repository pattern

# Error handling
Grep: "HTTPException" → existing error raising pattern
Grep: "except.*Exception" → exception handling
Grep: "@app.exception_handler" → global error handlers

# Background tasks
Grep: "BackgroundTasks" → FastAPI background tasks
Grep: "@celery" or "celery.task" → Celery tasks
Grep: "@scheduler" or "AsyncScheduler" → APScheduler jobs
Grep: "arq" → ARQ queue

# Auth
Grep: "Depends(get_current_user)" → auth middleware pattern
Grep: "jwt" or "JWT" → JWT usage
Grep: "oauth2" → OAuth2 scheme
```

### Node.js/Express Patterns
```
# Routes
Grep: "router\.(get|post|put|delete|patch)\(" → Express routes
Grep: "app\.(get|post|put|delete)\(" → Direct app routes
Grep: "export.*default.*router" → Route module exports

# Models
Grep: "Schema\({" or "new Schema" → Mongoose schemas
Grep: "model\(" → Mongoose model definitions
Grep: "@Entity" → TypeORM entity definitions

# Middleware
Grep: "app.use(" → middleware chain
Grep: "express.json()" → body parsing
Grep: "cors(" → CORS configuration

# Error handling
Grep: "next(err)" or "next(error)" → error propagation
Grep: "(err, req, res, next)" → error middleware

# Auth
Grep: "passport" → Passport.js auth
Grep: "jwt.verify" → JWT verification
Grep: "req.user" → authenticated user access
```

### Next.js Patterns
```
# Pages and routes
Glob: src/app/**/page.tsx, src/pages/**/*.tsx
Glob: src/app/**/route.ts, src/pages/api/**/*.ts → API routes

# Data fetching
Grep: "getServerSideProps" → SSR fetching (old pattern)
Grep: "async function.*Page" → Server component pattern
Grep: "use client" → Client components
Grep: "useQuery\|useSWR\|useFetch" → Client-side fetching

# State management
Grep: "createContext\|useContext\|Provider" → Context API
Grep: "zustand\|jotai\|recoil\|redux" → state management libraries

# Forms
Grep: "react-hook-form\|formik" → form library
Grep: "zod" → validation schema
```

### Go Patterns
```
# Handlers
Grep: "func.*Handler" → HTTP handlers
Grep: "http.HandleFunc\|router.GET\|r.GET" → route registration

# Services / Repositories
Grep: "type.*Service struct\|type.*Repository struct" → service/repo types
Grep: "interface {" → interface definitions

# Database
Grep: "sql.Open\|gorm.Open\|pgxpool.New" → database connections
Grep: "tx.Exec\|db.QueryRow\|db.Query" → query patterns

# Error handling
Grep: "if err != nil" → idiomatic Go error handling
Grep: "errors.Wrap\|fmt.Errorf" → error wrapping
```

---

## Step 4: Integration Map

Find every external service the codebase touches.

### HTTP Clients
```
Grep: "httpx\|requests\|aiohttp" → Python HTTP clients
Grep: "axios\|fetch\|node-fetch\|got\|ky" → JS HTTP clients
Grep: "net/http\|resty\|fasthttp" → Go HTTP clients
```

For each HTTP client usage, read surrounding code to identify:
- Target URL (often in env var or config)
- Authentication method (bearer token, API key, basic auth)
- Error handling approach

### Environment Variables (Integration Clues)
```
Grep: "os.environ\|os.getenv\|environ.get" → Python env usage
Grep: "process.env\." → Node.js env usage
Grep: "os.Getenv(" → Go env usage
```

List all env var names found. Group by service:
- `STRIPE_*` → Stripe integration
- `OPENAI_*` → OpenAI integration
- `TWILIO_*` → Twilio integration
- `DATABASE_URL` / `DB_*` → Database connection
- `REDIS_URL` / `REDIS_*` → Redis connection

### Webhook Handlers
```
Grep: "webhook" → any webhook endpoint
Grep: "stripe-signature\|X-Hub-Signature\|twilio" → specific service webhooks
```

---

## Step 5: Existing Plans Analysis

```
Glob: plans/**/*.md
Glob: specs/**/*.md, specs/**/*.yaml
```

Read all found plan files. Extract:
- What was already planned and when
- What patterns and decisions were already made
- What systems are already being built

This prevents the plan from conflicting with or duplicating existing decisions.

---

## Framework-Specific: What to Extract Per Stack

### Python / FastAPI
| Item | Where to find it |
|------|----------------|
| App version | pyproject.toml `[tool.poetry]` or `setup.cfg` |
| Database ORM | pyproject.toml dependencies (sqlalchemy, tortoise, beanie) |
| Migration tool | Glob alembic/, Glob migrations/ |
| Existing models | Grep `class.*Base\)` |
| Existing routes | Grep `@router` |
| Auth pattern | Grep `Depends(get_current_user)` |
| Background tasks | Grep `@scheduler`, `@celery`, `BackgroundTasks` |
| Settings class | Read `app/core/config.py` |

### Node.js / TypeScript
| Item | Where to find it |
|------|----------------|
| Framework | package.json `dependencies` (express, fastify, hono, koa) |
| ORM | package.json (prisma, typeorm, drizzle, sequelize) |
| Validation | package.json (zod, joi, yup) |
| Auth | package.json (passport, jose, next-auth) |
| Existing routes | Grep `router.(get|post)` |
| Types | Read types/ or @types/ for domain models |

### Next.js
| Item | Where to find it |
|------|----------------|
| App Router vs Pages | Glob src/app/ vs src/pages/ |
| API routes | Glob src/app/**/route.ts |
| Client vs Server components | Grep `use client` |
| Data patterns | Grep `fetch(` in server components |
| State | Grep `zustand\|redux\|jotai` |

---

## Output Format for Agent A

After completing the codebase scan, write findings to `.claude/plan-architect/codebase-research.md` in this format:

```markdown
# Codebase Research

## Tech Stack
- Runtime: [Python 3.12 / Node 20 / Go 1.21]
- Framework: [FastAPI 0.104 / Express 4.18 / Next.js 14]
- Database: [PostgreSQL via SQLAlchemy async]
- Queue: [ARQ / Celery / Bull]
- Auth: [JWT via custom middleware at app/api/deps.py:get_current_user]

## Architectural Patterns Found
- [Pattern name]: [What file / what it does / grep to find it]
- ...

## Relevant Existing Code
- [File path]: [Why it's relevant to the planned feature]
- ...

## External Integrations Found
- [Service]: [Evidence / env var names / files]
- ...

## Gaps Detected
- [Thing that exists in plan description but not in codebase]
- ...

## Reuse Opportunities
- [Existing pattern X] can be extended/reused for [planned feature Y]
- ...
```
