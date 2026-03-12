---
name: prompt-generator
description: Generates production-ready prompts for Retell AI voice agents. Creates persona-driven prompts with tone adaptation, state-based conversation flows, guardrails, forbidden phrases, and fallback handling. Ships with 9 complete templates. Use when user says "create prompt", "write agent prompt", "update conversation flow", "add states", "improve prompt", or needs prompt engineering for voice agents.
allowed-tools: Read Write Bash(python3:*)
---

# Prompt Generator

## Overview

Voice prompts are fundamentally different from text prompts. Callers hear every word
in real time — rambling loses attention, scripted language kills trust, and written-English
constructs ("I would like to inform you that...") sound robotic.

This sub-skill generates prompts engineered for the spoken word: short utterances,
natural phrasing, emotional awareness, and structured conversation flows using Retell's
state machine. Every prompt ships with persona definition, tone adaptation rules,
forbidden phrase lists, fallback behaviors, and guardrails.

The output is a complete JSON configuration ready for the Agent Config Builder or
direct API deployment: `general_prompt`, `states` array, `begin_message`,
`model`, `model_temperature`, and `guardrail_config`.

Base directory token: `{baseDir}` = the directory containing this SKILL.md.

---

## Quick Start

**Step 1: Pick a template.**
Read the template table below and select the closest match to the user's business.
If the user says "appointment setter for a dental clinic," use `appointment-setter`.
If nothing matches, use `general-assistant` as the base and customize.

**Step 2: Gather business info.**
Ask the user for: business name, industry, what the agent should do, hours of
operation, and any special instructions. If the user is brief, fill gaps from
template defaults.

**Step 3: Run the assembler.**
Execute `{baseDir}/scripts/prompt-assembler.py` with the gathered info. It produces
a complete JSON config. Review it, adjust if the user wants changes, and pass to
the next sub-skill in the chain (or return directly if standalone).

```bash
python3 {baseDir}/scripts/prompt-assembler.py \
  --template appointment-setter \
  --business-name "Bright Smile Dental" \
  --industry "dental" \
  --agent-name "Sarah" \
  --agent-role "receptionist" \
  --tone "warm and professional"
```

The script reads templates from the references directory, applies persona and tone
rules, assembles the 8-section prompt, generates states if needed, and outputs JSON.

---

## Inputs

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `template_name` | string | Yes | One of the 9 template names (see table below) |
| `business_info` | dict | Yes | `{name, industry, hours, services, special_instructions}` |
| `persona_details` | dict | No | `{name, role, personality_traits, energy_level}` — overrides template defaults |
| `interview_answers` | dict | No | Raw answers from orchestrator interview — auto-mapped to above fields |
| `custom_states` | array | No | Additional states to inject into the flow beyond template defaults |
| `pronunciation_rules` | string | No | Output from pronunciation-fixer sub-skill — injected into PRONUNCIATION section |
| `humanization_instructions` | string | No | Output from humanization-engine sub-skill — injected into PERSONALITY section |

---

## Outputs

| Field | Type | Description |
|-------|------|-------------|
| `general_prompt` | string | The complete system prompt (all 8 sections assembled) |
| `states` | array | State objects: `{name, prompt, tools, transitions}` — empty array if single-state |
| `begin_message` | string | First utterance the agent speaks (or `""` for user-speaks-first) |
| `model` | string | Recommended LLM model ID |
| `model_temperature` | float | Temperature setting (0-1) |
| `guardrail_config` | object | `{input_topics: [...], output_topics: [...]}` |
| `start_speaker` | string | `"agent"` or `"user"` |

---

## The 9 Templates

Templates now follow the research-validated 19-section structure. See PROMPT-ARCHITECTURE-GUIDE.md for the canonical section order.

