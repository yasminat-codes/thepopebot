---
name: retell-voice-agent-creator
description: Creates production-ready, human-sounding voice agents on Retell AI. Orchestrates pronunciation fixing, humanization, voice selection, prompt generation, latency optimization, API integration, and config assembly. Ships with 9 templates (sales, support, appointment, receptionist, personal assistant, lead qualifier, survey, debt collection, real estate). Use when user says "create voice agent", "build voice agent", "retell agent", "voice AI", "fix pronunciation", "humanize agent", "optimize voice agent", or mentions Retell AI.
allowed-tools: Read Write Bash(curl:*) Bash(python3:*) Bash(chmod:*)
metadata: {"clawdbot":{"requires":{"env":["RETELL_API_KEY"],"bins":["curl","jq","python3"]},"primaryEnv":"RETELL_API_KEY"}}
context: fork
agent: general-purpose
---

# Retell AI Voice Agent Creator — Orchestrator
<!-- ultrathink -->

## Overview

You are the orchestrator for building production-ready voice agents on Retell AI.
Your job is to route user intent to the correct sub-skill (or chain of sub-skills),
manage context flow between steps, and assemble the final deployable agent.

This skill handles:
- Full end-to-end agent creation (interview through deployment)
- Standalone fixes (pronunciation, humanization, latency, voice swap)
- Template-based rapid deployment (9 industry templates)
- Multi-account deployment (internal team use or client accounts)
- Existing agent optimization and updates

You coordinate 7 sub-skills. You never do the detailed work yourself — you delegate
to the sub-skill whose SKILL.md you read and follow. Think of yourself as a
dispatcher: you detect intent, select the route, read the sub-skill instructions,
and execute them faithfully.

Users range from non-technical business owners ("make me a receptionist") to
developers ("deploy agent with custom webhook and ElevenLabs voice"). Adapt your
interview depth accordingly. When in doubt, ask fewer questions and use smart
defaults from the matching template.

Base directory token: `{baseDir}` = the directory containing this SKILL.md.

---

## Iron Law

These rules override everything else. Never violate them.

1. **Always read the routing table first.** Before doing anything, match the user's
   intent against the routing table in Phase 1. Never guess which sub-skill to use.

2. **Never skip reading a sub-skill SKILL.md.** Before executing any sub-skill,
   read its SKILL.md in full. The sub-skill SKILL.md contains the exact procedure.
   Do not improvise or paraphrase — follow its instructions literally.

3. **Never fabricate API responses.** If a curl call fails, report the error.
   Do not invent agent IDs, voice IDs, or deployment URLs.

4. **Preserve context between chain steps.** Each step's output feeds the next.
   If Step 3 produces a prompt, Step 4 must receive that exact prompt text.

5. **Ask before deploying.** Never call the Retell API to create or modify a live
   agent without explicit user confirmation. Show the config first.

6. **Template defaults are suggestions, not mandates.** If the user specifies
   something that contradicts a template default, the user wins.

7. **Client API keys are ephemeral.** Never write a client's RETELL_API_KEY to
   disk. Hold it in working memory for the current session only.

---

## Sub-Skill Index

| # | Sub-Skill | Path | Standalone | Description |
|---|-----------|------|------------|-------------|
| 1 | Voice Selector | `sub-skills/voice-selector/SKILL.md` | Yes | Browse, filter, audition, and select voices from ElevenLabs, OpenAI, Deepgram, Cartesia, PlayHT |
| 2 | Prompt Generator | `sub-skills/prompt-generator/SKILL.md` | Yes | Generate the system prompt and conversation flow with states, transitions, guardrails |
| 3 | Pronunciation Fixer | `sub-skills/pronunciation-fixer/SKILL.md` | Yes | Build IPA/phonetic dictionaries for company names, products, medical terms, addresses |
| 4 | Humanization Engine | `sub-skills/humanization-engine/SKILL.md` | Yes | Add fillers, pauses, backchannel cues, breathing, ambient awareness to prompts |
| 5 | Latency Optimizer | `sub-skills/latency-optimizer/SKILL.md` | Yes | Tune responsiveness, interruption sensitivity, endpointing, denoising, model selection |
| 6 | Agent Config Builder | `sub-skills/agent-config-builder/SKILL.md` | Yes | Assemble agent-config.json and llm-config.json from all sub-skill outputs |
| 7 | Retell API Wrapper | `sub-skills/retell-api-wrapper/SKILL.md` | Yes | Create, update, list, delete agents and LLMs via Retell REST API; trigger test calls |

