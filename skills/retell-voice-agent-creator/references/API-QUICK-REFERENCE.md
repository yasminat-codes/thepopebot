# Retell API Quick Reference

Base URL: `https://api.retellai.com`
Authentication: `Authorization: Bearer $RETELL_API_KEY`
Content-Type: `application/json`

## Create Retell LLM

Creates the LLM configuration (system prompt, states, model, tools).

```bash
curl -s -X POST "https://api.retellai.com/create-retell-llm" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "general_prompt": "You are a helpful receptionist...",
    "general_tools": [],
    "states": [
      {
        "name": "greeting",
        "state_prompt": "Greet the caller warmly.",
        "transitions": [
          {
            "transition_name": "caller_has_question",
            "description": "Caller asks a question",
            "destination": "inquiry"
          }
        ]
      }
    ]
  }'
```

**Success response:**
```json
{
  "llm_id": "llm_abc123",
  "model": "gpt-4o-mini",
  "general_prompt": "...",
  "last_modification_timestamp": 1700000000
}
```

## Create Agent

Creates an agent with voice, LLM, and behavioral settings.

```bash
curl -s -X POST "https://api.retellai.com/create-agent" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "Dr Smith Receptionist",
    "voice_id": "elevenlabs_voice_abc123",
    "response_engine": {
      "type": "retell-llm",
      "llm_id": "llm_abc123"
    },
    "language": "en-US",
    "responsiveness": 1,
    "interruption_sensitivity": 0.8,
    "enable_backchannel": true,
    "ambient_sound": "off",
    "ambient_sound_volume": 1,
    "end_call_after_silence_ms": 30000,
    "max_call_duration_ms": 1800000,
    "post_call_analysis_data": [
      {
        "name": "caller_name",
        "type": "string",
        "description": "Name of the caller"
      }
    ],
    "webhook_url": "https://example.com/webhook"
  }'
```

**Success response:**
```json
{
  "agent_id": "agent_abc123",
  "agent_name": "Dr Smith Receptionist",
  "voice_id": "elevenlabs_voice_abc123",
  "response_engine": { "type": "retell-llm", "llm_id": "llm_abc123" },
  "last_modification_timestamp": 1700000000
}
```

## Update Agent

Patches an existing agent with new settings.

```bash
curl -s -X PATCH "https://api.retellai.com/update-agent/agent_abc123" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": "new_voice_id",
    "responsiveness": 0,
    "pronunciation_dictionary": [
      {
        "word": "Xeroflux",
        "pronunciation": "/ˈzɪəroʊflʌks/",
        "alphabet": "ipa"
      }
    ]
  }'
```

**Success response:** Same shape as create-agent response with updated fields.

## Get Agent

Retrieves agent details by ID.

```bash
curl -s -X GET "https://api.retellai.com/get-agent/agent_abc123" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

**Success response:** Full agent object (same shape as create response).

## List Agents

Returns all agents in the account.

```bash
curl -s -X GET "https://api.retellai.com/list-agents" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

**Success response:**
```json
[
  {
    "agent_id": "agent_abc123",
    "agent_name": "Dr Smith Receptionist",
    "voice_id": "...",
    "last_modification_timestamp": 1700000000
  }
]
```

## Delete Agent

Deletes an agent permanently.

```bash
curl -s -X DELETE "https://api.retellai.com/delete-agent/agent_abc123" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

**Success response:** `204 No Content`

## List Voices

Returns all available voices.

```bash
curl -s -X GET "https://api.retellai.com/list-voices" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

**Success response:**
```json
[
  {
    "voice_id": "elevenlabs_voice_abc123",
    "voice_name": "Sarah",
    "provider": "elevenlabs",
    "accent": "American",
    "gender": "female",
    "age": "young",
    "preview_audio_url": "https://..."
  }
]
```

## Create Phone Call

Triggers an outbound test call.

```bash
curl -s -X POST "https://api.retellai.com/v2/create-phone-call" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+14155551234",
    "to_number": "+14155555678",
    "agent_id": "agent_abc123"
  }'
```

**Success response:**
```json
{
  "call_id": "call_abc123",
  "agent_id": "agent_abc123",
  "call_status": "registered",
  "start_timestamp": 1700000000
}
```

## Get Call

Retrieves call details and transcript.

```bash
curl -s -X GET "https://api.retellai.com/v2/get-call/call_abc123" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

**Success response:**
```json
{
  "call_id": "call_abc123",
  "agent_id": "agent_abc123",
  "call_status": "ended",
  "transcript": "Agent: Good morning... Caller: Hi...",
  "call_analysis": {
    "call_summary": "...",
    "custom_analysis_data": {}
  },
  "start_timestamp": 1700000000,
  "end_timestamp": 1700000120
}
```

## Common Error Responses

| Status | Meaning | Common Cause |
|--------|---------|--------------|
| 401 | Unauthorized | Invalid or missing API key |
| 404 | Not Found | Invalid agent_id or call_id |
| 422 | Unprocessable Entity | Invalid request body (missing required fields, wrong types) |
| 429 | Rate Limited | Too many requests. Wait and retry. |
| 500 | Internal Server Error | Retell platform issue. Retry after delay. |

## New Parameters (2025-2026)

### begin_message_delay_ms
Delay before agent speaks its first message after call connects. Creates natural "human picking up the phone" effect.
- Range: 0-5000ms
- Recommended: 400-500ms for inbound, 0 for outbound
- Default: 0

### enable_dynamic_voice_speed
Agent automatically adjusts speaking speed to match caller's pace.
- Values: true / false
- Recommended: true for most templates
- Exception: false for debt collection (consistent pace required)

### fallback_voice_ids
Array of backup voice IDs to use if primary TTS provider fails.
- Format: ["provider-voice-id", "provider-voice-id"]
- Always use voices from DIFFERENT providers than primary
- Example: `["openai-nova", "deepgram-luna"]`

### vocab_specialization
Optimizes speech recognition for specialized vocabulary.
- Values: "medical" (English only)
- Use for: medical intake, clinical scheduling, healthcare support

### pii_config
Configure post-call PII redaction from transcripts.
- Redacts: names, SSN, credit card numbers, phone numbers
- Cost: $0.01/min additional
- Format: `{"pii_redaction_plan": "strict"}` or `{"pii_redaction_plan": "standard"}`

### data_storage_setting
Control how much call data Retell retains.
- Values: "default", "basic_attributes_only", "no_storage"
- Use "basic_attributes_only" for privacy-sensitive deployments

## Simulation Testing API

Run batch conversation tests programmatically:

```bash
curl -X POST https://api.retellai.com/v2/run-simulation \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_abc123",
    "caller_persona": "objector",
    "num_simulations": 20,
    "success_criteria": {
      "outcome": "booked_appointment",
      "max_duration_ms": 180000
    }
  }'
```

## Agent Version Control API

Create a version snapshot before any update:
```bash
# Get current config (save as version backup)
curl -s "https://api.retellai.com/get-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  > "agent-v$(date +%Y%m%d-%H%M%S).json"

# Retell dashboard: Agent → Versions → One-click revert to any snapshot
```
