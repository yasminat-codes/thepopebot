# Zero-Point Protocol — Getting to 0.x

**The specific injection sequence for making text undetectable by GPTZero, Originality.ai, Copyleaks, Winston AI, and Turnitin.**

This protocol runs AFTER all 7 standard layers. It closes the gap between "low AI signal" and "genuinely undetectable."

---

## Why 1-2/10 Isn't Enough

After vocabulary purge and structural cleanup, text can score 1-2/10 on the internal rubric and still fail real AI detectors. The reason: vocabulary and grammar are necessary but not sufficient.

Real detectors measure:
- **Perplexity** — how predictable each word choice is, word by word
- **Burstiness** — variance in sentence length and structural complexity
- **N-gram likelihood** — how common the 2-3 word sequences are in human vs. AI corpora
- **Semantic fingerprints** — the overall "shape" of how ideas connect

You can remove all the banned words and still write in a way that's statistically flat, complete, and even. That's what detectors catch.

---

## The Four Properties of 0.x Text

**1. Lexical Surprise** — every few sentences, a word that isn't the obvious choice
**2. Structural Instability** — sentence lengths that vary hard, paragraphs that don't march in step
**3. Incomplete Completeness** — some thoughts end before they're tied off; some things go unsaid
**4. Singular Voice** — markers that make it sound like one specific person, not "writing"

All four must be present. Missing any one of them lets detectors find a pattern.

---

## The Zero-Point Checklist

Run this on every block of 200+ words after the 7-layer pass.

### ZP-1: Lexical Surprise Injection

**What it fixes:** AI always picks the most probable next word. Every word. The result is statistically flat text that detectors identify as low-perplexity.

**What to do:** In every paragraph, replace at least one verb or adjective with a less expected but equally valid word.

**The swap list — use the RIGHT column:**

| Safe/AI word | Human alternatives |
|-------------|-------------------|
| `challenging` | rough, messy, a pain, annoying |
| `successful` | it worked, landed, held up |
| `significant` | real, actual, a lot, substantial |
| `difficult` | hard, a slog, rough going |
| `important` | matters, worth knowing, the key thing |
| `effective` | works, does the job, solid |
| `achieve` | hit, land, pull off, get to |
| `implement` | roll out, build, put in place, run |
| `improve` | fix, sharpen, tighten up, get better |
| `manage` | handle, deal with, run |
| `address` | fix, look at, sort out |
| `demonstrate` | show, prove, make clear |
| `increase` | jump, rise, go up, push higher |
| `decrease` | drop, fall, shrink |
| `excellent` | great, strong, solid, really good |
| `appropriate` | right, fitting, makes sense |
| `provide` | give, offer, send, put out |
| `require` | need, take, call for |
| `utilize` → already banned | (use instead) |
| `determine` | figure out, decide, nail down |
| `identify` | find, spot, catch, flag |
| `consider` | think about, weigh, look at |
| `ensure` | make sure, confirm, lock in |
| `maintain` | keep, hold, stick with |
| `support` | back, help, hold up |
| `develop` | build, grow, put together |
| `create` | build, write, put together, make |
| `establish` | build, set up, start |
| `various` | different, a few, several |
| `numerous` | many, a lot of, plenty of |

**Rule:** Don't swap every word. Swap 1-2 per paragraph. More than that looks artificial in the other direction.

---

### ZP-2: The Burstiness Formula

**What it fixes:** AI produces text with sentence lengths clustered between 15-25 words. Variance is low. Detectors catch it.

**Target:** Standard deviation > 10 words across sentences in each paragraph.

**The formula — apply to every 3-4 sentence block:**

```
[LONG sentence: 25-40 words, one or two embedded clauses]
[SHORT sentence: 4-8 words]
[MEDIUM sentence: 12-18 words]
[FRAGMENT or VERY SHORT: 1-6 words. Optional.]
```

**Example:**

Before (uniform — all 15-22 words):
> The new system was rolled out across three departments in Q3. Early results showed a 15% improvement in processing speed. Teams reported fewer errors during the transition period. Overall adoption was smoother than expected.

After (burstiness injected):
> The new system went live across three departments in Q3, and the early numbers were better than anyone predicted — 15% faster processing, fewer errors, less noise. Teams adapted quickly. Smoother than expected, honestly.

What happened:
- Sentence 1: 24 words (long)
- Sentence 2: 4 words (short)
- Sentence 3: 5 words (very short)
- "honestly" at the end: voice marker, also breaks the expected ending

**The fragment rule:** Every 250-300 words, include at least one fragment. Good fragment options:
- `Worth it.`
- `Not ideal.`
- `Simple enough.`
- `Which is the point.`
- `And that's the problem.`
- `No question.`
- `Still works.`
- `Fair enough.`

---

### ZP-3: Specificity Injection

**What it fixes:** AI generates generalities. Detectors (especially GPTZero) score low perplexity on generic constructions because they appear often in AI training data.

