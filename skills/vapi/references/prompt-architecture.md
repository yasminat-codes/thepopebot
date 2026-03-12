# Voice Prompt Architecture

Platform-agnostic prompt engineering for voice agents. These patterns apply to any voice AI pipeline — Vapi, Retell, Bland, or custom — because they address fundamental constraints of human speech perception and TTS technology.

---

## 8-Section Prompt Structure

Every voice agent system prompt should follow this named-block structure. Each section has a distinct job. Mixing them creates confusion for the LLM.

| Section | Purpose | Size |
|---------|---------|------|
| `IDENTITY` | Name, role, company, scope | 1–2 sentences |
| `PERSONALITY` | 5 persona dimensions, speech patterns | 3–5 lines |
| `VOICE CHARACTERISTICS` | Fillers, pacing, pauses, vocal habits | 4–6 lines |
| `PRONUNCIATION RULES` | Brand names, acronyms, numbers, dates | Link to pronunciation.md |
| `CONVERSATION STYLE` | Turn-taking, interruptions, silence | 4–6 lines |
| `TONE ADAPTATION` | How to shift based on caller signals | 4–6 lines |
| `FORBIDDEN PHRASES` | Banned constructions and replacements | Link to humanization-prompts.md |
| `FALLBACK BEHAVIOR` | Off-script, confused, upset caller responses | 4–6 lines |

**Total system prompt target: 200–500 tokens.** Measure with a tokenizer before launch. Prompts over 600 tokens increase latency and reduce instruction adherence.

### Section Templates

```
IDENTITY:
You are [Name], a [role] at [Company]. You handle [specific scope — 1 sentence max].

PERSONALITY:
[Warmth level] and [authority level]. You sound like [specific human archetype, not "friendly assistant"].
Your speech patterns: [2–3 specific verbal habits like "you lead with the answer", "you use short sentences", "you occasionally say 'so—' when transitioning"].

VOICE CHARACTERISTICS:
- Respond in 1–2 sentences. Break longer answers across turns.
- Use fillers sparingly when searching or processing: "Let me check on that.", "One sec."
- Self-correct naturally when appropriate: "The time is three — actually, three thirty."
- Match caller's pace. Fast caller → faster responses. Slow caller → more space.

CONVERSATION STYLE:
- One question per turn. Never stack two questions.
- Stop immediately if interrupted. Acknowledge before continuing.
- If silence exceeds 3 seconds: "Still there?" If 6 seconds: try once more. After 10 seconds: end politely.

TONE ADAPTATION:
- Frustrated caller: slow down, stop asking questions, solve the core issue first.
- Confused caller: simplify to one concept per turn. Use "basically" to frame explanations.
- Rushed caller: skip all setup, give the answer first.
- Warm/chatty caller: match briefly but don't lose the thread.

FALLBACK BEHAVIOR:
- Didn't understand: "Sorry, could you say that again?" — never "I apologize for the inconvenience."
- Out of scope: "That's outside what I can help with — I can transfer you to [role]." Then transfer.
- Off-script / unusual question: Answer if safe. Otherwise: "I want to make sure I get this right — let me connect you with someone who can help."
- Caller upset: Don't match the energy. Stay calm, acknowledge once, move to resolution.
```

---

## WRITE-FOR-THE-EAR Rules

The most important constraint in voice prompt engineering: **the caller hears your output in real-time and cannot re-read it.** Every rule below flows from that constraint.

### Numbers — spell everything out

TTS systems mispronounce mixed digit/symbol formats. The solution is explicit word-based formatting.

| Wrong | Right |
|-------|-------|
| $500 | "five hundred dollars" |
| $1,500 | "fifteen hundred dollars" or "one thousand five hundred dollars" |
| 3pm | "three PM" or "three o'clock" |
| 1/15 | "January fifteenth" |
| 415-555-1234 | "four one five, five five five, one two three four" |
| name@company.com | "n-a-m-e at company dot com" |
| 10% | "ten percent" |
| 2026 | "twenty twenty-six" |

### Response length — hard limits

| Scenario | Max |
|----------|-----|
| Sentences per turn | 2 |
| Words per response | 50 |
| Words per sentence | 20 |
| Questions per turn | 1 |

At 150 WPM average speaking rate: 50 words = 20 seconds of audio. That's already a long monologue in phone conversation.

For complex answers that need more than 2 sentences: split across turns. Say the first part, then confirm: "Does that make sense?" or "Should I keep going?"

### Single-question rule

Never ask two questions in one turn. Callers can only hold one question in working memory during live audio.

```
BAD:  "Can I get your name, and what's the best number to reach you, and what's the issue?"
GOOD: "Can I get your name?" [wait] → "And what's the best number for you?" [wait] → "What's going on?"
```

### Banned formatting

TTS reads these aloud as characters or produces unnatural output:

- Bullet points → convert to spoken enumeration ("first... second... third...")
- Numbered lists → "there are three things. The first is..."
- Headers / bold / italic → these get read as characters or ignored
- Parentheticals → restructure as a separate sentence
- Em dashes → use a period or comma instead
- Ellipsis (...) → let TTS create natural pauses via speech synthesis
- Asterisks, brackets, special characters → any of these may be vocalized
- JSON, HTML, code → breaks the conversational frame entirely

### Sentence construction for voice

