---
name: retell-api-wrapper
description: Complete Retell AI API wrapper covering agents, LLMs, calls, and voices. Handles authentication, deployment, versioning, rollback, webhooks, and Twilio integration. Supports multi-account deployment (internal and client accounts). Use when user says "deploy agent", "create agent via API", "list agents", "delete agent", "make a test call", "list voices", "set up webhook", "connect Twilio", "roll back agent", or any direct Retell API operation.
allowed-tools: Read Write Bash(curl:*) Bash(jq:*) Bash(chmod:*)
---

## Overview

This sub-skill provides complete coverage of the Retell AI REST API. It wraps every
endpoint (agents, LLMs, calls, voices) behind validated shell functions with proper
authentication, error handling, and retry logic.

All requests target `https://api.retellai.com` using Bearer token authentication.
The wrapper supports two deployment modes:

- **Internal mode** — uses `RETELL_API_KEY` from environment for your own account.
- **Client mode** — accepts an explicit `--api-key` flag so you can deploy agents
  into a client's Retell account without touching your own.

Every function validates inputs before making the request, checks HTTP status codes,
and returns clean JSON. Failed requests are retried up to 3 times with exponential
backoff.

For full deployment workflows see [deploy-agent.sh](scripts/deploy-agent.sh). For
individual endpoint details see the references directory.

## Quick Start

Deploy a complete agent in three commands:

```bash
# 1. Source the wrapper
source /path/to/retell-api.sh

# 2. Create LLM with prompt
LLM_RESPONSE=$(retell_create_llm '{
  "start_speaker": "agent",
  "general_prompt": "You are a helpful appointment-booking assistant for Acme Dental.",
  "begin_message": "Hi, thanks for calling Acme Dental. How can I help you today?",
  "model": "gpt-4.1"
}')
LLM_ID=$(echo "$LLM_RESPONSE" | jq -r '.llm_id')

# 3. Create agent with the LLM and a voice
AGENT_RESPONSE=$(retell_create_agent "{
  \"response_engine\": {\"type\": \"retell-llm\", \"llm_id\": \"$LLM_ID\"},
  \"voice_id\": \"11labs-Adrian\",
  \"agent_name\": \"Acme Dental Receptionist\"
}")
AGENT_ID=$(echo "$AGENT_RESPONSE" | jq -r '.agent_id')

echo "Deployed: agent=$AGENT_ID  llm=$LLM_ID"
```

For a scripted version with validation and retry see
[deploy-agent.sh](scripts/deploy-agent.sh).

## Prerequisites

| Requirement | Details |
|-------------|---------|
| `RETELL_API_KEY` | **Required.** Your Retell AI API key. Get it from the Retell dashboard under Settings > API Keys. |
| `RETELL_CLIENT_API_KEY` | Optional. A client's API key for multi-account deploys. Pass via `--api-key` flag. |
| `curl` | Must be installed. Used for all HTTP requests. |
| `jq` | Must be installed. Used for JSON parsing and validation. |
| `bash` 4+ | Scripts use associative arrays and `set -euo pipefail`. |

Store API keys in environment variables or in your `.env` file. Never hard-code keys
into scripts or config files that get committed to version control.

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `api_key` | string | Yes (env or flag) | Retell API key for authentication |
| `operation` | string | Yes | One of: create, update, delete, list, get |
| `resource` | string | Yes | One of: agent, llm, call, voice |
| `config_body` | JSON string | For create/update | Request body matching Retell API schema |
| `agent_id` | string | For get/update/delete agent | Target agent identifier |
| `llm_id` | string | For get/update/delete LLM | Target LLM identifier |
| `call_id` | string | For get call | Target call identifier |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `agent_id` | string | Identifier of created/updated agent |
| `llm_id` | string | Identifier of created/updated LLM |
| `call_id` | string | Identifier of created call |
| `api_response` | JSON | Full API response body |
| `http_status` | integer | HTTP status code from the request |
| `error_message` | string | Human-readable error if request failed |

## API Endpoint Index

