# linkedin-studio

**Version:** 1.0.0 | **Author:** Yasmine Seidu | **Namespace:** `ls` | **Tier:** 6

A production-grade LinkedIn content studio built as a Claude Code skill. linkedin-studio orchestrates an end-to-end research-to-publish pipeline across LinkedIn, Reddit, Google Trends, Neon PostgreSQL, Canva, and Metricool using 15 specialized skills — from topic discovery through AI humanization, visual design, and batch scheduling.

Built specifically for the AI consulting and implementation niche.

---

## What It Does

linkedin-studio manages the complete LinkedIn content lifecycle:

- **Intelligence layer** — Pulls signals from Reddit, Google Trends, and LinkedIn creator posts to surface high-engagement topics
- **Creation layer** — Generates posts, carousels, and document scripts with 3 A/B hook variants, then humanizes to defeat AI detection
- **Visual layer** — Generates AI image prompts and creates Canva designs using your brand kit
- **Distribution layer** — Plans content calendars, validates quality gates, and batch-schedules through Metricool

All content passes through automated quality gates before it can be scheduled. Posts that fail hook strength, AI detection, structure compliance, or duplicate similarity checks are blocked.

---

## Installation

linkedin-studio is a project-scoped Claude Code skill at `.claude/skills/linkedin-studio/`.

### Step 1 — Install system dependencies

```bash
# Python dependencies
pip install pytrends praw playwright serpapi psycopg2-binary openai

# Playwright browser (required for LinkedIn scraping)
npx playwright install chromium

# Node dependencies (for Canva MCP)
npm install -g @canva/cli
```

### Step 3 — Configure environment variables

Set credentials as environment variables in your shell profile or in Claude Code's `settings.json` under the `env` key. See the Environment Variables section below.

### Step 4 — Initialize the database

```bash
psql $NEON_DATABASE_URL -f .claude/skills/linkedin-studio/database/migrations/001_initial.sql
```

### Step 5 — Verify installation

Start a Claude Code session and run:

```
Run ls:research-engine with niche "AI consulting", keywords "AI implementation"
```

---

## Environment Variables

All credentials are set as shell environment variables or in Claude Code's `settings.json` under the `env` key.

| Variable | Required | Description | Example |
|---|---|---|---|
| `NEON_DATABASE_URL` | Yes | Neon PostgreSQL connection string | `postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/linkedin_studio` |
| `METRICOOL_API_KEY` | Yes | Metricool API key for scheduling | `mc_xxxxxxxxxxxxxxxx` |
| `METRICOOL_USER_ID` | Yes | Metricool account user ID | `12345` |
| `REDDIT_CLIENT_ID` | Yes | Reddit app client ID | `xXxXxXxXxXxX` |
| `REDDIT_CLIENT_SECRET` | Yes | Reddit app client secret | `xXxXxXxXxXxXxXxXxX` |
| `REDDIT_USERNAME` | Yes | Reddit account username | `your_username` |
| `REDDIT_PASSWORD` | Yes | Reddit account password | `your_password` |
| `OPENAI_API_KEY` | Yes | OpenAI API key (DALL-E 3 + embeddings) | `sk-proj-...` |
| `SERPAPI_KEY` | Recommended | SerpAPI key for LinkedIn scraping fallback | `xxxxxxxxxxxxxxxxxxx` |
| `CANVA_API_KEY` | Optional | Canva API key for design creation | `OAuthToken...` |
| `GOOGLE_IMAGEN_PROJECT_ID` | Optional | GCP project ID for Google Imagen | `my-project-id` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Optional | Path to GCP service account JSON | `/path/to/credentials.json` |
| `METRICOOL_BASE_URL` | Auto | Metricool API base URL | `https://app.metricool.com/api/v2` |
| `PUSHSHIFT_BASE_URL` | Auto | Pushshift Reddit API base | `https://api.pushshift.io/reddit` |
| `PLAYWRIGHT_HEADLESS` | Auto | Run Playwright headlessly | `true` |
| `PLAYWRIGHT_TIMEOUT_MS` | Auto | Playwright request timeout | `30000` |
| `NEON_POOL_SIZE` | Auto | Neon connection pool size | `5` |

