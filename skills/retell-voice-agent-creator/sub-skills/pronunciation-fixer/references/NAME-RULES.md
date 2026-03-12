# Name Pronunciation Rules

## Core Principle

Names are the most personal and important thing to pronounce correctly. There are two
approaches: IPA dictionary entries (precise, provider-limited) and phonetic prompt
injection (universal, less precise).

## Approach 1: IPA Dictionary Entry (Preferred)

**When to use:** Voice provider is ElevenLabs with Turbo v2 model.

Generate a pronunciation dictionary entry:

```json
{"word": "Nguyen", "alphabet": "ipa", "phoneme": "wIn"}
```

### Common Difficult Names with IPA

| Name | IPA | Approximate Sound |
|------|-----|-------------------|
| Nguyen | wIn | "win" |
| Siobhan | SI.vO:n | "shuh-VAWN" |
| Niamh | ni:v | "neev" |
| Saoirse | sEr.S@ | "SUR-shuh" |
| Aoife | i:.f@ | "EE-fuh" |
| Xiaoming | SaU.mIN | "SHOW-ming" |
| Priyanka | pri:.jAN.k@ | "pree-YAHN-kuh" |
| Rahul | rA:.hUl | "RAH-hool" |
| Dmitri | dmI.tri: | "duh-MEE-tree" |
| Bjorn | bjO:rn | "bee-YORN" |
| Joaquin | wA:.ki:n | "wah-KEEN" |
| Tsuyoshi | tsu.jo.Si | "tsoo-YO-shee" |

### Generating IPA for Unknown Names

When the user provides a phonetic hint like "sounds like win":

1. Break the hint into syllables
2. Map each syllable to IPA symbols
3. Combine into a single IPA string
4. Verify against known IPA patterns

Common phonetic-to-IPA mappings:
- "ee" -> i:
- "ah" -> A:
- "uh" -> @
- "oh" -> oU
- "oo" -> u:
- "ay" -> eI
- "sh" -> S
- "ch" -> tS
- "th" (thin) -> T
- "th" (this) -> D
- "ng" -> N


## Approach 2: Phonetic Prompt Injection (Universal)

**When to use:** Any voice provider, or when IPA is not available.

Add pronunciation guidance directly to the agent prompt:

```
IMPORTANT NAME PRONUNCIATION:
- The name "Nguyen" is pronounced "win". Always say it as "win".
- The name "Siobhan" is pronounced "shuh-VAWN". Stress the second syllable.
```

### Prompt Template

```
IMPORTANT - NAME PRONUNCIATION RULES:
{for each name}
- "{name}" is pronounced "{phonetic}". Always say it as "{phonetic}".
{end for}
Getting names right is crucial. If you are unsure of a name's pronunciation,
ask the caller: "I want to make sure I'm saying your name correctly. Is it {phonetic}?"
```


## Asking the User for Pronunciation

When the desired pronunciation is not provided and the name is ambiguous:

**Response template:**
"I need to know how to pronounce '{name}'. Could you tell me:
1. What it sounds like (e.g., 'rhymes with green' or 'sounds like win')
2. Or break it into syllables (e.g., 'SHUH-vawn')
This will help me set up the correct pronunciation for the agent."


## Business and Brand Names

Brand names follow the same rules but with extra care:

| Brand | Common Mistake | Correct |
|-------|---------------|---------|
| Smarterflo | "smarter-flow" | "smarter-flo" |
| Accenture | "accent-ure" | "AK-sen-chur" |
| Huawei | "ha-way" | "WAH-way" |
| Porsche | "porsh" | "POR-shuh" |
| Hyundai | "HUN-day" | "HUN-day" or "HYUN-day" |
| Adidas | "ah-DEE-das" | "AH-dee-das" |

### Strategy for Brand Names

1. Check if the user specifies the pronunciation
2. If not, use the most common regional pronunciation
3. Add both IPA entry AND prompt instruction for critical brand names
4. For the agent's own company name, ALWAYS ask the user how to pronounce it


## Multiple Names in One Agent

When an agent needs to handle multiple names (e.g., a team directory):

1. Prioritize names that appear most frequently
2. Add IPA entries for the top 10 most important names
3. Use prompt injection for additional names
4. Add a general instruction: "If you encounter a name you are unsure how to pronounce, ask the caller for the correct pronunciation"


## Edge Cases

- **Titles:** "Dr.", "Mrs.", "Prof." -- these are usually handled correctly by TTS
- **Suffixes:** "Jr.", "Sr.", "III" -- add prompt: "Jr is junior, III is the third"
- **Hyphenated names:** "Smith-Jones" -- usually handled correctly, test to verify
- **Names with apostrophes:** "O'Brien" -- usually handled correctly
- **Names with diacritics:** "Rene" vs "Renee" -- add IPA to distinguish
