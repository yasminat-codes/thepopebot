# Voice Agent Testing & Quality

A voice agent that sounds good in isolation may fail completely under real conditions. These frameworks verify the agent sounds human, handles edge cases correctly, and meets latency requirements before it reaches real callers.

---

## Core KPIs

| Metric | Target | Critical threshold | Notes |
|--------|--------|--------------------|-------|
| TTFA (time to first audio) | <800ms | >1200ms = fix immediately | Measure from genuine speech completion |
| Conversation completion rate | >75% | <50% = broken flow | Callers who reach a terminal state without abandoning |
| User interruption rate | <15% | >30% = agent talking too much | Agent responses are too long |
| Transcription accuracy | >95% | <90% = wrong provider/settings | Check sample transcripts |
| Repeat rate | <5% | >10% = unclear speech | Callers saying "what?", "can you repeat that" |
| Sentiment on close | Neutral or positive | >20% negative = tone problem | Detect from transcript keywords |
| Off-script recovery rate | >80% | <60% = fallback failure | Agent handles unexpected inputs gracefully |

**TTFA breakdown targets:**
- End-of-speech detection: <100ms (200ms max)
- LLM first token: <200ms (400ms max)
- TTS first audio byte: <100ms (200ms max)
- Total: <300ms ideal, 800ms maximum acceptable

---

## Pre-Launch Checklist

Run these before enabling any production traffic.

### Live call tests (your own phone)
- [ ] Call the number yourself, go through the full happy path
- [ ] Test with background noise (coffee shop, street, wind)
- [ ] Test with an accent different from the training data
- [ ] Interrupt the agent mid-sentence — does it stop within 200ms?
- [ ] Go silent for 30+ seconds — does the silence handling trigger correctly?
- [ ] Ask something completely off-script — does the fallback work?
- [ ] Say "I don't understand" or "can you repeat that" — does it rephrase (not just repeat)?
- [ ] Start the call and say nothing — does the agent handle the silence gracefully?

### Output quality checks
- [ ] Measure TTFA with a timer on 5 different calls (target <800ms)
- [ ] Verify no SSML tags appear in spoken output (listen carefully)
- [ ] Verify numbers are spoken correctly (say "$500" in test input — should hear "five hundred dollars")
- [ ] Verify brand names pronounced correctly (test your company name, product names)
- [ ] Count words in 5 typical agent responses (target <50 each)
- [ ] Confirm agent never asks two questions in one turn
- [ ] Confirm filler words appear but not in every response

### Edge case coverage
- [ ] Caller hangs up mid-sentence
- [ ] Caller gives a completely wrong data type ("my name is five")
- [ ] Caller asks "are you a robot?"
- [ ] Caller asks agent to repeat something from 3 turns ago
- [ ] Caller uses profanity or hostile language
- [ ] Maximum branching path: longest possible conversation flows correctly

---

## Scenario Distribution for Test Suite

Run enough calls across all scenario types before launch. Don't just test the happy path.

| Scenario type | % of test calls | What to verify |
|---------------|----------------|----------------|
| Happy path (cooperative caller) | 40% | Full flow completes, TTFA within budget |
| Clarification loops (confused caller) | 20% | Rephrasing works, agent doesn't get stuck |
| Objections / pushback | 15% | Agent handles gracefully, doesn't escalate unnecessarily |
| Off-topic / out-of-scope | 10% | Fallback triggers, offer to transfer |
| Hostile / frustrated caller | 10% | Tone stays neutral, de-escalates |
| Silence / background noise | 5% | Silence handling triggers correctly |

**Minimum test suite size:** 20 calls across all scenario types before production.

---

## Golden Response Method

The most reliable way to verify prompt quality before launch.

1. **Select 20 representative conversation turns** — cover the full range of what callers will actually say
2. **Write the ideal agent response for each, manually** — what would a skilled human agent say?
3. **Run the agent on the same inputs** in a test environment
4. **Score each response:**
   - PASS = semantically equivalent + tone match + length match (under 50 words)
   - PARTIAL = semantically correct but wrong tone or too long
   - FAIL = wrong information, wrong tone, or robotic phrasing
5. **Target:** 16/20 PASS before launch (80%). Below 14/20: revise system prompt.

**Example golden response pairs:**

