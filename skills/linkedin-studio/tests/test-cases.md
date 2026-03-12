# LinkedIn Studio — Test Cases
**Plugin:** linkedin-studio v1.0.0
**Namespace:** ls
**Skills under test:** 15 (4 layers)
**Last updated:** 2026-03-02

---

## How to Read These Tests

Each test case exercises one or more skills and specifies exact inputs, expected step-by-step behavior,
final output shape, which quality gates fire, and what the system must do when something fails.

Gate threshold reference (from settings.json):
- `post_quality_min`: 75
- `ai_score_max`: 25
- `hook_score_min`: 7 (scale 1–10)
- `duplicate_similarity_max`: 60%
- Word count standard post: 150–300 words
- Word count carousel slide: 50–150 words
- Hashtags: 3–5

---

## TC-01: Full Pipeline (research → write → humanize → structure → schedule)

**Skill:** `ls:content-pipeline`
**Input:**
```
niche: "AI consulting"
keywords: ["RAG failures", "AI implementation", "enterprise AI", "LLM production"]
format: text_post
cta_style: medium
publish_date: next Wednesday 08:00 UTC
```

**Expected behavior:**
1. `ls:content-pipeline` spawns pipeline-coordinator agent (claude-opus-4-6).
2. Coordinator dispatches `ls:research-engine` with the keywords and niche. Google Trends, Reddit (`r/Entrepreneur`, `r/artificial`), and LinkedIn creator search all run in parallel.
3. Research engine returns ranked topic list. Top topic (e.g., `tp_001` — "Why RAG fails in production") is selected automatically based on highest composite_score.
4. Coordinator dispatches `ls:content-writer` with `topic_id: tp_001`, `format: text_post`, `cta_style: medium`.
5. content-writer fetches topic row from `ls_topic_bank` and brand voice from `ls_brand_voice`. Generates Hook A (question), Hook B (stat), Hook C (story) plus post body and 3 CTA options.
6. Output is returned as `STATUS: DRAFT — PENDING QUALITY REVIEW`.
7. Coordinator dispatches `ls:humanizer`. All 6 humanizer passes run. AI phrase list is scanned and replaced. Sentence rhythm variability is calculated (must reach 0.4 minimum).
8. Coordinator dispatches `ls:structure-reviewer`. Hook score computed (target >= 7/10). CTA presence confirmed. Word count checked (150–300). Hashtag count checked (3–5). Whitespace formatting verified.
9. PreToolUse hook (`pre-tool-use-quality-gate.sh`) fires before batch-scheduler is invoked. Checks: post_quality >= 75, ai_score <= 25, hook_score >= 7, duplicate_similarity <= 60%.
10. All gates pass. Coordinator dispatches `ls:batch-scheduler`. Post submitted to Metricool API with `scheduled_time: Wednesday 08:00 UTC`. Metricool ID returned and stored in `ls_content_drafts`.
11. PostToolUse hook (`post-tool-use-logger.sh`) fires after batch-scheduler. Logs event to `ls_audit_log`: skill=batch-scheduler, post_id, quality_scores, timestamp.
12. Stop hook (`stop-final-validation.sh`) fires at session end. Confirms no unscheduled drafts remain.

**Expected output:**
```
PIPELINE COMPLETE
Topic: "Why RAG fails in production" (tp_001, score: 0.91)
Post format: text_post
Hook selected: Hook B (stat)
Word count: 212
Hook score: 8/10
Quality score: 81/100
AI detection score: 18/100
Duplicate similarity: 12%
Metricool ID: mtc_0483
Scheduled: Wednesday 08:00 UTC
Audit log entry: ls_audit_log row inserted
```

**Gate checks:**
- `pre-tool-use-quality-gate.sh`: post_quality >= 75 (PASS), ai_score <= 25 (PASS), hook_score >= 7 (PASS), duplicate_similarity <= 60% (PASS)
- `post-tool-use-logger.sh`: non-blocking log to `ls_audit_log`
- `stop-final-validation.sh`: no unscheduled drafts remaining

**Failure scenario:** If structure-reviewer returns hook_score < 7 at step 8, the PreToolUse gate at step 9 fires but blocks scheduling. Pipeline-coordinator reports the specific failing metric and prompts user to either manually select a stronger hook variant or re-run content-writer with a different hook formula.

---

## TC-02: Humanizer Blocks AI Content Correctly

**Skill:** `ls:humanizer`
**Input:**
```
post_text: |
  In today's rapidly evolving landscape, it's important to note that leveraging AI solutions
  can be a game-changer for your business. Delve into the transformative potential of these
  cutting-edge tools. At the end of the day, the synergy between human expertise and AI
  capabilities is paramount. It goes without saying that robust implementation is crucial
  to achieving optimal outcomes in this dynamic environment.
```
This input contains 8 flagged AI phrases: "In today's rapidly evolving landscape", "it's important to note", "leveraging", "game-changer", "Delve into", "cutting-edge", "synergy", "it goes without saying".

**Expected behavior:**
1. humanizer receives post text. Pass 1 — AI phrase scan: detects all 8 phrases against internal blocklist. Each phrase is flagged with position and severity.
2. Pass 2 — Phrase replacement: each flagged phrase replaced with a human-authored equivalent drawn from niche vocabulary. Example: "leveraging" → "using", "game-changer" → removed or rephrased as concrete claim, "Delve into" → "Look at", "synergy" → rewritten as specific interaction.
3. Pass 3 — Sentence rhythm: sentence lengths varied to prevent uniform cadence (variability_min: 0.4). Consecutive same-length sentences broken up.
4. Pass 4 — Voice calibration: tone checked against brand_voice_profile (authoritative yet approachable, first person, direct). Abstract filler sentences removed.
5. Pass 5 — Reading level check: target grade 10–12. Flesch-Kincaid calculation run. If below 10 or above 12, sentence complexity adjusted.
6. Pass 6 — Final AI score: re-scan for residual AI phrases. If ai_score > 25, additional replacement pass fires before returning.
7. Final ai_score returned: <= 25.

