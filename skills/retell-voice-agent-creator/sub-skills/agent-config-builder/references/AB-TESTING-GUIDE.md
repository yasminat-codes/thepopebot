# A/B Testing Guide

How to create, deploy, and analyze agent variants for comparison testing.

---

## Overview

A/B testing compares two or more agent configurations to find the best performer.
Each variant is a separate Retell agent with different settings. Split traffic
between variants and compare post-call analytics after sufficient data.

## What to Vary

Test one dimension at a time for clean results. Common dimensions:

### Voice Variants

| Variant | Change | Why |
|---------|--------|-----|
| A | Primary voice (e.g., 11labs-Myra) | Baseline |
| B | Different gender (e.g., 11labs-Adrian) | Gender preference |
| C | Different provider (e.g., openai-alloy) | Provider quality |

### Humanization Variants

| Variant | Change | Why |
|---------|--------|-----|
| A | Full humanization (backchannel + ambient + emotion) | Maximum naturalness |
| B | Minimal (no backchannel, no ambient) | Clean, professional |

### Responsiveness Variants

| Variant | Change | Why |
|---------|--------|-----|
| A | Conservative (responsiveness: 0.7) | Thoughtful pauses |
| B | Aggressive (responsiveness: 0.95) | Snappy responses |

### Prompt Style Variants

| Variant | Change | Why |
|---------|--------|-----|
| A | Warm, casual tone | Friendly approachability |
| B | Professional, concise tone | Authority and efficiency |

## Creating Variants

### File Naming Convention

```
agent-config-v1.json      # Variant A (control)
agent-config-v2.json      # Variant B (test)
agent-config-v3.json      # Variant C (optional)
llm-config-v1.json        # LLM for variant A
llm-config-v2.json        # LLM for variant B (if prompt differs)
```

### Agent Naming Convention

| Pattern | Example |
|---------|---------|
| `{name} (A)` | "Acme Receptionist (A)" |
| `{name} (B)` | "Acme Receptionist (B)" |
| `{name} (C)` | "Acme Receptionist (C)" |

### Building Variant Configs

Use build-config.py with different input files for each variant:

```bash
# Variant A: warm voice, full humanization
python3 build-config.py \
  --voice-config voice_warm.json \
  --humanization human_full.json \
  --prompt-config prompt_casual.json \
  --template sales-outbound \
  --business-info biz.json
mv agent-config.json agent-config-v1.json
mv llm-config.json llm-config-v1.json

# Variant B: professional voice, minimal humanization
python3 build-config.py \
  --voice-config voice_professional.json \
  --humanization human_minimal.json \
  --prompt-config prompt_professional.json \
  --template sales-outbound \
  --business-info biz.json
mv agent-config.json agent-config-v2.json
mv llm-config.json llm-config-v2.json
```

## Deployment

Deploy each variant as a separate agent using retell-api-wrapper:

```bash
# Deploy Variant A
./deploy-agent.sh --llm-config llm-config-v1.json --agent-config agent-config-v1.json
# Save agent_id_a

# Deploy Variant B
./deploy-agent.sh --llm-config llm-config-v2.json --agent-config agent-config-v2.json
# Save agent_id_b
```

## Traffic Splitting

Retell does not have built-in traffic splitting. Options:

1. **Manual rotation** — alternate which agent handles calls daily
2. **Webhook router** — build a small service that routes calls to agents
3. **Phone number split** — assign different phone numbers to each variant
4. **Time-based** — variant A handles morning calls, variant B handles afternoon

## Minimum Sample Size

For statistically meaningful results:

| Metric Type | Minimum Calls Per Variant |
|-------------|--------------------------|
| Boolean (booked/not) | 50 calls |
| Numeric (lead score) | 30 calls |
| Sentiment distribution | 50 calls |

## Analysis

After sufficient calls, compare using post-call analytics:

```bash
# Pull calls for each variant
curl -s "https://api.retellai.com/v2/list-calls?agent_id=$AGENT_A&limit=100" \
  -H "Authorization: Bearer $RETELL_API_KEY" > calls_a.json

curl -s "https://api.retellai.com/v2/list-calls?agent_id=$AGENT_B&limit=100" \
  -H "Authorization: Bearer $RETELL_API_KEY" > calls_b.json
```

### Metrics to Compare

| Metric | Source | Better = |
|--------|--------|----------|
| Success rate | `appointment_booked` / `did_express_interest` | Higher |
| Lead quality | Average `lead_score` | Higher |
| Sentiment | % positive `user_sentiment` | Higher |
| Call duration | Average `duration_ms` | Depends on goal |
| Escalation rate | % `escalation_needed` = true | Lower |

## Decision Framework

After analysis, choose the winner:

1. **Clear winner** — one variant beats the other on all metrics. Deploy winner.
2. **Mixed results** — each variant wins on different metrics. Decide which
   metrics matter most for the use case.
3. **No difference** — variants perform similarly. Keep the simpler/cheaper one.
4. **Both poor** — neither meets targets. Create new variants with bigger changes.
