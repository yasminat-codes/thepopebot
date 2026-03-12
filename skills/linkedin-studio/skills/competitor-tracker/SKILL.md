---
name: ls:competitor-tracker
description: >
  PROACTIVELY monitors competitor LinkedIn profiles over time to surface winning
  content patterns, exploitable content gaps, and strategic positioning opportunities
  for AI consulting creators. Triggers on competitor benchmarking requests, content
  strategy audits, market positioning tasks, gap analysis sessions, and scheduled
  weekly intelligence refreshes. Tracks engagement rate trends across 30-day windows,
  compares against stored historical baselines in Neon competitor_tracker, and
  generates strategic reports identifying what is working for competitors and where
  their blind spots create first-mover content opportunities.
model: sonnet
context: fork
allowed-tools: Bash Read Write WebFetch WebSearch
hooks:
  PreToolUse:
    - validate_competitor_urls
  PostToolUse:
    - log_tracker_run
  Stop:
    - confirm_neon_write
metadata:
  version: "2.0.0"
---

# ls:competitor-tracker

Monitors competitor LinkedIn profiles, extracts their best-performing content patterns,
and identifies strategic gaps. Stores historical data in Neon `competitor_tracker`
and generates actionable intelligence reports.

→ See references/SCRAPING-STRATEGY.md for the 3-fallback scraping chain
→ See references/NEON-SCHEMA.md for competitor_tracker table structure
→ See references/GAP-ANALYSIS.md for content gap identification methodology

---

## Phase 1: Input Competitor Profile URLs

**Accepted inputs:**
- Direct LinkedIn profile URLs: `https://www.linkedin.com/in/username/`
- List of up to 15 competitor URLs (comma-separated or one per line)
- Named competitor list stored in Neon (pass `list_name` to load saved set)

**Validation:**
- At least 1 URL required
- Normalize all URLs to `https://www.linkedin.com/in/{slug}/` format
- Reject company page URLs (this tracker is for individual creators only)
- Flag but do not block URLs already tracked within the last 6 hours (offer cached report)

**Load historical baseline:**
```sql
SELECT competitor_url, baseline_engagement_rate, baseline_post_freq,
       last_scraped_at, total_posts_tracked
FROM competitor_tracker
WHERE competitor_url = ANY($1)
ORDER BY last_scraped_at DESC;
```

If no baseline exists for a competitor, this run establishes it. New competitors
are flagged as `first_run: true` in the report.

---

## Phase 2: Scrape Recent Posts (30-Day Window, 3-Fallback Chain)

Apply the same 3-fallback chain used by `ls:creator-analyzer`. Attempt in order:

### Method 1 — Playwright (Primary)
```python
from playwright.async_api import async_playwright

async def scrape_competitor_posts(profile_url: str) -> list[dict]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)..."
        )
        activity_url = f"{profile_url}recent-activity/shares/"
        await page.goto(activity_url, wait_until='networkidle', timeout=20000)
        await page.wait_for_selector('[data-urn*="share"]', timeout=10000)
        posts = await page.query_selector_all('[data-urn*="share"]')
        raw = [await extract_post_data(p) for p in posts]
        # Filter to 30-day window
        cutoff = datetime.utcnow() - timedelta(days=30)
        return [p for p in raw if p['post_date'] >= cutoff]
```
- Extract: post text, reactions, comments, shares, post URL, post date
- Rate limiting: 3-second delay between profiles, max 3 concurrent sessions
- On block/CAPTCHA: immediately fall to Method 2

### Method 2 — SerpAPI LinkedIn Search (Fallback 1)
```python
def scrape_with_serpapi(competitor_name: str, api_key: str) -> list[dict]:
    params = {
        "engine": "google",
        "q": f'site:linkedin.com/posts "{competitor_name}" after:{thirty_days_ago}',
        "api_key": api_key,
        "num": 20
    }
    resp = requests.get("https://serpapi.com/search", params=params)
    return [parse_serpapi_linkedin_result(r) for r in resp.json().get("organic_results", [])]
```
- SerpAPI provides limited metadata; engagement estimated from snippet signals
- Mark all SerpAPI results with `data_quality: estimated`
- On API quota exceeded: fall to Method 3

