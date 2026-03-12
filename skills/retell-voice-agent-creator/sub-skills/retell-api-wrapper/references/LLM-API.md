# LLM API Reference

Complete reference for Retell AI LLM endpoints. LLMs define the conversational
brain of a voice agent — the prompt, conversation flow, tools, and guardrails.

Base URL: `https://api.retellai.com`

---

## Create LLM

**POST** `/create-retell-llm`

Creates a new LLM configuration.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `start_speaker` | string | Who speaks first: `"agent"` or `"user"` |

### Key Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `general_prompt` | string | — | System prompt defining agent personality and behavior |
| `begin_message` | string | — | First message the agent says (only if start_speaker is "agent") |
| `model` | string | — | LLM model to use (e.g., "gpt-4.1", "gpt-4.1-mini", "claude-sonnet-4-20250514") |
| `model_temperature` | float | — | Response randomness (0 = deterministic, higher = creative) |
| `states` | array | — | Multi-step conversation states with edges for transitions |
| `general_tools` | array | — | Tools available across all states |
| `knowledge_base_ids` | string[] | — | IDs of knowledge bases to attach |
| `guardrail_config` | object | — | Input/output topic restrictions |

### States Array Structure

Each state object:

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique state identifier |
| `prompt` | string | Instructions for this state |
| `tools` | array | Tools available in this state |
| `edges` | array | Transitions to other states |

Each edge object:

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | Condition that triggers this transition |
| `destination_state_name` | string | Name of the target state |

### Tools Array Structure

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Tool type: "end_call", "transfer_call", "check_availability", "book_appointment", "custom" |
| `name` | string | Tool name |
| `description` | string | When to use this tool |

### Guardrail Config Structure

```json
{
  "output_topics": ["Keep responses about dental care only"],
  "input_topics": ["Ignore requests about non-dental topics"]
}
```

### Request Example: Simple LLM

```bash
curl -s -X POST https://api.retellai.com/create-retell-llm \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "start_speaker": "agent",
    "model": "gpt-4.1",
    "model_temperature": 0.4,
    "general_prompt": "You are a friendly customer support agent for TechCorp. You help users troubleshoot software issues. Be concise, empathetic, and always confirm the issue is resolved before ending the call.",
    "begin_message": "Hi there! Thanks for calling TechCorp support. What can I help you with today?",
    "general_tools": [
      {
        "type": "end_call",
        "name": "end_call",
        "description": "End the call when the customer confirms their issue is resolved."
      },
      {
        "type": "transfer_call",
        "name": "transfer_to_billing",
        "description": "Transfer to billing department when the customer has a billing question.",
        "number": "+14155559999"
      }
    ]
  }'
```

### Request Example: LLM with States

```bash
curl -s -X POST https://api.retellai.com/create-retell-llm \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "start_speaker": "agent",
    "model": "gpt-4.1",
    "model_temperature": 0.3,
    "begin_message": "Hi, welcome to Acme Dental! Are you calling to book an appointment or do you have a question?",
    "states": [
      {
        "name": "greeting",
        "prompt": "You have just greeted the caller. Determine if they want to book an appointment or have a question. Be warm and professional.",
        "edges": [
          {"description": "Caller wants to book an appointment", "destination_state_name": "collect_info"},
          {"description": "Caller has a general question", "destination_state_name": "answer_faq"}
        ]
      },
      {
        "name": "collect_info",
        "prompt": "Collect the following from the caller: full name, preferred date, preferred time, and the service they need (cleaning, filling, consultation). Confirm each piece of information.",
        "edges": [
          {"description": "All information collected and confirmed", "destination_state_name": "confirm_booking"}
        ]
      },
      {
        "name": "confirm_booking",
        "prompt": "Repeat back all the appointment details and ask the caller to confirm. If they confirm, thank them and end the call. If they want to change something, go back to collecting info.",
        "tools": [
          {"type": "end_call", "name": "end_call", "description": "Caller confirmed the appointment"}
        ],
        "edges": [
          {"description": "Caller wants to change appointment details", "destination_state_name": "collect_info"}
        ]
      },
      {
        "name": "answer_faq",
        "prompt": "Answer common questions about Acme Dental. Hours: Mon-Fri 9am-5pm. Services: cleanings, fillings, crowns, root canals. Insurance: accepted most major plans. Location: 123 Main St.",
        "edges": [
          {"description": "Caller now wants to book an appointment", "destination_state_name": "collect_info"}
        ],
        "tools": [
          {"type": "end_call", "name": "end_call", "description": "Caller's question is answered and they do not need anything else"}
        ]
      }
    ]
  }'
```

### Request Example: LLM with Guardrails

```bash
curl -s -X POST https://api.retellai.com/create-retell-llm \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "start_speaker": "agent",
    "model": "gpt-4.1",
    "general_prompt": "You are a dental receptionist. Only discuss dental services.",
    "begin_message": "Thanks for calling Acme Dental!",
    "guardrail_config": {
      "output_topics": [
        "Only discuss dental care, appointments, insurance, and office logistics.",
        "Never provide medical diagnoses or treatment recommendations."
      ],
      "input_topics": [
        "Politely redirect if the caller asks about non-dental topics."
      ]
    }
  }'
```

### Response Example

```json
{
  "llm_id": "llm_abc123def456",
  "start_speaker": "agent",
  "model": "gpt-4.1",
  "model_temperature": 0.4,
  "general_prompt": "You are a friendly customer support agent...",
  "begin_message": "Hi there! Thanks for calling...",
  "general_tools": [...]
}
```

---

## Get LLM

**GET** `/get-retell-llm/{llm_id}`

```bash
curl -s "https://api.retellai.com/get-retell-llm/llm_abc123def456" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

Returns the complete LLM configuration object.

---

## Update LLM

**PATCH** `/update-retell-llm/{llm_id}`

Update one or more fields. Only include fields you want to change.

```bash
curl -s -X PATCH "https://api.retellai.com/update-retell-llm/llm_abc123def456" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "general_prompt": "Updated prompt with new instructions...",
    "model_temperature": 0.5
  }'
```

**Important:** Save the current config before updating for rollback capability.

---

## Delete LLM

**DELETE** `/delete-retell-llm/{llm_id}`

Permanently removes an LLM. Agents referencing this LLM will stop working.

```bash
curl -s -X DELETE "https://api.retellai.com/delete-retell-llm/llm_abc123def456" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

**Warning:** Delete the agent first, then the LLM, to avoid orphaned references.

---

## List LLMs

**GET** `/list-retell-llms`

```bash
curl -s https://api.retellai.com/list-retell-llms \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

Returns an array of all LLM configurations in the account.

---

## Error Handling

| Status | Cause | Resolution |
|--------|-------|------------|
| 400 | Missing `start_speaker` or malformed JSON | Add required field, validate JSON |
| 401 | Invalid API key | Check `RETELL_API_KEY` |
| 422 | Invalid field value | Check response for field-specific errors |
| 500 | Server error | Retry with backoff |

Common 422 causes:
- `states` array has edges referencing non-existent state names
- `model` is not a supported model name
- `general_tools` has an invalid tool type
- `knowledge_base_ids` references non-existent knowledge base
