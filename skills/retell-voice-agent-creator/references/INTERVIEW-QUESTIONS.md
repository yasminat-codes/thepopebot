# Interview Questions

Full 25-question enterprise interview organized by round. The orchestrator
selects question depth based on request complexity:
- Minimal (3-5 questions): Rounds 1, 5, 9 highlights only
- Standard (8-12 questions): Rounds 1-4, 9
- Full enterprise (15-25 questions): All 10 rounds

## Round 1: Business Basics (3 questions)

### Q1: Business Name
- **Question:** "What's the name of the business this agent will represent?"
- **Why it matters:** Used in greeting, closing, and throughout the prompt. Critical for pronunciation fixing.
- **Default if skipped:** "your company"
- **Maps to config:** system_prompt (greeting, references), pronunciation_dictionary

### Q2: Industry
- **Question:** "What industry are you in? (e.g., healthcare, real estate, SaaS, legal, dental)"
- **Why it matters:** Determines template selection, compliance guardrails, and vocabulary.
- **Default if skipped:** "general business"
- **Maps to config:** template selection, system_prompt (compliance notes)

### Q3: Primary Use Case
- **Question:** "What's the main job of this agent? (e.g., answer calls, book appointments, qualify leads, handle support)"
- **Why it matters:** Determines conversation flow, states, and post-call analysis.
- **Default if skipped:** "receptionist" (most versatile template)
- **Maps to config:** template selection, states[], post_call_analysis_data[]

## Round 2: Agent Persona (3 questions)

### Q4: Agent Name
- **Question:** "What should the agent's name be? (e.g., 'Sarah', 'Alex', or your brand name)"
- **Why it matters:** Used in greeting and self-identification. Affects voice selection.
- **Default if skipped:** Template default name (e.g., "Sarah" for receptionist)
- **Maps to config:** system_prompt (self-identification)

### Q5: Personality and Tone
- **Question:** "How should the agent come across? (e.g., professional and warm, casual and friendly, authoritative and direct)"
- **Why it matters:** Shapes the entire prompt tone and humanization choices.
- **Default if skipped:** "professional and warm"
- **Maps to config:** system_prompt (tone directives), humanization style

### Q6: Language
- **Question:** "What language(s) should the agent speak? (e.g., English only, English and Spanish)"
- **Why it matters:** Affects voice provider selection (not all support all languages) and prompt structure.
- **Default if skipped:** "English"
- **Maps to config:** agent_config.language, voice_id selection

## Round 3: Voice Preferences (3 questions)

### Q7: Voice Gender
- **Question:** "Do you prefer a male or female voice? Or no preference?"
- **Why it matters:** Primary filter for voice selection.
- **Default if skipped:** Template default (varies by template)
- **Maps to config:** voice_id selection filter

### Q8: Voice Provider Preference
- **Question:** "Do you have a preferred voice provider? Options: ElevenLabs (most natural, emotion support), OpenAI (fast, reliable), Deepgram (low latency), Cartesia (efficient). Or should I pick the best fit?"
- **Why it matters:** Each provider has different strengths. See voice-provider-comparison.md.
- **Default if skipped:** ElevenLabs (best naturalness)
- **Maps to config:** voice_id, voice provider selection

### Q9: Voice Character
- **Question:** "Any specific voice qualities? (e.g., warm, energetic, calm, authoritative, young, mature)"
- **Why it matters:** Fine-tunes voice selection within the chosen provider.
- **Default if skipped:** "warm, professional"
- **Maps to config:** voice_id selection criteria

## Round 4: Conversation Flow (3 questions)

### Q10: Greeting
- **Question:** "How should the agent greet callers? Give me an example or describe the vibe."
- **Why it matters:** First impression. Sets the tone for the entire call.
- **Default if skipped:** Template default greeting
- **Maps to config:** system_prompt (greeting state)