---

## Routing Table

Match user intent to the correct execution path.

| Intent Signal | Target Sub-Skill(s) | Mode | Notes |
|---------------|---------------------|------|-------|
| "create voice agent", "build agent", "new agent for [business]" | All 7 (full chain) | CHAIN | Run 8-step chain: Interview -> Voice -> Prompt -> Pronunciation -> Humanization -> Latency -> Config -> Deploy |
| "fix pronunciation", "can't say [word]", "pronunciation issues" | pronunciation-fixer | SINGLE | Standalone. May need existing agent ID to patch. |
| "make it sound more human", "humanize", "add pauses", "too robotic" | humanization-engine | SINGLE | Standalone. Operates on existing prompt text. |
| "change voice", "different voice", "voice selection", "browse voices" | voice-selector | SINGLE | Standalone. Returns voice_id for config update. |
| "update prompt", "rewrite prompt", "conversation flow", "add state" | prompt-generator | SINGLE | Standalone. May need existing prompt as starting point. |
| "too slow", "latency", "interruption issues", "background noise" | latency-optimizer | SINGLE | Standalone. Tunes numeric settings on existing agent. |
| "deploy agent", "list agents", "delete agent", "API call", "get call" | retell-api-wrapper | SINGLE | Standalone. Direct API operations. |
| "generate config", "build config", "show me the JSON" | agent-config-builder | SINGLE | Standalone. Assembles config from provided parameters. |
| "create and deploy immediately", "quick deploy [template]" | voice-selector + prompt-generator + agent-config-builder + retell-api-wrapper | CHAIN | Skip interview. Use template defaults. 4-step fast chain. |
| "optimize existing agent", "improve agent" | latency-optimizer + humanization-engine | PARALLEL | Run both simultaneously. Merge outputs into single config patch. |

---

## Phase 1: Intent Detection

When the user's message arrives, follow this procedure:

1. **Scan for keywords.** Check the user's message against the Intent Signal
   column in the routing table above. Also consult
   [references/USER-INTENT-MAP.md](references/USER-INTENT-MAP.md) for extended
   natural-language patterns.

2. **Classify the mode.**
   - If the intent maps to a single sub-skill row -> **SINGLE** mode.
   - If the intent maps to "create voice agent" or similar -> **CHAIN** mode.
   - If the intent maps to "optimize existing agent" -> **PARALLEL** mode.
   - If the intent maps to "quick deploy" -> **CHAIN** mode (shortened).

3. **Ambiguity resolution.** If the intent is unclear:
   - Ask one clarifying question: "Are you looking to create a new voice agent
     from scratch, or work on a specific part like pronunciation or voice selection?"
   - Never guess. One question is cheaper than re-doing work.

4. **Extract parameters.** Pull out any specifics from the message:
   - Business name, industry, use case
   - Existing agent_id (if updating)
   - Specific voice or provider preference
   - Template name (if mentioned)

5. **Proceed to the appropriate phase.** SINGLE -> Phase 4. CHAIN -> Phase 2.
   PARALLEL -> Phase 4 (with parallel dispatch).

---

## Phase 2: Pre-Execution Setup

This phase runs only for CHAIN mode (full agent creation).

### Step 2A: Template Detection

Check if the user's request matches one of the 9 templates. Consult
[references/TEMPLATE-CATALOG.md](references/TEMPLATE-CATALOG.md) for the full list.

| Template | Trigger Phrases |
|----------|----------------|
| receptionist | "receptionist", "front desk", "office phone" |
| sales | "sales agent", "cold call", "outbound sales" |
| support | "customer support", "help desk", "tech support" |
| appointment | "appointment setter", "booking", "scheduling" |
| personal-assistant | "personal assistant", "PA", "executive assistant" |
| lead-qualifier | "lead qualifier", "qualify leads", "inbound leads" |
| survey | "survey", "feedback", "customer satisfaction" |
| debt-collection | "debt collection", "collections", "payment reminder" |
| real-estate | "real estate", "property", "listing agent" |

If a template matches, pre-load its defaults. These become the fallback for any
interview question the user skips or answers with "default".

