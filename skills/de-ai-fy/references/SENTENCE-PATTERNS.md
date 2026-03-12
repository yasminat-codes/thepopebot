# Sentence Patterns — AI Structures to Break

**How AI writes sentences, why they're detectable, and how to fix them.**

---

## Why AI Sentence Patterns Are Detectable

AI language models generate text by predicting the next token based on training data. This creates systematic patterns:

1. **Length regularity** — AI produces sentences of similar length, avoiding extremes
2. **Structural repetition** — the same grammatical structure appears across a paragraph
3. **Completeness bias** — AI rounds off every idea. Humans leave some thoughts open.
4. **Parallel compulsion** — AI loves parallel structure. Humans break it.
5. **Transition dependence** — AI connects sentences with explicit connectors. Humans don't.

---

## Pattern 1: Length Regularity

**What AI does:**
Every sentence runs 15–25 words. Paragraphs have 3–4 of them. Predictably "balanced."

**Detection test:**
Count word lengths across 5 consecutive sentences. If they're all within 5 words of each other, it's AI.

**The fix:**
Mix aggressively. After a long sentence, drop a short one. Then a medium one.

**Before (AI):**
> The implementation of this system requires careful consideration of multiple factors. Each factor must be evaluated against the overall project requirements. The team should document their findings throughout this process. This documentation will serve as a reference for future iterations.

**After (human):**
> Setting this up right takes some thought. You need to weigh each factor against the broader project goals — and write it down as you go, so the next person (or future you) has a record to work from.

---

## Pattern 2: Subject-Verb-Object Monotony

**What AI does:**
Almost every sentence starts with the subject. "The system does X. The team does Y. This process does Z."

**The fix:**
Vary the opening. Start with:
- A dependent clause: "When X happens, Y occurs."
- A prepositional phrase: "In most cases, the answer is..."
- An adverb: "Technically, this works. But practically..."
- A conjunction: "But", "And", "So" — humans do this, style guides be damned
- The verb: "Run this first. Then check the output."
- A question: "What does this actually solve?"

---

## Pattern 3: The Perfect Triple

**What AI does:**
AI loves to present three things. Always three. Always in parallel. "X, Y, and Z."

**Detection test:**
Count how often a sentence lists exactly three things in parallel structure. More than twice in 300 words = AI.

**The fix:**
- Break up the triple. Say two things, then add the third as its own sentence.
- Or go to four, unevenly weighted.
- Or just pick the one that matters most.

**Before:**
> This approach improves efficiency, enhances collaboration, and reduces operational costs.

**After:**
> This approach cuts operational costs and makes the team faster. Collaboration improves as a side effect.

---

## Pattern 4: Artificial Completeness

**What AI does:**
Every idea gets fully rounded off. Every paragraph ends with a neat summary or bow. Nothing is left unresolved.

**Why it's a tell:**
Humans leave things slightly open. They make a point without explaining why they made it. They end a paragraph before they've exhausted the topic.

**The fix:**
End some sentences/paragraphs before the "therefore" appears. Let the reader arrive at the conclusion.

**Before:**
> This method has been tested extensively, and the results consistently demonstrate that it outperforms alternatives. As a result, it is recommended as the primary approach for all future implementations.

**After:**
> This method has been tested extensively and consistently outperforms alternatives. It's the right approach to use from here out.

---

## Pattern 5: Contractions Avoidance

**What AI does:**
Defaults to uncontracted forms. "It is", "they are", "do not", "cannot", "will not" — especially in contexts where a human would absolutely use contractions.

**The fix:**
Use contractions freely in:
- Conversational writing
- Emails
- Blogs and articles
- Social media
- Any first-person voice

Keep uncontracted in:
- Formal legal/technical documents
- Academic writing
- When emphasis requires the full form ("I will not do this")

**Quick replacement scan:**
- `it is` → `it's` (usually)
- `they are` → `they're` (usually)
- `do not` → `don't` (usually)
- `cannot` → `can't` (usually)
- `will not` → `won't` (usually)
- `should not` → `shouldn't` (usually)
- `does not` → `doesn't` (usually)
- `I am` → `I'm` (in conversational)
- `we are` → `we're` (in conversational)
- `you are` → `you're` (in conversational)

---

## Pattern 6: Passive Voice Overuse

**What AI does:**
Agents disappear. Actions happen by themselves. "It has been determined that..." "Studies have shown..." "The decision was made to..."

