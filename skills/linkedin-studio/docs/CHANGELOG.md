# Changelog

All notable changes to linkedin-studio are documented in this file.

Format: `[version] - YYYY-MM-DD`

---

## [2.0.0] - 2026-03-02

### Changed

**Database**
- Migration 002: Added `ls_` prefix to all tables, added missing columns (`contraction_style` to brand_voice_profile, `override_gates` to content_queue), converted `TEXT` columns to `TEXT[]` for array fields (hook_suggestions, cta_suggestions, post_ideas, sources, content_pillars, vocabulary_preferences, avoid_words, signature_phrases), added `neon-utils.sh` helper script

**Reference Files**
- 20 reference files created across 5 skills:
  - research-engine: NEON-SCHEMA.md, SCORING-MODEL.md, SCRAPING-STRATEGY.md, GOOGLE-TRENDS-PARAMS.md, REDDIT-INTEGRATION.md
  - content-writer: NEON-SCHEMA.md, HOOK-FORMULAS.md, LINKEDIN-FORMATS.md, CTA-LIBRARY.md
  - humanizer: AI-PHRASES-BLOCKLIST.md, DETECTION-HEURISTICS.md, SENTENCE-PATTERNS.md, PERSONALITY-LIBRARY.md, BRAND-VOICE-INJECTION.md
  - batch-scheduler: METRICOOL-SCHEDULE-API.md, CIRCUIT-BREAKER.md, QUALITY-GATES.md
  - content-pipeline: STAGE-HANDOFFS.md, GATE-DEFINITIONS.md, PIPELINE-MODES.md

**Orchestration**
- Pipeline can now invoke sub-skills via Agent tool
- All skills have correct tools lists matching their actual requirements
- content-pipeline tools list updated: Read, Write, Bash, Agent, Glob, Grep, WebFetch, WebSearch, AskUserQuestion

**Hooks**
- 3 Claude Code hooks created:
  - `PreToolUse` — pre-tool-use-quality-gate.sh (blocking quality gate before scheduling)
  - `PostToolUse` — post-tool-use-logger.sh (non-blocking audit logging to Neon)
  - `Stop` — stop-final-validation.sh (end-of-session validation for unresolved drafts)

### Added

**New Skills (4)**
- `ls:neon-setup` (Tier 2) — Database setup, migration runner, connection health checker
- `ls:brand-voice-builder` (Tier 3) — Interactive brand voice profile interview and Neon writer
- `ls:performance-feedback-loop` (Tier 4) — Metricool performance sync, hook library scoring, winning pattern identification
- `ls:onboarding` (Tier 3) — First-time setup wizard: env validation, DB init, brand voice, integration testing

**New Slash Commands (4)**
- `/ls:setup` — Run Neon database setup and migration
- `/ls:brand-voice` — Build or update brand voice profile
- `/ls:feedback` — Sync performance data and update content recommendations
- `/ls:onboarding` — First-time setup wizard

**Context Files (5)**
- `context/PLUGIN.md` — Plugin architecture overview and skill map
- `context/BRAND-VOICE.md` — Brand voice configuration guide
- `context/CONTENT-PILLARS.md` — Content pillar definitions and strategy
- `context/QUALITY-STANDARDS.md` — Quality gate thresholds and scoring rubrics
- `context/INTEGRATION-GUIDE.md` — External service integration reference

**Setup Files**
- `.env.example` — All required and optional environment variables documented
- `setup/validate-env.sh` — Environment variable validation script
- `database/neon-utils.sh` — Neon PostgreSQL utility functions (connect, query, migrate)

### Summary

- **Total skills:** 19 (15 original + 4 new)
- **Total slash commands:** 16 (12 original + 4 new)
- **Total database tables:** 11
- **Total hook scripts:** 8 (5 skill-level + 3 Claude Code)
- **Total reference files:** 20
- **Total files:** 84
- **All skills and plugin.json bumped to v2.0.0**

---

## [1.0.0] - 2026-03-02

### Added

**Core Plugin Infrastructure**
- Plugin manifest (`plugin.json`) with Tier 6 classification and full skill registry
- Settings schema (`settings.json`) with environment variable definitions, quality thresholds, scheduling defaults, and feature flags
- Global install path at `~/.claude/plugins/linkedin-studio/`
- Namespace `ls` registered for all skills and slash commands
- Neon PostgreSQL integration with 7 prefixed tables (`ls_*`) plus 3 shared tables

**Intelligence Layer — 4 Skills**