If no template matches, use the `receptionist` template as the base (it has the
most neutral defaults) and customize from the interview answers.

### Step 2B: Interview Depth Decision

Assess the user's technical level and request complexity:

- **Minimal interview** (3-5 questions): User said "quick", mentioned a template
  by name, or provided most details upfront. Ask only: business name, any
  pronunciation-sensitive terms, and deployment target (internal/client).

- **Standard interview** (8-12 questions): Default for most requests. Covers
  business basics, persona, voice preference, conversation flow highlights,
  and deployment.

- **Full enterprise interview** (15-25 questions): User said "enterprise",
  "complex", "multi-state", "multilingual", or the use case involves regulated
  industries (healthcare, finance, debt collection). Use the complete question
  set from [references/INTERVIEW-QUESTIONS.md](references/INTERVIEW-QUESTIONS.md).

### Step 2C: Deployment Mode

Ask: "Is this agent for your own Retell account, or are you building it for a
client?" This determines:

- **Internal mode**: Use `RETELL_API_KEY` from environment.
- **Client mode**: Prompt for the client's API key at deployment time (Phase 3,
  Step 8). See [references/MULTI-ACCOUNT-GUIDE.md](references/MULTI-ACCOUNT-GUIDE.md).

---

## Phase 3: Full Chain Flow

The complete 8-step chain for building a voice agent from scratch. Each step
reads the relevant sub-skill SKILL.md and follows its instructions exactly.

### Step 1: Interview

**Purpose:** Gather all requirements from the user.
**Input:** User's initial request + template defaults (if matched).
**Process:**
- Load interview questions from [references/INTERVIEW-QUESTIONS.md](references/INTERVIEW-QUESTIONS.md).
- Select question depth per Step 2B.
- Ask questions conversationally, not as a rigid form.
- Record answers in a structured context object.
**Output:** Interview context object containing: business_name, industry, use_case,
agent_name, agent_persona, voice_preferences, conversation_flow_notes,
pronunciation_terms[], humanization_level (1-10), technical_settings,
integration_requirements, deployment_mode.
**Passes to:** Steps 2-7 (all subsequent steps read from this context).

### Step 2: Voice Selection

**Purpose:** Select the optimal voice for this agent.
**Sub-skill:** Read and follow `sub-skills/voice-selector/SKILL.md`.
**Input:** voice_preferences from interview (gender, accent, warmth, provider preference).
**Process:** The voice-selector sub-skill handles browsing, filtering, and selection.
**Output:** voice_id, voice_provider, voice_name.
**Passes to:** Step 6 (Config Assembly).

### Step 3: Prompt Generation

**Purpose:** Generate the full system prompt with conversation states.
**Sub-skill:** Read and follow `sub-skills/prompt-generator/SKILL.md`.
**Input:** business_name, industry, use_case, agent_persona, conversation_flow_notes
from interview. Template prompt as starting point if template matched.
**Process:** The prompt-generator sub-skill builds the prompt with states, transitions,
guardrails, and post-call analysis variables.
**Output:** system_prompt (full text), states[] (if stateful), post_call_analysis_data[].
**Passes to:** Step 4 (Pronunciation), Step 5 (Humanization), Step 6 (Config).

### Step 4: Pronunciation Fixing

**Purpose:** Build pronunciation dictionaries for tricky terms.
**Sub-skill:** Read and follow `sub-skills/pronunciation-fixer/SKILL.md`.
**Input:** pronunciation_terms[] from interview, system_prompt from Step 3
(to scan for additional terms that may need fixing).
**Process:** The pronunciation-fixer sub-skill generates IPA entries and phonetic
respelling alternatives.
**Output:** pronunciation_dictionary[] (word -> IPA mapping), prompt_annotations
(inline pronunciation hints for the system prompt).
**Passes to:** Step 6 (Config Assembly — dictionary goes into agent config).

### Step 5: Humanization

**Purpose:** Make the agent sound natural, not robotic.
**Sub-skill:** Read and follow `sub-skills/humanization-engine/SKILL.md`.
**Input:** system_prompt from Step 3, humanization_level from interview.
**Process:** The humanization-engine sub-skill injects fillers, pauses, backchannel
cues, breathing patterns, and ambient awareness directives into the prompt.
**Output:** humanized_prompt (modified system_prompt with humanization directives).
**Passes to:** Step 6 (Config Assembly — replaces raw system_prompt).

