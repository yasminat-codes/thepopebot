# Config Schema Reference

Complete field reference for both configuration files produced by the
agent-config-builder.

---

## llm-config.json Schema

This file is the request body for `POST /create-retell-llm`.

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `start_speaker` | string | Yes | "agent" | Who speaks first: "agent" or "user" |
| `general_prompt` | string | No | — | System prompt for the LLM |
| `begin_message` | string | No | — | First message (only if start_speaker = "agent") |
| `model` | string | No | "gpt-4.1" | LLM model identifier |
| `model_temperature` | float | No | 0.4 | Response randomness (0 = deterministic) |
| `states` | array | No | — | Multi-step conversation flow |
| `general_tools` | array | No | — | Tools available across all states |
| `knowledge_base_ids` | string[] | No | — | Attached knowledge bases |
| `guardrail_config` | object | No | — | Topic restrictions |

### States Object

```json
{
  "name": "state_name",
  "prompt": "Instructions for this state...",
  "tools": [
    {"type": "end_call", "name": "end_call", "description": "When to end"}
  ],
  "edges": [
    {"description": "Condition", "destination_state_name": "other_state"}
  ]
}
```

### Guardrail Config Object

```json
{
  "output_topics": ["Only discuss relevant topics..."],
  "input_topics": ["Redirect off-topic requests..."]
}
```

### Example Complete llm-config.json

```json
{
  "start_speaker": "agent",
  "model": "gpt-4.1",
  "model_temperature": 0.4,
  "begin_message": "Hi, thanks for calling Acme Dental!",
  "states": [
    {
      "name": "greeting",
      "prompt": "Greet the caller warmly. Determine if they want to book or have a question.",
      "edges": [
        {"description": "Wants appointment", "destination_state_name": "booking"},
        {"description": "Has question", "destination_state_name": "faq"}
      ]
    },
    {
      "name": "booking",
      "prompt": "Collect: name, date, time, service type. Confirm each.",
      "tools": [{"type": "end_call", "name": "end_call", "description": "Booking complete"}]
    },
    {
      "name": "faq",
      "prompt": "Answer questions. Hours: Mon-Fri 9-5. Services: cleanings, fillings.",
      "tools": [{"type": "end_call", "name": "end_call", "description": "Question answered"}],
      "edges": [{"description": "Wants to book", "destination_state_name": "booking"}]
    }
  ],
  "guardrail_config": {
    "output_topics": ["Only dental services and scheduling."],
    "input_topics": ["Redirect non-dental queries politely."]
  }
}
```

---

## agent-config.json Schema

This file is the request body for `POST /create-agent`. The `response_engine` field
is injected at deployment time by the retell-api-wrapper.

### Voice Settings

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `voice_id` | string | — | — | **Required.** Voice identifier |
| `voice_model` | string | — | — | Voice model variant |
| `voice_temperature` | float | 1.0 | 0-2 | Voice randomness |
| `voice_speed` | float | 1.0 | 0.5-2 | Speech speed |
| `enable_dynamic_voice_speed` | bool | false | — | Auto-adjust speed |
| `volume` | float | 1.0 | 0-2 | Output volume |
| `voice_emotion` | string | — | calm/sympathetic/happy/sad/angry/fearful/surprised | Emotional tone |
| `fallback_voice_ids` | string[] | — | — | Backup voices |

### Interaction Settings

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `responsiveness` | float | 0.8 | 0-1 | Response speed |
| `interruption_sensitivity` | float | 0.7 | 0-1 | Interruption detection |
| `enable_backchannel` | bool | true | — | "Uh-huh" responses |
| `backchannel_frequency` | float | 0.5 | 0-1 | Backchannel rate |
| `backchannel_words` | string[] | — | — | Custom words |

### Environment Settings

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `ambient_sound` | string | — | coffee-shop/convention-hall/summer-outdoor/mountain-outdoor/static-noise/call-center | Background sound |
| `ambient_sound_volume` | float | — | 0-2 | Background volume |
| `denoising_mode` | string | noise-cancellation | no-denoise/noise-cancellation/noise-and-background-speech-cancellation | Input denoising |

### Speech Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `pronunciation_dictionary` | array | — | [{word, alphabet, phoneme}] |
| `normalize_for_speech` | bool | true | Normalize text for TTS |
| `boosted_keywords` | string[] | — | Keywords to boost in ASR |
| `language` | string | "en-US" | Language code or "multi" |

### Call Settings

| Field | Type | Default | Range | Description |
|-------|------|---------|-------|-------------|
| `end_call_after_silence_ms` | int | 30000 | 1000-600000 | End on silence (ms) |
| `max_call_duration_ms` | int | 900000 | 60000-7200000 | Max duration (ms) |

### Analytics Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `post_call_analysis_data` | array | — | [{name, type, description}] |
| `post_call_analysis_model` | string | — | Model for analysis |
| `data_storage_setting` | string | "everything" | Data retention policy |

### Webhook Settings

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `webhook_url` | string | — | URL for events |
| `webhook_events` | string[] | — | Event types to send |

### Example Complete agent-config.json

```json
{
  "voice_id": "11labs-Myra",
  "fallback_voice_ids": ["openai-alloy"],
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
    {"name": "appointment_booked", "type": "boolean", "description": "Was appointment booked?"}
  ],
  "data_storage_setting": "everything"
}
```