- `ls:research-engine` (Tier 5) — Multi-source topic research orchestrator
  - Parallel dispatch to Google Trends (pytrends), Reddit (Pushshift + PRAW), and LinkedIn creator analysis
  - Composite scoring formula: trend_score × 0.35 + pain_intensity × 0.40 + creator_engagement × 0.25
  - Multi-source bonus: +10% for topics appearing in 2 sources, +20% for all 3
  - 5-phase graceful degradation: continues if any individual source fails
  - Semantic deduplication against Neon `topic_bank` using cosine similarity (threshold: 0.85)
  - Outputs ranked topic table with hook suggestions, CTA suggestions, and post ideas per topic
  - Exponential backoff retry for Neon writes (2s, 4s, 8s)
  - All errors logged with `[research-engine][ERROR]` prefix for Coolify log capture

- `ls:creator-analyzer` (Tier 4) — LinkedIn creator post scraper and pattern extractor
  - 3-fallback scraping chain: Playwright → SerpAPI → manual paste
  - Playwright: headless Chromium, 2-second rate limiting, 5 concurrent sessions maximum
  - SerpAPI fallback: Google site search for creator posts with estimated engagement scoring
  - Manual paste fallback: structured prompts for browser copy-paste with parsing
  - 24-hour cache check against Neon `creator_posts_cache` before any scraping
  - Top 20% engagement filter (reactions + comments × 3 + shares × 2 scoring)
  - Pattern extraction: 6 hook types, 5 CTA types, emoji usage levels, paragraph structure
  - Supports up to 20 creators per session; auto-discovers top creators from niche keyword
  - Outputs insight report with top hooks, structural patterns, and adapted hook suggestions

- `ls:pain-point-miner` (Tier 4) — Reddit pain point extraction engine
  - Dual-source: Pushshift API for historical search + PRAW for real-time retrieval
  - Default subreddit set: r/Entrepreneur, r/smallbusiness, r/consulting, r/startups, r/freelance, r/marketing, r/artificial
  - Filters: minimum 50 upvotes, last 30 days default time window, up to 100 posts per subreddit
  - Emotional intensity scoring: upvote-weighted, clustered by pain theme
  - Deduplication against existing topic_bank entries
  - Output: ranked pain point list with subreddit source, upvote count, comment count, and URL

- `ls:competitor-tracker` (Tier 4) — Competitor LinkedIn profile monitor
  - Configurable monitoring cadence (default: weekly)
  - Tracks: posting frequency, engagement patterns, topic clusters, format distribution
  - Surfaces new topics competitors are covering that you haven't addressed
  - Flags competitors posting more than 2 times in a 7-day window
  - Stores snapshots in Neon `ls_competitor_snapshots` for trend analysis
  - Weekly diff report: new topics, engagement changes, frequency changes

**Creation Layer — 4 Skills**

- `ls:content-writer` (Tier 4) — LinkedIn post and carousel script generator
  - Accepts topic_id (from Neon topic_bank), raw_topic string, or URL (via WebFetch)
  - Supported formats: text_post, carousel_script, poll_post, document_post
  - Generates exactly 3 hook variants per draft: question hook, stat hook, story hook
  - Hook rules: max 15 words, no generic openers, must create curiosity gap or pattern interrupt
  - Body rules: max 15 words per sentence, 1-2 lines per paragraph, blank line between paragraphs
  - CTA variants: soft (reflection), medium (engagement), direct (conversion with trigger word)
  - Carousel script: labeled slides ([SLIDE 1] through [SLIDE N]), max 40 words per slide
  - Poll post: framing paragraph + question + 2-4 options + closing paragraph
  - All output marked DRAFT PENDING QUALITY REVIEW — requires humanizer and structure-reviewer
  - Loads brand voice from Neon `brand_voice_profile` table; uses default AI consulting voice on Neon failure
  - Pre-screens hooks against AI phrase blocklist before humanizer runs

- `ls:humanizer` (Tier 4) — 6-pass AI detection removal and naturalness rewriter
  - Pass 1: AI phrase substitution (targets GPTZero, Copyleaks, Originality.ai detection patterns)
  - Pass 2: Sentence structure variation (breaks uniform sentence length patterns)
  - Pass 3: Vocabulary naturalness (replaces high-frequency AI-generated word choices)
  - Pass 4: Rhythm adjustment (varies cadence, introduces natural sentence fragments)
  - Pass 5: Perspective deepening (adds practitioner specificity, removes generic generalizations)
  - Pass 6: Final detection scan and residual cleanup
  - Aggressive mode: increases substitution intensity, targets sentence-level rewrite not word-level
  - Default blocked words: leverage, utilize, delve, synergy, game-changer, it's important to note, in today's rapidly evolving landscape, we, our team
  - Target reading level: grade 10-12 (accessible to technical and executive audiences)
  - Target AI score: below 25/100 (plugin quality gate)
  - Sentence variability minimum: 0.4 (ratio of sentence length standard deviation to mean)

