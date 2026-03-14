---
name: de-ai-fy
description: Strips all AI fingerprints from text and rewrites it to sound authentically human. Use when text sounds robotic, AI-generated, or like it was written by a language model. Use when removing AI tells, humanizing content, de-roboticizing writing, wiping AI traces, making text sound human, fixing AI vocabulary, removing em-dashes, fixing over-structured formatting, eliminating hedging language, or any request to make writing less AI-like.
allowed-tools: Read Write Edit Bash(python:*)
metadata: {"clawdbot":{"emoji":"🧹"}}
---

# De-AI-Fy

**Wipes every detectable AI fingerprint from text. Transforms robotic, over-structured, hedge-filled writing into prose that reads like a real person wrote it — with human cadence, natural imperfection, and genuine voice.**

---

## The Iron Law

```
DE-AI-FY OPERATES ON 7 LAYERS + THE ZERO-POINT PROTOCOL:
├─ Layer 1: VOCABULARY — 244+ banned AI words and phrases replaced
├─ Layer 2: SENTENCE STRUCTURE — AI sentence patterns broken up
├─ Layer 3: FORMATTING — over-structured bullets/headers flattened
├─ Layer 4: TONE — hedging, hollow filler, passive voice stripped
├─ Layer 5: RHYTHM — unnaturally perfect cadence roughed up
├─ Layer 6: AUTHENTICITY — human quirks, directness, personality injected
├─ Layer 7: STATISTICAL — perplexity + burstiness optimized to beat AI detectors
└─ ZP: ZERO-POINT PROTOCOL — 7-step injection sequence targeting 0.x

ALL LAYERS + ZP APPLY TO EVERY TRANSFORMATION.
Partial de-AI-fying is not de-AI-fying.
TARGET: Score 0.x — undetectable on GPTZero, Originality.ai, Copyleaks, Winston AI.
```

---

## When to Use This Skill

Use when:
- Text was written by an AI and needs to sound human
- Writing uses AI vocabulary: "delve into", "leverage", "synergy", "utilize", "it's worth noting"
- Every paragraph starts with a transition word: "Furthermore", "Additionally", "Moreover"
- Em-dashes appear where commas or periods belong
- The tone is hollow, polished, and says nothing
- Bullet points outnumber actual sentences
- The text hedges everything: "It's important to note that...", "One might argue..."
- Headers appear in what should be conversational text
- The writing feels "complete" in a way no human would bother with
- AI score checkers flag it as AI-generated

---

## Quick Start

### Inline Text

Paste text directly after invoking. The skill will:
1. Score the input (AI probability estimate)
2. Identify all fingerprints present
3. Apply all 7 layers of transformation
4. Output clean human text
5. Show diff of what changed

### File Input

```bash
# Process a file
python {baseDir}/scripts/deaify.py --input path/to/file.txt --output path/to/output.txt

# Score only (no rewrite)
python {baseDir}/scripts/deaify.py --score-only path/to/file.txt

# Aggressive mode (maximum humanization)
python {baseDir}/scripts/deaify.py --aggressive path/to/file.txt
```

### Modes

| Mode | When to Use |
|------|-------------|
| **Standard** | Default. Fixes all AI patterns while preserving content fidelity |
| **Aggressive** | Maximum humanization. May alter phrasing significantly |
| **Vocabulary-only** | Just replaces banned words, no structural changes |
| **Score-only** | Returns AI probability score + fingerprint report, no rewrite |
| **Preserve-format** | Fixes language but keeps structure (lists, headers) intact |
| **LinkedIn** | LinkedIn posts: removes announcement openers, "Here's what I learned:", engagement beg, hashtag blocks |
| **Email** | Emails: removes "I hope this finds you well", "Please be advised", formal closers |
| **Twitter** | Tweets/threads: removes thread openers, "Hot take:", engagement farmers, "That's it!" endings |

---

## The 7 Transformation Layers

### Layer 1: Vocabulary Purge

Replace every word and phrase on the banned list with natural human equivalents.