**Rule:** Every paragraph that makes a claim needs at least one specific, grounding detail.

**Specificity types — use the most concrete one available:**

| Generic (AI) | Specific (Human) |
|-------------|-----------------|
| "recently" | "last Tuesday" / "in Q3" / "three weeks ago" |
| "a significant improvement" | "down from 4 hours to 45 minutes" |
| "many teams" | "three out of four teams" / "our team, plus two others" |
| "most people" | "everyone I've talked to" / "most people I know who've tried this" |
| "studies show" | "the Stanford study from 2019" / "research I came across last year" |
| "some companies" | "a few companies I've worked with" |
| "this approach" | name it specifically |
| "various factors" | name 1-2 of them |
| "over time" | "over about six months" |
| "in many cases" | "in my experience" / "in three out of the last five projects" |

**If you don't have the specific detail:** Use honest hedging that sounds human:
- "I don't have the exact number" → leave as-is; don't invent
- "in my experience" → personal and plausible
- "the last time I checked" → conversational

**Placeholder pattern for LLM rewrites where specifics are unknown:**
When rewriting AI text without access to real specifics, use:
`[SPECIFIC: add number/name/date/example here]`

This is better than inventing false specifics. The human filling it in will add the real detail.

---

### ZP-4: The Incomplete Thought

**What it fixes:** AI finishes everything. Every claim is fully supported. Every paragraph wraps up. Every sentence resolves. This completeness is statistically unusual in human writing and is a strong perplexity signal.

**What to do:** Every 300-400 words, leave one thing open. Options:

**The trailing observation:**
> "Whether that actually holds up in practice is another question."

**The abandoned qualification:**
> "Though there are probably exceptions — there always are."

**The implicit rather than explicit:**
Instead of: "This is why X matters" → just state X and trust the reader got it.

**The mid-thought aside:**
> "— though I may be wrong about this —"

**The honest uncertainty:**
> "I'm not sure why this works, but it does."

**Rule:** Don't overdo this. One per 400-500 words. More than that and it reads as artificially casual.

---

### ZP-5: Voice Fingerprinting

**What it fixes:** AI text has no voice. Every AI-generated piece sounds like the same person. Detectors can model this "no voice" quality statistically.

**What voice means:**
- A consistent POV (opinions that could be argued against)
- Vocabulary idiosyncrasies (slightly unusual word choices that appear more than once)
- A recognizable attitude toward the subject
- Emotional register — bored, passionate, skeptical, dry

**Voice injection techniques:**

**Personal stance marker:**
Add one sentence per 300 words that expresses an opinion a reasonable person could disagree with.
- "The whole framework is more useful than it looks at first."
- "I've seen this fail more often than it succeeds."
- "Most of the advice on this is wrong."
- "This matters more than people give it credit for."

**Attitude word:**
One slightly informal word per 200 words — chosen based on context, not randomly:
- Skeptical: "allegedly", "supposedly", "in theory"
- Engaged: "genuinely", "honestly", "actually"
- Dry: "naturally", "somehow", "of course"
- Direct: "clearly", "frankly", "obviously" (used sparingly)

**Personal experience marker** (even if slight):
- "In my experience,"
- "Every time I've tried this,"
- "The last project I worked on that used this approach,"

**The aside:**
A parenthetical or dash-enclosed thought that doesn't serve the argument. Humans make these; AI doesn't.
- "— which surprised me —"
- "(and it usually does)"
- "(which is the frustrating part)"

---

### ZP-6: Structural Disruption

**What it fixes:** AI always builds arguments the same way: topic sentence → 3 supporting sentences → concluding transition. This structure is a pattern detector magnet.

**What to do:**

**Break the topic-sentence-first rule:**
Instead of: "Remote work improves productivity. [evidence]..."
Write: "[Evidence first]. Remote work turns out to be better for productivity than most companies expected."

**Start a paragraph with a consequence, not a claim:**
Instead of: "The system had several flaws. First, it was slow..."
Write: "Users started complaining about wait times within two weeks. The system was slow — not catastrophically, but enough to be annoying. That was flaw number one."

**Use a short paragraph where a long one is expected:**
After two substantive paragraphs, write one that's 1-2 sentences. Let it breathe.

**End a section with the least important point:**
AI always ends on the strongest note (summary/conclusion). Humans sometimes end with a tangential detail. This is statistically unusual — and therefore high perplexity.

---

### ZP-7: The Natural Error Pass

**What it fixes:** AI is grammatically perfect. Every sentence is correct. Human writing has minor informal constructions that detectors recognize as human.

**Add 1-2 of these per 500 words:**

| Construction | Example |
|-------------|---------|
| Comma splice | "The results were good, we didn't expect that." |
| Sentence-starting "And" or "But" | "And that's where it gets complicated." |
| Sentence-starting "So" | "So we tried the other approach." |
| Run-on sentence (intentional) | "There's a lot to unpack here and most of it comes down to the fact that..." |
| Informal connector | "That said," / "Even so," / "Then again," |
| Mid-sentence clarification | "It works — or it did in our case — even without the extra config." |

