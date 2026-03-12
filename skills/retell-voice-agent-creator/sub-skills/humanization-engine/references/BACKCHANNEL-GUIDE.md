# Backchannel Configuration Guide

## What Is Backchannel

Backchannel refers to the small sounds and words a listener makes to signal they are
paying attention: "mhm", "yeah", "I see", "right". In voice AI, enabling backchannel
makes the agent produce these sounds while the caller is speaking.

## Retell API Parameters

### enable_backchannel
- **Type:** boolean
- **Default:** false
- **Effect:** When true, the agent produces listening sounds while the caller speaks

### backchannel_frequency
- **Type:** float, range [0, 1]
- **Default:** 0.8
- **Effect:** How often backchannel sounds occur. 0 = rarely, 1 = very frequently
- **Note:** Only active when enable_backchannel is true

### backchannel_words
- **Type:** array of strings
- **Default:** Provider-dependent
- **Effect:** The specific words/sounds the agent uses for backchannel
- **Examples:** ["mhm", "yeah", "I see", "right", "okay", "got it", "uh-huh"]


## Configuration by Humanization Level

| Level | Enabled | Frequency | Words |
|-------|---------|-----------|-------|
| 1-2 | false | N/A | N/A |
| 3 | true | 0.2 | ["mhm"] |
| 4 | true | 0.3 | ["mhm", "I see"] |
| 5 | true | 0.5 | ["mhm", "yeah", "I see"] |
| 6 | true | 0.6 | ["mhm", "yeah", "I see", "right"] |
| 7 | true | 0.7 | ["mhm", "yeah", "I see", "right", "oh okay", "got it"] |
| 8 | true | 0.8 | ["mhm", "yeah", "I see", "right", "oh okay", "got it"] |
| 9 | true | 0.9 | ["mhm", "yeah", "I see", "right", "oh okay", "got it", "uh-huh", "for sure"] |
| 10 | true | 1.0 | ["mhm", "yeah", "I see", "right", "oh okay", "got it", "uh-huh", "for sure", "totally"] |


## Word Selection by Context

### Professional/Corporate
Use: "mhm", "I see", "right", "understood"
Avoid: "totally", "for sure", "uh-huh"

### Casual/Friendly
Use: "yeah", "oh okay", "got it", "uh-huh", "for sure"
Avoid: "understood", "certainly"

### Empathetic/Support
Use: "mhm", "I see", "I understand", "of course"
Avoid: "yeah", "totally"


## Provider-Specific Notes

### ElevenLabs
- Backchannel sounds natural with most voices
- Custom backchannel words work well
- Test with specific voice to verify quality

### OpenAI
- Backchannel works but can sound slightly mechanical
- Stick to simple words: "mhm", "yeah", "I see"

### Cartesia
- Excellent backchannel quality due to emotion support
- Can combine with voice_emotion for empathetic listening

### Deepgram
- Basic backchannel support
- Keep to simple words

### MiniMax
- Good backchannel support across languages
- Test with target language for quality


## When to Disable Backchannel

- Survey agents (backchannel can influence caller responses)
- IVR-style agents (callers expect silence while they speak)
- Very fast transactions (backchannel adds perceived time)
- When callers report the agent is "interrupting" them


## Testing Backchannel

1. Make a test call
2. Speak for 10-15 seconds without pausing
3. Listen for backchannel sounds
4. Adjust frequency: too often = distracting, too rare = agent seems absent
5. Adjust words: ensure they sound natural with the chosen voice
