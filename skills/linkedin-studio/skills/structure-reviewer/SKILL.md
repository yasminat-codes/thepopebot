---
name: ls:structure-reviewer
description: >
  PROACTIVELY runs LinkedIn structure compliance checks across 7 scored dimensions,
  gates posts that fail hook strength or CTA presence, and returns specific fix
  instructions for every failed check. Triggers on requests to review a LinkedIn post,
  check post structure, score this draft, run quality check, validate my LinkedIn post,
  check hook strength, review CTA, or whenever ls:humanizer completes and returns a
  HUMANIZED DRAFT. Posts scoring below gate thresholds are BLOCKED from scheduling
  until defects are resolved.
model: sonnet
context: fork
allowed-tools: Read Write Bash
hooks:
  PreToolUse:
    - validate_humanized_status
  PostToolUse:
    - log_structure_scores
  Stop:
    - confirm_review_complete
metadata:
  version: "2.0.0"
---

# ls:structure-reviewer

LinkedIn structure compliance checker. Scores posts on 7 dimensions totaling 100 points.
Two hard gates: hook strength below minimum OR CTA absent = BLOCKED, cannot proceed
to scheduling or publishing.

→ See references/HOOK-SCORING.md for hook strength rubric with examples and score anchors
→ See references/FORMAT-RULES.md for per-format structure requirements
→ See references/HASHTAG-STRATEGY.md for niche/reach/community tag classification
→ See references/FIX-TEMPLATES.md for pre-written fix suggestions per failure type

---

## Phase 1: Receive and Validate Input

**Required input:**
- Post text (minimum 50 words for text posts; for carousels, all slide copy)
- Post format: `text_post`, `carousel_script`, `poll_post`, or `document_post`

**Required status check:**
Post must carry a `HUMANIZED DRAFT` status marker from ls:humanizer.
If status marker is absent: warn user that humanization has not run, ask to confirm
they want to proceed anyway. Do not block — structure review can run on any draft,
but log the missing humanization flag.

**Validation:**
```bash
if [ -z "$POST_TEXT" ]; then
  echo "[structure-reviewer][ERROR] Post text is required" >&2
  exit 1
fi

if [ "${#POST_TEXT}" -lt 100 ]; then
  echo "[structure-reviewer][WARN] Post is very short — review may be incomplete" >&2
fi
```

---

## Phase 2: Score All 7 Dimensions

Score each dimension independently. Apply the dimension's scoring rubric exactly.
Do not round — use integer scores. Sum all dimension scores for total.

---

### Dimension 1 — Hook Strength (25 points) [GATE]

Score the first line of the post (or Slide 1 for carousels).

| Score | Criteria |
|---|---|
| 23-25 | Showstopper — creates strong curiosity gap, pattern interrupt, bold claim, or personal story that demands a click. Reader cannot scroll past. |
| 18-22 | Strong — clearly engaging, relevant to audience, specific rather than generic. |
| 14-17 | Adequate — functional but predictable. Does not stop scroll. |
| 8-13 | Weak — generic, vague, or leads with context before the hook. |
| 0-7 | Fails — opener is a statement with no tension, a greeting, or a list lead-in. |

**Minimum required: 14/25 (equivalent to 7/10).**
Scores below 14 = GATE FAILURE — post is BLOCKED.

**Hook quality checklist (apply during scoring):**
- Does it create a curiosity gap? (reader wants to know what comes next)
- Does it make a bold or counterintuitive claim?
- Is it specific (names a number, person, situation) rather than abstract?
- Does it avoid common AI openers from the blocklist?
- Is it under 15 words?
- Would it stop a scroll in a busy LinkedIn feed?

→ See references/HOOK-SCORING.md for score anchor examples and hook type breakdown

---

### Dimension 2 — Sentence Structure (15 points)

| Score | Criteria |
|---|---|
| 13-15 | Consistently short sentences; avg word count per sentence ≤ 10; clear variety in length |
| 9-12 | Mostly short; a few run-ons but not dominant; avg ≤ 13 words |
| 5-8 | Some long sentences or run-ons; avg 14-17 words; noticeable drag |
| 0-4 | Frequent run-ons; compound sentences > 20 words; difficult to read quickly |

**Measurement:**
```
avg_sentence_length = total_words / sentence_count
run_on_count = sentences where word_count > 20
```

**Fix triggers:**
- avg_sentence_length > 13: "Break sentences at conjunctions. Target avg ≤ 10 words."
- run_on_count > 2: "Split the following sentences: [list sentences]"

---

### Dimension 3 — Whitespace and Formatting (15 points)

