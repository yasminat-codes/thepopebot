# Audio Texture — SSML, Flush Syntax, Emotion, and Pacing

Fine-tune the sound of each individual response. This is the final layer — applied after the voice provider, speech config, and system prompt are already working well.

---

## SSML Overview

SSML (Speech Synthesis Markup Language) lets you inject pauses, change prosody, and control pronunciation inline in the LLM's output.

**Supported provider: ElevenLabs only** (with `enableSsmlParsing: true`).
Other providers ignore or break SSML tags.

### Enable SSML

```json
{
  "voice": {
    "provider": "11labs",
    "voiceId": "JBFqnCBsd6RMkjVDRZzb",
    "model": "eleven_turbo_v2_5",
    "enableSsmlParsing": true
  }
}
```

**Critical requirement:** `voiceId` must be explicitly set when `enableSsmlParsing: true`. The PATCH request fails without it.

**Known bug (streaming fragmentation):** SSML break tags can be spoken aloud as literal text (`<break time="1s"/>`) when streamed through certain pipeline configurations. Fix:

```json
{
  "model": {
    "inputPreprocessingEnabled": false
  }
}
```

---

## SSML Tag Reference

### Break — Pause

Insert silence between words or sentences.

```xml
Let me check on that.<break time="1.5s"/>
Okay, I found it.
```

| Format | Example | Notes |
|--------|---------|-------|
| Seconds | `time="1.5s"` | Use for longer pauses (thinking, transitions) |
| Milliseconds | `time="500ms"` | Use for shorter pauses (between phrases) |
| Strength | `strength="medium"` | `none`, `x-weak`, `weak`, `medium`, `strong`, `x-strong` |

**Common pause lengths:**

| Situation | Duration |
|-----------|---------|
| Breath between sentences | `200ms` |
| Thinking pause | `500ms–1s` |
| After asking a question (rhetorical) | `1s` |
| Looking something up | `1.5s–2s` |
| Dramatic emphasis | `2s` |

**Don't add break tags everywhere.** Use them where a human would actually pause — before delivering a key piece of information, after asking a question, or when transitioning to a new topic.

### Prosody — Rate, Pitch, Volume

```xml
<prosody rate="slow">Let me read that back to you...</prosody>

<prosody rate="fast">The confirmation number is</prosody>
<prosody rate="slow">seven, eight, four, alpha, bravo, two</prosody>

<prosody volume="loud">Your appointment is confirmed.</prosody>
```

| Attribute | Values | Notes |
|-----------|--------|-------|
| `rate` | `x-slow`, `slow`, `medium`, `fast`, `x-fast` | Or percentage: `"50%"`, `"150%"` |
| `pitch` | `x-low`, `low`, `medium`, `high`, `x-high` | Or relative: `"+2st"` (semitones) |
| `volume` | `silent`, `x-soft`, `soft`, `medium`, `loud`, `x-loud` | Or dB: `"+3dB"` |

**Use cases:**
- Slow down when reading back important information (order numbers, addresses, appointment times)
- Slow down for clarity with elderly callers
- Speed up for quick acknowledgment phrases
- Use pitch change to signal a question

### Phoneme — Inline Pronunciation Control

```xml
I'll transfer you to <phoneme alphabet="ipa" ph="nwɪn">Nguyen</phoneme> in billing.
```

This overrides pronunciation for a single word inline — useful when you can't use the pronunciation dictionary for a specific response.

Supported alphabets:
- `"ipa"` — International Phonetic Alphabet
- `"x-sampa"` — X-SAMPA phonetic notation

### Say-As — Number Formatting

```xml
Your appointment is on <say-as interpret-as="date" format="mdy">01/15/2026</say-as>.
Call us at <say-as interpret-as="telephone">555-867-5309</say-as>.
Your order number is <say-as interpret-as="characters">AB1234</say-as>.
```

| interpret-as | Effect |
|-------------|--------|
| `"date"` | Reads as spoken date |
| `"telephone"` | Groups phone number naturally |
| `"characters"` | Spells out each character |
| `"cardinal"` | Reads as number: "one hundred twenty three" |
| `"ordinal"` | Reads as ordinal: "one hundred twenty third" |
| `"fraction"` | Reads as fraction: "one half" |
| `"unit"` | Reads as unit + measurement |

**Important:** For most voice agents, it's better to handle this in the system prompt than via SSML. SSML requires the LLM to generate XML correctly — which it sometimes doesn't. Use system prompt rules for reliability; SSML for precision when it matters.

---

## Flush Syntax

Vapi-specific feature. Causes the text accumulated so far to be immediately sent to TTS without waiting for more content. Creates natural audio pacing by starting speech earlier.

```
I'll check that for you now. <flush />
[tool call happens here]
Your appointment is confirmed for Thursday.
```

### How It Works

Normally, the LLM generates its full response before TTS begins. `<flush />` forces immediate audio delivery of everything written up to that point, while the rest continues generating in parallel.

**Result:** The caller hears "I'll check that for you now" immediately, without waiting for the tool call to complete.

### When to Use Flush

| Situation | Flush placement |
|-----------|----------------|
| Before a tool call | Right before the tool call trigger |
| After a long opening phrase | Midway through a long response |
| Before reading back detailed info | After "Let me read that back..." |
| During lookup/search operations | After the transition phrase |

### Example: Tool Call with Flush

System prompt instruction:
```
When you're about to look something up or call a tool, always say a brief filler phrase
BEFORE the tool call, followed by <flush />.
Example: "Let me pull that up for you. <flush />"
Then make the tool call.
Then give the answer.
```

This eliminates the "robot silence" during tool calls — the most common complaint about AI phone agents.

---

## ElevenLabs Emotion Controls