- `ls:structure-reviewer` (Tier 3) — 7-dimension LinkedIn post quality scorer
  - Dimension 1 — Hook strength (0-10): formula compliance, curiosity gap, pattern interrupt, word count
  - Dimension 2 — Body flow (0-10): sentence length variance, paragraph length compliance, narrative arc
  - Dimension 3 — Whitespace formatting (0-10): blank line presence between paragraphs, line break usage
  - Dimension 4 — CTA presence and quality (0-10): CTA exists, specificity, friction level, trigger word
  - Dimension 5 — Hashtag count and relevance (0-10): 3-5 hashtags, mix of niche/reach/community
  - Dimension 6 — Word count appropriateness (0-10): scored against format-specific ranges (150-3000)
  - Dimension 7 — Readability (0-10): Flesch-Kincaid grade, sentence complexity, vocabulary level
  - Minimum passing score: 75/100 overall, 7/10 on hook strength
  - On failure: returns specific fix recommendations per failing dimension
  - Supports `fix_hooks: true` flag to auto-generate 3 alternative hooks that would pass

- `ls:repurposer` (Tier 3) — Long-form to LinkedIn format transformer
  - Accepts: blog articles, newsletter issues, podcast transcripts, webinar recordings (transcript), PDF documents
  - Input via URL (WebFetch), file path, or direct paste
  - Extracts: title, key claims (max 5), supporting data points, direct quotes
  - Output formats: text_post (single best insight), carousel_script (multi-point breakdown), listicle (numbered insight post)
  - Preserves original phrasing for quotes while adapting surrounding copy to LinkedIn format rules
  - Flags repurposed content with source attribution suggestion ("Originally published at...")
  - Does not plagiarize — summarizes and reframes rather than excerpting

**Visual Layer — 2 Skills**

- `ls:visual-prompter` (Tier 3) — Structured JSON image prompt generator
  - Supported generation platforms: DALL-E 3 (OpenAI API), Google Imagen (Vertex AI), Midjourney (prompt text), Stable Diffusion XL
  - Supported formats: image_post (1080x1080), infographic (1080x1350), carousel_slide (1080x1080 series), quote_graphic (1080x1080)
  - Per-slide JSON objects with all required fields: platform, format, dimensions, style, background, text_overlay, visual_description, brand_colors, font_style, mood, negative_prompt
  - Platform-specific variations: DALL-E 3 (JSON as-is), Imagen (guidance_scale + disallowed_text), Midjourney (--v 6 --ar flags), SD (cfg_scale + sampler)
  - Negative prompt always included for DALL-E and SD (suppresses stock photo/generic aesthetics)
  - Content pillar to mood mapping: thought leadership → visionary/bold, education → clear/structured, social proof → warm/credible, CTA → urgent/direct
  - Brand defaults pulled from Neon `brand_voice_profile`; fallback: `#1a1a2e`, `#4a4a8a`, `#ffffff`, clean professional minimal
  - Carousel cap: maximum 10 slides
  - Output: formatted block with copy-pasteable JSON sections and Midjourney variations

- `ls:canva-designer` (Tier 4) — Canva MCP design creator
  - Creates LinkedIn carousels and single-image posts via Canva MCP integration
  - Applies connected brand kit: colors, fonts, and layout templates automatically
  - Supports carousel (5-10 slides) and single image formats
  - Text content populated from approved post draft
  - Returns Canva design link for review and export
  - Requires CANVA_API_KEY and active Canva MCP server connection

**Distribution Layer — 4 Skills**

- `ls:content-calendar` (Tier 4) — Content schedule planner
  - Generates weekly and monthly content calendars
  - Pillar balancing: distributes content pillars evenly across posting days
  - Optimal time assignment: Tuesday/Wednesday/Thursday, 07:00-08:00 or 12:00-17:00 UTC
  - Minimum 20-hour gap enforcement between posts
  - Maximum 5 posts per week cap
  - Monthly view includes research session scheduling (weeks 1 and 3) and competitor check scheduling (week 1)
  - Calendar status view: shows each post's current status (DRAFT/APPROVED/SCHEDULED/PUBLISHED) and quality scores
  - Quality gate applied at calendar scheduling stage (same thresholds as batch-scheduler)

- `ls:idea-bank` (Tier 3) — Neon topic bank browser and manager
  - Browse top unwritten topics sorted by composite_score
  - Filter by content pillar, score threshold, or time range
  - Tag management: mark topics as this_week, next_week, archived, in_progress
  - Brand voice profile viewer and editor (update tone, avoid words, vocabulary preferences)
  - Archive topics that are no longer relevant without deleting them
  - Retrieval by tag, pillar, or keyword search
  - Returns topic with all stored metadata: hook suggestions, CTA suggestions, post ideas, source breakdown

