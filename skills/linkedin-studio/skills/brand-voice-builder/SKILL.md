---
name: ls:brand-voice-builder
description: >
  PROACTIVELY builds or updates your brand voice profile through an interactive interview.
  Stores results in Neon ls_brand_voice_profile. Triggers on requests like 'set up my brand voice',
  'update my writing style', 'configure my persona', 'change my tone', or 'build brand profile'.
model: sonnet
context: fork
allowed-tools: Bash Read Write AskUserQuestion
metadata:
  version: "2.0.0"
---

# ls:brand-voice-builder

Interactive brand voice profile builder. Walks through a structured interview to define your writing persona, then stores it in Neon ls_brand_voice_profile.

## Phase 1: Check Existing Profile
1. Source `database/neon-utils.sh`
2. Query: `neon_query "SELECT profile_name, persona, writing_tone, niche FROM ls_brand_voice_profile WHERE is_active = true LIMIT 1" table`
3. If profile exists: show current profile, ask "Update existing profile or create new?"
4. If no profile: proceed to interview

## Phase 2: Interactive Interview (7 questions)

Ask one at a time using AskUserQuestion:

**Q1: Persona archetype**
"How would you describe your professional persona?"
Options: Pragmatic Expert, Thought Leader, Educator/Teacher, Storyteller

**Q2: Writing tone**
"What tone should your LinkedIn posts have?"
Options: Authoritative & direct, Conversational & warm, Data-driven & analytical, Inspirational & motivational

**Q3: Target audience**
Open-ended: "Who is your ideal reader on LinkedIn? (e.g., CTOs at mid-market companies, startup founders, etc.)"

**Q4: Content pillars**
"Which content pillars should your posts cover?" (multiSelect)
Options: Thought Leadership, Education/How-to, Social Proof/Case Studies, CTA/Lead Generation

**Q5: Vocabulary preferences**
Open-ended: "List any signature words or phrases you want to use regularly (comma-separated)"

**Q6: Words to avoid**
Open-ended: "Any words or phrases you never want in your posts? (defaults: leverage, utilize, synergy, delve, game-changer)"

**Q7: Hook preference**
"Which hook style do you prefer?"
Options: Questions, Statistics/Numbers, Personal stories, Bold claims

## Phase 3: Build Profile
Assemble the profile from interview answers. Set defaults for anything not answered.

## Phase 4: Store in Neon
```sql
INSERT INTO ls_brand_voice_profile (
  profile_name, persona, writing_tone, niche, target_audience,
  signature_phrases, avoid_words, preferred_hook_types,
  avg_post_length, vocabulary_preferences, typical_sentence_length,
  contraction_style, content_pillars, is_active
) VALUES (
  'default', $persona, $tone, $niche, $audience,
  $signature_phrases, $avoid_words, $hook_types,
  220, $vocab_prefs, 12,
  'high', $pillars_json, true
)
ON CONFLICT (profile_name) WHERE profile_name = 'default'
DO UPDATE SET persona = EXCLUDED.persona, ... , updated_at = NOW();
```

If using neon_exec, build the SQL string with proper escaping.

## Phase 5: Confirm
Show the saved profile in a formatted table. Suggest running `/ls:pipeline` to test it.

## Error Handling
| Error | Recovery |
|-------|---------|
| Neon unavailable | Save profile to local file BRAND-VOICE.md as fallback |
| User skips questions | Use defaults from BRAND-VOICE.md |
