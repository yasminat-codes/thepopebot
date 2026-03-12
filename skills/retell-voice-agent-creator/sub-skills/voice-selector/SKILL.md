---
name: voice-selector
description: Selects the optimal voice for a Retell AI agent based on use case, gender, accent, provider, and characteristics. Includes curated recommendations per template, live API verification, fallback voice auto-selection from different providers, and ElevenLabs voice cloning workflow. Use when user says "choose a voice", "change voice", "different voice", "clone voice", or needs voice recommendations.
allowed-tools: Read Write Bash(curl:*) Bash(python3:*)
---

# Voice Selector

## Overview

The voice is the single most important aspect of a voice agent's identity. The wrong voice
creates an immediate mismatch -- a deep authoritative male voice for a friendly yoga studio
receptionist, or a bubbly young voice for a law firm's intake line. Voice selection must
consider the use case, brand personality, target audience, and technical requirements.

This sub-skill handles:
- Recommending the best voice based on requirements
- Matching voices from a curated catalog of tested options
- Verifying voices exist via the Retell API
- Selecting fallback voices from different providers
- Configuring voice parameters (temperature, speed, emotion)
- Guiding through the ElevenLabs voice cloning workflow


## Quick Start

Get a voice recommendation in two steps:

1. **Define requirements** -- Gender, accent, use case, and any provider preference
2. **Run the matcher** -- The voice-matcher script returns voice_id, model, and fallbacks


## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| use_case | string | yes | What the agent does (sales, support, receptionist, etc.) |
| gender | enum | no | "male", "female", or "neutral"; defaults to template recommendation |
| accent | string | no | Desired accent (american, british, australian, neutral); defaults to "american" |
| provider_preference | string | no | Preferred provider (ElevenLabs, OpenAI, Cartesia, Deepgram, MiniMax, PlayHT) |
| language | string | no | Primary language code; defaults to "en" |
| characteristics | array | no | Desired voice traits: warm, authoritative, calm, energetic, young, mature |
| existing_voice_id | string | no | Current voice_id to find alternatives for |
| clone_voice | boolean | no | Whether to initiate voice cloning workflow |


## Outputs

| Parameter | Type | Description |
|-----------|------|-------------|
| voice_id | string | Recommended Retell voice ID |
| voice_model | string | Voice model identifier for the provider |
| voice_provider | string | Provider name |
| voice_temperature | float | Recommended temperature [0-2] |
| voice_speed | float | Recommended speed [0.5-2] |
| voice_emotion | string | Recommended emotion (if provider supports it) |
| fallback_voice_ids | array | 2-3 fallback voices from DIFFERENT providers |
| recommendation_reason | string | Why this voice was chosen |
| notes | string | Additional configuration notes |


## Phase 1: Gather Requirements

When selecting a voice, collect or infer these preferences:

### From the Template

Each template has a default voice recommendation:

| Template | Default Gender | Default Characteristics | Default Provider |
|----------|---------------|------------------------|------------------|
| Sales | female | warm, energetic, confident | ElevenLabs |
| Support | female | calm, patient, empathetic | ElevenLabs |
| Appointment | female | professional, clear, friendly | OpenAI |
| Receptionist | female | professional, warm, clear | ElevenLabs |
| Personal Assistant | female | warm, natural, conversational | ElevenLabs |
| Lead Qualifier | male | professional, confident, direct | OpenAI |
| Survey | neutral | neutral, clear, measured | OpenAI |
| Debt Collection | male | firm, professional, calm | Cartesia |
| Real Estate | female | warm, enthusiastic, trustworthy | ElevenLabs |

### From User Input

If the user specifies preferences, those override template defaults. Common requests:
- "I want a male voice" -> gender = male
- "British accent" -> accent = british
- "Something warm and friendly" -> characteristics = [warm, friendly]
- "Use ElevenLabs" -> provider_preference = ElevenLabs
- "Deep voice" -> characteristics = [deep, mature, authoritative]


## Phase 2: Match to Catalog

Use the curated voice catalog to find the best match. The catalog is organized by provider.

### Matching Algorithm

1. Filter by provider preference (if specified)
2. Filter by gender
3. Filter by accent
4. Score remaining voices by characteristic match
5. Return highest-scoring voice

### Curated Recommendations by Template