| Score | Criteria |
|---|---|
| 13-15 | Excellent visual rhythm — one sentence per line, strategic visual elements (→, —, ...), at least 2 short-punch lines (1-5 words), blank lines between all paragraphs, mobile-optimized |
| 10-12 | Good formatting — mostly one-sentence lines, some visual elements present, adequate whitespace, minor rhythm issues |
| 7-9 | Adequate — paragraphs separated by blank lines but lacking visual rhythm: multi-sentence lines, no visual elements, no short-punch emphasis |
| 0-6 | Dense blocks, multi-sentence lines, missing blank lines, no visual elements, unreadable on mobile |

**Checks:**
- Paragraphs separated by blank lines: yes/no
- Any paragraph > 3 lines (approx 45 words): flag it
- Bullet-point wall (5+ consecutive bullets): flag it
- Subheadings or markdown headers present: flag as not LinkedIn-native
- One sentence per line: flag any line containing two or more sentences
- Short-punch lines (1-5 words): count them — minimum 2 per post
- Visual element usage: at least 1 of (→, —, ...) used strategically
- Visual element overuse: flag if any element exceeds its max (→ max 4, — max 3, ... max 2)
- Two or more visual elements combined in one sentence: flag it

→ See content-writer/references/POST-ANATOMY.md for visual element limits and formatting rules

**Fix triggers:**
- Dense paragraph found: "Add a blank line after: '[first 8 words of paragraph]...'"
- Bullet wall: "Convert bullets to single-sentence paragraphs with line breaks."
- Multi-sentence line: "Split into separate lines — one sentence per line: '[the offending line]'"
- Missing short-punch lines: "Add 2+ short-punch lines (1-5 words) for visual emphasis. Examples: 'That's it.' / 'Every time.' / 'Wrong.'"
- No visual elements: "Add at least 1 visual element (→, —, or ...) — see POST-ANATOMY.md for usage guidance."
- Visual element overuse: "Reduce [element] usage — max [N] per post per POST-ANATOMY.md limits."

---

### Dimension 4 — CTA Strength (20 points) [GATE]

| Score | Criteria |
|---|---|
| 18-20 | Specific CTA + low-friction action. Names exactly what to do and why it's easy ("DM me 'X' and I'll send you..."; "Drop your answer below in one word.") |
| 12-17 | Specific CTA. Clear ask, but slightly more effort required. |
| 4-11 | Generic CTA. Vague ask ("let me know your thoughts", "share this if you agree"). |
| 0-3 | Absent or buried. No CTA found, or CTA hidden mid-post without emphasis. |

**GATE: Score of 0-3 (absent or buried CTA) = BLOCKED.**

**CTA detection:**
Scan last 60 words of post for action verbs directed at the reader.
Absent if: no action verb in final 60 words addressed to reader.
Generic if: "let me know", "share this", "what do you think", "leave a comment" with no specificity.

**Fix triggers:**
- CTA absent: "Add a CTA as the final line. Example: 'Drop your biggest X challenge below — I read every reply.'"
- CTA generic: "Replace '[generic cta]' with a specific ask. Name the action + the reward."

→ See references/FIX-TEMPLATES.md for CTA fix templates by post type

---

### Dimension 5 — Hashtag Strategy (10 points)

| Score | Criteria |
|---|---|
| 9-10 | 3-5 hashtags; mix of niche (high relevance, lower volume) + reach (higher volume, broad) + community tags; none are #LinkedIn, #Networking, or #Content |
| 6-8 | Correct count but suboptimal mix (all niche or all broad) |
| 3-5 | 1-2 hashtags only, or 6-8 hashtags (over-tagged) |
| 0-2 | No hashtags, or > 8 hashtags, or exclusively generic tags |

