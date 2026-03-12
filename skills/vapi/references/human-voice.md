# Human-Sounding Voice Agents — Master Guide

The complete system for building Vapi agents that pass as human. This file is the orchestrator — it routes to deeper references for each domain.

---

## The Three Systems You Must Understand

Most builders conflate three separate systems. Misunderstanding this causes most "still sounds robotic" failures.

| System | What It Does | How to Control |
|--------|-------------|----------------|
| **Filler Injection** | Adds "um", "uh", "like" at the orchestration layer, before TTS | Dashboard toggle only (no API field as of 2026) |
| **Backchanneling** | Adds "yeah", "got it", "uh-huh" while the user is speaking | `backchannelingEnabled: true/false` |
| **LLM Fillers** | The LLM itself outputs filler words in its text | System prompt directives |

These are independent. Disabling one does not affect the others. All three must be configured deliberately.

---

## The Human Voice Stack (Priority Order)

Work through these in order. Each layer compounds the effect of the previous.

### Layer 1 — Voice Provider Choice
The most impactful decision. Wrong voice = no amount of prompting fixes it.

→ See **[voice-provider-matrix.md](voice-provider-matrix.md)**

### Layer 2 — Speech Configuration
How long the agent waits, how it detects end-of-turn, how it handles interruptions.

→ See **[speech-config.md](speech-config.md)**

### Layer 3 — System Prompt Engineering
What the LLM says and how it says it. Forbidden phrases, filler words, response length, emotional range.

→ See **[humanization-prompts.md](humanization-prompts.md)**

### Layer 4 — Pronunciation
Brand names, acronyms, unusual words, numbers, addresses.

→ See **[pronunciation.md](pronunciation.md)**

### Layer 5 — Fine-tuning (Audio Texture)
SSML pauses, flush syntax, emotion controls, background sound.

→ See **[audio-texture.md](audio-texture.md)**

---

## Quick-Start: Minimum Configuration for Human-Sounding Agent

Apply this block to any assistant and it will immediately sound more natural:

```json
{
  "backchannelingEnabled": true,
  "backgroundSound": "off",
  "backgroundDenoisingEnabled": true,
  "responseDelaySeconds": 0.5,
  "startSpeakingPlan": {
    "waitSeconds": 0.6,
    "smartEndpointingPlan": {
      "provider": "livekit",
      "waitFunction": "200 + 8000 * x"
    },
    "transcriptionEndpointingPlan": {
      "onPunctuationSeconds": 0.1,
      "onNoPunctuationSeconds": 1.5,
      "onNumberSeconds": 0.5
    }
  },
  "stopSpeakingPlan": {
    "numWords": 2,
    "voiceSeconds": 0.2,
    "backoffSeconds": 1.0,
    "acknowledgementPhrases": ["yeah", "uh-huh", "okay", "got it", "mhm", "right"]
  },
  "model": {
    "provider": "openai",
    "model": "gpt-4o-mini",
    "temperature": 0.6,
    "maxTokens": 180
  },
  "voice": {
    "provider": "11labs",
    "model": "eleven_turbo_v2_5",
    "stability": 0.45,
    "similarityBoost": 0.75,
    "style": 0,
    "optimizeStreamingLatency": 3
  },
  "transcriber": {
    "provider": "deepgram",
    "model": "nova-3",
    "language": "en"
  }
}
```