**High-priority kills:**
- `delve into` → `look at`, `dig into`, `get into`
- `leverage` (as verb) → `use`, `tap into`, `take advantage of`
- `utilize` → `use`
- `synergy` → cut or rephrase entirely
- `it's worth noting` → cut entirely or "note that" or just say the thing
- `in today's X landscape` → cut the setup, start with the point
- `paradigm shift` → say what actually changed
- `game-changer` → say why it matters specifically
- `holistic approach` → say what the approach actually includes
- `moving forward` → cut or "from here", "going forward" only if needed
- `at the end of the day` → cut
- `circle back` → "follow up", "revisit"
- `deep dive` → "close look", "thorough review", "dig into"
- `pain points` → "problems", "frustrations", "issues"
- `robust` → "strong", "solid", "reliable", or cut
- `seamless` → say what's actually smooth about it
- `cutting-edge` → say what's actually new
- `state-of-the-art` → same as above
- `innovative` → say what the innovation is

**→ Complete 200+ word banned list: references/AI-VOCABULARY.md**
**→ Contextual replacements: assets/word-lists/ai-words.json**

---

### Layer 2: Sentence Structure Repair

Break AI sentence patterns that no human would naturally produce.

**Patterns to kill:**

| AI Pattern | Human Fix |
|------------|-----------|
| Every sentence is 15-25 words | Mix lengths — short punchy ones too |
| Sentences all start with subject | Vary: clause first, verb first, "So" |
| Triple structure: A, B, and C | Use two or drop to one with impact |
| Sentences end with neat summary | Let some thoughts trail or be incomplete |
| Perfect parallel structure | Break it occasionally — humans don't always |
| No sentence fragments | Add some. They work. |
| No contractions | Use can't, won't, it's, you're |
| Passive everywhere | Make it active — who did the thing? |

**→ Full sentence pattern guide: references/SENTENCE-PATTERNS.md**

---

### Layer 3: Structural Flattening

AI over-structures everything. Real humans write paragraphs.

**Kill on sight:**
- Headers in conversational text (emails, messages, short articles)
- Bullet lists that could be two sentences
- Bold on random phrases for no reason
- "Key Takeaways" sections at the end of every piece
- Numbered lists for non-sequential information
- Sub-bullets under bullets under bullets
- Table of contents in 400-word pieces
- "Introduction" and "Conclusion" headers in anything under 1,500 words

**When to keep structure:**
- Technical documentation where structure aids navigation
- Long-form content (1,500+ words) where headers genuinely help
- Actual instructions with real sequential steps
- Data-heavy content where tables serve a purpose

**The test:** Would a real person writing this email/post/article naturally use headers and bullets? If no — flatten it.

**→ Full structural guide: references/STRUCTURAL-PATTERNS.md**

---

### Layer 4: Tone Detox

Strip hollow, hedging, performatively-balanced AI tone.

**Kill these tone patterns:**

| Tone Pattern | What to Do |
|--------------|-----------|
| "It's important to note that..." | Say the thing. Cut the setup. |
| "One might argue..." | Say what you think. Not what "one" might think. |
| "There are many factors to consider..." | Name the actual factors. |
| "In conclusion, it is clear that..." | End with substance, not a recap announcement. |
| "This is a complex topic with many nuances..." | No. Just address the nuances. |
| "As we can see from the above..." | The reader can see. Cut it. |
| "It goes without saying..." | Then don't say it. Or say it without the prefix. |
| Over-balanced "on one hand... on the other hand" | Have an opinion. Qualify only if needed. |
| Constant reassurance ("great question!") | Cut all meta-commentary |
| Sign-off phrases ("I hope this helps!") | Cut unless explicitly friendly context |

**→ Full tone guide: references/TONE-AND-VOICE.md**

---

### Layer 5: Rhythm Reset

AI produces unnaturally perfect cadence. Human writing has rhythm variation, stumbles, and personality.

