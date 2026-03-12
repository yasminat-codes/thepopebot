# Retell 2026 Features Reference

Major Retell features added in 2025-2026 that most users don't know about.

## Flex Mode

Compiles conversation flow into a single structured prompt. The agent dynamically
navigates the flow instead of following rigid state transitions.

**Key constraints:**
- Limit to under 20 nodes
- Per-node Knowledge Base is ignored in Flex Mode (must set KB at agent level)
- Use when flows are dynamic and user-driven
- Avoid for compliance-heavy scripts where exact state transitions matter

## Agent Transfer

Mid-call agent switching with full conversation context preserved. Enables warm
handoffs between specialist agents (e.g., greeting agent transfers to sales agent
transfers to booking agent).

**Limitation:** Works on phone calls only, not web calls.

## Global Nodes

Always-accessible states that can be reached from any point in the conversation.
No need to wire transitions from every node.

**Use for:**
- Transfer to human ("I need to speak to someone")
- Repeat last message
- Capture caller name at any point
- Handle universal intents like "cancel" or "start over"

## Per-Node LLM Selection

Assign different models to different conversation nodes. Optimizes cost without
sacrificing quality where it matters.

**Recommended pattern:**
- `gpt-4.1-nano` for greetings, simple routing, confirmations
- `gpt-4.1` for complex reasoning, objection handling, nuanced responses

**Result:** 60-80% cost reduction on simple nodes while keeping full capability
on nodes that need it.

## Reusable Components

Nodes that sync across multiple agents. Change the component once and every agent
using it updates automatically. Essential for multi-agent deployments with shared
logic (e.g., a standard greeting or compliance disclaimer).

## Retell Assure (AI QA)

Automated call review with hallucination detection. Launched January 2026.

- Integrates with post-call analytics
- Configure hallucination detection threshold and topic adherence scoring
- Review weekly summary reports
- Flag calls scoring below threshold for human review

## Agent Guardrails

Jailbreak blocking and harmful content filtering. Launched February 2026.

**Always enable on production agents.** Prevents prompt injection attacks and
blocks harmful content generation during calls.

## Simulation Testing

Batch test full conversations with synthetic callers. Launched March 2025.

- Create test scenarios in the Retell dashboard (Simulation tab)
- Configure synthetic callers with specific personas (happy path, objector,
  angry, confused, rushed)
- Run batches of 20-50 simulated conversations
- Review transcripts for correct state transitions, no hallucinations, proper
  escalation triggers

## Agent Version Control

Built-in version management: create, test, and revert agent configurations.
Launched April 2025. Not just client-side backup — Retell tracks versions natively.

## MCP Client

External tool integration during live calls via Model Context Protocol.
Launched July 2025. Enables agents to call external APIs, query databases,
or trigger actions mid-conversation.

## Knowledge Base 2.0

50% accuracy improvement over the original KB. Launched alongside Flex Mode.

- Per-node KB assignment works in traditional flow mode only
- In Flex Mode, KB must be set at agent level
- Supports larger document uploads and better chunking

## Warm Transfer 2.0

Enhanced human handoff capabilities. Launched July 2025.

- Human detection: knows when a human picks up
- Whisper messages: brief the human agent before connecting
- Three-way calling: agent stays on briefly during handoff

## PII Redaction

Automatic redaction of sensitive data in transcripts and recordings.
Launched August 2025.

- Covers: names, SSN, credit card numbers
- Configure via `pii_config` parameter in agent config
- Cost: $0.01/min additional
- Redacted data replaced with `[REDACTED]` in transcripts

## GPT-5 Models

GPT-5, GPT-5 Mini, and GPT-5 Nano available as LLM options.
Launched August 2025. Select in the LLM configuration.

## MiniMax Voice Provider

40+ language support with voice cloning capability. Launched December 2025.
Strong option for Asian language markets at budget-friendly pricing.

## New Configuration Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `enable_dynamic_voice_speed` | Boolean | Auto-matches caller's speaking pace. Works with all voice providers. |
| `fallback_voice_ids` | Array | Backup voices from different TTS providers. Failover if primary voice is unavailable. |
| `begin_message_delay_ms` | Integer (0-5000) | Delay before first message. 300-500ms sounds like a human picking up the phone. |
| `vocab_specialization` | String ("medical") | Clinical vocabulary optimization. English only. |
| `data_storage_setting` | String | Set to `"basic_attributes_only"` for minimal data retention. |

## Fast Tier

Premium infrastructure tier. 1.5x normal cost.

**Benefits:**
- 50% latency variance reduction (more consistent response times)
- 99.9% availability SLA

**Recommended for:** Sales demos, high-value calls, any deployment where
consistency and uptime justify the cost premium.
