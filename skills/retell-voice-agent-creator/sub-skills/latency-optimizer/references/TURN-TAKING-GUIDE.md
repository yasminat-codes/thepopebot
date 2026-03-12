# Turn-Taking Guide

## How Retell Detects End of Turn

Retell uses a multi-signal approach to determine when the caller has finished speaking
and it is the agent's turn to respond. This is not a simple silence timer. The system
analyzes:

1. **Silence duration:** The most basic signal. A pause in speech may indicate the
   caller is done. But humans pause mid-thought constantly, so silence alone is
   unreliable.
2. **Speech patterns:** Falling intonation, completed sentence structure, and
   phrase-final lengthening all signal turn completion. Rising intonation (questions)
   is detected and processed differently.
3. **Semantic analysis:** The STT transcript is analyzed for completeness. "I'd like
   to book an appointment for..." is clearly incomplete. "I'd like to book an
   appointment for Tuesday at 3pm" is complete.
4. **Responsiveness parameter:** After Retell's model determines the turn is likely
   complete, the `responsiveness` parameter adds additional wait time. Lower
   responsiveness = longer wait before responding.

The combination of these signals makes Retell's turn detection significantly better
than simple silence-based systems. However, no system is perfect, and tuning is still
necessary for specific use cases and caller demographics.

---

## Key Parameters Affecting Turn-Taking

### responsiveness (0.0 - 1.0)

The primary lever for turn-taking timing. See the
[Responsiveness Guide](RESPONSIVENESS-GUIDE.md) for full details.

- Higher values: Agent responds sooner after detecting end-of-turn. Faster but more
  likely to jump in during mid-thought pauses.
- Lower values: Agent waits longer after detecting end-of-turn. Slower but more
  accurate turn detection for callers who pause frequently.

### interruption_sensitivity (0.0 - 1.0)

Controls how the agent handles the caller speaking while the agent is already talking.
See the [Interruption Guide](INTERRUPTION-GUIDE.md) for full details.

- Higher values: Agent yields immediately when the caller starts speaking. Good for
  natural conversation flow.
- Lower values: Agent continues speaking even when the caller tries to interrupt.
  Good for noisy environments or when the agent must deliver complete statements.

### end_call_after_silence_ms

How long the agent waits in complete silence before ending the call automatically.

- **Default:** 600000ms (10 minutes)
- **Minimum practical value:** 10000ms (10 seconds)
- This is a safety net, not a turn-taking parameter. It prevents zombie calls from
  staying open indefinitely.
- If this fires during a real conversation, it is set too low.

---

## Common Turn-Taking Problems and Fixes

### Problem: Agent Responds Too Early (Mid-Thought)

**Symptom:** The caller says "I need to reschedule my appointment because—" and the
agent jumps in with "Sure, I can help you reschedule!" before the caller explains why.

**Cause:** Responsiveness is too high (0.95-1.0). The brief pause after "because" is
interpreted as end-of-turn.

**Fix:**
- Lower `responsiveness` to 0.85-0.90 for general callers.
- Lower to 0.75-0.80 for elderly or deliberate speakers.
- The additional wait time lets the caller continue after natural pauses.

### Problem: Agent Waits Too Long to Respond

**Symptom:** The caller finishes speaking and there is 2-3 seconds of dead air before
the agent responds. Callers say "hello?" or think the call dropped.

**Cause:** Responsiveness is too low (below 0.70), or the LLM is slow to generate.

**Fix:**
- Raise `responsiveness` to 0.90-0.95.
- Check which LLM model is being used. Slower models (GPT-4) add inference latency
  on top of the responsiveness delay. Consider switching to a faster model.
- Check prompt length. Very long system prompts increase LLM inference time.

### Problem: Agent Interrupts During Natural Pauses

**Symptom:** The caller pauses to think or breathe, and the agent starts talking.
Differs from "responds too early" in that the agent is correctly detecting a silence
but the silence is a natural conversational pause, not a turn boundary.

**Cause:** Retell's semantic model cannot always distinguish "thinking pause" from
"finished speaking." This is more common with:
- Callers who speak slowly
- Complex questions that require thought
- Callers speaking a second language

**Fix:**
- Lower `responsiveness` to 0.80-0.85.
- Lower `interruption_sensitivity` to 0.70-0.75 so the caller can easily reclaim
  the floor if the agent does jump in.
