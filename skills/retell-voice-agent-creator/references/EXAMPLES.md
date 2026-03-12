# Worked Examples

Three end-to-end examples showing how the orchestrator handles different
types of requests.

## Example 1: Simple Receptionist

**User says:** "Create a receptionist for Dr. Smith's dental office"

### Step-by-step execution

**1. Intent Detection**
- Keywords: "create" + "receptionist" -> Full CHAIN mode
- Template match: "receptionist" -> load receptionist template defaults

**2. Pre-Execution Setup**
- Template: receptionist
- Interview depth: minimal (user request is straightforward)
- Deployment mode: ask

**3. Interview (Minimal — 4 questions)**

Agent asks:
> "I'll set up a receptionist using our dental office template. A few quick
> questions:"

Q1: "Any specific pronunciation for the doctor's name or practice name?"
> User: "No, Dr. Smith is straightforward."

Q2: "What are your office hours?"
> User: "Monday to Friday, 9 AM to 5 PM."

Q3: "Should the agent be able to schedule appointments, or just take messages?"
> User: "Schedule appointments."

Q4: "Is this for your own Retell account?"
> User: "Yes, internal."

**4. Voice Selection**
- Template default: female, warm, American English
- Agent confirms: "I'll use a warm female voice — Sarah from ElevenLabs. Sound good?"
- User: "Perfect."
- Output: `voice_id: "11labs_sarah_warm"`

**5. Prompt Generation**
- Loads receptionist template prompt
- Customizes: "Dr. Smith's Dental Office", hours M-F 9-5, appointment scheduling
- States: greeting -> inquiry_type -> appointment_scheduling -> information -> message_taking -> closing
- Output: system_prompt with 6 states

**6. Pronunciation Fixing**
- No custom terms needed. Skip.

**7. Humanization**
- Template default: level 6
- Adds: warm pause after greeting, "of course" and "absolutely" fillers,
  backchannel "mhm" during caller speech, natural pause before appointment times
- Output: humanized_prompt

**8. Latency Optimization**
- Template defaults: responsiveness 1, interruption_sensitivity 0.8
- No changes needed. Output: default latency_config

**9. Config Assembly**
- Generates llm-config.json (prompt, 6 states, gpt-4o-mini)
- Generates agent-config.json (voice, latency, post-call analysis)

**10. Deployment**
- Shows config to user for review
- User: "Looks good, deploy it."
- Creates LLM -> Creates agent -> Verifies
- Output: agent_id: "agent_dental_abc123"

**Final output to user:**
> "Your receptionist is live. Here's the summary:
> - Agent: Dr. Smith's Dental Office Receptionist
> - Voice: Sarah (ElevenLabs, female, warm)
> - Agent ID: agent_dental_abc123
> - States: greeting, inquiry, scheduling, information, messages, closing
> - Would you like me to trigger a test call?"

**Total time:** ~5 minutes
**Resources used:** receptionist template, voice-selector, prompt-generator,
humanization-engine, agent-config-builder, retell-api-wrapper

---

## Example 2: Complex Multilingual Sales Agent

**User says:** "Build a multilingual sales agent for our SaaS product Xeroflux.
It needs to handle objections, qualify leads, and transfer to a human for
enterprise deals over $50k. Should sound confident but not pushy. We need
English and Spanish."

### Step-by-step execution

**1. Intent Detection**
- Keywords: "build" + "sales agent" -> Full CHAIN mode
- Template match: "sales"
- Complexity signals: "multilingual", "objections", "qualify", "transfer"
  -> Full enterprise interview

**2. Pre-Execution Setup**
- Template: sales
- Interview depth: full enterprise (complex use case)
- Custom pronunciation needed: "Xeroflux"

**3. Interview (Full — 18 questions across rounds)**