Then apply the **minimum humanization system prompt block** from [humanization-prompts.md](humanization-prompts.md#minimum-block).

---

## Use Case Presets

### Sales / Outbound (Speed + Confidence)

**Priority:** Fast response, confident tone, handle interruptions gracefully

```json
{
  "responseDelaySeconds": 0.35,
  "startSpeakingPlan": {
    "waitSeconds": 0.3,
    "smartEndpointingPlan": {
      "provider": "livekit",
      "waitFunction": "100 + 4000 * x"
    }
  },
  "stopSpeakingPlan": {
    "numWords": 0,
    "backoffSeconds": 0.8
  },
  "voice": {
    "provider": "cartesia",
    "experimentalControls": {
      "speed": "normal",
      "emotion": ["positivity:high"]
    }
  },
  "model": {
    "maxTokens": 140,
    "temperature": 0.65
  }
}
```

Voice recommendation: Cartesia Sonic Turbo (40ms latency), male voice, American English.

### Support / Inbound (Warmth + Accuracy)

**Priority:** Empathy, accuracy, handle complex multi-turn queries

```json
{
  "responseDelaySeconds": 0.6,
  "startSpeakingPlan": {
    "waitSeconds": 0.8,
    "smartEndpointingPlan": {
      "provider": "livekit",
      "waitFunction": "300 + 10000 * x"
    }
  },
  "stopSpeakingPlan": {
    "numWords": 3,
    "backoffSeconds": 1.2
  },
  "voice": {
    "provider": "11labs",
    "model": "eleven_turbo_v2_5",
    "stability": 0.5,
    "style": 0
  },
  "model": {
    "maxTokens": 200,
    "temperature": 0.55
  }
}
```

Voice recommendation: ElevenLabs Turbo v2.5, warm female voice, your target demographic.

### Appointment Scheduling (Clarity + Patience)

**Priority:** Crystal-clear, no mishearing names or times, patient with slow talkers

```json
{
  "responseDelaySeconds": 0.7,
  "startSpeakingPlan": {
    "waitSeconds": 1.0,
    "smartEndpointingPlan": {
      "provider": "livekit",
      "waitFunction": "400 + 12000 * x"
    }
  },
  "transcriber": {
    "provider": "deepgram",
    "model": "nova-3",
    "keywords": ["appointment:3", "schedule:3", "cancel:3", "confirm:3"]
  }
}
```

### Medical / Finance / Legal (Compliance + Precision)

**Priority:** Accuracy, no fillers, formal but not robotic, HIPAA considerations

```json
{
  "hipaaEnabled": true,
  "responseDelaySeconds": 0.8,
  "backchannelingEnabled": false,
  "startSpeakingPlan": {
    "waitSeconds": 1.0
  },
  "model": {
    "temperature": 0.3,
    "maxTokens": 250
  }
}
```

Note: Disable filler injection via dashboard for compliance contexts. Disable backchanneling.

---

## The Human-Voice Decision Tree

```
Is the voice provider right for the use case?
├── NO → Go to voice-provider-matrix.md, re-select
└── YES
    ↓
Is the response too slow or too fast?
├── Too slow → Reduce waitSeconds, switch endpointing to livekit
├── Too fast → Increase waitSeconds, use more conservative waitFunction
└── Good
    ↓
Does the prompt produce robotic phrases?
├── YES → Apply forbidden phrases list from humanization-prompts.md
└── NO
    ↓
Are words mispronounced?
├── YES → Go to pronunciation.md, build dictionary
└── NO
    ↓
Does pacing feel unnatural?
├── Monotone/rushed → Add SSML breaks or flush syntax (audio-texture.md)
└── Natural → Agent is production-ready
```

---

## Common Failure Modes

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Says "Certainly!" or "Absolutely!" | Prompt doesn't forbid them | Add explicit forbidden phrases list |
| Too many "um"s | Filler injection on + LLM fillers in prompt | Disable one system, reduce the other |
| Cuts off mid-sentence | `waitSeconds` too low or `numWords: 0` | Increase `waitSeconds` to 0.6+, `numWords` to 2 |
| Long silence before responding | `onNoPunctuationSeconds: 1.5` + formatting on | Remove transcription endpointing plan, disable formatting |
| SSML break tags spoken aloud | SSML streaming fragmentation bug | Set `inputPreprocessingEnabled: false` |
| Mispronounces brand name | No pronunciation dictionary | Add ElevenLabs alias or IPA rule |
| Sounds flat/emotionless | Too much stability on voice | Lower `stability` to 0.4–0.45 |
| Interrupts caller constantly | `numWords: 0` and aggressive endpointing | `numWords: 2`, slower `waitFunction` |
| Doesn't stop when interrupted | `numWords` too high | Set `numWords: 0` or 1 |
| Robot voice during tool call | Tool has no loading message | Add `messages[type=request-start]` to tool |

---

## Production Checklist

Before going live, verify:

- [ ] Voice provider selected and configured (stability, speed, latency mode)
- [ ] Pronunciation dictionary built for all brand names, product names, unusual terms
- [ ] Forbidden phrases list in system prompt
- [ ] Response length limited (`maxTokens: 150–200`)
- [ ] `backchannelingEnabled` configured (true for conversational, false for compliance)
- [ ] `startSpeakingPlan` tuned for use case
- [ ] `stopSpeakingPlan.numWords` set (2 for standard, 0 for sales, 3 for scheduled)
- [ ] Temperature set (0.3–0.4 for factual, 0.6–0.7 for conversational)
- [ ] Idle messages configured for silence periods
- [ ] Test call run and transcript reviewed for robotic patterns
- [ ] Numbers verified (spoken as words, not digits)
- [ ] Interruption behavior tested

---

## Reference Map

| Need | File |
|------|------|
| Choose a voice provider | [voice-provider-matrix.md](voice-provider-matrix.md) |
| Configure speech timing and endpointing | [speech-config.md](speech-config.md) |
| Write a humanized system prompt | [humanization-prompts.md](humanization-prompts.md) |
| Fix pronunciation of specific words | [pronunciation.md](pronunciation.md) |
| Add SSML pauses, emotion, flush syntax | [audio-texture.md](audio-texture.md) |