**Required** = pipeline will not run without it. **Recommended** = degraded functionality if missing. **Optional** = specific integrations only. **Auto** = has a working default.

---

## Quick Start

Three commands to go from zero to scheduled post:

```bash
# 1. Research trending topics for your niche
"Run ls:research-engine with niche 'AI consulting', keywords 'AI agents, LLM implementation, RAG pipelines'"

# 2. Write and humanize a post from the top-ranked topic
"Run ls:content-writer with the top topic from research, format text_post, then pass to ls:humanizer"

# 3. Run structure review and schedule for next Tuesday at 8am UTC
"Run ls:structure-reviewer on the humanized draft, then ls:batch-scheduler to schedule for Tuesday 08:00 UTC"
```

Or run the full pipeline in one command:

```bash
"Run ls:content-pipeline with niche 'AI consulting', keywords 'AI agents, automation', target 3 posts"
```

---

## Pipeline Overview

```
INTELLIGENCE LAYER
├── ls:research-engine     → Orchestrates all research sources
│   ├── Google Trends      → Rising queries, breakout keywords
│   ├── ls:pain-point-miner → Reddit pain points (Pushshift + PRAW)
│   └── ls:creator-analyzer → LinkedIn creator post patterns
└── ls:competitor-tracker  → Competitor profile monitoring

CREATION LAYER
├── ls:content-writer      → Generates drafts with 3 hook variants
├── ls:humanizer           → 6-pass AI detection removal
├── ls:structure-reviewer  → 7-dimension quality scoring
└── ls:repurposer          → Long-form → LinkedIn format conversion

VISUAL LAYER
├── ls:visual-prompter     → JSON prompts for DALL-E / Imagen / Midjourney
└── ls:canva-designer      → Canva MCP carousel + image creation

DISTRIBUTION LAYER
├── ls:content-calendar    → Weekly/monthly schedule planning
├── ls:idea-bank           → Topic bank + brand voice management
├── ls:analytics-dashboard → Metricool performance reporting
└── ls:batch-scheduler     → Quality-gated Metricool batch submission

ORCHESTRATOR
└── ls:content-pipeline    → Full pipeline: research → schedule
```

The pipeline runs with circuit breakers at every external service boundary. If any source fails (Google Trends rate-limit, LinkedIn scrape block, Neon unavailable), the pipeline degrades gracefully and continues with available data.

---

## Skills Reference

| Skill | Tier | Description |
|---|---|---|
| `ls:research-engine` | 5 | Multi-source research orchestrator — Google Trends, Reddit, LinkedIn creators |
| `ls:creator-analyzer` | 4 | LinkedIn creator post scraper with Playwright → SerpAPI → manual paste fallback chain |
| `ls:pain-point-miner` | 4 | Reddit pain point extraction via Pushshift + PRAW, clustered by theme and emotional intensity |
| `ls:competitor-tracker` | 4 | Competitor LinkedIn profile monitoring on configurable cadence |
| `ls:content-writer` | 4 | LinkedIn post and carousel generator with 3 A/B hook variants per draft |
| `ls:humanizer` | 4 | 6-pass AI phrase removal pipeline targeting GPTZero, Copyleaks, and Originality.ai |
| `ls:structure-reviewer` | 3 | 7-dimension LinkedIn structure scorer (hook, body, whitespace, CTA, hashtags, length, readability) |
| `ls:repurposer` | 3 | Transforms articles, transcripts, and newsletters into LinkedIn post formats |
| `ls:visual-prompter` | 3 | Structured JSON prompt generator for DALL-E 3, Imagen, Midjourney, and Stable Diffusion |
| `ls:canva-designer` | 4 | Canva MCP integration — creates branded carousels and single-image posts |
| `ls:content-calendar` | 4 | Weekly/monthly content calendar planning with pillar balancing and optimal timing |
| `ls:idea-bank` | 3 | Neon topic bank browser — retrieve, tag, score, and archive content ideas |
| `ls:analytics-dashboard` | 4 | Metricool analytics reporting with top post analysis and recommendations |
| `ls:batch-scheduler` | 4 | Quality-gated batch submission to Metricool with circuit breaker |
| `ls:content-pipeline` | 6 | Master orchestrator that chains the full research-to-schedule workflow |

