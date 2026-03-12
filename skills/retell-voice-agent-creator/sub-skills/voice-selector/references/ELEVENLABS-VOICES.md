# ElevenLabs Voice Catalog for Retell AI

> **2026 Update:** ElevenLabs Flash v2.5 now available at ~75ms TTFA — fastest ElevenLabs option. ElevenLabs voices on Retell sound "solid but flat" compared to native ElevenLabs v3 — the "smile in the voice" and subtle emotional shifts are reduced in the Retell integration. For maximum expressiveness, consider Cartesia Sonic-3. For multilingual (29 languages), Flash v2.5 remains the top choice.

## Provider Configuration

- **Provider name in Retell:** `elevenlabs`
- **Recommended model:** `eleven_turbo_v2` (lowest latency, supports pronunciation dictionary)
- **Alternative model:** `eleven_multilingual_v2` (29 languages, higher latency)
- **Pronunciation dictionary:** Supported on Turbo v2 only (IPA format)

## Recommended Voices

| Voice ID | Name | Gender | Age Range | Accent | Tone | Best Use Cases |
|----------|------|--------|-----------|--------|------|----------------|
| `21m00Tcm4TlvDq8ikWAM` | Rachel | Female | 25-35 | American | Warm, conversational | Sales, receptionist, real estate, personal assistant |
| `29vD33N1CtxCmqQRPOHJ` | Drew | Male | 30-45 | American | Professional, steady | Lead qualification, B2B sales, consulting |
| `2EiwWnXFnvU5JabPnv8n` | Clyde | Male | 35-50 | American | Deep, authoritative | Debt collection, legal intake, insurance |
| `5Q0t7uMcjvnagumLfvZi` | Paul | Male | 30-40 | American | Warm, informative | Support, onboarding, tutorials |
| `AZnzlk1XvdvUeBnXmlld` | Domi | Female | 20-30 | American | Energetic, upbeat | Marketing, event booking, entertainment |
| `EXAVITQu4vr4xnSDxMaL` | Bella | Female | 25-35 | American | Friendly, natural | Personal assistant, casual support, wellness |
| `ErXwobaYiN019PkySvjV` | Antoni | Male | 25-35 | American | Confident, articulate | Sales, pitch delivery, product demos |
| `MF3mGyEYCl7XYWbV9V6O` | Elli | Female | 20-28 | American | Young, clear, calm | Customer support, surveys, appointment booking |
| `TxGEqnHWrfWFTfGW9XjX` | Josh | Male | 30-40 | American | Professional, deep | Enterprise sales, financial services, insurance |
| `VR6AewLTigWG4xSOukaG` | Arnold | Male | 35-50 | American | Deep, commanding | Legal, executive briefings, authoritative announcements |
| `pNInz6obpgDQGcFmaJgB` | Adam | Male | 30-40 | American | Confident, clear | Lead qualification, B2B outreach, professional services |
| `ThT5KcBeYPX3keUQqHPh` | Dorothy | Female | 45-60 | British | Warm, refined, mature | Healthcare, law firms, luxury brands, high-end receptionist |
| `jBpfuIE2acCO8z3wKNLl` | Gigi | Female | 20-25 | American | Youthful, bubbly | Casual bookings, entertainment, social media outreach |
| `oWAxZDx7w5VEj9dCyTzz` | Grace | Female | 30-40 | American | Calm, measured, soothing | Healthcare, therapy intake, meditation, wellness |
| `pqHfZKP75CvOlQylNhV4` | Bill | Male | 40-55 | American | Trustworthy, steady | Financial services, insurance, real estate |
| `yoZ06aMxZJJ28mfd3POQ` | Sam | Male | 30-45 | American | Authoritative, composed | Professional services, consulting, corporate |

## Voice Characteristics Settings

ElevenLabs voices accept additional tuning parameters when configured via their API:

| Parameter | Range | Default | Effect |
|-----------|-------|---------|--------|
| `stability` | 0.0-1.0 | 0.5 | Higher = more consistent; lower = more expressive |
| `similarity_boost` | 0.0-1.0 | 0.75 | Higher = closer to original voice; lower = more variation |
| `style` | 0.0-1.0 | 0.0 | Higher = more stylistic expression (increases latency) |
| `use_speaker_boost` | boolean | true | Enhances speaker similarity at slight latency cost |

### Recommended Settings by Use Case

| Use Case | stability | similarity_boost | style | speaker_boost |
|----------|-----------|-------------------|-------|---------------|
| Sales (warm, engaging) | 0.4 | 0.75 | 0.3 | true |
| Support (calm, consistent) | 0.7 | 0.8 | 0.1 | true |
| Receptionist (professional) | 0.6 | 0.75 | 0.15 | true |
| Appointment booking | 0.65 | 0.8 | 0.1 | true |
| Debt collection (firm) | 0.8 | 0.85 | 0.0 | true |
| Personal assistant | 0.45 | 0.7 | 0.25 | true |

## Voice Temperature in Retell

When using ElevenLabs voices through Retell, the `voice_temperature` parameter (0-2) maps to the underlying stability control:

- **Low temperature (0.3-0.5):** Maps to high stability. Consistent, predictable output. Best for medical, legal, financial.
- **Medium temperature (0.6-0.8):** Balanced variation. Best for general business use.
- **High temperature (0.9-1.2):** More expressive, natural variation. Best for sales, personal assistants.
- **Very high temperature (1.3-2.0):** Highly expressive, less predictable. Use with caution.

## Multilingual Voices

For non-English use cases, use the `eleven_multilingual_v2` model. All voices listed above support this model, but latency increases compared to Turbo v2.

### Supported Languages (29 total)

English, Spanish, French, German, Italian, Portuguese, Polish, Dutch, Turkish, Swedish, Indonesian, Filipino, Japanese, Ukrainian, Greek, Czech, Finnish, Romanian, Danish, Bulgarian, Malay, Slovak, Croatian, Arabic, Tamil, Hindi, Welsh, Korean, Mandarin Chinese.

### Multilingual Configuration Notes

- Set the `language` parameter in the Retell agent config to the target language code
- Voice quality varies by language -- English and European languages perform best
- For non-Latin script languages (Arabic, Hindi, Tamil, Chinese, Japanese, Korean), test thoroughly before deployment
- Pronunciation dictionary is NOT available with multilingual_v2 -- use prompt injection for pronunciation corrections

## Important Notes

- ElevenLabs does NOT support the `voice_emotion` parameter in Retell. Expressiveness is controlled via `voice_temperature` and prompt engineering.
- Voice IDs are stable but can change if ElevenLabs updates their catalog. Always verify via the Retell API before deploying.
- Turbo v2 has the lowest latency among ElevenLabs models and is recommended for real-time voice agents.
- ElevenLabs is the only provider that supports voice cloning through Retell. See VOICE-CLONING-GUIDE.md.
- Cost is higher than OpenAI but voice quality and flexibility are superior.
