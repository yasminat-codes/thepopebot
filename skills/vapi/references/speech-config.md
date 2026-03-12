# Speech Configuration — Timing, Endpointing, and Interruption

How long the agent waits before speaking, how it detects end-of-turn, and how it handles being interrupted. These settings determine whether conversations feel natural or robotic.

---

## Complete Field Reference

### Top-Level Timing Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `responseDelaySeconds` | number | 0 | Extra delay before the agent begins generating a response after detecting end-of-turn |
| `backchannelingEnabled` | boolean | false | Adds "yeah", "got it", "uh-huh" while user is speaking |
| `backgroundDenoisingEnabled` | boolean | false | Removes background noise from caller audio |
| `backgroundSound` | string | `"off"` | Ambient background sound (`"off"`, `"office"`, `"cafe"`) |

---

## startSpeakingPlan

Controls when the agent starts speaking after the user has (potentially) finished.

```json
{
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
    },
    "customEndpointingRules": []
  }
}
```

### `waitSeconds`

Time to wait after detecting end-of-turn before the agent begins speaking.

| Value | Effect |
|-------|--------|
| 0.2–0.3 | Aggressive. Good for sales. Risk: cuts off callers. |
| 0.4–0.6 | Balanced. Good default for most use cases. |
| 0.7–1.0 | Patient. Good for scheduling, support, elderly callers. |
| 1.0+ | Feels unresponsive for normal conversation. |

---

### Smart Endpointing (`smartEndpointingPlan`)

AI-based end-of-turn detection — better than transcription-based for natural speech.

| Provider | Description |
|----------|-------------|
| `livekit` | **Recommended.** Best performance. Uses LiveKit's audio processing. |
| `krisp` | Noise-canceling + endpointing. Good for noisy environments. |
| `assembly` | AssemblyAI's universal streaming. Good for accented speech. |
| `deepgram-flux` | Deepgram's real-time endpointing model. |

**`waitFunction` — the key knob:** A math expression where `x` is a confidence value from 0 to 1 (probability the user has finished speaking). Returns milliseconds to wait.

```
waitFunction: "200 + 8000 * x"
```

This means:
- At 0% confidence → wait 200ms
- At 50% confidence → wait 4200ms
- At 100% confidence → wait 8200ms

**Common presets:**

| Preset | Formula | Use case |
|--------|---------|---------|
| Aggressive (sales) | `"100 + 4000 * x"` | Fast-paced outbound |
| Balanced (default) | `"200 + 8000 * x"` | Most inbound use cases |
| Patient (scheduling) | `"400 + 12000 * x"` | Complex queries, elderly callers |
| Paranoid (medical) | `"500 + 15000 * x"` | Never interrupt; wait for full sentence |

---

### Transcription Endpointing (`transcriptionEndpointingPlan`)

Fallback endpointing based on transcript content. Used when smart endpointing is not configured or as a secondary layer.

| Field | Default | Effect |
|-------|---------|--------|
| `onPunctuationSeconds` | 0.1 | Wait after `.`, `?`, `!` in transcript |
| `onNoPunctuationSeconds` | 1.5 | **Primary latency driver.** Wait after speech with no punctuation. |
| `onNumberSeconds` | 0.5 | Wait after number detection (addresses, order numbers) |

**Critical gotcha:** `onNoPunctuationSeconds: 1.5` is the most common cause of "long silence before responding" bugs. If you're seeing 1.5–2 second delays, this is why — the transcriber formatting is generating numbers without punctuation.

**Fix:** Set `onNoPunctuationSeconds: 0.4–0.6` or rely on smart endpointing instead:

```json
{
  "transcriptionEndpointingPlan": {
    "onPunctuationSeconds": 0.1,
    "onNoPunctuationSeconds": 0.6,
    "onNumberSeconds": 0.3
  }
}
```

---

### Custom Endpointing Rules

Override endpointing for specific phrases or contexts:

