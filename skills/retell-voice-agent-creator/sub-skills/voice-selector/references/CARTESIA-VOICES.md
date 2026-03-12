# Cartesia Voice Catalog for Retell AI

> **2026 Update: Cartesia Sonic-3 is now the top recommendation for speed + emotion.** TTFA: ~95ms. Supports voice_emotion parameter with 7 emotions. Best balance of expressiveness and latency for most use cases.

## Provider Configuration

- **Provider name in Retell:** `cartesia`
- **Model:** `sonic-3`
- **Key differentiator:** Supports `voice_emotion` parameter
- **Pronunciation dictionary:** Not supported
- **Voice cloning:** Not supported

## Voice Emotion Support

Cartesia is one of only two providers (along with MiniMax) that supports the `voice_emotion` parameter in Retell. This allows per-utterance emotional control.

### Available Emotions

| Emotion | Effect | Best For |
|---------|--------|----------|
| `calm` | Steady, relaxed delivery | Support, healthcare, appointment booking, debt collection |
| `sympathetic` | Compassionate, understanding tone | Healthcare, insurance claims, complaint handling |
| `happy` | Upbeat, positive energy | Sales, marketing, event booking |
| `sad` | Subdued, empathetic tone | Condolence, sensitive topics |
| `angry` | Firm, intense delivery | Rarely used -- handle with extreme caution |
| `fearful` | Urgent, concerned tone | Emergency notifications (very niche) |
| `surprised` | Excited, reactive tone | Promotions, announcements, rewards |

### Emotion Selection by Template

| Template | Recommended Emotion | Why |
|----------|-------------------|-----|
| Sales | `happy` | Positive energy drives conversions |
| Support | `sympathetic` | Customers feel heard and understood |
| Appointment | `calm` | Professional, no-pressure booking |
| Receptionist | `calm` | Steady, welcoming first impression |
| Debt Collection | `calm` | Professional without aggression |
| Healthcare | `sympathetic` | Compassionate patient interaction |
| Real Estate | `happy` | Enthusiastic about properties |

## Voice Catalog

| Voice ID | Name | Gender | Tone | Best Use Cases |
|----------|------|--------|------|----------------|
| `a167e0f3-df7e-4277-976b-f722e6c0a56b` | Barbershop Man | Male | Warm, friendly | Sales, casual support |
| `00a77add-48d5-4ef6-8157-71e5437b282d` | Classy British Man | Male | Refined, authoritative | Legal, financial, luxury brands |
| `79a125e8-cd45-4c13-8a67-188112f4dd22` | Commercial Lady | Female | Clear, professional | Receptionist, corporate |
| `c8605446-247c-4f39-993c-f49145efdab7` | Commercial Man | Male | Professional, steady | B2B, consulting |
| `694f9389-aac1-45b6-b726-9d9369183238` | Confident British Man | Male | Confident, composed | Executive, legal, insurance |
| `e3827ec5-697a-4b7c-9f7b-2e98109a3c31` | Friendly Sidekick | Female | Warm, supportive | Personal assistant, wellness |
| `41534e16-2966-4c6b-9670-111411def906` | Narrator Lady | Female | Clear, measured | Surveys, onboarding |
| `bd9120b6-7761-47a6-a446-77ca49132781` | Narrator Man | Male | Authoritative, steady | Tutorials, professional |
| `248be419-c632-4f23-adf1-5324ed7dbf1d` | Professional Woman | Female | Professional, calm | Healthcare, appointment booking |
| `421b3369-f63f-4b03-8980-37a44df1d4e8` | Southern Woman | Female | Warm, friendly, southern accent | Real estate, hospitality |
| `fb26447f-308b-471e-8b00-341d93412d00` | Sportsman | Male | Energetic, confident | Fitness, sports, high-energy sales |
| `63ff761f-c1e8-414b-b969-ae73f7e1b90c` | Sweet Lady | Female | Gentle, warm | Healthcare, wellness, therapy intake |
| `e00d0e4c-a5c8-443f-a8a3-473eb9a62355` | Yoga Man | Male | Calm, soothing | Wellness, meditation, therapy |

## When to Choose Cartesia

1. **You need per-utterance emotion control.** This is the primary reason to choose Cartesia. If the agent needs to shift between calm, sympathetic, and happy within a single call, Cartesia is the best option.
2. **Latency is critical.** Cartesia Sonic-3 has among the lowest latency of all providers.
3. **Healthcare or sensitive use cases.** The combination of sympathetic/calm emotions with professional voices makes Cartesia ideal for patient-facing agents.
4. **Debt collection.** Calm emotion + professional voice = firm but not aggressive.

## When NOT to Choose Cartesia

- You need voice cloning (choose ElevenLabs)
- You need pronunciation dictionaries (choose ElevenLabs Turbo v2)
- You need maximum voice variety (ElevenLabs has a larger catalog)
- You need 40+ languages (choose MiniMax)
- Budget is the primary concern (OpenAI is cheaper)

## Voice Temperature and Speed

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| `voice_temperature` | 0-2 | 1.0 | Works in combination with `voice_emotion` -- keep temperature moderate (0.5-1.0) when using emotion to avoid unpredictable results |
| `voice_speed` | 0.5-2.0 | 1.0 | Cartesia handles speed changes well; stays natural within 0.7-1.3 range |

### Tip: Temperature + Emotion Interaction

When using `voice_emotion`, keep `voice_temperature` between 0.5 and 0.8. High temperature combined with emotion can produce exaggerated or inconsistent output. The emotion parameter already adds expressiveness, so lower temperature provides better control.

## enable_dynamic_voice_speed

All Cartesia voices support `enable_dynamic_voice_speed: true`. When enabled, the agent automatically matches the caller's speaking pace — faster for fast-talkers, slower for deliberate speakers. Recommended: enable for all templates.
