# Deepgram Voice Catalog for Retell AI

## Provider Configuration

- **Provider name in Retell:** `deepgram`
- **Key differentiator:** Fast processing, low latency, strong transcription heritage
- **Voice emotion:** Not supported
- **Pronunciation dictionary:** Not supported
- **Voice cloning:** Not supported

## Voice Catalog

| Voice ID | Name | Gender | Tone | Best Use Cases |
|----------|------|--------|------|----------------|
| `deepgram-aura-asteria-en` | Asteria | Female | Professional, clear | Receptionist, appointment booking, corporate |
| `deepgram-aura-luna-en` | Luna | Female | Warm, friendly | Support, personal assistant, wellness |
| `deepgram-aura-stella-en` | Stella | Female | Calm, measured | Healthcare, surveys, formal contexts |
| `deepgram-aura-athena-en` | Athena | Female | Confident, articulate | Sales, lead qualification |
| `deepgram-aura-hera-en` | Hera | Female | Authoritative, composed | Legal, financial, executive |
| `deepgram-aura-orion-en` | Orion | Male | Professional, steady | B2B, consulting, lead qualification |
| `deepgram-aura-arcas-en` | Arcas | Male | Warm, trustworthy | Sales, real estate, relationship-building |
| `deepgram-aura-perseus-en` | Perseus | Male | Deep, authoritative | Debt collection, legal, insurance |
| `deepgram-aura-angus-en` | Angus | Male | Confident, direct | Outbound sales, cold calling |
| `deepgram-aura-orpheus-en` | Orpheus | Male | Calm, soothing | Healthcare, wellness, therapy |
| `deepgram-aura-helios-en` | Helios | Male | Energetic, upbeat | Marketing, events, promotions |
| `deepgram-aura-zeus-en` | Zeus | Male | Commanding, authoritative | Executive, announcements |

## When to Choose Deepgram

1. **Latency-sensitive applications.** Deepgram's infrastructure is optimized for speed, making it suitable for high-volume call centers where every millisecond counts.
2. **High-volume call centers.** Deepgram pricing is competitive at scale, and their platform handles large concurrent call volumes well.
3. **Transcription-first workflows.** If you are already using Deepgram for speech-to-text, keeping TTS on the same provider simplifies the stack.
4. **Simple voice needs.** When you need a reliable, clear voice without advanced features like emotion or cloning.

## When NOT to Choose Deepgram

- You need voice emotion control (choose Cartesia or MiniMax)
- You need voice cloning (choose ElevenLabs or MiniMax)
- You need pronunciation dictionaries (choose ElevenLabs Turbo v2)
- You need maximum voice quality and expressiveness (ElevenLabs is richer)
- You need extensive multilingual support (MiniMax covers 40+ languages)

## Recommended Voices by Template

| Template | Voice | Why |
|----------|-------|-----|
| Sales | Athena (F) / Angus (M) | Confident delivery for outbound |
| Support | Luna (F) / Orpheus (M) | Warm and patient |
| Appointment | Asteria (F) / Orion (M) | Professional and clear |
| Receptionist | Asteria (F) / Orion (M) | Composed first impression |
| Lead Qualifier | Athena (F) / Arcas (M) | Direct and trustworthy |
| Survey | Stella (F) / Orion (M) | Neutral and measured |
| Debt Collection | Hera (F) / Perseus (M) | Authoritative and firm |
| Healthcare | Stella (F) / Orpheus (M) | Calm and soothing |

## Voice Temperature and Speed

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| `voice_temperature` | 0-2 | 1.0 | Deepgram voices are naturally consistent; temperature effects are moderate |
| `voice_speed` | 0.5-2.0 | 1.0 | Best results within 0.8-1.2 range |

## Limitations

- Smaller voice catalog compared to ElevenLabs (12 voices vs 30+)
- No voice emotion parameter
- No pronunciation dictionary support
- No voice cloning capability
- English-focused -- multilingual options are limited compared to MiniMax or ElevenLabs
- Less expressive range than ElevenLabs or Cartesia voices
