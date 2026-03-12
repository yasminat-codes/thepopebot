# Voice Provider Selection Matrix

Choosing the right voice provider is the single highest-impact decision for how human your agent sounds. Wrong provider = no amount of prompting or configuration fixes it.

---

## Latency Benchmarks

End-to-end latency = ASR + LLM inference + TTS generation + network. TTS is a significant component.

| Provider | TTS Latency | Streaming | Notes |
|----------|------------|-----------|-------|
| **Cartesia Sonic Turbo** | ~40ms | Yes | Lowest latency available. Best for sales/outbound. |
| **ElevenLabs Flash v2.5** | ~75ms | Yes | Best quality-to-latency ratio. |
| **ElevenLabs Turbo v2.5** | ~110ms | Yes | Slightly more expressive than Flash. |
| **Vapi native voices** | ~50ms | Yes | Good for cost-sensitive deployments. Less customizable. |
| **Deepgram Aura** | ~80ms | Yes | Good quality, solid option for neutral voices. |
| **OpenAI TTS** | ~120ms | Yes | Quality is decent; not recommended over ElevenLabs. |
| **Azure Neural** | ~150–300ms | Partial | High latency. Use only if Azure ecosystem required. |
| **PlayHT** | ~100–200ms | Partial | Higher latency. Custom voice cloning use cases. |

**For ultra-low latency stack:** AssemblyAI Universal-Streaming (90ms) + Groq Llama 4 (200ms) + ElevenLabs Flash v2.5 (75ms) ≈ **465ms end-to-end** for web calls.

---

## Provider Comparison Table

| Feature | ElevenLabs | Cartesia | Deepgram Aura | Vapi Native | OpenAI |
|---------|-----------|---------|--------------|------------|--------|
| Voice quality | ★★★★★ | ★★★★☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ |
| Latency | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★☆☆ |
| Pronunciation control | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |
| Emotion controls | ★★★☆☆ | ★★★★★ | ★☆☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |
| SSML support | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ | ★★☆☆☆ | ★☆☆☆☆ |
| Custom voice cloning | ★★★★★ | ★★★★☆ | ★★☆☆☆ | ★☆☆☆☆ | ★★☆☆☆ |
| Price | $$$ | $$ | $$ | $ | $$ |
| Reliability | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★★★ | ★★★★★ |

**Community voice quality winner (blind tests):** Cartesia > ElevenLabs for speed/naturalness, but ElevenLabs wins on warmth and expressiveness.

---

## Use Case → Provider Recommendation

| Use Case | Recommended | Why |
|---------|-------------|-----|
| Sales / outbound | Cartesia Sonic Turbo | 40ms latency. Confidence. Handles fast-paced calls. |
| Support / inbound | ElevenLabs Turbo v2.5 | Warmth. Handles complex emotional calls. Pronunciation control. |
| Appointment scheduling | ElevenLabs Turbo v2.5 | Clear. Pronunciation dictionary for address/name accuracy. |
| Medical / legal | ElevenLabs Turbo v2.5 | SSML for pacing. High accuracy. Professional tone voices. |
| Healthcare with HIPAA | ElevenLabs Flash v2.5 | Low latency + HIPAA compliance available. |
| Multilingual | Deepgram Aura or ElevenLabs | Strong multilingual voice options. |
| High-volume / cost-sensitive | Vapi native or Cartesia | Lowest cost per minute. |
| Developer testing | Vapi native (Elliot/Lily) | No external API key required. Fast to iterate. |

---

## ElevenLabs Configuration

### Recommended Models

| Model | Latency | Best for |
|-------|---------|---------|
| `eleven_flash_v2_5` | ~75ms | Production default. Best latency. |
| `eleven_turbo_v2_5` | ~110ms | Slightly more expressive. Support use cases. |
| `eleven_multilingual_v2` | ~200ms | Non-English languages. Not recommended for real-time. |

### Voice Configuration Fields

```json
{
  "voice": {
    "provider": "11labs",
    "voiceId": "JBFqnCBsd6RMkjVDRZzb",
    "model": "eleven_turbo_v2_5",
    "stability": 0.45,
    "similarityBoost": 0.75,
    "style": 0,
    "useSpeakerBoost": true,
    "optimizeStreamingLatency": 3,
    "enableSsmlParsing": false
  }
}
```

| Field | Range | Recommended | Effect |
|-------|-------|-------------|--------|
| `stability` | 0–1 | 0.40–0.50 | Lower = more expressive, natural variation. Higher = monotone, robotic. **Never above 0.6.** |
| `similarityBoost` | 0–1 | 0.70–0.80 | Higher = closer to original voice clone. Lower = more generic. |
| `style` | 0–1 | 0 | Style exaggeration. Leave at 0 for phone — it adds latency with minimal benefit. |
| `useSpeakerBoost` | bool | true | Slightly improves voice consistency. |
| `optimizeStreamingLatency` | 0–4 | 3 | 0 = highest quality, 4 = lowest latency. 3 is the best production balance. |
| `enableSsmlParsing` | bool | false | Set true only when using SSML tags. Requires voiceId to be set. |