### Q11: Key Actions
- **Question:** "What actions should the agent be able to take? (e.g., book appointments, transfer to human, take messages, answer FAQs, collect information)"
- **Why it matters:** Determines conversation states and transitions.
- **Default if skipped:** Template default actions
- **Maps to config:** states[], system_prompt (action states)

### Q12: Conversation States
- **Question:** "Does this agent need a multi-step flow? For example: greeting -> discovery questions -> qualification -> action -> closing? Or is it more free-form?"
- **Why it matters:** Stateful agents handle complex flows better. Simple use cases work fine with free-form.
- **Default if skipped:** Template default (receptionist = simple, sales = stateful)
- **Maps to config:** states[], state transitions

## Round 5: Pronunciation Needs (2 questions)

### Q13: Company/Product Names
- **Question:** "Are there any company names, product names, or brand terms that might be hard to pronounce? List them with how they should sound."
- **Why it matters:** Mispronounced brand names destroy credibility instantly.
- **Default if skipped:** No custom pronunciation
- **Maps to config:** pronunciation_dictionary[]

### Q14: Industry-Specific Terms
- **Question:** "Any industry jargon, medical terms, addresses, or proper nouns the agent will need to say correctly?"
- **Why it matters:** Industry terms (drug names, legal terms, addresses) often need pronunciation help.
- **Default if skipped:** No custom pronunciation
- **Maps to config:** pronunciation_dictionary[]

## Round 6: Humanization Level (2 questions)

### Q15: Humanization Scale
- **Question:** "On a scale of 1-10, how human should this agent sound? 1 = efficient and direct, 10 = indistinguishable from a human (with ums, pauses, thinking sounds)."
- **Why it matters:** Controls how many humanization elements are injected into the prompt.
- **Default if skipped:** 5 (moderate)
- **Maps to config:** humanization engine parameters

### Q16: Specific Humanization Elements
- **Question:** "Any specific human elements you want? Options: filler words (um, uh), thinking pauses, backchannel cues (mhm, right), breathing sounds, ambient awareness."
- **Why it matters:** Some clients want specific elements only (e.g., pauses but no fillers).
- **Default if skipped:** Template default elements
- **Maps to config:** humanization engine element selection

## Round 7: Technical Settings (2 questions)

### Q17: Responsiveness Priority
- **Question:** "What matters more: fast responses (may occasionally cut off the caller) or careful listening (slightly slower but never interrupts)?"
- **Why it matters:** Sets the responsiveness and interruption sensitivity values.
- **Default if skipped:** Balanced (responsiveness: 1, interruption_sensitivity: 0.5)
- **Maps to config:** responsiveness, interruption_sensitivity

### Q18: Environment
- **Question:** "Will callers typically be in a quiet environment (office, home) or noisy one (car, street, warehouse)?"
- **Why it matters:** Determines denoising and endpointing settings.
- **Default if skipped:** Quiet environment
- **Maps to config:** ambient_sound_volume, denoising mode

## Round 8: Integration (2 questions)

### Q19: Webhook URL
- **Question:** "Do you have a webhook URL for receiving call events? (post-call summary, transcripts, etc.)"
- **Why it matters:** Enables real-time and post-call data flow to the client's systems.
- **Default if skipped:** No webhook
- **Maps to config:** webhook_url in agent config

### Q20: CRM / External Systems
- **Question:** "Does this agent need to connect to any external systems? (CRM, calendar API, database, ticketing system)"
- **Why it matters:** May require custom function calling or tool use in the prompt.
- **Default if skipped:** No integrations
- **Maps to config:** system_prompt (function calling instructions), tools[]

## Round 9: Deployment (3 questions)

### Q21: Deployment Target
- **Question:** "Is this agent for your own Retell account, or are you building it for a client's account?"
- **Why it matters:** Determines which API key to use and security handling.
- **Default if skipped:** Internal (own account)
- **Maps to config:** deployment_mode, API key selection