**Expected output:**
```
HUMANIZER COMPLETE
Passes run: 6
Phrases replaced: 8
AI score before: 87/100
AI score after: 19/100
Sentence variability: 0.52
Reading level: Grade 11
Status: CLEARED — ai_score below threshold (19 <= 25)

[Revised post text with all AI phrases removed and natural voice applied]
```

**Gate checks:**
- Internal pass 6 re-scan: ai_score must be <= 25 before returning
- If ai_score still > 25 after pass 6: additional aggressive replacement pass fires (ai_phrase_replacement_aggressive: true in settings)
- PostToolUse hook logs humanizer event to `ls_audit_log`

**Failure scenario:** If ai_score cannot be reduced below 25 after all passes + aggressive mode, humanizer returns `STATUS: HUMANIZER FAILED` with residual phrase list. User must manually rewrite those specific lines. Skill does not return a falsely passing score.

---

## TC-03: Hook Strength Gate Blocks Weak Hook

**Skill:** `ls:structure-reviewer` → PreToolUse gate on `ls:batch-scheduler`
**Input:**
```
post_text: |
  Here's the thing about AI implementation. It can be challenging. Many companies struggle.
  There are several factors involved. This is something worth thinking about.

  Anyway, if you're in the space you probably know what I mean.

  Thoughts?

  #AI #consulting #business #tech #innovation
format: text_post
status: approved
```

**Expected behavior:**
1. `ls:structure-reviewer` receives post. Runs hook strength scoring. Evaluates: specificity of claim, curiosity gap created, pattern interrupt, word count of hook line (must be <= 15 words), absence of generic openers.
2. Hook line "Here's the thing about AI implementation." scores 3/10. Reason: generic opener ("Here's the thing"), no concrete claim, no curiosity gap, no number or story.
3. structure-reviewer returns full report: hook_score: 3/10 (FAIL), CTA detected: yes ("Thoughts?" — weak but present), word count: 68 words (FAIL — below 150 minimum for text_post), hashtag count: 5 (PASS), whitespace formatting: PASS.
4. Overall quality_score computed: 42/100 (FAIL — below 75 threshold).
5. User attempts to proceed to scheduling. PreToolUse hook (`pre-tool-use-quality-gate.sh`) fires.
6. Gate reads: hook_score 3 < 7 (FAIL), post_quality 42 < 75 (FAIL). Gate exits with code 1.
7. Batch-scheduler is blocked. Error output: `BLOCKED — hook_score 3/10 below minimum 7/10 and quality_score 42/100 below minimum 75/100`.

**Expected output:**
```
=== PRE-SCHEDULE VALIDATION FAILED ===

FAIL: hook_score 3/10 — minimum required: 7/10
FAIL: post_quality_score 42/100 — minimum required: 75/100
FAIL: word count 68 — minimum required: 150 for text_post

Recommended actions:
  1. Replace hook with a stat hook or story hook (see HOOK-FORMULAS.md)
  2. Expand post body to minimum 150 words with concrete insights
  3. Re-run ls:structure-reviewer after revisions

BLOCKED — post NOT submitted to Metricool
```

**Gate checks:**
- `pre-tool-use-quality-gate.sh`: hook_score_min 7 (FAIL at 3), post_quality_min 75 (FAIL at 42), word count check (FAIL at 68)
- Gate is blocking (exit code 1) — batch-scheduler tool call is never made

**Failure scenario:** N/A — this test case IS the failure scenario. Success means the gate correctly blocked the post and returned actionable fix instructions rather than a generic error.

---

## TC-04: Duplicate Detector Blocks Near-Duplicate Post

**Skill:** `ls:structure-reviewer` (duplicate check) → PreToolUse gate
**Input:**
```
post_text: |
  73% of enterprise AI projects fail before they reach production.

  I've seen it happen again and again with clients.

  The problem isn't the model. It's the data pipeline, the change management,
  and the unrealistic timelines set before anyone understood the actual scope.

  Fix those three things. The model handles itself.

  What's the biggest AI implementation challenge in your org right now?

  #AIImplementation #EnterpriseAI #MachineLearning #AIConsulting #TechLeadership
```
Context: Neon `ls_published_posts` already contains a post with 78% cosine similarity to this draft.

**Expected behavior:**
1. PreToolUse gate runs before batch-scheduler. Duplicate check query runs against `ls_published_posts` table: computes semantic similarity between incoming draft and all published posts in the past 90 days.
2. Similarity check finds existing post `post_id: pp_019` with similarity score 78%.
3. Gate threshold is 60% maximum. 78% > 60% — gate FAILS.
4. Scheduling blocked. Output identifies the conflicting post by ID and similarity score.
5. User presented with options: (a) archive draft and abandon, (b) significantly differentiate the angle and re-submit, (c) override with explicit confirmation (override adds `NEAR_DUPLICATE` flag to audit log).

**Expected output:**
```
=== PRE-SCHEDULE VALIDATION FAILED ===

FAIL: duplicate_similarity 78% exceeds threshold of 60%

Near-duplicate detected:
  Existing post: post_id pp_019 (published 2026-01-14)
  Similarity score: 78%
  Overlapping phrases: "73% of enterprise AI projects", "data pipeline", "change management"

Options:
  (a) Archive this draft
  (b) Revise to differentiate angle — rerun ls:structure-reviewer when ready
  (c) Override (adds NEAR_DUPLICATE flag to audit log) — type CONFIRM to proceed

BLOCKED — post NOT submitted to Metricool
```