**Stability is the most commonly misconfigured field.** Default is 0.75 — that's too high. Drop to 0.40–0.45 immediately.

### Recommended Voice IDs (verified working)

| Voice | Character | Best for |
|-------|-----------|---------|
| `JBFqnCBsd6RMkjVDRZzb` | George — male, British, warm | Support, professional services |
| `EXAVITQu4vr4xnSDxMaL` | Sarah — female, American, friendly | Support, scheduling |
| `TX3LPaxmHKxFdv7VOQHJ` | Liam — male, American, conversational | Sales, outbound |
| `XB0fDUnXU5powFXDhCwa` | Charlotte — female, British, professional | Finance, legal |
| `pFZP5JQG7iQjIQuC4Bku` | Lily — female, American, warm | Healthcare, wellness |

Test voices at https://elevenlabs.io/voice-library before committing.

---

## Cartesia Configuration

### Models

| Model | Latency | Notes |
|-------|---------|-------|
| `sonic-turbo` | ~40ms | Production default. Best speed. |
| `sonic-2` | ~80ms | Higher quality. Use for premium use cases. |

### Voice Configuration

```json
{
  "voice": {
    "provider": "cartesia",
    "voiceId": "your-voice-id",
    "model": "sonic-turbo",
    "experimentalControls": {
      "speed": "normal",
      "emotion": ["positivity:high", "curiosity:medium"]
    }
  }
}
```

### Emotion Controls

Cartesia supports real-time emotion injection via `experimentalControls.emotion`:

| Emotion | Values | Use case |
|---------|--------|---------|
| `positivity` | `low`, `medium`, `high`, `highest` | Sales warmth, support encouragement |
| `negativity` | `low`, `medium`, `high`, `highest` | Rarely used — for expressing concern |
| `curiosity` | `low`, `medium`, `high`, `highest` | Discovery/qualification calls |
| `surprise` | `low`, `medium`, `high`, `highest` | Use sparingly |
| `sadness` | `low`, `medium`, `high`, `highest` | Rarely appropriate |
| `anger` | `low`, `medium`, `high`, `highest` | Never use |

**Speed control:** `"slow"`, `"normal"`, `"fast"`. Keep at `"normal"` for phone; `"fast"` for web demos.

### Recommended Cartesia Voices (by accent)

| Voice type | Cartesia voice category | Notes |
|------------|------------------------|-------|
| American male, confident | Search "american male" in Cartesia voice library | Use for outbound sales |
| American female, warm | Search "american female warm" | Use for support |
| British male, professional | Search "british male professional" | Finance, legal |

Cartesia voices: https://play.cartesia.ai

---

## Vapi Native Voices

Zero-latency, no external API key required. Use for development or cost-sensitive production.

```json
{
  "voice": {
    "provider": "vapi",
    "voiceId": "Elliot"
  }
}
```

Available: `Elliot`, `Lily`, `Rohan`, `Paola`, `Kian`

**Limitation:** No pronunciation dictionary, no SSML, no emotion controls.

---

## OpenAI Realtime (Special Case)

The only speech-to-speech option — no separate STT, LLM, and TTS pipeline. The model handles everything.

```json
{
  "model": {
    "provider": "openai-realtime",
    "model": "gpt-4o-realtime-preview"
  }
}
```

**When to use:**
- Ultra-low latency requirements (<300ms total)
- Continuous emotional awareness needed
- Native multimodal context (audio + text)

**Limitations:**
- No external tool calls as cleanly as standard pipeline
- Less control over voice characteristics
- Higher cost per minute
- Not recommended for most production phone bots

---

## Provider Selection Decision Tree

```
What matters most?
├── Speed (outbound sales, live demos)
│   └── Cartesia Sonic Turbo (40ms)
├── Voice quality + warmth (support, medical, scheduling)
│   └── ElevenLabs Turbo v2.5 (110ms)
├── Speed + quality balance (most production deployments)
│   └── ElevenLabs Flash v2.5 (75ms)
├── Cost (high volume)
│   └── Vapi native or Cartesia
└── Pronunciation accuracy critical (addresses, names, medical terms)
    └── ElevenLabs (pronunciation dictionary API)
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using ElevenLabs `stability: 0.75` (default) | Drop to 0.40–0.45 |
| Using `eleven_multilingual_v2` for English | Use `eleven_turbo_v2_5` — 2x faster |
| Setting `style > 0` | Leave at 0 for phone; adds latency |
| Not setting `optimizeStreamingLatency` | Set to 3 in production |
| Using Azure or PlayHT for real-time | Latency is too high for natural conversation |
| Forgetting to test the actual voice via call | Run a test call before launch — written tests don't catch voice quality |

---

## References

- [Speech Configuration](speech-config.md) — timing and endpointing
- [Pronunciation](pronunciation.md) — ElevenLabs pronunciation dictionary
- [Audio Texture](audio-texture.md) — SSML and emotion controls
- [Human Voice Master Guide](human-voice.md)
- Vapi provider docs: https://docs.vapi.ai/customization/voices/voice-providers
- ElevenLabs voice library: https://elevenlabs.io/voice-library
- Cartesia voice library: https://play.cartesia.ai
