---
name: pronunciation-fixer
description: Fixes voice agent pronunciation for emails, phone numbers, URLs, names, acronyms, and numbers. Auto-generates IPA/CMU dictionary entries. Includes industry-specific pronunciation libraries. Use when agent mispronounces words, reads emails as gibberish, says phone numbers as large numbers, or butchers brand names.
allowed-tools: Read Write Bash(python3:*)
---

# Pronunciation Fixer

## Overview

Voice agents frequently mispronounce structured data because TTS engines treat text literally.
An email like `john.smith@gmail.com` becomes unintelligible noise. A phone number like
`4158923245` is read as "four billion one hundred fifty-eight million..." instead of
digit-by-digit. Brand names, acronyms, and foreign names get butchered.

This sub-skill fixes pronunciation across six domains:

| Domain | Problem | Solution |
|--------|---------|----------|
| Emails | Read as gibberish | Spell out with "at" and "dot" markers |
| Phone numbers | Read as large integers | Digit-by-digit with grouped pauses |
| URLs | Mashed together | Segment into spoken parts |
| Names | Mispronounced | IPA dictionary entry or phonetic prompt |
| Acronyms | Pronounced as words | Letter-by-letter with dashes |
| Numbers/Currency | Wrong format | normalize_for_speech or prompt rules |

Each domain has a dedicated reference file with detailed transformation rules, examples,
and prompt templates. The sub-skill also includes a Python script that auto-generates
IPA/CMU pronunciation dictionary entries for Retell's `pronunciation_dictionary` parameter.

### When to Use This Sub-Skill

- Agent mispronounces a specific word, name, or phrase
- Agent reads emails, phone numbers, or URLs incorrectly
- Agent says numbers as large integers instead of digit sequences
- Agent butchers brand names or industry-specific terms
- User asks to "fix pronunciation" or "make it say X correctly"
- Building an agent in an industry with specialized terminology


## Quick Start

Fix a pronunciation in three steps:

1. **Identify the type** -- Determine if the problem is an email, phone, URL, name, acronym, or number
2. **Apply the rules** -- Follow the domain-specific transformation from the reference file
3. **Generate the fix** -- Output either a `pronunciation_dictionary` entry (IPA/CMU) or a `prompt_instructions` string


## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| word_or_phrase | string | yes | The word, phrase, or structured data to fix |
| pronunciation_type | enum | yes | One of: email, phone, url, name, acronym, number, currency, auto |
| desired_pronunciation | string | no | How the user wants it pronounced (phonetic hint) |
| industry | string | no | Industry context for specialized terms (medical, legal, tech, finance, real-estate) |
| voice_provider | string | no | Current voice provider (affects whether IPA dictionary is available) |
| voice_model | string | no | Current voice model (IPA only works with ElevenLabs Turbo v2) |
| language | string | no | Language code, default "en" |

### Auto-Detection Logic

When `pronunciation_type` is set to `auto`, detect the type:

- Contains `@` -- email
- Starts with `+`, `(`, or is all digits with length 7-15 -- phone
- Contains `://`, `www.`, or ends with `.com`, `.org`, `.net`, etc. -- url
- All caps and 2-5 characters -- acronym
- Contains `$`, currency symbols, or `%` -- currency
- Pure digits or digit patterns with decimals -- number
- Everything else -- name


## Outputs

| Parameter | Type | Description |
|-----------|------|-------------|
| pronunciation_dictionary | array | Array of `{word, alphabet, phoneme}` objects for Retell config |
| prompt_instructions | string | Text to inject into the agent prompt for pronunciation guidance |
| fix_method | enum | Which method was used: `ipa_dictionary`, `cmu_dictionary`, `prompt_injection`, `normalize_for_speech` |
| notes | string | Explanation of what was fixed and why this method was chosen |
| normalize_for_speech | boolean | Whether to enable the normalize_for_speech parameter |


## Phase 1: Identify Pronunciation Type

Use this decision tree to classify the input:

```
START
  |
  v
Contains "@"? ----YES----> EMAIL
  |NO
  v
Matches phone pattern? ----YES----> PHONE
(digits, +, (, ), -, length 7-15)
  |NO
  v
Contains "://", "www.", or ----YES----> URL
known TLD (.com, .org, etc)?
  |NO
  v
All uppercase, 2-5 chars? ----YES----> ACRONYM
  |NO
  v
Contains $, EUR, GBP, %, ----YES----> CURRENCY/NUMBER
or is purely numeric?
  |NO
  v
DEFAULT -----> NAME
```

### Edge Cases

- `API@company.com` -- This is an EMAIL (the @ takes precedence)
- `1-800-FLOWERS` -- This is a PHONE (vanity number, convert letters to digits)
- `NASA` -- This is an ACRONYM (even though it is commonly said as a word)
- `Dr. Smith` -- This is a NAME (the "Dr." is a title, not an acronym)