**Tag classification:**
- Niche tags: highly specific to topic (e.g., #AIconsulting, #RAGimplementation)
- Reach tags: broader audience (e.g., #ArtificialIntelligence, #MachineLearning)
- Community tags: audience identity (e.g., #CTOs, #StartupFounders)

**Banned tags (always flag as defect):**
- #LinkedIn, #Networking, #SocialMedia, #Content, #Marketing (too generic)
- Any hashtag > 30 characters

**Fix triggers:**
- Missing hashtags: "Add 3-5 hashtags. Suggested: [niche tag], [reach tag], [community tag]"
- Over-tagged: "Remove hashtags down to 5. Keep the most specific ones."
- Banned tag present: "Remove [tag] — this tag is too generic and reduces reach."

→ See references/HASHTAG-STRATEGY.md for full niche tag taxonomy for AI consulting content

---

### Dimension 6 — Post Length (10 points)

**Length targets by format:**

| Format | Target Range | Scoring |
|---|---|---|
| text_post | 150-300 words | 10pts in range; 8pts 120-149 or 301-350; 5pts 100-119 or 351-400; 0pts outside |
| carousel_script | 5-10 slides | 10pts in range; 6pts 4 slides; 0pts < 4 or > 12 |
| poll_post | 80-150 words + 2-4 options | 10pts if body + options in range; proportional otherwise |
| document_post | 6-10 sections | 10pts in range; 6pts 5 sections; 0pts < 5 |

**Word count measurement:**
```
word_count = len(post_text.split())
slide_count = count of [SLIDE N] markers in carousel
```

**Fix triggers:**
- Too short: "Post is [N] words. Add more detail to reach 150 words minimum."
- Too long: "Post is [N] words. LinkedIn readers drop off after 300. Cut [N-280] words."

---

### Dimension 7 — Engagement Hook (5 points)

| Score | Criteria |
|---|---|
| 5 | Explicit engagement invitation at post end: question, poll suggestion, or comment prompt that is specific and easy to answer |
| 3 | Implied invitation (open-ended CTA doubles as engagement hook) |
| 0 | No engagement hook; post ends with pure information or a link |

**Detection:**
Scan final 40 words for: direct question to reader, "comment below", "drop a reply",
poll framing, or "tag someone who".

**Fix triggers:**
- Missing: "Add a one-sentence question before your CTA. Example: 'Which of these have you run into?'"
- Too complex: "Simplify your closing question — 5 words or fewer answer."

---

## Phase 3: Calculate Total Score and Gate Decisions

```
total_score = D1 + D2 + D3 + D4 + D5 + D6 + D7
```

**Gate checks (evaluated before total score):**

| Gate | Condition | Action |
|---|---|---|
| Hook Gate | D1 < 14 | BLOCKED — hook must be rewritten before review can pass |
| CTA Gate | D4 < 4 | BLOCKED — CTA must be added or rewritten before review can pass |

**Total score interpretation:**

| Score | Status | Action |
|---|---|---|
| 90-100 | EXCELLENT | Proceed to scheduling |
| 80-89 | STRONG | Proceed; optional improvements noted |
| 70-79 | ADEQUATE | Proceed with warnings; fix suggestions provided |
| 60-69 | WEAK | Fix recommended before scheduling; not blocked |
| 0-59 | POOR | Hard recommend to rewrite; not blocked unless gates fail |

---

## Phase 4: Build Fix Suggestions

For every dimension scoring below its target, generate a specific, actionable fix.

**Fix suggestion format (per dimension):**
```
[D{N} — {Dimension Name}] Score: {score}/{max}
Problem: {1-sentence problem description}
Fix: {specific actionable instruction}
Example: {before/after example if helpful}
```

Fixes must be specific — never generic ("improve your hook"). Always name the exact
text to change or the exact action to take.

→ See references/FIX-TEMPLATES.md for pre-written fix templates by failure type

---

## Phase 5: Return Scored Report

```
============================================================
STRUCTURE REVIEW COMPLETE
============================================================

POST FORMAT: {format}
WORD COUNT: {count}

SCORES
──────────────────────────────────────────
D1  Hook Strength          {score}/25   {PASS|GATE FAIL}
D2  Sentence Structure     {score}/15   {PASS|FAIL}
D3  Whitespace/Formatting  {score}/15   {PASS|FAIL}
D4  CTA Strength           {score}/20   {PASS|GATE FAIL}
D5  Hashtag Strategy       {score}/10   {PASS|FAIL}
D6  Post Length            {score}/10   {PASS|FAIL}
D7  Engagement Hook        {score}/5    {PASS|FAIL}
──────────────────────────────────────────
TOTAL                      {score}/100

STATUS: {BLOCKED|APPROVED|APPROVED WITH WARNINGS}

{if BLOCKED:}
GATE FAILURES — MUST FIX BEFORE PROCEEDING:
{gate failure fix suggestions}

{if any dimension failed:}
FIX SUGGESTIONS:
{fix suggestion blocks per failed dimension}

{if APPROVED:}
NEXT: ls:batch-scheduler or ls:content-calendar
============================================================
```

---

## Error Handling

| Error | Recovery |
|---|---|
| Post text empty | Abort; prompt for post text |
| Format not recognized | Warn; default to text_post scoring rules |
| Post < 50 words | Warn; score anyway; flag D6 automatically |
| Hook not identifiable | Score D1 as 0; provide hook fix template |
| No humanization marker | Warn; proceed; log missing humanization |

All scores and errors logged with `[structure-reviewer][SCORE]` and
`[structure-reviewer][ERROR]` prefixes for Coolify log capture.

---

## References

- `references/HOOK-SCORING.md` — Hook strength rubric with score anchors and examples
- `references/FORMAT-RULES.md` — Per-format structure requirements and word count rules
- `references/HASHTAG-STRATEGY.md` — Niche/reach/community tag taxonomy for AI consulting
- `references/FIX-TEMPLATES.md` — Pre-written fix suggestions by dimension and failure type
