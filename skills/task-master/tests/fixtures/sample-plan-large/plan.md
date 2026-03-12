# Plan: Niche Scout Agent System
**Date:** 2026-03-02
**Status:** APPROVED
**Complexity:** 4/5

---

## Overview

The Niche Scout Agent System is an automated research pipeline that discovers profitable
content niches by scraping Reddit, scoring opportunity gaps, and generating structured
reports. The system runs as a background job triggered daily, stores all findings in
Postgres, and exposes results via a FastAPI endpoint for downstream agents.

Pipeline: Scheduler → Reddit Scraper Agent → Opportunity Scorer → Report Generator → DB Write

This plan covers all implementation sections from database migrations through deployment.
Total estimated tasks: ~20. Some sections are large enough to warrant sub-tasks.

---

## Section 1: Database Migrations

Create Alembic migration for all Niche Scout tables. This is the foundation — all other
sections depend on it.

**Tables to create:**
- `niche_research_runs` — tracks each pipeline execution (id, status, triggered_at, completed_at, config_json)
- `subreddits_scraped` — Reddit communities analyzed (id, name, subscriber_count, scraped_at, run_id FK)
- `niche_opportunities` — scored opportunities (id, niche_name, score, evidence_json, run_id FK)
- `niche_keywords` — keyword associations per opportunity (id, keyword, frequency, opportunity_id FK)
- `scout_reports` — final generated reports (id, report_md, summary, run_id FK, created_at)

**Alembic migration file:** `alembic/versions/XXXX_niche_scout_tables.py`

Migration must include: FK constraints, indexes on `run_id` and `status`, rollback function.

---

## Section 2: NicheResearchRun Model

SQLAlchemy async model for the `niche_research_runs` table.

**File:** `app/models/niche_research_run.py`

Fields: `id` (UUID), `status` (Enum: pending/running/completed/failed), `triggered_at` (DateTime),
`completed_at` (DateTime, nullable), `config_json` (JSON), `error_message` (Text, nullable),
plus `TimestampMixin` (created_at, updated_at).

Register in `app/models/__init__.py`. Add to Alembic `target_metadata`.

---

## Section 3: SubredditScraped Model

SQLAlchemy async model for the `subreddits_scraped` table.

**File:** `app/models/subreddit_scraped.py`

Fields: `id` (UUID), `name` (str, unique per run), `subscriber_count` (int), `post_count_analyzed` (int),
`pain_signals` (JSON), `scraped_at` (DateTime), `run_id` (UUID FK → niche_research_runs.id).

---

## Section 4: NicheOpportunity Model

SQLAlchemy async model for the `niche_opportunities` table.

**File:** `app/models/niche_opportunity.py`

Fields: `id` (UUID), `niche_name` (str), `opportunity_score` (Float), `evidence_json` (JSON),
`competition_level` (Enum: low/medium/high), `estimated_audience_size` (int, nullable),
`run_id` (UUID FK → niche_research_runs.id).

---

## Section 5: NicheKeyword Model

SQLAlchemy async model for the `niche_keywords` table.

**File:** `app/models/niche_keyword.py`

Fields: `id` (UUID), `keyword` (str), `frequency` (int), `sentiment_score` (Float, nullable),
`opportunity_id` (UUID FK → niche_opportunities.id).

---

## Section 6: ScoutReport Model

SQLAlchemy async model for the `scout_reports` table.

**File:** `app/models/scout_report.py`

Fields: `id` (UUID), `report_markdown` (Text), `summary` (Text), `top_niches` (JSON),
`run_id` (UUID FK → niche_research_runs.id, unique=True), `generated_at` (DateTime).

---

## Section 7: OpenRouter Client Integration

Integrate the OpenRouterClient with Niche Scout agents for LLM-based opportunity scoring
and report generation.

**File:** `app/services/niche_scout_llm.py`

Wraps `OpenRouterClient` (existing) with niche-specific prompt templates and structured
output parsing. Must handle: prompt template loading from DB via `PromptManager`,
JSON response parsing with Pydantic models, retry on rate limit.

**New Pydantic schemas:**
- `OpportunityScoreResult(BaseModel)` — niche_name, score (0–10), rationale, keywords (list[str])
- `ReportGenerationResult(BaseModel)` — title, summary, sections (list[str]), top_niches (list[str])