**What to fix:**
- Sentence length variance: introduce short punchy sentences
- Paragraph length: break up long uniform blocks
- Transition overload: "Furthermore", "Additionally", "Moreover" in sequence → use one or none
- Em-dash overuse: AI uses `—` where commas or periods belong
- Semicolons everywhere: real people rarely use them in conversation
- Perfect paragraph endings: let some sentences trail without a bow
- Overly formal opening lines: humans don't open with "In today's rapidly evolving landscape..."

**Human rhythm markers to add (sparingly):**
- Sentence fragments for emphasis
- "But." / "So." / "And." at sentence start occasionally
- Contractions throughout
- Occasional colloquial word (depends on context)
- Question to reader (but not every paragraph)

**→ Full rhythm guide: references/SENTENCE-PATTERNS.md#rhythm**

---

### Layer 6: Authenticity Injection

After removing AI patterns, the text can feel flat. Add human markers.

**What humans do that AI doesn't:**
- State opinions directly without hedging
- Use specific numbers and names instead of vague generalities
- Reference things that don't serve a perfect rhetorical purpose
- Have a consistent POV (not balanced-to-the-point-of-saying-nothing)
- Occasionally repeat themselves or over-explain something they care about
- End on a point, not a summary

**Authenticity checklist:**
- [ ] Does it have a clear perspective?
- [ ] Are there specific details (not "many studies show" but which studies)?
- [ ] Would you know this was written by a specific person with a specific view?
- [ ] Does it sound like it was written in one sitting, not assembled?
- [ ] Is any of it surprising or unexpected?

**→ Full authenticity guide: references/REWRITE-TECHNIQUES.md**

---

### Layer 7: Statistical Humanization (Beat the Detectors)

After all vocabulary and structural work, the text still needs to pass AI detectors that measure **perplexity** and **burstiness** — statistical properties of how predictable the writing is.

**Perplexity** = how predictable each word choice is. AI always picks the most probable next word. Human writing surprises.

**Burstiness** = variance in sentence length/complexity. AI writes uniformly. Humans burst — short, then long, then short.

**What to do:**

| Fix | How |
|-----|-----|
| Increase perplexity | Replace safe/expected verbs with unexpected ones. "Cut" instead of "reduce". "Fix the mess" instead of "address the issue". |
| Add specific details | Numbers, names, dates. Specific = unpredictable. Generic = AI. |
| Add idiomatic phrases | "Good problem to have", "at this point", "for what it's worth" — these are statistically surprising |
| Vary sentence lengths hard | After a 25-word sentence, write one under 8. No exceptions. |
| Add at least one fragment | "Worth it." / "Not ideal." / "Simple enough." — fragments are human |
| Personal voice markers | "I'd argue", "in my experience", "honestly" — AI never sounds like one person |
| No two paragraphs same length | Visual uniformity = algorithmic tell |

**→ Full statistical guide with detector-specific techniques: references/PERPLEXITY-BURSTINESS.md**

---

## Workflow

### Manual Rewrite (Default)

When given text to de-AI-fy:

```
Phase 1 — Scan & Score
  1. Read entire text
  2. Identify all AI fingerprints present (by layer)
  3. Estimate AI probability (1-10 scale)
  4. Report findings to user before rewriting

Phase 2 — Layer-by-Layer Transform
  1. Vocabulary purge (Layer 1) — 300+ banned words + phrases
  2. Sentence repair (Layer 2) — fragments, contractions, passive, structure
  3. Structural flatten (Layer 3) — headers/bullets → prose
  4. Tone detox (Layer 4) — hedging, hollow openers/closers, setups
  5. Rhythm reset (Layer 5) — sentence length variance
  6. Authenticity inject (Layer 6) — POV, specifics, human voice
  7. Statistical pass (Layer 7) — perplexity + burstiness optimization

Phase 3 — Zero-Point Protocol
  1. Run ZP-1 through ZP-7 (references/ZERO-POINT-PROTOCOL.md)
     ZP-1: Inject 1-2 unexpected verbs per paragraph
     ZP-2: Apply burstiness — verify sentence length variance
     ZP-3: Add one specific detail per claim paragraph
     ZP-4: Leave one thought slightly unresolved per 400 words
     ZP-5: Add 1-2 voice markers per 300 words
     ZP-6: Break topic-sentence structure in at least 1 paragraph
     ZP-7: Add 1-2 informal constructions per 500 words

Phase 4 — Final Check
  1. Run ZP checklist (references/ZERO-POINT-PROTOCOL.md#checklist)
  2. Re-read aloud: does it sound like one specific person?
  3. Target: 0.x — undetectable on GPTZero, Originality.ai, etc.
  4. If still feels flat: add more ZP-3 (specifics) and ZP-5 (voice)

Phase 4 — Output
  1. Present transformed text
  2. List what changed (summary, not exhaustive)
  3. Note anything left intentionally (if format was preserved)
```

