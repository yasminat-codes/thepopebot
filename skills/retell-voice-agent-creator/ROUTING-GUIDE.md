# Routing Guide — Quick Reference

Use this table to quickly match user intent to the correct sub-skill and execution mode.

## Primary Routing Table

| Intent Phrases | Sub-Skill | Mode | Notes |
|----------------|-----------|------|-------|
| "create voice agent", "build agent", "new agent for [X]", "I need a voice agent", "set up a phone agent" | All 7 (full chain) | CHAIN | Full 8-step flow: Interview through Deploy |
| "quick deploy", "create and deploy immediately", "just use the [template] template" | voice-selector + prompt-generator + agent-config-builder + retell-api-wrapper | CHAIN (fast) | Skip interview, use template defaults |
| "fix pronunciation", "can't say [word]", "says [word] wrong", "pronunciation issues", "IPA dictionary" | pronunciation-fixer | SINGLE | May need agent_id to patch existing agent |
| "make it sound human", "humanize", "add pauses", "too robotic", "sounds like a robot", "more natural" | humanization-engine | SINGLE | Needs existing prompt text or agent_id |
| "change voice", "different voice", "browse voices", "voice selection", "what voices are available" | voice-selector | SINGLE | Returns voice_id for config |
| "update prompt", "rewrite prompt", "conversation flow", "add a state", "change the greeting" | prompt-generator | SINGLE | May need existing prompt as starting point |
| "too slow", "latency", "interruption issues", "background noise", "not responsive enough" | latency-optimizer | SINGLE | Tunes numeric settings on agent |
| "deploy agent", "list agents", "delete agent", "get call", "API call", "create phone call" | retell-api-wrapper | SINGLE | Direct Retell API operations |
| "generate config", "build config", "show JSON", "export config", "test scenarios" | agent-config-builder | SINGLE | Assembles JSON from parameters |
| "optimize existing agent", "improve agent", "make it better" | latency-optimizer + humanization-engine | PARALLEL | Both run simultaneously, outputs merged |

## Template Detection

| Template | Trigger Phrases |
|----------|----------------|
| receptionist | "receptionist", "front desk", "office phone", "medical office" |
| sales | "sales agent", "cold call", "outbound sales", "SDR", "closer" |
| support | "customer support", "help desk", "tech support", "troubleshoot" |
| appointment | "appointment setter", "booking agent", "scheduling", "calendar" |
| personal-assistant | "personal assistant", "PA", "executive assistant" |
| lead-qualifier | "lead qualifier", "qualify leads", "inbound leads", "screen calls" |
| survey | "survey", "feedback", "NPS", "customer satisfaction", "CSAT" |
| debt-collection | "debt collection", "collections", "payment reminder", "past due" |
| real-estate | "real estate", "property", "listing agent", "showing", "open house" |

## Mode Decision

- **CHAIN (full):** User wants a new agent from scratch
- **CHAIN (fast):** User wants template-only rapid deployment
- **SINGLE:** User wants one specific fix or action
- **PARALLEL:** User wants to optimize (latency + humanization together)

## Ambiguity Resolution

If intent is unclear, ask exactly one question:
> "Are you looking to create a new voice agent from scratch, or work on a
> specific part like pronunciation or voice selection?"