```json
{
  "customEndpointingRules": [
    {
      "type": "AssistantRegex",
      "regex": "address|zip code|phone number",
      "timeoutSeconds": 2.5
    },
    {
      "type": "CustomerRegex",
      "regex": "hold on|one second|let me",
      "timeoutSeconds": 5.0
    }
  ]
}
```

| Rule type | Matches against | Effect |
|-----------|----------------|--------|
| `AssistantRegex` | Last assistant utterance | When agent asks for complex input, wait longer |
| `CustomerRegex` | Customer's last words | When customer signals they're still thinking, hold |

---

## stopSpeakingPlan

Controls when the agent stops speaking after the user starts speaking (interruption handling).

```json
{
  "stopSpeakingPlan": {
    "numWords": 2,
    "voiceSeconds": 0.2,
    "backoffSeconds": 1.0,
    "acknowledgementPhrases": ["yeah", "uh-huh", "okay", "got it", "mhm", "right", "sure"]
  }
}
```

### Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `numWords` | number | 0 | Minimum words the user must speak before the agent stops |
| `voiceSeconds` | number | 0.1 | Duration of voice activity required to trigger stop |
| `backoffSeconds` | number | 1.0 | Time agent waits before speaking again after being interrupted |
| `acknowledgementPhrases` | string[] | See below | Words that DON'T count as real interruptions |

### `numWords` — The Interruption Threshold

| Value | Effect |
|-------|--------|
| 0 | Agent stops at any voice activity (breath, cough, "mm"). Too sensitive. |
| 1 | Agent stops at any single word. Sensitive but usable. |
| 2 | **Recommended.** Stops on real interruption. Ignores most accidental sounds. |
| 3–4 | Patient. Good for scheduled calls, reading back info. |
| 5+ | Rarely appropriate. Agent will talk over the caller. |

### `acknowledgementPhrases`

Words the user can say while the agent is speaking that don't trigger an interruption. The agent hears these as backchannels — "you're okay to keep going."

```json
"acknowledgementPhrases": [
  "yeah", "uh-huh", "okay", "got it", "mhm", "right", "sure",
  "I see", "yep", "mm-hmm", "ok", "alright", "go ahead",
  "yes", "no", "uhh"
]
```

---

## Transcriber Configuration

The transcriber affects how fast and accurately speech-to-text runs. This feeds directly into endpointing.

```json
{
  "transcriber": {
    "provider": "deepgram",
    "model": "nova-3",
    "language": "en",
    "smartFormat": false,
    "numerals": false,
    "keywords": [],
    "endpointing": 100
  }
}
```

### Field Reference

| Field | Value | Notes |
|-------|-------|-------|
| `provider` | `"deepgram"` | Best speed/accuracy for English. |
| `model` | `"nova-3"` | Latest. Best accuracy. Use this. |
| `language` | `"en"` or `"multi"` | `"multi"` for multilingual callers |
| `smartFormat` | `false` | **Important:** Disable. Smart formatting adds punctuation that triggers `onNoPunctuationSeconds` quirks and adds latency. |
| `numerals` | `false` | Disable. Converts "five hundred" → "500" which breaks TTS. |
| `endpointing` | `100` | Deepgram's internal endpointing timeout in ms. Default 300ms — reduce to 100ms for faster response. |
| `keywords` | array | Boost recognition of specific words. See format below. |

### Keyword Boosting

Improve transcription accuracy for domain-specific terms:

```json
{
  "keywords": [
    "appointment:3",
    "schedule:2",
    "cancel:2",
    "Smarterflo:5",
    "ElevenLabs:4"
  ]
}
```

Format: `"word:intensifier"` — intensifier range 1–10. Higher = stronger boost.

**Warning:** Over-boosting makes the transcriber hallucinate the word even when not said. Stay under 5 for common words.

---

## Idle Configuration

What the agent says when the caller goes silent.

```json
{
  "silenceTimeoutSeconds": 30,
  "idleMessages": [
    "Are you still there?",
    "Take your time, I'm here.",
    "Just let me know when you're ready."
  ],
  "idleMessageMaxSpokenCount": 3
}
```