Load prompts by slug: `niche-opportunity-scorer`, `niche-report-generator`.

---

## Section 8: Rate Limiter Service for Reddit API

Reddit API has strict rate limits: 60 requests/minute for OAuth clients. Implement
a `RedditRateLimiter` that wraps the existing `RateLimiterService` with Reddit-specific
defaults and exponential backoff.

**File:** `app/services/reddit_rate_limiter.py`

Reddit-specific: `window_seconds=60`, `limit=55` (5-request safety buffer),
backoff formula: `min(60, 2^attempt)` seconds, max 3 retries before raising.

Also implement `RedditAPIError(Exception)` and `RedditRateLimitError(RedditAPIError)`.

---

## Section 9: Reddit Scraper Service

Core scraper that fetches posts and comments from target subreddits using the Reddit API.

**File:** `app/services/reddit_scraper.py`

Class: `RedditScraperService`
- `async def scrape_subreddit(name: str, post_limit: int = 100) -> SubredditData`
  — Fetches top posts, extracts titles, bodies, comment counts, upvotes
- `async def extract_pain_signals(posts: list[RedditPost]) -> list[str]`
  — Uses keyword matching to find pain signal phrases
- Internal: `_build_reddit_headers()` using `get_settings().REDDIT_CLIENT_ID` and
  `get_settings().REDDIT_CLIENT_SECRET`

Rate limiting: all outbound calls go through `RedditRateLimiter`.
Authentication: OAuth2 client credentials flow, token cached in Redis (TTL = 3600s).

**Grep patterns:**
- `grep -rn "httpx.AsyncClient" app/services/` — confirm async HTTP pattern
- `grep -rn "REDDIT_" app/config.py` — check if Reddit config exists

---

## Section 10: Opportunity Scorer Agent

LLM-based agent that scores each scraped subreddit as a niche opportunity.

**File:** `app/agents/opportunity_scorer.py`

Pydantic AI agent using `OpportunityScoreResult` as output schema.
- Input: `SubredditData` (scraped posts + pain signals)
- Output: `OpportunityScoreResult` (niche_name, score 0-10, rationale, keywords)
- Model: `openrouter:anthropic/claude-3-haiku` (cheap, fast, good at structured output)
- Retry: 3 attempts with exponential backoff on validation error
- System prompt loaded from DB slug: `niche-opportunity-scorer`

---

## Section 11: Report Generator Agent

LLM-based agent that synthesizes scored opportunities into a final markdown report.

**File:** `app/agents/report_generator.py`

Pydantic AI agent using `ReportGenerationResult` as output schema.
- Input: `list[OpportunityScoreResult]` sorted by score descending
- Output: `ReportGenerationResult` with full markdown report
- Model: `openrouter:anthropic/claude-3-5-sonnet` (higher quality for final report)
- System prompt loaded from DB slug: `niche-report-generator`
- Max tokens: 4096 (report can be long)

---

## Section 12: Pipeline Orchestrator

Background job that coordinates the full Niche Scout pipeline end-to-end.

**File:** `app/workers/niche_scout_pipeline.py`

Class: `NicheScoutPipeline`
Phases: (1) Create run record → (2) Scrape subreddits → (3) Score opportunities →
(4) Generate report → (5) Write results to DB → (6) Mark run completed

Error handling: Any phase failure → mark run as `failed`, log error to `error_message`,
do NOT re-raise (swallow to prevent background job crash).

Subreddits to scrape loaded from `get_settings().NICHE_SCOUT_SUBREDDITS` (comma-separated string).

---

## Section 13: Webhook Handler

POST endpoint triggered by Coolify's scheduled cron to start a pipeline run.

**File:** `app/api/routes/niche_scout.py`

Routes:
- `POST /api/v1/niche-scout/run` — trigger a new pipeline run (background task)
- `GET /api/v1/niche-scout/runs` — list recent runs with status
- `GET /api/v1/niche-scout/runs/{run_id}` — get run details + report if completed
- `GET /api/v1/niche-scout/runs/{run_id}/report` — get full markdown report

Authentication: `X-Internal-Token` header, value from `get_settings().INTERNAL_API_TOKEN`.