- `ls:analytics-dashboard` (Tier 4) — Metricool analytics reporter
  - Pulls performance data via Metricool API for any date range
  - Weekly report: top 3 posts by engagement rate, average ER vs. 30-day baseline, best format/hook/pillar
  - Monthly report: adds frequency analysis, day/time optimization confirmation, pillar breakdown, 3 recommendations
  - Underperforming post analysis: flags posts below 1% engagement rate with diagnosis
  - Stores results in Neon `ls_analytics_cache` for trend comparison
  - Recommendation output can seed next ls:research-engine session (boost_pillar parameter)

- `ls:batch-scheduler` (Tier 4) — Quality-gated Metricool batch submitter
  - Validates batch against all 4 quality gates before any API call
  - Gate 1: post quality score >= 75/100
  - Gate 2: AI detection score <= 25/100
  - Gate 3: hook strength score >= 7/10
  - Gate 4: duplicate similarity <= 60% against last 90 days of published posts
  - Circuit breaker: pauses after 3 consecutive Metricool API failures, waits 60s, retries
  - Exponential backoff per request: 2s, 4s, 8s
  - Schedules with minimum 20-hour gap enforcement
  - Maximum 5 posts per week cap enforced at submission time
  - Returns Metricool post ID for each successfully scheduled post
  - Logs all submissions to Neon `ls_audit_log`

**Orchestration**

- `ls:content-pipeline` (Tier 6) — Master pipeline orchestrator
  - Chains the full workflow: research → write → humanize → structure review → visual prompt → schedule
  - Dispatches sub-tasks to individual skill agents in dependency order
  - Enforces quality gates between pipeline stages (blocks progression on failure, does not silently continue)
  - Handles partial pipeline runs (resume from any stage using stored draft IDs)
  - Aggregates final output: scheduled post IDs, quality scores, visual prompt files, calendar entries
  - Managed by `pipeline-coordinator` agent (claude-opus-4-6)

**Quality Gate Hooks**

- `PreToolUse` hook on `ls:batch-scheduler` and `ls:content-calendar`: blocking gate enforcing all 4 quality thresholds
- `PostToolUse` hook on `ls:content-writer`, `ls:humanizer`, `ls:repurposer`, `ls:canva-designer`, `ls:batch-scheduler`: non-blocking audit logging to Neon
- `Stop` hook: end-of-session validation — checks for unscheduled drafts, unresolved structure review failures, unsaved idea bank updates

**Database — 10 Tables**

- `ls_topic_bank` — Scored research topics with hook/CTA suggestions and source breakdown
- `ls_brand_voice` / `brand_voice_profile` — Brand tone, vocabulary, content pillars, visual style
- `ls_content_drafts` — Draft posts with status progression (DRAFT → APPROVED → SCHEDULED)
- `ls_published_posts` — Published post record with Metricool post ID and analytics snapshots
- `ls_competitor_snapshots` — Competitor profile data with posting frequency and topic clusters
- `ls_analytics_cache` — Metricool analytics cache for trend comparison
- `ls_audit_log` — Full audit trail for every skill invocation
- `creator_posts_cache` — Scraped LinkedIn creator posts with engagement and pattern data
- `content_queue` — Approved posts pending scheduling (shared by batch-scheduler and visual-prompter)

**Resilience**

- Full resilience tier throughout: circuit breakers per external service (Metricool, Neon, SerpAPI, Reddit API, Google Trends, Canva)
- Exponential backoff with jitter on all retry logic
- Graceful degradation: every skill continues with reduced functionality when a dependency fails
- All errors logged to stdout with `[skill-name][ERROR]` prefix for Coolify log capture
- No hard crashes on external service failure — always returns a useful partial result or actionable error message

**12 Slash Commands**

- `/ls:research` — Run research engine
- `/ls:write` — Write a post from topic bank or raw input
- `/ls:humanize` — Run 6-pass humanizer
- `/ls:review` — Run structure review and quality scoring
- `/ls:visual` — Generate AI image prompts
- `/ls:canva` — Create Canva design
- `/ls:calendar` — View or generate content calendar
- `/ls:schedule` — Batch-submit approved posts to Metricool
- `/ls:analyze` — Analyze a LinkedIn creator's post patterns
- `/ls:competitors` — Run competitor tracker
- `/ls:ideas` — Browse topic bank
- `/ls:pipeline` — Run full content pipeline end-to-end

**10 Integrations**

- Metricool (scheduling + analytics)
- Reddit Pushshift (historical search)
- Reddit PRAW (real-time retrieval)
- Google Trends / pytrends
- SerpAPI (LinkedIn scraping fallback)
- LinkedIn Playwright scraper
- Neon PostgreSQL (persistent storage)
- Canva MCP (design creation)
- OpenAI DALL-E 3 (image generation + embeddings)
- Google Imagen / Vertex AI (alternative image generation)
