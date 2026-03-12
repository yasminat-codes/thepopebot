---
name: google-workspace
description: >-
  Full Google Workspace integration via gws CLI for Gmail, Calendar, Drive, Docs, Sheets, Slides,
  Tasks, Chat, Meet, Forms, Keep, People, and Admin Reports. Use PROACTIVELY when user says
  "send email", "check calendar", "create google doc", "google sheet", "google drive",
  "schedule meeting", "gmail", "google slides", "add to calendar", "google forms",
  "google keep", "google chat", or any Google product interaction. Mandatory skill for
  ALL Google Workspace operations.
allowed-tools: Read Write Edit Bash Task
argument-hint: "[product-or-action] (optional)"
disable-model-invocation: false
user-invocable: true
model: sonnet
license: Proprietary
metadata:
  author: yasmine-seidu
  version: "3.0.0"
  category: productivity
---

# Google Workspace Integration

Complete Google Workspace access for yasmine@smarterflo.com via the `gws` CLI with service account domain-wide delegation.

---

## IRON LAW — NON-NEGOTIABLE

```
1. Verify gws CLI before any operation: gws gmail users getProfile --params '{"userId":"me"}'
2. Default workspace is yasmine@smarterflo.com — confirm if user specifies otherwise
3. Preview EVERY write/delete/send — show user exactly what will happen before executing
4. Batch operations require --dry-run first. No exceptions.
5. Never output credential files, tokens, or service account JSON contents
```

---

## Configuration

| Setting | Value |
|---------|-------|
| Engine | `gws` CLI (installed globally) |
| Credentials | `GOOGLE_WORKSPACE_CLI_CREDENTIALS_FILE=/Users/yasmineseidu/coding/google.json` |
| Delegated User | `yasmine@smarterflo.com` |
| Project ID | `clawdbot-484604` |
| Env var set in | `~/.zshrc` |

**Verify setup:**
```bash
gws --help
gws gmail users getProfile --params '{"userId": "me"}'
```

---

## EXPERT PROTOCOL — every request follows this flow

```
1. DETECT  — identify service (Gmail/Calendar/Drive/etc.) and action type (read/write/delete)
2. ROUTE   — use Capability Map to load the right reference file
3. CONFIRM — state exactly what will happen ("I'll send an email to X with subject Y")
4. APPROVE — wait for user yes before any write/delete/send
5. EXECUTE — run gws CLI commands
6. REPORT  — output in Output Structure format (see below)
```

**Execution Priority** (use highest available, fall back in order):

| Priority | Method | When |
|----------|--------|------|
| 1 | `gws` helper commands (`+send`, `+insert`, `+read`, `+append`) | Always try first |
| 2 | `gws` raw API (`gws gmail users messages list`) | Helper doesn't exist |
| 3 | `gws schema` to discover params, then raw API | Unfamiliar operation |
| Fallback | Python SDK scripts in `skills/google-workspace/scripts/` | gws unavailable |

---

## CAPABILITY MAP — auto-routes requests to the right reference

| Domain | Trigger keywords | Reference |
|--------|-----------------|-----------|
| Email | "send email", "draft", "gmail", "inbox", "unread", "label", "filter", "attachment", "forward" | recipes-email.md |
| Scheduling | "schedule", "meeting", "calendar", "free time", "focus block", "recurring", "agenda", "event" | recipes-scheduling.md |
| Files | "drive", "upload", "share file", "download", "folder", "move", "permissions" | recipes-drive.md |
| Sheets | "spreadsheet", "sheet", "row", "column", "append", "export csv", "formula" | recipes-sheets.md |
| Documents | "google doc", "write", "presentation", "slides", "template", "proposal" | recipes-docs.md |
| Forms/Tasks | "form", "feedback", "survey", "task list", "todo", "overdue" | recipes-forms-tasks.md |
| Operations | "post-mortem", "classroom", "meet participants", "audit", "report" | recipes-operations.md |
| Rate limits | "quota", "limit", "too many requests", "how many", "is there a limit" | quota-limits.md |
| Auth errors | "permission denied", "unauthorized", "scope", "403", "401", "invalid grant", "not working" | error-handling.md |
| Full API | "all methods", "API schema", "how does X work", unfamiliar resource | services.md |

---

## Services

