# OpenAI Voice Catalog for Retell AI

## Provider Configuration

- **Provider name in Retell:** `openai`
- **Model:** `gpt-4o-mini-tts`
- **Pronunciation dictionary:** Not supported
- **Voice emotion:** Not supported
- **Voice cloning:** Not supported

## Voice Catalog

| Voice ID | Name | Gender | Tone | Speed | Best Use Cases |
|----------|------|--------|------|-------|----------------|
| `openai-alloy` | Alloy | Neutral | Versatile, balanced, clear | Medium | Surveys, general assistants, neutral contexts |
| `openai-ash` | Ash | Male | Steady, professional, composed | Medium | Lead qualification, B2B, consulting |
| `openai-ballad` | Ballad | Male | Warm, smooth, calm | Medium-slow | Healthcare, wellness, patient intake |
| `openai-coral` | Coral | Female | Warm, professional, friendly | Medium | Receptionist, appointment booking, customer service |
| `openai-echo` | Echo | Male | Warm, resonant, engaging | Medium | Sales, outreach, relationship-building |
| `openai-fable` | Fable | Non-binary | Expressive, dynamic, storytelling | Medium-fast | Entertainment, tutorials, onboarding |
| `openai-nova` | Nova | Female | Warm, friendly, approachable | Medium | Personal assistants, wellness, casual support |
| `openai-onyx` | Onyx | Male | Deep, authoritative, commanding | Medium-slow | Legal, financial, executive, debt collection |
| `openai-sage` | Sage | Female | Clear, measured, professional | Medium | Surveys, data collection, formal contexts |
| `openai-shimmer` | Shimmer | Female | Clear, professional, polished | Medium | Corporate receptionist, enterprise support |
| `openai-verse` | Verse | Male | Confident, articulate, dynamic | Medium | Product demos, sales pitches, presentations |

## When to Choose OpenAI

OpenAI voices are the right choice when:

1. **Budget is a primary concern.** OpenAI TTS is significantly cheaper per minute than ElevenLabs.
2. **Simplicity matters.** No complex voice settings to tune -- just pick a voice and go.
3. **Reliability is critical.** OpenAI infrastructure has excellent uptime and consistent quality.
4. **You do not need pronunciation dictionaries.** If the agent handles standard vocabulary, OpenAI works well.
5. **You do not need voice emotion control.** Expressiveness is baked into the voice, not adjustable per-utterance.

## When NOT to Choose OpenAI

- You need IPA pronunciation dictionary support (choose ElevenLabs Turbo v2)
- You need per-utterance voice emotion control (choose Cartesia or MiniMax)
- You need voice cloning (choose ElevenLabs or MiniMax)
- You need maximum expressiveness and warmth (ElevenLabs voices are richer)
- You need 40+ language support (choose MiniMax)

## Recommended Voices by Template

| Template | Primary Voice | Why |
|----------|--------------|-----|
| Sales | Echo | Warm and engaging, builds rapport |
| Support | Coral | Friendly and clear, patient tone |
| Appointment | Coral | Professional and efficient |
| Receptionist | Shimmer | Clear and polished |
| Personal Assistant | Nova | Warm and approachable |
| Lead Qualifier | Ash | Professional and composed |
| Survey | Sage | Neutral and measured |
| Debt Collection | Onyx | Authoritative and firm |
| Real Estate | Nova | Warm and trustworthy |

## Voice Temperature and Speed

OpenAI voices respond to Retell's `voice_temperature` and `voice_speed` parameters:

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| `voice_temperature` | 0-2 | 1.0 | Affects expressiveness; OpenAI voices are naturally consistent, so temperature effects are subtler than ElevenLabs |
| `voice_speed` | 0.5-2.0 | 1.0 | Linear speed adjustment; stays natural within 0.8-1.2 range |

## Limitations

- No pronunciation dictionary -- mispronounced words must be corrected via prompt injection (e.g., "pronounce 'Nguyen' as 'Win'")
- No voice emotion parameter -- emotional tone comes from the LLM prompt, not the voice engine
- No voice cloning -- cannot replicate a specific person's voice
- Fewer voice options than ElevenLabs -- 11 voices vs 30+
- Less granular voice tuning -- no stability, similarity_boost, or style controls
- Voice quality is good but not as rich or natural as top ElevenLabs voices

## Cost Advantage

OpenAI TTS pricing is typically 50-70% lower per minute than ElevenLabs, making it the best choice for high-volume deployments where voice quality requirements are standard rather than premium.
