# DETECTION-HEURISTICS.md — AI Detection Scoring Criteria

10 heuristics for scoring a post's AI detectability. Score starts at 0. Higher = more AI-like.
Target: score of 15 or below before publishing. Above 30 = high detection risk.

---

## Scoring Table

| # | Heuristic | Max Penalty | Trigger |
|---|---|---|---|
| 1 | Blocklist phrase presence | +10 | Any phrase from the 350+ blocklist found |
| 2 | Sentence length uniformity | +10 | Avg deviation < 3 words |
| 3 | Paragraph length uniformity | +8 | All paragraphs within 1–2 lines of each other |
| 4 | Passive voice ratio | +8 | >20% of sentences are passive |
| 5 | Opener repetition | +7 | 3+ paragraphs start with the same word |
| 6 | Contraction absence | +7 | Fewer than 3 contractions in 200+ words |
| 7 | Missing first-person signals | +6 | No "I", "my", "me", or "I've" in text |
| 8 | Structural predictability | +6 | Intro + 3 identical-length points + conclusion |
| 9 | Vocabulary formality spike | +5 | Multiple words > 4 syllables in close proximity |
| 10 | CTA formula match | +3 | CTA is verbatim or near-verbatim generic template |
| 11 | Hedging language density | +7 | 3+ hedging phrases (tends to, seems to, arguably) |
| 12 | AI structure patterns | +6 | Numbered list intros, not-X-but-Y, framework announce |
| 13 | Emotional inflation | +5 | 2+ performative emotion declarations |

**Maximum possible score: 88**
**Target after humanization: 15 or below**
**Acceptable range: 16–25**
**High risk: 26+**

---

## Heuristic Details

### H1: Blocklist Phrase Presence
**What triggers it:** Any phrase from AI-PHRASES-BLOCKLIST.md with severity HIGH found in the post.
**Penalty:** +10 per distinct phrase found (not per occurrence). Cap at +10 total for this heuristic.
**How to fix:** Replace every HIGH-severity phrase. Remove MEDIUM-severity phrases where possible.
**Notes:** MEDIUM-severity phrases add +3 each, up to the H1 cap. LOW-severity add no score penalty but should be flagged.

---

### H2: Sentence Length Uniformity
**What triggers it:** When the average deviation between sentence lengths is less than 3 words.
**Penalty:** +10 if avg deviation < 3 words; +5 if avg deviation is 3–5 words.
**How to fix:** Introduce deliberate sentence length variation. Short punchy sentences (3–6 words) mixed with longer ones (12–18 words). See SENTENCE-PATTERNS.md.
**How to calculate:** Measure word count per sentence → compute mean → compute average absolute deviation from mean → if < 3, trigger fires.
**Target distribution:** 30% short (<8 words), 50% medium (8–14), 20% long (15+).

---

### H3: Paragraph Length Uniformity
**What triggers it:** All or most paragraphs are within 1–2 lines of each other in length.
**Penalty:** +8 if >80% of paragraphs are within 1 line of the mean paragraph length.
**How to fix:** Vary paragraph length deliberately. Use a one-line paragraph for emphasis. Allow one paragraph to run 3–4 sentences if the content warrants it. Never make all paragraphs the same length.
**Notes:** LinkedIn posts with all 2-line paragraphs are a common AI tell.

---

### H4: Passive Voice Ratio
**What triggers it:** More than 20% of sentences use passive voice construction.
**Penalty:** +8 if passive ratio > 20%; +4 if passive ratio is 15–20%.
**How to fix:** Identify passive constructions ("was done", "had been", "is being", "were given") and convert to active voice. See SENTENCE-PATTERNS.md passive → active conversion patterns.
**Examples:**
- Passive: "The proposal was reviewed by the team." → Active: "The team reviewed the proposal."
- Passive: "Mistakes were made." → Active: "I made a mistake." (own it)

---

### H5: Opener Repetition
**What triggers it:** 3 or more paragraphs begin with the same word.
**Penalty:** +7 if 3+ same opener; +4 if 2 paragraphs share a less-common opener (e.g., both start with "This").
**How to fix:** Audit every paragraph's first word. Vary openers deliberately. Common offenders: "This", "It", "The", "When", "And". See SENTENCE-PATTERNS.md opening word variation.
**Notes:** Starting every paragraph with "I" is also a pattern — vary even first-person openers.

---

### H6: Contraction Absence
**What triggers it:** Fewer than 3 contractions in a 200+ word post.
**Penalty:** +7 if 0–2 contractions; +3 if 3–4 contractions in 250+ word posts.
**How to fix:** Apply brand voice contraction style (from BRAND-VOICE-INJECTION.md). In "always" or "sometimes" mode, replace "do not" with "don't", "I have" with "I've", "it is" with "it's", "they are" with "they're", etc.
**Notes:** Contraction absence is one of the clearest AI signals in short-form text. Humans contract naturally. AI does not unless prompted.

---

### H7: Missing First-Person Signals
**What triggers it:** The post contains no instances of "I", "my", "me", or "I've".
**Penalty:** +6
**How to fix:** Add at least 2–3 first-person references. LinkedIn performs best with authentic personal voice. If the post is intentionally written from a brand or third-person perspective, this heuristic can be manually overridden.
**Notes:** Posts that read like "here is advice for you" with no "I" signal ghostwritten AI content.

---

