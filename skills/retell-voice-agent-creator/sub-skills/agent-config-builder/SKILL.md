---
name: agent-config-builder
description: Assembles complete Retell AI agent configurations by merging outputs from all sub-skills. Generates llm-config.json and agent-config.json, validates against API schema, auto-configures post-call analytics, generates test scenarios, and supports A/B testing variants. Use when user says "build config", "assemble agent", "generate config", "create test scenarios", "A/B test", or needs to combine all settings into deployable configs.
allowed-tools: Read Write Bash(python3:*) Bash(chmod:*)
---

## Overview

This sub-skill is the final assembly step in the Retell AI Voice Agent Creator
pipeline. It takes outputs from all other sub-skills (voice-selector,
prompt-generator, pronunciation-fixer, humanization-engine, latency-optimizer),
merges them into two deployable configuration files, validates everything against
the Retell API schema, auto-configures post-call analytics, and generates test
scenarios.

The two output files map directly to Retell API endpoints:
- `llm-config.json` — body for `POST /create-retell-llm`
- `agent-config.json` — body for `POST /create-agent`

These files are consumed by the [retell-api-wrapper](../retell-api-wrapper/SKILL.md)
sub-skill for deployment.

## Quick Start

Assemble a complete agent config in three steps:

**Step 1: Gather sub-skill outputs**

```bash
# Ensure these files exist from prior sub-skill runs
ls voice_config.json       # from voice-selector
ls prompt_config.json      # from prompt-generator
ls pronunciation_dict.json # from pronunciation-fixer
ls humanization_config.json # from humanization-engine
ls latency_config.json     # from latency-optimizer
```

**Step 2: Run the builder**

```bash
python3 build-config.py \
  --voice-config voice_config.json \
  --prompt-config prompt_config.json \
  --pronunciation pronunciation_dict.json \
  --humanization humanization_config.json \
  --latency latency_config.json \
  --template appointment-setter \
  --business-info business_info.json
```

**Step 3: Validate**

```bash
python3 validate-config.py --llm-config llm-config.json --agent-config agent-config.json
```

## Inputs

| Input | Source Sub-Skill | Required | Description |
|-------|-----------------|----------|-------------|
| `voice_config.json` | voice-selector | Yes | Voice ID, fallback voices, model |
| `prompt_config.json` | prompt-generator | Yes | General prompt, begin message, states, tools, model, temperature |
| `pronunciation_dict.json` | pronunciation-fixer | No | Array of {word, alphabet, phoneme} entries |
| `humanization_config.json` | humanization-engine | No | Backchannel, filler, pacing, emotion settings |
| `latency_config.json` | latency-optimizer | No | Responsiveness, interruption sensitivity, voice speed tuning |
| `template_name` | orchestrator | Yes | One of: appointment-setter, sales-outbound, sales-inbound, customer-support, lead-qualifier, survey, reminder, receptionist, custom |
| `business_info.json` | user input | Yes | Business name, industry, contact info for prompt injection |

## Outputs

| Output | Format | Description |
|--------|--------|-------------|
| `llm-config.json` | JSON | Complete LLM config ready for `/create-retell-llm` |
| `agent-config.json` | JSON | Complete agent config ready for `/create-agent` |
| `test-scenarios.json` | JSON | 10-15 test scenarios with scoring rubric |
| `optimization-report.md` | Markdown | Explains every configuration decision |
| `deployment-guide.md` | Markdown | Step-by-step deployment instructions |

## Phase 1: Collect Sub-Skill Outputs

Gather outputs from each sub-skill that has run. Not all are required — the
builder uses sensible defaults for missing inputs.

### Required Outputs

**voice-selector** produces `voice_config.json`:
```json
{
  "voice_id": "11labs-Myra",
  "voice_name": "Myra",
  "provider": "elevenlabs",
  "fallback_voice_ids": ["openai-alloy", "deepgram-luna"],
  "voice_model": null
}
```

**prompt-generator** produces `prompt_config.json`:
```json
{
  "general_prompt": "You are a friendly receptionist...",
  "begin_message": "Hi, thanks for calling...",
  "model": "gpt-4.1",
  "model_temperature": 0.4,
  "start_speaker": "agent",
  "states": [...],
  "general_tools": [...],
  "guardrail_config": {...}
}
```

### Optional Outputs

**pronunciation-fixer** produces `pronunciation_dict.json`:
```json
[
  {"word": "Acme", "alphabet": "ipa", "phoneme": "AEK.mi"},
  {"word": "Dr. Smith", "alphabet": "ipa", "phoneme": "DAHK.ter SMITH"}
]
```

