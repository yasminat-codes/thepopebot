---
name: humanization-engine
description: Makes voice agents sound human by adding pauses, filler words, backchannel sounds, ambient noise, voice emotion, and natural speech patterns. Uses a 1-10 humanization scale with template-specific defaults. Use when agent sounds robotic, too perfect, monotone, or unnatural. Also use when asked to "make it sound more human", "add pauses", "add filler words", or "change ambient sound".
allowed-tools: Read Write Bash(python3:*)
---

# Humanization Engine

## Overview

A perfectly articulated, zero-latency, never-hesitating voice agent sounds like a robot.
Real humans pause to think, say "um" and "uh", make small sounds to show they are listening,
and exist in environments with background noise. This sub-skill adds those human qualities
to a Retell AI voice agent.

The six humanization levers:

| Lever | What It Controls | Retell Parameter |
|-------|-----------------|------------------|
| Backchannel | "mhm", "yeah", "I see" while listening | `enable_backchannel`, `backchannel_frequency`, `backchannel_words` |
| Filler Words | "um", "uh", "well", "so" while speaking | Prompt injection |
| Pauses | Thinking pauses, dramatic pauses | Dash patterns in prompt |
| Ambient Sound | Background noise (coffee shop, call center) | `ambient_sound`, `ambient_sound_volume` |
| Voice Emotion | Tone of voice (happy, calm, sympathetic) | `voice_emotion` (Cartesia/MiniMax only) |
| Voice Temperature | How varied/expressive the speech is | `voice_temperature` [0-2] |

Each lever can be configured independently, but this sub-skill provides a unified
1-10 humanization scale that sets all levers coherently.


## Quick Start

Set the humanization level for an agent in two steps:

1. **Choose a level** -- Use the template default or pick 1-10 based on how human you want it
2. **Generate config** -- Run the humanization calculator to get all parameter values

That is it. The calculator outputs both Retell config parameters and prompt instructions
that work together to create the desired humanization level.


## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| humanization_level | integer (1-10) | no | Overall humanization level; defaults to template default |
| template_name | string | no | Agent template name for default level lookup |
| voice_provider | string | no | Current voice provider (affects emotion support) |
| voice_model | string | no | Current voice model |
| overrides | object | no | Override specific levers: backchannel, fillers, pauses, ambient, emotion, temperature |

### Override Object Structure

```json
{
  "backchannel": {"enabled": true, "frequency": 0.6, "words": ["mhm", "right"]},
  "fillers": {"frequency": "medium", "types": ["hesitation", "transition"]},
  "pauses": {"frequency": "medium", "style": "thinking"},
  "ambient": {"sound": "coffee-shop", "volume": 0.5},
  "emotion": "calm",
  "temperature": 0.8
}
```


## Outputs

| Parameter | Type | Description |
|-----------|------|-------------|
| config_params | object | Retell API parameters to set on the agent |
| prompt_instructions | string | Text to inject into the agent prompt |
| humanization_level | integer | The effective level used (from input or template default) |
| lever_summary | object | Summary of what each lever is set to |
| notes | string | Explanation of choices made |

### config_params Structure

```json
{
  "enable_backchannel": true,
  "backchannel_frequency": 0.6,
  "backchannel_words": ["mhm", "yeah", "I see", "right"],
  "ambient_sound": "coffee-shop",
  "ambient_sound_volume": 0.5,
  "voice_temperature": 0.8,
  "voice_emotion": "calm",
  "responsiveness": 0.8,
  "interruption_sensitivity": 0.7
}
```


## The Humanization Scale

The 1-10 scale provides a unified way to control all humanization levers at once.

| Level | Label | Description |
|-------|-------|-------------|
| 1 | Robotic | Zero humanization. Clean, precise, corporate. No fillers, no ambient, no backchannel. |
| 2 | Minimal | Very slight warmth. Occasional pause. Low temperature. Professional IVR feel. |
| 3 | Clean | Rare pauses before important info. Minimal backchannel. Corporate formal. |
| 4 | Professional | Occasional backchannel. Brief thinking pauses. Warm but controlled. |
| 5 | Natural | Fillers every 3-4 sentences. Backchannel active. Slight ambient maybe. Balanced. |
| 6 | Conversational | Regular fillers. Self-corrections occasionally. Backchannel moderate. Warm tone. |
| 7 | Human | Frequent fillers and pauses. Thinking sounds. Ambient on. Emotional variation. |
| 8 | Very Human | Heavy fillers. Self-corrections. Ambient always. High emotion. Casual tone. |
| 9 | Ultra-Human | Stuttering occasionally. Strong ambient. Very high emotion. Very casual. |
| 10 | Maximum | Everything maxed. Heavy stuttering, constant fillers, loud ambient. Use with caution. |

