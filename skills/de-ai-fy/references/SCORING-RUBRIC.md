# Scoring Rubric — AI Probability Assessment

**How to assess and score how AI a piece of writing is, on a scale of 1–10.**

---

## The Scale

| Score | Label | What It Means |
|-------|-------|---------------|
| 1 | Undetectable | No AI tells. Reads completely human. |
| 2 | Near-human | One or two minor tells, easily missed |
| 3 | Lightly marked | A few patterns — trained eye might catch it |
| 4 | Noticeable | Patterns present but subtle |
| 5 | Moderate | Clear AI tells, but not overwhelming |
| 6 | Strong signal | Multiple patterns across categories |
| 7 | Heavy | AI patterns dominate the writing |
| 8 | Very heavy | Most sentences have AI tells |
| 9 | Textbook AI | Classic AI output — all the markers present |
| 10 | Archetypal | Every pattern, every category, all at once |

**Target after de-AI-fy:** Score ≤ 3

---

## Scoring Method

Score each of the 6 categories independently, then average.

### Category Weights

| Category | Weight | Why |
|----------|--------|-----|
| Vocabulary | 25% | Highest signal — word choice is the most obvious tell |
| Sentence Structure | 20% | Strong tell — pattern repetition is hard to miss |
| Formatting | 20% | Structural tells are immediately visible |
| Tone | 20% | Hollow/hedged tone is pervasive in AI output |
| Rhythm | 10% | Subtler tell — requires trained ear |
| Content | 5% | Hardest to assess objectively |

**Final score = weighted average of all categories**

---

## Category Scoring Guides

### Category 1: Vocabulary (25%)

Score this category by counting tier 1 and tier 2 AI vocabulary hits per 500 words.

| Hits per 500 words | Score |
|-------------------|-------|
| 0 | 1 |
| 1-2 | 2-3 |
| 3-5 | 4-5 |
| 6-9 | 6-7 |
| 10-14 | 8 |
| 15-19 | 9 |
| 20+ | 10 |

**Instant 8+ if any of these appear:**
- "delve into"
- "leverage" (verb) appearing >1x
- "synergy" or "synergies"
- "holistic approach"
- "paradigm shift"
- "in today's X landscape"

---

### Category 2: Sentence Structure (20%)

| Condition | Points |
|-----------|--------|
| All sentences 15-25 words with <5 word variance | +3 |
| Zero contractions in conversational writing | +2 |
| Zero fragments in 500+ words | +2 |
| 3+ transition opener sequences (Furthermore/Additionally/Moreover) | +3 |
| Every paragraph exactly 3-4 sentences | +2 |
| 4+ passive constructions per 500 words | +2 |
| Subject starts >85% of sentences | +1 |
| 3+ perfect triple structures | +1 |

**Calculate score: total points / 1.6 (max 10)**

---

### Category 3: Formatting (20%)

| Condition | Points |
|-----------|--------|
| Headers in non-documentation content under 1,000 words | +3 |
| >30% of content in bullet lists | +2 |
| Nested bullets (sub-bullets) | +2 |
| "Key Takeaways" or "Summary" section in short content | +2 |
| "Introduction" / "Conclusion" headers | +2 |
| TOC in content under 2,000 words | +2 |
| >10% of prose words bolded | +1 |
| "In this article I will..." opener | +1 |

**Calculate score: total points / 1.5 (max 10)**

---

### Category 4: Tone (20%)

| Condition | Points |
|-----------|--------|
| "Great question!" or equivalent compliment opener | +3 |
| "I hope this helps!" or equivalent closer | +2 |
| "This is a complex topic" escape | +2 |
| "Both perspectives have merit" with no clear stance | +2 |
| 5+ hedge phrases per 500 words | +3 |
| 4+ setup phrases ("It's important to note...") per 500 words | +2 |
| Vague expert appeal without specifics | +1 |
| Empathy script ("I understand how frustrating...") | +2 |

**Calculate score: total points / 1.7 (max 10)**

---

### Category 5: Rhythm (10%)

| Condition | Points |
|-----------|--------|
| No sentence under 10 words in 500+ words | +3 |
| All paragraphs 3-4 sentences | +2 |
| No sentence over 30 words | +2 |
| Metronome-like uniformity throughout | +3 |

**Score = total points / 1 (max 10)**

---

### Category 6: Content (5%)

| Condition | Points |
|-----------|--------|
| 500+ words on debatable topic with no clear position taken | +3 |
| Every point given exactly equal depth | +2 |
| Historical context injected unnecessarily | +2 |
| Circular answer (restates question as answer) | +3 |
| "There are X types of..." classification for everything | +2 |

**Score = total points / 1.2 (max 10)**

---

## Quick Score (Fast Mode)

For rapid assessment without full rubric:

**Count the following:**

| Check | Points |
|-------|--------|
| Tier 1 vocabulary hits | 1 point each (max 4) |
| "Furthermore/Additionally/Moreover" appearances | 1 point each (max 3) |
| Headers in short non-doc content | 2 points |
| "Key Takeaways" section | 2 points |
| "Great question!" / "I hope this helps" | 2 points each |
| Hedge phrase sequences (3+ in 500 words) | 2 points |
| Zero contractions in conversational text | 1 point |
| All sentences same length | 2 points |

**Quick Score = total points (cap at 10)**

This correlates well enough with full scoring for most purposes. Use full scoring for close calls.

---

## Interpreting Scores

### Score 1-3: Minimal Treatment
- Quick vocabulary pass
- Fix any obvious transition openers
- Light contraction check
- 15-20 minutes of work

### Score 4-5: Standard Treatment
- Full vocabulary purge
- Sentence structure review
- Flatten any over-structure
- Tone review for hedging
- 30-45 minutes of work

### Score 6-7: Heavy Treatment
- All 6 layers
- May need full restructuring of paragraphs
- Opinion injection required
- 45-60 minutes of work

### Score 8-9: Full Rewrite
- Start from the core meaning
- Rebuild from scratch using the ideas, not the structure
- All AI patterns are deeply embedded
- 60-90 minutes

### Score 10: Complete Rewrite
- The AI text is a reference, not a draft
- Extract the factual content and key points
- Write fresh from scratch
- The original structure is not salvageable

---

## Pass Criteria

After de-AI-fying, the piece passes if:

- [ ] Vocabulary score ≤ 3
- [ ] Sentence structure score ≤ 3
- [ ] Formatting score ≤ 2
- [ ] Tone score ≤ 3
- [ ] Rhythm score ≤ 4
- [ ] Overall weighted score ≤ 3
- [ ] Text reads naturally when read aloud
- [ ] No sentence would be flagged by AI detection tools
- [ ] A human expert would not suspect AI authorship
