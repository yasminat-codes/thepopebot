# Versioning and Rollback Guide

How to track agent versions and roll back to previous configurations in Retell AI.

---

## Overview

Retell does not expose an explicit versioning API. However, every PATCH to an agent
or LLM creates a new internal version. To manage versions and enable rollback, you
must track configurations client-side.

## Version Tracking Strategy

### Before Every Update

Always save the current configuration before making changes:

```bash
# Save agent config
curl -s "https://api.retellai.com/get-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  > "versions/agent-${AGENT_ID}-$(date +%Y%m%d-%H%M%S).json"

# Save LLM config
curl -s "https://api.retellai.com/get-retell-llm/$LLM_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  > "versions/llm-${LLM_ID}-$(date +%Y%m%d-%H%M%S).json"
```

### Version Directory Structure

```
versions/
  agent-agent_7890xyz-20260224-100000.json
  agent-agent_7890xyz-20260224-143000.json
  llm-llm_abc123-20260224-100000.json
  llm-llm_abc123-20260224-143000.json
```

### Version Manifest

Maintain a `versions/manifest.json` to track changes:

```json
[
  {
    "timestamp": "2026-02-24T10:00:00Z",
    "agent_id": "agent_7890xyz",
    "llm_id": "llm_abc123",
    "description": "Initial deployment",
    "agent_file": "agent-agent_7890xyz-20260224-100000.json",
    "llm_file": "llm-llm_abc123-20260224-100000.json"
  },
  {
    "timestamp": "2026-02-24T14:30:00Z",
    "agent_id": "agent_7890xyz",
    "llm_id": "llm_abc123",
    "description": "Updated voice speed to 1.1",
    "agent_file": "agent-agent_7890xyz-20260224-143000.json",
    "llm_file": "llm-llm_abc123-20260224-143000.json"
  }
]
```

## Rolling Back

### Rollback Agent

PATCH the agent with the saved configuration:

```bash
# Find the version to restore
BACKUP="versions/agent-agent_7890xyz-20260224-100000.json"

# Remove read-only fields before patching
RESTORE_BODY=$(cat "$BACKUP" | jq 'del(.agent_id, .last_modification_timestamp)')

# Apply the rollback
curl -s -X PATCH "https://api.retellai.com/update-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$RESTORE_BODY"
```

### Rollback LLM

```bash
BACKUP="versions/llm-llm_abc123-20260224-100000.json"
RESTORE_BODY=$(cat "$BACKUP" | jq 'del(.llm_id, .last_modification_timestamp)')

curl -s -X PATCH "https://api.retellai.com/update-retell-llm/$LLM_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$RESTORE_BODY"
```

### Verify Rollback

After rolling back, verify the config matches:

```bash
CURRENT=$(curl -s "https://api.retellai.com/get-agent/$AGENT_ID" \
  -H "Authorization: Bearer $RETELL_API_KEY")

# Compare key fields
echo "$CURRENT" | jq '{voice_speed, responsiveness, voice_id}'
```

## Naming Convention for A/B Testing

When running multiple versions simultaneously (different agents):

| Pattern | Example | Use |
|---------|---------|-----|
| `{name} v{N}` | "Sales Agent v1" | Sequential versions |
| `{name} (A)` / `{name} (B)` | "Sales Agent (A)" | A/B test variants |
| `{name} v{N}-rollback` | "Sales Agent v2-rollback" | Rolled back from v2 to v1 |

## Automated Version Script

Use [retell-api.sh](../scripts/retell-api.sh) functions with version tracking:

```bash
source retell-api.sh

# Save current version before update
retell_get_agent "$AGENT_ID" > "versions/agent-${AGENT_ID}-$(date +%Y%m%d-%H%M%S).json"

# Apply update
retell_update_agent "$AGENT_ID" '{"voice_speed": 1.1}'

# If something goes wrong, roll back
LATEST_BACKUP=$(ls -t versions/agent-${AGENT_ID}-*.json | head -1)
RESTORE=$(cat "$LATEST_BACKUP" | jq 'del(.agent_id, .last_modification_timestamp)')
retell_update_agent "$AGENT_ID" "$RESTORE"
```