**humanization-engine** produces `humanization_config.json`:
```json
{
  "enable_backchannel": true,
  "backchannel_frequency": 0.5,
  "backchannel_words": ["mhm", "I see", "right"],
  "voice_emotion": "calm",
  "ambient_sound": "coffee-shop",
  "ambient_sound_volume": 0.3,
  "voice_temperature": 1.2
}
```

**latency-optimizer** produces `latency_config.json`:
```json
{
  "responsiveness": 0.85,
  "interruption_sensitivity": 0.7,
  "voice_speed": 1.05,
  "enable_dynamic_voice_speed": true
}
```

## Phase 2: Build llm-config.json

Map prompt-generator outputs to Retell LLM API fields. The builder script reads
`prompt_config.json` and constructs the LLM config.

### Field Mapping

| prompt_config Field | llm-config Field | Notes |
|--------------------|-----------------|-------|
| `general_prompt` | `general_prompt` | Direct copy |
| `begin_message` | `begin_message` | Direct copy |
| `model` | `model` | Default: "gpt-4.1" |
| `model_temperature` | `model_temperature` | Default: 0.4 |
| `start_speaker` | `start_speaker` | Required. Default: "agent" |
| `states` | `states` | Array of state objects with edges |
| `general_tools` | `general_tools` | Array of tool objects |
| `guardrail_config` | `guardrail_config` | Output/input topic restrictions |
| `knowledge_base_ids` | `knowledge_base_ids` | Pass through if present |

### Example Output: llm-config.json

```json
{
  "start_speaker": "agent",
  "model": "gpt-4.1",
  "model_temperature": 0.4,
  "general_prompt": "You are a friendly receptionist for Acme Dental...",
  "begin_message": "Hi, thanks for calling Acme Dental! How can I help you today?",
  "states": [
    {
      "name": "greeting",
      "prompt": "Determine caller intent...",
      "edges": [
        {"description": "Wants to book", "destination_state_name": "booking"},
        {"description": "Has a question", "destination_state_name": "faq"}
      ]
    }
  ],
  "general_tools": [
    {"type": "end_call", "name": "end_call", "description": "Conversation complete"}
  ],
  "guardrail_config": {
    "output_topics": ["Only discuss dental services and appointments."],
    "input_topics": ["Redirect non-dental questions politely."]
  }
}
```

### Conflict Resolution

If `states` is provided, `general_prompt` is ignored by Retell (states take
precedence). The builder warns about this but includes both for documentation.

If `model` is not specified, defaults to `"gpt-4.1"`. If `model_temperature` is
not specified, defaults to `0.4` for consistency.

## Phase 3: Build agent-config.json

Map all non-LLM sub-skill outputs to Retell Agent API fields.

### Field Mapping

| Source | Config Field | agent-config Field | Notes |
|--------|-----------|--------------------|-------|
| voice-selector | `voice_id` | `voice_id` | Required |
| voice-selector | `fallback_voice_ids` | `fallback_voice_ids` | Array of backup voices |
| voice-selector | `voice_model` | `voice_model` | Provider-specific model |
| humanization | `voice_temperature` | `voice_temperature` | Default: 1.0, Range: 0-2 |
| latency | `voice_speed` | `voice_speed` | Default: 1.0, Range: 0.5-2 |
| latency | `enable_dynamic_voice_speed` | `enable_dynamic_voice_speed` | Default: false |
| humanization | `voice_emotion` | `voice_emotion` | Enum value |
| latency | `responsiveness` | `responsiveness` | Default: 0.8, Range: 0-1 |
| latency | `interruption_sensitivity` | `interruption_sensitivity` | Default: 0.7, Range: 0-1 |
| humanization | `enable_backchannel` | `enable_backchannel` | Default: true |
| humanization | `backchannel_frequency` | `backchannel_frequency` | Range: 0-1 |
| humanization | `backchannel_words` | `backchannel_words` | Custom words array |
| humanization | `ambient_sound` | `ambient_sound` | Enum value |
| humanization | `ambient_sound_volume` | `ambient_sound_volume` | Range: 0-2 |
| pronunciation | (array) | `pronunciation_dictionary` | [{word, alphabet, phoneme}] |
| — | — | `normalize_for_speech` | Default: true |
| — | — | `language` | Default: "en-US" |
| — | — | `denoising_mode` | Default: "noise-cancellation" |
| — | — | `end_call_after_silence_ms` | Default: 30000 |
| — | — | `max_call_duration_ms` | Default: 900000 (15 min) |
| auto | — | `post_call_analysis_data` | Auto-configured by template |
| — | — | `data_storage_setting` | Default: "everything" |

