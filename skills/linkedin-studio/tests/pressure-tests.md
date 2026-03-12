# LinkedIn Studio — Pressure Tests
**Plugin:** linkedin-studio v1.0.0
**Namespace:** ls
**Type:** Adversarial / failure-mode scenarios
**Last updated:** 2026-03-02

---

## What Pressure Tests Verify

Unlike standard test cases that verify happy-path behavior, pressure tests force the system into
failure states — simultaneous outages, policy bypass attempts, data corruption, and resource limits.
A skill passes a pressure test when it degrades gracefully, surfaces honest errors, and never
produces a silently incorrect output or a falsely passing quality gate.

Passing criteria for all pressure tests:
- No silent failures (every error must surface to user or log)
- No fabricated data (empty results over invented results)
- No falsely passing gates (a post that should be blocked must be blocked)
- Circuit breakers and fallback chains must activate at the documented trigger point
- Neon writes that fail must be retried 3x before giving up (documented in research-engine and creator-analyzer)

---

## PT-01: All External Services Down

**Scenario:** Google Trends (pytrends), Reddit (Pushshift + PRAW), the LinkedIn Playwright scraper,
and Metricool all fail simultaneously during a single `ls:content-pipeline` run.

**Trigger conditions:**
- pytrends: raises `ConnectionError` (no response from Google)
- Pushshift: returns HTTP 503
- PRAW: raises `prawcore.exceptions.ServerError` (Reddit 500)
- LinkedIn Playwright: raises `playwright._impl._errors.TimeoutError` on all profiles
- SerpAPI (creator-analyzer fallback 1): returns HTTP 403 (quota exceeded)
- Metricool API: returns HTTP 503 on every scheduling attempt

**What `ls:content-pipeline` must do:**

Step-by-step expected behavior:

1. `ls:research-engine` dispatches all 3 parallel sub-searches.

2. Source A (Google Trends): `ConnectionError` on first call. research-engine waits 60 seconds per documented retry policy (references/GOOGLE-TRENDS-PARAMS.md). Second attempt also fails. Source A logged as FAILED: `[research-engine][ERROR] Google Trends unavailable — skipping, trend_score = 0 for all topics`.

3. Source B (Reddit): Pushshift returns 503. research-engine falls back to PRAW. PRAW raises `ServerError`. Both Reddit APIs have failed. Source B logged: `[research-engine][ERROR] Reddit unavailable (Pushshift 503 + PRAW ServerError) — skipping, pain_intensity weighting removed`.

4. Source C (LinkedIn creator via `ls:creator-analyzer`): Playwright TimeoutError on all profiles. creator-analyzer falls to SerpAPI. SerpAPI 403 (quota). creator-analyzer falls to Method 3 (manual paste). However — this is a pipeline run (non-interactive). Manual paste is not available in pipeline context. creator-analyzer returns empty result with flag `requires_manual_input: true`. Source C logged: `[research-engine][ERROR] LinkedIn creator data unavailable — all fallbacks exhausted in pipeline context`.

5. research-engine evaluates degradation state: all 3 sources failed. Per the graceful degradation table in research-engine SKILL.md: abort with actionable error message. research-engine does NOT attempt to invent topics or return cached stale data from `ls_topic_bank` as if it were fresh research.

6. `ls:content-pipeline` receives the abort signal from research-engine. Pipeline halts at the research stage. Downstream skills (content-writer, humanizer, structure-reviewer, batch-scheduler) are NOT invoked.

7. Metricool failure is never reached because the pipeline aborts before the scheduling stage.

**Required output:**
```
CONTENT PIPELINE — HALTED AT RESEARCH STAGE

[research-engine][ERROR] Google Trends unavailable — ConnectionError after 2 attempts
[research-engine][ERROR] Reddit unavailable — Pushshift 503 + PRAW ServerError
[research-engine][ERROR] LinkedIn creator data unavailable — Playwright timeout, SerpAPI 403, manual paste not available in pipeline context

RESULT: All 3 research sources failed. Cannot produce a reliable topic list.

PIPELINE STATUS: HALTED — 0 posts produced
SCHEDULED: none

Recovery actions:
  1. Check Google Trends API connectivity and pytrends configuration
  2. Check Reddit API credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET) in settings.json
  3. Check SERPAPI_KEY quota at serpapi.com/manage
  4. Retry pipeline once external services recover
  5. Alternative: run ls:idea-bank to browse existing topics already in Neon topic_bank

Metricool was not contacted — pipeline did not reach scheduling stage.
```

