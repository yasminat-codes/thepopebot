# Rewrite Techniques — How to Humanize

**Techniques for transforming AI text into human writing, by pattern type.**

---

## Technique Framework

Every rewrite follows this sequence:

1. **Identify** — spot the AI pattern
2. **Understand** — know why it's a tell and what it's trying to say
3. **Decompose** — break the AI structure into its core meaning
4. **Reconstruct** — rebuild using human patterns
5. **Verify** — re-read. Does any part still sound AI?

---

## Technique 1: Vocabulary Swap

The simplest transformation. Replace flagged words with natural equivalents.

**Process:**
1. Scan the text against the banned word list (references/AI-VOCABULARY.md)
2. For each hit, check context — which replacement fits?
3. Swap and read the surrounding sentence aloud
4. If the sentence still sounds off, restructure it

**Advanced vocabulary swap — when simple replacement isn't enough:**

Some AI phrases are so structurally embedded that word-swapping isn't sufficient. The whole sentence needs rebuilding.

**Example:**
> "To fully leverage the synergistic potential of this approach, teams should utilize holistic frameworks."

Simple swap gives: "To fully use the combined potential of this approach, teams should use comprehensive frameworks." — still sounds AI.

Reconstruction: "Teams that use this approach together get better results than those working in isolation."

**Rule:** When a sentence has 3+ flagged words, don't swap — reconstruct.

---

## Technique 2: The Deflation Cut

AI pads. Cut the padding without losing meaning.

**What to look for:**
- Introductory filler before the point
- Endings that summarize what was just said
- Transitions that announce rather than connect
- Qualifiers that add zero information

**Deflation operations:**

| Pattern | Cut Operation |
|---------|-------------|
| "It's important to note that [X]" | → "[X]" |
| "In order to [do X], you need to [Y]" | → "To [do X], [Y]" |
| "At the end of the day, [X] is what matters" | → "[X] is what matters" |
| "As we can see from the above, [X]" | → "[X]" |
| "Furthermore, it should be noted that [X]" | → "[X]" |
| "In conclusion, this demonstrates that [X]" | → This shows [X] |

**Test:** Remove the phrase. Does the meaning change? If no, cut it.

---

## Technique 3: Sentence Fragmentation

Break long AI sentences into varied lengths.

**Process:**
1. Find a sentence over 25 words
2. Identify the core claim
3. Break at natural boundaries
4. Vary: one long-ish sentence, one medium, one short

**Before:**
> "The implementation of automated testing frameworks across the development pipeline has consistently demonstrated its ability to reduce regression defects by identifying issues at an earlier stage of the development cycle."

**After:**
> Automated testing across the pipeline catches regression defects early. That's well-established. The earlier you catch something, the cheaper it is to fix.

**What changed:**
- 33 words → 3 sentences (21, 4, 12 words)
- Vague "demonstrated its ability" → direct claim
- Technical passive → direct statement
- Added opinion marker ("That's well-established") — shows the writer has a POV

---

## Technique 4: Active Voice Injection

Find the agent. Put them in the sentence.

**Process:**
1. Find passive constructions ("was done", "has been found", "is recommended")
2. Ask: who did this? Who found this? Who recommends this?
3. Put that agent first

**Examples:**

| Passive (AI) | Active (human) |
|-------------|----------------|
| "It has been determined that..." | "We determined..." / "The team determined..." |
| "The report was completed on time" | "[Name] finished the report on time" |
| "Mistakes were made" | "We made mistakes" |
| "It is recommended that you..." | "I recommend..." |
| "Further investigation is needed" | "We need to look into this more" |
| "This can be accomplished by..." | "You can do this by..." |
| "It was decided to..." | "We decided to..." / "[Name] decided to..." |

**When passive is OK:**
- When the agent is genuinely unknown ("The file was deleted")
- When the agent is irrelevant ("The package was delivered")
- Scientific writing where convention demands it
- When emphasizing the object, not the subject ("The CEO was arrested")

---

## Technique 5: Structure Compression

Collapse bullet lists and headers into prose.

**Bullet list compression:**

**Step 1:** Read the bullets as if they're sentences
**Step 2:** Find the natural connectors (and, but, so, because, which means)
**Step 3:** Write one or two sentences using those connectors
**Step 4:** If items are truly list-like (>4 discrete items), keep them; otherwise prose

**Example:**
> **Benefits of this approach:**
> - Reduces processing time
> - Lowers operational costs
> - Improves accuracy
> - Simplifies the workflow for all team members

→ "This approach cuts processing time and operational costs while improving accuracy — and the whole workflow gets simpler."

**Header removal:**

**Step 1:** Read the header
**Step 2:** Find the first sentence of the section under it
**Step 3:** Merge: the header's topic becomes the subject, the first sentence becomes a complete sentence