| Template | Default Persona | Default Tone | States | Begin Message | Best Model |
|----------|----------------|--------------|--------|---------------|------------|
| `appointment-setter` | Riley, Scheduling Assistant | Warm, efficient | 4 | "Hi, this is Riley from {company}. I can help you schedule an appointment — what works best for you?" | gpt-4.1-mini |
| `sales-agent` | Jordan, Sales Specialist | Confident, friendly | 5 | "Hey there! This is Jordan from {company}. Got a quick minute?" | gpt-4.1 |
| `customer-support` | Alex, Support Agent | Patient, helpful | 4 | "Hi, you've reached {company} support. I'm Alex — what's going on?" | gpt-4.1 |
| `receptionist` | Sam, Front Desk | Professional, warm | 3 | "Good morning, {company}, this is Sam speaking. How can I help?" | gpt-4.1-mini |
| `personal-assistant` | Morgan, Personal Assistant | Casual, proactive | 3 | "" (user speaks first) | gpt-4.1 |
| `lead-qualifier` | Casey, Outreach Specialist | Upbeat, direct | 5 | "Hi {name}, this is Casey from {company}. Do you have a sec?" | gpt-4.1-mini |
| `survey-agent` | Taylor, Research Associate | Neutral, encouraging | 4 | "Hi, this is Taylor calling from {company}. We're running a quick survey — do you have about 3 minutes?" | gpt-4.1-nano |
| `debt-collection` | Pat, Account Specialist | Firm, respectful | 4 | "Hello, this is Pat calling from {company} regarding your account. Is this {name}?" | gpt-4.1 |
| `real-estate` | Jamie, Real Estate Agent | Enthusiastic, knowledgeable | 5 | "Hey {name}! Jamie here from {company}. I saw you were looking at some properties — exciting stuff!" | gpt-4.1 |

All templates are baselines — users can override any default. Templates provide smart
defaults, not constraints.

---

## Phase 1: Select Template & Persona

### Template Auto-Detection

When the user describes their business without naming a template, match keywords:

| Keywords | Template |
|----------|----------|
| book, schedule, appointment, calendar, slot | `appointment-setter` |
| sell, demo, pitch, close, deal, pricing | `sales-agent` |
| help, support, issue, trouble, fix, ticket | `customer-support` |
| front desk, office, transfer, route, directory | `receptionist` |
| assistant, reminder, task, personal, manage | `personal-assistant` |
| qualify, lead, prospect, outreach, interested | `lead-qualifier` |
| survey, feedback, poll, research, opinion | `survey-agent` |
| payment, overdue, balance, collect, account | `debt-collection` |
| property, listing, showing, real estate, home, house | `real-estate` |

If multiple templates match, prefer the one with the most keyword hits. If tied,
ask the user to clarify.

### Building the Persona

Every voice agent needs a persona — a name, role, and personality. This is not
cosmetic. A persona constrains how the agent speaks, what phrases it uses, and how
it handles emotional situations.

**The 5 persona dimensions** (see [Persona Patterns](references/PERSONA-PATTERNS.md)):

1. **Warmth** (1-10): How friendly and approachable. 8+ for support, 5-6 for debt collection.
2. **Authority** (1-10): How confident and decisive. 8+ for sales, 4-5 for survey.
3. **Energy** (1-10): How upbeat and animated. 9+ for real estate, 3-4 for debt collection.
4. **Formality** (1-10): How polished the language. 8+ for debt collection, 3-4 for personal assistant.
5. **Humor** (1-10): How much levity. 6+ for real estate, 1-2 for debt collection.

Each template has default dimension scores. When the user says "make it more casual,"
decrease formality by 2-3 points. When they say "more professional," increase
formality and decrease humor.

Build the persona object:
```json
{
  "name": "Riley",
  "role": "Scheduling Assistant",
  "company": "Bright Smile Dental",
  "traits": ["warm", "efficient", "patient"],
  "warmth": 8, "authority": 5, "energy": 6, "formality": 5, "humor": 3
}
```

---

## Phase 2: Build Prompt Structure

Every voice prompt must contain these 8 sections. They are assembled in order and
concatenated into the `general_prompt` field. Each section is delimited by a markdown
header inside the prompt text.

### Section 1: IDENTITY

Who the agent is. First line of the prompt. Sets the frame for everything.

```
## Identity
You are {name}, a {role} at {company}. You handle {primary_task} for callers.
You have been working at {company} for years and know everything about {industry}.
```

Keep it to 2-3 sentences. The agent should feel like a real employee, not a bot.
Never say "You are an AI assistant." The agent IS the role.

### Section 2: PERSONALITY

How the agent speaks. Pulled from persona dimensions and the
[Persona Patterns](references/PERSONA-PATTERNS.md) reference.

```
## Personality
- You're naturally {traits joined by comma}
- You use casual contractions: "I'm", "you're", "let's", "we'll"
- You occasionally say "um" or "let me check" when looking things up
- You match the caller's energy — if they're excited, show enthusiasm
- You keep responses under 2 sentences unless explaining something complex
```

If `humanization_instructions` are provided (from humanization-engine), append them
to this section. They add fillers, pauses, and breathing patterns.

### Section 3: VOICE CHARACTERISTICS