**Gate checks:**
- `pre-tool-use-quality-gate.sh`: duplicate_similarity_max 60% (FAIL at 78%)
- Similarity computed via stored embedding in `ls_topic_bank` / `ls_published_posts`
- Override path audited in `ls_audit_log` with `event_type: NEAR_DUPLICATE_OVERRIDE`

**Failure scenario:** If embedding service is down during similarity check, the gate must log a warning (`[WARN] duplicate check skipped — embedding service unavailable`) and allow scheduling to proceed rather than falsely blocking. The draft is flagged `duplicate_check: skipped` in the audit log.

---

## TC-05: Research Engine with One Source Failing (Graceful Degradation)

**Skill:** `ls:research-engine`
**Input:**
```
niche: "AI consulting"
keywords: ["AI ROI", "implementation cost", "automation savings"]
content_pillars: ["thought leadership", "client transformation stories"]
time_range: last_30_days
max_topics: 20
```
Context: Google Trends (pytrends) returns HTTP 429 rate limit error on first attempt and on retry.

**Expected behavior:**
1. research-engine validates inputs (niche, keywords present — PASS).
2. Phase 2: dispatches all 3 sub-searches in parallel.
3. Source A (Google Trends): pytrends call returns 429. research-engine waits 60 seconds, retries once. Second attempt also returns 429. Source A is skipped. Logs: `[research-engine][ERROR] Google Trends rate limited — skipping, topics marked trend_unverified`.
4. Source B (Reddit via `ls:pain-point-miner`): executes normally. Returns 14 pain point entries from `r/Entrepreneur` and `r/consulting`.
5. Source C (LinkedIn creator via `ls:creator-analyzer`): executes normally. Returns 11 topics from Playwright scrape.
6. Phase 3: aggregate and score. Composite scoring runs with trend_score = 0 for all topics (Google Trends unavailable). Weighting adjusted: pain_intensity and creator_engagement carry full weight. Topics tagged `trend_unverified: true`.
7. Multi-source bonus applied where Reddit + LinkedIn both surfaced the same topic.
8. Phase 4: deduplication runs against `ls_topic_bank`.
9. Phase 5: results stored and ranked list returned. Report header explicitly states Google Trends was unavailable.

**Expected output:**
```
RESEARCH COMPLETE — 17 new topics discovered
WARNING: Google Trends unavailable (rate limited) — trend_score set to 0 for all topics
         Topics marked trend_unverified: true

RANK | TOPIC_ID | RAW TOPIC                              | SCORE | SOURCES | TOP HOOK
-----|----------|----------------------------------------|-------|---------|----------
1    | tp_031   | "Calculating AI ROI before project start" | 0.74 | 2/3 (Reddit+LI) | "Most AI ROI..."
2    | tp_032   | "Hidden costs of AI implementation"    | 0.68  | 1/3 (Reddit)   | "Your AI budget..."
...

STORAGE: 17 new, 0 skipped, 2 updated
SOURCES: Google Trends FAILED (429 rate limit), Reddit OK (14 results), LinkedIn OK (11 results)
NEXT: Pass topic_id list to ls:content-pipeline or ls:idea-bank
```

**Gate checks:**
- PreToolUse `validate_research_brief`: niche + keywords present (PASS)
- PostToolUse `log_topic_scores`: all 17 topics logged to `ls_audit_log`
- Stop `confirm_neon_write`: Neon write confirmation (PASS)

**Failure scenario:** If two sources fail (e.g., Reddit also times out): research-engine continues with LinkedIn results only and increases the warning severity to `[WARN] 2/3 sources unavailable — results may not reflect full audience interest`. If all three fail: abort with `[research-engine][ERROR] All research sources failed — cannot produce reliable topic list. Check API credentials and rate limits.`

---

## TC-06: Creator Analyzer with Playwright Failure (Falls Back to SerpAPI)

**Skill:** `ls:creator-analyzer`
**Input:**
```
creators: ["https://www.linkedin.com/in/justinwelsh/", "https://www.linkedin.com/in/lara-acosta-/"]
niche: "AI consulting"
```
Context: Playwright session hits LinkedIn login wall immediately for both profiles.

**Expected behavior:**
1. Phase 1: input validation. Both URLs normalized to standard format (PASS). Cache check runs against `ls_content_drafts` (actually `creator_posts_cache`) — no cache younger than 24 hours found.
2. Phase 2, Method 1 (Playwright): browser launches headless. Navigates to `justinwelsh/recent-activity/shares/`. Immediately encounters login redirect (HTTP 302 to linkedin.com/login). Block detected. Logs: `[creator-analyzer][ERROR] Playwright blocked — LinkedIn login wall for justinwelsh`. Falls to Method 2.
3. Method 2 (SerpAPI): constructs query `site:linkedin.com/posts "Justin Welsh"`. Sends request to SerpAPI with `SERPAPI_KEY`. Returns 18 organic results with post snippets. Reaction counts unavailable — engagement estimated from snippet length and keyword signals. `source: serpapi` flagged on all posts.
4. Repeats for Lara Acosta — same Playwright failure, same SerpAPI fallback.
5. Phase 3: engagement scoring run on SerpAPI results (estimated scores). 80th percentile threshold computed. Top performers retained (minimum floor: 3 posts per creator).
6. Phase 4: pattern extraction on top posts. Hook types classified. Structural patterns computed.
7. Phase 5: results written to Neon `creator_posts_cache`. `scrape_source: serpapi` recorded.
8. Phase 6: insight report returned. Report header notes Playwright was blocked and SerpAPI was used.

