---
name: ls:pain-point-miner
description: >
  PROACTIVELY extracts real audience pain points from Reddit using Pushshift and PRAW
  to surface the raw, unfiltered struggles of small business owners, consultants, and
  entrepreneurs for LinkedIn content ideation. Triggers on content research briefs,
  ICP pain discovery requests, hook ideation tasks, audience empathy mapping, and
  content angle research for AI consulting niches. Analyzes post and comment sentiment,
  clusters pain signals by theme, and stores structured records in Neon pain_points
  with keyword clusters and engagement scores for downstream content generation.
model: sonnet
context: fork
allowed-tools: Bash Read Write WebFetch WebSearch
hooks:
  PreToolUse:
    - validate_subreddit_list
  PostToolUse:
    - log_pain_extraction
  Stop:
    - confirm_neon_write
metadata:
  version: "2.0.0"
---

# ls:pain-point-miner

Extracts genuine audience pain points from Reddit for LinkedIn content ideation.
Uses Pushshift (primary) and PRAW (fallback) to search target subreddits. Clusters
results by theme and stores in Neon `pain_points` table.

→ See references/REDDIT-INTEGRATION.md for Pushshift and PRAW API setup
→ See references/NEON-SCHEMA.md for pain_points table structure
→ See references/SENTIMENT-SIGNALS.md for pain signal detection patterns

---

## Target Subreddits

Default subreddit list (override via input):
```
r/Entrepreneur
r/smallbusiness
r/consulting
r/startups
r/freelance
r/agency
r/marketing
```

These communities surface raw, high-emotion pain points from the exact ICPs served
by AI consulting. Prioritize posts with high comment-to-upvote ratios (indicates
discussion and emotional resonance, not just passive agreement).

---

## Phase 1: Specify Keywords, Subreddits, Time Range

**Required inputs:**
- `keywords` — List of 3–15 pain-related keywords (e.g., "AI implementation", "automation fails", "ROI")
- `subreddits` — Subreddit list (default: target list above)
- `time_range` — Options: `week`, `month`, `quarter`, `year` (default: `month`)
- `max_posts` — Cap per subreddit (default: 50, max: 200)
- `min_score` — Minimum upvote threshold (default: 10)

**Keyword expansion:**
Auto-expand seed keywords with pain-signal suffixes:
```python
PAIN_SUFFIXES = [
    "problem", "issue", "struggle", "help", "advice",
    "failing", "stuck", "frustrated", "how to", "why is"
]
expanded = [f"{kw} {suffix}" for kw in keywords for suffix in PAIN_SUFFIXES]
```

---

## Phase 2: Pushshift Search (Fallback: PRAW Direct)

### Method 1 — Pushshift (Primary)
```python
import requests

def search_pushshift(keyword: str, subreddit: str, time_range: str) -> list[dict]:
    before = int(time.time())
    after = before - TIME_MAP[time_range]  # e.g., month = 30 * 86400
    url = "https://api.pushshift.io/reddit/search/submission/"
    params = {
        "q": keyword,
        "subreddit": subreddit,
        "after": after,
        "before": before,
        "size": 100,
        "sort": "score",
        "score": f">{min_score}"
    }
    resp = requests.get(url, params=params, timeout=15)
    return resp.json().get("data", [])
```
- Advantage: Full-text search across all fields, time-range filtering
- On 503/504: retry once after 10s
- On persistent failure: fall to PRAW

### Method 2 — PRAW Direct (Fallback)
```python
import praw

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent="linkedin-studio-research/1.0"
)

def search_praw(keyword: str, subreddit_name: str) -> list[dict]:
    sub = reddit.subreddit(subreddit_name)
    results = sub.search(keyword, sort='relevance', time_filter='month', limit=100)
    return [serialize_submission(r) for r in results]
```
- PRAW is rate-limited to 60 requests/minute — add 1s delay between calls
- PRAW does not support arbitrary time ranges; maps to Reddit's native filters

→ See references/REDDIT-INTEGRATION.md for credential setup and rate limit strategy

---

## Phase 3: Analyze Posts + Top Comments for Pain Signals

For each collected post, analyze both the submission and top 5 comments.

**Pain signal detection:**
```python
PAIN_SIGNALS = {
    "frustration": ["frustrated", "stuck", "hate", "annoying", "terrible", "awful"],
    "confusion": ["confused", "don't understand", "no idea", "lost", "unclear"],
    "failure": ["failed", "doesn't work", "gave up", "waste of", "regret"],
    "urgency": ["need help", "please help", "urgent", "desperate", "asap"],
    "cost_pain": ["expensive", "can't afford", "too costly", "budget", "ROI"],
    "time_pain": ["takes forever", "so slow", "time-consuming", "hours", "wasting time"]
}

def detect_pain_signals(text: str) -> dict:
    text_lower = text.lower()
    return {
        category: sum(1 for phrase in phrases if phrase in text_lower)
        for category, phrases in PAIN_SIGNALS.items()
    }
```

**Comment analysis:**
- Fetch top 5 comments by upvotes for each post
- Comments with "same here", "also struggling", "this is me" = amplification signals
- Comments with solutions = evidence the pain is solvable (good for content angles)

**Composite pain intensity score:**
```
pain_score = (upvotes * 0.3) + (comment_count * 0.5) + (signal_density * 0.2)
signal_density = total_pain_signals / word_count * 100
```