ElevenLabs doesn't have Cartesia's `experimentalControls` emotion system, but you can influence emotional tone via:

**1. `stability` setting** — controls voice expressiveness:
- 0.35–0.40: Very expressive, natural variation. Can sound slightly unstable.
- 0.40–0.50: Expressive but controlled. Best for conversational agents.
- 0.50–0.65: Neutral, professional. Use for medical/legal.
- 0.65+: Monotone. Avoid.

**2. Model selection** — `eleven_turbo_v2_5` is more expressive than `eleven_flash_v2_5`.

**3. Prompt wording** — the content of what's being said affects natural emotional inflection. A question sounds different from a statement in well-trained voices.

---

## Cartesia Emotion Controls

For Cartesia voices, emotion is controlled in the assistant's voice configuration:

```json
{
  "voice": {
    "provider": "cartesia",
    "voiceId": "your-voice-id",
    "model": "sonic-turbo",
    "experimentalControls": {
      "speed": "normal",
      "emotion": [
        "positivity:high",
        "curiosity:medium"
      ]
    }
  }
}
```

**Multiple emotions:** Stack them in the array. They blend together.

**Speed options:** `"slow"`, `"normal"`, `"fast"`

**Emotion + intensity combinations:**

| Emotion | Intensities | Best for |
|---------|-------------|---------|
| `positivity` | `low`, `medium`, `high`, `highest` | Warmth, encouragement, sales |
| `negativity` | `low`, `medium`, `high`, `highest` | Expressing concern — use sparingly |
| `curiosity` | `low`, `medium`, `high`, `highest` | Discovery calls, qualification |
| `surprise` | `low`, `medium`, `high`, `highest` | Use sparingly |
| `sadness` | `low`, `medium`, `high` | Expressing genuine regret — very rare |

**Recommended starting points:**
- Sales outbound: `["positivity:high", "curiosity:low"]`
- Support inbound: `["positivity:medium"]`
- Complaint handling: `["positivity:low", "negativity:low"]` — calm and neutral

---

## Background Sound

Set ambient background sound to signal context (office environment, reduces caller suspicion of automation):

```json
{
  "backgroundSound": "office",
  "backgroundDenoisingEnabled": true
}
```

| Value | Effect |
|-------|--------|
| `"off"` | Silence — sounds clean, possibly too clean |
| `"office"` | Light ambient office noise |

**Recommendation:** Leave at `"off"` for most use cases. Office background sound is subtle but can reduce caller suspicion when the agent sounds slightly synthetic. Enable background denoising separately — it removes caller-side noise without adding synthetic noise.

---

## Practical SSML Template Library

### The "Reading Back Important Information" Pattern

```
Your appointment is confirmed. <break time="300ms"/>
Let me read that back to you. <break time="500ms"/>
<prosody rate="slow">Thursday, January fifteenth</prosody>,
<break time="200ms"/>
at <prosody rate="slow">three thirty in the afternoon</prosody>.
<break time="500ms"/>
Does that work for you?
```

### The "Lookup Pause" Pattern

```
Let me pull that up for you. <flush />
[agent makes tool call]
Got it. <break time="200ms"/>
Your order number <prosody rate="slow">four, seven, two, alpha</prosody> is currently in transit.
```

### The "Empathy Then Solution" Pattern

```
That's frustrating — I'm sorry about that. <break time="400ms"/>
Here's what we'll do. <break time="300ms"/>
I'm going to [solution].
```

### The "Number Confirmation" Pattern

```
Let me confirm your phone number. <break time="300ms"/>
<prosody rate="slow">Five, five, five</prosody>. <break time="300ms"/>
<prosody rate="slow">Eight, six, seven</prosody>. <break time="300ms"/>
<prosody rate="slow">Five, three, oh, nine</prosody>. <break time="500ms"/>
Is that correct?
```

---

## System Prompt Instructions for SSML

When using SSML, the LLM needs to know it should generate SSML tags. Add this to the system prompt:

```
AUDIO CONTROL INSTRUCTIONS:
You can control the audio using these tags in your responses:
- <break time="Xs"/> — pause for X seconds (use 0.3s–1.5s)
- <prosody rate="slow">text</prosody> — slow down for important information
- <flush /> — send audio immediately (use before tool calls)

Use break tags:
- Before delivering a key piece of information
- After asking a question (wait 0.5s before continuing)
- When transitioning between topics

Use prosody rate="slow":
- When reading back numbers, dates, addresses
- When confirming booking details

Use <flush />:
- Always before making a tool call
```

---

## What Not to Do

| Mistake | Why | Fix |
|---------|-----|-----|
| SSML on non-ElevenLabs voice | Tags read aloud as literal text | Only enable for 11labs voices |
| Enabling SSML without `inputPreprocessingEnabled: false` | Streaming fragmentation bug | Set `inputPreprocessingEnabled: false` |
| Enabling SSML without explicit `voiceId` | PATCH request fails | Always set `voiceId` |
| Long `<break time="5s"/>` pauses | Caller thinks call dropped | Keep pauses under 2s |
| Nested prosody tags | Unpredictable behavior | One prosody tag per segment |
| SSML tags without telling the LLM about them | LLM won't generate them | Add SSML instructions to system prompt |
| `<flush />` after every sentence | Audio sounds choppy | Use only at natural pause points |

---

## References

- [Voice Provider Matrix](voice-provider-matrix.md) — ElevenLabs and Cartesia configuration
- [Pronunciation](pronunciation.md) — pronunciation dictionary and phoneme IPA reference
- [Speech Configuration](speech-config.md) — timing and endpointing
- [Human Voice Master Guide](human-voice.md)
- Vapi SSML docs: https://docs.vapi.ai/customization/voice/ssml