**Expected output:**
```
CREATOR ANALYSIS COMPLETE

CREATORS ANALYZED: 2
POSTS COLLECTED: 36 total (SerpAPI), 9 top performers (top 25% — SerpAPI floor applied)
SCRAPE METHODS: Playwright 0, SerpAPI 36, Manual 0
NOTE: Engagement scores are estimated (SerpAPI — no raw reaction counts)

TOP PERFORMING HOOK TYPES:
  1. stat_hook — 4 posts, avg engagement est. HIGH
  2. story_hook — 3 posts, avg engagement est. HIGH
  3. contrarian_hook — 2 posts, avg engagement est. MEDIUM

STRUCTURAL PATTERNS:
  Average post length: 187 words
  Optimal paragraph count: 7
  Dominant CTA format: comment_prompt
  Emoji strategy: minimal

TOP 3 HOOKS TO STEAL (adapted):
  1. "..." (from justinwelsh, est. HIGH engagement)
  ...

CACHE: 36 new posts stored, 0 updated, 0 skipped
NEXT: Pass patterns to ls:content-writer or ls:idea-bank
```

**Gate checks:**
- PreToolUse `validate_creator_inputs`: URLs normalized (PASS)
- PostToolUse `log_scrape_result`: scrape method (serpapi) and post count logged
- Stop `confirm_cache_write`: Neon cache write confirmed

**Failure scenario:** If SerpAPI quota is also exhausted (403/429), creator-analyzer falls to Method 3 (manual paste). Prints clear instructions for each creator URL with a paste prompt. Marks all manually collected posts `source: manual_paste` in cache.

---

## TC-07: Pain Point Miner on r/Entrepreneur with Trending Keywords

**Skill:** `ls:pain-point-miner`
**Input:**
```
keywords: ["AI tools", "automation", "ChatGPT for business"]
subreddits: ["r/Entrepreneur", "r/smallbusiness"]
time_range: last_30_days
min_upvotes: 50
```

**Expected behavior:**
1. PRAW client authenticates using `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` / `REDDIT_USERNAME` / `REDDIT_PASSWORD` from settings.json env block.
2. Pushshift API queried first for historical data (faster for bulk retrieval).
3. For each keyword × subreddit combination, fetches posts with at minimum 50 upvotes in the last 30 days. Limit: 100 posts per query (from research defaults in settings.json).
4. PRAW fetches live comment threads for top 20 posts to extract comment-level pain points (higher comment count = higher pain intensity weighting).
5. Pain points extracted from post titles, selftext, and top-level comments. Upvote-weighted emotional intensity score computed per pain point.
6. Pain points clustered by theme: "AI tool overwhelm", "ROI measurement", "team resistance to automation", "prompt engineering time cost", etc.
7. Deduplication within clusters: near-identical pain points merged.
8. Results returned sorted by cluster size × avg upvote weight.
9. Trending keyword detection: if a keyword appears in 5+ posts from the past 7 days with increasing frequency, it is tagged `trending: true`.

**Expected output:**
```
PAIN POINT MINING COMPLETE

SUBREDDITS: r/Entrepreneur, r/smallbusiness
KEYWORDS: AI tools, automation, ChatGPT for business
POSTS SCANNED: 200 | COMMENTS SCANNED: 1,840
PAIN POINTS EXTRACTED: 34 unique | CLUSTERS: 7

CLUSTER RANK | THEME                          | POSTS | AVG UPVOTES | TRENDING
-------------|--------------------------------|-------|-------------|----------
1            | AI tool overwhelm / choice paralysis | 18 | 312      | YES
2            | Measuring ROI on AI spend       | 14    | 267         | NO
3            | Employee resistance to automation | 11   | 198         | NO
...

TRENDING KEYWORDS (appearing 5+ times in last 7 days, increasing freq):
  - "AI tool overwhelm" (9 posts, +80% week-over-week)

NEXT: Pass clusters to ls:research-engine or ls:idea-bank
```

**Gate checks:**
- PreToolUse: keyword and subreddit list validation (at least 1 keyword required)
- PostToolUse: pain point clusters logged to `ls_audit_log`
- Reddit rate limit: PRAW honors 60 requests/minute limit; built-in sleep between batches

**Failure scenario:** If Pushshift returns no results (API deprecated or down), PRAW is used exclusively. If PRAW also fails (auth error), skill aborts with `[pain-point-miner][ERROR] Reddit access failed — check REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in settings.json` and returns empty result set to research-engine caller, which marks Reddit source as failed.

---

## TC-08: Competitor Tracker Identifies Content Gap

**Skill:** `ls:competitor-tracker`
**Input:**
```
competitor_profiles:
  - "https://www.linkedin.com/in/eric-partaker/"
  - "https://www.linkedin.com/in/mckinsey/"
niche: "AI consulting"
your_content_pillars: ["AI implementation lessons", "tool breakdowns", "client transformation stories"]
lookback_days: 7
```

**Expected behavior:**
1. competitor-tracker fetches or refreshes post data for each competitor profile. Checks `ls_competitor_snapshots` for data younger than `competitor_check_frequency_days` (7 days from settings). No fresh cache found — triggers fresh scrape via creator-analyzer.
2. For each competitor: extracts post topics, categorizes into content pillars, counts posts per pillar, computes engagement rates per pillar.
3. Gap analysis: cross-references competitor pillar distribution against `your_content_pillars`. Identifies pillars where competitor posts heavily but you have not posted in 14+ days.
4. Eric Partaker has 3 posts on "leadership decision frameworks" in the past 7 days — none of your pillars cover this angle. Tagged as `opportunity_gap`.
5. McKinsey has 0 posts on "AI tool breakdowns" — you post frequently here. Tagged as `differentiation_strength`.
6. Posting frequency comparison: competitor A posts 5x/week, competitor B posts 2x/week, your cadence is 3x/week.
7. Engagement rate comparison computed on per-post basis.
8. Content gap report generated. Gap opportunities passed to `ls:idea-bank` for storage.