→ See references/SENTIMENT-SIGNALS.md for full signal taxonomy and scoring weights

---

## Phase 4: Cluster by Theme, Score by Upvotes + Comments

Group pain points into thematic clusters using keyword overlap and co-occurrence:

```python
from collections import defaultdict

def cluster_pain_points(pain_points: list[dict]) -> dict[str, list]:
    clusters = defaultdict(list)
    for pp in pain_points:
        primary_theme = identify_primary_theme(pp['text'], pp['signals'])
        clusters[primary_theme].append(pp)
    return dict(clusters)
```

**Cluster themes for AI consulting niche (auto-detected + mapped):**
- `ai_implementation` — Difficulty deploying or scaling AI tools
- `roi_justification` — Proving AI value to stakeholders
- `vendor_selection` — Overwhelm choosing AI tools/vendors
- `team_adoption` — Staff resistance to AI workflows
- `data_quality` — Garbage-in-garbage-out problems
- `cost_overrun` — Unexpected AI project costs
- `integration_complexity` — Connecting AI to existing systems
- `expertise_gap` — Lack of internal AI skills

**Per-cluster aggregate:**
```json
{
  "theme": "ai_implementation",
  "post_count": 47,
  "total_upvotes": 3420,
  "avg_comments": 23.4,
  "cluster_pain_score": 0.87,
  "top_keywords": ["implementation", "deploy", "production", "pilot"],
  "representative_post_url": "https://reddit.com/r/.../..."
}
```

---

## Phase 5: Generate Content IDs with Hook Angle Suggestions

For each pain point cluster, generate LinkedIn-ready content angles:

```python
def generate_hook_angles(cluster: dict) -> list[str]:
    theme = cluster['theme']
    top_pain = cluster['representative_pain']
    return [
        # Question hook
        f"Why do {percentage}% of {theme.replace('_', ' ')} efforts fail before launch?",
        # Stat hook (use upvote count as social proof proxy)
        f"{cluster['post_count']} founders are struggling with this right now. Here's the fix.",
        # Contrarian hook
        f"The real reason your {theme.replace('_', ' ')} isn't working (it's not what you think)",
        # Story hook seed
        f"A client came to me {top_pain[:50]}... Here's what we found.",
        # Pain-direct hook
        f"If you're stuck on {theme.replace('_', ' ')}, read this."
    ]
```

Each cluster also receives a `content_id` (UUID) for downstream tracking.

---

## Phase 6: Store in Neon pain_points Table

```sql
INSERT INTO pain_points (
  pain_id, niche, theme_cluster, raw_pain_text, source_url,
  subreddit, upvotes, comment_count, pain_score,
  pain_signals, keyword_clusters, hook_angle_suggestions,
  post_date, scraped_at, created_at
) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, NOW(), NOW())
ON CONFLICT (source_url) DO UPDATE
  SET pain_score = EXCLUDED.pain_score,
      updated_at = NOW();
```

Also upsert cluster-level summaries:
```sql
INSERT INTO pain_points (
  pain_id, is_cluster_summary, theme_cluster, cluster_json, updated_at
) VALUES ($1, TRUE, $2, $3, NOW())
ON CONFLICT (theme_cluster, is_cluster_summary) DO UPDATE
  SET cluster_json = EXCLUDED.cluster_json,
      updated_at = NOW();
```

→ See references/NEON-SCHEMA.md for full pain_points DDL

---

## Output: Ranked Pain Points with LinkedIn Post Angle Suggestions

```
PAIN POINT MINING COMPLETE

POSTS ANALYZED: {N} across {S} subreddits
PAIN POINTS EXTRACTED: {P} individual posts
CLUSTERS IDENTIFIED: {C} themes

RANKED PAIN CLUSTERS (by cluster_pain_score):

1. AI IMPLEMENTATION (score: 0.87, {N} posts, {U} total upvotes)
   Top pain: "We spent 6 months on an AI pilot that never went live"
   Hook angles:
   - "Why 80% of AI pilots die before production (and how to survive it)"
   - "{N} founders shared their AI implementation horror stories this month"
   - "The 3 decisions that kill AI projects before they start"

2. ROI JUSTIFICATION (score: 0.81, ...)
   ...

STORAGE: {new} new pain points, {updated} updated, {duplicates} skipped
NEXT: Pass pain_ids to ls:research-engine or ls:content-writer
```

---

## Error Handling

| Error | Recovery |
|---|---|
| Pushshift 503 | Retry after 10s; fall to PRAW on second failure |
| PRAW rate limit | Enforce 1s delay; queue remaining requests |
| Zero results for keyword | Expand with PAIN_SUFFIXES and retry once |
| Zero results across all subreddits | Return empty result; do not write to Neon |
| Neon connection refused | Retry 3x (2s, 4s, 8s); return in-memory results with warning |

All errors logged with `[pain-point-miner][ERROR]` prefix.

---

## References

- `references/REDDIT-INTEGRATION.md` — Pushshift and PRAW credentials, rate limits, quota management
- `references/NEON-SCHEMA.md` — pain_points table DDL, indexes, cluster summary schema
- `references/SENTIMENT-SIGNALS.md` — Full pain signal taxonomy, scoring weights, examples