**What must NOT happen:**
- Pipeline must not return a success status with 0 posts and no error explanation
- Pipeline must not fabricate research topics from internal knowledge
- Pipeline must not silently skip the scheduling stage without explaining why
- batch-scheduler must not be invoked with empty or null post IDs

**Pass/fail criteria:**
PASS if pipeline halts at research stage, all 3 source failures are individually logged with their error type, and actionable recovery steps are returned.
FAIL if any downstream skill is invoked after research-engine aborts, or if any fabricated topic appears in the output.

---

## PT-02: AI Detector Bypass Attempt

**Scenario:** A post is submitted to `ls:humanizer` that contains subtle AI patterns — not the
obvious blocklist phrases, but structural signatures that AI detectors flag: uniform sentence
length, hedging language, passive voice clustering, and excessive transitional phrases. The
text superficially reads as human but scores > 25 on an AI detection model.

**Input post (crafted to evade naive phrase-level detection):**
```
There are several considerations to keep in mind when approaching enterprise AI deployment.
First, it is essential to evaluate the existing infrastructure. Second, one should assess
the readiness of the team. Third, the timeline needs to be realistic. Additionally, proper
stakeholder alignment must be established. Furthermore, risk mitigation strategies should
be developed. In conclusion, a comprehensive approach will yield the best results.
```

This text contains:
- 0 words from the explicit `avoid_words` blocklist in settings.json
- Uniform sentence length: all sentences 9–12 words (variability < 0.4)
- Passive voice: "must be established", "should be developed", "needs to be realistic"
- Hedging: "it is essential", "one should"
- Transitional phrase stacking: "First... Second... Third... Additionally... Furthermore... In conclusion"
- Third-person impersonal POV ("one should", "the team")

**Expected behavior:**

1. Pass 1 (AI phrase scan against blocklist): 0 flagged phrases. Naive check would pass here. Humanizer must not stop after pass 1.

2. Pass 2 (phrase replacement): minimal replacement triggered since blocklist is clear.

3. Pass 3 (sentence rhythm / variability): calculates sentence length variability. Variance is 2.1 words (very low). `sentence_variability_min` is 0.4. FAIL — variability below threshold. Rewrite triggered: some short sentences extended with concrete detail, some long sentences split. Variability recalculated — must reach >= 0.4 before pass 3 is complete.

4. Pass 4 (voice calibration): passive voice detector scans for "be + past participle" constructions. Finds 3 instances. Rewrites to active voice: "you need to establish stakeholder alignment", "build a risk mitigation strategy". Third-person impersonal ("one should") rewritten to first-person or direct address.

5. Pass 5 (reading level): Flesch-Kincaid check. If the rewritten text is now below grade 10 (too simplified), complexity is restored through concrete specificity rather than passive hedging.

6. Pass 6 (final AI score): re-scan using full detection model (not just phrase list). Structural signatures re-evaluated. If score is still > 25 after standard 6 passes, the `ai_phrase_replacement_aggressive: true` flag in settings.json triggers an additional aggressive pass focused on sentence restructuring and voice shift.

7. Final ai_score must be <= 25 before humanizer returns.

**Required output (if score brought below threshold):**
```
HUMANIZER COMPLETE
Passes run: 6 (+ 1 aggressive pass triggered)
Phrases replaced (blocklist): 0
Structural rewrites: 9
  - Sentence rhythm corrections: 4
  - Passive voice → active: 3
  - Transitional phrase breaks: 2
AI score before: 71/100
AI score after: 22/100
Sentence variability before: 0.18 (FAIL)
Sentence variability after: 0.47 (PASS)
Reading level: Grade 11
Status: CLEARED — ai_score 22 <= 25
```

**Required output (if aggressive pass still cannot bring score below threshold):**
```
HUMANIZER — MAXIMUM PASSES REACHED
Passes run: 6 + 1 aggressive
AI score after aggressive pass: 31/100 (above threshold of 25)

Residual patterns still detected:
  Line 3: "a comprehensive approach will yield the best results" — vague outcome claim
  Line 1: sentence still reads as enumerated list (structural signature)

ACTION REQUIRED: Manual rewrite needed for lines 3 and 1.
Post NOT cleared for scheduling.
STATUS: HUMANIZER FAILED — manual intervention required
```

