# MiniMax Voice Catalog for Retell AI

## Provider Configuration

- **Provider name in Retell:** `minimax`
- **Key differentiators:** Voice emotion support, 40+ language support, voice cloning
- **Voice emotion:** Supported (same set as Cartesia)
- **Pronunciation dictionary:** Not supported
- **Voice cloning:** Supported

## Voice Emotion Support

MiniMax shares the same emotion parameter set as Cartesia:

| Emotion | Effect |
|---------|--------|
| `calm` | Steady, relaxed delivery |
| `sympathetic` | Compassionate, understanding |
| `happy` | Upbeat, positive |
| `sad` | Subdued, empathetic |
| `angry` | Firm, intense |
| `fearful` | Urgent, concerned |
| `surprised` | Excited, reactive |

## Voice Catalog

| Voice ID | Name | Gender | Tone | Best Use Cases |
|----------|------|--------|------|----------------|
| `minimax-Wise_Woman` | Wise Woman | Female | Mature, calm, authoritative | Healthcare, legal, financial advice |
| `minimax-Friendly_Person` | Friendly Person | Neutral | Warm, approachable | General assistant, support, onboarding |
| `minimax-Inspirational_girl` | Inspirational Girl | Female | Energetic, motivating | Sales, fitness, coaching |
| `minimax-Deep_Voice_Man` | Deep Voice Man | Male | Deep, commanding | Legal, debt collection, executive |
| `minimax-Calm_Woman` | Calm Woman | Female | Soothing, gentle | Healthcare, wellness, therapy intake |
| `minimax-Lively_Girl` | Lively Girl | Female | Youthful, bubbly | Casual bookings, entertainment, social |
| `minimax-Patient_Man` | Patient Man | Male | Calm, steady, patient | Support, appointment booking, onboarding |
| `minimax-Young_Knight` | Young Knight | Male | Confident, professional | B2B sales, lead qualification |
| `minimax-Determined_Man` | Determined Man | Male | Firm, direct, confident | Outbound sales, debt collection |
| `minimax-Gentle_Woman` | Gentle Woman | Female | Warm, nurturing | Wellness, patient follow-up, elderly care |

## Multilingual Strength

MiniMax supports 40+ languages, making it the broadest multilingual provider in the Retell ecosystem.

### Key Language Groups

- **European:** English, Spanish, French, German, Italian, Portuguese, Dutch, Polish, Swedish, Norwegian, Danish, Finnish, Greek, Czech, Romanian, Hungarian, Bulgarian, Croatian, Slovak, Lithuanian, Latvian, Estonian, Slovenian
- **Asian:** Mandarin Chinese, Japanese, Korean, Thai, Vietnamese, Indonesian, Malay, Filipino, Hindi, Bengali, Tamil, Telugu, Urdu
- **Middle Eastern:** Arabic, Turkish, Hebrew, Persian
- **African:** Swahili, Hausa, Yoruba

### When Multilingual Matters

- International businesses serving customers in multiple languages
- Non-English-primary markets where other providers have limited support
- Multilingual agents that need to switch languages mid-conversation

## When to Choose MiniMax

1. **You need voice emotion AND multilingual support.** MiniMax is the only provider offering both emotion control and 40+ languages.
2. **Non-English voice agents.** For languages where ElevenLabs or OpenAI quality drops off, MiniMax may perform better.
3. **Voice cloning in non-English languages.** ElevenLabs cloning is English-optimized; MiniMax handles non-English cloning better.
4. **Budget-conscious emotion support.** If you need emotion but Cartesia pricing does not work, MiniMax is an alternative.

## When NOT to Choose MiniMax

- You need pronunciation dictionaries (choose ElevenLabs Turbo v2)
- You need maximum English voice quality (ElevenLabs is superior for English)
- You need the largest English voice catalog (ElevenLabs has more options)
- You need the absolute lowest latency (Cartesia is faster)
- You want the most battle-tested provider (MiniMax is newer with less production track record)

## Voice Temperature and Speed

| Parameter | Range | Default | Notes |
|-----------|-------|---------|-------|
| `voice_temperature` | 0-2 | 1.0 | Like Cartesia, keep moderate (0.5-0.8) when using emotion |
| `voice_speed` | 0.5-2.0 | 1.0 | Natural range: 0.8-1.2 |

## Recommended Voices by Template

| Template | Voice | Emotion | Why |
|----------|-------|---------|-----|
| Sales | Inspirational Girl / Young Knight | `happy` | Energetic and motivating |
| Support | Calm Woman / Patient Man | `sympathetic` | Understanding and patient |
| Appointment | Wise Woman / Patient Man | `calm` | Professional booking |
| Healthcare | Gentle Woman / Patient Man | `sympathetic` | Compassionate care |
| Debt Collection | Deep Voice Man / Determined Man | `calm` | Firm without aggression |
| Multilingual | Friendly Person | `calm` | Best cross-language consistency |
