# Environment Variables Reference

All environment variables used by the Retell AI Voice Agent Creator skill.

## Required Variables

### RETELL_API_KEY

| Field | Value |
|-------|-------|
| Required | Yes (for any deployment or API operation) |
| Description | Primary API key for authenticating against the Retell AI REST API. Used for creating agents, LLMs, triggering calls, and all other API operations. |
| Where to get | Retell AI Dashboard -> Settings -> API Keys -> Copy your API key |
| URL | https://dashboard.retellai.com/ |
| Format | Starts with `key_` followed by alphanumeric string |
| Example | `key_abc123def456ghi789` |
| Used by | retell-api-wrapper, deploy.sh, test-agent.sh, verify.sh |

## Optional Variables

### RETELL_CLIENT_API_KEY

| Field | Value |
|-------|-------|
| Required | No (only for client-mode deployments) |
| Description | A client's Retell API key, used when deploying agents to a client's account instead of your own. This key is ephemeral — it should be provided at runtime and never persisted to disk. |
| Where to get | Client provides it from their Retell AI Dashboard |
| Format | Same as RETELL_API_KEY: starts with `key_` |
| Example | `key_client_xyz789abc123` |
| Used by | retell-api-wrapper (when --client flag is set), deploy.sh (when --api-key flag is used) |
| Security note | Never write this to .env files. Hold in memory only. |

### ELEVENLABS_API_KEY

| Field | Value |
|-------|-------|
| Required | No (only for ElevenLabs voice cloning and custom voices) |
| Description | API key for ElevenLabs. Required if the user wants to use ElevenLabs voices, clone a voice, or use ElevenLabs pronunciation dictionaries. Not needed for other voice providers (OpenAI, Deepgram, Cartesia). |
| Where to get | ElevenLabs Dashboard -> Profile -> API Key |
| URL | https://elevenlabs.io/ |
| Format | Alphanumeric string |
| Example | `sk_abc123def456ghi789jkl012` |
| Used by | voice-selector (for ElevenLabs voice browsing), pronunciation-fixer (for ElevenLabs dictionary upload) |

### TWILIO_ACCOUNT_SID

| Field | Value |
|-------|-------|
| Required | No (only for phone number assignment) |
| Description | Twilio Account SID for assigning phone numbers to Retell agents. Required if the agent will receive or make phone calls via a Twilio number. |
| Where to get | Twilio Console -> Dashboard -> Account SID |
| URL | https://console.twilio.com/ |
| Format | Starts with `AC` followed by 32 hex characters |
| Example | `AC` + 32 hex characters |
| Used by | retell-api-wrapper (phone number operations) |

### TWILIO_AUTH_TOKEN

| Field | Value |
|-------|-------|
| Required | No (only for phone number assignment, paired with TWILIO_ACCOUNT_SID) |
| Description | Twilio Auth Token. Must be provided alongside TWILIO_ACCOUNT_SID. |
| Where to get | Twilio Console -> Dashboard -> Auth Token |
| Format | 32 hex characters |
| Example | `1234567890abcdef1234567890abcdef` |
| Used by | retell-api-wrapper (phone number operations) |

## Variable Validation

The pre-flight script `scripts/verify.sh` checks for:
1. `RETELL_API_KEY` is set and non-empty
2. `RETELL_API_KEY` starts with `key_`
3. API connectivity: makes a test GET /list-agents call
4. Optional vars are noted as missing but do not block execution

## Loading Variables

Variables are loaded from the shared environment at `/home/clawdbot/shared/.env`.
The orchestrator reads them at runtime via `$RETELL_API_KEY` etc.

For client deployments, the client API key is provided interactively and held
in a shell variable for the duration of the session. It is never written to any
file.