### Automated Pipeline

**→ Full script documentation: references/REWRITE-TECHNIQUES.md#automated**
**→ Script usage: scripts/deaify.py**
**→ Pattern definitions: scripts/patterns.py**
**→ Scoring logic: scripts/score.py**

---

## AI Fingerprint Reference

### The 20 Core Tells

1. **The Em-Dash Spray** — using `—` constantly where `,` or `.` works fine
2. **The Vocabulary Repeat** — "leverage", "utilize", "delve", "tapestry", "vibrant" appearing more than once
3. **The Transition Flood** — "Furthermore", "Additionally", "Moreover" in every paragraph
4. **The Perfect Triple** — A, B, and C. Always three things. Always parallel.
5. **The Hollow Setup** — "It's important to note that..." before every key point
6. **The Balanced Nothing** — Every claim immediately qualified into irrelevance
7. **The Bullet Compulsion** — Everything converted into lists regardless of whether it needs to be
8. **The Header Addiction** — Headers on every paragraph of a 300-word piece
9. **The Landscape Opening** — "In today's [X] landscape..." at the start
10. **The Conclusion Announcement** — "In conclusion..." or "To summarize..."
11. **The Passive Blanket** — Agent erased: "It has been found that..." instead of "We found..."
12. **The Perfect Length** — Every paragraph is 3-4 sentences, every sentence 15-25 words
13. **The Poetic Overreach** — "tapestry of innovation", "beacon of hope", "realm of possibility"
14. **The LinkedIn Bro Format** — One sentence per line, emoji bullets, "Here's what I learned:"
15. **The Contrasting Pivot** — "It's not X, it's Y" — AI loves this structure
16. **The Manufactured Insight** — "What most people don't realize..." / "Here's the kicker:"
17. **The Qualification Pile-Up** — "crucial", "vital", "essential", "significant" all in the same paragraph
18. **The Engagement Beg** — "What do you think? Drop a comment!" at end of every post
19. **The Metronomic Rhythm** — No sentence under 15 words, no sentence over 25 — perfect uniformity
20. **The Hollow Compliment** — "Great question!" / "Absolutely!" / "Certainly!" before every answer

**→ Full detection guide with examples: references/DETECTION-SIGNATURES.md**
**→ Scoring rubric: references/SCORING-RUBRIC.md**

---

## Context-Specific Rules

Different content types need different treatment intensity. The score and the context determine how hard to apply each layer.

### Emails

**What to always kill:**
- "I hope this email finds you well" → cut entirely
- "I wanted to reach out to..." → just say what you're reaching out about
- "Please don't hesitate to contact me" → "Let me know if..."
- "I look forward to hearing from you" → cut or specify what you're looking forward to
- "Further to my previous email" → "Following up on..."
- Bullet lists for content that reads naturally as sentences

**What to keep:**
- Professional greeting (Hi, Hello, Dear)
- Sign-off (Best, Thanks, Regards)
- Structure when there are genuinely multiple distinct topics

**Intensity:** Medium. Preserve professionalism. Kill hollow phrases only.

---

### Blog Posts and Articles

**Full 6-layer treatment.** This is where AI writing is most visible and most damaging.