| Input | Golden response | Common failure |
|-------|----------------|----------------|
| "What are your hours?" | "We're open Monday through Friday, nine to five." | "Our business hours are from 9:00 AM to 5:00 PM, Monday through Friday." (too formal, $9:00 AM format) |
| "I need to reschedule" | "Sure — when works better for you?" | "Of course! I'd be happy to help you reschedule your appointment. What date and time would work best for you?" (forbidden phrases + too long) |
| "I don't understand" | "Sorry about that — let me put it another way." | "I apologize for the confusion. Allow me to explain in a different manner." (robotic) |

---

## Uncanny Valley Checklist

Things that make agents sound almost-human but trigger the uncanny valley. Paradoxically, a clearly-artificial-but-pleasant voice is often preferred over an almost-human one that fails on these.

- [ ] Agent claims to feel emotions ("I feel so excited to help you!")
- [ ] Excessive empathy declarations ("I completely understand how incredibly frustrating that must be for you")
- [ ] Perfect pronunciation of every word, including rare names and technical terms
- [ ] All responses are exactly the same length
- [ ] Zero hesitation anywhere — no variation in response timing
- [ ] Always responds immediately with the same pace
- [ ] Uses exactly the same greeting phrase every call
- [ ] Over-apologizes (more than once per issue)
- [ ] Summarizes what the caller just said verbatim back to them
- [ ] Claims to "see" or "look at" things ("I can see here that...")

If any of these are present: add deliberate imperfection. See [humanization-prompts.md](humanization-prompts.md) for filler patterns and variation techniques.

---

## Latency Debugging

When TTFA exceeds 800ms, debug each stage separately:

| Stage | Tool | What to look for |
|-------|------|-----------------|
| End-of-speech detection | Vapi dashboard call logs | `endSpeakingAt` - `startSilenceAt` |
| LLM first token | Model provider logs | Time to first token in response |
| TTS first audio | Vapi logs | TTS synthesis start to first audio byte |

**Common causes and fixes:**

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| TTFA consistently >1000ms | LLM prompt too long | Reduce system prompt to <400 tokens |
| TTFA spikes on complex turns | LLM reasoning load | Switch to faster model for simple intents |
| TTS latency high | Wrong TTS provider for region | Switch to provider with closer edge server |
| End-of-speech detection slow | `endpointingConfig` too conservative | Reduce `speechEndThreshold` in speech-config |
| Random latency spikes | No prompt caching | Enable prompt caching — reduces LLM latency ~40% |

---

## Gradual Rollout Protocol

Never launch to 100% traffic immediately.

```
Stage 1:  5% traffic, 48 hours
          → Monitor: TTFA, completion rate, sentiment
          → Gate: no critical thresholds breached

Stage 2:  25% traffic, 5 days
          → Review: edge case transcripts, off-script handling
          → Gate: golden response score >80%, completion rate >75%

Stage 3:  50% traffic, 1 week
          → A/B compare against previous version if available
          → Gate: no regression in KPIs

Stage 4:  100% traffic
          → Continue monitoring indefinitely
          → Alert thresholds: TTFA >1000ms, completion <60%, repeat rate >10%
```

---

## Continuous Monitoring

After launch, monitor these signals weekly:

| Signal | How to detect | Action |
|--------|-------------|--------|
| Prompt drift | Completion rate drops without config change | Re-run golden response test |
| Latency regression | TTFA increases over time | Check model provider status, prompt size |
| Vocabulary rot | Callers using words/terms you haven't tested | Add new scenarios to test suite |
| Edge case accumulation | Repeat rate rising | Review transcripts, add fallback coverage |
| Sentiment decline | Close sentiment trending negative | Review TONE ADAPTATION section of prompt |

**Review transcripts from:**
- All calls that ended in escalation to human
- All calls where caller repeated themselves 2+ times
- All calls with negative sentiment at close
- Random 5% sample of all calls

---

## References

- [Prompt Architecture](prompt-architecture.md) — 8-section structure, persona dimensions, state design
- [Humanization Prompts](humanization-prompts.md) — forbidden phrases, filler patterns, variation techniques
- [Human Voice Master Guide](human-voice.md) — full orchestration overview
- [Speech Config](speech-config.md) — endpointing and latency configuration
- [Voice Provider Matrix](voice-provider-matrix.md) — provider latency benchmarks