| Service | CLI Name | Coverage |
|---------|----------|----------|
| Gmail | `gmail` | Read, send, search, labels, filters, drafts, threads, watch |
| Google Calendar | `calendar` | Events, free/busy, recurring, invites, calendars |
| Google Drive | `drive` | Files, folders, shared drives, permissions, downloads, upload |
| Google Docs | `docs` | Create, read, write, batch update documents |
| Google Sheets | `sheets` | Create, read, append, batch update spreadsheets |
| Google Slides | `slides` | Create, read, update presentations |
| Google Tasks | `tasks` | Task lists, tasks, due dates, completion |
| Google Chat | `chat` | Spaces, messages, members, custom emoji |
| Google Meet | `meet` | Conference records, spaces, participants, recordings |
| Google Forms | `forms` | Create forms, questions, collect responses, watches |
| Google Keep | `keep` | Create, read, delete notes and labels |
| Google People | `people` | Contacts, contact groups, directory people |
| Admin Reports | `admin` | Activity logs, usage reports, audit trails |

Load [references/services.md](references/services.md) for per-service API resources and example commands.

---

## Common Operations

### Gmail
```bash
# Read inbox summary
gws gmail +triage

# Send email
gws gmail +send --to "recipient@example.com" --subject "Subject" --body "Body text"

# Search messages
gws gmail users messages list --params '{"userId":"me","q":"is:unread from:someone@example.com"}'

# Get message content
gws gmail users messages get --params '{"userId":"me","id":"MESSAGE_ID","format":"full"}'

# Create label
gws gmail users labels create --params '{"userId":"me"}' --json '{"name":"MyLabel"}'
```

### Calendar
```bash
# Today's agenda
gws calendar +agenda

# Create event
gws calendar +insert --summary "Meeting" --start "2026-03-10T10:00:00" --end "2026-03-10T11:00:00"

# Check free/busy (dynamic dates)
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
END=$(date -u -v+8H +%Y-%m-%dT%H:%M:%SZ)
gws calendar freebusy query --json '{"timeMin":"'"$NOW"'","timeMax":"'"$END"'","items":[{"id":"yasmine@smarterflo.com"}]}'

# List upcoming events
gws calendar events list --params '{"calendarId":"primary","maxResults":10,"orderBy":"startTime","singleEvents":true,"timeMin":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'
```

### Drive
```bash
# List files
gws drive files list --params '{"pageSize":20}'

# Upload file
gws drive +upload --file "/path/to/file.pdf" --name "filename.pdf" --folder "FOLDER_ID"

# Share file
gws drive permissions create --params '{"fileId":"FILE_ID"}' --json '{"role":"writer","type":"user","emailAddress":"user@example.com"}'

# Find large files
gws drive files list --params '{"orderBy":"quotaBytesUsed desc","pageSize":10,"fields":"files(id,name,size,mimeType)"}'
```

### Docs
```bash
# Create document
gws docs documents create --json '{"title":"Document Title"}'

# Get document content
gws docs documents get --params '{"documentId":"DOC_ID"}'

# Write to document
gws docs +write --doc-id "DOC_ID" --content "Text to insert"
```

### Sheets
```bash
# Read sheet values
gws sheets +read --spreadsheet-id "SHEET_ID" --range "Sheet1!A1:Z100"

# Append rows
gws sheets +append --spreadsheet-id "SHEET_ID" --range "Sheet1" --json '[["val1","val2","val3"]]'

# Create spreadsheet
gws sheets spreadsheets create --json '{"properties":{"title":"My Spreadsheet"}}'
```

### Slides
```bash
# Create presentation
gws slides presentations create --json '{"title":"Presentation Title"}'

# Get presentation
gws slides presentations get --params '{"presentationId":"PRESENTATION_ID"}'
```

### Tasks
```bash
# List task lists
gws tasks tasklists list

# Create task
gws tasks tasks insert --params '{"tasklist":"@default"}' --json '{"title":"Task title","due":"2026-03-15T00:00:00.000Z","notes":"Details here"}'

# List overdue tasks
gws tasks tasks list --params '{"tasklist":"@default","showCompleted":"false","dueMax":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}'
```

### Chat
```bash
# List spaces
gws chat spaces list

# Send message
gws chat +send --space "spaces/SPACE_ID" --text "Message text"

# List members in space
gws chat spaces members list --params '{"parent":"spaces/SPACE_ID"}'
```

### Meet
```bash
# Create meeting space
gws meet spaces create --json '{"config":{"accessType":"OPEN"}}'

# List conference records
gws meet conferenceRecords list

# List participants
gws meet conferenceRecords participants list --params '{"parent":"conferenceRecords/RECORD_ID"}'
```