**Layer 3 (structural) is critical here:**
- Headers on posts under 800 words → flatten to prose
- "Key Takeaways" at the end → cut. The piece IS the takeaways.
- "In Conclusion" section → write a real ending instead
- Intro paragraph that lists what the post will cover → cut. Just cover it.

**Layer 6 (authenticity) matters most:**
- The piece should have a perspective
- Not every claim needs to be hedged
- The ending should be a point, not a summary

---

### Social Media (LinkedIn, Twitter/X, Instagram)

**Maximum compression. All filler out.**

**Instagram/Twitter:**
- Every sentence must carry weight
- No filler words at all
- No hedge phrases
- No transition openers
- Short. Direct. One main point.

**LinkedIn (the most AI-contaminated platform):**
- Kill ALL corporate speak
- No "thrilled to announce" — just announce
- No "I'm excited to share" — just share
- "Game-changer", "synergy", "innovative" → always cut
- No bullet point posts unless genuinely list content
- The emoji-line-break format is an AI tell — use sparingly or not at all
- End with a real thought, not "What do you think? Drop a comment below!"

---

### Slack and Internal Messages

**Casual mode. Full contraction conversion. Fragments welcome.**

**AI tells to kill first:**
- "I wanted to touch base regarding..."
- "Please ensure that..."
- "It is important that..."
- Bullet lists for anything that would be one or two sentences in speech
- Bold on random phrases

**Target register:** How you'd say it out loud in the office.

---

### Marketing Copy

**Amplify directness. Aggressively strip hedging.**

Marketing copy that reads like it was written by AI loses all persuasive power. Real marketing copy has:
- A bold claim, stated directly
- Specific benefits, not vague value propositions
- Real language, not corporate-speak
- Personality

**Kill first in marketing:**
- "Innovative solutions" → say what the solution actually does
- "Seamless experience" → say what's smooth about it specifically
- "Empowering your team" → say what the team can actually do with it
- "Transformative" → say what transforms
- "World-class" / "Best-in-class" → either prove it with specifics or cut

---

### Technical Documentation

**Lightest touch. Structure often needed. Focus on tone + vocabulary.**

Technical docs benefit from:
- Headers (navigation)
- Bullet lists (steps, parameters, options)
- Bold (key terms, warnings)
- Tables (comparison data)

What to still fix:
- Passive voice: "The function can be called by..." → "Call the function with..."
- Overcomplicated noun-stacking: "The implementation of the configuration initialization process" → "Setting up the config"
- "It is recommended that" → "We recommend" or "Use..."
- Filler setups: "In order to accomplish X, you will need to..." → "To do X..."

---

### AI Chat Responses (Agents, Chatbots)

**Full treatment. Everything goes.**

AI chatbot responses are the most heavily AI-patterned text in existence. Specific to kill:

```
Layer 4 first — tone is the primary tell in chat:
1. "Great question!" opener → cut, start with answer
2. "Certainly!" / "Absolutely!" → cut
3. "I hope this helps!" → cut
4. "Feel free to..." → cut
5. "I'd be happy to..." → cut, just do it

Then Layer 1 — vocabulary is heavy in chat:
- "Delve into" / "leverage" / "utilize" → replace
- Setup phrases → cut
- Transition openers → cut

Layer 2 — structure in chat responses:
- Match the user's register. If they were casual, be casual.
- Use contractions throughout
- Keep responses tight — chat is not documentation
```

---

## Operator Instructions (For Agents Using This Skill)

When called by another agent or automation:

```
INPUT FORMAT:
  Text content as string, optional context type

OUTPUT FORMAT:
  {
    "original_score": float (1-10),
    "final_score": float (1-10),
    "transformed_text": string,
    "changes_applied": list[string],
    "manual_items": list[string],
    "passes": boolean (score <= 3)
  }

PIPELINE:
  1. Score input
  2. Apply scripts/deaify.py pipeline
  3. If score > 5 after automated pass → apply LLM-guided rewrite
  4. Re-score
  5. Return result

THRESHOLDS:
  passes = final_score <= 3
  needs_manual = any [REWRITE:...] markers remain
```