**Expected output:**
```
COMPETITOR TRACKING COMPLETE — 2 profiles analyzed

COMPETITOR: Eric Partaker (7 posts analyzed)
  Top pillar: leadership decision frameworks (3 posts, avg 847 reactions)
  Your coverage: NONE — CONTENT GAP IDENTIFIED
  Posting frequency: 5x/week (you: 3x/week)

COMPETITOR: McKinsey (5 posts analyzed)
  Top pillar: AI strategy (2 posts, avg 2,341 reactions)
  Your coverage: partial (tool breakdowns — adjacent)
  Posting frequency: 2x/week (you: 3x/week)

CONTENT GAPS (topics competitors own that you don't):
  1. "Leadership decision frameworks for AI adoption" — HIGH opportunity (8 competitor posts, 847 avg reactions)
  2. "AI ROI measurement frameworks" — MEDIUM opportunity (4 competitor posts, 312 avg reactions)

DIFFERENTIATION STRENGTHS (topics you own that competitors don't):
  1. "AI tool breakdowns and tutorials" — no competitor coverage in last 7 days

NEXT: Add gaps to ls:idea-bank | Generate posts with ls:content-pipeline
```

**Gate checks:**
- competitor_check_frequency_days: 7 (cache checked before re-scraping)
- PostToolUse: snapshot written to `ls_competitor_snapshots`
- Content gaps added to `ls_topic_bank` with `source: competitor_gap` tag

**Failure scenario:** If a competitor profile is private (login required), competitor-tracker falls back to SerpAPI search for that profile and flags results as `data_quality: estimated`. If both profiles are inaccessible, the skill returns an empty gap report rather than a fabricated one, with clear error messages per profile.

---

## TC-09: Carousel Creation (content-writer + visual-prompter + canva-designer)

**Skill:** `ls:content-writer` → `ls:visual-prompter` → `ls:canva-designer`
**Input:**
```
raw_topic: "5 reasons your AI implementation is failing"
format: carousel_script
cta_style: direct
slides: 7
visual_platform: dalle3
design_type: carousel_slide
```

**Expected behavior:**
1. `ls:content-writer` receives input. Phase 1: validates format (carousel_script) and cta_style (direct). Phase 2: loads brand voice from `ls_brand_voice`. Phase 3: generates 3 hook variants. Phase 4: writes carousel_script.
   - Slide 1: hook only (stat or story hook, max 15 words)
   - Slides 2–6: one insight per slide, max 40 words each
   - Slide 7: CTA slide — direct CTA with trigger word + resource
2. Output: `STATUS: DRAFT` carousel_script with 7 labeled slides.
3. `ls:visual-prompter` receives carousel_script. Phase 1: extracts hook from slide 1, key points from slides 2–6, CTA from slide 7. Phase 2: format auto-confirmed as carousel_slide (7 slides). Phase 3: generates one JSON prompt per slide. `text_overlay` per slide: max 10 words. `negative_prompt` included on all 7. Phase 4: DALL-E 3 variations generated (platform: dalle3).
4. Output: formatted prompt block with 7 slide JSON objects + Midjourney variations.
5. `ls:canva-designer` receives carousel_script + visual prompts. Phase 2: queries `ls_brand_voice` for brand_colors and visual_style. Queries Canva MCP `list-brand-kits`. Phase 3: calls `generate-design` with 7-page design. Phase 4: verifies 7 pages via `get-design-pages`. Phase 5: calls `export-design` for all pages (PNG). Phase 6: updates `ls_content_drafts` with design_url and media_urls array. Status set to `visual`.

**Expected output:**
```
CAROUSEL CREATION COMPLETE (3-skill chain)

content-writer:
  Format: carousel_script, 7 slides
  Hook selected: Hook B (stat) — "73% of AI implementations never reach production."
  Status: DRAFT — pending humanizer + structure-reviewer

visual-prompter:
  Platform: dalle3
  Prompts generated: 7 JSON objects
  Midjourney variations: 7

canva-designer:
  Design type: carousel_slide (7 slides)
  Brand kit applied: [kit name]
  Editable design: https://canva.com/design/[id]/...
  Exported slides: 7 PNG URLs
  content_queue updated: status = 'visual'

Next required: ls:humanizer → ls:structure-reviewer → ls:batch-scheduler
```

**Gate checks:**
- content-writer: `text_overlay` per slide enforced <= 10 words by visual-prompter output checklist
- canva-designer: page count verified via `get-design-pages` before export
- canva-designer: export dimensions verified (1080x1080 per slide)
- PostToolUse hook fires after canva-designer: logs design_url to `ls_audit_log`

**Failure scenario:** If Canva MCP `generate-design` returns an error after 3 retries, canva-designer automatically falls back to `ls:visual-prompter` (already completed). User is notified: `CANVA UNAVAILABLE — visual prompts delivered instead. Submit prompts to DALL-E 3 manually or retry Canva after resolving MCP connection.`

---

## TC-10: Batch Scheduling 5 Posts to Metricool

**Skill:** `ls:batch-scheduler`
**Input:**
```
post_ids: ["draft_001", "draft_002", "draft_003", "draft_004", "draft_005"]
schedule:
  draft_001: Tuesday 07:00 UTC
  draft_002: Wednesday 08:00 UTC
  draft_003: Wednesday 12:00 UTC
  draft_004: Thursday 07:00 UTC
  draft_005: Thursday 17:00 UTC
```

**Expected behavior:**
1. batch-scheduler receives 5 post IDs. Fetches each draft from `ls_content_drafts`.
2. For each post, PreToolUse hook (`pre-tool-use-quality-gate.sh`) fires sequentially:
   - post_quality >= 75 check
   - ai_score <= 25 check
   - hook_score >= 7 check
   - duplicate_similarity <= 60% check
   - CTA present check
   - Status == 'approved' check
   - No existing Metricool ID check
