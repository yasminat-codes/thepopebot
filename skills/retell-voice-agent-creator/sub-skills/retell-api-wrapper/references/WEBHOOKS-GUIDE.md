# Webhooks Guide

How to configure and use webhooks with Retell AI agents for real-time call events.

---

## Overview

Webhooks let your server receive real-time notifications when events occur during
or after a call. Set a `webhook_url` on your agent and specify which events to
receive via `webhook_events`.

## Setting Up Webhooks

### On Agent Creation

```bash
curl -s -X POST https://api.retellai.com/create-agent \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "response_engine": {"type": "retell-llm", "llm_id": "llm_abc123"},
    "voice_id": "11labs-Adrian",
    "webhook_url": "https://your-server.com/retell-webhook",
    "webhook_events": ["call_started", "call_ended", "call_analyzed"]
  }'
```

### On Existing Agent

```bash
curl -s -X PATCH "https://api.retellai.com/update-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_url": "https://your-server.com/retell-webhook",
    "webhook_events": ["call_started", "call_ended", "call_analyzed"]
  }'
```

## Available Events

| Event | When It Fires | Typical Use |
|-------|--------------|-------------|
| `call_started` | Call begins ringing or connects | Log call start, update CRM |
| `call_ended` | Call terminates (any reason) | Log call end, trigger follow-up |
| `call_analyzed` | Post-call analysis completes | Store analysis, score lead |
| `transcript_updated` | New transcript chunk available | Real-time monitoring |
| `transfer_started` | Agent initiates a transfer | Alert receiving team |
| `transfer_bridged` | Transfer connects to target | Log transfer success |
| `transfer_cancelled` | Transfer was cancelled | Log, maybe retry |
| `transfer_ended` | Transfer call terminates | Clean up transfer state |

## Payload Format

### call_started

```json
{
  "event": "call_started",
  "call_id": "call_abc123",
  "agent_id": "agent_7890xyz",
  "from_number": "+14155551234",
  "to_number": "+14155555678",
  "direction": "outbound",
  "timestamp": 1708790400000
}
```

### call_ended

```json
{
  "event": "call_ended",
  "call_id": "call_abc123",
  "agent_id": "agent_7890xyz",
  "duration_ms": 120000,
  "end_reason": "agent_ended",
  "transcript": "Agent: Hi there... User: I need to book...",
  "timestamp": 1708790520000
}
```

### call_analyzed

```json
{
  "event": "call_analyzed",
  "call_id": "call_abc123",
  "agent_id": "agent_7890xyz",
  "call_analysis": {
    "call_summary": "Customer booked a cleaning appointment for March 3rd.",
    "user_sentiment": "positive",
    "custom_field_1": "value"
  },
  "timestamp": 1708790530000
}
```

## Testing Webhooks

Use a service like webhook.site or ngrok to test locally:

1. Get a test URL from https://webhook.site
2. Set it as your agent's `webhook_url`
3. Make a test web call
4. Check webhook.site for received events

```bash
# Set test webhook
curl -s -X PATCH "https://api.retellai.com/update-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"webhook_url": "https://webhook.site/your-unique-id"}'
```

## Best Practices

- **Respond quickly** — return 200 within 5 seconds to avoid retries
- **Process async** — queue webhook payloads for background processing
- **Validate source** — check the payload structure matches expected format
- **Handle duplicates** — use `call_id` as idempotency key
- **Monitor failures** — log webhook delivery failures for debugging