### Step 6: Latency Optimization

**Purpose:** Tune performance settings for responsiveness and quality.
**Sub-skill:** Read and follow `sub-skills/latency-optimizer/SKILL.md`.
**Input:** technical_settings from interview, use_case (some use cases need
faster response, others need more accuracy).
**Process:** The latency-optimizer sub-skill selects optimal values for
responsiveness, interruption sensitivity, endpointing, model, and denoising.
**Output:** latency_config (responsiveness, interruption_sensitivity,
enable_backchannel, ambient_sound, end_call_after_silence_ms, etc.).
**Passes to:** Step 7 (Config Assembly).

### Step 7: Config Assembly

**Purpose:** Combine all outputs into deployable JSON configs.
**Sub-skill:** Read and follow `sub-skills/agent-config-builder/SKILL.md`.
**Input:** voice_id (Step 2), humanized_prompt (Step 5), pronunciation_dictionary
(Step 4), latency_config (Step 6), post_call_analysis_data (Step 3),
integration_requirements from interview.
**Process:** The agent-config-builder sub-skill assembles two JSON files:
`llm-config.json` (the Retell LLM definition with prompt and states) and
`agent-config.json` (the agent definition with voice, latency, webhook settings).
**Output:** `{baseDir}/output/llm-config.json`, `{baseDir}/output/agent-config.json`.
**Passes to:** Step 8 (Deployment).

### Step 7.5: Quality Gate

**Step 7.5 — Quality Gate** (agent-config-builder → latency-optimizer → review)
- Run Retell Simulation Testing: 5 synthetic personas × 10 calls = 50 simulated conversations
- Verify pronunciation: test all numbers, emails, URLs in the config
- Check latency: ensure begin_message_delay_ms set, prompts under 500 tokens
- Review deliberate imperfection rules are in prompt
- Score against pre-launch gate checklist (see [QUALITY-TESTING.md](references/QUALITY-TESTING.md))
- Gate: all thresholds met → proceed to Deploy | any failure → return to relevant sub-skill

### Step 8: Deployment

**Purpose:** Deploy the agent to Retell AI via API.
**Sub-skill:** Read and follow `sub-skills/retell-api-wrapper/SKILL.md`.
**Input:** llm-config.json, agent-config.json from Step 7. API key (from env
for internal, from user for client mode).
**Process:**
1. Show the user the final config for review.
2. Wait for explicit confirmation ("deploy it", "looks good", "yes").
3. Create the Retell LLM (POST /create-retell-llm).
4. Create the agent (POST /create-agent) with the LLM ID from step 3.
5. Verify the agent exists (GET /get-agent/{agent_id}).
6. Optionally trigger a test call if user wants.
**Output:** agent_id, agent_url, llm_id, deployment_status.

**Alternative:** Run `{baseDir}/scripts/deploy.sh` for scripted deployment.

---

## Phase 4: SINGLE Mode Dispatch

When the routing table points to a single sub-skill:

1. **Read the sub-skill SKILL.md.** Load `{baseDir}/sub-skills/{name}/SKILL.md`
   and read it completely before proceeding.

2. **Validate inputs.** Check that you have the required inputs for the sub-skill.
   If the user did not provide them, ask. Common missing inputs:
   - pronunciation-fixer: needs the list of words to fix
   - humanization-engine: needs existing prompt text or agent_id
   - latency-optimizer: needs existing agent_id or current settings
   - voice-selector: needs gender/accent/provider preference (or "surprise me")
   - retell-api-wrapper: needs the specific API action and parameters

3. **Execute.** Follow the sub-skill SKILL.md instructions exactly.

4. **Return output.** Present the sub-skill's output to the user. If the output
   is a config change, ask if they want to apply it to a live agent.

For **PARALLEL** mode: Load both sub-skill SKILL.md files. Validate inputs for
both. Execute both (you can interleave their steps since they operate on
different config sections). Merge their outputs into a single config patch
before presenting to the user.

---

## Phase 5: Output Assembly

After any chain or single execution, organize outputs.

### Output Folder Structure

All generated files are saved to `{baseDir}/output/`:

```
output/
  llm-config.json          # Retell LLM definition (prompt, states, model)
  agent-config.json         # Agent definition (voice, latency, webhook)
  pronunciation-dict.json   # IPA pronunciation dictionary
  prompt.txt                # Raw system prompt (before humanization)
  humanized-prompt.txt      # Final humanized prompt
  interview-notes.json      # Captured interview answers
  deployment-receipt.json   # agent_id, llm_id, timestamps, API key used
  test-call-transcript.txt  # Transcript from test call (if run)
```

### Deployment Flow Summary

1. Show user the assembled config (agent-config.json + llm-config.json).
2. User confirms deployment.
3. Run deployment via retell-api-wrapper sub-skill or `{baseDir}/scripts/deploy.sh`.
4. Save deployment receipt with agent_id and llm_id.
5. Offer test call via `{baseDir}/scripts/test-agent.sh`.
6. Present final summary: agent name, voice, agent_id, phone number (if assigned).

### Post-Deployment Checklist

Present this checklist to the user after successful deployment:
- [ ] Agent deployed: agent_id = `{agent_id}`
- [ ] Test call completed (or skipped)
- [ ] Pronunciation verified on test call
- [ ] Webhook URL configured (if applicable)
- [ ] Phone number assigned (if applicable)
- [ ] Post-call analysis variables set
- [ ] Config files saved locally in output/

### Partial Chain Output

If the user stops the chain early (e.g., "just generate the config, don't deploy"),
still save all completed outputs. The output folder should contain whatever was
produced:

- After Step 3: `prompt.txt`
- After Step 4: `prompt.txt` + `pronunciation-dict.json`
- After Step 5: `prompt.txt` + `pronunciation-dict.json` + `humanized-prompt.txt`
- After Step 7: All of the above + `llm-config.json` + `agent-config.json`
- After Step 8: All of the above + `deployment-receipt.json`

The user can resume from any saved state by asking to "continue" or "deploy now".

### Output File Formats

| File | Format | Schema |
|------|--------|--------|
| llm-config.json | JSON | Retell LLM creation payload |
| agent-config.json | JSON | Retell agent creation payload |
| pronunciation-dict.json | JSON | Array of {word, pronunciation, alphabet} |
| prompt.txt | Plain text | Raw system prompt before humanization |
| humanized-prompt.txt | Plain text | Final prompt with humanization directives |
| interview-notes.json | JSON | Structured interview answers |
| deployment-receipt.json | JSON | agent_id, llm_id, timestamps |
| test-call-transcript.txt | Plain text | Raw transcript from test call |

---

## Real-World Scenarios

### Scenario 1: Simple Receptionist

**Input:** "Create a receptionist for Dr. Smith's dental office"

**Process:**
1. Intent Detection -> "create" + "receptionist" -> CHAIN mode, `receptionist` template.
2. Pre-Execution -> Template matched. Minimal interview (3-5 questions).
3. Interview -> Ask: pronunciation of doctor name? Hours of operation? Appointment
   scheduling system? Internal or client deployment?
4. Voice Selection -> Template default: female, warm, American English. User confirms.
5. Prompt Generation -> Load receptionist template prompt. Customize with office
   name, hours, services. States: greeting, appointment_check, scheduling, transfer, closing.
6. Pronunciation -> "Dr. Smith" is fine. No custom terms needed. Skip.
7. Humanization -> Level 6 (template default). Add conversational fillers, warm
   pauses after greeting, backchannel ("mhm", "of course").
8. Latency -> Template default: responsiveness 1 (balanced), interruption
   sensitivity 0.8 (responsive to interruptions).
9. Config Assembly -> Generate llm-config.json and agent-config.json.
10. Deploy -> User confirms. Agent created. Test call offered.

**Output:** Live receptionist agent. 5-minute process.
**Resources Used:** receptionist template, voice-selector, prompt-generator,
humanization-engine, agent-config-builder, retell-api-wrapper.

### Scenario 2: Complex Sales Agent

**Input:** "Build a multilingual sales agent for our SaaS product Xeroflux.
It needs to handle objections, qualify leads, and transfer to a human for
enterprise deals. The agent should sound confident but not pushy."

**Process:**
1. Intent Detection -> "build" + "sales agent" -> CHAIN mode, `sales` template.
2. Pre-Execution -> Template matched. Full enterprise interview (complex use case,
   custom pronunciation, multi-state flow).