**What must NOT happen:**
- Humanizer must not return `ai_score: 19` after only running the phrase blocklist scan
- Humanizer must not skip structural analysis (variability, passive voice) when phrase scan returns 0 hits
- Humanizer must not declare CLEARED if ai_score > 25 under any circumstances
- The pre-tool-use quality gate must independently re-check ai_score <= 25 before scheduling even if humanizer claims CLEARED

**Pass/fail criteria:**
PASS if humanizer catches the structural AI patterns (not just phrase matches), runs all 6+ passes, and either clears the post with a score <= 25 or explicitly fails with a per-line residual pattern report.
FAIL if humanizer returns CLEARED based solely on the phrase blocklist returning 0 hits.

---

## PT-03: Neon DB Connection Failure During Batch Scheduling

**Scenario:** `ls:batch-scheduler` is mid-way through a 5-post batch when the Neon PostgreSQL
connection drops. Posts 1 and 2 have been submitted to Metricool and their Metricool IDs
need to be stored back to `ls_content_drafts`. Posts 3, 4, 5 are not yet submitted.

**Trigger conditions:**
- Posts 1 and 2: Metricool API calls succeeded. Metricool IDs returned: mtc_0491, mtc_0492.
- During the `UPDATE ls_content_drafts SET metricool_id = ...` write for post 2: Neon returns `FATAL: remaining connection slots are reserved for non-replication superuser connections`.
- All subsequent Neon connections fail for the remainder of the session.

**Expected behavior:**

1. batch-scheduler detects Neon write failure for post 2. Attempts retry 1 (2s delay): fails. Retry 2 (4s): fails. Retry 3 (8s): fails. After 3 retries, logs: `[batch-scheduler][ERROR] Neon write failed for draft_002 after 3 retries — Metricool ID mtc_0492 NOT persisted to database`.

2. Because Neon is down, batch-scheduler cannot validate the quality gate data for posts 3, 4, 5 from `ls_content_drafts` (quality scores stored in Neon). Without verified quality data, the PreToolUse gate cannot run.

3. batch-scheduler halts processing for posts 3, 4, 5. Does NOT proceed to submit them to Metricool without passing the quality gate. Reason: the PreToolUse hook requires Neon-stored quality scores to run checks.

4. Batch-scheduler compiles a reconciliation report covering:
   - Posts successfully scheduled AND stored in Neon: post 1 (COMPLETE)
   - Posts successfully scheduled but NOT stored in Neon: post 2 (PARTIAL — at risk)
   - Posts not yet submitted to Metricool: posts 3, 4, 5 (PENDING)

5. The reconciliation report includes exact Metricool IDs for partial entries so the user can manually verify in the Metricool dashboard and recover.

6. Stop hook (`stop-final-validation.sh`) fires at session end. Detects unresolved state (posts 3–5 not scheduled, post 2 not stored). Generates warning in output.

**Required output:**
```
BATCH SCHEDULER — PARTIAL COMPLETION (Neon DB failure)

[batch-scheduler][ERROR] Neon connection lost after post 2 — writing to database failed after 3 retries

RESULTS:
  draft_001 → Metricool mtc_0491 | Neon persisted: YES | Status: COMPLETE
  draft_002 → Metricool mtc_0492 | Neon persisted: NO  | Status: PARTIAL (at risk)
  draft_003 → Metricool: NOT SUBMITTED | Status: PENDING
  draft_004 → Metricool: NOT SUBMITTED | Status: PENDING
  draft_005 → Metricool: NOT SUBMITTED | Status: PENDING

POSTS FULLY SCHEDULED: 1/5
POSTS PARTIALLY SCHEDULED (Metricool only, no DB record): 1/5
POSTS NOT SUBMITTED: 3/5

RECOVERY ACTIONS:
  1. Verify mtc_0492 exists in Metricool dashboard for draft_002
  2. Once Neon recovers, manually run:
     UPDATE ls_content_drafts SET metricool_id = 'mtc_0492', status = 'scheduled' WHERE id = 'draft_002';
  3. Re-run ls:batch-scheduler for draft_003, draft_004, draft_005 once Neon is restored
  4. Check Neon connection: NEON_DATABASE_URL in settings.json

Stop hook: 4 unresolved issues flagged — 1 partial record, 3 unscheduled posts
```

