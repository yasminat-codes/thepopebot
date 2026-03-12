---
name: vapi
description: >
  Vapi voice AI platform. TRIGGER when user wants to: create a voice assistant, build a phone bot,
  configure a voice agent, create outbound calls, make batch calls, set up webhooks, build tool servers,
  create squads with agent handoffs, build conversation workflows, set up a Vapi API key,
  integrate Vapi with Google Calendar/Sheets/Slack, handle transcripts, configure STT/TTS/LLM providers,
  add hooks to calls, or anything related to Vapi's voice AI API.
  Covers the full Vapi platform: assistants, calls, squads, tools, workflows, webhooks, phone numbers,
  voice providers (ElevenLabs, Cartesia, PlayHT, Deepgram, OpenAI TTS, Azure), transcribers (Deepgram,
  Google STT, AssemblyAI, Gladia, Speechmatics), LLM providers (OpenAI, Anthropic, Google, Groq, Perplexity).
license: MIT
compatibility: Requires internet access and VAPI_API_KEY environment variable.
metadata:
  author: Yasmine Seidu (consolidated from VapiAI/skills)
  version: "1.2.0"
---

# Vapi Voice AI

Single skill covering the full Vapi platform. All detailed content lives in `references/` — loaded on demand.

> **Prerequisite:** `VAPI_API_KEY` environment variable must be set.
> First time? See [API Key Setup](references/setup-api-key.md).

## Quick Reference

| Want to... | Reference | Key sections |
|-----------|-----------|-------------|
| Create a voice assistant | [create-assistant](references/create-assistant.md) | Quick Start, Core Config, Behavior, Hooks |
| Make an outbound call | [create-call](references/create-call.md) | Outbound, Batch, Scheduled |
| Create tools for agents | [create-tool](references/create-tool.md) | Tool Types, Tool Server, Attaching |
| Build multi-agent squads | [create-squad](references/create-squad.md) | Handoffs, Member Overrides |
| Build structured workflows | [create-workflow](references/create-workflow.md) | Node Types, Patterns |
| Set up webhooks | [setup-webhook](references/setup-webhook.md) | Event Types, Auth, Examples |
| Configure API key | [setup-api-key](references/setup-api-key.md) | Validation, Storage |
| Browse voice/model providers | [providers](references/providers.md) | All STT, TTS, LLM options |
| Configure call hooks | [hooks](references/hooks.md) | Events, Actions, Filters |
| Build a tool server | [tool-server](references/tool-server.md) | Request/response format, examples |
| Look up webhook payloads | [webhook-events](references/webhook-events.md) | All event schemas |
| Make agent sound human | [human-voice](references/human-voice.md) | Quick-start config, use case presets, failure modes |
| Write humanized system prompts | [humanization-prompts](references/humanization-prompts.md) | Forbidden phrases, filler patterns, response rules |
| Choose a voice provider | [voice-provider-matrix](references/voice-provider-matrix.md) | Latency, quality, emotion controls, recommendations |
| Configure speech timing | [speech-config](references/speech-config.md) | startSpeakingPlan, endpointing, interruptions |
| Fix pronunciation | [pronunciation](references/pronunciation.md) | ElevenLabs dictionary API, IPA, phoneme guide |
| Add SSML/pauses/emotion | [audio-texture](references/audio-texture.md) | SSML tags, flush syntax, Cartesia controls |
| Engineer voice prompts | [prompt-architecture](references/prompt-architecture.md) | 8-section structure, persona dimensions, WRITE-FOR-THE-EAR rules |
| Test and QA voice agents | [testing-quality](references/testing-quality.md) | KPIs, pre-launch checklist, golden response method |

## Common Workflows

### 1. Launch a Support Bot (5 min)

```bash
# Step 1: Create the assistant
curl -X POST https://api.vapi.ai/assistant \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Support Bot",
    "firstMessage": "Hello! How can I help you today?",
    "model": {
      "provider": "openai",
      "model": "gpt-4.1",
      "messages": [{"role": "system", "content": "You are a friendly support agent. Keep responses under 30 words."}]
    },
    "voice": {"provider": "vapi", "voiceId": "Lily"},
    "transcriber": {"provider": "deepgram", "model": "nova-3", "language": "en"}
  }'
# Step 2: Attach to phone number in Vapi Dashboard → Phone Numbers → select number → assign assistant
```

### 2. Outbound Sales Call

```bash
curl -X POST https://api.vapi.ai/call \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "assistantId": "your-assistant-id",
    "phoneNumberId": "your-phone-number-id",
    "customer": {"number": "+11234567890", "name": "Jane Smith"}
  }'
```