### Example Output: agent-config.json

```json
{
  "voice_id": "11labs-Myra",
  "fallback_voice_ids": ["openai-alloy", "deepgram-luna"],
  "voice_temperature": 1.2,
  "voice_speed": 1.05,
  "enable_dynamic_voice_speed": true,
  "voice_emotion": "calm",
  "responsiveness": 0.85,
  "interruption_sensitivity": 0.7,
  "enable_backchannel": true,
  "backchannel_frequency": 0.5,
  "backchannel_words": ["mhm", "I see", "right"],
  "ambient_sound": "coffee-shop",
  "ambient_sound_volume": 0.3,
  "pronunciation_dictionary": [
    {"word": "Acme", "alphabet": "ipa", "phoneme": "AEK.mi"}
  ],
  "normalize_for_speech": true,
  "language": "en-US",
  "denoising_mode": "noise-cancellation",
  "end_call_after_silence_ms": 30000,
  "max_call_duration_ms": 900000,
  "post_call_analysis_data": [
    {"name": "call_summary", "type": "string", "description": "Summarize the call."},
    {"name": "user_sentiment", "type": "enum", "description": "positive, neutral, negative"},
    {"name": "appointment_booked", "type": "boolean", "description": "Did the caller book?"}
  ],
  "data_storage_setting": "everything"
}
```

### Merge Priority

When multiple sub-skills set the same field (e.g., `voice_temperature` from both
humanization-engine and latency-optimizer), the priority is:

1. latency-optimizer (performance-critical settings take precedence)
2. humanization-engine (experience settings)
3. voice-selector (base voice settings)
4. Defaults

## Phase 4: Auto-Configure Post-Call Analytics

Based on the template, automatically add the right `post_call_analysis_data`
variables. Every agent gets universal variables plus template-specific ones.

### Universal Variables (all templates)

| Name | Type | Description |
|------|------|-------------|
| `call_summary` | string | Summarize the call in 2-3 sentences |
| `user_sentiment` | enum | Caller sentiment: positive, neutral, negative |

### Template-Specific Variables

**appointment-setter:**
| Name | Type | Description |
|------|------|-------------|
| `appointment_booked` | boolean | Was an appointment successfully booked? |
| `appointment_date` | string | Date and time of the booked appointment |
| `appointment_type` | string | Type of service requested |

**sales-outbound / sales-inbound:**
| Name | Type | Description |
|------|------|-------------|
| `did_express_interest` | boolean | Did the prospect express interest? |
| `lead_score` | number | Rate lead quality 1-10 |
| `objections_raised` | string | List any objections the prospect raised |
| `next_steps` | string | What follow-up actions are needed? |

**customer-support:**
| Name | Type | Description |
|------|------|-------------|
| `issue_resolved` | boolean | Was the issue fully resolved? |
| `issue_category` | enum | billing, technical, account, general, other |
| `escalation_needed` | boolean | Does this need human follow-up? |

**lead-qualifier:**
| Name | Type | Description |
|------|------|-------------|
| `is_qualified` | boolean | Does the lead meet qualification criteria? |
| `budget_range` | string | Stated or implied budget |
| `timeline` | string | When do they want to proceed? |
| `decision_maker` | boolean | Is the caller the decision maker? |

**survey:**
| Name | Type | Description |
|------|------|-------------|
| `survey_completed` | boolean | Did the caller complete all questions? |
| `responses` | string | Summarize all survey responses |

**reminder:**
| Name | Type | Description |
|------|------|-------------|
| `reminder_acknowledged` | boolean | Did the caller confirm the reminder? |
| `reschedule_requested` | boolean | Did the caller ask to reschedule? |

**receptionist:**
| Name | Type | Description |
|------|------|-------------|
| `call_purpose` | string | Why did the caller call? |
| `transferred` | boolean | Was the call transferred? |
| `message_taken` | string | Any message left for staff |

See [POST-CALL-ANALYTICS.md](references/POST-CALL-ANALYTICS.md) for the full
reference.

## Phase 5: Validate Config

Run [validate-config.py](scripts/validate-config.py) to check both configs against
the Retell API schema before deployment.

### Validation Checks

**Required fields:**
- `llm-config.json`: `start_speaker` must be present
- `agent-config.json`: `voice_id` must be present

