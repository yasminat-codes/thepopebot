# Perplexity & Burstiness — Statistical Humanization

**How AI detectors measure writing statistically, and how to beat them at the text level.**

---

## What Detectors Actually Measure

Modern AI detectors don't just look for vocabulary. They analyze the statistical properties of text at a character, word, and sentence level. The two primary metrics are perplexity and burstiness — and understanding them is how you write text that passes every detector, not just vocabulary checks.

---

## Perplexity — Predictability Score

**What it is:** How surprised a language model is by each word choice. Low perplexity = predictable text = AI signal. High perplexity = surprising text = human signal.

**Why AI scores low:**
AI picks the most statistically likely next word. It optimizes for coherence, which means every word is exactly what you'd expect. Clean, coherent, and predictable.

**Why humans score high:**
Humans make unexpected word choices. They use idioms, slang, personal references, unconventional phrasing. Their writing is full of minor surprises.

**What low perplexity looks like:**
> "The implementation of this approach will significantly improve team productivity and collaboration."

Every word here is the obvious next choice. "Implementation" → "of" → "this" → "approach" → "will" → "significantly" → "improve"... Each word is maximally predictable.

**What high perplexity looks like:**
> "This approach will absolutely crush the productivity problem — and honestly, the team will love it."

"Crush" is an unexpected verb. "Honestly" is an unexpected qualifier. "Will love it" is informal. The language model is more surprised by these choices.

---

## How to Increase Perplexity (Make Text Less Predictable)

### Technique P1: Unconventional Verb Choice

Replace safe, expected verbs with more specific, vivid, or unexpected ones.

| Safe/AI | Unexpected/Human |
|---------|-----------------|
| "improve performance" | "sharpen performance", "lift performance", "fix the performance gap" |
| "enhance user experience" | "make it easier to use", "stop frustrating users" |
| "leverage the tool" | "squeeze more out of the tool", "actually use the tool" |
| "address the issue" | "fix the mess", "deal with it", "put out the fire" |
| "facilitate collaboration" | "get people talking", "make teamwork actually work" |
| "implement the changes" | "roll this out", "make the switch", "ship the changes" |
| "navigate challenges" | "deal with the problems", "push through the hard parts" |
| "optimize processes" | "cut the waste", "make it faster", "simplify" |

### Technique P2: Idiomatic and Colloquial Language (Context-Appropriate)

Human writing — even professional writing — contains phrases that are semi-idiomatic.

**Examples:**
- "That's a good problem to have" (in appropriate contexts)
- "At this point, honestly..."
- "For what it's worth..."
- "Here's the thing though..."
- "And that's the catch"
- "Which is fine, actually"
- "Not ideal, but workable"
- "More or less"
- "Roughly speaking"
- "Give or take"
- "Fair enough"

**Warning:** Use sparingly and only where the register fits. Don't force idioms.

### Technique P3: Specific Details Over Vague Generalities

Specific details are statistically unpredictable because they're unique. Vague generalities are maximally predictable because they could appear anywhere.

| Vague (predictable) | Specific (unpredictable) |
|--------------------|--------------------------|
| "Many companies" | "We've seen this at three fintech startups" |
| "Studies show" | "A 2023 MIT study of 340 engineering teams found" |
| "Recently" | "In the last 6 months" |
| "Significant improvement" | "42% reduction" |
| "Some customers" | "About 1 in 5 customers who cancel" |

### Technique P4: Personal Voice Markers

First-person observations that reflect a genuine point of view are highly unpredictable.

**Examples:**
- "I'd argue that..."
- "In my experience..."
- "What I've seen is..."
- "The part that surprised me..."
- "What I actually think is..."
- "Honestly, the reason this matters is..."

These phrases can't be predicted because they represent a specific person's perspective, not an average of all writing on the topic.

### Technique P5: Self-Referential or Meta Observations

Occasional meta comments about the writing itself or the situation are unexpected:

- "This sounds obvious but it's worth saying anyway"
- "Bear with me here"
- "I'm going to skip the background and get to the part that actually matters"
- "This is one of those things that's hard to explain without an example"

---

## Burstiness — Sentence Variation Score

**What it is:** The variation in sentence complexity and length across a document. High burstiness = varied, unpredictable rhythm = human signal. Low burstiness = uniform rhythm = AI signal.

**Why AI scores low:**
AI generates sentences of consistent length and complexity. Every paragraph looks like every other paragraph. The rhythm is like a metronome.

**Why humans score high:**
Humans write in bursts. Short punchy sentences. Then a longer one that develops an idea more fully, potentially with a clause or two. Then another short one. The rhythm varies naturally based on what the writer is trying to convey.

**Statistical test for burstiness:**
Take 10 consecutive sentences. Calculate the word count of each. If the standard deviation is less than 5 words, burstiness is low. Human writing typically has standard deviations of 10–20+ words.

