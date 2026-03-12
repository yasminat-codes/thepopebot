# Filler Words Guide

## Overview

Filler words are injected through the agent's system prompt, not through Retell API
parameters. The prompt instructs the agent when and how to use natural speech fillers.

## Types of Filler Words

### Hesitations
Words that signal thinking or processing:
- "um", "uh", "hmm", "er"
- Used before answering questions or when pausing to think

### Transitions
Words that connect thoughts naturally:
- "well", "so", "anyway", "you know", "I mean"
- Used to move between topics or introduce new information

### Thinking Sounds
Extended pauses with vocalization:
- "let me see...", "hmm let me think...", "okay so..."
- Used before complex answers or when looking up information

### Self-Corrections
Natural mistake-and-fix patterns:
- "The meeting is at 3 -- actually, 3:30"
- "We have ten -- no, twelve items available"
- Used sparingly to add authenticity


## Frequency by Humanization Level

| Level | Frequency | Types Used | Per-Response Average |
|-------|-----------|------------|---------------------|
| 1-2 | None | N/A | 0 fillers |
| 3-4 | Rare | Transitions only | 1 filler every 3-4 responses |
| 5-6 | Occasional | Transitions + Hesitations | 1 filler every 2 responses |
| 7-8 | Regular | All types | 1-2 fillers per response |
| 9-10 | Frequent | All types + Self-corrections | 2-3 fillers per response |


## Prompt Templates

### Rare Fillers (Level 3-4)
```
Occasionally use transitional phrases like "So," or "Well," at the start of
your responses. Keep it minimal -- no more than once every few exchanges.
```

### Occasional Fillers (Level 5-6)
```
Speak naturally with occasional filler words. You can say "um" or "well"
when transitioning between thoughts. Use these sparingly -- about once every
other response. They should sound natural, not forced.
```

### Regular Fillers (Level 7-8)
```
Speak like a natural conversationalist. Use filler words regularly:
- Start some responses with "So," or "Well,"
- Say "um" or "uh" when thinking before an answer
- Use "you know" or "I mean" to connect thoughts
- Occasionally say "let me see..." or "hmm, let me think about that"
- Rarely, correct yourself: "It's at 3 -- wait, actually 3:30"
These should feel completely natural, not scripted.
```

### Frequent Fillers (Level 9-10)
```
Speak exactly like a real person in casual conversation. Use natural fillers
frequently:
- "Um", "uh", "like" when thinking
- "You know", "I mean", "basically" as connectors
- "Let me see...", "Hmm okay so...", "Right, so..." when processing
- Self-correct occasionally: "It costs fifty -- sorry, forty-nine dollars"
- Think out loud: "Okay so let me pull that up... um... yeah, here it is"
Make it sound like you are genuinely thinking and speaking spontaneously.
Never sound scripted or rehearsed.
```


## Important Rules

### Never Overuse
Even at level 10, fillers should feel natural. If every sentence starts with "um",
it sounds broken, not human. Distribute fillers unevenly -- cluster them when
thinking, skip them when delivering clear information.

### Context Matters
- **Delivering important info:** Fewer fillers, clearer speech
- **Thinking/searching:** More fillers, longer pauses
- **Small talk:** Natural filler frequency
- **Confirming details:** Clear, minimal fillers

### Avoid These Patterns
- "Um" at the start of every response (sounds broken)
- "You know" more than once per response (sounds nervous)
- Self-corrections on critical info like names or numbers (confusing)
- Fillers during confirmations ("Your appointment is, um, at 3" -- bad)


## Combining with Pauses

Filler words work best when combined with pause dashes:

```
"Hmm -- let me check on that for you... -- Okay, so I see your appointment is scheduled for Thursday."
```

The dashes create natural-sounding pauses around the filler words.