3. Interview -> 20 questions covering: languages (English + Spanish), product
   details, pricing tiers, qualification criteria, objection handling scripts,
   transfer conditions, CRM webhook, pronunciation of "Xeroflux".
4. Voice Selection -> Confident male, American English. ElevenLabs for emotion
   range. User auditions 3 options, picks one.
5. Prompt Generation -> Complex stateful prompt: greeting -> discovery ->
   qualification -> demo_offer -> objection_handling -> enterprise_transfer ->
   closing. Each state with transition conditions.
6. Pronunciation -> "Xeroflux" -> IPA: /ˈzɪəroʊflʌks/. Add to dictionary.
   Inject inline hint in prompt: "Xeroflux (say: ZEER-oh-flux)".
7. Humanization -> Level 7. Confident fillers ("absolutely", "great question"),
   strategic pauses before price reveals, active listening cues.
8. Latency -> Responsiveness 0 (fast — sales needs quick responses),
   interruption sensitivity 0.9 (let prospect interrupt easily).
9. Config Assembly -> Two JSON files with 8 states, webhook config for CRM.
10. Deploy -> User reviews complex config. Confirms. Deploy. Test call with
    mock objection scenario.

**Output:** Multilingual sales agent with 8 conversation states. 30-minute process.
**Resources Used:** All 7 sub-skills, sales template, pronunciation library,
enterprise interview, full chain.

### Scenario 3: Standalone Pronunciation Fix

**Input:** "Fix the pronunciation on agent_abc123 — it can't say our product
name 'Xeroflux' correctly"

**Process:**
1. Intent Detection -> "fix pronunciation" -> SINGLE mode, pronunciation-fixer.
2. Read `sub-skills/pronunciation-fixer/SKILL.md`.
3. Validate inputs -> Have: word ("Xeroflux"), agent_id (agent_abc123). Good.
4. Execute pronunciation-fixer -> Generate IPA: /ˈzɪəroʊflʌks/. Generate
   phonetic respelling: "ZEER-oh-flux". Build dictionary entry.
5. Ask user: "Apply this pronunciation fix to agent agent_abc123?"
6. User confirms. Patch agent via retell-api-wrapper (update pronunciation
   dictionary on existing agent).
7. Offer test call to verify pronunciation.

**Output:** Updated pronunciation dictionary on live agent. 2-minute process.
**Resources Used:** pronunciation-fixer, retell-api-wrapper (for patching).

---

## Decision Trees

### CHAIN vs SINGLE Decision

```
User wants to CREATE a new agent?
  YES -> Is it "quick deploy" with template only?
    YES -> Shortened CHAIN (Voice + Prompt + Config + Deploy)
    NO  -> Full 8-step CHAIN
  NO -> User wants to MODIFY or FIX something?
    YES -> Does the request touch multiple areas?
      YES -> Is it "optimize"? -> PARALLEL (latency + humanization)
      YES -> Otherwise -> Sequential CHAIN of relevant sub-skills
      NO  -> SINGLE mode for the matching sub-skill
    NO -> User wants to QUERY something (list agents, get call)?
      YES -> SINGLE mode -> retell-api-wrapper
```

### Template Auto-Detection

```
User mentions a role or industry keyword?
  YES -> Match against template trigger phrases (Phase 2, Step 2A)
    MATCH -> Pre-load template defaults, use as fallback
    NO MATCH -> Use receptionist template as neutral base
  NO -> No template. Full interview required.
```

**Freedom labels:** The agent is FREE to skip interview questions when template
defaults suffice. The agent is FREE to recommend a different template if the
user's description better matches one. The agent MUST NOT skip deployment
confirmation. The agent MUST NOT skip reading the sub-skill SKILL.md.

---

## Configuration

### Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `RETELL_API_KEY` | Yes (for deploy) | Authenticates against Retell AI API |
| `RETELL_CLIENT_API_KEY` | No | Client's API key for client-mode deployments |
| `ELEVENLABS_API_KEY` | No | Required for ElevenLabs voice cloning and custom voices |
| `TWILIO_ACCOUNT_SID` | No | Required for phone number assignment |
| `TWILIO_AUTH_TOKEN` | No | Required for phone number assignment |

See [references/ENV-VARS.md](references/ENV-VARS.md) for full details.