### Forms
```bash
# Create form
gws forms forms create --json '{"info":{"title":"Form Title","documentTitle":"Form Doc Title"}}'

# Get form responses
gws forms forms responses list --params '{"formId":"FORM_ID"}'
```

### Keep
```bash
# Create note
gws keep notes create --json '{"body":{"text":{"text":"Note content"}}}'

# List notes
gws keep notes list --params '{"pageSize":20}'
```

### People
```bash
# List contacts
gws people people connections list --params '{"resourceName":"people/me","pageSize":50,"personFields":"names,emailAddresses,phoneNumbers"}'

# Create contact
gws people people createContact --json '{"names":[{"givenName":"First","familyName":"Last"}],"emailAddresses":[{"value":"email@example.com"}]}'
```

### Admin Reports
```bash
# List login activity
gws admin activities list --params '{"userKey":"all","applicationName":"login","maxResults":10}'

# Get user usage report
gws admin userUsageReport get --params '{"userKey":"yasmine@smarterflo.com","date":"'$(date -u -v-1d +%Y-%m-%d)'"}'
```

---

## EXPERT PRINCIPLES — embedded decision rules

```
1.  Email = individuals. Chat = groups. Sending to 3+ people → prefer Chat space + email copy.
2.  Always show recipients, subject, body before sending. You can't un-send Gmail.
3.  Drive sharing is permanent until explicitly unshared. Confirm permissions scope before creating.
4.  Recurring event edits: ask "this event only, or all future events?" before patching.
5.  Batch operations (bulk label, bulk delete, bulk share): --dry-run first, always.
6.  Quota enforcement is silent. Before bulk ops, check quota via Admin Reports.
7.  Timestamp formats: RFC3339 for Calendar API, ISO8601 for Sheets, epoch ms for Gmail settings.
8.  Service account delegation scope: can only impersonate users in the Smarterflo workspace.
9.  When IDs are needed, extract them via jq before the next step. Never guess IDs.
10. If a command returns empty, check pagination. Try --page-all before concluding "no results".
```

---

## GUARDRAILS — what this skill will NOT do

```
- Create Google accounts or add users to the workspace (use Google Admin console directly)
- Access other users' private calendars (only shared/public calendars)
- Send email from non-Smarterflo addresses (service account delegates to yasmine@smarterflo.com only)
- Mass-delete emails or files without per-item confirmation
- Create auto-delete filters (only label/archive — safer)
- Export Meet transcripts (requires Cloud Recording + manual download in Meet UI)
- Recursively change permissions on nested Drive folders (one level at a time)
```

---

## Recipes

Pre-built multi-step workflows — load the reference file for full steps.

### Scheduling
| Recipe | Description |
|--------|-------------|
| find-free-time | Find overlapping free slots across calendars and schedule a meeting |
| schedule-recurring-event | Create a recurring event with attendees and verify with agenda |
| reschedule-meeting | Find an event and move it to a new time, notifying attendees |
| batch-invite-to-event | Add a list of attendees to an existing calendar event |
| block-focus-time | Create a recurring weekly focus block that shows as busy |
| create-meet-space | Create a Meet space and email the join link to the team |
| plan-weekly-schedule | Check agenda, query free/busy, and fill in the week |

### Email
| Recipe | Description |
|--------|-------------|
| create-gmail-filter | Create a label and filter to auto-sort incoming email |
| label-and-archive-emails | Bulk-label and archive messages matching a search query |
| forward-labeled-emails | Forward all messages with a given label to another address |
| save-email-to-doc | Save an email's content to a new Google Doc |
| save-email-attachments | Download email attachments and upload them to Drive |
| draft-email-from-doc | Create a draft email using content from a Google Doc |
| create-vacation-responder | Enable auto-reply with custom message and date range |
| send-team-announcement | Send an email and post the same message to a Chat space |
| email-drive-link | Share a Drive file and email the link to a recipient |

### Drive
| Recipe | Description |
|--------|-------------|
| bulk-download-folder | Download all files in a Drive folder (exports Docs as PDF) |
| create-shared-drive | Create a shared drive and add team members with roles |
| share-folder-with-team | Share a folder with multiple editors and viewers |
| share-doc-and-notify | Share a doc with collaborators and email them the link |
| organize-drive-folder | Create project folder structure and move files into it |
| watch-drive-changes | Subscribe to Drive change events and renew before expiry |
| find-large-files | List files consuming the most Drive quota |
| share-event-materials | Share a file with all attendees of a calendar event |