### Method 3 — Manual Paste (Fallback 2)
```
SCRAPING BLOCKED for: {competitor_url}

To continue tracking this competitor manually:
1. Open {competitor_url}recent-activity/shares/ in your browser
2. Scroll to load the last 30 days of posts
3. Copy and paste the visible post content below
4. Type DONE when finished

Format: separate each post with "---"
```
- Parse pasted content; extract approximate signals from text patterns
- Flag all manual entries with `source: manual_paste`

→ See references/SCRAPING-STRATEGY.md for Playwright session management and anti-detection

---

## Phase 3: Rank by Engagement Rate (Not Raw Numbers)

Raw engagement numbers are misleading without follower context. Always use rate.

**Engagement rate formula:**
```python
def engagement_rate(post: dict, follower_count: int) -> float:
    """Engagement rate as percentage of follower count."""
    total = post['reactions'] + post['comments'] + post['shares']
    if follower_count == 0:
        return 0.0
    return (total / follower_count) * 100

def weighted_engagement_rate(post: dict, follower_count: int) -> float:
    """Comments weighted 3x (high-intent signal)."""
    weighted = post['reactions'] + (post['comments'] * 3) + (post['shares'] * 2)
    return (weighted / follower_count) * 100 if follower_count else 0.0
```

**Follower count collection:**
- Extract from Playwright scrape (visible on profile page)
- If unavailable: use stored `follower_count` from last Neon record
- If no historical data: mark `follower_count: unknown`, use raw engagement only

**Ranking output:**
- Sort all posts by `weighted_engagement_rate` descending
- Tag top 10% as `tier_1`, top 25% as `tier_2`, remainder as `tier_3`
- Calculate per-competitor percentile rank vs. their own historical baseline

---

## Phase 4: Extract Patterns vs. Stored Historical Baseline

**Pattern extraction (same taxonomy as creator-analyzer):**

For each competitor's top-tier posts, extract:
- Hook type distribution (question, stat, contrarian, story, list, pain)
- Average post length (words) — tier_1 vs tier_2 vs tier_3
- Paragraph structure and whitespace usage
- CTA type and placement
- Hashtag count and strategy
- Emoji density and position
- Posting day and time patterns (if timestamps available)
- Topic cluster (mapped to pain-point-miner themes)

**Baseline comparison:**
```python
def compare_to_baseline(current: dict, baseline: dict) -> dict:
    return {
        "engagement_rate_delta": current['avg_rate'] - baseline['avg_engagement_rate'],
        "post_freq_delta": current['posts_per_week'] - baseline['baseline_post_freq'],
        "new_hook_types": set(current['hook_types']) - set(baseline['hook_types']),
        "dropped_hook_types": set(baseline['hook_types']) - set(current['hook_types']),
        "topic_shifts": identify_topic_shifts(current['topics'], baseline['topics'])
    }
```

Flag significant changes:
- Engagement rate delta > ±20% = "significant shift detected"
- New hook type appearing in tier_1 posts = "new tactic signal"
- Topic cluster absent from recent posts = "abandoned topic" (potential gap)

→ See references/GAP-ANALYSIS.md for baseline comparison rules and threshold definitions

---

## Phase 5: Identify Content Gaps and Opportunity Areas

**Gap identification strategy:**

1. **Coverage gaps** — Topics your competitors have never posted about, but pain-point-miner
   shows high Reddit engagement:
   ```python
   competitor_topics = set(all_tracked_competitor_topics)
   high_pain_topics = set(pain_point_miner_results['top_themes'])
   coverage_gaps = high_pain_topics - competitor_topics
   ```

2. **Depth gaps** — Topics competitors touch on but only with surface-level posts
   (short word count, low comment-to-reaction ratio = no real conversation started):
   ```python
   depth_gaps = [
       t for t in competitor_topics
       if avg_word_count(t) < 150 and comment_ratio(t) < 0.05
   ]
   ```

3. **Format gaps** — Content formats competitors are not using in their top performers:
   - No carousel descriptions despite high-performing list hooks elsewhere
   - No case study posts despite consulting niche
   - No data/research posts despite stat hooks performing well

4. **Timing gaps** — Days or times of week with low competitor posting activity
   but historically strong engagement (based on stored data)

**Opportunity scoring:**
```
opportunity_score = gap_size * 0.4 + pain_signal_strength * 0.4 + competitor_absence * 0.2
```