**What must NOT happen:**
- batch-scheduler must not proceed to submit posts 3, 4, 5 to Metricool without the quality gate running
- batch-scheduler must not silently discard the Metricool ID for post 2 (mtc_0492) — it must surface it in the output even if it cannot be stored
- batch-scheduler must not mark post 2 as FAILED just because the DB write failed — Metricool received it and it IS scheduled, which must be reflected accurately
- batch-scheduler must not retry indefinitely — the 3-retry exponential backoff cap is enforced

**Pass/fail criteria:**
PASS if partial state is accurately reported with exact Metricool IDs, unsubmitted posts are correctly held back, and recovery instructions are actionable.
FAIL if the Metricool ID for post 2 is lost, or if posts 3–5 are submitted to Metricool without quality gate validation.

---

## PT-04: Rate Limit Hit on Metricool Mid-Batch

**Scenario:** `ls:batch-scheduler` is scheduling a batch of 20 posts. Posts 1–12 are submitted
successfully. On post 13, the Metricool API returns HTTP 429 (Too Many Requests) with a
`Retry-After: 3600` header — a 1-hour backoff.

**Trigger conditions:**
- Posts 1–12: Metricool returns HTTP 200 with Metricool IDs.
- Post 13: Metricool returns HTTP 429 with `Retry-After: 3600`.
- Posts 14–20: not yet attempted.

**Expected behavior:**

1. batch-scheduler receives HTTP 429 for post 13. Reads `Retry-After: 3600` header. Understands that retrying immediately or in short intervals will not work — a 1-hour wait is required.

2. Circuit breaker activates. Per the plugin.json hooks config and the PreToolUse gate on `ls:batch-scheduler`: the circuit breaker state is set to OPEN for the Metricool integration. No further API calls to Metricool are made for posts 14–20.

3. batch-scheduler does NOT wait 3600 seconds in-session (this would block the user for 1 hour). Instead, it suspends the batch and persists state to Neon: stores `pending_posts: [draft_013, ..., draft_020]` in `ls_content_drafts` with `status: rate_limited` and `retry_after: [timestamp + 3600s]`.

4. User is notified of the situation, the circuit breaker state, the number of posts successfully scheduled, and the exact time at which the batch can be resumed.

5. PostToolUse hook logs the rate limit event to `ls_audit_log`: `event_type: RATE_LIMIT_HIT`, `integration: metricool`, `posts_scheduled: 12`, `posts_pending: 8`, `retry_after: [timestamp]`.

6. Stop hook fires: confirms 8 unscheduled posts remain in `status: rate_limited`. Reminds user to resume the batch.

**Required output:**
```
BATCH SCHEDULER — RATE LIMITED (Metricool API)

Posts scheduled before limit: 12/20
  draft_001 through draft_012 → Metricool IDs: mtc_0501–mtc_0512 | SCHEDULED

Rate limit hit on: draft_013
  Metricool response: HTTP 429 — Too Many Requests
  Retry-After: 3600 seconds (approx. 1 hour)

CIRCUIT BREAKER: OPEN — Metricool integration suspended
  No further Metricool API calls will be made this session.

Posts paused (8 remaining):
  draft_013 through draft_020 → status: rate_limited in ls_content_drafts

RESUME INSTRUCTIONS:
  Wait until: [current_time + 1 hour] UTC
  Then run: ls:batch-scheduler with the same post list — already-scheduled posts will be skipped (Metricool ID present)

Stop hook: 8 posts in rate_limited state — resume required
Audit log: RATE_LIMIT_HIT event written to ls_audit_log
```

**What must NOT happen:**
- batch-scheduler must not retry post 13 immediately or in a short loop
- batch-scheduler must not wait 3600 seconds in-session (blocking the user)
- batch-scheduler must not mark posts 14–20 as FAILED — they were never attempted and are still valid
- batch-scheduler must not lose track of which posts were already successfully scheduled (posts 1–12 must not be re-submitted on retry)
- Circuit breaker must remain OPEN for the full `Retry-After` duration — any retry before that window must be blocked with `CIRCUIT BREAKER OPEN — retry available at [timestamp]`