---

## How to Increase Burstiness

### Technique B1: The Short-Long-Short Pattern

After any long sentence (25+ words), follow with one under 8 words. Then a medium one.

**Example:**
> The deployment process went through three stages of testing, each one designed to catch a different class of failure before anything hit production. All three passed. The rollout was clean.

Three sentences: 30 words, 4 words, 5 words. High burstiness.

### Technique B2: Strategic Fragments

Sentence fragments are extremely human. They appear in human writing constantly. Never in AI writing.

**Effective fragments:**
- "Worth it."
- "Not always."
- "Simple enough."
- "Not ideal."
- "Big difference."
- "Which is the problem."
- "Usually, anyway."
- "Mostly."

**Usage rule:** One fragment per 200 words maximum. After a completed thought. For emphasis.

### Technique B3: Vary Opening Clause Length

Don't start every sentence at the same depth. Some sentences start with subject immediately. Some start with long context-setting clauses that run many words before arriving at the main verb.

**Short opening (direct):** "The system works."
**Medium opening:** "In most cases, the system works."
**Long opening:** "When the traffic spikes and the queue is backed up, the system works — it just takes longer than you'd want."

Mix all three.

### Technique B4: The Run-On (Sparingly)

Controlled informal run-ons are human. AI never produces them.

> "You run it, it checks the output, and if something's off it flags it — pretty simple."

This is a run-on. It's also how a real person would explain it casually. Use in informal contexts only.

### Technique B5: One-Sentence Paragraphs

AI paragraphs are always 3–4 sentences. Human writers drop single-sentence paragraphs for impact.

> The system passed all three tests.
>
> Then it failed in production.

The second paragraph is one sentence. It's abrupt. That's the point.

---

## Applying Both Metrics Together

High perplexity + high burstiness = undetectable.

**Before (low perplexity, low burstiness):**
> "The implementation of this comprehensive approach will significantly enhance team productivity and collaboration. Furthermore, it will facilitate better communication across departments. Additionally, the robust framework ensures seamless integration with existing workflows."

Three sentences, all 15–20 words. All predictable. All AI.

**After (high perplexity, high burstiness):**
> "This approach will cut wasted time across teams — and the communication problem that everyone's been complaining about gets fixed in the process. Seamless integration? It plugs directly into what you're already using. No new tools."

Different lengths: 27 words, 8 words, 3 words. Unexpected phrasing: "cut wasted time," "everyone's been complaining about," "No new tools." Burstiness and perplexity both high.

---

## Statistical Targets

After de-AI-fying, aim for:

| Metric | Target |
|--------|--------|
| Sentence length std deviation | > 10 words |
| Average sentence length | 14–16 words (not uniformly) |
| Shortest sentence | < 8 words |
| Longest sentence | > 25 words |
| Fragments present | At least 1 per 400 words (in informal writing) |
| Unique word ratio | > 60% of content words used once only |
| Contraction rate | > 15% of eligible constructions (conversational) |
| First-person voice | Present in opinion/narrative content |
| Specific numbers/names | At least 1 per 300 words |

---

## Detector-Specific Notes

### GPTZero
Measures both sentence-level perplexity and document-level burstiness. Highly sensitive to vocabulary. Burstiness variation across paragraphs is weighted heavily.

**Beat it by:** Sentence length variation (Technique B1-B3) and idiomatic phrases (Technique P2).

### Originality.ai
Focuses on token-level prediction probability. More sensitive to vocabulary patterns than burstiness.

**Beat it by:** Unconventional verb choice (Technique P1) and specific details (Technique P3).

### Copyleaks
Combines linguistic and semantic analysis. Looks at sentence structure and vocabulary simultaneously.

**Beat it by:** Full 6-layer treatment + burstiness techniques.

### Turnitin
Primarily plagiarism-focused but now includes AI detection using similar methods. Sensitive to both vocabulary patterns and structural uniformity.

**Beat it by:** Full treatment — especially structural variation and personal voice markers.

### Winston AI / Sapling
Classifier-based approaches that look at multiple features simultaneously.

**Beat them by:** Complete transformation across all 7 layers.

---

## Layer 7 Summary: Statistical Humanization

This is the 7th layer of de-AI-fy — layered on top of the original 6.

**Checklist:**
- [ ] Sentence length varies — shortest under 8 words, longest over 25
- [ ] At least one sentence fragment in informal/conversational pieces
- [ ] Unexpected verb choices used at least twice per 200 words
- [ ] Specific numbers or named examples instead of vague generalities
- [ ] Personal voice markers ("I'd argue", "what I've seen", "honestly")
- [ ] No two consecutive paragraphs are the same length
- [ ] Idiomatic phrases used at least once per 300 words (where register fits)
- [ ] No sentence has an "obviously predicted" word in every slot