For detailed parameter values at each level, see [HUMANIZATION-SCALE.md](references/HUMANIZATION-SCALE.md).


## Phase 1: Determine Humanization Level

### From Template Default

If a `template_name` is provided and no `humanization_level` is specified, use the
template default:

| Template | Default Level | Rationale |
|----------|--------------|-----------|
| Sales | 6 | Conversational and warm, builds rapport |
| Support | 5 | Natural and patient, not too casual |
| Appointment | 5 | Natural, efficient but friendly |
| Receptionist | 4 | Professional, clean, reliable |
| Personal Assistant | 7 | Human, warm, like talking to a real person |
| Lead Qualifier | 4 | Professional, focused, efficient |
| Survey | 3 | Clean, neutral, does not influence responses |
| Debt Collection | 3 | Clean, serious, professional but not robotic |
| Real Estate | 7 | Very human, warm, builds trust and rapport |

### From User Override

If the user specifies a humanization level directly, use that level regardless of template.

### From Contextual Clues

If neither is provided, infer from the conversation:
- "Make it sound more natural" -> increase by 2 levels
- "Make it sound more professional" -> decrease by 2 levels
- "Add filler words" -> increase fillers specifically
- "Remove the background noise" -> set ambient to none
- "Make it warmer" -> increase temperature and emotion


## Phase 2: Configure Each Lever

For each lever, apply the settings based on the humanization level:

### Backchannel Configuration

| Level Range | enable_backchannel | backchannel_frequency | backchannel_words |
|-------------|-------------------|----------------------|-------------------|
| 1-2 | false | N/A | N/A |
| 3-4 | true | 0.2-0.4 | ["mhm", "I see"] |
| 5-6 | true | 0.5-0.6 | ["mhm", "yeah", "I see", "right"] |
| 7-8 | true | 0.7-0.8 | ["mhm", "yeah", "I see", "right", "oh okay", "got it"] |
| 9-10 | true | 0.9-1.0 | ["mhm", "yeah", "I see", "right", "oh okay", "got it", "uh-huh", "for sure"] |

Full reference: [BACKCHANNEL-GUIDE.md](references/BACKCHANNEL-GUIDE.md)

### Filler Word Configuration

Filler words are injected through prompt instructions, not API parameters.

| Level Range | Frequency | Types | Example |
|-------------|-----------|-------|---------|
| 1-2 | None | N/A | (no fillers) |
| 3-4 | Rare | Transitions only | "So," "Well," |
| 5-6 | Occasional | Transitions + hesitations | "Um," "Well," "So," |
| 7-8 | Regular | All types | "Um," "Uh," "Well," "You know," "Let me see," |
| 9-10 | Frequent | All types + self-corrections | "Um," "Uh," "Actually wait," "I mean," |

Full reference: [FILLER-WORDS-GUIDE.md](references/FILLER-WORDS-GUIDE.md)

### Pause Configuration

Pauses are created through dash patterns in the prompt and responsiveness settings.

| Level Range | responsiveness | Pause Style |
|-------------|---------------|-------------|
| 1-2 | 1.0 | No pauses, immediate responses |
| 3-4 | 0.9 | Brief pauses before key info |
| 5-6 | 0.8 | Natural thinking pauses |
| 7-8 | 0.6-0.7 | Frequent thinking pauses, longer consideration |
| 9-10 | 0.4-0.5 | Heavy pauses, slow deliberate speech |

Full reference: [PAUSE-TIMING-GUIDE.md](references/PAUSE-TIMING-GUIDE.md)

### Ambient Sound Configuration