## Phase 2: Apply Transformation Rules

Each domain has a dedicated reference file with complete rules. Here is the summary:

### Email Transformation
- Spell each character individually with pauses between groups
- `@` becomes "at", `.` becomes "dot", `_` becomes "underscore", `-` becomes "dash"
- Group by natural segments: username segments, domain, TLD
- Full rules: [EMAIL-RULES.md](references/EMAIL-RULES.md)

### Phone Transformation
- Read digit by digit, never as a large number
- Group digits naturally: area code, then groups of 3-4
- Use dashes/pauses between groups
- Handle country codes, extensions
- Full rules: [PHONE-RULES.md](references/PHONE-RULES.md)

### URL Transformation
- Identify pronounceable segments vs letter sequences
- `.` becomes "dot", `/` becomes "slash", `-` becomes "dash"
- Spell out unpronounceable character sequences
- Full rules: [URL-RULES.md](references/URL-RULES.md)

### Acronym Transformation
- Default: spell letter by letter with dashes (A-P-I)
- Known exceptions: SQL can be "sequel", SCUBA is always "scuba"
- Industry-specific acronyms may have known pronunciations
- Full rules: [ACRONYM-RULES.md](references/ACRONYM-RULES.md)

### Name Transformation
- Two approaches: IPA dictionary (precise) or phonetic prompt (universal)
- IPA is preferred when voice provider supports it
- Phonetic prompt works with all providers
- Full rules: [NAME-RULES.md](references/NAME-RULES.md)

### Number/Currency Transformation
- First try `normalize_for_speech: true` for basic cases
- For specific formatting, add prompt instructions
- Dates, percentages, large numbers, currencies each have patterns
- Full rules: [NUMBER-CURRENCY-RULES.md](references/NUMBER-CURRENCY-RULES.md)


## Phase 3: Generate IPA/CMU Entry

Decide which fix method to use based on the voice provider and pronunciation type:

```
Is the voice provider ElevenLabs with Turbo v2 model?
  |
  YES --> Is the fix for a single word or short phrase?
  |         |
  |         YES --> Use IPA dictionary entry (most precise)
  |         |
  |         NO --> Use prompt injection (dictionary has word limits)
  |
  NO --> Is it a number/currency issue?
           |
           YES --> Try normalize_for_speech first, then prompt injection
           |
           NO --> Use prompt injection (works with all providers)
```

### IPA Dictionary Entry Format

```json
{
  "word": "Nguyen",
  "alphabet": "ipa",
  "phoneme": "wIN"
}
```

### CMU Dictionary Entry Format

```json
{
  "word": "Nguyen",
  "alphabet": "cmu",
  "phoneme": "W IH N"
}
```

### Prompt Injection Format

Add to the agent's prompt instructions:

```
PRONUNCIATION RULES:
- When saying the email "john.smith@gmail.com", say it as:
  "j-o-h-n dot s-m-i-t-h at g-m-a-i-l dot com"
- When saying phone number (415) 892-3245, say it as:
  "four one five -- eight nine two -- three two four five"
```

For full IPA/CMU reference, see [IPA-CMU-GUIDE.md](references/IPA-CMU-GUIDE.md).


## Phase 4: Validate and Test

After generating the pronunciation fix:

1. **Review the output** -- Does the IPA/CMU phoneme look correct?
2. **Check provider compatibility** -- IPA dictionary only works with ElevenLabs Turbo v2
3. **Test with a sample call** -- Use Retell's test call feature to verify
4. **Iterate if needed** -- Adjust phonemes or prompt wording

### Common Validation Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| IPA entry ignored | Wrong voice model | Switch to ElevenLabs Turbo v2 or use prompt injection |
| Sounds slightly off | IPA phoneme inaccurate | Adjust specific phoneme symbols |
| Works but sounds robotic | Too many spelled-out letters | Group pronounceable segments together |
| Inconsistent pronunciation | Only fixed in one place | Add to both dictionary AND prompt |


## Domain Reference Map

| Domain | Reference File | Script Support |
|--------|---------------|----------------|
| Emails | [EMAIL-RULES.md](references/EMAIL-RULES.md) | Prompt injection |
| Phone numbers | [PHONE-RULES.md](references/PHONE-RULES.md) | Prompt injection |
| URLs | [URL-RULES.md](references/URL-RULES.md) | Prompt injection |
| Acronyms | [ACRONYM-RULES.md](references/ACRONYM-RULES.md) | IPA/CMU or prompt |
| Names | [NAME-RULES.md](references/NAME-RULES.md) | IPA/CMU or prompt |
| Numbers/Currency | [NUMBER-CURRENCY-RULES.md](references/NUMBER-CURRENCY-RULES.md) | normalize_for_speech or prompt |
| IPA/CMU Guide | [IPA-CMU-GUIDE.md](references/IPA-CMU-GUIDE.md) | generate-pronunciation.py |


