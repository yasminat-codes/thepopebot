# Pronunciation Control

Fix how the TTS engine pronounces specific words. Critical for brand names, acronyms, technical terms, addresses, and unusual words.

---

## Two Approaches

| Approach | Provider | What it does |
|----------|---------|--------------|
| **ElevenLabs Pronunciation Dictionary** | ElevenLabs only | Persistent dictionary at the API level. Best method. |
| **Prompt-Level Phonetic Hints** | Any provider | Write phonetic spelling in the system prompt. Fallback approach. |
| **Deepgram Keyword Boosting** | Deepgram transcriber | Not TTS pronunciation — improves transcription recognition of unusual words. |

---

## Method 1: ElevenLabs Pronunciation Dictionary API

The most powerful and accurate approach. Create a dictionary once; it applies to all requests using that voice.

### Create a Dictionary

```bash
# 1. Create a pronunciation dictionary
curl -X POST https://api.elevenlabs.io/v1/pronunciation-dictionaries \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-company-pronunciations",
    "description": "Brand names and technical terms"
  }'
```

Response contains a `pronunciation_dictionary_id`. Store this.

### Add Alias Rules (Respelling)

Use when a word sounds different from how it's spelled:

```bash
curl -X POST "https://api.elevenlabs.io/v1/pronunciation-dictionaries/{dictionary_id}/add-rules" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [
      {
        "type": "alias",
        "string_to_replace": "Smarterflo",
        "alias": "Smarter Flow"
      },
      {
        "type": "alias",
        "string_to_replace": "ElevenLabs",
        "alias": "Eleven Labs"
      },
      {
        "type": "alias",
        "string_to_replace": "Vapi",
        "alias": "VAY-pee"
      }
    ]
  }'
```

### Add Phoneme Rules (IPA)

Use for precise phonetic control when alias doesn't give accurate enough results:

```bash
curl -X POST "https://api.elevenlabs.io/v1/pronunciation-dictionaries/{dictionary_id}/add-rules" \
  -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "rules": [
      {
        "type": "phoneme",
        "string_to_replace": "Nguyen",
        "phoneme": "nwɪn",
        "alphabet": "ipa"
      },
      {
        "type": "phoneme",
        "string_to_replace": "GIF",
        "phoneme": "dʒɪf",
        "alphabet": "ipa"
      }
    ]
  }'
```

### Attach Dictionary to Vapi Assistant

```json
{
  "voice": {
    "provider": "11labs",
    "voiceId": "JBFqnCBsd6RMkjVDRZzb",
    "model": "eleven_turbo_v2_5",
    "pronunciationDictionaryLocators": [
      {
        "pronunciation_dictionary_id": "your-dictionary-id",
        "version_id": "your-version-id"
      }
    ]
  }
}
```

Multiple dictionaries can be attached. They apply in order — first match wins.

---

## IPA Pronunciation Reference

IPA (International Phonetic Alphabet) gives you precise phonetic control. Common sounds:

### Vowels

| IPA | Example word | Sound |
|-----|-------------|-------|
| `æ` | cat, app | "a" as in trap |
| `eɪ` | day, say | "ay" as in face |
| `iː` | see, key | "ee" as in fleece |
| `ɪ` | sit, kit | Short "i" |
| `oʊ` | go, show | "oh" as in goal |
| `uː` | too, blue | "oo" as in goose |
| `ʌ` | cup, luck | Short "u" as in strut |
| `ɑː` | car, part | "ah" as in father |
| `ɔː` | four, more | "aw" as in thought |
| `ɜː` | her, bird | "er" as in nurse |
| `aɪ` | my, kite | "eye" as in price |
| `aʊ` | now, out | "ow" as in mouth |
| `ɔɪ` | boy, coin | "oy" as in choice |

### Consonants (tricky ones)

| IPA | Example | Notes |
|-----|---------|-------|
| `θ` | think, both | Soft "th" |
| `ð` | the, this | Hard "th" |
| `ʃ` | she, nation | "sh" sound |
| `ʒ` | vision, measure | "zh" sound |
| `tʃ` | chip, witch | "ch" sound |
| `dʒ` | job, bridge | "j" sound |
| `ŋ` | sing, ring | "ng" sound |
| `j` | yes, yellow | "y" sound |
| `w` | we, away | "w" sound |

### Stress Markers

| Symbol | Meaning |
|--------|---------|
| `ˈ` | Primary stress — place before stressed syllable |
| `ˌ` | Secondary stress |

Examples:
- "photograph" → `ˈfoʊtəˌɡræf`
- "photography" → `fəˈtɒɡrəfi`

---

## Common Brand Names and Technical Terms

Pre-built IPA for frequently mispronounced names:

| Word | IPA | Alias (simpler option) |
|------|-----|----------------------|
| Vapi | `ˈveɪpi` | "VAY-pee" |
| ElevenLabs | `ɪˈlɛvənlæbz` | "Eleven Labs" |
| Deepgram | `ˈdiːpɡræm` | "Deep Gram" |
| Cartesia | `kɑːrˈtiːziə` | "Car-TEE-zia" |
| HIPAA | `ˈhaɪpə` | "HI-pah" |
| SQL | `ˈsiːkwəl` | "SEE-quell" |
| API | `eɪpiˈaɪ` | "A-P-I" (spell out) |
| OAuth | `oʊˈɔːθ` | "OH-auth" |
| AWS | `eɪdʌbljuːˈɛs` | "A-W-S" (spell out) |
| PostgreSQL | `ˈpoʊstɡrɛsˌkjuːˈɛl` | "Post-gres Q-L" |
| Nguyen | `nwɪn` | "Win" |
| Zheng | `dʒʌŋ` | "Jung" |

---

## Method 2: Prompt-Level Phonetic Hints

When you can't use ElevenLabs pronunciation dictionaries (wrong provider, quick fix needed):

### Technique 1: Phonetic Parenthetical

Tell the LLM the pronunciation in the system prompt:

```
When saying "Smarterflo", pronounce it as "Smarter Flow" (two words).
When saying "Vapi", say "VAY-pee".
When saying "ElevenLabs", say "Eleven Labs" with a brief pause between words.
```

### Technique 2: Respelling in Output Instructions

Instruct the LLM to write the phonetic version when it says the word:

```
PRONUNCIATION RULES FOR SPOKEN RESPONSES:
- Never write "API" — write "A, P, I" instead (it will be read aloud as three letters)
- Never write "SQL" — write "sequel"
- Never write "$500" — write "five hundred dollars"
- Never write "3pm" — write "three PM"
- Never write "Jan 15" — write "January fifteenth"
```

### Technique 3: System Prompt Substitution Map

```
When you say the following words, use the pronunciation shown in brackets:
- "ElevenLabs" → say "Eleven Labs"
- "Smarterflo" → say "Smarter Flow"
- "AI" → say "A I" (not "ay")
- "URL" → say "U R L"
```

---

## Numbers, Dates, and Addresses

The most consistently mispronounced content category. Always handle in the system prompt.

```
NUMBERS AND FORMATTING RULES:
- Money: "five hundred dollars" not "$500" or "500 dollars"
- Phone numbers: "five, five, five — one, two, three, four" (with pauses between groups)
- Addresses: "123 Main Street" → "one twenty-three Main Street"
- Dates: "1/15/2026" → "January fifteenth, twenty twenty-six"
- Times: "3:30 PM" → "three thirty in the afternoon" or "three thirty PM"
- Percentages: "15%" → "fifteen percent"
- Zip codes: "90210" → "nine oh two one oh" (digit by digit)
- Card numbers: never read aloud — always mask and confirm last four only
- Large numbers: "1,500" → "fifteen hundred" (not "one thousand five hundred")
- Ordinals: "1st, 2nd, 3rd" → "first, second, third"
```

---

## Deepgram Keyword Boosting (Transcription Only)

This controls the speech-to-text transcription, not TTS pronunciation. Helps the transcriber correctly recognize unusual words the caller says.

```json
{
  "transcriber": {
    "provider": "deepgram",
    "model": "nova-3",
    "keywords": [
      "Smarterflo:5",
      "ElevenLabs:4",
      "Deepgram:4",
      "appointment:3",
      "cancellation:3"
    ]
  }
}
```

Format: `"word:intensifier"` (intensifier 1–10)

**Use this for:**
- Brand names callers say
- Domain-specific terms
- Names and locations unique to your context

**Do NOT use keyword boosting for:**
- Words you want TTS to pronounce differently (wrong system — this is transcription only)
- Common English words (causes hallucination)
- Words with intensifier > 5 (over-eager recognition)

---

## Building a Production Pronunciation Dictionary

### Step 1: Audit Your Content

List all words that could be mispronounced:
- Your company name and product names
- Competitor names mentioned in calls
- Technical jargon (acronyms, API names)
- Staff names if used in handoffs
- Location names if relevant
- Any domain-specific terminology

### Step 2: Test Without Dictionary First

Run a test call. Listen for mispronunciations. Build the dictionary for confirmed failures — don't add words speculatively.

### Step 3: Choose Alias vs. Phoneme

- **Alias** (simpler, preferred): Works for ~80% of cases. Just respell the word phonetically.
- **IPA phoneme**: Use when alias isn't precise enough, or for foreign-language names.

### Step 4: Version Control Your Dictionary

ElevenLabs dictionaries are versioned. When you add rules, a new version is created. Pin the `version_id` in your Vapi config to avoid unexpected changes from a production dictionary update.

---

## References

- [Voice Provider Matrix](voice-provider-matrix.md) — ElevenLabs configuration fields
- [Audio Texture](audio-texture.md) — SSML phoneme tags as inline alternative
- [Human Voice Master Guide](human-voice.md)
- ElevenLabs pronunciation dictionary docs: https://elevenlabs.io/docs/developer-guides/pronunciation-dictionaries
