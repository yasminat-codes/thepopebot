# Retell AI Voice Agent Creator

An OpenClaw skill that creates production-ready, human-sounding voice agents
on [Retell AI](https://www.retellai.com/). Handles the full lifecycle from
requirements gathering through deployment and testing.

## Architecture

```
                    +----------------------------+
                    |        SKILL.md            |
                    |   (Parent Orchestrator)    |
                    +----------------------------+
                               |
            Intent Detection + Routing Table
                               |
         +---------------------+---------------------+
         |         |         |         |         |    |         |
    +--------+ +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
    | Voice  | | Prompt | |Pronun- | |Human-  | |Latency | |Config  | |Retell  |
    |Selector| |Gener.  | |ciation | |ization | |Optim.  | |Builder | |API     |
    +--------+ +--------+ +--------+ +--------+ +--------+ +--------+ +--------+
         |         |         |         |         |    |         |
         +---------------------+---------------------+
                               |
                    +----------------------------+
                    |     output/ folder          |
                    | agent-config.json           |
                    | llm-config.json             |
                    | pronunciation-dict.json     |
                    | deployment-receipt.json      |
                    +----------------------------+
                               |
                    +----------------------------+
                    |     Retell AI Platform      |
                    |     (via REST API)          |
                    +----------------------------+
```

## Execution Modes

| Mode | When | Steps |
|------|------|-------|
| CHAIN (full) | "Create a voice agent for..." | Interview -> Voice -> Prompt -> Pronunciation -> Humanization -> Latency -> Config -> Deploy |
| CHAIN (fast) | "Quick deploy receptionist" | Voice -> Prompt -> Config -> Deploy (template defaults) |
| SINGLE | "Fix pronunciation on..." | One sub-skill only |
| PARALLEL | "Optimize existing agent" | Latency + Humanization simultaneously |

## Templates (9 built-in)

Sales, Support, Appointment, Receptionist, Personal Assistant, Lead Qualifier,
Survey, Debt Collection, Real Estate.

Each template includes: default voice, persona, conversation states, humanization
level, latency settings, sample greeting, and post-call analysis variables.
See [references/TEMPLATE-CATALOG.md](references/TEMPLATE-CATALOG.md).

## Prerequisites

- **curl** — for Retell API calls
- **jq** — for JSON processing
- **python3** — for pronunciation IPA generation and config assembly
- **RETELL_API_KEY** — required for deployment (get from https://dashboard.retellai.com/)
- **ELEVENLABS_API_KEY** — optional, for ElevenLabs voice cloning
- **TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN** — optional, for phone number assignment

## Quick Start

1. Run the pre-flight check:
   ```bash
   ./scripts/verify.sh
   ```

2. Ask the orchestrator to create an agent:
   > "Create a receptionist for Dr. Smith's dental office"

3. The orchestrator will:
   - Match the `receptionist` template
   - Conduct a short interview (3-5 questions)
   - Select a voice, generate the prompt, humanize it
   - Assemble config and deploy to Retell AI

4. Review the output in `output/`.

## File Structure

```
retell-voice-agent-creator/
  SKILL.md                 # Orchestrator (start here)
  README.md                # This file
  CHANGELOG.md             # Version history
  ROUTING-GUIDE.md         # Quick-reference routing table
  references/              # Reference documents
    API-QUICK-REFERENCE.md
    ENV-VARS.md
    EXAMPLES.md
    INTERVIEW-QUESTIONS.md
    MULTI-ACCOUNT-GUIDE.md
    ORCHESTRATION-LOGIC.md
    TEMPLATE-CATALOG.md
    TROUBLESHOOTING.md
    USER-INTENT-MAP.md
    VOICE-PROVIDER-COMPARISON.md
  scripts/                 # Executable scripts
    verify.sh              # Pre-flight check
    deploy.sh              # Full deployment
    test-agent.sh          # Trigger test call
  sub-skills/              # 7 sub-skills (each with own SKILL.md)
    voice-selector/
    prompt-generator/
    pronunciation-fixer/
    humanization-engine/
    latency-optimizer/
    agent-config-builder/
    retell-api-wrapper/
  templates/               # 9 industry templates
  assets/                  # Schemas, configs, pronunciation libraries
```

## References

- [Routing Guide](ROUTING-GUIDE.md) — Quick intent-to-sub-skill lookup
- [Orchestration Logic](references/ORCHESTRATION-LOGIC.md) — Chain execution rules
- [API Quick Reference](references/API-QUICK-REFERENCE.md) — Retell API curl examples
- [Troubleshooting](references/TROUBLESHOOTING.md) — Common issues and fixes