Key answers captured:
- Business: Xeroflux (SaaS, B2B)
- Languages: English + Spanish
- Agent name: "Alex"
- Persona: Confident, consultative, not pushy
- Voice: Male, American English, ElevenLabs (for emotion range)
- Qualification criteria: Budget >$10k, decision maker, 90-day timeline
- Transfer condition: Enterprise deals >$50k -> human sales
- Objection scripts: Price ("let me break down the ROI"), timing ("I understand,
  when would be better?"), competitor ("here's what makes us different")
- Pronunciation: "Xeroflux" -> ZEER-oh-flux
- Humanization: Level 7
- Webhook: https://crm.xeroflux.com/webhook/retell
- Deployment: Internal

**4. Voice Selection**
- Criteria: Male, confident, American English, ElevenLabs
- Sub-skill browses voices, presents 3 options
- User picks "Marcus" — confident, warm, 30s male
- Output: `voice_id: "11labs_marcus_confident"`

**5. Prompt Generation**
- Complex 8-state prompt:
  - greeting: "Hey [Name], this is Alex from Xeroflux..."
  - rapport_building: Find common ground, ask about their current setup
  - discovery: "What challenges are you facing with [current solution]?"
  - qualification: Budget, timeline, decision maker checks
  - pitch: Tailored to discovered pain points
  - objection_handling: 3 scripted objection responses
  - enterprise_transfer: "Let me connect you with our enterprise team..."
  - closing: Next steps, follow-up scheduling
- Post-call analysis: lead_qualified, budget_range, timeline, objections_raised,
  deal_stage, transfer_requested
- Output: 8-state system_prompt, Spanish language variant

**6. Pronunciation Fixing**
- "Xeroflux" -> IPA: /ˈzɪəroʊflʌks/
- Inline prompt hint: "Xeroflux (pronounced ZEER-oh-flux)"
- Dictionary entry added
- Output: pronunciation_dictionary with 1 entry, annotated prompt

**7. Humanization**
- Level 7 applied to both English and Spanish prompts
- Confident fillers: "absolutely", "great question", "that's a really good point"
- Strategic pauses: before price reveals, after prospect shares a challenge
- Active listening: "I hear you", "that makes sense"
- No "um/uh" (not appropriate for confident sales persona)
- Output: humanized_prompt (English + Spanish)

**8. Latency Optimization**
- Responsiveness: 0 (fast — sales needs quick rapport)
- Interruption sensitivity: 0.9 (let prospect interrupt freely)
- Backchannel: enabled
- Model: gpt-4o (needs reasoning for qualification logic)
- Output: latency_config

**9. Config Assembly**
- llm-config.json: 8 states, gpt-4o, bilingual prompt, function calls for CRM
- agent-config.json: voice, latency, webhook URL, post-call analysis, pronunciation
- Output: both JSON files saved to output/

**10. Deployment**
- Shows full config to user (2 JSON files)
- User reviews: "Change the qualification budget threshold to $15k"
- Prompt-generator re-runs for that section only
- Config re-assembled
- User: "Deploy it."
- Creates LLM -> Creates agent -> Verifies
- Triggers test call with mock objection scenario
- Output: agent_id: "agent_xeroflux_sales_def456"

**Final output to user:**
> "Your sales agent is live. Summary:
> - Agent: Alex (Xeroflux Sales)
> - Voice: Marcus (ElevenLabs, male, confident)
> - Languages: English, Spanish
> - States: 8 (greeting through closing)
> - Qualification: Budget >$15k, decision maker, 90-day timeline
> - Transfer: Enterprise deals >$50k -> human
> - Pronunciation: Xeroflux (/ˈzɪəroʊflʌks/)
> - Webhook: https://crm.xeroflux.com/webhook/retell
> - Agent ID: agent_xeroflux_sales_def456
> - Test call completed. Transcript saved to output/test-call-transcript.txt"

**Total time:** ~30 minutes
**Resources used:** All 7 sub-skills, sales template, full interview, pronunciation library

---

## Example 3: Standalone Pronunciation Fix

**User says:** "Fix the pronunciation on agent_abc123 — it can't say our product
name 'Xeroflux' and our CEO's name 'Thierry Leclerc'"

### Step-by-step execution

**1. Intent Detection**
- Keywords: "fix pronunciation" -> SINGLE mode, pronunciation-fixer
- Extract: agent_id = "agent_abc123", words = ["Xeroflux", "Thierry Leclerc"]

**2. Read Sub-Skill**
- Read `sub-skills/pronunciation-fixer/SKILL.md` in full

**3. Validate Inputs**
- agent_id: provided (agent_abc123)
- Words to fix: provided (Xeroflux, Thierry Leclerc)
- All inputs present. Proceed.

**4. Execute Pronunciation Fixer**

For "Xeroflux":
- IPA: /ˈzɪəroʊflʌks/
- Phonetic respelling: ZEER-oh-flux
- Dictionary entry: `{"word": "Xeroflux", "pronunciation": "/ˈzɪəroʊflʌks/", "alphabet": "ipa"}`

For "Thierry Leclerc":
- IPA: /tiˈɛri ləˈklɛr/
- Phonetic respelling: tee-AIR-ee luh-KLAIR
- Dictionary entry: `{"word": "Thierry Leclerc", "pronunciation": "/tiˈɛri ləˈklɛr/", "alphabet": "ipa"}`

Also generates inline prompt hints:
- "Xeroflux (say: ZEER-oh-flux)"
- "Thierry Leclerc (say: tee-AIR-ee luh-KLAIR)"

**5. Present to User**
> "Here are the pronunciation fixes:
> - Xeroflux -> ZEER-oh-flux (/ˈzɪəroʊflʌks/)
> - Thierry Leclerc -> tee-AIR-ee luh-KLAIR (/tiˈɛri ləˈklɛr/)
>
> I can apply these to agent_abc123 in two ways:
> 1. Add to pronunciation dictionary (works with ElevenLabs Turbo v2+)
> 2. Add inline hints to the system prompt (works with any voice provider)
>
> Which approach, or both?"

User: "Both."

**6. Apply to Agent**
- Fetch current agent config: GET /get-agent/agent_abc123
- Verify voice provider supports dictionaries (ElevenLabs Turbo v2 — yes)
- PATCH agent: add pronunciation_dictionary entries
- Fetch current LLM: get llm_id from agent config
- PATCH LLM: add inline hints to system prompt
- Verify updates applied

**7. Offer Test**
> "Pronunciation fixes applied. Want me to trigger a test call to verify?"
- User: "Yes."
- Triggers test call via retell-api-wrapper
- Retrieves transcript, confirms both names are pronounced correctly

**Total time:** ~2 minutes
**Resources used:** pronunciation-fixer, retell-api-wrapper (for patching and test call)