| Endpoint | Method | Purpose | Reference |
|----------|--------|---------|-----------|
| `/create-agent` | POST | Create a new voice agent | [AGENTS-API.md](references/AGENTS-API.md) |
| `/get-agent/{agent_id}` | GET | Retrieve agent configuration | [AGENTS-API.md](references/AGENTS-API.md) |
| `/update-agent/{agent_id}` | PATCH | Update agent fields | [AGENTS-API.md](references/AGENTS-API.md) |
| `/delete-agent/{agent_id}` | DELETE | Remove an agent | [AGENTS-API.md](references/AGENTS-API.md) |
| `/list-agents` | GET | List all agents in account | [AGENTS-API.md](references/AGENTS-API.md) |
| `/create-retell-llm` | POST | Create a new LLM config | [LLM-API.md](references/LLM-API.md) |
| `/get-retell-llm/{llm_id}` | GET | Retrieve LLM configuration | [LLM-API.md](references/LLM-API.md) |
| `/update-retell-llm/{llm_id}` | PATCH | Update LLM fields | [LLM-API.md](references/LLM-API.md) |
| `/delete-retell-llm/{llm_id}` | DELETE | Remove an LLM | [LLM-API.md](references/LLM-API.md) |
| `/list-retell-llms` | GET | List all LLMs in account | [LLM-API.md](references/LLM-API.md) |
| `/v2/create-phone-call` | POST | Start outbound phone call | [CALLS-API.md](references/CALLS-API.md) |
| `/v2/create-web-call` | POST | Start browser-based call | [CALLS-API.md](references/CALLS-API.md) |
| `/v2/get-call/{call_id}` | GET | Get call details + transcript | [CALLS-API.md](references/CALLS-API.md) |
| `/v2/list-calls` | GET | List calls with filters | [CALLS-API.md](references/CALLS-API.md) |
| `/list-voices` | GET | List all available voices | [VOICES-API.md](references/VOICES-API.md) |

## Phase 1: Authentication

Before any API call, verify that a valid API key is available.

**Steps:**

1. Check for `RETELL_API_KEY` in environment. If missing and no `--api-key` flag
   was passed, abort with a clear error message.
2. If `--api-key` flag is present, use that value instead (client mode).
3. Test authentication by calling `GET /list-agents`. If 401 is returned, the key
   is invalid.

**Auth header format:**
```
Authorization: Bearer <api_key>
```

**Testing authentication:**
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  https://api.retellai.com/list-agents
```

A `200` response confirms the key is valid. A `401` means the key is wrong or
expired. See [AUTHENTICATION.md](references/AUTHENTICATION.md) for security best
practices and multi-account key management.

## Phase 2: Agent Operations

Agents are the top-level resource in Retell. Each agent combines a voice, an LLM,
and behavioral configuration into a deployable unit.

### Create Agent

Required fields: `response_engine` (object with `type` and `llm_id`), `voice_id`.

```bash
curl -s -X POST https://api.retellai.com/create-agent \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "response_engine": {
      "type": "retell-llm",
      "llm_id": "llm_abc123"
    },
    "voice_id": "11labs-Adrian",
    "agent_name": "Sales Agent v1",
    "language": "en-US",
    "voice_temperature": 1,
    "voice_speed": 1,
    "responsiveness": 0.8,
    "interruption_sensitivity": 0.7,
    "enable_backchannel": true,
    "backchannel_frequency": 0.5,
    "ambient_sound": "coffee-shop",
    "ambient_sound_volume": 0.3
  }'
```

Response includes `agent_id` — save this for all subsequent operations.

### Update Agent

PATCH with only the fields you want to change:

```bash
curl -s -X PATCH "https://api.retellai.com/update-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"voice_speed": 1.1, "responsiveness": 0.9}'
```

### Delete Agent

```bash
curl -s -X DELETE "https://api.retellai.com/delete-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

### List Agents

```bash
curl -s https://api.retellai.com/list-agents \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

### Get Agent

```bash
curl -s "https://api.retellai.com/get-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

Full field reference: [AGENTS-API.md](references/AGENTS-API.md)

## Phase 3: LLM Operations

LLMs define what the agent says — the prompt, conversation flow, tools, and
guardrails. Every agent must reference exactly one LLM via `response_engine.llm_id`.

