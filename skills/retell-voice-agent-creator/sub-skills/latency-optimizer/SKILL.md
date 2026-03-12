---
name: latency-optimizer
description: Optimizes voice agent response timing, interruption handling, noise suppression, and turn-taking for Retell AI agents. Tunes responsiveness, interruption sensitivity, denoising mode, STT settings, and silence detection. Use when agent is too slow, too fast, gets interrupted by noise, cuts off callers, or has awkward pauses.
allowed-tools: Read Write Bash(python3:*)
---

# Latency Optimizer

## Overview

Latency is the invisible factor that makes or breaks voice agents. A 200ms response
feels instant and natural. A 2000ms response feels like talking to someone on a bad
satellite connection. But going too fast is equally destructive — if the agent responds
before the caller finishes thinking, it feels aggressive and pushy.

This sub-skill tunes the timing parameters of Retell AI agents: how fast the agent
responds, how it handles interruptions, how it filters noise, and when it decides the
caller is done speaking. The goal is to make the agent feel like a natural
conversational partner, not a machine.

Base directory token: `{baseDir}` = the directory containing this SKILL.md.

---

## Quick Start

**Step 1: Assess the environment.**
Is the caller in a quiet office, a noisy restaurant, or on a mobile phone in traffic?
This determines denoising and interruption settings.

**Step 2: Identify the caller profile.**
Are callers elderly (need more response time), fast-talkers (need quick responses),
or mixed (need balanced defaults)?

**Step 3: Run the calculator.**
Execute `{baseDir}/scripts/latency-calculator.py` with the gathered info. It outputs
optimized settings as JSON.

```bash
python3 {baseDir}/scripts/latency-calculator.py \
  --use-case appointment-setter \
  --environment mixed \
  --caller-type normal
```

The script outputs a JSON object with all timing parameters ready for the Agent Config
Builder or direct API deployment.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `use_case` | string | Yes | Template name or description of the agent's purpose |
| `environment` | string | Yes | `quiet`, `noisy`, or `mixed` — caller's typical environment |
| `caller_type` | string | No | `elderly`, `fast-talker`, `normal` (default: `normal`) |
| `existing_agent_id` | string | No | Retell agent ID to fetch current settings and optimize |
| `boosted_keywords` | array | No | Industry terms to boost in speech recognition |

---

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `responsiveness` | float | Response speed: 0-1, default 1 (fastest). Each 0.1 decrease adds ~0.5s delay |
| `interruption_sensitivity` | float | How easily the agent is interrupted: 0-1, default 1 |
| `denoising_mode` | string | `no-denoise`, `noise-cancellation`, or `noise-and-background-speech-cancellation` |
| `end_call_after_silence_ms` | int | Milliseconds of silence before auto-hangup. Default 600000 (10 min) |
| `stt_mode` | string | Speech-to-text mode: `fast`, `accurate`, or `custom` |
| `vocab_specialization` | string | `general` or `medical` (English only) |
| `boosted_keywords` | array | Words to bias transcription toward |

---

## Human Timing Benchmarks

Understanding how humans time their conversations is essential for tuning voice agents.
These benchmarks come from conversation analysis research. See
[Latency Benchmarks](references/LATENCY-BENCHMARKS.md) for the full dataset.

| Response Type | Human Timing | Retell Responsiveness | Feels Like |
|---------------|-------------|----------------------|------------|
| Reflexive (yes/no, greetings) | 200-400ms | 0.95-1.0 | Snappy, attentive |
| Thoughtful (answering questions) | 600-900ms | 0.80-0.90 | Natural, considered |
| Complex (explaining, calculating) | 1000-1500ms | 0.70-0.80 | Thinking, careful |
| Too slow (any response) | >2000ms | <0.60 | Broken, laggy, frustrating |

The key insight: humans tolerate slower responses when the answer is expected to require
thought. A 1-second pause before a complex answer feels natural. A 1-second pause before
"yes" feels broken. Retell's turn-taking model handles some of this automatically, but
the `responsiveness` parameter sets the baseline.

---

## Phase 1: Assess Environment

