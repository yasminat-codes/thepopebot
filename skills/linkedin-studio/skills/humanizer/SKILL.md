---
name: ls:humanizer
description: >
  PROACTIVELY runs production-grade 6-pass AI humanization to make LinkedIn drafts
  undetectable by GPTZero, Copyleaks, Originality.ai, ZeroGPT, and Turnitin. Triggers
  on requests to humanize a draft, make this sound more human, remove AI phrases,
  pass AI detection, rewrite this so it doesn't sound like AI, strip robotic language,
  or whenever ls:content-writer or ls:repurposer produces a DRAFT. Loads ai_phrases_blocklist
  and brand_voice_profile from Neon. BLOCKS output if AI self-score exceeds 25% after
  3 iterations — post cannot proceed to ls:structure-reviewer until it passes.
model: opus
context: fork
allowed-tools: Read Write Bash
hooks:
  PreToolUse:
    - validate_draft_input
    - confirm_draft_status
  PostToolUse:
    - log_humanization_scores
  Stop:
    - confirm_gate_status
metadata:
  version: "2.0.0"
---

# ls:humanizer

THE MOST CRITICAL SKILL IN THE LINKEDIN STUDIO PLUGIN.

**ZERO TOLERANCE: The output must contain 0 AI phrases. Not "few". Not "minimal". ZERO.**

Production-grade AI humanizer. Applies 6 sequential passes to eliminate every detectable
AI signal from a draft. Scans against a 350+ phrase blocklist across 12 categories
(corporate jargon, openers, transitions, conclusions, intensifiers, AI tells, filler,
hedging, academic phrasing, emotional performance, LinkedIn patterns, structure patterns).
Every phrase has a concrete replacement — no vague "rephrase" instructions.
Posts that fail the AI self-score gate (> 25%) after 3 iterations
are BLOCKED — they cannot be scheduled, shared, or passed to structure-reviewer.

→ See references/AI-PHRASES-BLOCKLIST.md for the full 350+ phrase catalog with concrete replacements (12 categories, zero vague entries)
→ See references/DETECTION-HEURISTICS.md for the 13 self-scoring criteria and weights
→ See references/SENTENCE-PATTERNS.md for restructuring patterns by sentence type
→ See references/PERSONALITY-LIBRARY.md for opinion markers and conversational asides
→ See references/BRAND-VOICE-INJECTION.md for brand fingerprinting application rules
→ See strategy/BRAND-VOICE.md for Yasmine-specific voice markers to PRESERVE during humanization
→ See strategy/POSITIONING.md for competitive moat context (nurse-to-builder narrative)

---

## Pre-Flight: Load Required Neon Data

Before any pass begins, load both datasets. Both are required.

### Load AI Phrases Blocklist
```sql
SELECT phrase, category, replacement_suggestions
FROM ai_phrases_blocklist
ORDER BY category, phrase;
```

Expected minimum: 200 rows. If fewer than 150 rows returned: warn user and proceed
with built-in blocklist (see Pass 1 fallback below).

### Load Brand Voice Profile
```sql
SELECT
  persona,
  tone,
  vocabulary_preferences,
  avoid_words,
  signature_phrases,
  typical_sentence_length,
  contraction_style
FROM brand_voice_profile
LIMIT 1;
```

If Neon unavailable: warn, proceed with built-in blocklist and default AI consulting persona.

---

## Pass 1 — AI Phrase Purge

**Goal:** Eliminate every phrase from ai_phrases_blocklist. No exceptions.

**Process:**
1. Scan full draft text against all 200+ Neon blocklist phrases (case-insensitive)
2. For each match: apply the phrase's `replacement_suggestions` (first suggestion preferred)
3. If no replacement suggestion exists: rephrase using context to preserve meaning
4. Never delete content — always replace with equivalent natural language

**Built-in blocklist (always applied regardless of Neon):**

Corporate/consulting cluster:
- leverage → use
- utilize → use
- synergies → (rephrase)
- bandwidth → time / capacity
- circle back → follow up
- touch base → check in
- move the needle → make progress / change results
- low-hanging fruit → easy wins
- best practices → (be specific)
- deep dive → look closely at / examine
- paradigm shift → fundamental change
- thought leadership → (be specific)