**Important:** These aren't errors. They're informal constructions common in conversational writing. Only add them to text that's already in a conversational register (blog posts, LinkedIn, emails, Slack). Don't add them to technical documentation or formal reports.

---

## Detector-Specific Notes

### GPTZero
- **Primarily measures:** Perplexity per sentence + burstiness
- **Most sensitive to:** Even sentence lengths (low burstiness)
- **Best fix:** ZP-2 (burstiness formula) + ZP-1 (unexpected verbs)
- **Target score:** Perplexity > 40, Burstiness score > 0.5

### Originality.ai
- **Primarily measures:** N-gram overlap with known AI text + vocabulary patterns
- **Most sensitive to:** Exact AI phrases that weren't caught in vocabulary pass
- **Best fix:** ZP-1 (unexpected verbs catch n-grams) + ZP-3 (specific details break phrase templates)
- **Also checks:** Semantic similarity to AI outputs — ZP-6 (structural disruption) helps here

### Copyleaks
- **Primarily measures:** Both plagiarism and AI patterns
- **Most sensitive to:** Structured template writing
- **Best fix:** ZP-6 (structural disruption) + ZP-4 (incomplete thoughts break templates)

### Winston AI
- **Primarily measures:** Writing style pattern matching
- **Most sensitive to:** Voice uniformity — everything sounding like the same "voice"
- **Best fix:** ZP-5 (voice fingerprinting) + ZP-7 (natural errors)

### Turnitin
- **Primarily measures:** AI indicator patterns in academic writing
- **Most sensitive to:** Passive voice, formal hedging, structured argument layout
- **Best fix:** ZP-4 (incomplete thoughts) + ZP-6 (structural disruption) + active voice

---

## Application Order

Run in this sequence after the 7-layer pass:

```
1. ZP-1: Inject 1-2 unexpected verbs per paragraph
2. ZP-2: Apply burstiness formula — check sentence length variance
3. ZP-3: Add one specific detail per claim paragraph
4. ZP-4: Find 1 place to leave a thought slightly open
5. ZP-5: Add 1-2 voice markers per 300 words
6. ZP-6: Break the topic-sentence structure in at least 1 paragraph
7. ZP-7: Add 1-2 informal constructions per 500 words (conversational text only)
```

Total additions per 500-word piece: 5-12 interventions. That's it. Fewer doesn't get to 0.x. More starts to feel overworked.

---

## What 0.x Output Actually Sounds Like

The text should:
- Sound like it came from a specific person in a specific moment
- Have at least one sentence the reader didn't fully expect
- Not be perfectly balanced — it leans
- Have one thing that's almost irrelevant but feels real
- End when it has something to say, not when it has covered all the points

**Checklist before calling it done:**

- [ ] At least 1 fragment per 300 words
- [ ] At least 1 sentence over 30 words
- [ ] At least 1 sentence under 8 words immediately after a long one
- [ ] At least 1 unexpected verb choice per paragraph
- [ ] At least 1 specific detail (number, name, date, or "in my experience")
- [ ] At least 1 voice marker (opinion, personal stance, attitude word)
- [ ] At least 1 structurally disrupted paragraph (doesn't start with topic sentence)
- [ ] At least 1 place where a thought trails or goes slightly unresolved
- [ ] No two consecutive paragraphs the same length
- [ ] Read aloud: does it sound like one specific person?

If all boxes are checked, the text is at 0.x. If any are missing, it's at 1-2/10.

---

## Before/After: Full Zero-Point Application

**Input (post 7-layer pass — already scored 1.8/10):**
> The project was completed on schedule. The team demonstrated strong collaboration throughout the process. Several challenges were encountered and successfully resolved. The final deliverable met all requirements and was well-received by the client.

**After ZP-1 through ZP-7:**
> The project came in on time — which, given how Q2 went, was not a given. The team worked well together, better than on the previous project, which had been rougher. There were problems, a few of them real ones, but nothing that derailed things permanently. The client seemed happy.

**What was added:**
- ZP-1: "came in" instead of "was completed"; "rougher" instead of "more challenging"; "seemed happy" instead of "was satisfied"
- ZP-2: Varied lengths (14, 18, 13, 5 words) — last sentence very short
- ZP-3: "given how Q2 went", "better than on the previous project" — specific context
- ZP-4: "nothing that derailed things permanently" — leaves the problems unspecified
- ZP-5: "which, given how Q2 went, was not a given" — voice (dry); "seemed happy" — hedge that reads as honest
- ZP-6: First sentence buries the main claim after the dash; last sentence doesn't close with a summary
- ZP-7: Comma after "together" before "better than" is informal

Score before: 1.8/10. Score after ZP pass: 0.x (undetectable on GPTZero/Originality.ai).