**Range checks:**
| Field | Min | Max |
|-------|-----|-----|
| `voice_temperature` | 0 | 2 |
| `voice_speed` | 0.5 | 2 |
| `volume` | 0 | 2 |
| `responsiveness` | 0 | 1 |
| `interruption_sensitivity` | 0 | 1 |
| `backchannel_frequency` | 0 | 1 |
| `ambient_sound_volume` | 0 | 2 |
| `model_temperature` | 0 | 2 |
| `end_call_after_silence_ms` | 1000 | 600000 |
| `max_call_duration_ms` | 60000 | 7200000 |

**Type checks:**
- Arrays must be arrays (fallback_voice_ids, backchannel_words, etc.)
- Enums must match allowed values (ambient_sound, denoising_mode, etc.)
- Numbers must be numeric

**Cross-config checks:**
- If states are defined, warn that general_prompt may be ignored
- State edges must reference valid state names

See [VALIDATION-RULES.md](references/VALIDATION-RULES.md) for the complete rules.

## Phase 6: Generate Test Scenarios

Run [generate-tests.py](scripts/generate-tests.py) to create 10-15 test scenarios
tailored to the agent's template and configuration.

### Scenario Categories

**Happy path (3-4 scenarios):** Standard successful interactions.
- Straightforward caller who follows the expected flow
- Caller who needs minor clarification but completes successfully
- Repeat caller who knows the process
- Caller with a simple variant of the main use case

**Edge cases (3-4 scenarios):** Unusual but valid situations.
- Caller who changes their mind mid-conversation
- Caller with background noise
- Caller who provides incomplete information
- Caller who asks an off-topic question

**Pronunciation tests (2-3 scenarios):** Validate pronunciation dictionary.
- Caller mentions business name and key terms
- Caller asks to spell out names or addresses
- Caller uses terms from the pronunciation dictionary

**Emotional tone tests (2-3 scenarios):** Validate humanization settings.
- Frustrated caller who needs empathy
- Excited caller with high energy
- Confused caller who needs patient guidance

### Scoring Rubric

Each scenario is scored on 5 dimensions (1-10 scale):

| Dimension | Weight | Measures |
|-----------|--------|----------|
| Pronunciation Accuracy | 20% | Business names, terms pronounced correctly |
| Response Latency | 20% | Appropriate pause lengths, no awkward delays |
| Conversational Tone | 25% | Natural, matches configured emotion/personality |
| Interruption Handling | 15% | Graceful response to interruptions |
| Fallback Behavior | 20% | Handles off-topic or unclear input gracefully |

See [TEST-SCENARIO-PATTERNS.md](references/TEST-SCENARIO-PATTERNS.md) for template-
specific scenario patterns.

## Phase 7: Generate Reports

### Optimization Report

The builder generates `optimization-report.md` explaining every decision:

- **Voice choice:** Why this voice was selected, what alternatives exist
- **Humanization settings:** Why these backchannel/emotion/ambient settings
- **Latency tuning:** Why these responsiveness and speed values
- **Pronunciation:** How many terms were added, coverage assessment
- **Analytics:** Which post-call variables were added and why
- **Trade-offs:** Any compromises between latency and naturalness

### Deployment Guide

The builder generates `deployment-guide.md` with step-by-step instructions:

1. Review and approve both config files
2. Source the API wrapper: `source retell-api.sh`
3. Deploy using `deploy-agent.sh`
4. Set up webhooks if needed
5. Run test scenarios
6. Monitor first 10 calls
7. Adjust and redeploy if needed

## A/B Testing

Create 2-3 agent variants to compare performance. Each variant changes one
dimension while keeping others constant.

### Variant Dimensions

| Dimension | Variant A | Variant B | Variant C |
|-----------|-----------|-----------|-----------|
| Voice | Primary voice | Different gender/accent | Different provider |
| Humanization | Full (backchannel + ambient) | Minimal (no backchannel) | — |
| Responsiveness | Conservative (0.7) | Aggressive (0.95) | — |
| Prompt style | Warm and casual | Professional and concise | — |

### Creating Variants

The builder creates separate config files for each variant:

```
agent-config-v1.json      # Primary
agent-config-v2.json      # Different voice
agent-config-v3.json      # Different humanization
llm-config-v1.json        # Primary prompt
llm-config-v2.json        # Alternative prompt style
```

### Variant Naming