Guides the LLM to produce text that sounds natural when synthesized by TTS.
Key rules: vary tone, keep responses to 1-2 sentences, use short sentences,
pause naturally with "...", and sound conversational — not scripted.

### Section 4: PRONUNCIATION RULES

Injected from the pronunciation-fixer sub-skill output. If no pronunciation rules
are provided, include a minimal section:

```
## Pronunciation
- Pronounce the company name as: {phonetic}
- Say phone numbers digit by digit: "5-5-5, 1-2-3, 4-5-6-7"
- Say times naturally: "two thirty" not "14:30"
- Say dates naturally: "January fifth" not "01/05"
```

If `pronunciation_rules` are provided, replace this section entirely with those rules.

### Section 5: CONVERSATION STYLE

How the agent manages the flow. Key rules: acknowledge before responding, use thinking
sounds ("hmm", "let me see"), confirm understanding before acting, ask one question at
a time, handle mishears gracefully. See [Conversation Patterns](references/CONVERSATION-PATTERNS.md).

### Section 6: TONE ADAPTATION

Dynamic tone adjustment based on caller emotion. Frustrated → slow down, empathize.
Confused → simplify. Happy → match energy. Rushed → be direct. Hesitant → encourage.
See [Tone Adaptation Guide](references/TONE-ADAPTATION-GUIDE.md).

Tone adaptation is the difference between a bot and an agent that feels human.

### Section 7: FORBIDDEN PHRASES

Robotic phrases that break the illusion. See [Forbidden Phrases](references/FORBIDDEN-PHRASES.md).
Key replacements: "Certainly" → "sure", "I apologize for the inconvenience" → "sorry about that",
"Is there anything else I can help you with?" → "anything else?", never reveal AI identity.

### Section 8: FALLBACK BEHAVIOR

Five fallback handlers every prompt needs: didn't understand, can't answer (offer transfer),
off-topic (redirect), AI question (deflect to task), system error (ask for patience).
Never leave the agent without fallbacks — silence or "I don't know" sounds broken.

---

## Phase 3: State-Based Flow Design

### When to Use States

Use Retell's state machine when the conversation has **3 or more distinct phases**.
States constrain what the agent focuses on in each phase, reducing hallucination
and keeping the conversation on track.

**Use states for:** Appointment setting (greeting → collect info → confirm booking → closing),
Sales calls (intro → qualification → pitch → objection handling → close),
Surveys (intro → questions → wrap-up).

**Skip states for:** Simple Q&A agents, personal assistants, general receptionists
where the conversation is freeform.

See [State-Based Flows](references/STATE-BASED-FLOWS.md) for complete patterns.

### Designing State Flows

Every state-based flow follows this skeleton:

```
State 1: GREETING
  → Introduce self, set context
  → Transition: after greeting → DISCOVERY

State 2: DISCOVERY
  → Ask questions, understand caller needs
  → Transition: info collected → ACTION
  → Transition: caller unsure → stay in DISCOVERY

State 3: ACTION
  → Perform the primary task (book, sell, route, record)
  → Transition: task complete → CLOSING
  → Transition: task failed → FALLBACK

State 4: CLOSING
  → Summarize, confirm, say goodbye
  → Transition: caller has more questions → DISCOVERY
  → Transition: done → end call
```

### State Object Format

Each state is a JSON object matching Retell's API:

```json
{
  "name": "greeting",
  "prompt": "You are greeting the caller. Introduce yourself as {name} from {company}. Ask how you can help today. Keep it to 1-2 sentences. Be warm but efficient.",
  "tools": [],
  "transitions": [
    {
      "to": "discovery",
      "condition": "Caller has stated their reason for calling",
      "description": "Move to discovery when caller explains their need"
    }
  ]
}
```

### State Design Rules

1. **Each state prompt should be SHORT** — 3-5 sentences max. The state constrains focus.
   Long state prompts defeat the purpose.
2. **Tools are state-specific.** A booking tool only belongs in the ACTION state, not GREETING.
3. **Transitions must have clear conditions.** Vague conditions like "when appropriate"
   cause the agent to get stuck. Use specific triggers: "caller provides their name and
   date preference."
4. **Allow backward transitions.** Callers change their mind. Let ACTION go back to
   DISCOVERY if they say "actually, wait..."
5. **The general_prompt applies to ALL states.** Put persona, tone, and forbidden phrases
   in general_prompt. Put task-specific instructions in state prompts.

### Flow Patterns

**Linear Flow** (simplest): A → B → C → D. Good for surveys and structured interviews.