### Create LLM

Required: `start_speaker`. Recommended: `general_prompt`, `begin_message`, `model`.

```bash
curl -s -X POST https://api.retellai.com/create-retell-llm \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "start_speaker": "agent",
    "model": "gpt-4.1",
    "model_temperature": 0.4,
    "general_prompt": "You are a friendly receptionist for Acme Dental...",
    "begin_message": "Hi, thanks for calling Acme Dental. How can I help?",
    "general_tools": [
      {
        "type": "end_call",
        "name": "end_call",
        "description": "End the call when the conversation is complete"
      }
    ]
  }'
```

### Create LLM with States

States allow multi-step conversation flows. Add a `states` array with `name`, `prompt`,
`edges` (transitions), and optional `tools` per state. See [LLM-API.md](references/LLM-API.md)
for full state schema and examples.

### Update LLM

```bash
curl -s -X PATCH "https://api.retellai.com/update-retell-llm/$LLM_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"general_prompt": "Updated prompt text here..."}'
```

### Delete LLM

```bash
curl -s -X DELETE "https://api.retellai.com/delete-retell-llm/$LLM_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

### List LLMs

```bash
curl -s https://api.retellai.com/list-retell-llms \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

Full field reference: [LLM-API.md](references/LLM-API.md)

## Phase 4: Call Operations

Once an agent is deployed, you can initiate calls or retrieve call data.

### Create Outbound Phone Call

```bash
curl -s -X POST https://api.retellai.com/v2/create-phone-call \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+14155551234",
    "to_number": "+14155555678",
    "agent_id": "agent_abc123"
  }'
```

### Create Web Call (for browser testing)

```bash
curl -s -X POST https://api.retellai.com/v2/create-web-call \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "agent_abc123"}'
```

Returns `call_id` and `web_call_link` for browser-based testing.

### Get Call Details

```bash
curl -s "https://api.retellai.com/v2/get-call/$CALL_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

Returns full transcript, duration, call status, and post-call analysis results.

### List Calls

```bash
curl -s "https://api.retellai.com/v2/list-calls?agent_id=$AGENT_ID&sort_order=descending&limit=10" \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

Full reference: [CALLS-API.md](references/CALLS-API.md)

## Phase 5: Voice Operations

Retell offers voices from multiple providers. List and filter to find the right one.

### List All Voices

```bash
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY"
```

### Filter Voices

The API returns all voices in one call. Filter client-side with `jq`:

```bash
# Female voices from ElevenLabs
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  | jq '[.[] | select(.provider == "elevenlabs" and .gender == "female")]'

# Voices with American accent
curl -s https://api.retellai.com/list-voices \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  | jq '[.[] | select(.accent == "American")]'
```

Full reference: [VOICES-API.md](references/VOICES-API.md)

## Deployment Workflow

A complete deployment follows this sequence. The
[deploy-agent.sh](scripts/deploy-agent.sh) script automates all of these steps.

**Step 1: Validate Configuration**
- Read `llm-config.json` and `agent-config.json`
- Verify required fields are present
- Verify value ranges (temperatures, speeds, sensitivities)

**Step 2: Create LLM**
- POST to `/create-retell-llm` with contents of `llm-config.json`
- Capture `llm_id` from response
- Verify LLM exists with `GET /get-retell-llm/{llm_id}`

**Step 3: Create Agent**
- Inject `llm_id` into `agent-config.json` under `response_engine`
- POST to `/create-agent`
- Capture `agent_id` from response

**Step 4: Verify Agent**
- GET `/get-agent/{agent_id}` and confirm all fields match config
- If verification fails, retry up to 3 times

**Step 5: Output Results**
- Print `agent_id`, `llm_id`, dashboard URL
- Save deployment receipt to `deployment-receipt.json`

**Multi-Account Deployment:**
Pass `--api-key <client_key>` to deploy into a client's account:
```bash
./deploy-agent.sh --api-key "$CLIENT_API_KEY" \
  --llm-config llm-config.json \
  --agent-config agent-config.json
```