### Sheets
| Recipe | Description |
|--------|-------------|
| backup-sheet-as-csv | Export a spreadsheet tab to CSV |
| compare-sheet-tabs | Read two tabs and identify rows that differ |
| copy-sheet-for-new-month | Copy a sheet tab and rename it for the current month |
| create-expense-tracker | Create a sheet with headers, sample entries, and share it |
| create-events-from-sheet | Read event rows from a sheet and create calendar events |
| generate-report-from-sheet | Read sheet data, create a Doc report, and share it |
| log-deal-update | Append a new deal row to a tracking spreadsheet |
| sync-contacts-to-sheet | Export Google directory contacts into a sheet |

### Documents
| Recipe | Description |
|--------|-------------|
| create-doc-from-template | Copy a template Drive file and populate it with content |
| create-presentation | Create a new Slides presentation and share it |

### Forms & Tasks
| Recipe | Description |
|--------|-------------|
| collect-form-responses | Retrieve and display all responses from a form |
| create-feedback-form | Create a feedback form and email the link to attendees |
| create-task-list | Create a task list with tasks, notes, and due dates |
| review-overdue-tasks | List all incomplete tasks past their due date |

### Operations
| Recipe | Description |
|--------|-------------|
| post-mortem-setup | Create a post-mortem doc, schedule a review meeting, and notify in Chat |
| log-deal-update | Append a deal update row to a tracking sheet |
| create-classroom-course | Create a Classroom course, invite students, and list enrolled |
| review-meet-participants | List Meet conference records and participant sessions |

---

## OUTPUT STRUCTURE — report every operation in this format

```
Operation: [what was done — "Email sent to X with subject Y"]
Result:    [success / partial / failed]
Details:   [IDs, timestamps, links — "Event ID: abc123, Calendar link: ..."]
Links:     [webViewLink for Docs/Drive, Calendar event URL, Meet join link if created]
Next:      [follow-up needed — "Check spam folder", "Share link with team", or "None"]
```

---

## MEMORY PROTOCOL — persist workspace context via claude-mem

| What | Key | Value |
|------|-----|-------|
| Primary workspace | gws.primary_workspace | "yasmine@smarterflo.com" |
| Preferred calendar | gws.primary_calendar | "primary" (or calendar ID if customized) |
| Known label names | gws.gmail_labels | ["Clients", "Content", ...] — update when created |
| Shared Drive IDs | gws.shared_drives | {"name": "drive_id", ...} — update when discovered |
| Recent operation | gws.last_operation | {timestamp, service, action, result} |

---

## Security

- **Confirm before write/delete.** Always show the user what will be changed.
- **Use `--dry-run`** for destructive or bulk operations.
- **Use `--sanitize <TEMPLATE>`** when processing external content through Model Armor.
- Never output credentials or tokens.
- Service account key: `chmod 600 /Users/yasmineseidu/coding/google.json`

---

## References

Load on demand — do not preload.

| File | Load when |
|------|-----------|
| [references/auth.md](references/auth.md) | Auth errors, scope issues, delegation setup |
| [references/cli.md](references/cli.md) | Unfamiliar flags, `gws schema`, pagination, format options |
| [references/services.md](references/services.md) | Need all API resources/methods for a service |
| [references/recipes-scheduling.md](references/recipes-scheduling.md) | Full steps for any scheduling recipe (7 recipes) |
| [references/recipes-email.md](references/recipes-email.md) | Full steps for any email/Gmail recipe (9 recipes) |
| [references/recipes-drive.md](references/recipes-drive.md) | Full steps for any Drive/file recipe (8 recipes) |
| [references/recipes-sheets.md](references/recipes-sheets.md) | Full steps for any Sheets/spreadsheet recipe (7 recipes) |
| [references/recipes-docs.md](references/recipes-docs.md) | Full steps for doc/presentation recipes (2 recipes) |
| [references/recipes-forms-tasks.md](references/recipes-forms-tasks.md) | Full steps for Forms and Tasks recipes (4 recipes) |
| [references/recipes-operations.md](references/recipes-operations.md) | Full steps for operations recipes (3 recipes) |
| [references/quota-limits.md](references/quota-limits.md) | Quota limits, bulk op safety, "how many" questions |
| [references/error-handling.md](references/error-handling.md) | Any API error, 401/403/429, gws CLI issues, auth failures |