| Field | Default | Notes |
|-------|---------|-------|
| `silenceTimeoutSeconds` | 30 | Seconds of silence before idle message triggers |
| `idleMessages` | `[]` | Array of messages — randomly selected each time |
| `idleMessageMaxSpokenCount` | 3 | How many times idle messages fire before call ends |

---

## Complete Recommended Configurations

### Standard Inbound Support

```json
{
  "responseDelaySeconds": 0.5,
  "backchannelingEnabled": true,
  "backgroundDenoisingEnabled": true,
  "startSpeakingPlan": {
    "waitSeconds": 0.6,
    "smartEndpointingPlan": {
      "provider": "livekit",
      "waitFunction": "200 + 8000 * x"
    },
    "transcriptionEndpointingPlan": {
      "onPunctuationSeconds": 0.1,
      "onNoPunctuationSeconds": 0.6,
      "onNumberSeconds": 0.4
    }
  },
  "stopSpeakingPlan": {
    "numWords": 2,
    "voiceSeconds": 0.2,
    "backoffSeconds": 1.0,
    "acknowledgementPhrases": ["yeah", "uh-huh", "okay", "got it", "mhm", "right"]
  },
  "transcriber": {
    "provider": "deepgram",
    "model": "nova-3",
    "language": "en",
    "smartFormat": false,
    "numerals": false,
    "endpointing": 100
  }
}
```

### Aggressive Outbound Sales

```json
{
  "responseDelaySeconds": 0.3,
  "backchannelingEnabled": true,
  "startSpeakingPlan": {
    "waitSeconds": 0.3,
    "smartEndpointingPlan": {
      "provider": "livekit",
      "waitFunction": "100 + 4000 * x"
    }
  },
  "stopSpeakingPlan": {
    "numWords": 1,
    "voiceSeconds": 0.15,
    "backoffSeconds": 0.7
  }
}
```

### Appointment Scheduling (Patience Mode)

```json
{
  "responseDelaySeconds": 0.7,
  "backchannelingEnabled": true,
  "startSpeakingPlan": {
    "waitSeconds": 1.0,
    "smartEndpointingPlan": {
      "provider": "livekit",
      "waitFunction": "400 + 12000 * x"
    },
    "customEndpointingRules": [
      {
        "type": "AssistantRegex",
        "regex": "date|time|address|phone|name",
        "timeoutSeconds": 3.0
      },
      {
        "type": "CustomerRegex",
        "regex": "let me|hold on|one moment|just a",
        "timeoutSeconds": 8.0
      }
    ]
  },
  "stopSpeakingPlan": {
    "numWords": 3,
    "backoffSeconds": 1.2
  },
  "transcriber": {
    "provider": "deepgram",
    "model": "nova-3",
    "keywords": ["appointment:3", "schedule:3", "cancel:3", "confirm:3"]
  }
}
```

---

## Common Symptoms and Fixes

| Symptom | Most Likely Cause | Fix |
|---------|------------------|-----|
| Long silence before response | `onNoPunctuationSeconds: 1.5` default | Set to 0.4–0.6 or use smart endpointing only |
| Agent cuts off caller mid-sentence | `waitSeconds` too low, `numWords: 0` | Increase `waitSeconds` to 0.6+, `numWords` to 2 |
| Agent won't stop when interrupted | `numWords` too high (4+) | Set to 1 or 2 |
| Agent stops at every "mm-hmm" | `numWords: 0` | Set to 2; add phrases to `acknowledgementPhrases` |
| Response is too slow overall | `waitSeconds` too high | Reduce; switch to livekit smart endpointing |
| Agent keeps talking after "goodbye" | No endCall hook | Add `call.ending` hook or `endCall` tool |
| Transcription misses domain words | No keyword boosting | Add keywords with 2–4 intensifier |

---

## References

- [Voice Provider Matrix](voice-provider-matrix.md) — provider selection and configuration
- [Human Voice Master Guide](human-voice.md) — full orchestration overview
- [Audio Texture](audio-texture.md) — SSML and flush syntax for pacing
- Vapi speech docs: https://docs.vapi.ai/assistants/speech-config
