# IPA and CMU Pronunciation Dictionary Guide for Retell AI

## Overview

Retell AI supports pronunciation dictionaries through the `pronunciation_dictionary`
parameter in the agent configuration. This allows you to specify exact pronunciations
for words that the TTS engine mispronounces.

**Critical limitation:** Pronunciation dictionaries only work with ElevenLabs Turbo v2
(`eleven_turbo_v2`) voice model and English language only.


## Dictionary Entry Format

Each entry is a JSON object with three fields:

```json
{
  "word": "string",
  "alphabet": "ipa" | "cmu",
  "phoneme": "string"
}
```

The `pronunciation_dictionary` parameter accepts an array of these objects:

```json
{
  "pronunciation_dictionary": [
    {"word": "Nguyen", "alphabet": "ipa", "phoneme": "wIn"},
    {"word": "HIPAA", "alphabet": "ipa", "phoneme": "hIp@"},
    {"word": "SaaS", "alphabet": "cmu", "phoneme": "S AE S"}
  ]
}
```


## IPA (International Phonetic Alphabet)

### Vowels

| IPA Symbol | Sound | Example Word | In IPA |
|------------|-------|-------------|--------|
| i: | "ee" | fl**ee**ce | fli:s |
| I | "ih" | k**i**t | kIt |
| e | "ay" | f**a**ce | feIs |
| E | "eh" | dr**e**ss | drEs |
| ae | "a" | tr**a**p | traep |
| A: | "ah" | p**al**m | pA:m |
| O: | "aw" | th**ough**t | TO:t |
| o | "oh" | g**oa**t | goUt |
| U | "uh" | f**oo**t | fUt |
| u: | "oo" | g**oo**se | gu:s |
| V | "uh" (short) | str**u**t | strVt |
| @ | "schwa" | **a**bout | @baUt |
| 3: | "ur" | n**ur**se | n3:s |

### Diphthongs

| IPA Symbol | Sound | Example Word | In IPA |
|------------|-------|-------------|--------|
| eI | "ay" | f**a**ce | feIs |
| aI | "eye" | pr**i**ce | praIs |
| OI | "oy" | ch**oi**ce | tSOIs |
| aU | "ow" | m**ou**th | maUT |
| oU | "oh" | g**oa**t | goUt |
| I@ | "ear" | n**ear** | nI@ |
| E@ | "air" | squ**are** | skwE@ |
| U@ | "oor" | c**ure** | kjU@ |

### Consonants

| IPA Symbol | Sound | Example Word |
|------------|-------|-------------|
| p | p | **p**at |
| b | b | **b**at |
| t | t | **t**ap |
| d | d | **d**og |
| k | k | **c**at |
| g | g | **g**ot |
| f | f | **f**at |
| v | v | **v**at |
| T | th (thin) | **th**ink |
| D | dh (this) | **th**is |
| s | s | **s**it |
| z | z | **z**oo |
| S | sh | **sh**ip |
| Z | zh | mea**s**ure |
| h | h | **h**at |
| m | m | **m**an |
| n | n | **n**ot |
| N | ng | si**ng** |
| l | l | **l**eg |
| r | r | **r**ed |
| w | w | **w**et |
| j | y | **y**es |
| tS | ch | **ch**urch |
| dZ | j | **j**udge |


## CMU (Carnegie Mellon University) Phoneme Set

CMU phonemes are uppercase and separated by spaces.

### CMU Vowels

| CMU | IPA Equivalent | Example |
|-----|---------------|---------|
| AA | A: | b**o**t |
| AE | ae | b**a**t |
| AH | V / @ | b**u**t |
| AO | O: | b**ough**t |
| AW | aU | b**ou**t |
| AY | aI | b**i**te |
| EH | E | b**e**t |
| ER | 3: | b**ir**d |
| EY | eI | b**a**ke |
| IH | I | b**i**t |
| IY | i: | b**ea**t |
| OW | oU | b**oa**t |
| OY | OI | b**oy** |
| UH | U | b**oo**k |
| UW | u: | b**oo**t |

### CMU Consonants

| CMU | IPA Equivalent | Example |
|-----|---------------|---------|
| B | b | **b**uy |
| CH | tS | **ch**air |
| D | d | **d**ie |
| DH | D | **th**at |
| F | f | **f**ight |
| G | g | **g**uy |
| HH | h | **h**igh |
| JH | dZ | **j**oy |
| K | k | **k**ite |
| L | l | **l**ie |
| M | m | **m**y |
| N | n | **n**igh |
| NG | N | si**ng** |
| P | p | **p**ie |
| R | r | **r**ye |
| S | s | **s**igh |
| SH | S | **sh**y |
| T | t | **t**ie |
| TH | T | **th**igh |
| V | v | **v**ie |
| W | w | **w**ise |
| Y | j | **y**acht |
| Z | z | **z**oo |
| ZH | Z | plea**s**ure |


## IPA vs CMU: When to Use Which

| Criteria | IPA | CMU |
|----------|-----|-----|
| Precision | Higher | Lower |
| Ease of use | Harder | Easier |
| Documentation | More extensive | Simpler |
| Recommended for | Non-English sounds, precise control | English words, quick fixes |

**General recommendation:** Use IPA for names, foreign words, and anything requiring
precise control. Use CMU for quick fixes of common English words.


## Generating Pronunciations

### From Phonetic Hints

When the user says "sounds like win":
1. Break into sounds: "w" + "ih" + "n"
2. Map to IPA: w + I + n
3. Result: `"phoneme": "wIn"`

### From Syllable Breakdown

When the user says "shuh-VAWN":
1. "shuh" -> S + @ (sh + schwa)
2. "VAWN" -> v + O: + n (v + aw + n)
3. Result: `"phoneme": "S@.vO:n"` (dot separates syllables)

### Using the Script

The [generate-pronunciation.py](../scripts/generate-pronunciation.py) script automates
this process for common patterns.


## Verification Steps

After generating a pronunciation entry:

1. **Read it back** -- Can you mentally sound out the IPA/CMU and hear the right word?
2. **Check symbol validity** -- Are all symbols from the tables above?
3. **Test syllable count** -- Does the phoneme have the right number of syllable nuclei (vowels)?
4. **Check stress** -- For multi-syllable words, is the primary stress on the right syllable?
5. **Test in Retell** -- Make a test call to verify the pronunciation sounds correct


## Limitations

- **Provider:** Only ElevenLabs supports pronunciation dictionaries
- **Model:** Only Turbo v2 (`eleven_turbo_v2`) model works
- **Language:** English only
- **Word matching:** The `word` field must match exactly as it appears in the prompt
- **Case sensitivity:** IPA symbols are case-sensitive (S is "sh", s is "s")
- **Entry limit:** Check your Retell plan for maximum dictionary entries
- **No phrases:** Each entry is a single word; for phrases, add entries for each word


## Common Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| Using lowercase `s` for "sh" | `s` = "s" sound | Use uppercase `S` for "sh" |
| Missing colon for long vowels | `i` vs `i:` are different | Add `:` for long vowels |
| Using CMU format in IPA field | "W IH N" in IPA field | Set `alphabet: "cmu"` or convert to IPA |
| Word not matching prompt | Dictionary has "nguyen" but prompt has "Nguyen" | Match case exactly |
| Trying with non-ElevenLabs | Dictionary silently ignored | Switch provider or use prompt injection |