### H8: Structural Predictability
**What triggers it:** Post follows a textbook intro → N equal-weight points → conclusion structure with no variation, surprise, or departure from expected form.
**Penalty:** +6
**How to fix:** Add a structural surprise — a one-line paragraph, a turn that reframes the earlier points, a question mid-post, or an abrupt shift in tone. See LINKEDIN-FORMATS.md for format-appropriate structural variation.
**How to detect:** Read the post. Could you predict paragraph 4 from paragraph 2? If yes, it's too predictable.

---

### H9: Vocabulary Formality Spike
**What triggers it:** 3 or more words with 4+ syllables appear within a 50-word window.
**Penalty:** +5
**How to fix:** Replace multi-syllable formal words with simpler equivalents. "Operationalize" → "put into practice". "Implementation" → "rollout" or "how you actually do it". "Prioritization" → "what you do first".
**Notes:** One or two technical terms are fine if the audience expects them. The issue is density of formal vocabulary — it reads as generated text.

---

### H10: CTA Formula Match
**What triggers it:** The closing CTA is a generic, templated phrase with no specificity to the post content.
**Penalty:** +3
**How to fix:** Tie the CTA to something specific from the post. Reference a pain point, topic, or idea that was raised in the body. Generic CTAs ("What do you think? Let me know in the comments!") score the penalty.
**Examples:**
- Generic (penalty): "Let me know your thoughts in the comments."
- Specific (no penalty): "What's the biggest gap you've seen between AI strategy and execution in your org?"

---

## Scoring Worked Example

**Post submitted for scoring:**

> In today's fast-paced business landscape, it is important to leverage your team's synergies effectively. When teams are aligned, moreover, they can deliver impactful results that move the needle. Additionally, stakeholders need to be engaged throughout the process. Furthermore, the utilization of data-driven approaches can enhance performance. In conclusion, by implementing these strategies, organizations can achieve their goals.

**Scoring:**

| Heuristic | Finding | Penalty |
|---|---|---|
| H1: Blocklist phrases | "In today's", "leverage", "synergies", "impactful", "move the needle", "stakeholders", "moreover", "Additionally", "Furthermore", "utilize", "In conclusion" | +10 (capped) |
| H2: Sentence length uniformity | All sentences: 12, 14, 11, 13, 12 words. Avg deviation = 1.0 | +10 |
| H3: Paragraph length uniformity | All 1 paragraph (single block) — N/A | 0 |
| H4: Passive voice ratio | "can be engaged" = passive. 1/5 sentences = 20% — borderline | +4 |
| H5: Opener repetition | "When", "Additionally", "Furthermore" — no exact repeat | 0 |
| H6: Contraction absence | 0 contractions in 70 words (under 200-word threshold) | 0 |
| H7: Missing first-person | No "I", "my", "me" | +6 |
| H8: Structural predictability | Intro + generic points + conclusion — textbook | +6 |
| H9: Vocabulary formality spike | "leveraging", "utilizing", "implementing", "operationalize" in close proximity | +5 |
| H10: CTA formula match | "achieve their goals" = generic | +3 |

**Total score: 44 — HIGH detection risk. Full rewrite required.**

---

## New Heuristics (H11–H13)

### H11: Hedging Language Density
**What triggers it:** 3 or more hedging phrases from Category 8 (hedging) found in a single post.
**Penalty:** +7 if 3+ hedging phrases; +3 if 2 hedging phrases.
**How to fix:** Commit to statements. Replace "tends to" with "often does". Replace "seems to" with direct assertion. Delete "it's possible that" and just state the possibility. Delete "arguably" and make the argument instead.
**Hedging markers to scan for:** tends to, seems to, appears to, might be, could potentially, it's possible that, may or may not, to some extent, in some ways, it could be argued, one could say, it's fair to say, arguably, perhaps, it is believed that, some would argue, the jury is still out, only time will tell.
**Notes:** AI hedges because it's trained to be cautious. Humans who know their subject commit. A post with 3+ hedges reads as someone who doesn't believe their own point.

---

### H12: AI Structure Pattern Detection
**What triggers it:** Post follows a recognizable AI structural template.
**Penalty:** +6 for any of the following patterns:
- **Numbered list intro:** Post opens with "Here are X things/tips/ways" then lists them → +6
- **Not-X-but-Y pattern:** 2+ instances of "It's not about X, it's about Y" or "Not just X, but Y" → +4
- **Framework announce:** Post says "Here's a framework" or "Let me share a framework" then presents a named framework → +3
- **Mirror structure:** Hook makes a claim, body has 3 equal-weight points, CTA restates the hook → +6
**How to fix:** Start with the strongest point instead of announcing how many points you have. Eliminate "Not X but Y" framing — just state Y. Don't announce frameworks — just share the content. Break mirror structure by making one section longer, adding a turn, or ending on a different note than where you started.
**Cap:** +6 total for this heuristic (worst pattern scores).

---

### H13: Emotional Inflation
**What triggers it:** Post contains performative emotion declarations from Category 10 (emotional).
**Penalty:** +5 if 2+ emotional performance phrases; +3 if 1 emotional performance phrase.
**How to fix:** Delete the emotion declaration. Show the emotion through specifics instead. "I'm thrilled to announce we raised $5M" → "We raised $5M. Took 14 months and 47 investor meetings." The specifics carry more emotional weight than the declaration.
**Emotional inflation markers:** I'm so excited, I'm thrilled, I'm honored, I'm humbled, I'm passionate about, I'm blessed, I'm grateful for, I couldn't be more proud, words cannot express, it fills me with joy, this means the world, absolutely blown away, super pumped, beyond excited, deeply moved.
**Notes:** Real emotion in writing comes from concrete detail, not from telling the reader what emotion you feel. "I'm thrilled" is a mask. "I called my mom at midnight" is real.