| Template | Voice | Provider | Voice ID | Why |
|----------|-------|----------|----------|-----|
| Sales | Rachel | ElevenLabs | 21m00Tcm4TlvDq8ikWAM | Warm, engaging, builds rapport |
| Support | Elli | ElevenLabs | MF3mGyEYCl7XYWbV9V6O | Calm, patient, clear |
| Appointment | Coral | OpenAI | openai-Coral | Professional, efficient |
| Receptionist | Rachel | ElevenLabs | 21m00Tcm4TlvDq8ikWAM | Warm, professional |
| Personal Assistant | Bella | ElevenLabs | EXAVITQu4vr4xnSDxMaL | Natural, conversational |
| Lead Qualifier | Adam | ElevenLabs | pNInz6obpgDQGcFmaJgB | Confident, professional |
| Survey | Sage | OpenAI | openai-Sage | Neutral, measured |
| Debt Collection | Sonic (Calm Male) | Cartesia | sonic-3-calm-male | Firm, steady, calm |
| Real Estate | Rachel | ElevenLabs | 21m00Tcm4TlvDq8ikWAM | Warm, trustworthy |

**Important:** Voice IDs can change. Always verify via API before using.

For detailed voice catalogs per provider, see:
- [ELEVENLABS-VOICES.md](references/ELEVENLABS-VOICES.md)
- [OPENAI-VOICES.md](references/OPENAI-VOICES.md)
- [CARTESIA-VOICES.md](references/CARTESIA-VOICES.md)
- [DEEPGRAM-VOICES.md](references/DEEPGRAM-VOICES.md)
- [MINIMAX-VOICES.md](references/MINIMAX-VOICES.md)


## Phase 3: Select Fallback Voice

Every agent MUST have fallback voices from DIFFERENT providers. If the primary provider
has an outage, the fallback ensures the agent stays operational.

### Fallback Selection Rules

1. **Different provider** -- Fallback must be from a different provider than primary
2. **Same gender** -- Match the gender of the primary voice
3. **Similar characteristics** -- Match as closely as possible
4. **Same language** -- Must support the same language

### Example Fallback Chain

Primary: Rachel (ElevenLabs, female, warm)
- Fallback 1: Coral (OpenAI, female, warm)
- Fallback 2: Sonic-3 Female (Cartesia, female, calm)

Primary: Adam (ElevenLabs, male, confident)
- Fallback 1: Ash (OpenAI, male, professional)
- Fallback 2: Sonic-3 Male (Cartesia, male, steady)

Full fallback strategy: [FALLBACK-VOICE-STRATEGY.md](references/FALLBACK-VOICE-STRATEGY.md)


## Phase 4: Configure Voice Parameters

After selecting the voice, configure these parameters:

### Voice Temperature

Controls how varied and expressive the speech sounds.

| Range | Effect | Best For |
|-------|--------|----------|
| 0.3-0.5 | Stable, consistent, predictable | Support, surveys, formal |
| 0.5-0.7 | Balanced, natural variation | Receptionists, appointments |
| 0.7-1.0 | Expressive, warm, dynamic | Sales, personal assistants |
| 1.0-1.5 | Highly expressive, unpredictable | Entertainment, casual |

Full guide: [VOICE-TEMPERATURE-GUIDE.md](references/VOICE-TEMPERATURE-GUIDE.md)

### Voice Speed

Controls how fast the agent speaks.

| Range | Effect | Best For |
|-------|--------|----------|
| 0.7-0.8 | Slow, deliberate | Elderly callers, complex info |
| 0.9-1.0 | Normal pace | Most use cases |
| 1.0-1.1 | Slightly fast | Energetic sales, young audience |
| 1.2-1.5 | Fast | Quick transactions, callbacks |

### Voice Emotion

Only available with Cartesia and MiniMax. See the humanization-engine sub-skill
for detailed emotion configuration.

### Parameter Recommendations by Template

| Template | Temperature | Speed | Emotion |
|----------|-------------|-------|---------|
| Sales | 0.8 | 1.0 | happy |
| Support | 0.6 | 0.9 | sympathetic |
| Appointment | 0.6 | 1.0 | calm |
| Receptionist | 0.6 | 1.0 | calm |
| Personal Assistant | 0.8 | 1.0 | happy |
| Lead Qualifier | 0.6 | 1.0 | calm |
| Survey | 0.5 | 0.9 | null |
| Debt Collection | 0.5 | 0.9 | calm |
| Real Estate | 0.8 | 1.0 | happy |