Agents are named with variant suffixes:
- `Acme Receptionist (A)` — primary
- `Acme Receptionist (B)` — voice variant
- `Acme Receptionist (C)` — humanization variant

### Analysis

After 50+ calls per variant, compare:
- Post-call analysis scores (sentiment, success rate)
- Average call duration
- Transfer/escalation rate
- Customer satisfaction proxy (sentiment distribution)

See [AB-TESTING-GUIDE.md](references/AB-TESTING-GUIDE.md) for the full guide.

## Real-World Scenarios

### Scenario 1: Full Config Assembly from Pipeline

A dental office needs an appointment-booking agent. All sub-skills have run.

1. **Collect outputs** — voice_config.json (Myra, ElevenLabs), prompt_config.json
   (appointment states), pronunciation_dict.json (Dr. names), humanization_config.json
   (calm, coffee-shop ambient), latency_config.json (responsive, moderate speed).

2. **Run builder:**
   ```bash
   python3 build-config.py \
     --voice-config voice_config.json \
     --prompt-config prompt_config.json \
     --pronunciation pronunciation_dict.json \
     --humanization humanization_config.json \
     --latency latency_config.json \
     --template appointment-setter \
     --business-info business_info.json
   ```

3. **Validate:**
   ```bash
   python3 validate-config.py --llm-config llm-config.json --agent-config agent-config.json
   # Output: All 24 checks PASSED
   ```

4. **Generate tests:**
   ```bash
   python3 generate-tests.py --agent-config agent-config.json --template appointment-setter
   # Output: 12 test scenarios written to test-scenarios.json
   ```

5. **Deploy** using retell-api-wrapper.

### Scenario 2: A/B Test Setup

A sales team wants to test two approaches for outbound cold calls.

1. **Create Variant A** — warm, casual tone with backchannel and coffee-shop
   ambient. Voice: Myra (female, friendly).

2. **Create Variant B** — professional, concise tone without backchannel, no
   ambient sound. Voice: Adrian (male, authoritative).

3. **Build both configs:**
   ```bash
   # Variant A
   python3 build-config.py --voice-config voice_a.json --prompt-config prompt_a.json \
     --humanization human_a.json --template sales-outbound --business-info biz.json
   mv agent-config.json agent-config-a.json
   mv llm-config.json llm-config-a.json

   # Variant B
   python3 build-config.py --voice-config voice_b.json --prompt-config prompt_b.json \
     --humanization human_b.json --template sales-outbound --business-info biz.json
   mv agent-config.json agent-config-b.json
   mv llm-config.json llm-config-b.json
   ```

4. **Deploy both** via retell-api-wrapper, naming them "Sales (A)" and "Sales (B)".

5. **After 50 calls each**, compare `did_express_interest` and `lead_score`
   across variants.

## Decision Trees

**Which analytics config?**
```
Template = appointment-setter? --> appointment_booked, appointment_date, appointment_type
Template = sales-*?            --> did_express_interest, lead_score, objections_raised
Template = customer-support?   --> issue_resolved, issue_category, escalation_needed
Template = lead-qualifier?     --> is_qualified, budget_range, timeline, decision_maker
Template = survey?             --> survey_completed, responses
Template = reminder?           --> reminder_acknowledged, reschedule_requested
Template = receptionist?       --> call_purpose, transferred, message_taken
Template = custom?             --> call_summary + user_sentiment only (user adds custom)
```

**When to create A/B variants?**
```
Client unsure about voice?       --> Create voice variants
Client unsure about tone?        --> Create prompt style variants
High-stakes deployment?          --> Create conservative vs aggressive responsiveness variants
First agent for this use case?   --> Create 2 variants as baseline
```

## Resource Reference Map

| Resource | Reference File | Script |
|----------|---------------|--------|
| Config schema | [CONFIG-SCHEMA.md](references/CONFIG-SCHEMA.md) | [build-config.py](scripts/build-config.py) |
| Post-call analytics | [POST-CALL-ANALYTICS.md](references/POST-CALL-ANALYTICS.md) | [build-config.py](scripts/build-config.py) |
| A/B testing | [AB-TESTING-GUIDE.md](references/AB-TESTING-GUIDE.md) | [build-config.py](scripts/build-config.py) |
| Validation rules | [VALIDATION-RULES.md](references/VALIDATION-RULES.md) | [validate-config.py](scripts/validate-config.py) |
| Test patterns | [TEST-SCENARIO-PATTERNS.md](references/TEST-SCENARIO-PATTERNS.md) | [generate-tests.py](scripts/generate-tests.py) |
