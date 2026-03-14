# Google Workspace — Auth Reference

## Credential Setup

| Setting | Value |
|---------|-------|
| Credential file | `/Users/yasmineseidu/coding/google.json` |
| Env var | `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` |
| Set in | `~/.zshrc` |
| File permissions | `chmod 600 /Users/yasmineseidu/coding/google.json` |

The env var is already set globally. Verify with:
```bash
echo $GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE
```

## Authentication Methods

### Service Account (Domain-Wide Delegation) — Current Setup
```bash
# Already configured via env var. Test it:
gws gmail users getProfile --params '{"userId":"me"}'
```

Service account key at `/Users/yasmineseidu/coding/google.json` authenticates as `yasmine@smarterflo.com` through domain-wide delegation configured in Google Workspace Admin Console.

### OAuth (Interactive — Fallback Only)
```bash
gws auth login
```
Use only when service account fails. Creates `~/.config/gws/` token store.

## Domain-Wide Delegation Setup

Delegation is already configured. If it breaks:
1. Google Workspace Admin Console → Security → API Controls → Domain-wide delegation
2. Add service account Client ID (found in `google.json` as `"client_id"`)
3. Add the required OAuth scopes (see below)

**Scope rule:** Use a single broad scope per service. Never mix granular + broad scopes for the same service — the broader one wins and the narrower ones cause auth errors.

## Scopes (Currently Delegated)

```
https://www.googleapis.com/auth/gmail.modify
https://www.googleapis.com/auth/calendar
https://www.googleapis.com/auth/tasks
https://www.googleapis.com/auth/drive
https://www.googleapis.com/auth/documents
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/presentations
https://www.googleapis.com/auth/chat.bot
https://www.googleapis.com/auth/forms.body
https://www.googleapis.com/auth/keep
https://www.googleapis.com/auth/contacts
https://www.googleapis.com/auth/admin.reports.audit.readonly
https://www.googleapis.com/auth/admin.reports.usage.readonly
```

## Common Auth Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `PERMISSION_DENIED: Request had insufficient authentication scopes` | Missing scope in delegation | Add scope in Admin Console |
| `unauthorized_client` | Service account not authorized for delegation | Re-add service account in Admin Console |
| `invalid_grant` | Token expired or clock skew | Re-run `gws auth login` for OAuth, or check system clock |
| `403 Forbidden` | Scope present but not granted to this user | Check per-user settings in Admin Console |
| Credential file not found | Wrong path or missing env var | Verify `$GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` |