See [create-call reference](references/create-call.md) for batch calls, scheduling, and web calls.

### 3. Multi-Department Routing (Squad)

```bash
curl -X POST https://api.vapi.ai/squad \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Support Squad",
    "members": [
      {
        "assistant": {
          "name": "Receptionist",
          "firstMessage": "Hello! Sales or support?",
          "model": {
            "provider": "openai", "model": "gpt-4.1",
            "messages": [{"role": "system", "content": "Route to sales or support."}],
            "tools": [{"type": "handoff", "destinations": [
              {"type": "assistant", "assistantId": "SALES_ID", "description": "Transfer for purchase questions"},
              {"type": "assistant", "assistantId": "SUPPORT_ID", "description": "Transfer for technical issues"}
            ]}]
          },
          "voice": {"provider": "vapi", "voiceId": "Elliot"},
          "transcriber": {"provider": "deepgram", "model": "nova-3", "language": "en"}
        }
      },
      {"assistantId": "SALES_ID"},
      {"assistantId": "SUPPORT_ID"}
    ]
  }'
```

See [create-squad reference](references/create-squad.md) for full squad patterns.

### 4. Receive & Process Call Events

```typescript
// Minimal Express webhook handler
app.post("/vapi/webhook", (req, res) => {
  const { message } = req.body;
  if (message.type === "tool-calls") {
    const results = message.toolCallList.map(tc => ({
      toolCallId: tc.id,
      result: handleTool(tc.name, tc.arguments)
    }));
    return res.json({ results });
  }
  if (message.type === "end-of-call-report") {
    console.log("Call ended:", message.call.id, "Summary:", message.summary);
  }
  res.json({});
});
```

See [setup-webhook reference](references/setup-webhook.md) for full server examples, auth, and local dev.

## API Essentials

| Item | Value |
|------|-------|
| Base URL | `https://api.vapi.ai` |
| Auth header | `Authorization: Bearer $VAPI_API_KEY` |
| Content-Type | `application/json` |
| Dashboard | `https://dashboard.vapi.ai` |
| Docs | `https://docs.vapi.ai` |

## MCP Docs Server

Add the Vapi docs MCP server to get full API knowledge inline:

```bash
claude mcp add vapi-docs -- npx -y mcp-remote https://docs.vapi.ai/_mcp/server
```

Use the `searchDocs` tool to look up anything beyond what these references cover.

## Reference Index

| File | Purpose |
|------|---------|
| [create-assistant.md](references/create-assistant.md) | Build voice agents with model/voice/transcriber config, hooks, tools |
| [create-call.md](references/create-call.md) | Outbound calls, web calls, batch calls, scheduling |
| [create-squad.md](references/create-squad.md) | Multi-assistant squads with context-preserving handoffs |
| [create-tool.md](references/create-tool.md) | Function tools, transfer tools, Google/Slack integrations |
| [create-workflow.md](references/create-workflow.md) | Node-based deterministic conversation flows |
| [setup-api-key.md](references/setup-api-key.md) | Get and configure Vapi API credentials |
| [setup-webhook.md](references/setup-webhook.md) | Receive real-time call events and handle tool calls |
| [hooks.md](references/hooks.md) | Hook event types and action configuration |
| [providers.md](references/providers.md) | All STT, TTS, and LLM provider options |
| [tool-server.md](references/tool-server.md) | Implement a tool server (request/response format) |
| [webhook-events.md](references/webhook-events.md) | All webhook event payload schemas |
| **Human Voice** | |
| [human-voice.md](references/human-voice.md) | Master guide: 5-layer stack, presets, failure modes, production checklist |
| [humanization-prompts.md](references/humanization-prompts.md) | System prompt templates, 50+ forbidden phrases, filler patterns, response length rules |
| [voice-provider-matrix.md](references/voice-provider-matrix.md) | Latency benchmarks, ElevenLabs/Cartesia config fields, use-case recommendations |
| [speech-config.md](references/speech-config.md) | startSpeakingPlan, stopSpeakingPlan, endpointing, waitFunction, transcriber fields |
| [pronunciation.md](references/pronunciation.md) | ElevenLabs pronunciation dictionary API, IPA guide, phoneme rules, number/date formatting |
| [audio-texture.md](references/audio-texture.md) | SSML tags, flush syntax, emotion controls, background sound, SSML bug fix |
| [prompt-architecture.md](references/prompt-architecture.md) | 8-section prompt structure, persona dimensions, state design, WRITE-FOR-THE-EAR rules |
| [testing-quality.md](references/testing-quality.md) | KPIs, pre-launch checklist, scenario testing, golden response method, gradual rollout |
