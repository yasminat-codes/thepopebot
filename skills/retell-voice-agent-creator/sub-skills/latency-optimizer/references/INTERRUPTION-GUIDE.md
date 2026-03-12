# Interruption Sensitivity Guide

## Parameter Overview

| Field | Value |
|-------|-------|
| Parameter name | `interruption_sensitivity` |
| Type | Float |
| Range | 0.0 to 1.0 |
| Default | 1.0 |
| API location | Agent configuration object |

The `interruption_sensitivity` parameter controls how easily the caller can interrupt
the agent while it is speaking. At 1.0 (default), any detected speech from the caller
will cause the agent to stop immediately. At 0.0, the agent will almost never stop
mid-response, regardless of what the caller says.

Retell's interruption detection uses a proprietary model that analyzes speech patterns,
intonation, and context — it is not a simple volume threshold. The sensitivity parameter
adjusts how aggressive this detection is.

---

## Range Breakdown

### Low Sensitivity (0.0 - 0.3)

The agent finishes nearly all responses without yielding. Callers cannot easily
break in, even with deliberate attempts.

- **Best for:** Automated announcements, legal disclaimers, compliance-required
  statements in debt collection, terms and conditions readings.
- **Risk:** Callers feel ignored. If they are trying to correct the agent or redirect
  the conversation, they cannot. Frustration builds quickly.
- **Use sparingly.** Most callers expect to be able to interrupt.

### Medium Sensitivity (0.4 - 0.6)

The agent completes most sentences but yields to clear, deliberate interruptions.
Background noise rarely triggers false interrupts.

- **Best for:** Noisy environments, agents that deliver important information that
  should be heard in full, survey questions, appointment confirmations.
- **Risk:** Fast-talking callers may feel the agent is ignoring their interjections.
- **This is the "noisy environment sweet spot."** High enough to allow real
  interruptions, low enough to reject noise.

### High Sensitivity (0.7 - 1.0)

The agent yields quickly to any detected speech. Conversations feel fluid and natural.

- **Best for:** Quiet environments, conversational agents, sales calls where the
  caller's input is more important than the agent's script.
- **Risk:** In noisy environments, background sounds trigger false interruptions.
  The agent stops mid-sentence, restarts, stops again — the number one complaint
  about voice agents in noisy settings.

---

## Environment-Based Recommendations

The caller's environment is the most important factor in choosing interruption
sensitivity. Noise creates false interruption signals.

| Environment | Examples | Recommended Range | Notes |
|-------------|----------|-------------------|-------|
| Quiet | Home office, private room, parked car | 0.80 - 1.0 | No noise to cause false triggers |
| Moderate | Open office, home with family, car driving | 0.65 - 0.80 | Occasional noise, need some resistance |
| Noisy | Restaurant, call center, construction | 0.45 - 0.65 | High noise, many false triggers |
| Very noisy | Outdoor event, factory floor, speakerphone in crowd | 0.30 - 0.50 | Must resist most noise |

---

## Common Problems and Solutions

### Problem: Agent Stops Mid-Sentence Repeatedly

**Symptom:** The agent says 3-5 words, stops, restarts from the beginning, stops again.
**Cause:** Interruption sensitivity too high (0.9-1.0) in a noisy environment.
**Fix:** Lower to 0.5-0.6 and enable `noise-and-background-speech-cancellation`.

### Problem: Caller Cannot Get a Word In

**Symptom:** The caller tries to correct the agent or answer a question, but the agent
keeps talking over them.
**Cause:** Interruption sensitivity too low (0.0-0.3) for a conversational use case.
**Fix:** Raise to 0.7-0.8. If the agent must deliver complete statements, consider
breaking long responses into shorter segments with natural pause points.

### Problem: Echo Causes Self-Interruption

**Symptom:** The agent seems to interrupt itself — it starts responding, then stops
as if it heard something, then starts again.
**Cause:** The caller is on speakerphone. The agent's own voice is picked up by the
caller's microphone and fed back, triggering the interruption detector.
**Fix:** Enable `noise-and-background-speech-cancellation` (which includes echo
suppression). Lower interruption sensitivity to 0.5-0.6.

### Problem: TV/Radio in Background Triggers Agent

**Symptom:** The agent responds to dialogue from a TV show or radio playing near the caller.
**Cause:** Background speech is being detected as caller speech.
**Fix:** Set denoising to `noise-and-background-speech-cancellation`. This mode
isolates the primary caller's voice and suppresses other speech sources.

---

## Interaction with enable_backchannel

Retell's `enable_backchannel` feature allows the agent to produce acknowledgment sounds
("mm-hmm", "I see", "got it") while the caller is speaking. This interacts with
interruption sensitivity in an important way.

| Backchannel | Interruption Sensitivity | Effect |
|-------------|-------------------------|--------|
| Enabled | High (0.8-1.0) | Natural, responsive conversation. Agent acknowledges and yields fluidly. |
| Enabled | Low (0.3-0.5) | Agent makes acknowledgment sounds but is hard to actually interrupt. Feels slightly odd. |
| Disabled | High (0.8-1.0) | Agent is silent while listening, then responds. Clean but less natural. |
| Disabled | Low (0.3-0.5) | Agent is silent and hard to interrupt. Feels like a one-way announcement. |

**Recommendation:** Enable backchannel for most conversational agents. It signals to the
caller that the agent is listening, which reduces the urge to interrupt with "hello? are
you there?" — one of the most common sources of unnecessary interruption.

---

## Use Case Specific Settings

| Use Case | Sensitivity | Reasoning |
|----------|-------------|-----------|
| Sales (objection handling) | 0.80 - 0.90 | Let callers interrupt naturally during objections |
| Appointment setter | 0.75 - 0.85 | Balanced — agent confirms, caller corrects |
| Customer support | 0.70 - 0.80 | Agent often explains steps, slight resistance helps |
| Receptionist | 0.75 - 0.85 | Professional, responsive to caller needs |
| Debt collection | 0.55 - 0.70 | Must deliver compliance statements fully |
| Survey agent | 0.65 - 0.80 | Must finish reading questions before accepting answers |
| Personal assistant | 0.75 - 0.85 | Natural, responsive feel |
| Lead qualifier | 0.80 - 0.90 | Fast-paced, responsive to caller interest signals |
| Real estate | 0.75 - 0.85 | Conversational, responsive to questions |
