# Responsiveness Parameter Guide

## Parameter Overview

| Field | Value |
|-------|-------|
| Parameter name | `responsiveness` |
| Type | Float |
| Range | 0.0 to 1.0 |
| Default | 1.0 |
| API location | Agent configuration object |

The `responsiveness` parameter controls how quickly the agent begins speaking after
it detects the caller has finished their turn. Each 0.1 decrease from 1.0 adds
approximately 500ms of deliberate wait time before the agent responds. This wait
time is additive to Retell's built-in turn-detection processing (~400-600ms).

---

## Range Breakdown

### Low Responsiveness (0.0 - 0.3)

Adds 3.5-5 seconds of delay. The agent feels extremely deliberate, almost sluggish.

- **Best for:** Rarely recommended. Only use for specialized scenarios where the agent
  must wait for the caller to compose long, multi-part thoughts.
- **Risk:** Callers will think the connection is broken or the agent has crashed.
- **Practical use:** Almost none. If you need delays this long, consider adding filler
  phrases ("Let me look into that for you...") rather than silence.

### Medium Responsiveness (0.4 - 0.6)

Adds 2-3 seconds of delay. The agent feels thoughtful and measured.

- **Best for:** Complex advisory topics where callers expect the agent to "think" before
  answering. Medical triage, legal intake, financial consultations.
- **Risk:** General callers may perceive sluggishness. Only use when the content
  justifies the pause.
- **Practical use:** Financial advisors, medical intake lines, legal consultations.

### High Responsiveness (0.7 - 1.0)

Adds 0-1.5 seconds of delay. The agent feels natural to snappy.

- **0.95-1.0:** Snappy and energetic. Best for sales, appointment setting, outbound
  campaigns where momentum matters. Risk of interrupting callers who pause mid-thought.
- **0.85-0.90:** Natural conversational pace. The sweet spot for most business agents.
  Matches the timing of a well-trained human receptionist.
- **0.70-0.80:** Patient and measured. Best for elderly callers, complex support
  scenarios, or callers who tend to speak slowly and pause between thoughts.

---

## Recommended Settings by Template Type

| Template | Responsiveness | Reasoning |
|----------|---------------|-----------|
| appointment-setter | 0.90 | Balanced — collecting info, confirming details |
| sales-agent | 0.95 | Fast pace maintains energy and engagement |
| customer-support | 0.85 | Thoughtful responses build caller trust |
| receptionist | 0.90 | Professional, efficient, no wasted time |
| personal-assistant | 0.85 | Unhurried, natural, attentive feel |
| lead-qualifier | 0.95 | Outbound pace — keep the caller engaged |
| survey-agent | 0.85 | Patient — gives callers time to formulate answers |
| debt-collection | 0.85 | Measured, professional, compliance-safe |
| real-estate | 0.90 | Enthusiastic but not pushy |

---

## Interaction with Interruption Sensitivity

Responsiveness and `interruption_sensitivity` work as a pair. They should be tuned
together, not independently.

| Combination | Effect | When to Use |
|-------------|--------|-------------|
| High responsiveness + High interruption | Fast, fluid conversation. Agent responds quickly and yields quickly when interrupted. | Sales calls, fast-paced support |
| High responsiveness + Low interruption | Agent responds fast but does not yield easily. Can feel aggressive — agent jumps in quickly and then refuses to stop. | Rarely recommended |
| Low responsiveness + High interruption | Agent waits patiently, then yields easily if interrupted. | Elderly callers, complex topics |
| Low responsiveness + Low interruption | Agent waits a long time and then delivers full responses. | Legal disclaimers, compliance messages |

**Rule of thumb:** If you lower responsiveness, also lower interruption sensitivity by
a proportional amount. A patient agent that also yields easily to interruption feels
natural. A patient agent that refuses to be interrupted feels robotic.

---

## Testing Methodology

1. **Recruit 3+ test callers** who match your target demographic. Internal team members
   who know the system do not count — they are too forgiving of timing issues.
2. **Run 5 test calls per setting.** Change responsiveness in 0.05 increments.
3. **Ask callers to rate:** "Did the agent feel too fast, too slow, or just right?"
4. **Listen to recordings.** Pay attention to moments where the agent cuts in early
   (responsiveness too high) or where there is awkward dead air (too low).
5. **Check the analytics.** Retell's call analytics show response latency per turn.
   Look for outliers — turns where the agent took >2 seconds indicate the caller said
   something the model found complex, and the responsiveness delay compounded with
   LLM inference time.
6. **Iterate.** Start at 0.90, adjust by 0.05 based on feedback, and re-test.

## begin_message_delay_ms (Critical for Natural Greeting)

When an inbound call connects, the agent typically begins speaking immediately. This sounds unnatural — humans take a moment before speaking after picking up.

**Configuration:** `"begin_message_delay_ms": 300-500`

| Delay | Sounds Like |
|-------|-------------|
| 0ms | Robot picking up instantly |
| 200ms | Slightly rushed human |
| 500ms | Natural — person just picked up the phone |
| 800ms | Slightly slow — like they were busy |
| 1000ms+ | Too slow — caller wonders if connected |

**Recommendation:** 400-500ms for most templates. 600-800ms for debt collection (creates sense of deliberateness).

**Outbound calls:** Set to 0 — the agent initiates, so natural timing is controlled by the call connection.