AI writing cluster — single-phrase openers (delete the phrase, keep the idea):
- "Here's the thing:" → (start with the idea directly)
- "Let me break it down:" → (start with the breakdown)
- "Let's dive in." → (start with the content)
- "Let's explore" → (start with the exploration)
- "I've been thinking about" → (state the thought)
- "I want to talk about" → (state the topic)
- "I've noticed that" → (state the observation)
- "Spoiler alert:" → (state the revelation)

AI writing cluster — embedded phrases:
- "it's important to note" → DELETE; state the note directly
- "it's worth noting" → DELETE; state it directly
- "in today's world" → DELETE entirely
- "in today's fast-paced world" → DELETE entirely
- "at the end of the day" → in the end
- "moving forward" → from now on
- "the bottom line" → DELETE; state it
- "in conclusion" → DELETE entirely
- "when it comes to X" → for X
- "in the realm of" → in
- "game-changer" → turning point
- "game-changing" → significant
- "revolutionary" → new
- "transformative" → meaningful
- "mind-blowing" → surprising
- "testament to" → proof of
- "delve into" → look at
- "unpack" → break down
- "multifaceted" → complex
- "nuanced" → specific
- "seamlessly" → smoothly
- "robust" → strong
- "leverage" → use
- "utilize" → use

Hedging cluster (NEW — AI hedges, humans commit):
- "tends to" → often does
- "seems to" → DELETE; state directly
- "appears to" → DELETE; state directly
- "could potentially" → can
- "it's possible that" → DELETE; state it or don't
- "arguably" → DELETE; make the argument
- "it could be argued" → I'd argue
- "one could say" → I'd say
- "the jury is still out" → we don't know yet
- "only time will tell" → we'll see

Academic cluster (NEW — formal phrasing AI defaults to):
- "in order to" → to
- "in accordance with" → following
- "prior to" → before
- "subsequent to" → after
- "in conjunction with" → with
- "in the event that" → if
- "for the purpose of" → to
- "it is imperative" → you need to
- "it cannot be overstated" → DELETE; state importance directly
- "due to the fact that" → because

Emotional performance cluster (NEW — fake emotion declarations):
- "I'm thrilled to announce" → DELETE; just announce it
- "I'm excited to share" → DELETE; just share it
- "I'm humbled by" → DELETE; just state what happened
- "I'm passionate about" → SHOW passion through results
- "I can't stress enough" → DELETE; let content carry weight
- "Words cannot express" → DELETE; use words

LinkedIn AI pattern cluster (NEW — engagement bait):
- "Agree? 🤝" → ask a specific question about the topic
- "Thoughts? 👇" → ask a specific question
- "Here are X things" → start with the first thing directly
- "Read that again." → DELETE entirely
- "Let that sink in." → DELETE entirely
- "Follow for more" → DELETE entirely

Structure pattern cluster (NEW — AI organizational tells):
- "The key is" → DELETE; state the key thing
- "The secret is" → DELETE; state it
- "Not just X, but Y" → just say Y
- "It's not about X, it's about Y" → just say "It's about Y"
- "Here's what nobody tells you" → DELETE; just say it
- "Buckle up" → DELETE entirely

**Validation after Pass 1:**
Scan output again. If any blocklist phrase still present: flag it with `[PHRASE REMAINING]`
and apply manual replacement. Zero blocklist phrases allowed in output.

→ See references/AI-PHRASES-BLOCKLIST.md for full 200+ phrase catalog with category tags

---

## Pass 2 — Sentence Restructuring

**Goal:** Eliminate parallel sentence structures and homogenized rhythm that AI detectors
flag as non-human.

**Restructuring rules:**

1. **Break parallel structures.** If 3+ consecutive sentences follow the same pattern
   (e.g., all start with "I", all follow Subject-Verb-Object identically), restructure at
   least 2 of them.

2. **Vary sentence openings.** Scan first word of each sentence:
   - If 3+ consecutive sentences start with the same word → vary at least 2
   - Preferred openers: adverbials, dependent clauses, gerunds, direct objects first

3. **Convert passive voice to active.** Find all passive constructions → rewrite active.
   Exception: intentional passive for emphasis is allowed (max 1 per post).