**Pass/fail criteria:**
PASS if circuit breaker activates, state is correctly persisted to Neon for the 8 remaining posts, user is given the exact retry time, and already-scheduled posts are protected from re-submission.
FAIL if batch-scheduler attempts to call Metricool again on the same session after receiving 429, or if any of the 8 paused posts are marked FAILED rather than rate_limited.

---

## PT-05: Empty Research Results — All 3 Sources Return Nothing

**Scenario:** `ls:research-engine` is called with very narrow keywords that return zero results
from all 3 sources. Not a connectivity failure — the APIs respond successfully but return
empty result sets.

**Trigger conditions:**
- Google Trends: API call succeeds (HTTP 200) but `interest_over_time()` returns an empty DataFrame for all keywords.
- Reddit: Pushshift and PRAW both respond (HTTP 200) but zero posts found with >= 50 upvotes matching the keywords in the last 30 days.
- LinkedIn creator: creator-analyzer runs Playwright successfully but finds 0 posts containing the keywords across all scraped profiles.

**Input:**
```
niche: "AI consulting"
keywords: ["quantum-AI-blockchain-metaverse-synergy-framework"]
content_pillars: ["thought leadership"]
time_range: last_30_days
max_topics: 25
```

**Expected behavior:**

1. research-engine dispatches all 3 parallel sub-searches. All complete without errors.

2. Source A (Google Trends): DataFrame is empty. No rising queries, no related topics. research-engine records: `google_trends_results: 0`.

3. Source B (Reddit): 0 posts returned from Pushshift. 0 posts from PRAW. `reddit_results: 0`.

4. Source C (LinkedIn): creator-analyzer returns empty topic list. `linkedin_results: 0`.

5. Phase 3 (aggregate and score): aggregate list is empty. 0 topics to score.

6. Phase 4 (deduplication): skipped — nothing to deduplicate.

7. Phase 5 (store and return): 0 topics to write to Neon. Write is skipped (no INSERT executed).

8. research-engine returns an honest empty result — does NOT fabricate topics, does NOT pull stale topics from `ls_topic_bank` and present them as fresh research, does NOT return a generic AI consulting topic list from its training knowledge.

9. Output explicitly tells the user that no results were found for this keyword and suggests actionable next steps: broaden keywords, check different subreddits, or browse existing `ls_topic_bank`.

**Required output:**
```
RESEARCH COMPLETE — 0 new topics discovered

WARNING: All 3 research sources returned empty results for keywords:
  "quantum-AI-blockchain-metaverse-synergy-framework"

SOURCE RESULTS:
  Google Trends: 0 results (keyword too narrow or no search interest in last 30 days)
  Reddit: 0 results (no posts >= 50 upvotes in r/Entrepreneur, r/smallbusiness, r/consulting, r/startups, r/freelance, r/marketing, r/artificial)
  LinkedIn Creators: 0 results (no matching posts in scraped profiles)

No topics written to Neon topic_bank.

SUGGESTED RECOVERY:
  1. Broaden keywords — try: ["AI tools", "automation", "ChatGPT for business"]
  2. Lower min_upvotes threshold — try: min_upvotes: 10
  3. Extend time_range — try: last_90_days
  4. Browse existing topics: run ls:idea-bank to retrieve previously stored topics
  5. Try different subreddits — add r/MachineLearning, r/technology
```

**What must NOT happen:**
- research-engine must not pull topics from `ls_topic_bank` that are 60+ days old and present them as fresh research results
- research-engine must not generate AI consulting topics from model knowledge and label them as research
- research-engine must not claim a non-zero topic count when 0 topics were actually discovered
- PostToolUse `log_topic_scores` hook must log 0 topics (not skip the hook entirely)
- Stop hook `confirm_neon_write` must confirm that 0 writes occurred (not error because nothing was written)

**Pass/fail criteria:**
PASS if research-engine returns an honest 0-topic result, all 3 source failure states are explained separately, and no fabricated or stale data appears in the output.
FAIL if research-engine returns any topics not found in the live research run, or if it pulls from `ls_topic_bank` without explicitly labeling those results as coming from the existing bank (not from new research).

---

## PT-06: Brand Voice Conflict — "No Emojis" vs Emojis in Generated Content