---

## Layer Application by Mode

| Mode | L1 Vocab | L2 Sentence | L3 Structure | L4 Tone | L4b Platform | L5 Rhythm | L6 Auth | L7 Statistical |
|------|----------|-------------|--------------|---------|-------------|-----------|---------|----------------|
| vocab-only | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| preserve-format | ✓ | ✓ | ✗ | ✓ | ✗ | ✓ | ✗ | ✗ |
| standard | ✓ | ✓ | Guided | ✓ | ✗ | ✓ | Guided | Guided |
| aggressive | ✓✓ | ✓ | Guided | ✓✓ | ✗ | ✓ | Guided | Guided |
| linkedin | ✓ | ✓ | Guided | ✓ | LinkedIn | ✓ | Guided | Guided |
| email | ✓ | ✓ | Guided | ✓ | Email | ✓ | Guided | Guided |
| twitter | ✓ | ✓ | Guided | ✓ | Twitter | ✓ | Guided | Guided |
| full (LLM-guided) | ✓✓ | ✓✓ | ✓✓ | ✓✓ | All | ✓✓ | ✓✓ | ✓✓ |

Layers marked "Guided" require LLM judgment — handled when text is pasted directly to the skill.

---

## Edge Cases & Decisions

| Situation | Decision |
|-----------|----------|
| Technical writing that needs structure | Keep structure, fix vocabulary + tone only |
| Academic writing with formal register | Loosen tone minimally, focus on vocabulary |
| Marketing copy that should be bold | Amplify directness, strip hedging aggressively |
| Social media posts | Maximum compression, all filler out |
| Email to a client | Moderate. Keep professional, remove hollow phrases |
| Internal Slack/team messages | Casual mode, contractions, fragments welcome |
| Blog post | Full treatment, all 7 layers |
| Press release | Preserve some formality, but kill the worst offenders |
| AI chat responses | Full treatment — everything goes |

---

## Scoring Reference

| Score | Meaning | Action |
|-------|---------|--------|
| 0.x | Undetectable | Done. No further action. |
| 1-2 | Barely detectable | ZP pass only (references/ZERO-POINT-PROTOCOL.md) |
| 3-4 | Low AI signal | Layers 1-4 + ZP pass |
| 5-6 | Moderate AI signal | Full 7-layer + ZP pass |
| 7-8 | Heavy AI signal | Full 7-layer + ZP + authenticity injection |
| 9-10 | Textbook AI output | Reconstruct from scratch using ZP principles |

**→ Full scoring rubric: references/SCORING-RUBRIC.md**

---

## Resources

**→ Complete banned vocabulary (300+ words): references/AI-VOCABULARY.md**
**→ Sentence structure patterns: references/SENTENCE-PATTERNS.md**
**→ Structural flattening guide: references/STRUCTURAL-PATTERNS.md**
**→ Tone detox playbook: references/TONE-AND-VOICE.md**
**→ All AI fingerprints + severity: references/DETECTION-SIGNATURES.md**
**→ AI grammar constructions: references/GRAMMAR-PATTERNS.md**
**→ Humanization techniques: references/REWRITE-TECHNIQUES.md**
**→ Before/after examples: references/BEFORE-AFTER-EXAMPLES.md**
**→ AI probability scoring: references/SCORING-RUBRIC.md**
**→ Perplexity + burstiness (Layer 7): references/PERPLEXITY-BURSTINESS.md**
**→ Zero-Point Protocol (0.x targeting): references/ZERO-POINT-PROTOCOL.md**
**→ Platform-specific patterns (LinkedIn, email, blog): references/PLATFORM-PATTERNS.md**
**→ Main script: scripts/deaify.py**
**→ Pattern engine: scripts/patterns.py**
**→ Scorer: scripts/score.py**
**→ Banned word list: assets/word-lists/ai-words.json**
**→ Replacement map: assets/word-lists/replacements.json**