## Agent Versioning and Rollback

Retell automatically creates a new version every time you PATCH an agent or LLM.
There is no explicit version API, so version management is done client-side.

### Tracking Versions

Before any update, save the current configuration:

```bash
# Save current agent config before updating
curl -s "https://api.retellai.com/get-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  > "agent-backup-$(date +%Y%m%d-%H%M%S).json"
```

### Rolling Back

To roll back, PATCH with the saved configuration:

```bash
# Restore previous config
BACKUP=$(cat agent-backup-20260224-143000.json)
curl -s -X PATCH "https://api.retellai.com/update-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$BACKUP"
```

Name agents with version suffixes during A/B testing: `Sales Agent v1`, `v2`, `v1-rollback`.
Full guide: [VERSIONING-ROLLBACK.md](references/VERSIONING-ROLLBACK.md)

## Webhook Configuration

Configure webhooks to receive real-time events from your agent's calls.

### Setting Up Webhooks

Set `webhook_url` and `webhook_events` when creating or updating an agent:

```bash
curl -s -X PATCH "https://api.retellai.com/update-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://your-server.com/retell-webhook",
    "webhook_events": ["call_started", "call_ended", "call_analyzed"]
  }'
```

### Available Events

| Event | Fires When |
|-------|-----------|
| `call_started` | A call begins |
| `call_ended` | A call terminates |
| `call_analyzed` | Post-call analysis completes |
| `transcript_updated` | New transcript segment available |
| `transfer_started` | Call transfer initiated |
| `transfer_bridged` | Transfer connected |
| `transfer_cancelled` | Transfer was cancelled |
| `transfer_ended` | Transfer completed |

Full guide: [WEBHOOKS-GUIDE.md](references/WEBHOOKS-GUIDE.md)

## Twilio Integration

Connect a Retell agent to a Twilio phone number for inbound and outbound calling.

### Setup Steps

1. **Get a Twilio phone number** — Purchase from Twilio console or via API.
2. **Import to Retell** — Add the phone number in Retell dashboard under
   Phone Numbers, or use the API (phone number import endpoint).
3. **Assign agent** — Link the phone number to your agent. Inbound calls to that
   number will be handled by the agent.

### Outbound Calls via Twilio

Once a Twilio number is imported and assigned, use it as `from_number`:

```bash
curl -s -X POST https://api.retellai.com/v2/create-phone-call \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+14155551234",
    "to_number": "+14155555678",
    "agent_id": "agent_abc123"
  }'
```

Full guide: [TWILIO-INTEGRATION.md](references/TWILIO-INTEGRATION.md)

## Error Handling

All API errors return a JSON body with details. The wrapper scripts handle these
automatically, but here is the reference for manual troubleshooting.

### Error Code Reference

| Code | Meaning | Common Cause | Fix |
|------|---------|-------------|-----|
| 400 | Bad Request | Malformed JSON body or missing required field | Validate JSON syntax and required fields |
| 401 | Unauthorized | Invalid or expired API key | Check `RETELL_API_KEY` value |
| 422 | Unprocessable | Field validation failed | Check response body for specific field errors |
| 500 | Server Error | Retell internal issue | Retry with exponential backoff |

### Retry Strategy

For 500 errors and network failures, retry up to 3 times:

| Attempt | Delay |
|---------|-------|
| 1 | 2 seconds |
| 2 | 4 seconds |
| 3 | 8 seconds |

After 3 failures, save the request body locally and report the error.

Common 422 errors: out-of-range values (`voice_temperature` 0-2, `responsiveness` 0-1,
`voice_speed` 0.5-2), invalid `response_engine.type`, unknown `voice_id`, missing
`start_speaker`. Full reference: [ERROR-HANDLING.md](references/ERROR-HANDLING.md)

## Multi-Account Guide

Two modes: **Internal** (`RETELL_API_KEY` env var) and **Client** (`--api-key` flag).
All wrapper functions accept `--api-key` to deploy into a client's account.
Security: never store client keys in version control, pass via env or CLI only,
don't mix keys in one session. See parent [MULTI-ACCOUNT-GUIDE.md](../../references/MULTI-ACCOUNT-GUIDE.md).

