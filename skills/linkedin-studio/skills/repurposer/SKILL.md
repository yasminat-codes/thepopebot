---
name: ls:repurposer
description: >
  PROACTIVELY transforms long-form content into multiple LinkedIn post formats by
  extracting the highest-engagement angles, scoring each for LinkedIn potential, and
  generating formatted output in 1-4 formats. Triggers on requests to repurpose this
  article, turn this into a LinkedIn post, extract LinkedIn content from this blog,
  make LinkedIn posts from this transcript, repurpose this newsletter, pull LinkedIn
  content from this URL, or turn this podcast into posts. All output enters the
  ls:humanizer and ls:structure-reviewer pipeline before scheduling.
model: sonnet
context: fork
allowed-tools: Read Write WebFetch Bash
hooks:
  PreToolUse:
    - validate_source_input
  PostToolUse:
    - log_repurpose_session
  Stop:
    - confirm_drafts_pending
metadata:
  version: "2.0.0"
---

# ls:repurposer

Transforms long-form content — blog posts, podcast transcripts, YouTube descriptions,
newsletters, case studies — into LinkedIn-optimized post formats. Extracts multiple
angles from source material and lets the user choose which formats to generate.

All output is marked DRAFT and must pass ls:humanizer and ls:structure-reviewer.

→ See references/ANGLE-SCORING.md for engagement potential scoring model
→ See references/LINKEDIN-FORMATS.md for per-format structure rules and templates
→ See references/EXTRACTION-PATTERNS.md for insight extraction techniques by content type
→ See references/HOOK-FORMULAS.md for hook generation from extracted insights

---

## Phase 1: Receive and Validate Source Content

**Accepted input types (exactly one required):**

| Type | Description | Notes |
|---|---|---|
| `url` | URL to blog post, YouTube description, newsletter archive | Fetched via WebFetch |
| `paste` | Direct paste of text content | Paste into input |
| `file_path` | Path to local .txt or .md transcript file | Read via Read tool |

**Optional parameters:**
- `content_type` — Hint for extraction: `blog`, `podcast_transcript`, `youtube_description`, `newsletter`, `case_study`, `research_paper`. If omitted, auto-detect from content.
- `formats` — Comma-separated list of desired output formats (see Phase 4). If omitted, prompt user to select after angle scoring.
- `max_angles` — Max number of angles to extract and score (default: 5, max: 10)

**Input validation:**
```bash
if [ -z "$SOURCE_URL" ] && [ -z "$PASTE_TEXT" ] && [ -z "$FILE_PATH" ]; then
  echo "[repurposer][ERROR] One of url, paste, or file_path is required" >&2
  exit 1
fi
```

**URL fetch:**
If `url` provided, fetch with WebFetch. If fetch fails or returns < 200 words of
usable text: abort with `[repurposer][ERROR] URL returned insufficient content —
paste the text directly instead.`

**File read:**
If `file_path` provided, read with Read tool. Validate path exists before proceeding.

---

## Phase 2: Extract Key Insights and Angles

Parse the full source content. Extract 3-5 distinct content angles.
If `max_angles` is set higher, extract up to that number.

**Auto-detect content type if not provided:**

| Signal | Type Detected |
|---|---|
| "Episode", "Host:", "Guest:", timestamps like "[00:00]" | podcast_transcript |
| "Subscribe", "Issue #", "This week in" | newsletter |
| YouTube watch URLs, "video description", "subscribe" | youtube_description |
| Headers, H2/H3 structure, "Read more" | blog |
| "Client", "results", "before/after", "ROI" | case_study |

**Extraction instructions by type:**

**blog:** Extract the 3-5 strongest individual claims, counterintuitive points, data
points, or personal stories from the text. Each must stand alone without the article.

**podcast_transcript:** Identify the 3-5 most quotable or insight-dense speaker turns.
Strip filler words ("um", "you know", "like") and compress to the core idea.

**newsletter:** Extract the main thesis + any numbered lessons, frameworks, or
tactical recommendations. Each numbered item is a candidate angle.

**case_study:** Extract: the before-state (problem), the turning point (action), the
result (outcome with numbers if present). Each stage is a candidate angle.

**research_paper:** Extract the key finding, the most surprising statistic, and any
practitioner-relevant implication. Avoid jargon in the angle description.

→ See references/EXTRACTION-PATTERNS.md for extraction techniques per content type

**Angle structure (for each extracted angle):**
```json
{
  "angle_id": "A1",
  "angle_type": "insight|story|data|framework|counterintuitive|how-to",
  "core_idea": "1-sentence summary of the angle",
  "source_excerpt": "the raw text this angle came from (50-100 words)",
  "target_linkedin_format": "text_post|carousel|poll|document",
  "hook_seed": "the tension or curiosity gap in this angle"
}
```

---

## Phase 3: Score Each Angle for LinkedIn Engagement Potential

Score each angle on 5 dimensions. Total out of 100.

| Dimension | Weight | What it measures |
|---|---|---|
| Relatability | 25pts | Will the target audience immediately recognize this problem or situation? |
| Originality | 20pts | Is this a fresh take, or has this been said 100 times on LinkedIn? |
| Actionability | 20pts | Can the reader do something with this today? |
| Emotional pull | 20pts | Does this create any emotional response (frustration, hope, surprise, validation)? |
| Hook potential | 15pts | How strong is the natural curiosity gap or tension in this angle? |