4. **Fragment long compound sentences.**
   - Any sentence > 20 words: consider splitting
   - Any sentence with 3+ conjunctions (and/but/or): split at natural break point

5. **Inject intentional sentence length variety:**
   - Target distribution: 30% short (< 8 words), 50% medium (8-14 words), 20% long (15+ words)
   - Ensure at least 2 sentences under 6 words in any 200-word post

→ See references/SENTENCE-PATTERNS.md for restructuring pattern library by sentence type

---

## Pass 3 — Rhythm Variation

**Goal:** Make the post sound like a person typed it in a focused state — not a machine
generating uniformly spaced prose.

**Techniques to apply:**

| Technique | Rule | Example |
|---|---|---|
| Paragraph length variation | Mix 1-sentence and 2-sentence paragraphs; avoid 3+ | — |
| Rhetorical questions | Add 1-2 per post (not at every paragraph break) | "Sound familiar?" |
| Ellipses | Use 1-2 per post for trailing thought | "And they wonder why it fails..." |
| Em-dashes | Use for emphasis or abrupt clarification | "One metric — that's it." |
| One-word impact paragraphs | Use 1 maximum per post | "Exactly." / "Wrong." |
| Conversational interjections | Insert 1 natural aside | "And honestly?" / "No joke." |

**Rules:**
- Do not use more than 2 ellipses in a single post
- Em-dashes: max 3 per post
- One-word paragraphs: max 1 per post (overuse destroys credibility)
- Rhetorical questions must connect to the surrounding idea; no generic "Right?"

---

## Pass 4 — Personality Injection

**Goal:** Add unmistakably human micro-signals throughout the text.

**Contractions (mandatory application):**
Scan every instance of these full forms and convert:
- do not → don't
- can not → can't
- will not → won't
- I have → I've (where appropriate)
- I am → I'm
- it is → it's (where appropriate)
- here is → here's
- that is → that's
- they are → they're

**First-person observation markers (add 1-2 per post):**

Preferred: naturalistic, niche-specific
- "In my experience..."
- "Honestly,"
- "Real talk:"
- "Here's what I've seen:"
- "And I've seen this a lot —"
- "After working with [X clients/teams/companies]..."
- "I'll be direct:"
- "No sugarcoating:"

Avoid: overused markers that themselves sound AI-generated
- "Here's the thing:" (blocklisted in Pass 1)
- "The truth is:" (blocklisted in Pass 1)

**Personal opinion signals (add 1 per post where natural):**
- "I think..." / "I believe..." — use sparingly; shows opinion without hedging
- "My take:" — introduces a distinct POV
- "Controversial opinion:" — use only if the point is actually controversial

→ See references/PERSONALITY-LIBRARY.md for 60+ personality markers by tone category

---

## Pass 5 — Style Fingerprinting

**Goal:** Apply the user's specific brand voice so the post sounds like them, not like
generic LinkedIn content.

**Apply from brand_voice_profile loaded in Pre-Flight:**

| Profile Field | Application |
|---|---|
| `persona` | Confirm voice matches persona archetype (e.g., "pragmatic expert") |
| `tone` | Adjust warmth, directness, formality to match profile |
| `vocabulary_preferences` | Scan post; add preferred terms where natural |
| `avoid_words` | Scan post; remove any remaining avoid-words |
| `signature_phrases` | Insert 1-2 if they fit naturally (never force) |
| Yasmine voice markers | PRESERVE nursing metaphors (triage, vitals, charting, code blue), building metaphors (ship, wire up, from scratch), and immigrant hustle language. These are NOT AI patterns — they ARE her voice. Never remove them. |
| `typical_sentence_length` | Compare post avg sentence length to profile target; adjust if >20% off |
| `contraction_style` | If profile prefers high contractions, ensure Pass 4 applied fully |

**If brand_voice_profile is empty or unavailable:**
Load voice from `strategy/BRAND-VOICE.md`: nurse turned AI builder, direct, warm-but-not-soft,
opinionated with receipts, dry humor welcome. Use Yasmine-specific vocabulary preferences
(ship > deliver, build > develop, works > performs). Preserve all voice markers. Zero emojis.

→ See references/BRAND-VOICE-INJECTION.md for per-persona fingerprinting rules

---

## Pass 6 — AI Detection Self-Score