| Level Range | ambient_sound | ambient_sound_volume |
|-------------|--------------|---------------------|
| 1-3 | null (none) | N/A |
| 4-5 | Optional, context-dependent | 0.3-0.5 |
| 6-7 | Recommended | 0.5-0.8 |
| 8-9 | Always on | 0.8-1.2 |
| 10 | Always on | 1.2-1.5 |

Ambient sound selection by context:
- Office/corporate -> `call-center`
- Casual/friendly -> `coffee-shop`
- Outdoor/relaxed -> `summer-outdoor` or `mountain-outdoor`
- Busy/energetic -> `convention-hall`
- Phone-call feel -> `static-noise`

Full reference: [AMBIENT-SOUND-GUIDE.md](references/AMBIENT-SOUND-GUIDE.md)

### Voice Emotion Configuration

**Important:** `voice_emotion` only works with Cartesia and MiniMax voice providers.

| Level Range | voice_emotion | Notes |
|-------------|--------------|-------|
| 1-3 | null | No emotion setting |
| 4-5 | "calm" | Steady and professional |
| 6-7 | Context-dependent | "happy" for sales, "sympathetic" for support |
| 8-10 | Strong emotion | Match to conversation purpose |

Emotion mapping by template:
- Sales -> "happy"
- Support -> "sympathetic"
- Appointment -> "calm"
- Receptionist -> "calm"
- Personal Assistant -> "happy"
- Debt Collection -> "calm"
- Real Estate -> "happy"

Full reference: [VOICE-EMOTION-GUIDE.md](references/VOICE-EMOTION-GUIDE.md)

### Voice Temperature Configuration

| Level Range | voice_temperature | Effect |
|-------------|------------------|--------|
| 1-2 | 0.3-0.4 | Very stable, almost monotone |
| 3-4 | 0.5-0.6 | Stable with slight variation |
| 5-6 | 0.7-0.8 | Natural variation |
| 7-8 | 0.9-1.1 | Expressive, varied |
| 9-10 | 1.2-1.5 | Highly expressive, unpredictable |

Full reference: [VOICE-TEMPERATURE-GUIDE.md](references/VOICE-TEMPERATURE-GUIDE.md) (part of voice-selector sub-skill)


## Phase 3: Generate Prompt Instructions

Based on the humanization level, generate prompt text that instructs the agent to
speak naturally. This text is appended to the agent's system prompt.

### Level 1-2 Prompt Addition
```
Speak clearly and precisely. Do not use filler words. Respond promptly.
```

### Level 3-4 Prompt Addition
```
Speak in a professional and warm tone. You may occasionally pause briefly
before sharing important information. Use transitional phrases like "So,"
and "Well," sparingly.
```

### Level 5-6 Prompt Addition
```
Speak naturally, like a friendly professional. Use occasional filler words
like "um" and "well" to sound more human. Pause briefly when thinking.
Show warmth in your voice. You can say things like "That's a great question,
let me think about that for a moment."
```

### Level 7-8 Prompt Addition
```
Speak like a real person having a genuine conversation. Use filler words
naturally -- "um", "uh", "you know", "let me see". Pause when thinking.
Occasionally correct yourself: "The appointment is at 3 -- actually, 3:30."
Show genuine emotion and interest. React naturally to what the caller says.
Take your time responding, as if you are actually thinking about the answer.
```

### Level 9-10 Prompt Addition
```
Speak exactly like a real person. Use lots of natural fillers -- "um", "uh",
"like", "you know what I mean". Pause frequently. Correct yourself sometimes.
Occasionally stumble slightly on words. React with genuine surprise, empathy,
or enthusiasm. Take your time, think out loud: "Hmm, let me pull that up...
okay so... yeah, I see it here." Sound like you are multitasking. Be casual
and authentic above all else.
```


## Phase 4: Generate Config Parameters

Combine all lever values into a single configuration output:

```json
{
  "config_params": {
    "enable_backchannel": true,
    "backchannel_frequency": 0.6,
    "backchannel_words": ["mhm", "yeah", "I see", "right"],
    "ambient_sound": "coffee-shop",
    "ambient_sound_volume": 0.5,
    "voice_temperature": 0.8,
    "voice_emotion": "happy",
    "responsiveness": 0.8,
    "interruption_sensitivity": 0.7
  },
  "prompt_instructions": "Speak naturally, like a friendly professional...",
  "humanization_level": 6,
  "lever_summary": {
    "backchannel": "moderate (freq 0.6, 4 words)",
    "fillers": "occasional (transitions + hesitations)",
    "pauses": "natural thinking pauses",
    "ambient": "coffee-shop at 50% volume",
    "emotion": "happy (Cartesia/MiniMax only)",
    "temperature": "0.8 (natural variation)"
  },
  "notes": "Level 6 (Conversational) applied for Sales template. Optimized for rapport building."
}
```


## Template Default Table

Complete table of default humanization settings per template:

| Template | Level | Backchannel | Fillers | Ambient | Emotion | Temperature |
|----------|-------|-------------|---------|---------|---------|-------------|
| Sales | 6 | On (0.6) | Occasional | coffee-shop | happy | 0.8 |
| Support | 5 | On (0.5) | Occasional | none | sympathetic | 0.7 |
| Appointment | 5 | On (0.5) | Occasional | none | calm | 0.7 |
| Receptionist | 4 | On (0.3) | Rare | none | calm | 0.6 |
| Personal Assistant | 7 | On (0.7) | Regular | coffee-shop | happy | 0.9 |
| Lead Qualifier | 4 | On (0.3) | Rare | none | calm | 0.6 |
| Survey | 3 | On (0.2) | None | none | null | 0.5 |
| Debt Collection | 3 | On (0.2) | None | none | calm | 0.5 |
| Real Estate | 7 | On (0.7) | Regular | coffee-shop | happy | 0.9 |


## Real-World Scenarios

### Scenario 1: Sales Agent Sounds Too Robotic

**Problem:** A sales agent at level 4 sounds too stiff and is not building rapport.

**Input:**
```json
{
  "humanization_level": 7,
  "template_name": "Sales",
  "voice_provider": "Cartesia"
}
```

**Output:**
```json
{
  "config_params": {
    "enable_backchannel": true,
    "backchannel_frequency": 0.7,
    "backchannel_words": ["mhm", "yeah", "I see", "right", "oh okay", "got it"],
    "ambient_sound": "coffee-shop",
    "ambient_sound_volume": 0.6,
    "voice_temperature": 0.9,
    "voice_emotion": "happy",
    "responsiveness": 0.7,
    "interruption_sensitivity": 0.7
  },
  "prompt_instructions": "Speak like a real person having a genuine conversation...",
  "humanization_level": 7,
  "notes": "Increased from default 6 to 7 for warmer rapport. Cartesia supports voice_emotion."
}
```

### Scenario 2: Survey Agent Needs to Stay Neutral

**Problem:** A survey agent should be clean and neutral but not cold.

**Input:**
```json
{
  "template_name": "Survey",
  "voice_provider": "OpenAI"
}
```

**Output:**
```json
{
  "config_params": {
    "enable_backchannel": true,
    "backchannel_frequency": 0.2,
    "backchannel_words": ["mhm", "I see"],
    "ambient_sound": null,
    "ambient_sound_volume": null,
    "voice_temperature": 0.5,
    "responsiveness": 0.9,
    "interruption_sensitivity": 0.8
  },
  "prompt_instructions": "Speak clearly and precisely. Do not use filler words...",
  "humanization_level": 3,
  "notes": "Survey default level 3. OpenAI does not support voice_emotion. Minimal humanization to avoid influencing survey responses."
}
```

### Scenario 3: Personal Assistant with Custom Overrides

**Problem:** User wants a personal assistant that sounds very human but without ambient noise.

**Input:**
```json
{
  "humanization_level": 8,
  "template_name": "Personal Assistant",
  "voice_provider": "ElevenLabs",
  "overrides": {
    "ambient": {"sound": null, "volume": null}
  }
}
```

**Output:**
```json
{
  "config_params": {
    "enable_backchannel": true,
    "backchannel_frequency": 0.8,
    "backchannel_words": ["mhm", "yeah", "I see", "right", "oh okay", "got it"],
    "ambient_sound": null,
    "ambient_sound_volume": null,
    "voice_temperature": 1.1,
    "responsiveness": 0.6,
    "interruption_sensitivity": 0.6
  },
  "prompt_instructions": "Speak like a real person having a genuine conversation...",
  "humanization_level": 8,
  "notes": "Level 8 with ambient sound disabled per user override. ElevenLabs does not support voice_emotion parameter."
}
```