## Real-World Scenarios

### Scenario 1: Fix Company Email Pronunciation

**Problem:** The agent says "info at smarterflo dot com" but mispronounces "smarterflo" as
"smarter-flow" instead of "smarter-flo".

**Input:**
```json
{
  "word_or_phrase": "info@smarterflo.com",
  "pronunciation_type": "email",
  "desired_pronunciation": "smarter-flo"
}
```

**Process:**
1. Identify as EMAIL type (contains @)
2. Apply email rules: split into segments
3. "smarterflo" is a brand name -- needs special handling
4. Generate prompt injection with phonetic guide

**Output:**
```json
{
  "pronunciation_dictionary": [],
  "prompt_instructions": "When saying the email info@smarterflo.com, say it as: 'info at smarter-flo dot com'. The company name 'smarterflo' is pronounced 'smarter-flo', NOT 'smarter-flow'.",
  "fix_method": "prompt_injection",
  "notes": "Email pronunciation fixed via prompt injection. Brand name 'smarterflo' given explicit phonetic guidance.",
  "normalize_for_speech": false
}
```

### Scenario 2: Fix Unusual Name Pronunciation

**Problem:** The agent cannot pronounce the client name "Nguyen" correctly.

**Input:**
```json
{
  "word_or_phrase": "Nguyen",
  "pronunciation_type": "name",
  "desired_pronunciation": "win",
  "voice_provider": "ElevenLabs",
  "voice_model": "eleven_turbo_v2"
}
```

**Process:**
1. Identify as NAME type
2. Voice provider is ElevenLabs Turbo v2 -- IPA dictionary is available
3. Generate IPA entry for "Nguyen" -> "wIN" (approximation of Vietnamese pronunciation)
4. Also add prompt instruction as backup

**Output:**
```json
{
  "pronunciation_dictionary": [
    {"word": "Nguyen", "alphabet": "ipa", "phoneme": "wIN"}
  ],
  "prompt_instructions": "The name 'Nguyen' is pronounced 'win'. Always pronounce it as 'win'.",
  "fix_method": "ipa_dictionary",
  "notes": "IPA dictionary entry generated for ElevenLabs Turbo v2. Prompt instruction added as backup. The Vietnamese name Nguyen is commonly anglicized as 'win'.",
  "normalize_for_speech": false
}
```

### Scenario 3: Fix Industry Acronyms for Medical Office

**Problem:** Building a medical receptionist agent that needs to pronounce EKG, MRI, HIPAA,
and other medical acronyms correctly.

**Input:**
```json
{
  "word_or_phrase": "EKG, MRI, HIPAA, CBC, PT, OT",
  "pronunciation_type": "acronym",
  "industry": "medical"
}
```

**Process:**
1. Identify as ACRONYM type with medical industry context
2. Load medical pronunciation library
3. Some are letter-by-letter (EKG, MRI, CBC), some are words (HIPAA = "hip-uh")
4. PT and OT are context-dependent (Physical Therapy, Occupational Therapy)

**Output:**
```json
{
  "pronunciation_dictionary": [],
  "prompt_instructions": "MEDICAL ACRONYM PRONUNCIATION:\n- EKG: say 'E-K-G' (letter by letter)\n- MRI: say 'M-R-I' (letter by letter)\n- HIPAA: say 'hip-uh' (as a word, two syllables)\n- CBC: say 'C-B-C' (letter by letter)\n- PT: say 'P-T' (letter by letter) or 'physical therapy' (use full term when first mentioned)\n- OT: say 'O-T' (letter by letter) or 'occupational therapy' (use full term when first mentioned)",
  "fix_method": "prompt_injection",
  "notes": "Medical acronyms handled via prompt injection for universal provider compatibility. HIPAA is the only one pronounced as a word. PT and OT should use full terms on first mention for clarity.",
  "normalize_for_speech": false
}
```


## Industry Pronunciation Libraries

When an industry context is provided, load the relevant pronunciation patterns:

| Industry | Common Terms | Reference |
|----------|-------------|-----------|
| Medical | EKG, MRI, HIPAA, CBC, STAT, PRN, BID, TID, QID | Medical terms are mixed: some letter-by-letter, some as words |
| Legal | LLC, LLP, SCOTUS, ADA, EEOC, FMLA, tort, voir dire | Latin terms need phonetic guides |
| Tech | API, SDK, REST, OAuth, SAML, CI/CD, SaaS, PaaS | Most are letter-by-letter except SaaS ("sass"), PaaS ("pass") |
| Finance | ROI, ETF, IPO, EBITDA, GAAP, SEC, FDIC, APR, APY | EBITDA ("ee-bit-dah"), GAAP ("gap") are words |
| Real Estate | MLS, HOA, REIT, ARM, FHA, VA, PMI, escrow | HOA can be "H-O-A" or "hoe-uh", REIT is "reet" |

