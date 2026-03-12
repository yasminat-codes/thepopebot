# Calls API Reference

Complete reference for Retell AI Call endpoints. Calls can be initiated via phone
(outbound) or web browser, and call data can be retrieved after completion.

Base URL: `https://api.retellai.com`

---

## Create Phone Call

**POST** `/v2/create-phone-call`

Initiates an outbound phone call using a Retell agent.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `from_number` | string | Caller ID phone number (must be imported in Retell) |
| `to_number` | string | Destination phone number |
| `agent_id` | string | Agent to handle the call |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `metadata` | object | Custom key-value pairs attached to the call |
| `retell_llm_dynamic_variables` | object | Variables injected into the LLM prompt |

### Request Example

```bash
curl -s -X POST https://api.retellai.com/v2/create-phone-call \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+14155551234",
    "to_number": "+14155555678",
    "agent_id": "agent_7890xyz",
    "metadata": {
      "lead_id": "lead_001",
      "campaign": "feb_2026_outreach"
    },
    "retell_llm_dynamic_variables": {
      "customer_name": "Jane",
      "appointment_date": "March 3rd"
    }
  }'
```

### Response Example

```json
{
  "call_id": "call_abc123",
  "agent_id": "agent_7890xyz",
  "call_status": "registered",
  "from_number": "+14155551234",
  "to_number": "+14155555678"
}
```

---

## Create Web Call

**POST** `/v2/create-web-call`

Creates a browser-based call for testing or web integrations.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `agent_id` | string | Agent to handle the call |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `metadata` | object | Custom key-value pairs |
| `retell_llm_dynamic_variables` | object | Variables injected into prompt |

### Request Example

```bash
curl -s -X POST https://api.retellai.com/v2/create-web-call \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent_7890xyz",
    "metadata": {"test_run": "true"}
  }'
```

### Response Example

```json
{
  "call_id": "call_web_456",
  "web_call_link": "https://call.retellai.com/call_web_456",
  "agent_id": "agent_7890xyz",
  "call_status": "registered"
}
```

Open `web_call_link` in a browser to start the call.

---

## Get Call

**GET** `/v2/get-call/{call_id}`

Retrieves full details of a call including transcript and analysis.

```bash
curl -s "https://api.retellai.com/v2/get-call/call_abc123" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

### Response Example

```json
{
  "call_id": "call_abc123",
  "agent_id": "agent_7890xyz",
  "call_status": "ended",
  "start_timestamp": 1708790400000,
  "end_timestamp": 1708790520000,
  "duration_ms": 120000,
  "transcript": "Agent: Hi there! Thanks for calling... User: I need to book...",
  "call_analysis": {
    "call_summary": "Customer booked a dental cleaning for March 3rd.",
    "user_sentiment": "positive"
  },
  "metadata": {"lead_id": "lead_001"}
}
```

---

## List Calls

**GET** `/v2/list-calls`

Returns calls matching the specified filters.

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_id` | string | Filter by agent |
| `after_start` | int | Calls starting after this Unix timestamp (ms) |
| `before_start` | int | Calls starting before this Unix timestamp (ms) |
| `sort_order` | string | "ascending" or "descending" |
| `limit` | int | Max number of results |

### Request Example

```bash
# List last 20 calls for an agent
curl -s "https://api.retellai.com/v2/list-calls?agent_id=agent_7890xyz&sort_order=descending&limit=20" \
  -H "Authorization: Bearer $RETELL_API_KEY"

# List calls from a specific date range
curl -s "https://api.retellai.com/v2/list-calls?after_start=1708700000000&before_start=1708800000000" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

### Response Example

```json
[
  {
    "call_id": "call_abc123",
    "agent_id": "agent_7890xyz",
    "call_status": "ended",
    "duration_ms": 120000,
    "start_timestamp": 1708790400000
  },
  {
    "call_id": "call_def456",
    "agent_id": "agent_7890xyz",
    "call_status": "ended",
    "duration_ms": 85000,
    "start_timestamp": 1708780000000
  }
]
```

---

## Error Handling

| Status | Cause | Resolution |
|--------|-------|------------|
| 400 | Missing required field or invalid phone number format | Check `from_number`, `to_number`, `agent_id` |
| 401 | Invalid API key | Verify `RETELL_API_KEY` |
| 422 | Agent not found or phone number not imported | Verify `agent_id` exists, verify `from_number` is imported |
| 500 | Server error | Retry with backoff |
