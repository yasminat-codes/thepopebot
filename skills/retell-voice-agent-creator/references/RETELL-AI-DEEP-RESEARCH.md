# Retell AI Deep Research: Best Practices, Advanced Configuration & Insider Tips

> Last updated: 2026-02-24
> Sources: Official Retell AI docs, changelog, community forums, Hacker News, third-party reviews

---

## Table of Contents

1. [Prompt Engineering Guide](#1-prompt-engineering-guide)
2. [Situation-Specific Prompt Templates](#2-situation-specific-prompt-templates)
3. [Advanced Configuration Parameters (Full API Reference)](#3-advanced-configuration-parameters)
4. [Voice Provider Comparison & Optimal Settings](#4-voice-provider-comparison--optimal-settings)
5. [LLM Configuration & Temperature Guide](#5-llm-configuration--temperature-guide)
6. [Conversation Flow, States & Node Architecture](#6-conversation-flow-states--node-architecture)
7. [Flex Mode](#7-flex-mode)
8. [Dynamic Variables](#8-dynamic-variables)
9. [Function Calling & Tools](#9-function-calling--tools)
10. [Agent Transfer, Warm Transfer & MCP](#10-agent-transfer-warm-transfer--mcp)
11. [Background Sound & Denoising](#11-background-sound--denoising)
12. [Post-Call Analysis](#12-post-call-analysis)
13. [Human-Sounding Agent Tips](#13-human-sounding-agent-tips)
14. [Community Tips & Insider Knowledge](#14-community-tips--insider-knowledge)
15. [Changelog Highlights (2025-2026)](#15-changelog-highlights-2025-2026)
16. [Complete Prompt Template](#16-complete-prompt-template)

---

## 1. Prompt Engineering Guide

Source: https://docs.retellai.com/build/prompt-engineering-guide

### Core Structure (Mandatory Sections)

Break every prompt into these focused sections:

```
## Identity
[Who the agent is, their role, expertise, company]

## Style Guardrails
[Tone: concise, conversational, empathetic]
[What to avoid: jargon, long monologues, robotic language]

## Response Guidelines
[Format rules: dates in spoken form, one question at a time]
[Confirm understanding by paraphrasing]
[Keep responses under 2 sentences unless explaining complex topics]

## Task Instructions
[Numbered step-by-step procedure]
[Include "wait for user response" markers between steps]
[Conditional logic for different user responses]

## Objection Handling
[Predefined responses to common objections]
```

### Key Principles

1. **Sectional Organization** -- reusable, easier to maintain, easier for LLM to understand
2. **Keep responses under 2 sentences** unless explaining complex topics
3. **Ask one question at a time** -- never bundle multiple questions
4. **Use natural language with contractions** -- "I'll" not "I will", "don't" not "do not"
5. **Show empathy** -- acknowledge feelings before problem-solving
6. **Use "wait for user response" markers** when agent struggles with timing:
   ```
   1. Ask for their name
   wait for user response
   2. Ask for their email
   wait for user response
   3. Confirm both details
   ```
7. **Reference tools by exact names** -- specify exact conditions for tool usage
8. **Include trigger words/phrases** that activate tool calls
9. **Define boundaries** clarifying when NOT to use tools

### When to Use Conversation Flow vs Single Prompt

Use Conversation Flow when:
- 3-4+ conditional decision branches
- 5+ different functions/tools
- Need to track variables across conversation
- Experiencing reliability issues with single prompt

---

## 2. Situation-Specific Prompt Templates

Source: https://docs.retellai.com/build/prompt-situation-guide

### Phone Number Pronunciation
```
Always pronounce phone numbers with dashes and pauses:
"four one five - eight nine two - three two four five" (not "4158923245")
```

### Email Spelling
```
Spell emails letter-by-letter with "at" and "dot":
"n-a-m-e - at - c-o-m-p-a-n-y - dot - com"
```

### Website URL Pronunciation
```
Spell individual letters phonetically (N = "en", K = "kay"),
pronounce recognizable words naturally, say "dot" before TLD.
Example: "nklaundry.com" -> "en-kay-laundry dot com"
```

### Time Format
```
Use: "One PM" (1:00), "Three thirty PM" (3:30), "Eight forty-five AM" (8:45)
Always include AM/PM. Never use "O'clock" -- say "O-Clock" instead.
```

### Handling "Hold On" Requests

**For non-reasoning models (GPT-4.1, etc.):**
```
When the user says "hold on", "one moment", "give me a second", or similar,
output the exact text: NO_RESPONSE_NEEDED
```
(This is a stop sequence that ceases response generation)

**For reasoning models (GPT-5, GPT-5.1):**
```
When user says hold on, simply do not respond. Wait silently for them to speak again.
```

---

## 3. Advanced Configuration Parameters

Source: https://docs.retellai.com/api-references/create-agent

### Required Fields
| Parameter | Type | Description |
|-----------|------|-------------|
| `response_engine` | Object | The response engine configuration |
| `voice_id` | String | Unique voice ID for the agent |

### Voice & Audio Properties
| Parameter | Type | Default | Range | Notes |
|-----------|------|---------|-------|-------|
| `voice_model` | String | null | `eleven_turbo_v2`, `eleven_flash_v2`, `eleven_turbo_v2_5`, `eleven_flash_v2_5`, `sonic-3`, `sonic-2`, `tts-1`, `gpt-4o-mini-tts`, `speech-02-turbo`, `s1` | Voice engine model |
| `voice_temperature` | Number | 1 | [0, 2] | Stability control (lower = more stable). Only applies to ElevenLabs voices |
| `voice_speed` | Number | 1 | [0.5, 2] | Speech rate |
| `volume` | Number | 1 | [0, 2] | Agent loudness |
| `voice_emotion` | String | null | `calm`, `sympathetic`, `happy`, `sad`, `angry`, `fearful`, `surprised` | Cartesia Sonic-3 supports: Happy, Surprised, Sympathetic, Calm. MiniMax supports: Happy, Surprised, Calm |
| `enable_dynamic_voice_speed` | Boolean | false | - | Adjusts speed based on user speech rate |
| `fallback_voice_ids` | Array | null | - | Backup voices from different TTS providers for auto-failover |

### Interaction Behavior
| Parameter | Type | Default | Range | Notes |
|-----------|------|---------|-------|-------|
| `responsiveness` | Number | 1 | [0, 1] | How fast agent responds. Reducing by 0.1 adds 0.5s delay. Lower for elderly callers |
| `interruption_sensitivity` | Number | 1 | [0, 1] | How easily user can interrupt. 0 = never interrupted. Lower for noisy environments |
| `enable_backchannel` | Boolean | false | - | Enables "yeah", "uh-huh" interjections |
| `backchannel_frequency` | Number | 0.8 | [0, 1] | How often backchanneling occurs |
| `backchannel_words` | Array | defaults | - | Custom backchannel phrases |
| `reminder_trigger_ms` | Number | 10000 | - | Milliseconds of silence before reminder |
| `reminder_max_count` | Integer | 1 | >= 0 | 0 disables reminders |

### Call Management
| Parameter | Type | Default | Range | Notes |
|-----------|------|---------|-------|-------|
| `end_call_after_silence_ms` | Integer | 600000 | >= 10000 | Auto-end after silence (ms) |
| `max_call_duration_ms` | Integer | 3600000 | 60000-7200000 | 1 min to 2 hours |
| `begin_message_delay_ms` | Integer | 0 | [0, 5000] | Delay before first message |
| `ring_duration_ms` | Integer | 30000 | [5000, 90000] | Phone ringing duration |

### Speech Recognition
| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `stt_mode` | String | `fast` | `fast`, `accurate`, `custom` |
| `custom_stt_config` | Object | - | Provider: `azure` or `deepgram`, includes `endpointing_ms` |
| `vocab_specialization` | String | `general` | `general`, `medical` (English only) |
| `boosted_keywords` | Array | null | Brand names, people names, industry terms prioritized in transcription |
| `allow_user_dtmf` | Boolean | true | Enable/disable keypad input |
| `user_dtmf_options` | Object | null | `digit_limit`, `termination_key`, `timeout_ms` |
| `denoising_mode` | String | `noise-cancellation` | `no-denoise`, `noise-cancellation`, `noise-and-background-speech-cancellation` |

### Ambient Sound
| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `ambient_sound` | String | null | `coffee-shop`, `convention-hall`, `summer-outdoor`, `mountain-outdoor`, `static-noise`, `call-center` |
| `ambient_sound_volume` | Number | 1 | [0, 2] |

### Pronunciation
| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `pronunciation_dictionary` | Array | null | Objects with `word`, `alphabet` (`ipa`/`cmu`), `phoneme` |
| `normalize_for_speech` | Boolean | false | Converts numbers, dates, currency to spoken form |

### Voicemail & IVR
| Parameter | Type | Default | Range |
|-----------|------|---------|-------|
| `enable_voicemail_detection` | Boolean | false | Phone calls only |
| `voicemail_message` | String | - | Static message for voicemail |
| `voicemail_detection_timeout_ms` | Integer | 30000 | [5000, 180000] |
| `voicemail_option` | Object | null | Actions: `static_text`, `prompt`, `hangup`, `bridge_transfer` |
| `ivr_option` | Object | null | Action: `hangup` |

### Post-Call Analysis
| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `post_call_analysis_data` | Array | null | Extract: `string`, `enum`, `boolean`, `number` variables |
| `post_call_analysis_model` | String | `gpt-4.1-mini` | Also: `gpt-4.1`, `claude-4.5-sonnet`, `gemini-2.5-flash` |
| `analysis_successful_prompt` | String | - | Custom success determination prompt |
| `analysis_summary_prompt` | String | - | Custom summary generation prompt |
| `analysis_user_sentiment_prompt` | String | - | Custom sentiment evaluation prompt |

### Security & Privacy
| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `data_storage_setting` | String | `everything` | `everything`, `everything_except_pii`, `basic_attributes_only` |
| `data_storage_retention_days` | Integer | forever | [1, 730] |
| `pii_config` | Object | - | Mode: `post_call`; categories: `person_name`, `ssn`, `credit_card`, etc. |
| `guardrail_config` | Object | - | `output_topics`, `input_topics`: `harassment`, `self_harm`, `violence`, `gambling`, `regulated_advice`, `child_safety` |

### Webhooks
| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `webhook_url` | String | null | Call event listener |
| `webhook_events` | Array | `call_started`, `call_ended`, `call_analyzed` | Also: `transcript_updated`, `transfer_*` |
| `webhook_timeout_ms` | Integer | 10000 | Milliseconds |

---

## 4. Voice Provider Comparison & Optimal Settings

### Available Voice Models on Retell

| Model ID | Provider | Quality | Speed | Cost | Best For |
|----------|----------|---------|-------|------|----------|
| `eleven_turbo_v2` | ElevenLabs | High | Medium-Fast | Higher | Premium quality English |
| `eleven_flash_v2` | ElevenLabs | Medium | Fast | Medium | English-only speed priority |
| `eleven_flash_v2_5` | ElevenLabs | Medium | Fast | Medium | Multilingual, fast |
| `eleven_turbo_v2_5` | ElevenLabs | High | Medium | Higher | Multilingual, high quality |
| `sonic-3` | Cartesia | High | Ultra-Fast | $0.07/min | Best latency + emotion control |
| `sonic-2` | Cartesia | Good | Fast | Lower | Budget option |
| `tts-1` | OpenAI | Good | Medium | Medium | General purpose |
| `gpt-4o-mini-tts` | OpenAI | Good | Fast | Lower | Budget-friendly |
| `speech-02-turbo` | MiniMax | High | Fast | - | 40+ languages, voice cloning |
| `s1` | MiniMax | High | Fast | - | Newest MiniMax model |

### Provider Benchmarks

| Provider | TTFA (Time to First Audio) | Pronunciation Accuracy | Naturalness | Prosody |
|----------|---------------------------|----------------------|-------------|---------|
| ElevenLabs | ~75-150ms | 82% | High (45%) | 65% |
| OpenAI TTS | ~200ms | 77% | Low (22%) | 46% |
| Cartesia Sonic | ~95ms | High | High | High |

### Recommended Settings Per Provider

**ElevenLabs (Best for quality):**
- `voice_temperature`: 0.7-1.0 (more expressive) or 0.3-0.5 (more consistent)
- `voice_speed`: 1.0-1.1
- Supports: Voice cloning, community voices, professional voice imports
- Limitation: Community reports it sounds "flat" compared to native ElevenLabs v3

**Cartesia Sonic-3 (Best for speed + emotion):**
- `voice_emotion`: Use `happy`, `surprised`, `sympathetic`, `calm`
- Best latency of all providers
- Limitation: Fewer voice options

**MiniMax (Best for multilingual):**
- 40+ languages
- Voice cloning support
- `voice_emotion`: `happy`, `surprised`, `calm`

**OpenAI TTS (Budget option):**
- Lower naturalness scores
- Adequate for non-premium use cases

### Voice Fallback Configuration
```json
{
  "fallback_voice_ids": ["voice_id_from_different_provider"]
}
```
Auto-failover if primary TTS has issues.

---

## 5. LLM Configuration & Temperature Guide

Source: https://docs.retellai.com/build/llm-options

### Temperature Settings by Use Case

| Use Case | Temperature | Reasoning |
|----------|------------|-----------|
| Appointment Booking | 0.1-0.3 | Highly deterministic, no creativity needed |
| Data Collection | 0.1-0.3 | Consistent, reliable extraction |
| Technical Support | 0.3-0.5 | Some flexibility for explanations |
| Customer Support | 0.3-0.5 | Balanced consistency/variation |
| Sales Outreach | 0.5-0.7 | Adaptive, persuasive |
| Virtual Companion | 0.7-0.9 | Creative, varied responses |

### Structured Output
- Enable for: Production agents, critical function calls, financial/medical data
- Disable for: Development/testing, simple functions, rapid iteration
- Trade-off: Slower auto-save, reduced flexibility, but eliminates malformed function arguments

### Fast Tier (Premium)
- Cost: 1.5x standard rate
- Benefits: 50% latency variance reduction, 25% avg response time improvement, 99.9% availability
- Best for: High-value interactions, sales demos, premium customer tiers

### LLM Prompt Token Limit
- Extended to **32,768 tokens** (as of June 2025)

### Recommended LLM
- **GPT-4.1** -- best balance of quality, latency, cost
- **GPT-5** -- for complex reasoning tasks
- **GPT-5 Mini** -- balanced option
- **GPT-5 Nano** -- cost-sensitive

---

## 6. Conversation Flow, States & Node Architecture

Source: https://docs.retellai.com/build/conversation-flow/overview

### Node Types

| Node Type | Purpose |
|-----------|---------|
| **Conversation Node** | Dialogue interactions with users |
| **Function Node** | API integrations, execute actions |
| **Logic Node** | Conditional branching |
| **End Node** | Call termination |
| **Global Node** | Always-accessible nodes (e.g., "transfer to human" available from any state) |

### Key Features

- **Per-Node LLM Selection** -- change LLM model for each node (e.g., cheap model for simple greeting, powerful model for complex reasoning)
- **Per-Node Knowledge Base** -- assign specific KB to specific nodes for accuracy and latency gains
- **Fine-tune Examples** -- add example conversations per node to improve AI decisions
- **Global Node Return Paths** -- customers exit global nodes and resume previous context
- **Always Edges** -- force transitions with timing controls ("After User Responds" or "Skip User Response")
- **Equation-Based Transitions** -- `variable = value` transitions (but LLM struggles with these; prefer Prompt edges)

### Transition Types

| Type | How It Works | Best For |
|------|-------------|----------|
| **Prompt Edge** | LLM evaluates condition from conversation context | Most situations |
| **Equation Edge** | `variable = value` check | Simple variable checks |
| **Always Edge** | Automatic transition | Forced flow progression |
| **Default Edge** | Fallback when no other condition matches | Error handling |

### Pricing
Cost = time spent in each node (seconds) x model price per second for that node. Optimize by using cheaper models for simple nodes.

### Conversation Flow Components (Reusable)
- Create sub-flows as reusable components
- Update once, sync everywhere across agents
- Import/export as JSON

---

## 7. Flex Mode

Source: https://docs.retellai.com/build/conversation-flow/flex-mode

### What It Does
Compiles conversation flow into one structured prompt made of Tasks and available Tools, allowing dynamic navigation while maintaining global prompt adherence.

### When to Use
- Context switching across tasks without losing state
- Multi-task completion (user finishes several objectives simultaneously)
- Cross-flow resumption (return to previous tasks after switching)

### Configuration Levels
1. **Agent level** -- converts ALL nodes into a single flex node
2. **Component level** -- only that component's nodes convert; standard flow continues elsewhere

### Best Practices
- Keep node instructions concise
- Use **Prompt edges exclusively** -- avoid Equation edges (LLM struggles)
- Establish explicit, observable transition conditions
- **Limit to under 20 nodes** -- more causes performance degradation and hallucination
- Split larger implementations into smaller components

### Known Issues
- LLM may not consistently follow static text instructions
- Equation-based logic produces unpredictable behavior
- Node-level knowledge bases are ignored (configure KB at agent level only)

---

## 8. Dynamic Variables

Source: https://docs.retellai.com/build/dynamic-variables

### Syntax
`{{variable_name}}` -- double curly braces

### Where They Work
- Agent prompts and instructions
- Begin messages (opening greetings)
- Tool configurations (URLs, descriptions, properties)
- Call handling (voicemail, transfers)
- Webhook URLs

### System Variables (Auto-Provided)

| Variable | Description |
|----------|-------------|
| `{{current_time}}` | Formatted time in PST |
| `{{current_time_[timezone]}}` | Time in specified timezone (e.g., `{{current_time_America/New_York}}`) |
| `{{current_hour}}` | Fractional hour format |
| `{{current_calendar}}` | 14-day calendar view |
| `{{session_type}}` | "voice" or "chat" |
| `{{session_duration}}` | Elapsed time |
| `{{direction}}` | "inbound" or "outbound" |
| `{{user_number}}` | Caller's phone number |
| `{{agent_number}}` | Agent's number |
| `{{call_id}}` | Session identifier |
| `{{chat_id}}` | Chat session ID |
| `{{current_agent_state}}` | Current state name (multi-state agents) |
| `{{previous_agent_state}}` | Previous state name |

### Advanced Features
- **Nested Variables**: `{{current_time_{{my_timezone}}}}` -- evaluates inner first
- **Existence Check**: `{{variable_name}} exists` in conversation flow equations
- **All values must be strings** -- no numbers, booleans, or other types
- Missing variables remain as literal text (design prompts to handle gracefully)

### Best Practices
1. Configure agent-level defaults as safety nets
2. Design prompts that function with or without variables
3. Test with both populated and missing variables
4. Spaces around variable names are auto-trimmed

---

## 9. Function Calling & Tools

Source: https://docs.retellai.com/build/single-multi-prompt/function-calling

### Pre-built Functions
- **End Call** -- terminate gracefully
- **Transfer Call** -- route to human/department (E.164 format or SIP URI)
- **Press Digits** -- send DTMF tones for IVR navigation
- **Check Availability** -- query time slots
- **Book Calendar** -- create events
- **Send SMS** -- deliver text notifications (one-time SMS during calls available since May 2025)

### Custom Functions
- Support GET, POST, PUT, PATCH, DELETE
- Custom headers and parameters
- Reply limit: 15,000 characters
- Async execution without blocking conversation
- Error handling with fallback options
- Constants: static values or dynamic variables in functions

### Function Calling Best Practices
- **Lower temperature** when using function calls (0.1-0.3) for accuracy
- **Specify exact conditions** in prompt for when to call each function
- Reference functions by exact name
- Define sequences for multi-step operations
- Clarify when NOT to use tools

### MCP (Model Context Protocol)
- Connect external tools via MCP for HTTP-based service calls
- Add multiple tools to same server
- Restrict which tools agent can access
- Works mid-conversation

---

## 10. Agent Transfer, Warm Transfer & MCP

### Agent Transfer (Agent Swap)
- Near-instant transitions (no new phone call needed)
- Destination agent has full conversation history
- No handoff message needed
- Override via `override_agent_id` in batch calls
- Configure which agent's webhook receives updates

### Warm Transfer Features
- **Human Detection** -- completes connection only when human answers
- **Whisper Messages** -- private context summary to receiving agent before connection
- **Three-Way Messaging** -- all parties can communicate
- **On-Hold Music** -- plays during transfer
- **Caller ID Control** -- display agent's number or original caller's number
- **Rejection Capability** -- receiving agent can reject transfer

### Cold Transfer
- Simple transfer to number or SIP URI
- Less context preservation

---

## 11. Background Sound & Denoising

### Ambient Sound Options
| Sound | Use Case |
|-------|----------|
| `coffee-shop` | Casual, friendly atmosphere |
| `convention-hall` | Professional, busy environment |
| `summer-outdoor` | Relaxed, natural |
| `mountain-outdoor` | Calm, outdoor |
| `static-noise` | Subtle background presence |
| `call-center` | Professional call center simulation |

**Insider tip**: Adding `call-center` ambient sound makes the agent sound noticeably more human-like and believable. Humans expect micro-noise and room tone -- eliminating all ambient sound makes agents sound synthetic.

### Denoising Modes
| Mode | What It Does | Cost | When to Use |
|------|-------------|------|-------------|
| `noise-cancellation` (default) | Removes background noise | Free | Most situations |
| `no-denoise` | No audio processing | Free | Clean environments |
| `noise-and-background-speech-cancellation` | Removes noise AND background speech | $0.005/min | TV, construction, crowds |

### Interruption Sensitivity for Noisy Environments
Lower to ~0.8 to prevent false triggers from background noise. Trade-off: harder for user to intentionally interrupt.

---

## 12. Post-Call Analysis

Source: https://docs.retellai.com/features/post-call-analysis-create

### Analysis Types

**Boolean** -- yes/no:
```
"user_reached": "Was the user reached? Set to false if voicemail detected,
if only asked for reason of call, or only asked to leave message. Otherwise true."
```

**Text** -- detailed extraction:
```
"detailed_call_summary": Extract a summary including topic, resolution, and follow-up needs.
```

**Number** -- numerical values:
```
"purchase_intent_amount": Extract the dollar amount the customer wishes to spend.
```

**Selector** -- categorization:
```
"issue_category": ["Technical Support", "Billing Question", "Sales Inquiry", "Product Information"]
```

### Custom Prompts
- `analysis_successful_prompt`: Determine if call achieved its goal
- `analysis_summary_prompt`: Generate custom summary format
- `analysis_user_sentiment_prompt`: Evaluate sentiment with custom criteria

### Models Available
`gpt-4.1-mini` (default), `gpt-4.1`, `claude-4.5-sonnet`, `gemini-2.5-flash`

---

## 13. Human-Sounding Agent Tips

### From Retell's Official Recommendations

1. **Enable Backchanneling** (`enable_backchannel: true`)
   - Use custom words: `["yeah", "uh huh", "mm hmm", "got it", "right"]`
   - Set frequency: 0.6-0.8 for natural cadence

2. **Add Background Sound** (`ambient_sound: "call-center"`)
   - Volume: 0.3-0.5 (subtle, not overwhelming)

3. **Use Speech Normalization** (`normalize_for_speech: true`)
   - Converts "03/15/2025" to "March fifteenth, twenty twenty-five"
   - Converts "$1,500" to "fifteen hundred dollars"

4. **Set Natural Responsiveness** (`responsiveness: 0.8-0.9`)
   - Not too fast (robotic) or too slow (laggy)
   - Lower to 0.5-0.7 for elderly callers

5. **Enable Dynamic Voice Speed** (`enable_dynamic_voice_speed: true`)
   - Matches user's speaking pace

6. **Use Pronunciation Dictionary** for brand names, proper nouns

7. **Add Filler Words in Prompt**:
   ```
   Use natural speech patterns including occasional filler words like "um", "let me check",
   "so", "well". Don't overuse them -- about 1 per 3-4 sentences.
   ```

8. **Prompt for Empathy**:
   ```
   Show empathy before problem-solving. If a customer expresses frustration,
   acknowledge their feeling first: "I completely understand how frustrating that must be."
   ```

9. **Keep Responses Short** -- under 2 sentences for most responses

10. **Use Contractions** -- "I'll check that for you" not "I will check that for you"

### From Custom LLM Best Practices
- Incorporate minor verbal elements like filler words and stammering
- Keep prompts concise (longer prompts degrade performance)
- Use RAG for extensive knowledge bases instead of stuffing prompts

### From Community Feedback
- Voice sounds "too perfect" sometimes -- adding slight imperfection helps
- Turn-taking model is the key differentiator
- ~600ms end-to-end latency is achievable

---

## 14. Community Tips & Insider Knowledge

### From Hacker News (Launch HN: Retell AI YC W24)

- Platform achieves ~800ms end-to-end latency
- Developers bring their own LLM (not locked to one provider)
- Deepgram noted as fastest STT option
- Natural-sounding voices with effective interruption handling
- Better than Vocode for conversation dynamics
- Voice occasionally sounds "too perfect" or monotone (community concern)
- LLM hallucinations reported: booking unavailable slots, date confusion -- mitigate with structured conversation flow

### From Retell Community Forum

- **Interruption sensitivity at 0** completely disables interruptions
- **Speech normalization is critical** for preventing pronunciation issues with numbers, dates, currencies
- **Transfer call only works on phone calls**, not web calls
- **Webhook URL can be set at account or agent level** for flow agents
- Community requesting more emotionally expressive voices (ElevenLabs v3 level)
- Current voices described as "solid but flat" -- missing "smile in the voice", subtle empathy shifts

### Advanced Tips Most Users Don't Know

1. **Per-Node LLM Selection** -- use cheap model for greetings, expensive for complex logic
2. **Node-Level Knowledge Base** -- assign specific KB per node for better accuracy + lower latency
3. **Global Node Fine-Tuning** -- add example conversations to improve AI node-jumping decisions
4. **Conversation Flow Components** -- reusable sub-flows that sync across agents
5. **Agent Version Control** -- create versions, test, one-click revert
6. **Simulation Testing** -- write prompts to simulate full conversations, batch test
7. **Per-Call Agent Override** -- dynamically override agent config at call level
8. **Update Call with External Context** -- override dynamic variables mid-call
9. **Custom Function Constants** -- static values or dynamic variables in functions
10. **Audio Transcription Auto-Failover** -- Deepgram/Azure switching mid-call
11. **Medical Transcription Mode** (`vocab_specialization: "medical"`) -- clinical vocabulary for English
12. **Batch Call Window** -- define allowed call times (hours/days) per campaign
13. **CPS Limits Per Provider** -- control calls-per-second to protect deliverability
14. **Reserved Concurrency** -- reserve concurrent call slots for priority traffic
15. **Concurrency Blast** -- up to 3x concurrency or 300 additional concurrent calls at $0.1/min

---

## 15. Changelog Highlights (2025-2026)

### February 2026
- Agent Guardrails (block jailbreaks, filter harmful output)
- Global Node Return Paths
- Webhook & Functions Test Tools
- Always Edges (forced transitions with timing)
- Audio Transcription Auto-Failover
- Batch Testing API
- Branded Caller ID for Custom Telephony
- 7 deprecated models auto-replaced

### January 2026
- **AI QA Analyst (Retell Assure)** -- automated 24/7 call review, hallucination detection
- Alert System -- custom triggers for performance issues
- HubSpot Integration
- Voice Emotion Control (Cartesia Sonic-3, MiniMax)
- Concurrency Blast

### December 2025
- **Flex Mode** -- dynamic node navigation
- AI Assisted Warm Transfers (human detection, whisper messages)
- Agent Version Comparison (semantic diff)
- Rerun Post-Call Analysis on historical calls
- Per-Call Agent Override
- New Models: GPT-5.2, Gemini 3 Flash, Claude 4.5 Haiku & Sonnet
- New Voice Providers: MiniMax (40 languages, voice cloning)

### November 2025
- **Conversation Flow Components** (reusable sub-flows)
- Warm Transfer Caller ID Control
- Claude 4.5 Sonnet Support
- Simulation Test Case Management (import/export JSON)

### September 2025
- **Node-Level Knowledge Base**
- Role-Based Access Control (Admin, Developer, Member)
- Outbound SMS via API
- Phone Extensions & IVR Navigation
- Batch Call Window scheduling

### August 2025
- **GPT-5 Models** (GPT-5, GPT-5 Mini, GPT-5 Nano)
- Two-Way SMS Agents
- **PII Redaction** ($0.01/min)
- Toll-Free Numbers + International Calling (14 countries)
- Update Call with External Context (mid-call variable override)

### July 2025
- **Agent Transfer** (mid-call agent switching with full context)
- **MCP Client** (external tool integration)
- **Knowledge Base 2.0** (50% accuracy improvement)
- **Warm Transfer 2.0** (human detection, whisper, three-way, hold music)
- **Analytics Dashboard 2.0**
- Real-Time Variable Extraction
- Cartesia Voice Partnership

### June 2025
- Chat Widget (embeddable)
- **Fast Tier** for OpenAI Models (1.5x cost, 50% latency reduction)
- **Medical Transcription Mode**
- LLM Prompt Token Limit extended to 32,768
- Custom Function Reply Limit increased to 15,000 chars

### May 2025
- Token-Based LLM Pricing
- 100-200ms latency reduction
- One-Time SMS during calls
- Advanced Denoising Mode
- Equation-Based Transitions
- Retell MCP Server
- Make & Zapier Integrations

### April 2025
- GPT-4.1 Family
- **Agent Version Control**
- Expanded Multilingual Support

### March 2025
- **Simulation Testing**
- System Default Dynamic Variables
- Inbound Call Webhook routing
- Agent Folders

### February 2025
- **Performance Analytics**
- Conversational Flow Testing Suite
- Telnyx Integration
- Import/Export Agents

### January 2025
- **Conversation Flow Agent (Beta)**
- Usage-Based Pricing per node

---

## 16. Complete Prompt Template

Based on all research, here is an optimal prompt structure:

```
## Identity
You are [Name], a [role] at [Company]. You help customers with [primary tasks].
You are friendly, professional, and efficient.

## Style Guardrails
- Be concise: Keep responses under 2 sentences unless explaining something complex.
- Be conversational: Use contractions (I'll, don't, we're). Speak naturally.
- Be empathetic: Acknowledge feelings before solving problems.
- Use filler words occasionally: "Let me check on that", "So", "Well"
- Never use technical jargon unless the customer does first.
- Never reveal you are an AI unless directly asked.

## Response Guidelines
- Ask only ONE question at a time.
- Pronounce phone numbers with pauses: "four one five - eight nine two - three two four five"
- Spell emails letter by letter: "j-o-h-n - at - company - dot - com"
- Say times naturally: "Three thirty PM" not "15:30"
- Confirm important details by paraphrasing: "Just to make sure I have that right..."
- If user says "hold on" or "one moment", respond with NO_RESPONSE_NEEDED

## Task
1. Greet the customer warmly using their name if available: "Hi {{customer_name}}, thanks for calling [Company]! How can I help you today?"
wait for user response
2. Listen to their request and identify their intent.
wait for user response
3. [Specific task steps with conditional logic]
   - If [condition A]: [action]
   - If [condition B]: [action]
wait for user response
4. Confirm all details before taking action.
wait for user response
5. Execute the appropriate function (call [exact_function_name] with collected parameters).
6. Confirm completion and ask if there's anything else.
7. End the call warmly: "Thanks for calling [Company]! Have a great day."

## Objection Handling
- If customer is frustrated: "I completely understand how frustrating that must be. Let me help fix this right away."
- If customer wants to speak to a human: "Of course, let me connect you with a team member right away." Then call transfer_call.
- If customer questions pricing: [specific response]
- If customer wants to cancel: [specific retention script]

## Important Rules
- NEVER make up information. If you don't know, say "Let me check on that" and use the appropriate function.
- NEVER discuss competitor products.
- ALWAYS confirm before making changes to accounts.
- If the customer provides sensitive information (SSN, credit card), acknowledge but do not repeat it back.
```

### Recommended Agent Settings to Pair With This Prompt

```json
{
  "voice_model": "sonic-3",
  "voice_speed": 1.0,
  "voice_temperature": 0.8,
  "volume": 1.0,
  "enable_dynamic_voice_speed": true,
  "responsiveness": 0.85,
  "interruption_sensitivity": 0.8,
  "enable_backchannel": true,
  "backchannel_frequency": 0.7,
  "backchannel_words": ["yeah", "uh huh", "mm hmm", "got it", "right"],
  "ambient_sound": "call-center",
  "ambient_sound_volume": 0.4,
  "normalize_for_speech": true,
  "reminder_trigger_ms": 10000,
  "reminder_max_count": 2,
  "end_call_after_silence_ms": 30000,
  "max_call_duration_ms": 1800000,
  "stt_mode": "fast",
  "denoising_mode": "noise-cancellation",
  "boosted_keywords": ["[brand name]", "[product names]", "[people names]"],
  "enable_voicemail_detection": true
}
```

---

## Sources

- [Retell AI Prompt Engineering Guide](https://docs.retellai.com/build/prompt-engineering-guide)
- [Retell AI Situation-Specific Prompt Guide](https://docs.retellai.com/build/prompt-situation-guide)
- [Retell AI Configure Basic Settings](https://docs.retellai.com/build/single-multi-prompt/configure-basic-settings)
- [Retell AI Conversation Flow Overview](https://docs.retellai.com/build/conversation-flow/overview)
- [Retell AI Custom LLM Best Practices](https://docs.retellai.com/integrate-llm/llm-best-practice)
- [Retell AI LLM Options](https://docs.retellai.com/build/llm-options)
- [Retell AI Global Settings](https://docs.retellai.com/build/conversation-flow/global-setting)
- [Retell AI Single Prompt Guide](https://docs.retellai.com/build/single-multi-prompt/write-single-prompt)
- [Retell AI Multi-Prompt Guide](https://docs.retellai.com/build/single-multi-prompt/write-multi-prompt)
- [Retell AI Create Agent API](https://docs.retellai.com/api-references/create-agent)
- [Retell AI Flex Mode](https://docs.retellai.com/build/conversation-flow/flex-mode)
- [Retell AI Dynamic Variables](https://docs.retellai.com/build/dynamic-variables)
- [Retell AI Function Calling](https://docs.retellai.com/build/single-multi-prompt/function-calling)
- [Retell AI Background Noise Handling](https://docs.retellai.com/build/handle-background-noise)
- [Retell AI Post-Call Analysis](https://docs.retellai.com/features/post-call-analysis-create)
- [Retell AI Changelog](https://www.retellai.com/changelog)
- [Retell AI Blog: 5 Useful Prompts](https://www.retellai.com/blog/5-useful-prompts-for-building-ai-voice-agents-on-retell-ai)
- [Retell AI Blog: Voice Bot Scripts](https://www.retellai.com/blog/how-to-write-voice-bot-prompt)
- [Retell AI Blog: Training & Customizing](https://www.retellai.com/blog/training-and-customizing-voice-agents-with-retell-ai)
- [Retell AI Blog: Conversation Flow](https://www.retellai.com/blog/unlocking-complex-interactions-with-retell-ais-conversation-flow)
- [Retell AI Blog: Prompt-Based vs Conversational Pathways](https://www.retellai.com/blog/prompt-based-vs-conversational-pathways-choosing-the-right-approach)
- [Retell AI Blog: Building Good Voice Agents](https://docs.retellai.com/blog/build-voice-agent)
- [Hacker News: Launch HN Retell AI](https://news.ycombinator.com/item?id=39453402)
- [Retell AI Community Forum](https://community.retellai.com/)
- [Retell AI Agent Transfer](https://docs.retellai.com/build/single-multi-prompt/transfer-agent)
