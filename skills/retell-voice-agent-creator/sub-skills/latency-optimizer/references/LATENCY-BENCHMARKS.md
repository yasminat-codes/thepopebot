# Latency Benchmarks

## Human Conversation Timing

These benchmarks come from conversation analysis research and represent what callers
subconsciously expect from any conversational partner, human or AI.

| Response Time | Perception | Notes |
|---------------|-----------|-------|
| 0 - 200ms | Reflexive | Feels like a prepared/scripted answer. Appropriate for greetings and simple acknowledgments. |
| 200 - 300ms | Instant | Average human response time in natural conversation. The gold standard. |
| 300 - 500ms | Natural | Still feels completely natural. Most callers cannot distinguish this from instant. |
| 500 - 800ms | Acceptable | Noticeable but not uncomfortable. Feels like the agent is "thinking." Appropriate for complex answers. |
| 800 - 1200ms | Noticeable delay | Caller is aware of the pause. Acceptable for complex queries but feels slow for simple ones. |
| 1200 - 2000ms | Uncomfortable | Caller starts to wonder if something is wrong. Feels like lag or a bad connection. |
| 2000 - 3000ms | Unacceptable | Caller assumes the connection dropped or the system froze. Will say "hello?" or hang up. |
| > 3000ms | Broken | Call is effectively lost. Caller will hang up or become frustrated beyond recovery. |

**Key insight:** Humans tolerate longer response times when the question was complex.
A 1-second pause after "What's your address?" feels broken. A 1-second pause after
"Can you explain the difference between your premium and standard plans?" feels like
the agent is composing a thoughtful answer. Retell's turn-detection model partially
accounts for this, but the `responsiveness` parameter sets the baseline.

---

## Retell Latency Components

Total perceived latency = STT + LLM inference + TTS + network overhead

| Component | Typical Range | What Controls It |
|-----------|--------------|------------------|
| Speech-to-text (STT) | 100 - 300ms | `stt_mode` (fast vs accurate), audio quality, denoising |
| Turn detection | 200 - 400ms | Built-in Retell model + `responsiveness` parameter |
| LLM inference | 200 - 800ms | Model choice, prompt length, response complexity |
| Text-to-speech (TTS) | 100 - 300ms | Voice provider, voice model, streaming vs batch |
| Network overhead | 50 - 150ms | Caller's connection quality, geographic distance |
| **Total typical** | **650 - 1950ms** | **All of the above combined** |

---

## Typical Latencies by LLM Model

Measured as time from end-of-caller-speech to start-of-agent-speech, with
responsiveness at 1.0 (no added delay), in a quiet environment.

| Model | Typical Total Latency | Best Case | Worst Case | Notes |
|-------|----------------------|-----------|------------|-------|
| GPT-4o-mini | 500 - 800ms | ~400ms | ~1200ms | Fastest mainstream option. Good for simple agents. |
| GPT-4o | 800 - 1200ms | ~600ms | ~1800ms | Better reasoning. Noticeable latency increase. |
| Claude 3.5 Sonnet | 700 - 1100ms | ~550ms | ~1600ms | Strong reasoning with moderate latency. |
| Claude 3.5 Haiku | 500 - 800ms | ~400ms | ~1200ms | Fast, good for straightforward tasks. |
| GPT-3.5 Turbo | 400 - 700ms | ~300ms | ~1000ms | Fastest but weakest reasoning. Legacy option. |

**Note:** These are approximate ranges. Actual latency depends on prompt length,
response length, server load, and time of day. Peak hours (US business hours) tend
to have higher latencies across all providers.

---

## Voice Provider Latency Comparison

TTS latency varies by provider and voice model. Retell supports multiple providers.

| Provider | Typical Latency | Quality | Notes |
|----------|----------------|---------|-------|
| Retell built-in voices | 100 - 200ms | Good | Optimized for Retell's pipeline. Lowest latency. |
| ElevenLabs | 150 - 350ms | Excellent | Best voice quality. Slightly higher latency. |
| OpenAI TTS | 100 - 250ms | Good | Fast with natural-sounding output. |
| Deepgram | 80 - 200ms | Good | Optimized for speed. |
| PlayHT | 150 - 300ms | Good | Wide voice selection. |