---

## Slash Commands

| Command | Usage | Description |
|---|---|---|
| `/ls:research` | `/ls:research "AI agents in enterprise"` | Run research engine for a topic |
| `/ls:write` | `/ls:write topic_id:tp_042 format:text_post` | Write a post from a topic bank entry |
| `/ls:humanize` | `/ls:humanize` (with draft in context) | Run 6-pass humanizer on current draft |
| `/ls:review` | `/ls:review` (with draft in context) | Run structure review and get quality score |
| `/ls:visual` | `/ls:visual format:carousel_slide platform:dalle3` | Generate AI image prompts for a post |
| `/ls:canva` | `/ls:canva` (with approved post in context) | Create Canva design from post content |
| `/ls:calendar` | `/ls:calendar week` | Generate or view weekly content calendar |
| `/ls:schedule` | `/ls:schedule` (with approved posts in context) | Batch-submit approved posts to Metricool |
| `/ls:analyze` | `/ls:analyze https://linkedin.com/in/username` | Analyze a creator's post patterns |
| `/ls:competitors` | `/ls:competitors` | Run competitor tracker on monitored profiles |
| `/ls:ideas` | `/ls:ideas` | Browse topic bank and idea inventory |
| `/ls:pipeline` | `/ls:pipeline niche:"AI consulting" target:5` | Run full content pipeline end-to-end |

---

## Neon Database Setup

linkedin-studio uses Neon PostgreSQL for persistent storage across all sessions. All tables are prefixed with `ls_`.

### Tables Required

| Table | Purpose |
|---|---|
| `ls_topic_bank` | Research results — topics scored by composite engagement signal |
| `ls_brand_voice` | Brand voice profile — tone, vocabulary, content pillars, visual style |
| `ls_content_drafts` | Draft posts — status tracking from DRAFT through APPROVED |
| `ls_published_posts` | Published post record with Metricool post ID and analytics snapshots |
| `ls_competitor_snapshots` | Competitor profile data — posting frequency, topic clusters, engagement patterns |
| `ls_analytics_cache` | Metricool analytics cache — performance metrics per post and per week |
| `ls_audit_log` | Full audit trail — every skill invocation with inputs, outputs, and quality scores |
| `creator_posts_cache` | LinkedIn creator post cache — scraped posts with engagement and pattern data |
| `brand_voice_profile` | Active brand voice row (single-row reference table for skill queries) |
| `content_queue` | Approved posts pending scheduling — used by batch-scheduler and visual-prompter |

### Initialize

```bash
psql $NEON_DATABASE_URL -f .claude/skills/linkedin-studio/database/migrations/001_initial.sql
```

### Connection

The plugin uses `NEON_DATABASE_URL` from settings. All skills handle connection failure gracefully — they warn and continue with degraded functionality rather than crashing. Pool size defaults to 5 connections.

---

## Quality Gates

linkedin-studio enforces quality gates at the scheduling boundary. A post cannot be submitted to Metricool unless it passes all four gates:

| Gate | Threshold | What It Checks |
|---|---|---|
| Post quality score | >= 75/100 | Overall composite quality (hook + body + CTA + structure) |
| AI detection score | <= 25/100 | AI-generated language probability (GPTZero-equivalent scoring) |
| Hook strength score | >= 7/10 | Hook formula compliance, curiosity gap, pattern interrupt |
| Duplicate similarity | <= 60% | Cosine similarity against all posts published in the last 90 days |

These thresholds are configured in `settings.json` under `defaults` and can be adjusted per project.

The `PreToolUse` hook on `ls:batch-scheduler` and `ls:content-calendar` enforces these gates automatically. Any post failing a gate is rejected with a specific reason and suggestions for improvement.

