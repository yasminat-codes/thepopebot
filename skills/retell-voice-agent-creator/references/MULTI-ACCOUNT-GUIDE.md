# Multi-Account Deployment Guide

How to deploy agents to your own account (internal) or a client's account.

## Deployment Modes

### Internal Mode

The default mode. Uses the `RETELL_API_KEY` environment variable from the
shared environment (`/home/clawdbot/shared/.env`).

**When to use:**
- Building agents for your own business
- Testing and development
- Internal team tools

**Flow:**
1. Orchestrator detects internal mode (default, or user confirms "this is for me").
2. API key loaded from `$RETELL_API_KEY` environment variable.
3. All API calls use this key.
4. Agent appears in your Retell Dashboard.

### Client Mode

Deploys to a client's Retell account using their API key.

**When to use:**
- Building agents for a client's account
- Agency work (building agents on behalf of others)
- White-label deployments

**Flow:**
1. Orchestrator detects client mode (user says "this is for a client" or answers
   the deployment question with "client").
2. Orchestrator asks: "Please provide your client's Retell API key. I'll use it
   only for this session and won't store it anywhere."
3. User provides the client's API key.
4. All deployment API calls use the client's key.
5. Agent appears in the client's Retell Dashboard.

## Security Rules

### Client API Key Handling

1. **Never write to disk.** Client API keys are held in working memory only.
   They are never written to `.env` files, config files, logs, or any persistent
   storage.

2. **Session-scoped.** The client key is valid only for the current conversation
   session. When the session ends, the key is discarded.

3. **Explicit consent.** Always inform the user before using a client key:
   "I'm about to create an agent in your client's account using the key you
   provided. Proceed?"

4. **No cross-contamination.** Client keys are never used for internal operations.
   If you need to do something in your own account during a client session,
   switch back to `$RETELL_API_KEY` explicitly.

## Multi-Organization Deployment

For deploying the same agent configuration to multiple accounts:

### Same Config, Multiple Accounts

1. Build the agent config once (full chain or template-based).
2. Save the config files to `output/`.
3. Deploy to the first account (internal or client).
4. For each additional account:
   a. Ask for the next account's API key.
   b. Re-run only Step 8 (Deployment) with the new key.
   c. The same `llm-config.json` and `agent-config.json` are reused.

### Using deploy.sh for Client Deployments

```bash
# Internal deployment (uses $RETELL_API_KEY)
./scripts/deploy.sh

# Client deployment (overrides API key)
./scripts/deploy.sh --api-key "key_client_xyz789"
```

The `--api-key` flag overrides the environment variable for that execution only.
It does not persist.

## Interview Question for Mode Detection

During the interview (Round 9, Q21), the orchestrator asks:

> "Is this agent for your own Retell account, or are you building it for a
> client's account?"

Responses and their mapping:
- "my account", "internal", "for me", "our team" -> Internal mode
- "client", "for a client", "their account", "agency work" -> Client mode
- No answer / skipped -> Default to internal mode

## Switching Modes Mid-Session

If the user needs to switch from internal to client mode (or vice versa) during
a session:

1. The config files in `output/` remain the same.
2. Only the API key used for deployment changes.
3. Ask for the new key if switching to client mode.
4. Confirm which account before proceeding with any API call.

## Troubleshooting Client Deployments

| Issue | Cause | Fix |
|-------|-------|-----|
| 401 on client key | Key invalid or expired | Ask client for a new key |
| 403 on client key | Key has restricted permissions | Ask client to use a full-access key |
| Agent created but not visible | Looking in wrong account | Verify by listing agents with the client key |
| Different features available | Client on different Retell plan | Some features require specific Retell plan tiers |
