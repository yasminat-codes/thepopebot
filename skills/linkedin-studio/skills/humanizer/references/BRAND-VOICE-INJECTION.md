# BRAND-VOICE-INJECTION.md — Per-Persona Brand Voice Fingerprinting

Rules for loading and applying brand voice from ls_brand_voice_profile during humanization.

---

## Step 1: Load Brand Voice from Neon

```bash
source database/neon-utils.sh

BRAND_VOICE=$(neon_query "
  SELECT
    persona,
    writing_tone,
    vocabulary_preferences,
    avoid_words,
    signature_phrases,
    typical_sentence_length,
    content_pillars,
    contraction_style
  FROM ls_brand_voice_profile
  WHERE is_active = true
  LIMIT 1;
")

# Parse JSON fields
PERSONA=$(echo "$BRAND_VOICE" | jq -r '.persona')
WRITING_TONE=$(echo "$BRAND_VOICE" | jq -r '.writing_tone')
VOCAB_PREFS=$(echo "$BRAND_VOICE" | jq -r '.vocabulary_preferences[]')
AVOID_WORDS=$(echo "$BRAND_VOICE" | jq -r '.avoid_words[]')
SIG_PHRASES=$(echo "$BRAND_VOICE" | jq -r '.signature_phrases[]')
TARGET_SENT_LEN=$(echo "$BRAND_VOICE" | jq -r '.typical_sentence_length')
CONTRACTION_STYLE=$(echo "$BRAND_VOICE" | jq -r '.contraction_style')
```

If no active profile is found, fall back to the Default Persona below.

---

## Step 2: Persona → Tone Adjustments

Map the loaded `persona` to a tone adjustment profile. These adjustments layer on top of the `writing_tone` field.

| Persona | Tone adjustments |
|---|---|
| senior AI implementation consultant | Use Authoritative + Opinionated markers. Data-backed claims. Avoid humor. |
| founder | Conversational + Vulnerable markers. Can use dry humor sparingly. |
| executive | Authoritative. No vulnerability markers. Declarative and concise. |
| consultant | Authoritative + Opinionated. High specificity. No generic advice. |
| mentor | Conversational + Vulnerable. Inviting tone. Soft CTAs preferred. |
| coach | Conversational. Direct but warm. Challenge CTAs work well. |
| practitioner | Authoritative. Examples from direct experience. Data preferred. |
| entrepreneur | Conversational + Dry humor. Before/After hooks work well. |
| (default) | See Default Persona below |

### Tone → Personality Marker Category (reference PERSONALITY-LIBRARY.md)

| writing_tone | Primary category | Secondary category |
|---|---|---|
| direct | Authoritative | Opinionated |
| conversational | Conversational | Dry Humor |
| authoritative | Authoritative | — |
| vulnerable | Vulnerable | Conversational |
| pragmatic | Authoritative | Opinionated |
| mentor-style | Conversational | Vulnerable |
| energetic | Conversational | Dry Humor |
| analytical | Authoritative | — |

---

## Step 3: Vocabulary Preferences → Word Substitution Rules

`vocabulary_preferences` is a JSONB array of preferred words or phrases. During humanization:

1. Parse the array into a list of preferred terms
2. For each preferred term, scan the post for near-synonyms or generic equivalents
3. Where substitution improves specificity or tone-match, apply it
4. Do not force every preferred term into the post — natural insertion only

**Example:**
- vocabulary_preferences includes: ["concrete", "specific", "direct", "outcome-focused"]
- Post contains "impactful results" → replace with "concrete outcomes"
- Post contains "important considerations" → replace with "specific things to get right"

**Rule:** Never substitute a preferred term for a better, more specific word already in the post. Preferences are minimums, not constraints.

---

## Step 4: Avoid Words → Removal and Replacement

`avoid_words` is a JSONB array of words and phrases that must not appear.

### Process:
1. Parse avoid_words into a list
2. Scan post for any instance (exact match or near-match)
3. Replace with the most contextually appropriate alternative
4. If no good replacement exists, rewrite the sentence to avoid the word entirely

**Common avoid_words patterns and replacements:**