3. All 5 posts pass all 7 checks.
4. Scheduling gap validation: confirms minimum 20-hour gap between consecutive posts (from settings.json scheduling defaults). Wednesday 08:00 and Wednesday 12:00 are 4 hours apart — FAIL.
5. batch-scheduler reports the scheduling conflict for draft_002 and draft_003. Proposes alternatives: move draft_003 to Thursday 08:00 or Friday 07:00 to respect the 20-hour minimum gap.
6. User confirms alternative schedule. draft_003 rescheduled to Thursday 08:00 UTC.
7. Confirmed schedule: Tue 07:00, Wed 08:00, Thu 08:00, Thu 17:00, Fri 07:00 — all gaps > 20 hours. Checks max_posts_per_week: 5 (exactly at limit — PASS).
8. Each post submitted to Metricool API (`POST /api/v2/planner/post`). Metricool IDs returned and stored back to `ls_content_drafts`.
9. PostToolUse hook fires after each successful scheduling: logs to `ls_audit_log`.

**Expected output:**
```
BATCH SCHEDULING REPORT

Posts submitted: 5/5
Scheduling conflicts detected and resolved: 1
  draft_003: moved from Wed 12:00 → Thu 08:00 (gap conflict with draft_002)

SCHEDULE:
  draft_001 → Tuesday 07:00 UTC    | Metricool ID: mtc_0491 | SCHEDULED
  draft_002 → Wednesday 08:00 UTC  | Metricool ID: mtc_0492 | SCHEDULED
  draft_003 → Thursday 08:00 UTC   | Metricool ID: mtc_0493 | SCHEDULED
  draft_004 → Thursday 17:00 UTC   | Metricool ID: mtc_0494 | SCHEDULED
  draft_005 → Friday 07:00 UTC     | Metricool ID: mtc_0495 | SCHEDULED

Posts this week: 5 (max: 5) — AT LIMIT
All posts status updated to 'scheduled' in ls_content_drafts
Audit log: 5 entries written to ls_audit_log
```

**Gate checks:**
- PreToolUse `pre-tool-use-quality-gate.sh`: fires for each of 5 posts before submission
- Gap validation: 20-hour minimum between consecutive posts enforced
- max_posts_per_week: 5 enforced (at limit — warning issued but not blocked)
- PostToolUse `post-tool-use-logger.sh`: 5 log entries to `ls_audit_log`

**Failure scenario:** If one post fails the quality gate (e.g., draft_004 has hook_score 5/10), that post is skipped and the other 4 are scheduled. Report clearly shows draft_004 as `BLOCKED — hook_score below threshold` with the specific score and recommended fix. The other 4 posts proceed without interruption.

---

## TC-11: Analytics Dashboard Generates Recommendations

**Skill:** `ls:analytics-dashboard`
**Input:**
```
time_range: last_30_days
include_recommendations: true
```

**Expected behavior:**
1. analytics-dashboard authenticates with Metricool API using `METRICOOL_API_KEY` and `METRICOOL_USER_ID`.
2. Fetches all posts published in last 30 days via Metricool API. Stores raw response in `ls_analytics_cache` for 6-hour TTL.
3. Computes per-post: reactions, comments, shares, engagement rate (reactions+comments+shares / impressions × 100).
4. Identifies top 3 posts by engagement rate. Extracts: hook type, post format, word count, day of week published, time published, content pillar.
5. Identifies bottom 3 posts by engagement rate. Same extraction.
6. Pattern comparison: top vs bottom. Surfaces: which hook types outperform, which publishing times correlate with higher engagement, which content pillars underperform.
7. Content pillar balance check: compares pillar distribution of published posts vs `your_content_pillars` in settings. Flags if any pillar has 0 posts in the period.
8. Posting cadence check: compares actual posts/week vs optimal (3x from scheduling defaults).
9. Generates actionable recommendations based on pattern comparison.

**Expected output:**
```
ANALYTICS DASHBOARD — Last 30 Days

OVERVIEW
  Posts published: 12
  Avg engagement rate: 3.8%
  Total reactions: 2,847
  Total comments: 412

TOP 3 POSTS:
  1. "73% of AI projects never ship — here's why" | stat_hook | Wed 08:00 | 8.2% ER
  2. "I turned a client's 18-month AI roadmap..." | story_hook | Tue 07:00 | 7.1% ER
  3. "5 AI tools I wish I'd known in year 1" | list_hook | Thu 17:00 | 6.4% ER

BOTTOM 3 POSTS:
  1. "Thoughts on AI regulation..." | question_hook | Mon 14:00 | 0.9% ER
  ...

RECOMMENDATIONS:
  1. stat_hook and story_hook posts outperform question_hook by 4x — increase usage
  2. Wednesday 07:00–09:00 UTC is your highest-engagement window — prioritize this slot
  3. "Industry trend analysis" pillar has 0 posts this month — content gap
  4. Average post word count for top performers: 218 words — target 200–250 range
  5. Monday posts underperform by 62% — avoid scheduling on Monday

Analytics cache: written to ls_analytics_cache (TTL: 6 hours)
```

**Gate checks:**
- Metricool API auth: valid API key + user ID required before any fetch
- Cache check: if `ls_analytics_cache` has data younger than 6 hours, return cached rather than re-fetching
- PostToolUse: dashboard event logged to `ls_audit_log`

**Failure scenario:** If Metricool API returns 401 (invalid credentials), analytics-dashboard aborts immediately with `[analytics-dashboard][ERROR] Metricool authentication failed — verify METRICOOL_API_KEY and METRICOOL_USER_ID in settings.json`. No cached data write occurs. No fabricated metrics returned.

---