The caller's environment determines noise handling and interruption sensitivity.
Getting this wrong causes the most common voice agent failures.
See [Denoising Guide](references/DENOISING-GUIDE.md) for detailed mode descriptions.

### Quiet Environment
**Examples:** Home office, private room, quiet car (parked).
**Characteristics:** Minimal background noise, clear speech, no competing voices.

**Settings:**
- `denoising_mode`: `no-denoise` or `noise-cancellation`
- `interruption_sensitivity`: 0.85-1.0 (can be high — noise won't cause false triggers)
- `stt_mode`: `fast` (clean audio needs less processing)

### Noisy Environment
**Examples:** Restaurant, call center, construction site, busy street, car with radio.
**Characteristics:** Significant background noise, competing voices, variable volume.

**Settings:**
- `denoising_mode`: `noise-and-background-speech-cancellation` (critical)
- `interruption_sensitivity`: 0.5-0.7 (low — prevent noise from interrupting the agent)
- `stt_mode`: `accurate` (noisy audio needs better processing)

### Mixed Environment
**Examples:** Open office, coffee shop, home with family, mobile phone in varying locations.
**Characteristics:** Unpredictable noise levels, occasional competing voices.

**Settings:**
- `denoising_mode`: `noise-cancellation` (balanced default)
- `interruption_sensitivity`: 0.7-0.85 (moderate — handle occasional noise)
- `stt_mode`: `accurate` (better to over-process than miss words)

### Environment Detection Heuristic

If the user does not specify the environment, infer from the use case:

| Use Case | Likely Environment |
|----------|-------------------|
| appointment-setter (medical, dental) | Quiet (callers at home/office) |
| appointment-setter (restaurant, salon) | Mixed (callers anywhere) |
| receptionist | Quiet to Mixed (office or lobby) |
| sales-agent | Mixed (callers at work or mobile) |
| customer-support | Mixed (callers anywhere) |
| debt-collection | Mixed (callers at home or mobile) |
| personal-assistant | Quiet (personal device) |
| survey-agent | Mixed (callers anywhere) |
| real-estate | Mixed to Noisy (callers at properties, in cars) |

---

## Phase 2: Tune Responsiveness

The `responsiveness` parameter controls how quickly the agent starts responding after
the caller stops speaking. It ranges from 0 to 1. The default is 1 (fastest possible).
See [Responsiveness Guide](references/RESPONSIVENESS-GUIDE.md) for the full breakdown.

### How Responsiveness Maps to Delay

Each 0.1 decrease from 1.0 adds approximately 0.5 seconds of wait time before the
agent responds. This is additive to Retell's built-in turn-detection processing time.

| Responsiveness | Approximate Added Delay | Total Perceived Delay |
|---------------|------------------------|----------------------|
| 1.0 | 0ms | ~400-600ms (turn detection only) |
| 0.95 | ~250ms | ~650-850ms |
| 0.90 | ~500ms | ~900-1100ms |
| 0.85 | ~750ms | ~1150-1350ms |
| 0.80 | ~1000ms | ~1400-1600ms |
| 0.70 | ~1500ms | ~1900-2100ms |
| 0.60 | ~2000ms | ~2400-2600ms (too slow for most use cases) |

### Recommendations by Caller Type

**Normal callers (default):**
- Use 0.90 for most agents. This adds ~500ms, which matches the natural "thoughtful
  response" timing humans expect.
- Fast-paced sales or outbound calls: bump to 0.95.
- Complex support or advisory: drop to 0.85.

**Elderly callers:**
- Use 0.70-0.80. Elderly callers speak more slowly, pause longer between thoughts,
  and need more time to process responses. A fast-responding agent feels overwhelming.
- The longer pause also prevents the agent from cutting in when the caller is still
  thinking mid-sentence.

**Fast-talker callers:**
- Use 0.95-1.0. These callers expect rapid back-and-forth. Slow responses feel
  broken to them.
- Combine with higher interruption_sensitivity so they can cut in naturally.

### Recommendations by Use Case

| Use Case | Responsiveness | Reasoning |
|----------|---------------|-----------|
| appointment-setter | 0.90 | Balanced — collecting info and confirming |
| sales-agent | 0.95 | Fast pace keeps energy up |
| customer-support | 0.85 | Thoughtful responses build trust |
| receptionist | 0.90 | Professional, efficient |
| personal-assistant | 0.85 | Natural, unhurried feel |
| lead-qualifier | 0.95 | Fast-paced outbound |
| survey-agent | 0.85 | Patient, gives time to think |
| debt-collection | 0.85 | Measured, professional pace |
| real-estate | 0.90 | Enthusiastic but not rushed |

---

## Phase 3: Configure Interruption Handling

The `interruption_sensitivity` parameter controls how easily the caller can interrupt
the agent mid-speech. It ranges from 0 to 1. The default is 1 (most easily interrupted).
See [Interruption Guide](references/INTERRUPTION-GUIDE.md) for the deep dive.

### How Interruption Sensitivity Works

Retell's interruption detection uses a proprietary model — it does not simply detect
silence breaks. It analyzes speech patterns, intonation, and context to determine
whether the caller is actually trying to interrupt or just making a noise.

Despite this intelligence, the sensitivity parameter adjusts the threshold:

| Sensitivity | Behavior | Best For |
|-------------|----------|----------|
| 0.9-1.0 | Very easily interrupted. Any speech from caller stops the agent. | Fast-paced conversations, callers who interrupt naturally |
| 0.7-0.8 | Moderately resistant. Agent finishes short phrases before yielding. | Most business calls, balanced experience |
| 0.5-0.6 | Resistant to interruption. Agent completes most sentences. | Noisy environments, important announcements |
| 0.3-0.4 | Very resistant. Agent rarely stops mid-sentence. | Extremely noisy environments, one-way messages |
| 0.0-0.2 | Almost never interrupted. Agent completes full responses. | Automated announcements, legal disclaimers |

### Interruption vs Environment Matrix

| Environment | Fast-Talker | Normal | Elderly |
|-------------|-------------|--------|---------|
| Quiet | 0.95 | 0.85 | 0.75 |
| Mixed | 0.85 | 0.75 | 0.65 |
| Noisy | 0.70 | 0.60 | 0.50 |

The key rule: **lower interruption sensitivity as noise increases.** In a noisy
environment, background sounds and other voices can trigger false interruptions,
causing the agent to stop mid-sentence repeatedly. This is the number one complaint
about voice agents in noisy settings.

### Special Cases

**Debt collection:** Use 0.6-0.7 regardless of environment. The agent often needs to
deliver complete statements about account status and legal requirements. Getting
interrupted mid-sentence on a compliance-critical statement is worse than slightly
slow turn-taking.

**Surveys:** Use 0.7-0.8. The agent needs to read full questions without being
interrupted by the caller's anticipatory responses.

**Sales objection handling:** Use 0.8-0.9. When handling objections, let the caller
interrupt naturally — it shows you're listening and responsive.

---

## Phase 4: Set Denoising Mode

Retell offers three denoising modes. The right choice depends entirely on the caller's
environment. See [Denoising Guide](references/DENOISING-GUIDE.md) for technical details.

### The Three Modes

**`no-denoise`**
- No audio processing. Raw audio goes to STT.
- Use when: Caller is in a perfectly quiet environment. Studio recording quality.
- Advantage: Zero processing overhead, fastest path.
- Risk: Any background noise will degrade STT accuracy and may trigger interruptions.

**`noise-cancellation`**
- Removes ambient noise (HVAC, traffic, music) but preserves all speech.
- Use when: Caller has background noise but no competing voices.
- Advantage: Clean audio for STT without removing speech from other people the caller
  might be interacting with.
- Best default for most use cases.

**`noise-and-background-speech-cancellation`**
- Removes ambient noise AND background speech from other people.
- Use when: Caller is in a call center, busy office, restaurant, or any environment
  where other people are talking nearby.
- Advantage: Only the primary caller's voice reaches STT.
- Risk: May occasionally filter the caller's own speech if they move away from the mic.
  Use with slightly lower interruption sensitivity to compensate.

### Decision Matrix

| Environment | Denoising Mode |
|-------------|---------------|
| Quiet office, home | `no-denoise` or `noise-cancellation` |
| Car, light traffic | `noise-cancellation` |
| Cafe, restaurant | `noise-and-background-speech-cancellation` |
| Call center | `noise-and-background-speech-cancellation` |
| Construction site | `noise-and-background-speech-cancellation` |
| Unknown / varies | `noise-cancellation` (safe default) |

---

## Phase 5: Configure STT & Keywords

Speech-to-text settings determine how accurately the agent understands the caller.
See [Turn-Taking Guide](references/TURN-TAKING-GUIDE.md) for how STT interacts with
turn detection.

### STT Mode

| Mode | Description | Best For |
|------|-------------|----------|
| `fast` | Optimized for speed. Slightly lower accuracy. | Clean audio, simple vocabulary, latency-critical |
| `accurate` | Optimized for accuracy. Slightly higher latency. | Noisy audio, specialized vocabulary, accuracy-critical |
| `custom` | Custom STT model. Requires additional configuration. | Enterprise deployments with specific needs |

**Default recommendation:** `accurate` for most agents. The latency difference between
`fast` and `accurate` is minimal (~50-100ms) and not perceptible to callers. The
accuracy improvement is significant, especially with industry-specific terms.

Use `fast` only when: the environment is guaranteed quiet, vocabulary is simple, and
every millisecond of latency matters (high-frequency outbound dialing).

### Vocabulary Specialization

| Setting | Description | When to Use |
|---------|-------------|-------------|
| `general` | Standard vocabulary model | All non-medical agents |
| `medical` | Enhanced medical terminology recognition | Medical offices, telehealth, healthcare support |

**Note:** `medical` specialization is English-only. For non-English medical agents,
use `general` with `boosted_keywords` for medical terms.

### Boosted Keywords

The `boosted_keywords` array biases the STT model toward specific words. This is
critical for proper nouns, industry jargon, and uncommon terms that the STT model
might otherwise misrecognize.

**What to boost:**
- Company name and brand names
- Product names and service names
- Industry-specific terminology
- Common caller names in your market
- Street names and neighborhoods (for real estate, delivery)
- Medical terms (if not using medical specialization)

**Example:**
```json
{
  "boosted_keywords": [
    "Bright Smile Dental",
    "Dr. Chen",
    "Dr. Patel",
    "Invisalign",
    "periodontal",
    "veneer",
    "crown lengthening"
  ]
}
```

**Limit:** Keep the list under 20-30 keywords. Too many boosted keywords can degrade
overall STT accuracy by biasing the model too heavily.

---

## Phase 6: Silence & Call Duration

These parameters control when the agent considers the call finished and how long
it will stay on the line.

### end_call_after_silence_ms

How long the agent waits in silence before automatically ending the call.

| Setting | Value | Use Case |
|---------|-------|----------|
| Default | 600000 (10 min) | Most agents — generous timeout |
| Short | 30000 (30 sec) | Outbound sales — if nobody responds, hang up |
| Medium | 60000 (1 min) | Standard business calls |
| Long | 300000 (5 min) | Support — caller might be troubleshooting |
| Maximum | 600000 (10 min) | Hold-heavy scenarios, elderly callers |

**Minimum value:** 10000ms (10 seconds). Setting it lower will cause premature hangups.

**Recommendations by use case:**
- Sales/lead qualification: 30000-60000ms. If the caller goes silent for 30 seconds on
  an outbound call, they are likely not engaged.
- Appointment setting: 60000ms. Callers may need to check their calendar.
- Customer support: 120000-300000ms. Callers may be following instructions and need
  time to perform steps.
- Debt collection: 60000ms. Professional and time-bounded.
- Survey: 30000-60000ms. If silence, they have likely lost interest.
- Personal assistant: 300000ms. Caller may be multitasking.

### Reminder Configuration

Retell supports reminders during silence:
- `reminder_trigger_ms`: Milliseconds of silence before sending a reminder. Example: 25000 (25 sec).
- `reminder_max_count`: How many reminders before giving up. Example: 2.

**Recommended reminder pattern:**
```json
{
  "reminder_trigger_ms": 25000,
  "reminder_max_count": 2
}
```
This sends a gentle "Are you still there?" after 25 seconds of silence, up to 2 times.
If the caller does not respond after 2 reminders, the silence timer continues until
`end_call_after_silence_ms` is reached.

---

## Template Optimization Profiles

Default timing settings for each template, assuming mixed environment and normal callers.
These are starting points — adjust based on specific environment and caller type.

| Template | Responsiveness | Interruption | Denoising | STT | Silence Timeout |
|----------|---------------|-------------|-----------|-----|-----------------|
| appointment-setter | 0.90 | 0.80 | noise-cancellation | accurate | 60000 |
| sales-agent | 0.95 | 0.85 | noise-cancellation | fast | 30000 |
| customer-support | 0.85 | 0.75 | noise-cancellation | accurate | 120000 |
| receptionist | 0.90 | 0.80 | noise-cancellation | accurate | 60000 |
| personal-assistant | 0.85 | 0.80 | noise-cancellation | accurate | 300000 |
| lead-qualifier | 0.95 | 0.85 | noise-cancellation | fast | 30000 |
| survey-agent | 0.85 | 0.75 | noise-cancellation | accurate | 60000 |
| debt-collection | 0.85 | 0.65 | noise-cancellation | accurate | 60000 |
| real-estate | 0.90 | 0.80 | noise-cancellation | accurate | 60000 |

---

## Real-World Scenarios

### Scenario 1: Noisy Restaurant Receptionist

**Input:** "Our restaurant receptionist agent keeps getting interrupted by kitchen noise
and background conversations. It stops mid-sentence and starts over."

**Diagnosis:**
- Environment: Noisy (restaurant with kitchen, other diners, music)
- Problem: Background noise triggers false interruptions
- Current likely settings: default interruption_sensitivity=1.0, no denoising

**Optimization:**
1. Set `denoising_mode` to `noise-and-background-speech-cancellation` — removes kitchen
   noise and other diners' conversations
2. Lower `interruption_sensitivity` to 0.55 — agent resists false triggers from noise
3. Set `stt_mode` to `accurate` — better transcription in noisy audio
4. Keep `responsiveness` at 0.90 — restaurant callers expect efficient service
5. Boost keywords: restaurant name, menu items, reservation system terms

**Output:**
```json
{
  "responsiveness": 0.90,
  "interruption_sensitivity": 0.55,
  "denoising_mode": "noise-and-background-speech-cancellation",
  "stt_mode": "accurate",
  "end_call_after_silence_ms": 60000,
  "boosted_keywords": ["Bella Vista", "prix fixe", "tasting menu", "OpenTable"]
}
```

**Resources Used:** [Denoising Guide](references/DENOISING-GUIDE.md),
[Interruption Guide](references/INTERRUPTION-GUIDE.md)

### Scenario 2: Elderly Patient Appointment Setter

**Input:** "We serve mostly elderly patients. The agent talks over them and responds
before they finish their sentences."

**Diagnosis:**
- Caller type: Elderly (slower speech, longer pauses, needs processing time)
- Problem: Agent responds too quickly, interprets mid-thought pauses as turn completion
- Current likely settings: default responsiveness=1.0, high interruption sensitivity

**Optimization:**
1. Lower `responsiveness` to 0.75 — adds ~1.25 seconds of wait time, matching the
   longer natural pauses elderly callers take between thoughts
2. Lower `interruption_sensitivity` to 0.65 — agent is more patient, does not cut in
3. Set `denoising_mode` to `noise-cancellation` — elderly callers often at home (quiet)
   but may have TV or radio in background
4. Set `stt_mode` to `accurate` — softer voices benefit from better processing
5. Set `end_call_after_silence_ms` to 120000 — elderly callers may need to get their
   calendar, find paperwork, or just take longer
6. Set `vocab_specialization` to `medical` — medical office context

**Output:**
```json
{
  "responsiveness": 0.75,
  "interruption_sensitivity": 0.65,
  "denoising_mode": "noise-cancellation",
  "stt_mode": "accurate",
  "vocab_specialization": "medical",
  "end_call_after_silence_ms": 120000,
  "boosted_keywords": ["Medicare", "Aetna", "Blue Cross"]
}
```

**Resources Used:** [Responsiveness Guide](references/RESPONSIVENESS-GUIDE.md),
[Latency Benchmarks](references/LATENCY-BENCHMARKS.md),
[Turn-Taking Guide](references/TURN-TAKING-GUIDE.md)

---

## Decision Trees

### Environment to Denoising

```
What is the caller's environment?
├── Quiet (home office, private room)
│   └── noise-cancellation (safe) or no-denoise (if guaranteed quiet)
├── Noisy (restaurant, call center, construction)
│   └── noise-and-background-speech-cancellation
└── Mixed / Unknown
    └── noise-cancellation (balanced default)
```

### Caller Type to Responsiveness

```
Who are the callers?
├── Elderly / slow speakers
│   └── 0.70-0.80 (patient, no rushing)
├── Normal / general public
│   └── 0.85-0.95 (natural conversational timing)
└── Fast-talkers / professionals
    └── 0.95-1.0 (snappy, keeps pace)
```

### Use Case to Interruption Sensitivity

```
What is the agent doing?
├── Delivering required statements (debt collection, legal)
│   └── 0.5-0.7 (must complete statements)
├── Reading survey questions
│   └── 0.7-0.8 (must finish questions)
├── Normal conversation (support, scheduling)
│   └── 0.7-0.85 (balanced)
└── Fast-paced dialogue (sales, lead qual)
    └── 0.8-0.95 (responsive to interruptions)
```

---

## Common Issues & Fixes

### Agent Cuts Off Callers
**Symptom:** Agent starts responding before the caller finishes speaking.
**Cause:** Responsiveness too high (1.0) for callers who pause mid-thought.
**Fix:** Lower responsiveness to 0.85-0.90. For elderly callers, 0.70-0.80.

### Agent Too Slow to Respond
**Symptom:** Awkward silence after the caller finishes speaking.
**Cause:** Responsiveness too low, or STT mode too slow.
**Fix:** Increase responsiveness to 0.90-0.95. Switch STT to `fast` if audio is clean.

### Agent Stops Mid-Sentence (Noise)
**Symptom:** Agent gets interrupted by background noise, restarts sentences.
**Cause:** High interruption_sensitivity + noisy environment without denoising.
**Fix:** Enable `noise-and-background-speech-cancellation`. Lower interruption_sensitivity to 0.5-0.6.

### Echo or Feedback Issues
**Symptom:** Agent hears its own voice and responds to it.
**Cause:** Caller using speakerphone without echo cancellation.
**Fix:** Enable `noise-and-background-speech-cancellation`. Lower interruption_sensitivity.

### Background Speech Triggers Responses
**Symptom:** Agent responds to other people in the room, not the caller.
**Cause:** Missing background speech cancellation.
**Fix:** Set denoising to `noise-and-background-speech-cancellation`. This mode isolates
the primary speaker's voice.

---

## Resource Reference Map

| Resource | Path | Used In |
|----------|------|---------|
| Responsiveness Guide | [references/RESPONSIVENESS-GUIDE.md](references/RESPONSIVENESS-GUIDE.md) | Phase 2 (responsiveness tuning) |
| Interruption Guide | [references/INTERRUPTION-GUIDE.md](references/INTERRUPTION-GUIDE.md) | Phase 3 (interruption handling) |
| Denoising Guide | [references/DENOISING-GUIDE.md](references/DENOISING-GUIDE.md) | Phase 1, Phase 4 (environment, denoising) |
| Turn-Taking Guide | [references/TURN-TAKING-GUIDE.md](references/TURN-TAKING-GUIDE.md) | Phase 5 (STT and turn detection) |
| Latency Benchmarks | [references/LATENCY-BENCHMARKS.md](references/LATENCY-BENCHMARKS.md) | Human timing reference |
| Latency Calculator | [scripts/latency-calculator.py](scripts/latency-calculator.py) | Quick Start (automated optimization) |