**Branching Flow**: A → B → (C1 or C2 based on answer) → D. Good for qualification
where different answers lead to different paths.

**Looping Flow**: A → B → C → (back to B if incomplete) → D. Good for appointment
setting where the first time slot might not work.

See [State-Based Flows](references/STATE-BASED-FLOWS.md) for detailed examples of each pattern.

### Flex Mode vs Traditional States

Use Flex Mode for open-ended conversations with fewer than 20 nodes where the LLM drives navigation dynamically. Use Traditional States for compliance scripts, flows >20 nodes, or when an audit trail is required.

→ Full decision matrix and implementation: [FLEX-MODE-GUIDE.md](references/FLEX-MODE-GUIDE.md)

### Global Nodes (always include)

Always-accessible states from any conversation point: `transfer_to_human` (trigger: "speak to a person"), `repeat_last` (trigger: "say that again"), `end_call` (trigger: "goodbye"), `capture_name` (trigger: first name mention). Global Nodes prevent callers from getting stuck in a flow.

---

## Phase 4: Guardrails Configuration

Guardrails protect the agent from misuse and prevent harmful outputs. They are
configured via the `guardrail_config` object. See
[Guardrails Guide](references/GUARDRAILS-GUIDE.md) for the full reference.

### Input Topic Blocking

These block callers from manipulating the agent:

| Input Topic | Description | Always Enable |
|-------------|-------------|---------------|
| `jailbreaks` | Attempts to override system instructions | Yes |
| `prompt_extraction` | Attempts to get the agent to reveal its prompt | Yes |
| `instruction_bypasses` | Attempts to make the agent ignore its rules | Yes |
| `unauthorized_tool_calls` | Attempts to trigger tools the agent shouldn't use | Yes |

**Always enable all four input topic blocks.** There is no scenario where you want
callers to jailbreak your voice agent.

### Output Topic Blocking

These prevent the agent from generating harmful content:

| Output Topic | Description | Enable When |
|--------------|-------------|-------------|
| `harassment` | Insulting or threatening language | Always |
| `self_harm` | Content promoting self-harm | Always |
| `violence` | Violent or graphic content | Always |
| `gambling` | Gambling promotion | Most templates |
| `regulated_advice` | Medical, legal, financial advice | Non-expert agents |
| `sexual_exploitation` | Sexual content | Always |
| `child_safety` | Content endangering minors | Always |

### Template Guardrail Profiles

| Template | Input Blocking | Output Blocking Level | Notes |
|----------|----------------|----------------------|-------|
| `debt-collection` | All | Strict (all topics) | Regulatory compliance critical |
| `customer-support` | All | Standard (all except regulated_advice) | May need to give product guidance |
| `sales-agent` | All | Standard | Normal commercial use |
| `appointment-setter` | All | Standard | Normal commercial use |
| `receptionist` | All | Standard | Normal commercial use |
| `lead-qualifier` | All | Standard | Normal commercial use |
| `survey-agent` | All | Moderate (core safety only) | Needs latitude for survey topics |
| `personal-assistant` | All | Moderate | User-directed, needs flexibility |
| `real-estate` | All | Standard | Normal commercial use |

---

## Phase 5: Model Selection

The LLM model affects response quality, latency, and cost. Choose based on the
agent's complexity and the caller's expectations.

### Model Recommendation Matrix

| Model | Best For | Latency | Cost | Intelligence |
|-------|----------|---------|------|-------------|
| `gpt-4.1` | Complex conversations, sales, debt collection | Medium | High | Highest |
| `gpt-4.1-mini` | Most agents — balanced performance | Low | Medium | High |
| `gpt-4.1-nano` | Simple tasks, surveys, basic routing | Lowest | Low | Moderate |
| `gpt-5` | Maximum intelligence, complex reasoning | High | Highest | Maximum |
| `gpt-5-mini` | Advanced tasks with better latency than gpt-5 | Medium | High | Very High |
| `claude-4.5-sonnet` | Nuanced conversation, empathy-heavy agents | Medium | High | Highest |
| `claude-4.5-haiku` | Fast, capable, good for most use cases | Low | Medium | High |
| `gemini-2.5-flash` | Cost-effective, fast responses | Low | Low | High |
| `gemini-2.5-flash-lite` | Ultra-low-cost, simple tasks | Lowest | Lowest | Moderate |

### Decision Logic

