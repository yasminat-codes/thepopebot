# Agents API Reference

Complete reference for Retell AI Agent endpoints. Agents are the top-level deployable
resource that combine a voice, an LLM, and behavioral settings.

Base URL: `https://api.retellai.com`

---

## Create Agent

**POST** `/create-agent`

Creates a new voice agent.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `response_engine` | object | Must contain `type` ("retell-llm") and `llm_id` |
| `voice_id` | string | Voice identifier from `/list-voices` |

### Optional Fields

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `agent_name` | string | — | — | Display name for the agent |
| `voice_model` | string | — | — | Voice model variant |
| `voice_temperature` | float | 1 | 0-2 | Voice randomness |
| `voice_speed` | float | 1 | 0.5-2 | Speech speed multiplier |
| `enable_dynamic_voice_speed` | bool | false | — | Auto-adjust speed |
| `volume` | float | 1 | 0-2 | Output volume |
| `voice_emotion` | string | — | calm/sympathetic/happy/sad/angry/fearful/surprised | Emotional tone |
| `responsiveness` | float | 1 | 0-1 | How quickly agent responds |
| `interruption_sensitivity` | float | 1 | 0-1 | Sensitivity to interruptions |
| `enable_backchannel` | bool | false | — | Enable "uh-huh", "I see" |
| `backchannel_frequency` | float | — | 0-1 | How often to backchannel |
| `backchannel_words` | string[] | — | — | Custom backchannel words |
| `ambient_sound` | string | — | coffee-shop/convention-hall/summer-outdoor/mountain-outdoor/static-noise/call-center | Background sound |
| `ambient_sound_volume` | float | — | 0-2 | Background sound volume |
| `language` | string | "en-US" | — | Language code or "multi" |
| `webhook_url` | string | — | — | URL for event webhooks |
| `webhook_events` | string[] | — | — | Which events to send |
| `pronunciation_dictionary` | array | — | — | [{word, alphabet, phoneme}] |
| `normalize_for_speech` | bool | — | — | Normalize text for TTS |
| `denoising_mode` | string | — | no-denoise/noise-cancellation/noise-and-background-speech-cancellation | Input denoising |
| `end_call_after_silence_ms` | int | 600000 | — | End call after silence (ms) |
| `max_call_duration_ms` | int | — | 60000-7200000 | Max call length (ms) |
| `post_call_analysis_data` | array | — | — | [{name, type, description}] |
| `post_call_analysis_model` | string | — | — | Model for analysis |
| `fallback_voice_ids` | string[] | — | — | Backup voice IDs |
| `boosted_keywords` | string[] | — | — | Keywords to boost in ASR |
| `data_storage_setting` | string | — | everything/everything_except_pii/basic_attributes_only | Data retention |

### Request Example

```bash
curl -s -X POST https://api.retellai.com/create-agent \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "response_engine": {
      "type": "retell-llm",
      "llm_id": "llm_abc123def456"
    },
    "voice_id": "11labs-Adrian",
    "agent_name": "Customer Support Agent",
    "voice_temperature": 1.0,
    "voice_speed": 1.0,
    "responsiveness": 0.8,
    "interruption_sensitivity": 0.7,
    "enable_backchannel": true,
    "backchannel_frequency": 0.5,
    "language": "en-US",
    "ambient_sound": "coffee-shop",
    "ambient_sound_volume": 0.3,
    "end_call_after_silence_ms": 30000,
    "max_call_duration_ms": 900000,
    "post_call_analysis_data": [
      {"name": "call_summary", "type": "string", "description": "Summarize the call in 2-3 sentences."},
      {"name": "user_sentiment", "type": "enum", "description": "Caller sentiment: positive, neutral, negative."}
    ]
  }'
```

### Response Example

```json
{
  "agent_id": "agent_7890xyz",
  "response_engine": {"type": "retell-llm", "llm_id": "llm_abc123def456"},
  "voice_id": "11labs-Adrian",
  "agent_name": "Customer Support Agent",
  "voice_temperature": 1.0,
  "voice_speed": 1.0,
  "responsiveness": 0.8,
  "interruption_sensitivity": 0.7,
  "enable_backchannel": true,
  "language": "en-US"
}
```

---

## Get Agent

**GET** `/get-agent/{agent_id}`

Retrieve the full configuration of an existing agent.

```bash
curl -s "https://api.retellai.com/get-agent/agent_7890xyz" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

Returns the complete agent object with all fields.

---

## Update Agent

**PATCH** `/update-agent/{agent_id}`

Update one or more fields on an existing agent. Only include the fields you want
to change. Omitted fields remain unchanged.

```bash
curl -s -X PATCH "https://api.retellai.com/update-agent/agent_7890xyz" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "voice_speed": 1.1,
    "responsiveness": 0.9,
    "agent_name": "Customer Support Agent v2"
  }'
```

Returns the updated agent object.

**Important:** Every PATCH creates a new version of the agent internally. Save the
current config before updating if you want rollback capability.

---

## Delete Agent

**DELETE** `/delete-agent/{agent_id}`

Permanently removes an agent. This cannot be undone.

```bash
curl -s -X DELETE "https://api.retellai.com/delete-agent/agent_7890xyz" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

Returns empty body with 200 on success.

---

## List Agents

**GET** `/list-agents`

Returns an array of all agents in the account.

```bash
curl -s https://api.retellai.com/list-agents \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

### Response Example

```json
[
  {
    "agent_id": "agent_7890xyz",
    "agent_name": "Customer Support Agent",
    "voice_id": "11labs-Adrian",
    "response_engine": {"type": "retell-llm", "llm_id": "llm_abc123def456"},
    "language": "en-US"
  },
  {
    "agent_id": "agent_0001abc",
    "agent_name": "Sales Agent",
    "voice_id": "11labs-Myra",
    "response_engine": {"type": "retell-llm", "llm_id": "llm_def789ghi012"},
    "language": "en-US"
  }
]
```

---

## Error Handling

| Status | Cause | Resolution |
|--------|-------|------------|
| 400 | Malformed JSON or missing required field | Validate JSON body, ensure `response_engine` and `voice_id` are present |
| 401 | Invalid API key | Verify `RETELL_API_KEY` is correct |
| 422 | Field validation error | Check response body for field-specific error messages |
| 500 | Server error | Retry with exponential backoff (2s, 4s, 8s) |

Common 422 causes for agent endpoints:
- `voice_id` does not match any known voice
- `voice_temperature` outside 0-2 range
- `responsiveness` outside 0-1 range
- `response_engine.type` is not `"retell-llm"`
- `response_engine.llm_id` does not exist
