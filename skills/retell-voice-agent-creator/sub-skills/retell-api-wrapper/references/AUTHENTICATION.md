# Authentication Reference

How to authenticate with the Retell AI API and manage API keys securely.

---

## Getting Your API Key

1. Log into the Retell AI dashboard at https://www.retellai.com/dashboard
2. Navigate to **Settings > API Keys**
3. Copy your API key

## Header Format

All requests require the `Authorization` header:

```
Authorization: Bearer <your_api_key>
```

Example:
```bash
curl -s https://api.retellai.com/list-agents \
  -H "Authorization: Bearer ret_abc123def456..."
```

## Testing Authentication

Verify your key works with a simple list call:

```bash
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $RETELL_API_KEY" \
  https://api.retellai.com/list-agents)

if [ "$STATUS" = "200" ]; then
  echo "Authentication successful"
elif [ "$STATUS" = "401" ]; then
  echo "ERROR: Invalid API key"
else
  echo "ERROR: Unexpected status $STATUS"
fi
```

## Environment Variable Setup

Store your API key in an environment variable. Never hard-code it.

```bash
# In .env file
RETELL_API_KEY=ret_your_key_here

# For client deployments
RETELL_CLIENT_API_KEY=ret_client_key_here
```

## Multi-Account Key Management

When deploying to both internal and client accounts:

- **Internal key**: Store in `RETELL_API_KEY` environment variable
- **Client key**: Pass via `--api-key` flag on each command
- Never mix keys in a single deployment session
- Log which key was used in the deployment receipt

## Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** or secure secret stores
3. **Rotate keys** if you suspect compromise
4. **Separate keys** per environment (dev, staging, production)
5. **Limit access** — only share keys with team members who need them
6. **Audit usage** — check the Retell dashboard for unexpected API calls