1. **Needs complex reasoning or objection handling?** → `gpt-4.1` or `claude-4.5-sonnet`
2. **Needs empathy and emotional intelligence?** → `claude-4.5-sonnet`
3. **Cost-sensitive, moderate complexity?** → `gpt-4.1-mini` or `claude-4.5-haiku`
4. **Simple routing or survey?** → `gpt-4.1-nano` or `gemini-2.5-flash-lite`
5. **Latency-critical (fast-paced sales)?** → `gpt-4.1-mini` or `gemini-2.5-flash`

### Temperature Settings

| Use Case | Temperature | Reasoning |
|----------|------------|-----------|
| Appointment setting | 0 | Accuracy matters — no creative scheduling |
| Customer support | 0 | Consistent, reliable answers |
| Sales | 0.3 | Slight creativity for objection handling |
| Personal assistant | 0.2 | Some flexibility in responses |
| Survey | 0 | Must follow script precisely |
| Debt collection | 0 | Legal compliance, no improvisation |
| Real estate | 0.3 | Enthusiasm and variety in descriptions |

---

## Phase 6: Assemble & Validate

### Assembly Process

1. **Build persona** from template defaults + user overrides (Phase 1)
2. **Assemble 8 sections** into `general_prompt` string (Phase 2)
3. **Generate states** if conversation has 3+ phases (Phase 3)
4. **Set guardrails** by template profile (Phase 4)
5. **Select model** and temperature (Phase 5)
6. **Generate begin_message** from template, substituting `{company}`, `{name}` placeholders
7. **Set start_speaker** — `"agent"` if begin_message is set, `"user"` if empty

### Validation Checklist

Before outputting, verify:

- [ ] `general_prompt` is under 4000 characters (Retell recommendation for speed)
- [ ] Each state prompt is under 500 characters
- [ ] All state transitions reference valid state names
- [ ] No circular transitions without exit conditions
- [ ] `begin_message` has no unresolved `{placeholders}`
- [ ] Guardrails include all 4 input topic blocks
- [ ] Forbidden phrases section is present
- [ ] Fallback section is present
- [ ] Persona name matches across all sections

### Running the Assembler

```bash
python3 {baseDir}/scripts/prompt-assembler.py \
  --template appointment-setter \
  --business-name "Bright Smile Dental" \
  --industry "dental" \
  --agent-name "Sarah" \
  --agent-role "scheduling assistant" \
  --tone "warm and professional" \
  --pronunciation-rules "Say 'Bright Smile' as 'BRYTE SMYLE'" \
  --humanization "Use 'um' occasionally, say 'let me check' when looking things up"
```

Output is a JSON object written to stdout. Capture it and pass to the next sub-skill
or return to the user for review.

---

## Real-World Scenarios

### Scenario 1: Dental Receptionist from Scratch

**Input:** "I need a voice agent for my dental practice, Bright Smile Dental. It should
book appointments, answer basic questions about services, and transfer complex
insurance questions to our office manager."

**Process:**
1. Auto-detect template: `appointment-setter` (keywords: book, appointment)
2. Gather info: name=Bright Smile Dental, industry=dental, services=[cleanings, fillings,
   crowns, whitening], hours=Mon-Fri 8am-5pm
3. Build persona: Sarah, Scheduling Assistant, warmth=8, authority=5, energy=6
4. Assemble 8-section prompt with dental-specific language
5. Generate 4 states: greeting → collect-info → book-appointment → closing
6. Add transfer fallback for insurance questions
7. Select model: gpt-4.1-mini (balanced for scheduling)

**Output:** Complete JSON config with prompt, 4 states, begin_message, guardrails.

**Resources Used:** [Persona Patterns](references/PERSONA-PATTERNS.md),
[Conversation Patterns](references/CONVERSATION-PATTERNS.md),
[State-Based Flows](references/STATE-BASED-FLOWS.md)

### Scenario 2: Updating an Existing Sales Agent's Tone

**Input:** "My sales agent sounds too pushy. Make it more consultative and less aggressive."

**Process:**
1. This is a prompt modification, not a new build
2. Adjust persona dimensions: decrease authority from 9 to 6, increase warmth from 5 to 8
3. Rewrite PERSONALITY section: remove "closing" language, add "advisory" language
4. Update TONE ADAPTATION: when caller hesitates, be patient instead of pushing
5. Update FORBIDDEN: add "limited time offer", "you don't want to miss", "act now"
6. Keep existing states but soften transition conditions

**Output:** Updated `general_prompt` with adjusted tone throughout.