**Goal:** Quantitatively assess how detectable the post is before sending forward.

Score the post against 13 detection heuristics. Lower is better.

| # | Heuristic | Penalty Triggers |
|---|---|---|
| 1 | Blocklist phrase presence | Any of 350+ blocklist phrases remaining → +10 |
| 2 | Sentence length uniformity | Avg deviation < 3 words across 10+ sentences → +10 |
| 3 | Paragraph length uniformity | All paragraphs same length (±1 sentence) → +8 |
| 4 | Passive voice ratio | > 20% passive constructions → +8 |
| 5 | Opener repetition | 3+ sentences same first word → +7 |
| 6 | Contraction absence | < 3 contractions in 200+ word post → +7 |
| 7 | Hedging language density | 3+ hedging phrases (tends to, seems to, arguably) → +7 |
| 8 | Missing first-person signals | No opinion markers or personal observations → +6 |
| 9 | Structural predictability | Perfect 3-part structure with equal-length sections → +6 |
| 10 | AI structure patterns | Numbered list intros, not-X-but-Y, framework announce → +6 |
| 11 | Vocabulary formality spike | 3+ formal/academic words not in brand vocabulary → +5 |
| 12 | Emotional inflation | 2+ performative emotion declarations → +5 |
| 13 | CTA formula match | CTA matches common AI CTA templates verbatim → +3 |

**Scoring:**
```
total_penalty = sum of triggered heuristic penalties (max possible: 88)
ai_score = min(total_penalty, 100)
```

→ See references/DETECTION-HEURISTICS.md for full scoring rubric with examples (13 heuristics)

### Gate Decision

| AI Score | Action |
|---|---|
| 0-15 | PASS — excellent. Proceed to ls:structure-reviewer. |
| 16-25 | PASS — acceptable. Flag score in output. Proceed. |
| 26-40 | FAIL — re-run Passes 1-4 with aggressive settings. Increment iteration counter. |
| 41-100 | FAIL — re-run Passes 1-5. Increment iteration counter. |

**Iteration limit: 3.** If score > 25% after 3 full re-runs: HARD BLOCK.

```
============================================================
HUMANIZATION BLOCKED
AI score: {score}/100 after {3} iterations
This draft cannot be scheduled or reviewed.

ACTION REQUIRED: Rewrite the draft manually or provide new
source material to ls:content-writer.
============================================================
```

---

## Output Format

On PASS:
```
============================================================
HUMANIZATION COMPLETE
AI Self-Score: {score}/100 ({pass/warning})
Iterations: {n}
Passes completed: 6/6
Blocklist phrases removed: {count}
Sentences restructured: {count}
Contractions added: {count}
Personality markers added: {count}
Brand voice applied: {yes/no (profile loaded)}
============================================================

{humanized_post_text}

============================================================
STATUS: HUMANIZED DRAFT
NEXT REQUIRED: ls:structure-reviewer
============================================================
```

---

## Error Handling

| Error | Recovery |
|---|---|
| No draft input provided | Abort; prompt for DRAFT text |
| Draft missing DRAFT status marker | Warn; ask user to confirm this is a DRAFT |
| Neon ai_phrases_blocklist unavailable | Use built-in blocklist (Pass 1); warn user |
| Neon brand_voice_profile unavailable | Use default persona; warn user |
| AI score > 25% after iteration 3 | HARD BLOCK; output blocked message |
| Post < 50 words | Warn; humanization may not be meaningful |

All errors and scores logged with `[humanizer][ERROR]` or `[humanizer][SCORE]` prefix.

---

## References

- `references/AI-PHRASES-BLOCKLIST.md` — Full 350+ phrase catalog, 12 categories, ALL concrete replacements, zero tolerance
- `references/DETECTION-HEURISTICS.md` — 13 self-scoring heuristics with penalty weights (max 88 points)
- `references/SENTENCE-PATTERNS.md` — Restructuring patterns by sentence type
- `references/PERSONALITY-LIBRARY.md` — 60+ personality markers by tone category
- `references/BRAND-VOICE-INJECTION.md` — Per-persona fingerprinting application rules
- `strategy/BRAND-VOICE.md` — Yasmine-specific voice markers to preserve
- `strategy/POSITIONING.md` — Competitive moat context for voice alignment