## TC-12: Content Calendar Shows Pillar Imbalance Warning

**Skill:** `ls:content-calendar`
**Input:**
```
view: weekly
weeks_ahead: 4
```

**Expected behavior:**
1. content-calendar fetches all scheduled posts from `ls_content_drafts` where status = 'scheduled' and publish_date is within the next 4 weeks.
2. Also fetches published posts from last 2 weeks to understand recent history.
3. For each post: reads content_pillar tag.
4. Content pillar distribution computed across the 6-week window (2 past + 4 future).
5. Expected distribution compared against `content_pillars` in settings.json (5 pillars defined). Even distribution would be 20% each.
6. Detects imbalance: "AI implementation lessons" = 58% of scheduled posts. "Client transformation stories" = 4% (1 post in 6 weeks). Threshold: any pillar below 10% in 4-week window triggers a warning.
7. Publishing window check: verifies all scheduled posts fall on optimal days (Tue, Wed, Thu) and optimal times (07:00, 08:00, 12:00, 17:00 UTC). Flags any posts scheduled on suboptimal days.
8. Gap detection: identifies any week in the 4-week horizon with 0 scheduled posts (posting gap).
9. Returns calendar view + warnings.

**Expected output:**
```
CONTENT CALENDAR — Next 4 Weeks

WEEK 1 (Mar 3–9):
  Tue Mar 4 07:00 — "Why RAG fails..." (AI implementation) ✓
  Wed Mar 5 08:00 — "5 tools..." (tool breakdowns) ✓
  Thu Mar 6 17:00 — "Client story..." (client transformation) ✓

WEEK 2 (Mar 10–16):
  Tue Mar 11 07:00 — "AI ROI..." (thought leadership) ✓
  Thu Mar 13 08:00 — "Automation..." (AI implementation) ✓

WEEK 3 (Mar 17–23):
  [NO POSTS SCHEDULED] ← POSTING GAP WARNING

WEEK 4 (Mar 24–30):
  Wed Mar 26 08:00 — "Industry trends..." (trend analysis) ✓

PILLAR DISTRIBUTION WARNINGS:
  [!] "Client transformation stories" — 8% of schedule (minimum: 10%)
      Only 1 post in 6-week window. Add 2+ posts to this pillar.
  [!] "Consulting business insights" — 0% of schedule
      Zero posts planned. Schedule at least 1 post this pillar per month.

POSTING GAP WARNING:
  Week of Mar 17–23 has no scheduled posts. LinkedIn algorithm rewards consistency.
  Recommend scheduling 2–3 posts this week.

SCHEDULING QUALITY: 7/10 — resolve 3 warnings to reach optimal cadence
```

**Gate checks:**
- PreToolUse hook fires when content-calendar is invoked: validates that post_quality >= 75 for all posts being added to calendar
- Pillar balance threshold: any pillar < 10% in 4-week window triggers warning (not block)
- Posting gap threshold: any 7-day window with 0 posts triggers gap warning

**Failure scenario:** If `ls_content_drafts` returns no scheduled posts (empty queue), content-calendar returns an empty calendar with a prominent `QUEUE EMPTY — No posts scheduled for the next 4 weeks. Run ls:content-pipeline to generate content.` message rather than a blank or error state.

---

## TC-13: Brand Voice Profile Applied to Writing

**Skill:** `ls:content-writer` (brand voice enforcement)
**Input:**
```
raw_topic: "AI implementation consulting rates"
format: text_post
cta_style: soft
```
Context: `ls_brand_voice` table contains:
```
tone: "authoritative yet approachable"
avoid_words: ["leverage", "synergy", "game-changer", "delve", "it's important to note", "we", "our team"]
signature_phrases: ["in practice", "from the field", "here's what actually happens"]
typical_sentence_length: 12
persona: "practitioner with 10+ years shipping AI in enterprise"
```

**Expected behavior:**
1. content-writer Phase 2B: queries `ls_brand_voice` and loads full brand_context.
2. Phase 3: generates 3 hook variants. Each hook pre-screened against `avoid_words` before returning. Any hook containing a flagged word is regenerated.
3. Phase 4: post body written with the following brand_voice rules enforced:
   - First-person singular ("I", never "we" or "our team")
   - Sentences avg 12 words or fewer
   - At least 2 uses of `signature_phrases` naturally incorporated
   - Zero instances of `avoid_words`
4. Phase 5: CTA generated in soft style — invites reflection, zero friction.
5. Phase 6: output returned as DRAFT. Brand voice compliance check noted in draft header.

**Expected output:**
```
============================================================
DRAFT — PENDING QUALITY REVIEW
ls:humanizer and ls:structure-reviewer required before use
============================================================

FORMAT: text_post
TOPIC: AI implementation consulting rates
BRAND VOICE: practitioner with 10+ years shipping AI in enterprise
BRAND RULES APPLIED:
  - avoid_words: 0 instances detected
  - signature_phrases: 2 instances included
  - avg sentence length: 11.4 words
  - POV: first-person singular throughout

--- HOOK VARIANTS (select one for A/B test) ---

[HOOK A — Question]
What should you actually pay for AI implementation consulting?

[HOOK B — Stat]
Day rates for AI consulting range from $1,200 to $8,000.

[HOOK C — Story]
A client asked me last week if $4,500/day was reasonable.

--- POST BODY (uses Hook A by default) ---
[body text — no "we", no avoid_words, signature phrases present]

--- CTA OPTIONS ---
[CTA-1 — Soft]
What's been your experience negotiating AI consulting rates?
...
```

**Gate checks:**
- Phase 2B Neon query: if brand_voice_profile empty, warn and use default (tone: authoritative yet approachable, style: direct no fluff)
- avoid_words scan: runs before returning any draft
- PostToolUse `log_draft_created`: logs draft to `ls_audit_log` with brand_voice_applied: true

