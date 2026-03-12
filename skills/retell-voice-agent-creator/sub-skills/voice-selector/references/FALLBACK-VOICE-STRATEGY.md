# Fallback Voice Strategy

## Why Fallbacks Matter

Voice provider outages happen. ElevenLabs, Cartesia, and every other provider have experienced downtime. When your primary voice provider goes down and you have no fallback, your agent goes silent -- calls drop, customers leave, revenue is lost.

Beyond outages, fallbacks protect against:
- **Voice deprecation:** Providers retire voices without warning
- **Account issues:** Billing failures, API key rotation mistakes, quota exhaustion
- **Regional availability:** Some providers have higher latency or lower reliability in certain regions
- **Quality degradation:** Provider updates can change how a voice sounds

Every production agent MUST have at least two fallback voices from different providers.

## Fallback Strategy

### Three-Tier Approach

```
Tier 1: Primary voice (preferred provider)
  |
  v -- if unavailable --
Tier 2: Same-provider fallback (different voice, same provider)
  |
  v -- if unavailable --
Tier 3: Cross-provider fallback (different provider entirely)
```

### Selection Priority

When selecting fallback voices, match attributes in this order:

1. **Gender** -- Must match. A male voice falling back to female (or vice versa) is jarring.
2. **Age range** -- Should be similar. A 25-year-old voice falling back to a 55-year-old voice is noticeable.
3. **Tone** -- Match the general feel: warm, authoritative, calm, energetic.
4. **Accent** -- Match if possible, but a neutral American accent is an acceptable fallback for most English voices.
5. **Provider features** -- If the primary voice uses emotion, the fallback should too (if possible).

## Fallback Voice Table

### Female Voices

| Primary Voice | Provider | Fallback 1 | Provider | Fallback 2 | Provider |
|--------------|----------|------------|----------|------------|----------|
| Rachel (warm, 25-35) | ElevenLabs | Coral (warm, professional) | OpenAI | Sweet Lady (warm, gentle) | Cartesia |
| Bella (friendly, 25-35) | ElevenLabs | Nova (warm, friendly) | OpenAI | Friendly Sidekick (warm) | Cartesia |
| Elli (young, calm) | ElevenLabs | Sage (clear, measured) | OpenAI | Calm Woman | MiniMax |
| Dorothy (mature, British) | ElevenLabs | Shimmer (clear, professional) | OpenAI | Professional Woman | Cartesia |
| Grace (calm, soothing) | ElevenLabs | Nova (warm, friendly) | OpenAI | Gentle Woman | MiniMax |
| Coral (warm, professional) | OpenAI | Rachel (warm, conversational) | ElevenLabs | Commercial Lady | Cartesia |
| Shimmer (clear, professional) | OpenAI | Dorothy (refined, mature) | ElevenLabs | Narrator Lady | Cartesia |
| Professional Woman | Cartesia | Shimmer (clear, professional) | OpenAI | Elli (calm, clear) | ElevenLabs |
| Asteria (professional) | Deepgram | Coral (warm, professional) | OpenAI | Commercial Lady | Cartesia |

### Male Voices

| Primary Voice | Provider | Fallback 1 | Provider | Fallback 2 | Provider |
|--------------|----------|------------|----------|------------|----------|
| Josh (professional, deep) | ElevenLabs | Onyx (authoritative) | OpenAI | Commercial Man | Cartesia |
| Adam (confident, clear) | ElevenLabs | Ash (steady, professional) | OpenAI | Confident British Man | Cartesia |
| Antoni (confident, articulate) | ElevenLabs | Verse (confident, dynamic) | OpenAI | Sportsman | Cartesia |
| Sam (authoritative, composed) | ElevenLabs | Onyx (deep, commanding) | OpenAI | Narrator Man | Cartesia |
| Clyde (deep, authoritative) | ElevenLabs | Onyx (deep, commanding) | OpenAI | Deep Voice Man | MiniMax |
| Ash (steady, professional) | OpenAI | Adam (confident, clear) | ElevenLabs | Commercial Man | Cartesia |
| Onyx (deep, authoritative) | OpenAI | Josh (professional, deep) | ElevenLabs | Determined Man | MiniMax |
| Orion (professional) | Deepgram | Ash (steady, professional) | OpenAI | Patient Man | MiniMax |

## Configuring Fallbacks in Agent Config

Include fallback voice IDs in the agent configuration:

```json
{
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "voice_model": "eleven_turbo_v2",
  "voice_provider": "ElevenLabs",
  "fallback_voice_ids": [
    {
      "voice_id": "openai-Coral",
      "provider": "OpenAI",
      "model": "gpt-4o-mini-tts",
      "reason": "Same gender, warm tone, reliable provider"
    },
    {
      "voice_id": "63ff761f-c1e8-414b-b969-ae73f7e1b90c",
      "provider": "Cartesia",
      "model": "sonic-3",
      "reason": "Same gender, warm tone, low latency fallback"
    }
  ]
}
```

## Testing Fallback Voices

Before deploying, verify every fallback voice:

1. **Existence check.** Call the Retell API to confirm the voice_id is valid and accessible.
2. **Quality check.** Generate a test utterance with each fallback voice using the same prompt content.
3. **Consistency check.** Compare the primary and fallback voices side by side. The transition should not be jarring to a caller.
4. **Parameter check.** Verify that voice_temperature and voice_speed produce acceptable results with the fallback voice.
5. **Feature check.** If the primary uses voice_emotion, confirm the fallback provider supports it (or accept that emotion will be lost).

### Test Script

```bash
# Verify voice exists in Retell
curl -s -X GET "https://api.retellai.com/v2/get-voice/VOICE_ID" \
  -H "Authorization: Bearer YOUR_RETELL_API_KEY" | python3 -m json.tool
```

## Monitoring Voice Availability

### Proactive Checks

- Run a daily health check that attempts to generate a short utterance with each configured voice
- Alert if any voice returns an error or takes longer than 5 seconds to respond
- Track provider status pages: ElevenLabs, OpenAI, Cartesia, Deepgram, MiniMax

### Reactive Measures

- If a primary voice fails during a call, Retell can be configured to retry with the fallback
- Log every fallback activation for review
- If fallback activations exceed 5% of calls, investigate the primary provider

## Common Pitfalls

1. **No fallback configured.** The most common mistake. Every production agent needs fallbacks.
2. **Fallback from the same provider.** If ElevenLabs is down, another ElevenLabs voice will also be down. Always include a cross-provider fallback.
3. **Gender mismatch in fallback.** A male voice falling back to a female voice (or vice versa) confuses callers.
4. **Untested fallbacks.** A fallback voice that was never tested may sound terrible with your specific prompts.
5. **Stale voice IDs.** Providers retire voices. Check fallback voice_ids quarterly.

## fallback_voice_ids Parameter (Retell API)

Configure automatic voice failover directly in the agent config:

```json
{
  "voice_id": "11labs-Rachel",
  "fallback_voice_ids": ["cartesia-sonic-3-us-female", "openai-nova"]
}
```

Rules:
- List fallbacks in priority order — first listed is tried first
- Always choose fallbacks from DIFFERENT providers than primary
- Test fallback voices before deployment — they must sound acceptable, not just work
- Retell automatically tries fallbacks if primary TTS provider returns an error
- No configuration needed beyond this array — failover is automatic