**Scoring quick-reference:**

| Score | Relatability | Originality | Actionability | Emotional pull | Hook potential |
|---|---|---|---|---|---|
| 90-100% of weight | Universal pain point, everyone nods | Genuinely novel frame | Immediate, specific action | Strong visceral response | Natural showstopper |
| 60-80% | Most in audience | Somewhat fresh | Actionable with context | Noticeable reaction | Good tension |
| 30-60% | Some in audience | Familiar but okay | Aspirational only | Mild interest | Weak tension |
| 0-30% | Niche or abstract | Overdone | No clear action | No reaction | No tension |

**Composite score:**
```
angle_score = (relatability + originality + actionability + emotional_pull + hook_potential)
```

→ See references/ANGLE-SCORING.md for detailed scoring rubric with anchor examples

---

## Phase 4: Present Angles and Format Selection

Present scored angles to user before generating content.

```
============================================================
REPURPOSER — ANGLE ANALYSIS
Source: {content_type} — {title or first 60 chars}
Word count: {N} words extracted
============================================================

RANKED ANGLES (by engagement score)

#  SCORE  TYPE            CORE IDEA
── ────── ─────────────── ────────────────────────────────
1  87/100 counterintuitive {core idea}
2  79/100 story           {core idea}
3  71/100 data            {core idea}
4  63/100 how-to          {core idea}
5  58/100 insight         {core idea}

SELECT ANGLES: Which angles do you want to use? (e.g., "1, 3" or "all top 3")
SELECT FORMATS: text_post | carousel_script | poll_post | document_post
               (One format per angle, or same format for multiple angles)
============================================================
```

**If `formats` was pre-specified in input:** skip the format selection prompt and
proceed immediately with the provided combination.

**Valid combinations:**
- 1 angle × 1-4 formats (generates multiple formats for same angle)
- 2-5 angles × 1 format each (generates one post per angle)
- 2-5 angles × multiple formats each (batch generation)

---

## Phase 5: Generate Content in Selected Formats

For each selected angle + format combination, generate a full draft.

### text_post (150-300 words)
- Open with hook derived from `hook_seed`
- Body: narrative or insight arc using `source_excerpt` as foundation
- Apply LinkedIn writing rules: short sentences, whitespace, conversational voice
- Close with engagement question + CTA
- Label: `[TEXT POST — Angle {id}]`

### carousel_script (5-10 slides)
- Slide 1: Hook slide — hook text only, no explanation
- Slides 2-3: Build the tension or context (one point per slide, ≤ 40 words/slide)
- Slides 4-N: Resolution, framework, or lessons (one per slide)
- Final slide: CTA + handle or resource
- Label: `[CAROUSEL — Angle {id}]` with `[SLIDE N]` markers

### poll_post
- Opening paragraph (50-80 words): frame the debate or dilemma from the angle
- Poll question (≤ 25 words): binary or multiple-choice dilemma
- 2-4 answer options (≤ 30 chars each)
- Closing paragraph (30-50 words): why the poll matters + engagement prompt
- Label: `[POLL POST — Angle {id}]`

### document_post
- Structured outline for a PDF or slide document
- Cover: title derived from angle + hook statement
- Table of contents: 5-8 sections
- Per-section: header + 2-3 bullet points of content direction (not full copy)
- Last section: CTA page content
- Label: `[DOCUMENT POST — Angle {id}]`

→ See references/LINKEDIN-FORMATS.md for detailed per-format rules and word count requirements

---

## Phase 6: Assemble All Drafts and Return

Return all generated drafts in a single output block.

```
============================================================
REPURPOSER COMPLETE
Source: {content_type}
Angles used: {N}
Drafts generated: {N}
============================================================

{for each draft:}

------------------------------------------------------------
DRAFT — PENDING QUALITY REVIEW
ls:humanizer and ls:structure-reviewer required before use
------------------------------------------------------------

{draft label}

{draft content}

------------------------------------------------------------

{repeat for each draft}

============================================================
STATUS: {N} DRAFTS PENDING
NEXT REQUIRED FOR EACH: ls:humanizer → ls:structure-reviewer
DO NOT SCHEDULE UNTIL BOTH PASS
============================================================
```

---

## Error Handling

| Error | Recovery |
|---|---|
| URL returns no content | Abort; ask user to paste content directly |
| Content < 200 words | Warn; proceed but note extraction may be limited |
| No clear angles found | Abort; ask user to identify the main insight manually |
| Format not recognized | Abort; list valid formats |
| WebFetch blocked or 403 | Abort; ask user to paste content directly |
| File path not found | Abort; ask user to check path or paste content |
| Score tie between angles | Present all tied angles; let user decide |

All errors logged with `[repurposer][ERROR]` prefix for Coolify log capture.

---

## References

- `references/ANGLE-SCORING.md` — Engagement potential scoring model with anchor examples
- `references/LINKEDIN-FORMATS.md` — Per-format structure rules, slide templates, word counts
- `references/EXTRACTION-PATTERNS.md` — Insight extraction techniques by content type
- `references/HOOK-FORMULAS.md` — Hook generation from extracted angle hook_seed
