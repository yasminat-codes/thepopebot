# Voice Emotion Guide

## Overview

The `voice_emotion` parameter controls the emotional tone of the agent's voice.
This is a powerful humanization lever but has significant provider limitations.

**Supported providers:** Cartesia and MiniMax ONLY.
All other providers (ElevenLabs, OpenAI, Deepgram, PlayHT, Fish Audio) do NOT support
this parameter. For those providers, achieve emotional tone through prompt instructions
and voice_temperature instead.

## Available Emotions

| Emotion | Description | Use Case |
|---------|-------------|----------|
| `calm` | Steady, relaxed, soothing | Support, receptionist, medical |
| `sympathetic` | Understanding, compassionate | Support, debt collection, complaints |
| `happy` | Upbeat, enthusiastic, warm | Sales, personal assistant, real estate |
| `sad` | Somber, gentle, subdued | Sensitive topics, bad news delivery |
| `angry` | Firm, assertive, intense | Almost never appropriate for agents |
| `fearful` | Uncertain, anxious | Almost never appropriate for agents |
| `surprised` | Excited, amazed, reactive | Reactions to good news, celebrations |

## Recommended Emotions by Template

| Template | Primary Emotion | Secondary Emotion | Notes |
|----------|----------------|-------------------|-------|
| Sales | happy | surprised | Happy builds rapport; surprised for reacting to caller's good news |
| Support | sympathetic | calm | Sympathetic for problems; calm for routine inquiries |
| Appointment | calm | happy | Calm for scheduling; happy for confirmations |
| Receptionist | calm | happy | Calm baseline; happy for greetings |
| Personal Assistant | happy | calm | Happy default; calm for serious topics |
| Lead Qualifier | calm | happy | Calm professionalism; happy when prospect is interested |
| Survey | calm | null | Neutral, do not influence responses |
| Debt Collection | calm | sympathetic | Calm authority; sympathetic when caller is distressed |
| Real Estate | happy | surprised | Happy for showings; surprised at good matches |

## Interaction with Voice Temperature

Emotion and temperature work together:

| Emotion | Recommended Temperature | Effect |
|---------|------------------------|--------|
| calm | 0.4-0.6 | Low temp keeps calm voice steady |
| sympathetic | 0.5-0.7 | Moderate temp adds warmth to sympathy |
| happy | 0.7-1.0 | Higher temp makes happiness sound natural |
| surprised | 0.8-1.2 | Higher temp for genuine surprise |
| sad | 0.4-0.6 | Low temp for controlled sadness |

## Configuring Emotion by Humanization Level

| Level | Emotion Setting |
|-------|----------------|
| 1-3 | null (no emotion) |
| 4-5 | Template primary emotion |
| 6-7 | Template primary emotion, stronger expression |
| 8-10 | Dynamic: primary for most, secondary for context shifts |

## Fallback for Non-Supported Providers

When using ElevenLabs, OpenAI, Deepgram, or other providers that do not support
voice_emotion, achieve emotional tone through:

### Prompt-Based Emotion

```
SPEAKING STYLE:
Speak with warmth and genuine enthusiasm. When the caller shares good news,
react with excitement. When they have a problem, speak with understanding
and compassion. Your tone should convey that you truly care about helping.
```

### Temperature-Based Emotion

- Calm effect -> lower temperature (0.4-0.6)
- Happy effect -> higher temperature (0.7-1.0)
- Sympathetic effect -> moderate temperature (0.5-0.7) + empathetic prompt

### Voice Selection

Choose voices that naturally convey the desired emotion:
- ElevenLabs "Rachel" -- naturally warm and friendly (happy/calm)
- ElevenLabs "Adam" -- naturally calm and authoritative (calm/professional)
- OpenAI "Coral" -- naturally warm (happy/friendly)
- OpenAI "Sage" -- naturally measured (calm/professional)

## Important Caveats

1. **Do not use angry or fearful** for customer-facing agents -- these create negative experiences
2. **Sad should be rare** -- only for delivering genuinely bad news, and even then, prefer sympathetic
3. **Surprised should be brief** -- a moment of reaction, not a sustained state
4. **Test with real conversations** -- emotions can sound exaggerated with certain voices
5. **One emotion at a time** -- the parameter sets a single emotional tone for the entire conversation