---

## Section 14: Background Job Scheduler

APScheduler configuration for daily Niche Scout pipeline execution.

**File:** `app/workers/scheduler.py`

Schedule: `cron(hour=3, minute=0)` — 3:00 AM UTC daily
Job: calls `POST /api/v1/niche-scout/run` internally via httpx to decouple scheduler from pipeline.
Scheduler started in `app/main.py` lifespan event (not in a separate worker process).

Config: `get_settings().NICHE_SCOUT_ENABLED` (bool, default False) — disables job if False.

---

## Section 15: Unit Tests — Models

Unit tests for all 5 Niche Scout SQLAlchemy models.

**File:** `tests/unit/test_niche_scout_models.py`

- Test model instantiation with all required fields
- Test default values (UUID generation, status defaults)
- Test FK relationship declarations
- Test `TimestampMixin` fields populated on create
- 1 test per model = 5 minimum tests

---

## Section 16: Unit Tests — Services

Unit tests for Reddit scraper, rate limiter wrapper, and LLM service.

**File:** `tests/unit/test_niche_scout_services.py`

- `test_reddit_scraper_builds_correct_headers` — mock httpx, assert Authorization header
- `test_reddit_scraper_extracts_pain_signals` — fixture posts → assert pain phrases found
- `test_reddit_rate_limiter_respects_limit` — mock RateLimiterService, assert called with correct args
- `test_niche_scout_llm_parses_json_response` — mock OpenRouterClient, assert Pydantic parse
- `test_niche_scout_llm_retries_on_validation_error` — mock returns invalid JSON twice, then valid

---

## Section 17: Unit Tests — Agents

Unit tests for the two Pydantic AI agents.

**File:** `tests/unit/test_niche_scout_agents.py`

- `test_opportunity_scorer_returns_valid_schema` — mock LLM response, assert schema validated
- `test_opportunity_scorer_retries_on_invalid_output` — mock returns invalid JSON once, then valid
- `test_report_generator_returns_markdown` — mock LLM, assert output contains markdown headers
- `test_report_generator_handles_empty_opportunities` — empty input → graceful minimal report

---

## Section 18: Integration Tests

End-to-end integration tests using real database (test Postgres) but mocked external APIs.

**File:** `tests/integration/test_niche_scout_pipeline.py`

- `test_pipeline_creates_run_record` — pipeline start → DB has run in `running` status
- `test_pipeline_completes_and_writes_report` — full mocked pipeline → report in DB
- `test_pipeline_marks_failed_on_scraper_error` — scraper raises → run status = `failed`
- `test_webhook_triggers_background_task` — POST /api/v1/niche-scout/run → 202 accepted

---

## Section 19: Live API Tests — Reddit

Live integration tests requiring real Reddit API credentials.

**File:** `tests/live/test_reddit_live.py`

- `test_live_scrape_python_subreddit` — scrape r/Python with limit=5, assert post count >= 1
- `test_live_rate_limiter_respected` — make 60 rapid requests, assert no HTTP 429

Requires: `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET` in `.env`.

---

## Section 20: Deployment Config

Docker and environment configuration for the Niche Scout system on Coolify.

**Files to update:**
- `Dockerfile` — confirm `apscheduler` in requirements, no new build steps needed
- `.env.example` — add new env vars: `NICHE_SCOUT_ENABLED`, `NICHE_SCOUT_SUBREDDITS`,
  `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `INTERNAL_API_TOKEN`
- Coolify cron: `0 3 * * * curl -X POST http://localhost:8000/api/v1/niche-scout/run -H "X-Internal-Token: $INTERNAL_API_TOKEN"`
- Health check: `GET /health/ready` should verify DB and Redis connections

---

## Non-Implementation Sections (Skip — do not generate tasks)

### Architecture Context

Data flows: Scheduler → Pipeline → [Scraper, Scorer, ReportGen] → DB → API
All external calls (Reddit, OpenRouter) are async with circuit breaker protection.
Redis used for: rate limiting, OAuth token caching, pipeline state caching.

### Security Notes

Reddit credentials are read-only OAuth2. Token refresh handled automatically.
Internal API token protects the webhook trigger endpoint from public invocation.
No user PII is stored — only public Reddit post content.