## Voice Provider Summary

| Provider | Strengths | Weaknesses | Emotion | Cloning | Languages |
|----------|-----------|------------|---------|---------|-----------|
| ElevenLabs | Best quality, IPA dictionaries, voice cloning | Higher cost | No | Yes | 29 |
| OpenAI | Cost-effective, reliable, consistent | Less expressive | No | No | Multi |
| Cartesia | Emotion support, low latency, fast | Fewer voices | Yes | No | Multi |
| Deepgram | Transcription accuracy, fast | Fewer voice options | No | No | Multi |
| MiniMax | 40 languages, emotion, cloning | Newer, less tested | Yes | Yes | 40 |
| PlayHT | Large voice library | Variable quality | No | Yes | Multi |
| Fish Audio | Growing library | Newest, least tested | No | Yes | Multi |

### Provider Selection Decision Tree

```
Need pronunciation dictionary (IPA)? ----YES----> ElevenLabs (Turbo v2)
  |NO
  v
Need voice emotion parameter? ----YES----> Cartesia or MiniMax
  |NO
  v
Need voice cloning? ----YES----> ElevenLabs (best quality) or MiniMax (40 languages)
  |NO
  v
Need 40+ languages? ----YES----> MiniMax
  |NO
  v
Budget-conscious? ----YES----> OpenAI
  |NO
  v
Need lowest latency? ----YES----> Cartesia
  |NO
  v
DEFAULT -----> ElevenLabs (best overall quality)
```


## Voice Cloning Workflow

ElevenLabs offers the highest quality voice cloning for Retell agents.

### Summary

1. Record a high-quality voice sample (1-5 minutes)
2. Upload to ElevenLabs via their API or dashboard
3. Generate a cloned voice and get the voice_id
4. Import the voice_id into Retell

### Requirements
- ElevenLabs Professional plan or higher
- Clean audio recording, minimal background noise
- At least 1 minute of speech (3-5 minutes recommended)
- Consistent tone and energy throughout the sample
- Legal consent from the voice owner

Full workflow: [VOICE-CLONING-GUIDE.md](references/VOICE-CLONING-GUIDE.md)


## Real-World Scenarios

### Scenario 1: Sales Agent for a Tech Startup

**Input:**
```json
{
  "use_case": "Sales",
  "gender": "female",
  "accent": "american",
  "characteristics": ["warm", "energetic", "young"],
  "provider_preference": "ElevenLabs"
}
```

**Output:**
```json
{
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "voice_model": "eleven_turbo_v2",
  "voice_provider": "ElevenLabs",
  "voice_temperature": 0.8,
  "voice_speed": 1.0,
  "voice_emotion": null,
  "fallback_voice_ids": [
    {"voice_id": "openai-Coral", "provider": "OpenAI", "model": "gpt-4o-mini-tts"},
    {"voice_id": "cartesia-female-warm", "provider": "Cartesia", "model": "sonic-3"}
  ],
  "recommendation_reason": "Rachel (ElevenLabs) is warm, engaging, and natural. Perfect for tech startup sales where rapport and enthusiasm matter.",
  "notes": "ElevenLabs does not support voice_emotion. Warmth achieved via temperature 0.8 and prompt instructions."
}
```

### Scenario 2: Law Firm Receptionist Needing British Accent

**Input:**
```json
{
  "use_case": "Receptionist",
  "gender": "female",
  "accent": "british",
  "characteristics": ["professional", "authoritative", "clear"]
}
```

**Output:**
```json
{
  "voice_id": "ThT5KcBeYPX3keUQqHPh",
  "voice_model": "eleven_turbo_v2",
  "voice_provider": "ElevenLabs",
  "voice_temperature": 0.5,
  "voice_speed": 0.95,
  "voice_emotion": null,
  "fallback_voice_ids": [
    {"voice_id": "openai-Sage", "provider": "OpenAI", "model": "gpt-4o-mini-tts"},
    {"voice_id": "cartesia-british-female", "provider": "Cartesia", "model": "sonic-3"}
  ],
  "recommendation_reason": "Dorothy (ElevenLabs) has a British accent with professional, clear diction. Appropriate for a law firm receptionist where authority and clarity are essential.",
  "notes": "Lower temperature (0.5) for consistent professional tone. Slightly slower speed for clarity."
}
```