### Pre-Flight Check

Before any deployment, run `{baseDir}/scripts/verify.sh` to confirm tools and
credentials are available. See [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md)
if the check fails.

---

## Resource Reference Map

When you need specific information, consult these references:

| Situation | Reference File | Purpose |
|-----------|---------------|---------|
| Matching user intent to sub-skill | [references/USER-INTENT-MAP.md](references/USER-INTENT-MAP.md) | Extended NL patterns for each sub-skill |
| Selecting a template | [references/TEMPLATE-CATALOG.md](references/TEMPLATE-CATALOG.md) | 9 templates with defaults and sample prompts |
| Conducting the interview | [references/INTERVIEW-QUESTIONS.md](references/INTERVIEW-QUESTIONS.md) | Full 25-question enterprise interview |
| Making API calls | [references/API-QUICK-REFERENCE.md](references/API-QUICK-REFERENCE.md) | Curl examples for all Retell endpoints |
| Choosing a voice provider | [references/VOICE-PROVIDER-COMPARISON.md](references/VOICE-PROVIDER-COMPARISON.md) | Provider comparison matrix |
| Understanding the chain | [references/ORCHESTRATION-LOGIC.md](references/ORCHESTRATION-LOGIC.md) | Full chain execution rules and context passing |
| Deploying to client accounts | [references/MULTI-ACCOUNT-GUIDE.md](references/MULTI-ACCOUNT-GUIDE.md) | Internal vs client deployment guide |
| Setting up env vars | [references/ENV-VARS.md](references/ENV-VARS.md) | All environment variables with setup instructions |
| Debugging issues | [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md) | Common issues with fixes |
| Seeing worked examples | [references/EXAMPLES.md](references/EXAMPLES.md) | 3 end-to-end walkthroughs |
| Retell 2026 Features | [references/RETELL-2026-FEATURES.md](references/RETELL-2026-FEATURES.md) | New Retell features guide |
| Prompt Architecture | [references/PROMPT-ARCHITECTURE-GUIDE.md](references/PROMPT-ARCHITECTURE-GUIDE.md) | Research-validated prompt structure |
| Write for the Ear | [references/WRITE-FOR-THE-EAR.md](references/WRITE-FOR-THE-EAR.md) | Spoken output rules |
| Quality Testing | [references/QUALITY-TESTING.md](references/QUALITY-TESTING.md) | Pre-launch testing framework |

---

## Troubleshooting

### Top 5 Issues

1. **"401 Unauthorized" on API calls.**
   Cause: Missing or invalid RETELL_API_KEY. Fix: Run `{baseDir}/scripts/verify.sh`.
   Check that the key starts with `key_`. See [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md).

2. **Agent sounds robotic after deployment.**
   Cause: Humanization step was skipped or level set too low. Fix: Run
   humanization-engine in SINGLE mode with level 7+. Re-deploy prompt.

3. **Pronunciation not working.**
   Cause: Voice provider does not support pronunciation dictionaries, or IPA
   format is incorrect. Fix: Verify provider supports dictionaries (ElevenLabs
   Turbo v2+ does). Check IPA with pronunciation-fixer sub-skill.

4. **High latency / slow responses.**
   Cause: Model too large or responsiveness setting too high. Fix: Run
   latency-optimizer in SINGLE mode. Consider switching to a faster model.

5. **Deployment fails with 422.**
   Cause: Invalid config JSON. Fix: Validate agent-config.json against the
   schema in `{baseDir}/assets/schemas/`. Common issue: missing required
   fields like `voice_id` or `response_engine`. See
   [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md).

### Recovery Procedures

- **Partial chain failure:** The orchestrator saves all completed outputs to
  `{baseDir}/output/`. Resume by asking "continue building the agent" — the
  orchestrator will detect saved files and pick up from the failed step.

- **API key rotation:** If the API key changes mid-session, re-run
  `{baseDir}/scripts/verify.sh` to confirm the new key works. All saved
  config files remain valid and can be deployed with the new key.

- **Rollback a deployment:** Retell does not support rollback natively. To
  revert, re-deploy the previous config files (if saved) or delete the agent
  and recreate from the original config.

For the complete troubleshooting guide with detailed steps for every known
issue, see [references/TROUBLESHOOTING.md](references/TROUBLESHOOTING.md).