### Q22: Phone Number
- **Question:** "Do you have a phone number to assign to this agent, or should we skip that for now?"
- **Why it matters:** Agents can work via API-triggered calls without a number, or via inbound calls with one.
- **Default if skipped:** No phone number (API-triggered calls only)
- **Maps to config:** phone_number assignment (via Twilio)

### Q23: Go-Live Timing
- **Question:** "Should we deploy this agent live right away, or just generate the config for review first?"
- **Why it matters:** Some users want to review before going live. Others want immediate deployment.
- **Default if skipped:** Generate config for review first
- **Maps to config:** deployment step execution

## Round 10: Testing and Analytics (2 questions)

### Q24: Test Scenarios
- **Question:** "What scenarios should we test after deployment? (e.g., happy path, edge cases, specific objections)"
- **Why it matters:** Shapes the test call script and validation criteria.
- **Default if skipped:** Basic greeting + primary action test
- **Maps to config:** test-agent.sh parameters

### Q25: Success Criteria
- **Question:** "How will you measure if this agent is successful? (e.g., appointment booking rate, call duration, customer satisfaction, lead qualification rate)"
- **Why it matters:** Determines post-call analysis variables and reporting setup.
- **Default if skipped:** Template default metrics
- **Maps to config:** post_call_analysis_data[]

## Round 11: Advanced Features & Compliance

**Q21: PII Redaction**
"Does this agent handle sensitive caller information — names, social security numbers, credit card details? If so, do you need PII redaction (these are automatically removed from transcripts)?"
- Yes → Enable pii_config, note $0.01/min additional cost
- No → Skip

**Q22: Dynamic Voice Speed**
"Should the agent automatically match the caller's speaking pace — slower for deliberate speakers, faster for fast-talkers?"
- Yes → enable_dynamic_voice_speed: true (recommended for most templates)
- No → Keep fixed voice_speed

**Q23: Conversation Flow Architecture**
"Does your conversation have a linear, scripted flow (like debt collection or a compliance intake) — or is it more open-ended where callers might jump between topics?"
- Linear/compliance → Traditional States
- Open-ended → Flex Mode (if under 20 nodes)
- Not sure → Default to Traditional States

**Q24: Fallback Voice Provider**
"If your primary voice provider has an outage, what should the fallback be? We'll automatically configure a backup from a different provider."
- Collect preference or auto-assign based on primary voice provider

**Q25: Vocabulary Specialization**
"Is this agent in a specialized field — specifically medical/clinical? If so, we can optimize vocabulary recognition."
- Medical → vocab_specialization: "medical"
- Other → Not applicable (English only)

**Q26: Fast Tier**
"Is this agent handling high-value calls (sales demos, enterprise prospects, VIP support) where call quality is more important than cost?"
- Yes → Recommend Fast Tier (1.5x cost, 50% latency variance reduction, 99.9% uptime SLA)
- No → Standard tier

**Q27: AI Disclosure Approach**
"Some states legally require disclosing that the caller is speaking with AI within the first 30 seconds. How would you like to handle this?"
- Required disclosure → Build into begin_message naturally: "Hi, I'm [Name], an AI assistant from [Company]..."
- No requirement → Keep persona, disclose only if directly asked

**Q28: Retell Assure (AI QA)**
"Would you like automated call quality monitoring — AI that reviews transcripts for hallucinations, off-topic responses, and compliance issues?"
- Yes → Enable Retell Assure, configure thresholds
- No → Manual review only

## Interview Flow Tips

- Ask questions conversationally, not as a rigid numbered list.
- Group related questions naturally: "Tell me about the business and what the agent should do" covers Q1-Q3.
- If the user gives detailed upfront info, skip questions already answered.
- Always acknowledge answers before moving to the next question.
- For minimal interviews, ask Q1 + Q13 + Q21 at minimum.
- End the interview with: "Great, I have everything I need. Let me build this for you."