---

## Optimization Levers (Ranked by Impact)

From highest to lowest impact on total latency:

1. **LLM model selection** (saves 200-600ms): Switch from GPT-4o to GPT-4o-mini for
   simple agents. The reasoning difference rarely matters for appointment setters
   or basic support agents.

2. **Prompt length** (saves 100-400ms): Shorter system prompts = faster first-token
   time. Keep prompts under 2000 tokens when possible. Move reference data to
   function calls rather than stuffing it into the system prompt.

3. **Responsiveness parameter** (adjusts 0-2500ms): Not an optimization per se, but
   the most direct control over perceived latency. Set appropriately for the use case.

4. **Voice provider** (saves 50-200ms): Retell's built-in voices are fastest. Use
   ElevenLabs only when voice quality is a priority over speed.

5. **STT mode** (saves 50-100ms): `fast` mode saves a small amount vs `accurate`.
   Only switch to `fast` if every millisecond matters and audio quality is guaranteed.

6. **Denoising** (adds 5-15ms): Negligible impact. Never skip denoising to save
   latency — the quality degradation from noise far outweighs the tiny time saving.

---

## Target Latency by Use Case

| Use Case | Target Total Latency | Acceptable Max | Priority |
|----------|---------------------|----------------|----------|
| Sales / outbound | 600 - 900ms | 1200ms | Speed over accuracy |
| Lead qualifier | 600 - 900ms | 1200ms | Speed over accuracy |
| Appointment setter | 700 - 1100ms | 1500ms | Balance |
| Receptionist | 700 - 1000ms | 1300ms | Balance (efficiency matters) |
| Customer support | 800 - 1200ms | 1800ms | Accuracy over speed |
| Personal assistant | 800 - 1200ms | 1800ms | Accuracy over speed |
| Survey agent | 700 - 1100ms | 1500ms | Balance |
| Debt collection | 800 - 1200ms | 1500ms | Accuracy and compliance |
| Real estate | 700 - 1100ms | 1500ms | Balance |

---

## How to Measure

1. **Retell call analytics:** Every call includes per-turn latency metrics. Review
   these after test calls to identify slow turns.
2. **Test calls with stopwatch:** Have a test caller note perceived response time.
   Subjective perception matters more than raw numbers.
3. **Compare against benchmarks:** If average turn latency exceeds the "Acceptable Max"
   for your use case, investigate which component (STT, LLM, TTS) is the bottleneck.
4. **Check for outliers:** Average latency may be fine, but occasional 3-second turns
   destroy the caller's experience. Look at p95 and p99 latency, not just averages.
5. **Test at peak hours:** Run test calls during US business hours (10am-4pm ET) when
   LLM provider latency is highest. Do not base your tuning on off-peak test results.

## The 500-Token Prompt Rule

Every 100 tokens of system prompt adds approximately 50ms of LLM processing latency.

| Prompt Length | Added Latency | Impact |
|--------------|---------------|--------|
| Under 300 tokens | ~0ms | Optimal |
| 300-500 tokens | ~50-100ms | Acceptable |
| 500-800 tokens | ~100-200ms | Noticeable |
| 800-1200 tokens | ~200-350ms | Degraded |
| 1200+ tokens | ~350ms+ | Unacceptable |

**Solution:** Keep general_prompt under 500 tokens. Move detailed knowledge to:
- Dynamic context injection (per-call variables)
- Knowledge Base (retrieved on demand)
- State-specific prompts (only loaded when in that state)

## Streaming TTS

With streaming TTS, audio begins playing as soon as the first tokens generate — not after the full response. This dramatically reduces perceived latency.

First-word delivery (TTFW) matters more than total response time. Callers forgive a sentence that takes 1.5 seconds more than one that starts instantly but then pauses.

**Enable streaming by default.** Retell uses streaming TTS automatically for supported providers. ElevenLabs Flash v2.5 and Cartesia Sonic-3 have the fastest streaming TTFW.
