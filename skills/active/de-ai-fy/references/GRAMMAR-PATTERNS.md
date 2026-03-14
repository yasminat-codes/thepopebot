# Grammar Patterns — AI Grammatical Constructions

**AI grammatical fingerprints that survive vocabulary replacement. These are structural grammar tells, not vocabulary. They require sentence-level rewrites.**

---

## Overview

Vocabulary replacement catches word-level AI tells. Grammar patterns catch how AI builds sentences. A text can pass vocabulary checks and still read as AI because of these constructions.

These patterns are harder to auto-fix. They require LLM-guided rewriting (Layer 2).

---

## Pattern 1: The "Not Only X, But Also Y" Construction

**What it looks like:**
> "This approach is not only efficient, but also cost-effective."
> "The platform not only integrates with existing tools, but also provides seamless..."
> "Leaders must not only inspire their teams, but also cultivate a culture of..."

**Why AI uses it:** It signals "balanced analysis." AI generates it reflexively to show it considered both sides.

**Why it's an AI tell:** Real writers use it rarely. In AI text, it appears in almost every paragraph where two ideas connect.

**Fix:**
- Collapse to one strong claim: "This approach is efficient and cheap."
- Or rewrite entirely: "It's efficient. And it doesn't cost much."
- Never use twice in the same document.

**Detection:** `not only .{1,50} but also`

---

## Pattern 2: "While X, Y" Openers

**What it looks like:**
> "While remote work offers flexibility, it also presents challenges for team cohesion."
> "While the technology is impressive, there are important considerations to keep in mind."
> "While this approach has its merits, it's important to recognize the limitations."

**Why AI uses it:** Forces artificial balance. AI is trained to present both sides.

**Why it's an AI tell:** Humans write their actual opinion. They don't constantly balance every claim with a concession opener.

**Fix:**
- Take a position: "Remote work is good for individuals and rough on team cohesion. Both things are true."
- Or: "The technology works. The real question is whether your team will actually use it."
- Cut the "while" opener entirely — start with the real point.

**Detection:** `^[Ww]hile .{1,80},` (sentence-starting "While")

---

## Pattern 3: Gerund-Heavy Bullet Lists

**What it looks like:**
> - Implementing robust processes
> - Leveraging cutting-edge tools
> - Fostering a culture of innovation
> - Optimizing team performance
> - Enhancing stakeholder engagement

**Why AI uses it:** Bullets with gerunds (-ing words) feel action-oriented and parallel. AI generates them on autopilot.

**Why it's an AI tell:** Every bullet starts with an "-ing" word → monotonous rhythm. Real humans mix constructions.

**Fix:**
- Break the gerund parallelism: vary how bullets start
- Convert to prose where possible
- If keeping bullets: make each one a full thought, not a noun phrase

**Detection:** 3+ consecutive bullets starting with `\b\w+ing\b`

---

## Pattern 4: The Definitional Chain

**What it looks like:**
> "Leadership is the ability to inspire, motivate, and guide teams toward achieving shared goals. Effective leaders understand that communication is key to building trust and fostering collaboration among team members."

**Why AI uses it:** AI defines terms, then immediately defines the adjacent terms, building an expanding chain of definitions. No original thought — just structured explanation.

**Why it's an AI tell:** Real writers assume the reader knows what leadership is. They don't define every term. They make a specific point.

**Fix:**
- Skip the definition. Start with the specific observation.
- "The managers who keep teams together during hard quarters share one habit: they make decisions quickly and visibly."
- Not: "Leadership is the ability to... effective leaders understand that..."

**Detection:** Pairs like `X is [the/a] [noun phrase]. [Adjective] X [verb] that...` — definitional → elaboration pattern.

---

## Pattern 5: The Parallel Triplet (AI Overuse)

**What it looks like:**
> "We are committed to innovation, excellence, and collaboration."
> "The solution helps teams communicate, collaborate, and achieve their goals."
> "Effective leadership requires clarity, consistency, and compassion."

**Why AI uses it:** Triplets feel conclusive and rhetorical. AI generates them constantly — especially in closers.

**Why it's an AI tell:** Used in almost every AI paragraph. One triplet per document is fine. Three or more = AI signal.

**Fix:**
- Use once if it lands. Cut the rest.
- Replace with a specific claim: "We ship fast and fix mistakes quickly."
- Don't end paragraphs with a triplet — it's the most common AI closing move.

**Detection:** `\b\w+, \w+, and \w+\b` — count frequency. >2 per 500 words = flag.

---

## Pattern 6: "It Is [Adjective] That" Constructions

**What it looks like:**
> "It is essential that organizations adapt to these changes."
> "It is crucial that leaders prioritize communication."
> "It is important that teams understand the implications."
> "It is worth noting that this approach has limitations."

**Why AI uses it:** Impersonal construction + importance signal = confident-sounding hedge. AI uses it to assert without committing.