## Real-World Scenarios

### Scenario 1: Full Agent Deployment

A dental office needs a new appointment-booking agent.

1. **Create LLM** with appointment-booking prompt, states for greeting / booking /
   FAQ, and an end_call tool.
2. **Create Agent** with the LLM, a friendly female voice (`11labs-Myra`),
   `responsiveness: 0.8`, `enable_backchannel: true`, and coffee-shop ambient sound.
3. **Set up webhook** to `https://dental-crm.com/retell-webhook` for `call_ended`
   and `call_analyzed` events.
4. **Import Twilio number** and assign the agent for inbound calls.
5. **Make a test call** using `create-web-call` to verify behavior.
6. **Review transcript** via `get-call` to confirm quality.

```bash
source retell-api.sh
LLM=$(retell_create_llm "$(cat llm-config.json)")
LLM_ID=$(echo "$LLM" | jq -r '.llm_id')
AGENT_CONFIG=$(cat agent-config.json | jq --arg id "$LLM_ID" \
  '.response_engine.llm_id = $id')
AGENT=$(retell_create_agent "$AGENT_CONFIG")
AGENT_ID=$(echo "$AGENT" | jq -r '.agent_id')
echo "Deployed: $AGENT_ID"
```

### Scenario 2: Rollback After Bad Update

An agent update caused poor call quality. Roll back immediately.

1. **Identify the backup** — find the most recent `agent-backup-*.json` file.
2. **Rollback agent** — PATCH with the backup config.
3. **Verify** — GET the agent and confirm config matches backup.
4. **Check calls** — List recent calls to confirm quality restored.

```bash
BACKUP=$(ls -t agent-backup-*.json | head -1)
curl -s -X PATCH "https://api.retellai.com/update-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$(cat $BACKUP)"
echo "Rolled back to $BACKUP"
```

## Decision Trees

**Which endpoint do I need?**

```
Want to change what the agent SAYS? --> LLM endpoints
  - Prompt, begin message, states, tools, guardrails --> PATCH /update-retell-llm/{llm_id}

Want to change how the agent SOUNDS? --> Agent endpoints
  - Voice, speed, temperature, backchannel --> PATCH /update-agent/{agent_id}

Want to test the agent? --> Call endpoints
  - Browser test --> POST /v2/create-web-call
  - Phone test --> POST /v2/create-phone-call

Want to find a voice? --> Voice endpoints
  - Browse voices --> GET /list-voices
```

**Create or Update?**

```
Agent exists? --No--> POST /create-agent
              --Yes-> Need to change fields? --Yes--> PATCH /update-agent/{agent_id}
                                              --No--> No action needed
```

## Resource Reference Map

| Resource | Reference File | Script |
|----------|---------------|--------|
| Agent CRUD | [AGENTS-API.md](references/AGENTS-API.md) | [retell-api.sh](scripts/retell-api.sh) |
| LLM CRUD | [LLM-API.md](references/LLM-API.md) | [retell-api.sh](scripts/retell-api.sh) |
| Calls | [CALLS-API.md](references/CALLS-API.md) | [retell-api.sh](scripts/retell-api.sh) |
| Voices | [VOICES-API.md](references/VOICES-API.md) | [retell-api.sh](scripts/retell-api.sh) |
| Authentication | [AUTHENTICATION.md](references/AUTHENTICATION.md) | [retell-api.sh](scripts/retell-api.sh) |
| Error Handling | [ERROR-HANDLING.md](references/ERROR-HANDLING.md) | [retell-api.sh](scripts/retell-api.sh) |
| Webhooks | [WEBHOOKS-GUIDE.md](references/WEBHOOKS-GUIDE.md) | [retell-api.sh](scripts/retell-api.sh) |
| Twilio | [TWILIO-INTEGRATION.md](references/TWILIO-INTEGRATION.md) | [deploy-agent.sh](scripts/deploy-agent.sh) |
| Versioning | [VERSIONING-ROLLBACK.md](references/VERSIONING-ROLLBACK.md) | [retell-api.sh](scripts/retell-api.sh) |