---

## Integration Setup

### Metricool

1. Log in to Metricool and go to Settings > API Access
2. Generate an API key
3. Copy your User ID from the account page
4. Set `METRICOOL_API_KEY` and `METRICOOL_USER_ID` in settings

Metricool is used for: batch scheduling, analytics retrieval, optimal time suggestions.

### Reddit (PRAW + Pushshift)

1. Go to https://www.reddit.com/prefs/apps and create a "script" app
2. Copy the client ID (under the app name) and secret
3. Set `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`, `REDDIT_PASSWORD`

Default subreddits monitored: `r/Entrepreneur`, `r/consulting`, `r/startups`, `r/freelance`, `r/marketing`, `r/artificial`, `r/smallbusiness`.

### LinkedIn Scraping (Playwright)

No API key required. Playwright runs headlessly and scrapes creator public activity feeds.

```bash
npx playwright install chromium
```

If LinkedIn blocks scraping (CAPTCHA or login wall), the system falls back to SerpAPI automatically, then prompts for manual paste as a final fallback.

### SerpAPI

1. Sign up at https://serpapi.com and generate an API key
2. Set `SERPAPI_KEY` in settings

SerpAPI is the fallback for LinkedIn scraping when Playwright is blocked. It counts against your SerpAPI quota — the plugin uses it sparingly.

### OpenAI (DALL-E 3 + Embeddings)

1. Generate an API key at https://platform.openai.com/api-keys
2. Set `OPENAI_API_KEY` in settings

Used for: DALL-E 3 image generation (via `ls:visual-prompter`) and topic similarity embeddings (duplicate detection in `ls:research-engine`).

### Canva

1. Register a Canva app at https://www.canva.com/developers/
2. Obtain an OAuth token or API key
3. Set `CANVA_API_KEY` in settings
4. Ensure the Canva MCP server is running

Used for: `ls:canva-designer` to create branded LinkedIn carousels and single-image posts.

### Google Imagen (Optional)

1. Enable Vertex AI on your GCP project
2. Create a service account with Vertex AI User role
3. Download the service account JSON credentials
4. Set `GOOGLE_IMAGEN_PROJECT_ID` and `GOOGLE_APPLICATION_CREDENTIALS`

Only required if you want Google Imagen as an image generation alternative to DALL-E 3.

---

## Troubleshooting

### Playwright fails to install

```bash
# Install system dependencies first (macOS)
brew install --cask chromium

# Then install Playwright
npx playwright install chromium --with-deps
```

### LinkedIn scraping returns zero posts

This usually means LinkedIn is serving a login wall. The system should fall back to SerpAPI automatically. Check:

1. `SERPAPI_KEY` is set correctly in settings
2. SerpAPI quota is not exhausted (check https://serpapi.com/dashboard)
3. If both fail, use manual paste mode — the skill will prompt you

### Neon connection refused

```bash
# Test connection directly
psql $NEON_DATABASE_URL -c "SELECT 1"
```

Common causes: IP not allowlisted in Neon dashboard, connection string format incorrect (must include `?sslmode=require` for Neon), pool exhaustion.

Skills handle Neon failure gracefully — they warn and continue. Persistent data will not be stored, but the pipeline continues.

### Reddit API returns 401

Reddit credentials for PRAW use the account's actual username and password (not OAuth). Verify that the app type in Reddit's developer portal is "script" not "web app".

### Posts blocked by quality gates

The error message from the PreToolUse hook will specify which gate failed and why. Common fixes:

- **AI score too high** — Run `ls:humanizer` again, or manually rewrite sentences flagged as AI-sounding
- **Hook score too low** — Run `ls:structure-reviewer` with `fix_hooks: true` to get specific rewrites
- **Duplicate similarity too high** — Check `ls:idea-bank` for the similar existing post and differentiate the angle

### Metricool API returns 403

Verify `METRICOOL_USER_ID` matches the account that owns the API key. The user ID is a numeric value found in Metricool account settings, not the username.