**Failure scenario:** If `ls_brand_voice` table is empty (no profile configured), content-writer logs `[WARN] brand_voice_profile not found — using plugin defaults from settings.json` and continues with the defaults defined in settings.json. Draft header notes `BRAND VOICE: default (no profile in Neon)` so user is aware.

---

## TC-14: Repurposer Transforms Blog Post to Carousel

**Skill:** `ls:repurposer`
**Input:**
```
url: "https://yasmineseidu.com/blog/rag-production-failures"
target_format: carousel_script
slides: 7
```

**Expected behavior:**
1. repurposer receives URL. Calls WebFetch on the URL. Extracts: page title, body text (stripping nav, ads, footer), all H2/H3 headings, statistics, and pull quotes.
2. Analyzes structure: blog post has 6 H2 sections, 3 statistics, 1 key framework, 1800 words.
3. Maps blog structure to carousel:
   - Slide 1: Strongest hook derived from the blog's opening claim or most striking statistic
   - Slides 2–6: One H2 section summary per slide (condensed to max 40 words each)
   - Slide 7: CTA derived from blog's conclusion + link to original post
4. Rewrites each slide in LinkedIn voice (conversational, first-person, no subheadings). Does not copy-paste from blog directly.
5. Returns carousel_script with 7 labeled slides, in the same DRAFT format as content-writer.
6. PostToolUse hook fires: logs repurpose event to `ls_audit_log` with `source_url`, `source_format: blog`, `target_format: carousel_script`.

**Expected output:**
```
============================================================
DRAFT — PENDING QUALITY REVIEW
ls:humanizer and ls:structure-reviewer required before use
============================================================

FORMAT: carousel_script (7 slides)
SOURCE: https://yasmineseidu.com/blog/rag-production-failures
SOURCE FORMAT: blog post
REPURPOSED TO: carousel_script

[SLIDE 1 — Hook]
73% of RAG implementations fail before they reach users.

[SLIDE 2]
The data pipeline is almost always the culprit.
Not the model. Not the prompts. The ingestion layer is broken.

[SLIDE 3]
Chunking strategy matters more than embedding model selection.
[...40 words max...]

...

[SLIDE 7 — CTA]
Full breakdown: [original blog URL]
DM me "RAG" and I'll send you my implementation checklist.

STATUS: DRAFT
NEXT REQUIRED: ls:humanizer → ls:structure-reviewer
```

**Gate checks:**
- WebFetch must return valid content (HTTP 200 + extractable body text)
- Each slide enforced to <= 40 words in carousel_script format
- PostToolUse: repurpose event logged
- Stop hook: confirms draft is in pending status (not yet approved)

**Failure scenario:** If WebFetch returns empty content or a 404/403, repurposer aborts with `[repurposer][ERROR] Could not fetch content from URL. Please paste the blog post content directly.` User can paste raw text which is then treated as `raw_topic` input. Skill does not fabricate content from the URL.

---

## TC-15: Pre-Schedule Validator Blocks Post Without CTA

**Skill:** `ls:structure-reviewer` → `pre-schedule-validator.sh`
**Input:**
```bash
POST_TEXT="Most AI projects fail because nobody defined what success looks like.

I've seen this happen across 30+ enterprise implementations.

The requirements doc exists. The model is trained. The infra is ready.

But nobody agreed on the KPIs before the project started.

That's the real problem. Not the technology.

#AI #Enterprise #Implementation #Consulting #Technology"
POST_STATUS="approved"
METRICOOL_ID=""
IS_CAROUSEL_SLIDE="false"
```

**Expected behavior:**
1. `pre-schedule-validator.sh` runs all 6 checks sequentially.
2. Check 1 (empty text): text is present — PASS.
3. Check 2 (word count): 52 words — FAIL. Minimum is 150 for standard post.
4. Check 3 (CTA): last non-hashtag line is "That's the real problem. Not the technology." — no question mark, no imperative verb starter. FAIL.
5. Check 4 (hashtags): 5 hashtags detected — PASS.
6. Check 5 (status): "approved" — PASS.
7. Check 6 (Metricool ID): empty string — PASS.
8. 2 checks failed. Script exits code 1. Output printed to stderr. `BLOCKED` printed to stdout.

**Expected output (stderr):**
```
[PASS] Post text is present.
[FAIL] Post is too short for a standard post: 52 words (minimum: 150). Add more substance to the content.
[FAIL] No CTA found. The last content line must end with a question (?) or start with an imperative verb (e.g., 'Share this if...', 'Comment below', 'Follow for more').
[PASS] Hashtag count acceptable: 5 hashtags found.
[PASS] Content status is 'approved'.
[PASS] No existing Metricool ID — post is not yet scheduled.

=== PRE-SCHEDULE VALIDATION FAILED ===

The following checks did not pass:
  FAIL: Post is too short for a standard post: 52 words (minimum: 150)
  FAIL: No CTA found. The last content line must end with a question (?) or start with an imperative verb

Fix the above issues and re-run validation before scheduling.
```

**Expected output (stdout):** `BLOCKED`

**Gate checks:**
- This test case directly exercises all 6 checks in `pre-schedule-validator.sh`
- Exit code 1 is returned — any caller (batch-scheduler, content-pipeline) that checks exit code will halt
- CTA detection regex: covers `?`, and imperative starters: `comment|share|follow|tag|click|read|join|drop|tell|let me know|save|repost|dm|connect|subscribe|visit|check out|try|start|grab`

**Failure scenario:** If the script is run with no environment variables set (all empty/default), it must handle gracefully: Check 1 fires and immediately exits code 1 with `BLOCKED — Post text is empty. Cannot schedule an empty post.` No further checks run on an empty post, preventing false passes on subsequent checks.
