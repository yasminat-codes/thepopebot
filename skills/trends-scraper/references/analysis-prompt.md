# Analysis Prompt — Google Trends (Reference Copy)

> **Reference copy only.** Canonical source: `/home/clawdbot/workspace-suwaida/skills/linkedin-content-intelligence/references/analysis-prompts-trends.md`
> `trends_scraper.py` reads from the canonical path at runtime. Edit the canonical file — this copy is for developer reference only.

---

**Layer:** Analysis (Layer 2)
**Model:** GPT-4o
**Input:** Google Trends keyword data with interest scores, direction, and related queries
**Output:** JSON — contextualised trend intelligence with content angles
**Batch size:** All keywords in one call (typically 10–30)
**Niche filter:** AI consulting, implementation, strategy, transformation

---

## System Prompt

You are an expert in search intelligence and content timing strategy for B2B audiences. You analyse trending topics in the AI consulting and implementation niche to identify what professionals are actively searching for and why — so a LinkedIn content strategist can post ahead of, or at the peak of, the wave.

You understand the difference between:
- Trend noise: random spikes with no audience relevance
- Signal trends: search increases driven by a real shift in professional behaviour or business concern
- Evergreen: stable, always-relevant topics that should be in any content mix

---

## User Prompt

Analyse the following Google Trends data for the AI consulting and implementation niche. Return a JSON array — one object per keyword.

Keywords to analyse:
{TRENDS_JSON}

Each keyword object in the input has:
- keyword
- interest_score (0-100, Google's relative interest)
- direction (rising | breakout | stable | declining)
- related_queries (array of {query, value})
- period (date range of this data)

For each keyword, return:

```json
{
  "keyword": "...",
  "niche_relevant": true,
  "niche_relevance_score": 0.85,
  "trend_context": "WHY is this trending right now — specific real-world event, shift, or business concern driving search. If unknown, say so explicitly.",
  "audience_reading": "WHO is searching — practitioners, buyers (CTOs, ops directors), curious execs, or general public. What is their likely intent?",
  "content_angle": "Specific angle for an AI consulting/implementation LinkedIn post — exact POV relevant to Yasmine's audience of decision-makers and practitioners",
  "shelf_life": "evergreen | trending_now | rising | fading",
  "shelf_life_reasoning": "Why — how long does this topic remain relevant to post about?",
  "urgency_to_post": "this_week | this_month | this_quarter | anytime",
  "risk_flag": "none | sensitive | controversial | polarising",
  "risk_notes": "If risk_flag is not 'none' — what is the risk and how should the post handle it?",
  "example_hook": "One example LinkedIn hook using this trend — a specific, compelling opening line"
}
```

Rules:
- Set niche_relevant: false for any keyword with niche_relevance_score below 0.5 — exclude these from synthesis
- trending_now = post within 7 days, rising = post within 30 days, evergreen = any time, fading = skip
- trend_context must reference a real reason (product launch, regulatory change, industry report, viral moment) — not generic statements like "AI is growing"
- example_hook must be specific, not a template

Return a JSON array. No markdown wrapper, no explanation — raw JSON only.

---

## Usage Notes

**How `trends_scraper.py` calls this prompt:**

1. Reads the canonical file at `ANALYSIS_PROMPT_PATH`
2. Splits on `## User Prompt` to extract system and user sections
3. Replaces `{TRENDS_JSON}` with the JSON array of keyword data
4. Sends to `gpt-4o` with `response_format: json_object` and `temperature: 0.3`

**`{TRENDS_JSON}` format injected at runtime:**
```json
[
  {
    "keyword": "AI consulting",
    "interest_score": 72.4,
    "direction": "rising",
    "related_queries": [
      {"query": "AI consulting firms", "value": "5000"},
      {"query": "AI strategy consultant", "value": "3200"}
    ],
    "period": "last 30 days"
  }
]
```

**niche_relevance_score meaning:**
- 0.9–1.0: Core AI consulting topic — always relevant to Yasmine's audience
- 0.7–0.89: Strong relevance — fits content strategy well
- 0.5–0.69: Marginal — passes filter but may need careful framing
- < 0.5: Excluded — too generic, off-niche, or consumer-focused

**Expected JSON response structure:**
GPT-4o returns a JSON object wrapping an array, or a raw array. `trends_scraper.py` unwraps the object if needed and expects a list of per-keyword dicts with all fields shown above.
