# Denoising Mode Guide

## Parameter Overview

| Field | Value |
|-------|-------|
| Parameter name | `denoising_mode` |
| Type | String enum |
| Values | `no-denoise`, `noise-cancellation`, `noise-and-background-speech-cancellation` |
| Default | Varies by setup |
| API location | Agent configuration object |

Denoising controls how Retell processes the caller's audio before sending it to
speech-to-text. The right mode depends entirely on the caller's environment. Getting
this wrong is the root cause of most voice agent quality complaints.

---

## Mode Details

### no-denoise

No audio processing is applied. Raw audio passes directly to the STT engine.

- **Latency impact:** None. Zero additional processing time.
- **Voice quality:** Perfect preservation — no artifacts, no distortion.
- **Best for:** Studio-quality calls, controlled quiet environments, internal testing.
- **Risk:** Any background noise degrades STT accuracy. HVAC hum, keyboard clicks,
  and distant traffic can all introduce transcription errors. Noise may also trigger
  false interruptions if `interruption_sensitivity` is high.
- **When to use:** Only when you can guarantee the caller is in a quiet environment
  with a good microphone. Practically, this means internal calls or premium setups.

### noise-cancellation

Removes ambient noise (HVAC, fans, traffic, music, keyboard typing) while preserving
all human speech, including speech from other people nearby.

- **Latency impact:** Minimal. Under 10ms additional processing in nearly all cases.
- **Voice quality:** Slight processing artifacts possible on very quiet speech, but
  generally imperceptible to callers.
- **Best for:** The safe default for most agents. Handles the majority of real-world
  calling environments effectively.
- **Risk:** Does NOT remove background speech. If the caller is in a room where other
  people are talking, those voices will still reach the STT engine and may cause
  confusion or false interruptions.
- **When to use:** Home offices, cars, moderate-noise environments, or when the
  caller's environment is unknown.

### noise-and-background-speech-cancellation

Removes ambient noise AND background speech from other people. Isolates only the
primary caller's voice.

- **Latency impact:** Minimal. Under 15ms additional processing. Not perceptible.
- **Voice quality:** May occasionally clip the caller's own speech if they turn away
  from the microphone or speak very softly. The speech isolation model must distinguish
  "primary speaker" from "background speaker," which is imperfect.
- **Best for:** Noisy environments with competing voices — restaurants, call centers,
  open offices, busy households, outdoor locations.
- **Risk:** Aggressive filtering may remove the caller's speech if they are far from
  the phone or speaking at the same volume as background speakers. Compensate by
  lowering `interruption_sensitivity` slightly (so filtered-out speech does not cause
  false end-of-turn detection).
- **When to use:** Any environment where other people are audibly talking near the caller.

---

## Recommended Mode by Environment

| Environment | Mode | Notes |
|-------------|------|-------|
| Quiet home office | `no-denoise` or `noise-cancellation` | Either works; noise-cancellation is safer |
| Home with family/TV | `noise-and-background-speech-cancellation` | TV dialogue and family speech cause issues |
| Private office | `noise-cancellation` | HVAC and building noise handled |
| Open office / coworking | `noise-and-background-speech-cancellation` | Coworker speech is the main threat |
| Car (windows up) | `noise-cancellation` | Road noise handled well |
| Car (windows down / traffic) | `noise-and-background-speech-cancellation` | Horns, sirens, other drivers |
| Restaurant / cafe | `noise-and-background-speech-cancellation` | Staff, other diners, kitchen noise |
| Call center | `noise-and-background-speech-cancellation` | Adjacent agents' speech |
| Outdoor / street | `noise-and-background-speech-cancellation` | Unpredictable noise sources |
| Construction / factory | `noise-and-background-speech-cancellation` | Extreme noise levels |

---

## Interaction with Interruption Sensitivity

Denoising and interruption sensitivity should be tuned as a pair.

| Combo | Effect |
|-------|--------|
| High denoising + High interruption sensitivity | Clean audio means interruption detection works accurately. Good for noisy environments where you still want responsive turn-taking. |
| High denoising + Low interruption sensitivity | Maximum noise resistance. Agent filters noise AND resists false interrupts. Best for extreme noise. |
| No denoising + High interruption sensitivity | Every sound triggers interruptions. Only use in perfectly quiet environments. |
| No denoising + Low interruption sensitivity | Raw audio but agent resists interruptions. Niche use — recording scenarios. |

**The golden rule:** If the environment is noisy, ALWAYS enable denoising BEFORE
lowering interruption sensitivity. Denoising removes the noise at the source. Lowering
interruption sensitivity just makes the agent ignore it — which also makes the agent
ignore the caller's real interruptions.

---

## Testing Recommendations

1. **Test from the actual target environment.** Do not test a restaurant agent from
   a quiet office. Call from the restaurant during service hours.
2. **Test with speakerphone.** Many callers use speakerphone, which amplifies echo
   and background noise. This is the hardest scenario for any denoising mode.
3. **Listen to STT transcripts.** After test calls, review the raw transcription in
   Retell's call analytics. If background noise or speech appears in the transcript,
   increase denoising.
4. **Watch for over-filtering.** If the caller's own words are missing from transcripts,
   the denoising is too aggressive for their setup. This is rare but possible with
   `noise-and-background-speech-cancellation` on very quiet callers.
