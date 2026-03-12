# Humanization Scale: Complete 1-10 Reference

## Level 1: Robotic

**Label:** Robotic
**Description:** Zero humanization. Clean, precise, machine-like.

| Lever | Setting |
|-------|---------|
| Backchannel | Off |
| Fillers | None |
| Responsiveness | 1.0 |
| Interruption Sensitivity | 1.0 |
| Ambient Sound | None |
| Voice Emotion | None |
| Voice Temperature | 0.3 |

**Prompt addition:** "Speak clearly and precisely. Do not use filler words. Respond immediately."
**When to use:** IVR systems, automated announcements, information kiosks.


## Level 2: Minimal

**Label:** Minimal
**Description:** Barely perceptible warmth. Still very clean and corporate.

| Lever | Setting |
|-------|---------|
| Backchannel | Off |
| Fillers | None |
| Responsiveness | 1.0 |
| Interruption Sensitivity | 0.9 |
| Ambient Sound | None |
| Voice Emotion | None |
| Voice Temperature | 0.4 |

**Prompt addition:** "Speak clearly and professionally. Be warm but efficient."
**When to use:** Corporate voicemail, formal information lines.


## Level 3: Clean

**Label:** Clean
**Description:** Rare pauses. Very light backchannel. Professional and controlled.

| Lever | Setting |
|-------|---------|
| Backchannel | On, frequency 0.2, words: ["mhm"] |
| Fillers | None |
| Responsiveness | 0.9 |
| Interruption Sensitivity | 0.9 |
| Ambient Sound | None |
| Voice Emotion | None |
| Voice Temperature | 0.5 |

**Prompt addition:** "Speak in a professional tone. You may pause briefly before sharing important information."
**When to use:** Survey agents, formal business lines, debt collection.


## Level 4: Professional

**Label:** Professional
**Description:** Occasional backchannel. Brief thinking pauses. Warm but controlled.

| Lever | Setting |
|-------|---------|
| Backchannel | On, frequency 0.3, words: ["mhm", "I see"] |
| Fillers | Rare (transitions only) |
| Responsiveness | 0.9 |
| Interruption Sensitivity | 0.8 |
| Ambient Sound | Optional (low volume) |
| Voice Emotion | calm (if supported) |
| Voice Temperature | 0.6 |

**Prompt addition:** "Speak professionally with a warm undertone. Use transitional phrases like 'So,' and 'Well,' sparingly."
**When to use:** Receptionists, lead qualifiers, corporate agents.


## Level 5: Natural

**Label:** Natural
**Description:** Balanced natural speech. Occasional fillers. Backchannel active.

| Lever | Setting |
|-------|---------|
| Backchannel | On, frequency 0.5, words: ["mhm", "yeah", "I see"] |
| Fillers | Occasional (transitions + hesitations) |
| Responsiveness | 0.8 |
| Interruption Sensitivity | 0.8 |
| Ambient Sound | Optional |
| Voice Emotion | Template-dependent (if supported) |
| Voice Temperature | 0.7 |

**Prompt addition:** "Speak naturally. Use occasional filler words like 'um' and 'well'. Pause briefly when thinking."
**When to use:** Support agents, appointment scheduling, general-purpose.


## Level 6: Conversational

**Label:** Conversational
**Description:** Regular fillers. Moderate backchannel. Self-corrections occasionally.

| Lever | Setting |
|-------|---------|
| Backchannel | On, frequency 0.6, words: ["mhm", "yeah", "I see", "right"] |
| Fillers | Occasional-to-regular |
| Responsiveness | 0.8 |
| Interruption Sensitivity | 0.7 |
| Ambient Sound | Recommended (coffee-shop or context-dependent) |
| Voice Emotion | Template-dependent (if supported) |
| Voice Temperature | 0.8 |

**Prompt addition:** "Speak like a friendly professional. Use filler words naturally. Pause to think. Show warmth."
**When to use:** Sales agents, friendly service agents.


## Level 7: Human

**Label:** Human
**Description:** Frequent fillers and pauses. Thinking sounds. Ambient on. Emotional.

| Lever | Setting |
|-------|---------|
| Backchannel | On, frequency 0.7, words: ["mhm", "yeah", "I see", "right", "oh okay", "got it"] |
| Fillers | Regular (all types) |
| Responsiveness | 0.7 |
| Interruption Sensitivity | 0.7 |
| Ambient Sound | On (context-dependent) |
| Voice Emotion | Strong (if supported) |
| Voice Temperature | 0.9 |

**Prompt addition:** "Speak like a real person. Use 'um', 'uh', 'you know'. Pause when thinking. Correct yourself occasionally."
**When to use:** Personal assistants, real estate agents, relationship-focused roles.


## Level 8: Very Human

**Label:** Very Human
**Description:** Heavy fillers. Self-corrections. Ambient always on. High emotion.

| Lever | Setting |
|-------|---------|
| Backchannel | On, frequency 0.8, words: ["mhm", "yeah", "I see", "right", "oh okay", "got it"] |
| Fillers | Regular-to-frequent |
| Responsiveness | 0.6 |
| Interruption Sensitivity | 0.6 |
| Ambient Sound | Always on |
| Voice Emotion | Strong (if supported) |
| Voice Temperature | 1.1 |

**Prompt addition:** "Speak like a real person in a genuine conversation. Use fillers naturally. Think out loud. Be casual."
**When to use:** Highly personalized services, lifestyle brands, community-focused.


## Level 9: Ultra-Human

**Label:** Ultra-Human
**Description:** Occasional stuttering. Strong ambient. Very high emotion. Very casual.

| Lever | Setting |
|-------|---------|
| Backchannel | On, frequency 0.9, words: ["mhm", "yeah", "I see", "right", "oh okay", "got it", "uh-huh", "for sure"] |
| Fillers | Frequent |
| Responsiveness | 0.5 |
| Interruption Sensitivity | 0.5 |
| Ambient Sound | Always on, higher volume |
| Voice Emotion | Dynamic (if supported) |
| Voice Temperature | 1.3 |

**Prompt addition:** "Speak exactly like a real person. Lots of fillers. Correct yourself. Stumble occasionally. Be authentic."
**When to use:** Experimental, specific personas, entertainment.


## Level 10: Maximum

**Label:** Maximum
**Description:** Everything maxed. Use with extreme caution.

| Lever | Setting |
|-------|---------|
| Backchannel | On, frequency 1.0, words: (all available) |
| Fillers | Very frequent |
| Responsiveness | 0.4 |
| Interruption Sensitivity | 0.5 |
| Ambient Sound | Always on, high volume |
| Voice Emotion | Dynamic (if supported) |
| Voice Temperature | 1.5 |

**Prompt addition:** "Maximum natural speech. Heavy fillers, stuttering, thinking out loud, casual slang. Sound completely unscripted."
**When to use:** Demonstrations, testing, specific entertainment use cases. Not recommended for production.