**Resources Used:** [Tone Adaptation Guide](references/TONE-ADAPTATION-GUIDE.md),
[Forbidden Phrases](references/FORBIDDEN-PHRASES.md),
[Persona Patterns](references/PERSONA-PATTERNS.md)

### Scenario 3: Multi-State Survey Agent

**Input:** "Build a 5-question customer satisfaction survey for our restaurant chain."

**Process:**
1. Auto-detect template: `survey-agent`
2. Design 4 states: intro → questions (loops through 5 questions) → rating → closing
3. Build neutral persona: Taylor, Research Associate, warmth=6, authority=3, energy=5
4. Each question state has specific prompt and transition to next question
5. Use gpt-4.1-nano (simple, scripted, low cost)
6. Temperature=0 (must follow script exactly)
7. Moderate guardrails (survey may touch sensitive topics)

**Output:** JSON config with 4 states (questions handled via loop in discovery state),
begin_message with survey intro, nano model selection.

**Resources Used:** [State-Based Flows](references/STATE-BASED-FLOWS.md),
[Conversation Patterns](references/CONVERSATION-PATTERNS.md),
[Guardrails Guide](references/GUARDRAILS-GUIDE.md)

---

## Decision Trees

### States vs Single Prompt (Low freedom — deterministic)

3+ distinct phases → use states. Choose flow type: **Linear** (phases always sequential: A→B→C→D) | **Branching** (path depends on caller answers: A→B→C1 or C2→D) | **Looping** (may revisit: A→B→C→back to B). Fewer than 3 phases, or fully open-ended → single `general_prompt`, no states.

### Model Selection (Low freedom — use defaults)

Default: `gpt-4.1-mini` for most agents. Override when: complex reasoning or objections → `gpt-4.1` or `claude-4.5-sonnet` | empathy-critical → `claude-4.5-sonnet` | simple routing or survey → `gpt-4.1-nano` or `gemini-2.5-flash-lite` | cost-sensitive, moderate complexity → `gemini-2.5-flash`.

### Guardrail Levels (Low freedom — template-driven)

**Strict** (debt-collection): all input + output topics blocked. **Standard** (sales, support, appointments, receptionist, lead-qualifier, real-estate): all except `regulated_advice`. **Moderate** (survey, personal-assistant): core safety only.

---

## Common Anti-Patterns

- **No formal language** — "I would be happy to assist" → "Sure, let's get you booked!"
- **No long paragraphs** — Break into bullets. LLMs process bullets more reliably.
- **No exact scripts** — "Greet warmly and mention company" not "You MUST say exactly..."
- **No ignoring caller emotion** — Always include TONE ADAPTATION section.
- **No skipping fallbacks** — Every prompt needs: didn't understand, can't answer, off-topic.
- **No over-engineering states** — 3-5 states max. Put shared behaviors in `general_prompt`.
- **No revealing AI** — Deflect: "I'm here to help you with {task}."
- **No academic language** — "Got it, you're asking about..." not "I comprehend your inquiry..."

---

## Resource Reference Map

| Resource | Path | Used In |
|----------|------|---------|
| Persona Patterns | [references/PERSONA-PATTERNS.md](references/PERSONA-PATTERNS.md) | Phase 1 (persona building) |
| Tone Adaptation Guide | [references/TONE-ADAPTATION-GUIDE.md](references/TONE-ADAPTATION-GUIDE.md) | Phase 2 (Section 6: Tone Adaptation) |
| State-Based Flows | [references/STATE-BASED-FLOWS.md](references/STATE-BASED-FLOWS.md) | Phase 3 (state design) |
| Guardrails Guide | [references/GUARDRAILS-GUIDE.md](references/GUARDRAILS-GUIDE.md) | Phase 4 (guardrail config) |
| Conversation Patterns | [references/CONVERSATION-PATTERNS.md](references/CONVERSATION-PATTERNS.md) | Phase 2 (Section 5: Conversation Style) |
| Forbidden Phrases | [references/FORBIDDEN-PHRASES.md](references/FORBIDDEN-PHRASES.md) | Phase 2 (Section 7: Forbidden) |
| Prompt Assembler Script | [scripts/prompt-assembler.py](scripts/prompt-assembler.py) | Phase 6 (assembly) |
| Flex Mode Guide | [references/FLEX-MODE-GUIDE.md](references/FLEX-MODE-GUIDE.md) | Flex Mode vs states decision |
| Prompt Architecture | [../../references/PROMPT-ARCHITECTURE-GUIDE.md](../../references/PROMPT-ARCHITECTURE-GUIDE.md) | Canonical prompt structure |