| Pattern | Replacement approach |
|---|---|
| Filler words (very, quite, just) | Delete |
| Competitor names | Delete or use "[competitor]" |
| Overused jargon | Use brand's preferred vocabulary instead |
| Self-deprecating phrases | Rewrite as confidence neutral |
| Exclamation marks | Remove — replace with stronger statement |
| Emojis | Remove unless explicitly allowed |

**Rule:** If avoid_words conflicts with AI-PHRASES-BLOCKLIST.md, the more restrictive rule applies. Both must be satisfied.

---

## Step 5: Signature Phrases → Natural Insertion

`signature_phrases` is a JSONB array of phrases the brand uses consistently to build recognition.

### Insertion rules:
- Max 2 signature phrases per post
- Never force — only insert where it flows naturally
- Never start or end the post with a signature phrase — embed in body
- Never insert consecutive signature phrases
- Common natural insertion points: transition between points, supporting a claim, adding texture to a lesson

**Example:**
- signature_phrases: ["the gap between strategy and execution", "what it actually takes", "concrete over clever"]
- Post is about AI implementation failure → insert "the gap between strategy and execution" as a natural reference mid-post

---

## Step 6: Sentence Length Calibration

Compare the post's average sentence length to `typical_sentence_length` from the profile.

### Process:
1. Measure average sentence length (words per sentence) across the post
2. Compare to target: `typical_sentence_length`
3. If post avg is more than 20% above target → shorten sentences
4. If post avg is more than 20% below target → extend or merge some short sentences

**Example:**
- `typical_sentence_length` = 10
- Post avg = 14 words/sentence (40% above target)
- Action: apply Pattern 3 (long compound → split) from SENTENCE-PATTERNS.md until avg is within 20%

**Adjustment table:**

| Post avg vs target | Action |
|---|---|
| Within 20% | No change needed |
| 20–35% too long | Split 2–3 long sentences |
| 35%+ too long | Major restructuring required |
| 20–35% too short | Merge 2–3 short sentences or extend with detail |
| 35%+ too short | Add supporting details or examples |

---

## Step 7: Contraction Application

Apply based on `contraction_style` field.

| contraction_style | Rule |
|---|---|
| always | Replace all "do not" → "don't", "I have" → "I've", "it is" → "it's", "they are" → "they're", "you are" → "you're", "cannot" → "can't", "will not" → "won't" |
| sometimes | Apply contractions in conversational sentences, keep formal in data-heavy or declarative sentences |
| never | Do not apply any contractions — verify H6 (contraction absence) is manually overridden in scoring |

**Standard contraction replacement pairs (for "always" mode):**

| Expand → Contract |
|---|
| do not → don't |
| cannot → can't |
| will not → won't |
| have not → haven't |
| is not → isn't |
| are not → aren't |
| it is → it's |
| I have → I've |
| I am → I'm |
| I will → I'll |
| you are → you're |
| they are → they're |
| we are → we're |
| there is → there's |
| that is → that's |
| what is → what's |

---

## Default Persona

Used when no active brand voice profile exists in ls_brand_voice_profile.

```
persona: nurse turned AI builder who ships real systems
writing_tone: direct, warm-but-not-soft, conversational
vocabulary_preferences: ["ship", "build", "works", "money", "fix", "real", "simple", "test"]
avoid_words: ["leverage", "synergy", "ecosystem", "impactful", "holistic", "authentic", "journey", "powerful", "incredible", "mindset", "thrive", "passionate about", "innovative", "solutions"]
signature_phrases: ["Nobody taught me this. I figured it out at 2 AM.", "I built this, so I know where it breaks.", "I don't sell advice. I build systems."]
typical_sentence_length: 12
contraction_style: always
content_pillars: ["AI consulting for small business", "automation implementation", "solo founder building"]
```

**Default tone rules:**
- Authoritative + Conversational markers (from strategy/BRAND-VOICE.md)
- Preserve Yasmine-specific voice markers: nursing metaphors, building metaphors, immigrant hustle language
- Specific numbers and receipts over vague claims
- Direct CTAs or medium engagement CTAs — no soft "let me know your thoughts"
- First person, past tense for stories — present tense for lessons
- Zero emojis. Always.
- See strategy/BRAND-VOICE.md for the full canonical voice reference