**Why this matters:**
- Passive removes accountability and specificity
- It's vague in ways humans aren't naturally vague
- Real people name who did the thing

**The fix:**
Find the agent. Put it in the sentence.

| Passive (AI) | Active (human) |
|--------------|----------------|
| It has been found that X | We found X / Research shows X |
| It should be noted that | Note that / Worth knowing: |
| The decision was made to | We decided to / [Name] decided to |
| This can be accomplished by | You can do this by |
| It is recommended that | I recommend / We recommend |
| Mistakes were made | We made mistakes / [Who] made mistakes |
| The report was completed | [Name] finished the report |
| Further improvements are needed | We need to improve X |

---

## Pattern 7: Transition Flood

**What AI does:**
Connects every sentence to the previous one with an explicit transition word. "Furthermore", "Additionally", "Moreover", "In addition", "Consequently", "Therefore", "Thus" — one per paragraph minimum.

**The fix:**
Cut most transitions. Good prose implies connection without announcing it.

**When transitions ARE needed:**
- Genuine contrast: "But", "However" (sparingly)
- Genuine consequence: "So", "As a result"
- Time sequence: "Then", "After that", "Next"

**When to cut:**
- "Furthermore" almost always
- "Additionally" almost always
- "Moreover" — essentially never needed
- "In conclusion" / "To summarize" — always cut the prefix

---

## Pattern 8: No Fragments, No Run-ons

**What AI does:**
Every sentence is grammatically complete. Perfect subject, verb, object. Punctuated correctly. No fragments, no run-ons.

**Why it's a tell:**
Humans use fragments constantly for emphasis and rhythm. "Perfect grammar. Every time. Never a fragment" is the tell.

**The fix:**
Add fragments. Strategically.

**Examples of natural fragments:**
- "Worth considering."
- "Not ideal."
- "Simple enough."
- "The short version: it works."
- "Which is the problem."
- "Big deal."

**Run-ons** (used sparingly) can also read human:
> You run it, it checks the output, and if something's off it flags it — pretty simple.

---

## Pattern 9: Semicolon Overuse

**What AI does:**
Uses semicolons frequently to connect independent clauses in a "sophisticated" way.

**The fix:**
In most cases, break the semicolon into two sentences. Real people rarely use semicolons outside of lists.

| AI | Human |
|----|-------|
| "The process is efficient; it requires minimal oversight." | "The process is efficient. Minimal oversight needed." |
| "Results were positive; the team was pleased." | "Results were positive. The team was pleased." |

---

## Pattern 10: Hedging Constructions

**What AI does:**
Qualifies almost every claim. "This may suggest...", "It could be argued...", "In some cases...", "This tends to..."

**The fix:**
If the claim is true, state it. If it needs qualification, qualify specifically and briefly.

| Hedged (AI) | Direct (human) |
|-------------|----------------|
| "This may suggest that..." | "This suggests..." |
| "It could be argued that..." | "The argument is..." or just make the argument |
| "In many cases..." | "Often..." or be specific |
| "This tends to..." | "This does..." or "This usually..." |
| "There is some evidence that..." | "Evidence shows..." or cite it specifically |
| "One might consider..." | "Consider..." |

---

## Rhythm Reference

### Good Rhythm Indicators
- Sentences vary from 5 to 35 words
- Short sentences (≤10 words) appear at least once per 5 sentences
- Paragraphs vary from 1–6 sentences
- No two consecutive sentences start the same way
- Contractions appear in conversational sections

### Bad Rhythm Indicators (AI)
- All sentences 15–25 words
- 3-4 sentence paragraphs, uniform
- Every paragraph starts with "The" or subject
- "Furthermore"/"Additionally" appear multiple times
- No sentence under 10 words in 200+ word passage

---

## Quick Checklist

Before finishing a de-AI-fied piece, check:

- [ ] Sentence lengths vary — some short punchy ones exist
- [ ] At least some sentences start with non-subject openers
- [ ] Contractions used throughout (if conversational)
- [ ] No "Furthermore/Additionally/Moreover" sequences
- [ ] Active voice dominates — agents named
- [ ] At least one fragment exists (in conversational writing)
- [ ] Semicolons minimal or absent
- [ ] Claims stated directly, not hedged into nothing
- [ ] No perfect triples dominating every point