- Enable `enable_backchannel` so the agent produces "mm-hmm" instead of a full
  response during ambiguous pauses.

### Problem: Caller Thinks Agent Disconnected

**Symptom:** Caller says "hello? are you still there?" during what should be normal
processing time.

**Cause:** No feedback during the agent's "thinking" time. The caller hears silence
and interprets it as a dropped connection.

**Fix:**
- Enable `enable_backchannel` for acknowledgment sounds.
- Ensure `responsiveness` is at least 0.85.
- Consider adding filler phrases to the agent's prompt: "Let me check on that for you"
  or "One moment please" for queries that require database lookups.
- Lower `end_call_after_silence_ms` is NOT the fix — that controls hangup, not feedback.

### Problem: Compound Questions Get Partial Answers

**Symptom:** Caller asks "What are your hours and do you accept walk-ins?" Agent only
answers the first question about hours.

**Cause:** The agent detected end-of-turn after "What are your hours" (which is a
complete question) and started responding before "and do you accept walk-ins?"

**Fix:**
- Lower `responsiveness` to 0.85 so the agent waits slightly longer for compound
  questions.
- Instruct the agent in its prompt to ask "Was there anything else you wanted to know?"
  after answering, which catches the missed second question.
- This is partially a prompt engineering problem, not just a latency problem.

---

## Cultural and Demographic Considerations

Turn-taking norms vary significantly across cultures and demographics. A setting that
feels natural to one group may feel aggressive or sluggish to another.

| Factor | Typical Pattern | Recommendation |
|--------|----------------|----------------|
| East Asian callers | Longer pauses between turns, less interruption | Lower responsiveness (0.80-0.85), lower interruption sensitivity |
| Latin American callers | Shorter gaps, more overlap, natural interruption | Higher responsiveness (0.90-0.95), higher interruption sensitivity |
| Elderly callers | Longer pauses, slower speech, mid-thought breaks | Lower responsiveness (0.70-0.80), lower interruption sensitivity |
| Young / tech-savvy callers | Fast speech, short pauses, comfortable with quick AI | Higher responsiveness (0.90-1.0) |
| Non-native speakers | Longer pauses (translating mentally), unusual intonation | Lower responsiveness (0.80-0.85), lower interruption sensitivity |
| Professional / business | Moderate pace, clear turn boundaries | Standard (0.85-0.90) |

**Important:** These are generalizations based on conversational analysis research.
Individual callers vary widely. When building an agent for a specific demographic,
test with actual callers from that demographic.

---

## Best Practices by Call Type

### Inbound Calls (Caller Initiates)

The caller has a purpose and knows what they want to say. They expect efficient
responses. Use slightly higher responsiveness (0.90-0.95) since callers tend to
have clear turn boundaries when they are driving the conversation.

### Outbound Calls (Agent Initiates)

The caller was not expecting the call. They may be confused, distracted, or
multitasking. Use slightly lower responsiveness (0.85-0.90) to give them time to
orient and formulate responses. First 30 seconds of the call need the most patience.

### Transfer Calls (Agent Receives Transfer)

The caller has already spoken to someone and may be frustrated by repeating
themselves. Use higher responsiveness (0.90-0.95) to feel responsive and efficient.
Low responsiveness after a transfer feels like "great, another slow system."

## Tool Preamble Pattern (Latency Masking)

When the agent calls an external function (calendar check, account lookup, booking), there is a 1-3 second processing delay. Without a preamble, this feels like the agent froze.

**Pattern:**
1. Detect tool call needed
2. Speak preamble phrase IMMEDIATELY (before starting tool call)
3. Tool runs during preamble delivery
4. Resume conversation with tool result

**Preamble Examples by Action:**
- Calendar check: "Let me check what's available for you..."
- Account lookup: "Let me pull up your account..."
- Booking: "Let me get that booked for you now..."
- Data entry: "I'm going to go ahead and update that..."
- Transfer: "Let me connect you with someone who can help with that..."

**Prompt Instruction:**
`"Before calling any function, speak a brief natural preamble phrase. Never call a tool in silence."`

**Latency Impact:** A 0.5-second preamble phrase masks up to 2 seconds of tool processing latency. Perceived wait time drops from 2 seconds to ~1.5 seconds (the preamble plays while the tool runs).