### Loading Industry Libraries

When the `industry` parameter is set:

1. Identify all industry-specific terms in the agent's prompt and knowledge base
2. Cross-reference with the industry pronunciation table above
3. Generate prompt instructions for all terms that need special pronunciation
4. Add IPA dictionary entries for the most critical terms (if provider supports it)


## Integration with Orchestrator

This sub-skill produces two outputs that feed into the agent-config-builder:

### Output 1: pronunciation_dictionary array

Goes directly into the agent configuration:

```json
{
  "pronunciation_dictionary": [
    {"word": "Nguyen", "alphabet": "ipa", "phoneme": "wIN"},
    {"word": "HIPAA", "alphabet": "ipa", "phoneme": "hIp@"}
  ]
}
```

**Limitation:** Only works with ElevenLabs Turbo v2. Maximum entries vary by plan.

### Output 2: prompt_instructions string

Appended to the agent prompt by the prompt-generator sub-skill:

```
## Pronunciation Rules
- Say email addresses by spelling each part: "j-o-h-n at g-m-a-i-l dot com"
- Say phone numbers digit by digit with pauses: "four one five -- eight nine two"
- The name "Nguyen" is pronounced "win"
- HIPAA is pronounced "hip-uh"
```

### Output 3: normalize_for_speech boolean

Set on the agent config directly:

```json
{
  "normalize_for_speech": true
}
```

### Data Flow

```
User request
    |
    v
pronunciation-fixer (this sub-skill)
    |
    +--> pronunciation_dictionary[] --> agent-config-builder --> Retell agent config
    |
    +--> prompt_instructions --> prompt-generator --> agent prompt
    |
    +--> normalize_for_speech --> agent-config-builder --> Retell agent config
```


## Script Reference

### generate-pronunciation.py

Located at [scripts/generate-pronunciation.py](scripts/generate-pronunciation.py).

Takes a JSON file with words and generates IPA pronunciation dictionary entries.

**Usage:**
```bash
python3 scripts/generate-pronunciation.py --input words.json --output pronunciations.json
```

**Input format:**
```json
{
  "words": [
    {"word": "Nguyen", "hint": "win"},
    {"word": "Siobhan", "hint": "shuh-vawn"},
    {"word": "GIF", "hint": "jif"}
  ]
}
```

**Output format:**
```json
{
  "pronunciation_dictionary": [
    {"word": "Nguyen", "alphabet": "ipa", "phoneme": "wIn"},
    {"word": "Siobhan", "alphabet": "ipa", "phoneme": "SIvO:n"},
    {"word": "GIF", "alphabet": "ipa", "phoneme": "dZIf"}
  ]
}
```


## Troubleshooting

### IPA Entry Not Working

1. Verify the voice provider is ElevenLabs
2. Verify the voice model is `eleven_turbo_v2` (not flash, not multilingual)
3. Check that the word in the dictionary matches exactly what appears in the prompt
4. IPA is case-sensitive -- uppercase and lowercase phonemes mean different sounds

### Prompt Injection Not Working

1. Make sure the pronunciation instruction is near the top of the prompt
2. Use explicit phrasing: "Always pronounce X as Y" not "X sounds like Y"
3. Add emphasis: "This is very important: pronounce X as Y"
4. If the agent still mispronounces, try spelling it phonetically in the prompt itself

### Phone Numbers Still Read as Integers

1. First enable `normalize_for_speech: true`
2. If that does not work, format the number with dashes in the prompt
3. Add explicit instruction: "Always read phone numbers digit by digit"
4. As a last resort, store the number pre-formatted: "four one five - eight nine two - three two four five"

### Email Pronunciation Sounds Robotic

1. Group pronounceable segments instead of spelling every letter
2. "gmail" should be said as "gmail" not "g-m-a-i-l"
3. Common domains (gmail, yahoo, outlook, hotmail) are said as words
4. Only spell out unusual or ambiguous parts


## Appendix: Supported IPA Symbols Quick Reference

| Symbol | Sound | Example |
|--------|-------|---------|
| i: | ee | fleece |
| I | ih | kit |
| e | ay | face |
| E | eh | dress |
| ae | a | trap |
| A: | ah | palm |
| O: | aw | thought |
| o | oh | goat |
| U | uh | foot |
| u: | oo | goose |
| @ | schwa | about |
| S | sh | ship |
| Z | zh | measure |
| T | th | think |
| D | dh | this |
| tS | ch | church |
| dZ | j | judge |
| N | ng | sing |

For the complete IPA and CMU reference, see [IPA-CMU-GUIDE.md](references/IPA-CMU-GUIDE.md).