## Decision Tree: When to Adjust Each Lever

```
Agent sounds too robotic?
  |
  YES --> Which aspect is the problem?
  |         |
  |         Monotone voice ---------> Increase voice_temperature
  |         |
  |         Too fast/immediate -----> Decrease responsiveness, add pauses
  |         |
  |         Not reacting to caller -> Enable/increase backchannel
  |         |
  |         Too formal speech ------> Add filler words via prompt
  |         |
  |         Sounds like a recording -> Add ambient_sound
  |         |
  |         No emotion -------------> Set voice_emotion (Cartesia/MiniMax)
  |
  NO --> Agent sounds too casual?
           |
           YES --> Decrease humanization level
           |       Remove fillers, reduce backchannel, remove ambient
           |
           NO --> Agent sounds good. No changes needed.
```


## Resource Reference Map

| Resource | Path | Description |
|----------|------|-------------|
| Backchannel Guide | [BACKCHANNEL-GUIDE.md](references/BACKCHANNEL-GUIDE.md) | Full backchannel config |
| Filler Words Guide | [FILLER-WORDS-GUIDE.md](references/FILLER-WORDS-GUIDE.md) | Filler injection patterns |
| Pause Timing Guide | [PAUSE-TIMING-GUIDE.md](references/PAUSE-TIMING-GUIDE.md) | Dash patterns and timing |
| Ambient Sound Guide | [AMBIENT-SOUND-GUIDE.md](references/AMBIENT-SOUND-GUIDE.md) | All 6 ambient sounds |
| Voice Emotion Guide | [VOICE-EMOTION-GUIDE.md](references/VOICE-EMOTION-GUIDE.md) | Emotion parameter usage |
| Humanization Scale | [HUMANIZATION-SCALE.md](references/HUMANIZATION-SCALE.md) | Complete 1-10 scale |
| Calculator Script | [scripts/humanization-calculator.py](scripts/humanization-calculator.py) | Auto-generate config |


## Integration with Orchestrator

This sub-skill's output feeds into two places:

### Config Parameters -> agent-config-builder

The `config_params` object is merged into the agent configuration:

```json
{
  "enable_backchannel": true,
  "backchannel_frequency": 0.6,
  "backchannel_words": ["mhm", "yeah", "I see", "right"],
  "ambient_sound": "coffee-shop",
  "ambient_sound_volume": 0.5,
  "voice_temperature": 0.8,
  "voice_emotion": "happy",
  "responsiveness": 0.8,
  "interruption_sensitivity": 0.7
}
```

### Prompt Instructions -> prompt-generator

The `prompt_instructions` string is appended to the agent's system prompt as a
dedicated section:

```
## Speech Style
Speak naturally, like a friendly professional. Use occasional filler words
like "um" and "well" to sound more human...
```

### Data Flow

```
User request (or template default)
    |
    v
humanization-engine (this sub-skill)
    |
    +--> config_params --> agent-config-builder --> Retell agent config
    |
    +--> prompt_instructions --> prompt-generator --> agent prompt
```


## Troubleshooting

### Backchannel Sounds Unnatural

- Reduce `backchannel_frequency` by 0.1-0.2
- Remove unusual backchannel words, keep only "mhm" and "I see"
- Some voices handle backchannel better than others -- test with the specific voice

### Filler Words Are Overused

- Reduce filler frequency in the prompt: change "frequently" to "occasionally"
- Remove self-correction patterns
- Keep only simple fillers like "um" and "well"

### Ambient Sound Is Distracting

- Reduce `ambient_sound_volume` by 0.2-0.3
- Try a different ambient sound (e.g., switch from convention-hall to coffee-shop)
- For phone calls, `static-noise` at low volume adds realism without distraction

### Voice Emotion Not Working

- Verify the provider is Cartesia or MiniMax (only providers that support `voice_emotion`)
- If using ElevenLabs, OpenAI, or Deepgram, achieve emotion through prompt instructions
  and `voice_temperature` instead