**Scenario:** The user's brand voice profile explicitly disallows emojis (`avoid_emojis: true`).
`ls:content-writer` generates a post containing 4 emojis. The post passes through `ls:humanizer`
without the emojis being flagged. The brand voice conflict must be caught before the post can
be scheduled.

**Setup conditions:**
- `ls_brand_voice` in Neon contains: `avoid_emojis: true`, `vocabulary_preferences: "no symbols, plain text only"`
- content-writer generates a post (possibly because it defaulted to brand preferences without checking `avoid_emojis` — a bug scenario) containing: `🔥`, `✅`, `💡`, `👇`
- humanizer runs all 6 passes. No AI phrase issues. Does not check for emojis (not in its scope — humanizer handles AI pattern removal, not brand voice compliance).
- Post proceeds to `ls:structure-reviewer`.

**Expected behavior:**

1. `ls:structure-reviewer` runs its standard checks. As part of brand voice compliance check: reads `ls_brand_voice` and finds `avoid_emojis: true`.

2. structure-reviewer scans post text for Unicode emoji characters. Finds 4 emojis at specific positions.

3. Brand voice violation flagged: `BRAND VOICE CONFLICT — avoid_emojis: true but 4 emojis found in post body`.

4. structure-reviewer does not simply silently strip the emojis. It flags the violation and blocks the post from advancing to approved status until the conflict is resolved — either by removing the emojis or by the user explicitly overriding the brand voice rule for this post.

5. Quality score penalty applied: brand voice compliance is a scored dimension. 4 emoji violations reduce the quality_score by a calculated amount (e.g., 8 points per violation = -32 points from brand compliance sub-score).

6. If the resulting quality_score drops below 75, the PreToolUse gate will block scheduling independently.

7. structure-reviewer returns full report with brand voice violations clearly itemized.

8. content-writer is flagged in the audit log for generating an emoji-containing post against a no-emoji brand profile — this represents a content-writer bug that should trigger a PostToolUse log entry for diagnosis.

**Required output from structure-reviewer:**
```
STRUCTURE REVIEW COMPLETE

Hook score: 8/10 — PASS
CTA detected: YES — PASS
Word count: 198 words — PASS
Hashtag count: 4 — PASS
Whitespace formatting: PASS

BRAND VOICE COMPLIANCE: FAIL

  BRAND VOICE CONFLICT: avoid_emojis: true
  Emojis found in post body: 4
    Position 1: "🔥" — line 2
    Position 2: "✅" — line 5
    Position 3: "💡" — line 8
    Position 4: "👇" — line 11

  Required action: Remove all 4 emojis from post body.
  Override option: Add brand_voice_override: allow_emojis to this specific post record in Neon.

Quality score: 47/100 (brand compliance penalty: -32 points, 4 violations × 8 pts)
Status: BLOCKED — quality_score 47 < 75 and brand voice violation unresolved

NOTE: content-writer generated this post with emojis despite avoid_emojis: true in brand_voice_profile.
      This has been logged to ls_audit_log (event_type: BRAND_VOICE_VIOLATION, skill: content-writer).
```

**PreToolUse gate behavior (if user attempts to schedule without resolving):**
```
=== PRE-SCHEDULE VALIDATION FAILED ===

FAIL: post_quality_score 47/100 — minimum required: 75/100
FAIL: brand_voice_violation — avoid_emojis: true, 4 emojis present

BLOCKED — post NOT submitted to Metricool
```

**What must NOT happen:**
- structure-reviewer must not strip emojis silently without reporting the violation
- humanizer must not be blamed for the emoji issue — humanizer's scope is AI phrase removal, not brand voice compliance. The bug is in content-writer.
- The post must not be marked approved while emojis remain in the body
- The pre-schedule gate must not be the first place the emoji conflict is caught — structure-reviewer must catch it first. The gate is a last-resort backstop, not the primary compliance layer.
- quality_score must not be reported as > 75 while a brand voice violation is active

**Pass/fail criteria:**
PASS if structure-reviewer catches the emoji conflict before the PreToolUse gate, the quality_score correctly reflects the penalty, the post is blocked, and the content-writer violation is logged to the audit table for diagnosis.
FAIL if the emojis are silently stripped without user notification, or if the post reaches the PreToolUse gate without structure-reviewer having flagged the brand voice violation first.