---

## Phase 6: Update Neon competitor_tracker and Generate Strategic Report

**Neon write — individual post records:**
```sql
INSERT INTO competitor_tracker (
  record_id, competitor_url, competitor_name, post_url,
  post_text, post_date, reactions, comments, shares,
  engagement_rate, weighted_engagement_rate, follower_count,
  tier, hook_type, cta_type, word_count, topic_cluster,
  data_quality, scrape_source, scraped_at, created_at
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
          $13, $14, $15, $16, $17, $18, $19, NOW(), NOW())
ON CONFLICT (post_url) DO UPDATE
  SET engagement_rate = EXCLUDED.engagement_rate,
      scraped_at = NOW();
```

**Neon write — baseline update:**
```sql
INSERT INTO competitor_tracker (
  record_id, competitor_url, is_baseline_row,
  baseline_engagement_rate, baseline_post_freq,
  hook_type_distribution, topic_distribution,
  follower_count, last_scraped_at
) VALUES ($1, $2, TRUE, $3, $4, $5, $6, $7, NOW())
ON CONFLICT (competitor_url, is_baseline_row) DO UPDATE
  SET baseline_engagement_rate = EXCLUDED.baseline_engagement_rate,
      last_scraped_at = NOW();
```

→ See references/NEON-SCHEMA.md for full competitor_tracker DDL

---

## Output: Competitor Intelligence Report

```
COMPETITOR INTELLIGENCE REPORT — {date}

COMPETITORS TRACKED: {N}
POSTS ANALYZED: {total} across {N} profiles (30-day window)
SCRAPE METHODS: Playwright {p}%, SerpAPI {s}%, Manual {m}%

ENGAGEMENT LEADERS (this period):
  1. {competitor_name} — avg {rate}% WER, {posts} posts
     Top content: {hook_type} hooks on {topic_cluster}
     Delta vs. baseline: {delta:+.1f}% (SIGNIFICANT SHIFT)
  2. ...

WHAT'S WORKING FOR THEM:
  • Hook type: {hook_type} — {N} top-tier posts, avg {rate}% WER
  • Format: {format_observation}
  • Topic: {topic_cluster} — consistently outperforming their average

CONTENT GAPS (your opportunities):
  HIGH PRIORITY:
  1. "{topic}" — {N} Reddit posts/month, zero coverage from any competitor
     Opportunity score: {score} | Suggested hook: "..."
  2. "{topic}" — Competitors post shallowly; no real case studies
     Opportunity score: {score} | Your angle: "..."

  MEDIUM PRIORITY:
  3. "{topic}" — {format_gap} not used despite {hook_type} performing well
     ...

STRATEGIC RECOMMENDATIONS:
  1. {specific_actionable_recommendation}
  2. {specific_actionable_recommendation}
  3. {specific_actionable_recommendation}

STORAGE: {new} new posts, {updated} updated baselines
NEXT: Pass opportunity topics to ls:idea-bank or ls:research-engine
```

---

## Error Handling

| Error | Recovery |
|---|---|
| Playwright blocked on all competitors | Escalate to SerpAPI for batch; manual paste for priority competitors |
| SerpAPI quota exhausted mid-run | Complete current competitor; mark remaining as `pending_manual` |
| Follower count unavailable | Use raw engagement with `ER: estimated` flag in report |
| No posts in 30-day window | Flag competitor as `inactive`; skip pattern extraction |
| Baseline missing (first run) | Establish baseline from current run; note in report as `baseline_established` |
| Neon write failure | Retry 3x (2s, 4s, 8s); return in-memory report with storage warning |

All errors logged with `[competitor-tracker][ERROR]` prefix.

---

## Scheduling Note

For automated weekly runs, invoke via `ls:batch-scheduler` with:
```yaml
schedule: "every Monday at 07:00"
skill: ls:competitor-tracker
inputs:
  list_name: "primary_competitors"
  notify: slack
```

---

## References

- `references/SCRAPING-STRATEGY.md` — Playwright config, 3-fallback chain, session management
- `references/NEON-SCHEMA.md` — competitor_tracker DDL, baseline row schema, indexes
- `references/GAP-ANALYSIS.md` — Gap identification methodology, opportunity scoring, threshold definitions
