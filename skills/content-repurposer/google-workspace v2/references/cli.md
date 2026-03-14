# Google Workspace CLI — Full Reference

## Syntax

```bash
gws <service> <resource> [sub-resource] <method> [flags]
```

### Examples
```bash
gws gmail users messages list --params '{"userId":"me","q":"is:unread"}'
gws calendar events insert --json '{"summary":"Meeting","start":{"dateTime":"2026-03-10T10:00:00"},"end":{"dateTime":"2026-03-10T11:00:00"}}'
gws drive files list --params '{"pageSize":10}' --format table
```

## Global Flags

| Flag | Description | Example |
|------|-------------|---------|
| `--format <FORMAT>` | Output: `json` (default), `table`, `yaml`, `csv` | `--format table` |
| `--dry-run` | Validate locally — no API call made | `--dry-run` |
| `--sanitize <TEMPLATE>` | Screen response through Model Armor template | `--sanitize my-template` |

## Method Flags

| Flag | Short | Description | Example |
|------|-------|-------------|---------|
| `--params '{"key":"val"}'` | | URL/query parameters | `--params '{"userId":"me","maxResults":10}'` |
| `--json '{"key":"val"}'` | | Request body (JSON) | `--json '{"title":"Doc Title"}'` |
| `--output <PATH>` | `-o` | Save binary response to file | `-o /tmp/file.pdf` |
| `--upload <PATH>` | | Upload file (multipart) | `--upload /path/to/file.png` |
| `--page-all` | | Auto-paginate all results (NDJSON output) | `--page-all` |
| `--page-limit <N>` | | Max pages when using --page-all (default: 10) | `--page-limit 5` |
| `--page-delay <MS>` | | Delay between pages in ms (default: 100) | `--page-delay 500` |

## API Discovery

Before calling any method, inspect it first:

```bash
# List all resources for a service
gws gmail --help
gws drive --help

# List methods for a resource
gws gmail users messages --help
gws calendar events --help

# Get full API schema for a specific method
gws schema gmail.users.messages.list
gws schema calendar.events.insert
gws schema drive.files.list

# List all available services
gws --help
```

`gws schema` is the most powerful tool — it shows all parameters, their types, required vs optional, and descriptions.

## Pagination

```bash
# Get all results across pages (NDJSON — one JSON object per line)
gws drive files list --params '{"pageSize":100}' --page-all

# Parse NDJSON output with jq
gws drive files list --page-all | jq -r '.files[].name'

# Limit to 3 pages max
gws drive files list --page-all --page-limit 3
```

## Output Formatting

```bash
# JSON (default) — for programmatic use
gws gmail users messages list --params '{"userId":"me","maxResults":5}'

# Table — for human reading
gws drive files list --format table

# CSV — for export to sheets
gws sheets spreadsheets values get \
  --params '{"spreadsheetId":"ID","range":"Sheet1"}' \
  --format csv

# YAML
gws calendar events list --params '{"calendarId":"primary"}' --format yaml
```

## File Upload

```bash
# Upload a file to Drive
gws drive files create \
  --json '{"name":"report.pdf","parents":["FOLDER_ID"]}' \
  --upload /path/to/report.pdf

# Upload via helper
gws drive +upload --file "/path/to/file.pdf" --name "filename.pdf"
```

## Helper Commands (`+` prefix)

Simplified interfaces for common operations:

| Helper | Service | Description |
|--------|---------|-------------|
| `gws gmail +send` | Gmail | Send email with --to --subject --body |
| `gws gmail +triage` | Gmail | Unread inbox summary |
| `gws gmail +watch` | Gmail | Stream new emails as NDJSON |
| `gws calendar +insert` | Calendar | Create event with --summary --start --end |
| `gws calendar +agenda` | Calendar | Today's calendar agenda |
| `gws drive +upload` | Drive | Upload file with --file --name --folder |
| `gws docs +write` | Docs | Write content to a doc |
| `gws sheets +read` | Sheets | Read a range of values |
| `gws sheets +append` | Sheets | Append rows to a sheet |
| `gws chat +send` | Chat | Send a message to a space |

## Common Patterns

```bash
# Extract a field from JSON output
gws gmail users getProfile --params '{"userId":"me"}' | jq '.emailAddress'

# Get IDs for further operations
FILE_ID=$(gws drive files list --params '{"q":"name='\''My File'\''"}' | jq -r '.files[0].id')
gws drive files get --params "{\"fileId\":\"$FILE_ID\"}"

# Batch operations with --page-all
gws calendar events list \
  --params '{"calendarId":"primary","timeMin":"2026-03-01T00:00:00Z","timeMax":"2026-03-31T23:59:59Z"}' \
  --page-all | jq '.items[] | {summary: .summary, start: .start.dateTime}'
```

## Error Handling

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request / invalid params | Check `gws schema` for correct params |
| 401 | Unauthorized | Verify `$GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE` |
| 403 | Permission denied / scope missing | Add scope in Admin Console delegation |
| 404 | Resource not found | Verify ID is correct |
| 429 | Rate limited | Add delay, use `--page-delay` |
| 500 | Server error | Retry with backoff |
