# SENTENCE-PATTERNS.md — Sentence Restructuring Patterns

Restructuring templates for common AI sentence types. Apply during humanization pass.
Target distribution after restructuring: 30% short (<8 words), 50% medium (8–14 words), 20% long (15+).

---

## Pattern 1: Subject-Verb-Object → Invert, Fragment, or Embed

**Problem:** SVO is the default AI sentence structure. Consistent SVO creates robotic rhythm.
**Fix options:** Invert the structure, fragment it, or embed a dependent clause.

### Option A: Invert (Object first)
- Before: "I've spent three years building systems like this."
- After: "Three years building systems like this. That's what it took."

### Option B: Fragment for emphasis
- Before: "This approach saves significant time during the planning phase."
- After: "This approach saves time. A lot of it. Especially in planning."

### Option C: Embed a clause
- Before: "The founder rejected the proposal without reading it."
- After: "The founder — who hadn't read past page two — rejected it on the spot."

---

## Pattern 2: Parallel Structures → Vary 2 of Every 3

**Problem:** Three consecutive parallel sentences read like a list even when formatted as prose.
**Rule:** Never write more than 2 parallel structures in a row without a structural break.

### Before (3 parallel):
> I've seen teams get this wrong. I've seen executives ignore the data. I've seen founders blame the market.

### After (break the third):
> I've seen teams get this wrong. I've seen executives ignore the data. But founders — they blame the market. Every time.

### Techniques for breaking parallels:
- Drop the introductory phrase on the third item
- Use a fragment
- Add a short commentary sentence after the third
- Change the subject of the third sentence

---

## Pattern 3: Long Compound Sentences → Split, Em-Dash, or Two Sentences

**Problem:** Long compound sentences strung together with "and", "but", or "so" read as AI-generated stream-of-consciousness.

### Option A: Split into two sentences
- Before: "We redesigned the onboarding flow and the completion rate went from 23% to 71% in six weeks."
- After: "We redesigned the onboarding flow. Completion went from 23% to 71% in six weeks."

### Option B: Em-dash for dramatic pause
- Before: "The proposal was perfect on paper but it missed the one thing the client actually cared about."
- After: "The proposal was perfect on paper — but it missed the one thing the client actually cared about."

### Option C: Turn the conjunction into a sentence opener
- Before: "The strategy was sound and the team executed well but the timing was off."
- After: "The strategy was sound. The team executed well. But the timing was off."

---

## Pattern 4: Passive → Active Conversion

**Problem:** Passive voice removes the actor and softens accountability. AI overuses it.
**Rule:** Convert all passive constructions unless the actor is genuinely unknown or unimportant.

### Passive markers to find:
- "was [verb]ed" → "I / we / they [verb]ed"
- "had been [verb]ed" → was done in the past — name who did it
- "is being [verb]ed" → name who is doing it
- "were given" → name who gave it
- "can be [verb]ed" → say who can do it

### Conversion examples:
| Passive | Active |
|---|---|
| The proposal was rejected. | They rejected the proposal. |
| Mistakes were made. | I made a mistake. |
| It was decided that... | We decided... / I decided... |
| The strategy had been misaligned. | The team had misaligned the strategy. |
| A decision needs to be made. | Someone needs to decide. |
| Feedback was provided. | The client gave feedback. |

---

## Pattern 5: Opening Word Variation

**Problem:** Repeated first words across paragraphs signal AI structure (often all start with "The", "This", or "I").
**Rule:** No word should open 3 or more paragraphs in a single post.

### Variation techniques:

**Adverbial openers** (time, place, manner):
- "Last Tuesday, ..."
- "Six months in, ..."
- "On the third call, ..."
- "After the rewrite, ..."

**Dependent clause openers:**
- "When the data came in, ..."
- "If you've ever dealt with this, ..."
- "Once the team aligned, ..."
- "Unless the brief changes, ..."

**Gerund (action noun) openers:**
- "Building this taught me something."
- "Selling to enterprise is different."
- "Reviewing 300 proposals gives you pattern recognition."

**Object-first openers:**
- "The data surprised me."
- "That rejection stung."
- "One client changed everything."

**Direct statement (fragment or assertion):**
- "Here's what I missed."
- "It wasn't the strategy."
- "Most teams skip this step."

---

## Pattern 6: Sentence Length Calibration

**Problem:** AI produces sentences of similar length in a narrow band (typically 11–15 words per sentence).
**Fix:** Deliberately introduce short sentences and longer winding sentences to break the band.

### Short sentence techniques (<8 words):
- Cut the subject if it's obvious: "It worked." → "Worked."
- Use a sentence fragment: "Not always." / "Until it wasn't." / "That's the trap."
- Name the outcome with no context: "We fixed it." / "She said no."

### Long sentence techniques (15+ words):
- Include a concrete example or specific detail mid-sentence
- Use an em-dash to extend: "The proposal was perfect — every metric, every projection, every risk mitigation clearly laid out."
- Add a qualifying clause: "It took three months longer than expected, not because the work was hard, but because no one owned the decision."

### Calibration checklist:
- Count sentences in the post
- Calculate word count per sentence
- Ensure at least 2 sentences < 8 words
- Ensure at least 1 sentence > 15 words
- No more than 3 consecutive sentences in the same length band

---

## Before/After Full Examples

### Example A: Standard AI paragraph → Humanized

**Before:**
> Many professionals struggle with time management in their daily work. It is important to prioritize tasks effectively. Additionally, establishing clear boundaries can help improve productivity. Furthermore, utilizing tools and systems can streamline workflows.

**After:**
> Most people don't have a time problem. They have a prioritization problem.
>
> And those are different. If you're overwhelmed, more hours won't fix it.
>
> What usually does: cutting the list, not managing it.

---

### Example B: Over-parallel structure → Varied

**Before:**
> I've learned that great teams communicate openly. I've learned that great teams move fast. I've learned that great teams own their mistakes.

**After:**
> Great teams communicate openly. They move fast.
>
> But the thing that separates the best ones from everyone else? They own their mistakes — publicly, specifically, without hedging.