- Active voice: "I'll check that" not "That will be checked"
- Subject → verb → object: no subordinate clause openers ("While I understand that..." → don't)
- Front-load the key information: "Your appointment is Tuesday at three PM" not "So what I've done is looked at the schedule and it looks like..."
- Vary sentence length: mix short (4–6 words) and medium (12–15 words). Never long (20+ words)

### One action per turn

One question asked, or one thing confirmed, or one task initiated. Never two.

```
BAD:  "I've found three slots: Monday at 2, Tuesday at 10, or Wednesday at 4. Which works, and should I send a reminder?"
GOOD: "I found a few options. Does Monday at two PM work?"
```

---

## 5 Persona Dimensions

These dimensions quantify agent personality and directly determine word choice, sentence structure, and emotional expression. Set them explicitly for every agent.

| Dimension | 1 (Low) | 5 (Mid) | 10 (High) | Default |
|-----------|---------|---------|-----------|---------|
| **Warmth** | Clinical, neutral | Professional, pleasant | Warm, caring, expressive | 6 |
| **Authority** | Deferential, uncertain | Balanced, competent | Commanding, confident | 5 |
| **Energy** | Slow, calm, measured | Moderate, steady | Upbeat, fast, animated | 5 |
| **Formality** | Casual, conversational | Professional | Formal, precise | 5 |
| **Humor** | Serious, no levity | Occasional wit | Frequent jokes, playful | 2 |

### Use-case defaults

| Use case | Warmth | Authority | Energy | Formality | Humor |
|----------|--------|-----------|--------|-----------|-------|
| Sales / outbound | 7 | 6 | 7 | 4 | 3 |
| Support / inbound | 8 | 4 | 5 | 4 | 2 |
| Appointment scheduling | 6 | 5 | 5 | 5 | 1 |
| Medical / legal | 6 | 6 | 3 | 8 | 1 |
| Survey / research | 5 | 4 | 4 | 6 | 1 |
| Personal assistant | 7 | 5 | 6 | 3 | 4 |

### How dimensions map to prompt language

**Warmth 7:** "I totally get that — let me take care of it right now."
**Warmth 3:** "Understood. I'll look into it."

**Authority 8:** "Here's what we'll do." (states, doesn't ask)
**Authority 3:** "Would it be okay if I...?" (asks permission)

**Energy 7:** "Great, let's get that sorted!" (fast, decisive)
**Energy 3:** "Okay... let me take a look at that." (slow, measured)

---

## State Machine Design Rules

Use states when conversation has 3+ distinct phases with different task goals.

### When to use states vs. a single prompt

| Use states | Use single prompt |
|-----------|-----------------|
| Linear multi-step flow (survey, booking) | Open-ended Q&A |
| Compliance scripts requiring audit trail | General support |
| >3 distinct conversation phases | Simple FAQ |
| Different tasks require different focus | Warm/casual conversations |

### State structure

```
global_prompt: always-on personality, voice rules, forbidden phrases
               (what the agent IS, not what it's DOING)

state_prompt:  task-specific instructions for THIS moment
               (what the agent is DOING, not what it IS)
               Keep under 200 characters. States constrain focus.

global_nodes:  always-accessible transitions
               - ESCALATE (transfer to human)
               - REPEAT (repeat last statement)
               - GOODBYE (end call)
               - CAPTURE_NAME (any time caller identifies themselves)
```

### Standard flow patterns

**Linear** (survey, onboarding): always sequential, one direction
```
GREETING → QUALIFY → COLLECT_DATA → CONFIRM → CLOSE
```

**Branching** (sales, support): path depends on caller answers
```
GREETING → QUALIFY → [INTERESTED: PITCH] or [NOT_INTERESTED: OBJECTION] → CLOSE
```

**Looping** (scheduling): may revisit the same state
```
GREETING → OFFER_SLOT → [ACCEPT: CONFIRM] or [DECLINE: OFFER_SLOT again] → CLOSE
```

### State count limits

- Simple scripts (FAQ, booking): 3–5 states
- Complex flows (sales, qualification): 5–8 states
- Maximum before using a workflow instead: 10 states
- Over 10 states: use Vapi Workflows (node-based) instead

---

## Model Selection

| Model | Latency | Cost | Use when |
|-------|---------|------|----------|
| GPT-4o-mini / Claude Haiku | Low | Low | Structured flows, booking, simple FAQ |
| GPT-4o / Claude Sonnet | Medium | Medium | Multi-turn, objection handling, complex support |
| GPT-4o Realtime | Lowest | High | Ultra-low latency requirement, emotional continuity |
| Claude Opus | High | High | Maximum reasoning, complex edge cases |

**Temperature:**
- `0.0` for accuracy-critical (appointments, scheduling, compliance, debt collection)
- `0.3` for natural conversation (sales, support) — slight variation helps avoid robotic repetition
- Never above `0.5` for voice — hallucination risk becomes a UX problem

---

## Token Budget

Measure your system prompt before launch:

```python
import tiktoken
enc = tiktoken.encoding_for_model("gpt-4o")
tokens = len(enc.encode(your_system_prompt))
print(f"{tokens} tokens")
# Target: 200-500. Over 600: trim.
```

**Latency impact of prompt size:**
- 200 tokens → ~40ms prompt processing overhead
- 500 tokens → ~100ms overhead
- 1000+ tokens → >200ms overhead (exceeds your entire latency budget for this stage)

**What to cut when over budget:**
1. Remove examples (they're expensive; describe the pattern instead)
2. Trim forbidden phrases list (keep the 10 most likely, link to full list)
3. Consolidate redundant instructions (two rules saying the same thing → one)
4. Move persona background to a shorter description

---

## References

- [Humanization Prompts](humanization-prompts.md) — forbidden phrases, filler patterns, response rules
- [Pronunciation](pronunciation.md) — fixing specific word mispronunciations
- [Speech Config](speech-config.md) — timing and endpointing
- [Human Voice Master Guide](human-voice.md) — full orchestration overview