**Example:**
> **## Benefits of Remote Work**
> Remote work has been shown to increase individual productivity.

→ "Remote work tends to increase individual productivity."

The header is gone. The section starts directly.

---

## Technique 6: Opinion Injection

Give the text a perspective.

**AI writes without a POV.** It presents information. Human writing argues, recommends, disagrees, or at least has a clear lean.

**Process:**
1. Identify the core topic or claim
2. Ask: what does the writer actually think?
3. Find one place to state it directly
4. Remove the "it could be argued" or "some might say" wrapper

**Escalation levels:**

| Neutrality Level | Example | Fix |
|-----------------|---------|-----|
| Total neutrality | "Both approaches have merits and drawbacks." | Pick one. Say why. |
| Soft lean | "Approach A may be preferable in some cases." | "Approach A is better for X. Use B when Y." |
| Hedged opinion | "I think Approach A tends to work better." | "Approach A works better." |
| Direct opinion | "Approach A is the right call here." | ✓ This is the target |

**Important:** Don't manufacture opinions if the content doesn't call for them. Not every piece needs an opinion. Technical documentation shouldn't have one. But persuasive, analytical, or explanatory writing should take a stance.

---

## Technique 7: Specificity Injection

Replace vague AI generalities with real details.

**When to apply:**
- "Many studies show..." → If you know which studies, name them. If you don't, say "There's evidence that..." or restructure.
- "Companies like X have found..." → What did they find? Say it.
- "In recent years..." → What year? What happened?
- "A significant number..." → What number?

**If you don't know the specifics:**
Replace with honest language:
- "Many studies show..." → "Research consistently points to..." (slightly less vague, still honest)
- "As experts note..." → "The prevailing view is..." (position without false precision)
- Or cut the claim if you can't support it specifically

---

## Technique 8: Rhythm Variation

Introduce natural variation in sentence length and structure.

**The rhythm repair formula:**
After a sentence over 20 words, write one under 10.

**Implementation:**
1. Read through the text
2. Find any sequence of 3+ medium-length sentences
3. After the third, insert a short one — a point, a reaction, a consequence
4. This breaks the metronome effect

**Example:**
> "The new protocol requires teams to submit weekly reports detailing their progress, challenges encountered, and planned activities for the following week. These reports are then reviewed by project managers who provide feedback and guidance. This process has been designed to improve accountability and communication across the organization."

After technique 8:
> "The new protocol requires weekly progress reports — what got done, what got blocked, what's next. Managers review and respond. Simple, in theory."

The "Simple, in theory" fragment is intentionally short. It creates rhythm and implies a POV (it's not as simple as it sounds).

---

## Technique 9: Contraction Conversion

Convert formal uncontracted forms to natural contractions in appropriate contexts.

**Scan and replace in conversational writing:**

```
"it is" → "it's"
"they are" → "they're"
"do not" → "don't"
"cannot" → "can't"
"will not" → "won't"
"should not" → "shouldn't"
"does not" → "doesn't"
"I am" → "I'm"
"we are" → "we're"
"you are" → "you're"
"is not" → "isn't"
"are not" → "aren't"
"have not" → "haven't"
"has not" → "hasn't"
"would not" → "wouldn't"
"could not" → "couldn't"
"that is" → "that's"
"there is" → "there's"
"here is" → "here's"
"what is" → "what's"
"who is" → "who's"
```

**Exception:** Keep uncontracted for:
- Emphasis ("I will NOT do this")
- Formal/legal documents
- Academic writing

---

## Technique 10: The Closing Reconstruction

Replace AI endings with endings that land.

**AI endings:**
- Restated summary of what was just said
- Meta-announcement that the piece is ending
- Generic call to action ("I hope this helps!")
- Balanced nothing ("Overall, both approaches have merit")

**Human endings:**
- The strongest point, saved for last
- A question that opens thinking
- A concrete next step
- A direct, specific recommendation
- Something that reframes what came before

**Process:**
1. Read the last paragraph
2. Ask: what's the actual point the piece is making?
3. Is that point in the last paragraph? If yes — is it buried under filler? Cut the filler.
4. If the point isn't there — write one sentence that states it
5. Cut everything after it

---

## Automated Pipeline Reference

The `scripts/deaify.py` script applies Techniques 1, 2, 5, 9 automatically.
Techniques 3, 4, 6, 7, 8, 10 require LLM-guided rewriting.

**Automated pipeline:**
```bash
python {baseDir}/scripts/deaify.py --input file.txt --output output.txt
```

**Interactive pipeline (with LLM guidance):**
Paste text directly to the skill and request full de-AI-fy treatment.

**→ Script documentation: scripts/deaify.py**
**→ Pattern definitions: scripts/patterns.py**