**Why it's an AI tell:** It's a grammatical coward's way to make a claim. Humans just make the claim.

**Fix:**
- "Organizations need to adapt." Full stop.
- "Leaders should prioritize communication." Direct.
- Cut "it is [adjective] that" from every sentence.

**Detection:** `[Ii]t is (?:essential|crucial|important|vital|necessary|worth noting|clear|evident|apparent) that`

---

## Pattern 7: "By [Gerund], Organizations/Teams/Leaders Can..."

**What it looks like:**
> "By implementing these strategies, organizations can significantly improve productivity."
> "By fostering a culture of collaboration, leaders can unlock the full potential of their teams."
> "By leveraging cutting-edge technology, companies can streamline operations and drive growth."

**Why AI uses it:** The `by [doing X], [actor] can [achieve Y]` formula is a safe, logical-sounding construction. AI generates it constantly as a way to connect action to outcome.

**Why it's an AI tell:** It's a template. Humans don't naturally write in this formula for every claim.

**Fix:**
- Flip: "These strategies improve productivity." Direct.
- Or: "The teams that do [X] tend to [Y]." Specific and real.
- Never string two of these together in the same paragraph.

**Detection:** `^[Bb]y \w+ing .{1,60}, (?:organizations?|teams?|leaders?|companies|businesses?) can`

---

## Pattern 8: Subordinate Clause Stacking

**What it looks like:**
> "As organizations continue to navigate the complexities of an ever-evolving landscape, it becomes increasingly important to consider the multifaceted challenges that teams face as they adapt to new technologies and shifting market dynamics."

**Why AI uses it:** One long sentence with stacked subordinate clauses sounds sophisticated. AI uses this to create a sense of depth without saying anything.

**Why it's an AI tell:** No single sentence should require that much unpacking. Real writers break it up.

**Fix:**
- Split into 2-3 sentences with actual claims.
- "Companies are adapting to new tech. The problem isn't the technology — it's that most teams never get proper training for it."
- Sentence max: 25-30 words. If over, split.

**Detection:** Sentences > 40 words with 3+ subordinating conjunctions (`as`, `while`, `although`, `since`, `when`, `that`, `which`).

---

## Pattern 9: Empty Comparative ("More X Than Ever")

**What it looks like:**
> "Collaboration is more important than ever."
> "Communication has never been more critical."
> "The need for strong leadership has never been greater."
> "Now more than ever, organizations must..."

**Why AI uses it:** Creates urgency without evidence. AI uses this constantly because it sounds relevant without requiring specifics.

**Why it's an AI tell:** This claim is always unsubstantiated. If something is more important than ever, say why — with a specific reason from the present moment.

**Fix:**
- "Collaboration is important." (Drop the superlative if you can't support it.)
- Or: "Since the shift to remote work in 2020, alignment across timezones has become genuinely harder to maintain." (Actual reason.)
- Never use "more than ever" or "never been more [adjective]" without a specific supporting claim.

**Detection:** `more .{1,20} than ever`, `never been more`, `now more than ever`

---

## Summary Table

| Pattern | Detection Signal | Severity |
|---------|-----------------|---------|
| Not only X but also Y | `not only .* but also` | 🟠 High |
| While X, Y opener | `^While .{1,80},` | 🟠 High |
| Gerund bullet lists | 3+ bullets with `\w+ing` start | 🟡 Medium |
| Definitional chain | `X is the [noun]. [Adj] X [verb]...` | 🟡 Medium |
| Parallel triplet | `\w+, \w+, and \w+` > 2x/500 words | 🟡 Medium |
| It is [adj] that | `[Ii]t is (?:essential\|crucial\|important) that` | 🔴 Critical |
| By [gerund], X can... | `^By \w+ing.*can` | 🟠 High |
| Subordinate stacking | Sentence > 40 words, 3+ subordinators | 🟡 Medium |
| Empty comparative | `more .* than ever`, `never been more` | 🟠 High |

---

## Automated Detection Status

| Pattern | Auto-fixable? | Notes |
|---------|--------------|-------|
| Not only X but also Y | Partial | Can flag; rewrite requires LLM |
| While X, Y opener | Flag only | Rewrite requires knowing which side to keep |
| Gerund bullets | Flag only | Fix requires restructuring |
| Definitional chain | Flag only | Context-dependent |
| Parallel triplet | Count + flag | Can cut 2nd/3rd automatically |
| It is [adj] that | Auto-fix | Strip prefix, capitalize rest |
| By [gerund], X can | Flag only | Rewrite requires knowing the claim |
| Subordinate stacking | Flag only | Split requires judgment |
| Empty comparative | Auto-fix | Cut "more than ever", "now more than ever" |

Grammar patterns flagged but not auto-fixed: these get marked `[REWRITE: ...]` in the output for manual review.
