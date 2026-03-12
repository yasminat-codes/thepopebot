# Voice Temperature and Speed Tuning Guide

## Voice Temperature

The `voice_temperature` parameter in the Retell API controls how varied and expressive the speech output sounds. It applies to all providers.

### Range: 0 to 2

| Range | Label | Effect | Best For |
|-------|-------|--------|----------|
| 0.0-0.3 | Very Low | Extremely consistent, almost robotic. Minimal variation between utterances. | Automated announcements, IVR menus, system notifications |
| 0.3-0.5 | Low | Stable and predictable. Professional tone with little deviation. | Medical, legal, financial, debt collection, surveys |
| 0.5-0.7 | Medium-Low | Balanced consistency with subtle natural variation. | Receptionist, appointment booking, corporate support |
| 0.7-1.0 | Medium | Natural variation, warm delivery. Sounds conversational. | Sales, personal assistants, general support |
| 1.0-1.2 | Medium-High | Expressive, dynamic. Noticeable tonal shifts between sentences. | Energetic sales, coaching, entertainment |
| 1.2-1.5 | High | Highly expressive, varied pacing and emphasis. | Casual chat, creative content, storytelling |
| 1.5-2.0 | Very High | Unpredictable, exaggerated expression. Risk of inconsistency. | Rarely recommended. Testing or novelty use only. |

### Default: 1.0

A temperature of 1.0 works well for most general-purpose agents. Only adjust when you have a specific reason.

## Voice Speed

The `voice_speed` parameter controls how fast the agent speaks. It applies to all providers.

### Range: 0.5 to 2.0

| Range | Label | Effect | Best For |
|-------|-------|--------|----------|
| 0.5-0.7 | Very Slow | Deliberate, careful pacing. Each word gets emphasis. | Elderly callers, complex instructions, accessibility |
| 0.7-0.85 | Slow | Measured pace, easy to follow. | Healthcare, legal disclaimers, technical explanations |
| 0.85-1.0 | Normal | Natural conversational speed. | Most use cases |
| 1.0-1.1 | Slightly Fast | Energetic but still clear. | Outbound sales, young demographics |
| 1.1-1.3 | Fast | Quick delivery, efficient. | Callbacks, quick transactions, confirmations |
| 1.3-2.0 | Very Fast | Rapid speech. Risks clarity and comprehension. | Rarely recommended. Testing only. |

### Default: 1.0

## Recommended Settings by Template

| Template | Temperature | Speed | Reasoning |
|----------|-------------|-------|-----------|
| Sales | 0.8 | 1.0 | Warm and expressive to build rapport, normal pace for clarity |
| Support | 0.6 | 0.9 | Consistent and calm, slightly slower for patience |
| Appointment Booking | 0.6 | 1.0 | Professional and efficient, standard pace |
| Receptionist | 0.6 | 1.0 | Steady and welcoming, standard pace |
| Personal Assistant | 0.8 | 1.0 | Natural and conversational |
| Lead Qualifier | 0.6 | 1.0 | Professional and direct |
| Survey | 0.5 | 0.9 | Neutral and measured, slightly slower for question clarity |
| Debt Collection | 0.5 | 0.9 | Firm and consistent, measured pace conveys seriousness |
| Real Estate | 0.8 | 1.0 | Warm and enthusiastic |
| Healthcare | 0.5 | 0.85 | Calm and steady, slower for comprehension |

## Provider-Specific Notes

### ElevenLabs
Temperature maps to the inverse of the underlying `stability` parameter. Low temperature = high stability. ElevenLabs voices are the most responsive to temperature changes.

### OpenAI
Temperature effects are subtler. OpenAI voices maintain consistency across a wider temperature range. Noticeable differences appear mainly at extremes (below 0.3 or above 1.5).

### Cartesia
When using `voice_emotion`, keep temperature between 0.5-0.8. The emotion parameter already adds expressiveness. High temperature + emotion = exaggerated, inconsistent output.

### MiniMax
Same guidance as Cartesia when using emotion. Without emotion, temperature behaves similarly to ElevenLabs.

### Deepgram
Temperature effects are moderate. Deepgram voices are naturally consistent, so adjustments are less dramatic than ElevenLabs.

## Tuning Tips

1. **Start at 1.0 and adjust.** Do not guess -- listen to the voice with your actual prompt content before changing settings.
2. **Adjust temperature first, then speed.** Temperature has a larger impact on perceived quality.
3. **Test with real conversation flows.** A voice that sounds great reading a script may sound different in a back-and-forth dialogue.
4. **Match temperature to audience.** Older or professional audiences prefer lower temperature (consistency). Younger or casual audiences tolerate higher temperature (expressiveness).
5. **Never go above 1.5 in production.** Temperatures above 1.5 produce unreliable results across all providers.