## Decision Tree: Provider Selection

```
START: What are the requirements?
  |
  +--> Must have IPA pronunciation dictionary?
  |      YES --> ElevenLabs (eleven_turbo_v2 model only)
  |
  +--> Must have voice_emotion parameter?
  |      YES --> Cartesia or MiniMax
  |              |
  |              Need 40+ languages? --> MiniMax
  |              Otherwise --> Cartesia (lower latency)
  |
  +--> Must clone a specific voice?
  |      YES --> ElevenLabs (best quality)
  |              or MiniMax (if non-English)
  |
  +--> Need multilingual (40+ languages)?
  |      YES --> MiniMax
  |
  +--> Budget is the primary concern?
  |      YES --> OpenAI (most cost-effective)
  |
  +--> Latency is critical?
  |      YES --> Cartesia (fastest)
  |
  +--> No special requirements?
         DEFAULT --> ElevenLabs (best overall)
```


## Resource Reference Map

| Resource | Path | Description |
|----------|------|-------------|
| ElevenLabs Voices | [ELEVENLABS-VOICES.md](references/ELEVENLABS-VOICES.md) | Full ElevenLabs voice catalog |
| OpenAI Voices | [OPENAI-VOICES.md](references/OPENAI-VOICES.md) | Full OpenAI voice catalog |
| Cartesia Voices | [CARTESIA-VOICES.md](references/CARTESIA-VOICES.md) | Full Cartesia voice catalog |
| Deepgram Voices | [DEEPGRAM-VOICES.md](references/DEEPGRAM-VOICES.md) | Full Deepgram voice catalog |
| MiniMax Voices | [MINIMAX-VOICES.md](references/MINIMAX-VOICES.md) | Full MiniMax voice catalog |
| Temperature Guide | [VOICE-TEMPERATURE-GUIDE.md](references/VOICE-TEMPERATURE-GUIDE.md) | Temperature tuning |
| Cloning Guide | [VOICE-CLONING-GUIDE.md](references/VOICE-CLONING-GUIDE.md) | Voice cloning workflow |
| Fallback Strategy | [FALLBACK-VOICE-STRATEGY.md](references/FALLBACK-VOICE-STRATEGY.md) | Fallback selection logic |
| Matcher Script | [scripts/voice-matcher.py](scripts/voice-matcher.py) | Auto voice matching |


## Integration with Orchestrator

This sub-skill's outputs feed into the agent-config-builder:

### Voice Config -> agent-config-builder

```json
{
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "voice_model": "eleven_turbo_v2",
  "voice_temperature": 0.8,
  "voice_speed": 1.0,
  "fallback_voice_ids": ["openai-Coral", "cartesia-female-warm"]
}
```

### Voice Emotion -> humanization-engine

If the selected provider supports voice_emotion, pass that info to the humanization-engine
so it can set the appropriate emotion parameter.

### Pronunciation Support -> pronunciation-fixer

If the selected provider is ElevenLabs Turbo v2, the pronunciation-fixer can use IPA
dictionary entries. Otherwise, it falls back to prompt injection.

### Data Flow

```
User requirements
    |
    v
voice-selector (this sub-skill)
    |
    +--> voice_id, voice_model --> agent-config-builder --> Retell agent config
    |
    +--> voice_provider info --> humanization-engine (emotion support check)
    |
    +--> voice_provider info --> pronunciation-fixer (IPA support check)
    |
    +--> fallback_voice_ids --> agent-config-builder --> Retell agent config
```


## Troubleshooting

### Voice ID Not Found

- Voice IDs change when providers update their catalog
- Always verify via Retell API before setting
- Use the voice-matcher.py script with RETELL_API_KEY for live verification

### Voice Sounds Different Than Expected

- Check voice_temperature: too high = unpredictable, too low = flat
- Check voice_speed: may be too fast or slow for the content
- Test with the actual prompt content, not just test phrases
- Some voices sound different with long vs short utterances

### Wrong Accent

- Verify the voice actually has the stated accent (some are labeled incorrectly)
- Test with accent-specific phrases
- Consider a different voice from the same provider or a different provider

### Voice Cloning Quality Issues

- Ensure source recording is high quality (16-bit, 44.1kHz minimum)
- Remove background noise from the recording
- Record in a consistent tone (do not switch between casual and formal)
- Minimum 1 minute, recommended 3-5 minutes of speech
