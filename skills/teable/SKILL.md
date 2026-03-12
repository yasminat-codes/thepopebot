---
name: teable
description: >-
  Manage records in Teable (open-source Airtable alternative) via REST API. Use
  PROACTIVELY when user says "teable", "teable record", "teable table", "teable
  base", "teable api", "create teable record", "update teable", "query teable",
  "teable workspace", or "teable database". Use when creating, reading, updating,
  or deleting records in Teable for task management or project tracking.
  Requires TEABLE_API_TOKEN and TEABLE_BASE_URL env vars.
allowed-tools: Read Write Edit Bash Task
argument-hint: "[base-id-or-action] (optional)"
disable-model-invocation: false
user-invocable: true
model: sonnet
license: Proprietary
metadata:
  author: yasmine-seidu
  version: "2.0.0"
  category: project-management
---

# Teable Skill

Comprehensive integration with Teable (Airtable alternative) for task management, project tracking, and team collaboration.

## What is Teable?

Teable is an open-source, PostgreSQL-backed alternative to Airtable with:
- Spreadsheet-like interface
- Multiple views (Grid, Kanban, Calendar, Gallery)
- Real-time collaboration
- Scales to millions of rows
- REST API
- Self-hostable or cloud-hosted

## Use Cases

- **Task Management**: Replace Todoist with Teable tasks
- **Project Tracking**: Kanban boards for pipeline/projects
- **Team Workload**: Visualize agent assignments
- **Client Portal**: Share views with clients
- **Content Calendar**: Schedule posts across platforms
- **CRM**: Track leads, deals, contacts

---

## Setup

### 1. Get API Token

**Cloud (app.teable.ai):**
1. Go to [Token Management](https://app.teable.ai/setting/personal-access-token)
2. Click "Create Token"
3. Set expiration period
4. Add permissions (scopes): `table:read`, `table:write`, `record:read`, `record:write`
5. Specify bases/spaces the token can access
6. Copy token (shown only once!)

**Self-hosted:**
Same process at your domain: `https://your-teable.com/setting/personal-access-token`

### 2. Configure Environment

Add to `/home/clawdbot/shared/.env`:

```bash
# Teable Configuration
TEABLE_API_TOKEN=your_personal_access_token_here
TEABLE_BASE_URL=https://app.teable.ai  # or your self-hosted domain
```

### 3. Get IDs

You'll need these for API calls:

**Base ID** (starts with `bas`):
- Open your base in Teable
- URL: `https://app.teable.ai/base/{baseId}/...`

**Table ID** (starts with `tbl`):
- Open table view
- URL: `https://app.teable.ai/base/{baseId}/{tableId}`

**View ID** (starts with `viw`):
- Click on a view (Grid/Kanban/Calendar)
- URL includes: `/view/{viewId}`

**Field ID** (starts with `fld`):
- Hover over field column header
- Click "..." → "Copy field ID"

**Record ID** (starts with `rec`):
- Right-click on a record row
- "Copy record ID"

---

## Core Functions (Records)

### Get Records (List/Search)

```bash
python3 scripts/get_records.py \
  --table-id tblXXXXXXXXXXXXXX \
  --view-id viwYYYYYYYYYYYYYY \
  --filter '{"conjunction":"and","conditions":[{"fieldId":"fldZZZ","operator":"is","value":"Open"}]}' \
  --take 100
```

**Use cases:**
- List all tasks assigned to an agent
- Search for overdue tasks
- Get tasks by status (Open, In Progress, Done)
- Filter by priority, project, or custom fields

### Create Records (Add Tasks/Items)

```bash
python3 scripts/create_records.py \
  --table-id tblXXXXXXXXXXXXXX \
  --records '[{"fields":{"Title":"New task","Status":"Open","Assigned To":"Qamar","Priority":3}}]' \
  --typecast
```

**Use cases:**
- Create task when delegating to agent
- Add new lead to pipeline
- Log client interaction
- Create project milestone

### Update Records (Edit/Status Change)

```bash
python3 scripts/update_records.py \
  --table-id tblXXXXXXXXXXXXXX \
  --record-id recAAAAAAAAAAAAA \
  --fields '{"Status":"Done","Completed At":"2026-02-24T10:30:00Z"}' \
  --typecast
```

**Use cases:**
- Mark task as complete
- Update task status (In Progress, Blocked, Done)
- Change assignee
- Add notes/comments to record

### Delete Records (Remove Items)

```bash
python3 scripts/delete_records.py \
  --table-id tblXXXXXXXXXXXXXX \
  --record-ids recAAAAAAAAAAAAA recBBBBBBBBBBBBB
```

**Use cases:**
- Delete completed/archived tasks
- Remove duplicate records
- Clean up test data

---

## Extended Functions (All Endpoints)

### Field Operations

**Manage table fields (columns) programmatically:**

```bash
# List all fields in a table
python3 scripts/fields.py list --table-id tblXXX

# Create a new field
python3 scripts/fields.py create \
  --table-id tblXXX \
  --name "Priority" \
  --type "singleSelect" \
  --options '{"choices": [{"name": "Low"}, {"name": "High"}]}'

# Update field name
python3 scripts/fields.py update \
  --table-id tblXXX \
  --field-id fldYYY \
  --name "New Name"

# Convert field type
python3 scripts/fields.py convert \
  --table-id tblXXX \
  --field-id fldYYY \
  --type "multipleSelect"

# Duplicate field
python3 scripts/fields.py duplicate \
  --table-id tblXXX \
  --field-id fldYYY

# Delete field
python3 scripts/fields.py delete \
  --table-id tblXXX \
  --field-id fldYYY
```

**Use cases:**
- Auto-create fields for new projects
- Standardize schemas across tables
- Migrate field types (number → rating, text → select)
- Clone field configurations

### View Operations

**Manage views (Grid, Kanban, Calendar, etc.):**

```python
from extended import extended_client as client

# List all views
views = client.list_views(table_id="tblXXX")

# Create Kanban view
kanban_view = client.create_view(
    table_id="tblXXX",
    name="Pipeline Kanban",
    view_type="kanban",
    description="Deal stages kanban board"
)

# Update view (add filter/sort/group)
client.update_view(
    table_id="tblXXX",
    view_id="viwYYY",
    filter={
        "conjunction": "and",
        "conditions": [
            {"fieldId": "fldStatus", "operator": "is", "value": "Active"}
        ]
    },
    sort=[{"fieldId": "fldPriority", "order": "desc"}]
)

# Delete view
client.delete_view(table_id="tblXXX", view_id="viwYYY")
```

**Use cases:**
- Create custom views per agent
- Auto-generate filtered views (My Tasks, This Week, High Priority)
- Programmatic Kanban board setup
- Clone view configurations

### Comments

**Add context and notes to records:**

```bash
# List comments on a record
python3 scripts/comments.py list \
  --table-id tblXXX \
  --record-id recYYY

# Add comment
python3 scripts/comments.py create \
  --table-id tblXXX \
  --record-id recYYY \
  --content "Task completed successfully. Next: follow up on Monday."

# Update comment
python3 scripts/comments.py update \
  --comment-id comZZZ \
  --content "Updated: Follow up moved to Wednesday."

# Delete comment
python3 scripts/comments.py delete \
  --comment-id comZZZ
```

**Use cases:**
- Agent collaboration notes
- Task completion details
- Client communication logs
- Delegation handoff notes

### SQL Queries

**Direct SQL access to your data:**

```bash
# Execute SQL query
python3 scripts/sql_query.py \
  --base-id basXXX \
  --sql "SELECT title, status, priority FROM tasks WHERE assigned_to = 'Aaliyah' ORDER BY priority DESC" \
  --format table

# Complex aggregation
python3 scripts/sql_query.py \
  --base-id basXXX \
  --sql "SELECT assigned_to, COUNT(*) as task_count, AVG(priority) as avg_priority FROM tasks WHERE status != 'Done' GROUP BY assigned_to" \
  --format json
```

**Use cases:**
- Complex analytics queries
- Cross-table joins
- Custom aggregations
- Data exports for reporting
- Migration scripts

### Attachments

**Upload files to records:**

```python
from extended import extended_client as client

# Upload from URL
client.upload_attachment(
    table_id="tblXXX",
    record_id="recYYY",
    field_id="fldAttachments",
    url="https://example.com/document.pdf"
)
```

**Use cases:**
- Attach deliverables to tasks
- Link proposals to deals
- Store client files
- Screenshot/log uploads

### Aggregations

**Get statistics without manual calculation:**

```python
from extended import extended_client as client

# Get sum of all deal values
total_revenue = client.get_aggregation(
    table_id="tblDeals",
    view_id="viwActive",
    aggregation_field_id="fldDealValue",
    aggregation_func="sum"
)

# Get row count in view
count = client.get_row_count(
    table_id="tblTasks",
    view_id="viwOverdue"
)

# Get group distribution
groups = client.get_group_points(
    table_id="tblTasks",
    view_id="viwByAgent"
)
```

**Use cases:**
- Real-time pipeline value
- Task completion metrics
- Team workload distribution
- Performance dashboards

### Base & Table Operations

**Create/manage bases and tables:**

```python
from extended import extended_client as client

# List bases in space
bases = client.list_bases(space_id="spcXXX")

# Get base info
base = client.get_base(base_id="basXXX")

# Create new table
new_table = client.create_table(
    base_id="basXXX",
    name="Client Contacts",
    description="CRM contact database"
)

# Update table
client.update_table(
    table_id="tblYYY",
    name="Qualified Leads",
    description="High-intent prospects"
)

# Delete table (careful!)
client.delete_table(table_id="tblYYY")
```

**Use cases:**
- Programmatic base setup
- Template deployment
- Schema migrations
- Multi-tenant table creation

### Sharing

**Create public/protected views:**

```python
from extended import extended_client as client

# Create shareable link
share = client.create_share_view(
    table_id="tblXXX",
    view_id="viwClientPortal",
    password="secure123"  # Optional password
)

# Share URL: share['shareUrl']
print(f"Share link: {share['shareUrl']}")

# Get share info
info = client.get_share_view(share_id=share['id'])

# Delete share
client.delete_share_view(share_id=share['id'])
```

**Use cases:**
- Client portals (read-only project status)
- Public forms (lead capture)
- Team collaboration links
- Embed in websites

---

## Task Management Workflows

### Morning Briefing: Get My Tasks

```python
# Get tasks assigned to current agent
tasks = get_records(
    table_id="tblTasks",
    filter={
        "conjunction": "and",
        "conditions": [
            {"fieldId": "fldAssignedTo", "operator": "is", "value": agent_name},
            {"fieldId": "fldStatus", "operator": "isNot", "value": "Done"}
        ]
    },
    order_by=[{"fieldId": "fldDueDate", "order": "asc"}]
)

# Format for briefing
print(f"TASKS: {len(tasks)} open tasks")
for task in tasks:
    print(f"  - {task['fields']['Title']} (due: {task['fields']['Due Date']})")
```

### Delegation: Create Task

```python
# Agent delegates task to another agent
create_records(
    table_id="tblTasks",
    records=[{
        "fields": {
            "Title": "Launch cold email campaign - Financial services",
            "Description": "Target CFOs at $5M-50M companies...",
            "Assigned To": "Qamar",
            "Priority": 3,  # High
            "Status": "Open",
            "Due Date": "2026-02-27",
            "Project": "Q1 Outreach",
            "Tags": ["cold-email", "financial-services"]
        }
    }],
    typecast=True  # Auto-convert field types
)
```

### Completion: Update Status

```python
# Mark task as done
update_record(
    table_id="tblTasks",
    record_id="recXXXXXXXXXXXXXX",
    fields={
        "Status": "Done",
        "Completed At": datetime.now().isoformat(),
        "Notes": "Campaign launched successfully. 500 emails sent."
    },
    typecast=True
)
```

### Heartbeat: Check Overdue

```python
# Get overdue tasks across all agents
overdue_tasks = get_records(
    table_id="tblTasks",
    filter={
        "conjunction": "and",
        "conditions": [
            {"fieldId": "fldStatus", "operator": "isNot", "value": "Done"},
            {"fieldId": "fldDueDate", "operator": "isBefore", "value": datetime.now().isoformat()}
        ]
    }
)

# Alert for each overdue task
for task in overdue_tasks:
    agent = task['fields']['Assigned To']
    print(f"⚠️ OVERDUE: {task['fields']['Title']} (assigned to {agent})")
```

---

## Schema Examples

### Tasks Table

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Title | Single Line Text | Task name |
| Description | Long Text | Full details |
| Status | Single Select | Open, In Progress, Blocked, Done |
| Priority | Number | 1 (low) to 4 (urgent) |
| Assigned To | Single Select | Agent name |
| Due Date | Date | Deadline |
| Project | Link to Projects | Associated project |
| Tags | Multiple Select | Categories/labels |
| Created At | Created Time | Auto-populated |
| Updated At | Last Modified Time | Auto-tracked |

### Projects Table

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Name | Single Line Text | Project name |
| Description | Long Text | Overview |
| Status | Single Select | Planning, Active, On Hold, Complete |
| Owner | Single Select | Lead agent |
| Start Date | Date | Project start |
| End Date | Date | Target completion |
| Tasks | Link to Tasks | Related tasks |
| Progress | Percent | Completion % |

### Agents Table

| Field Name | Field Type | Description |
|------------|------------|-------------|
| Name | Single Line Text | Agent name |
| Role | Single Select | Domain/specialty |
| Status | Single Select | Active, Away, Offline |
| Current Tasks | Link to Tasks | Assigned tasks |
| Capacity | Number | Max concurrent tasks |
| Workload | Percent | Current utilization |

---

## API Reference

### Base URL

- **Cloud**: `https://app.teable.ai/api`
- **Self-hosted**: `https://your-domain.com/api`

### Authentication

All requests require Bearer token:

```bash
Authorization: Bearer YOUR_TEABLE_API_TOKEN
```

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/table/{tableId}/record` | List records |
| POST | `/table/{tableId}/record` | Create records |
| PATCH | `/table/{tableId}/record/{recordId}` | Update record |
| DELETE | `/table/{tableId}/record` | Delete records |
| GET | `/table/{tableId}/record/{recordId}` | Get single record |

### Query Parameters

**GET /table/{tableId}/record:**
- `viewId`: Filter by view
- `take`: Limit results (max 1000)
- `skip`: Pagination offset
- `filter`: Complex JSON filter
- `orderBy`: Sort specification
- `search`: Text search
- `projection`: Field subset

**POST /table/{tableId}/record:**
- `typecast`: Auto-convert types (boolean)
- `fieldKeyType`: `name` | `id` | `dbFieldName`
- `order`: Position in view

**PATCH /table/{tableId}/record/{recordId}:**
- `typecast`: Auto-convert types (boolean)
- `fieldKeyType`: `name` | `id` | `dbFieldName`

---

## Filter Syntax

### Simple Filter

```json
{
  "conjunction": "and",
  "conditions": [
    {"fieldId": "fldStatus", "operator": "is", "value": "Open"}
  ]
}
```

### Complex Filter

```json
{
  "conjunction": "and",
  "conditions": [
    {"fieldId": "fldStatus", "operator": "isNot", "value": "Done"},
    {"fieldId": "fldPriority", "operator": "isGreater", "value": 2},
    {
      "conjunction": "or",
      "conditions": [
        {"fieldId": "fldAssignedTo", "operator": "is", "value": "Qamar"},
        {"fieldId": "fldAssignedTo", "operator": "is", "value": "Laila"}
      ]
    }
  ]
}
```

### Operators

| Operator | Description | Example Value |
|----------|-------------|---------------|
| `is` | Equals | `"Open"` |
| `isNot` | Not equals | `"Done"` |
| `contains` | Text contains | `"email"` |
| `doesNotContain` | Text doesn't contain | `"spam"` |
| `isEmpty` | Field is empty | `null` |
| `isNotEmpty` | Field has value | `null` |
| `isGreater` | Number > | `2` |
| `isGreaterEqual` | Number >= | `3` |
| `isLess` | Number < | `5` |
| `isLessEqual` | Number <= | `4` |
| `isBefore` | Date before | `"2026-02-24"` |
| `isAfter` | Date after | `"2026-02-20"` |

---

## Error Handling

Common errors and solutions:

| Status | Error | Solution |
|--------|-------|----------|
| 401 | Unauthorized | Check TEABLE_API_TOKEN is valid |
| 403 | Forbidden | Token missing required scope |
| 404 | Not Found | Verify table ID, base ID, record ID |
| 400 | Bad Request | Check JSON syntax, required fields |
| 429 | Rate Limited | Add delay between requests |

---

## Best Practices

### 1. Use Typecast for Flexibility

```python
# Without typecast - must match exact format
create_records(
    records=[{
        "fields": {
            "Due Date": "2026-02-24T10:00:00.000Z",  # Exact ISO format
            "Assigned To": ["usrXXXXXXXX"]  # User ID array
        }
    }]
)

# With typecast - accepts natural input
create_records(
    records=[{
        "fields": {
            "Due Date": "2026-02-24",  # Simple date string
            "Assigned To": "Qamar"  # Name instead of ID
        }
    }],
    typecast=True  # Auto-converts
)
```

### 2. Batch Operations

Create/update multiple records in one request:

```python
create_records(
    records=[
        {"fields": {"Title": "Task 1", "Status": "Open"}},
        {"fields": {"Title": "Task 2", "Status": "Open"}},
        {"fields": {"Title": "Task 3", "Status": "Open"}}
    ]
)
```

### 3. Use Views for Filtering

Instead of complex filters, create views in Teable UI:
- "My Open Tasks" view
- "Overdue Items" view
- "This Week" view

Then fetch by `viewId`:

```python
tasks = get_records(table_id="tblTasks", view_id="viwMyOpenTasks")
```

### 4. Field Key Types

**Use field names** (default) for readability:
```python
{"Title": "New task", "Status": "Open"}
```

**Use field IDs** for stability (names can change):
```python
{"fldABCDEF": "New task", "fldGHIJKL": "Open"}
```

### 5. Pagination

For large datasets:

```python
def get_all_records(table_id, batch_size=1000):
    all_records = []
    skip = 0
    
    while True:
        batch = get_records(table_id, take=batch_size, skip=skip)
        if not batch:
            break
        all_records.extend(batch)
        skip += batch_size
    
    return all_records
```

---

## Integration Examples

### Aaliyah Morning Briefing

```python
# Get Yasmine's tasks for today
today_tasks = get_records(
    table_id=TASKS_TABLE_ID,
    filter={
        "conjunction": "and",
        "conditions": [
            {"fieldId": "fldAssignedTo", "operator": "is", "value": "Yasmine"},
            {"fieldId": "fldDueDate", "operator": "is", "value": datetime.now().date().isoformat()}
        ]
    }
)

# Include in morning briefing
print(f"TASKS: {len(today_tasks)} due today")
for task in today_tasks:
    print(f"  - {task['fields']['Title']} (priority: {task['fields']['Priority']})")
```

### Qamar Creates Campaign Tasks

```python
# When launching cold email campaign, create tracking tasks
campaign_tasks = create_records(
    table_id=TASKS_TABLE_ID,
    records=[
        {"fields": {"Title": "Build lead list", "Assigned To": "Qamar", "Priority": 4, "Due Date": "+1 day"}},
        {"fields": {"Title": "Write email sequences", "Assigned To": "Qamar", "Priority": 4, "Due Date": "+2 days"}},
        {"fields": {"Title": "Set up Instantly campaign", "Assigned To": "Qamar", "Priority": 3, "Due Date": "+3 days"}},
        {"fields": {"Title": "Monitor deliverability", "Assigned To": "Qamar", "Priority": 2, "Due Date": "+5 days"}}
    ],
    typecast=True
)
```

### Jalila Updates Deal Status

```python
# When deal progresses, update in Teable
update_record(
    table_id=DEALS_TABLE_ID,
    record_id=deal_record_id,
    fields={
        "Stage": "Proposal Sent",
        "Proposal Value": 15000,
        "Next Follow-up": "2026-02-26",
        "Notes": "Sent custom proposal for AI automation setup. Follows up Wednesday."
    },
    typecast=True
)
```

---

## Task Management System (v2)

### Overview

The v2 task management system provides a complete task lifecycle for all 16 OpenClaw agents with:
- **6 tables**: Projects, Epics, Tasks, Activity Log, Task Templates, Agents
- **8-state lifecycle** with enforced transitions and permission checks
- **Approval gates**: All completed work goes through Yasmine's review before closing
- **Activity logging**: Every status change, creation, and comment is recorded
- **Dependency tracking**: Tasks can block other tasks, checked before claiming
- **Agent current-task tracking**: Each agent's active task is reflected in the Agents table

### Tables

| Table | Purpose |
|-------|---------|
| **Projects** | Top-level containers grouping related epics and tasks |
| **Epics** | Mid-level groupings within a project (feature sets, milestones) |
| **Tasks** | Individual work items assigned to agents with full lifecycle tracking |
| **Activity Log** | Immutable audit trail of all task actions (status changes, comments, assignments) |
| **Task Templates** | Reusable task definitions for common work types (bootstrap new tasks quickly) |
| **Agents** | Agent roster with current task, capacity, status, and Slack channel info |

### Task Lifecycle

The 8-state lifecycle with enforced transitions:

```
Draft -> Backlog -> Ready -> In Progress -> Needs Review -> Approved -> Done
                      |           |              |
                      v           v              v
                   Blocked    Blocked      In Progress (rejection)
```

| Transition | Who Can Do It | Requirements |
|------------|---------------|--------------|
| Draft -> Backlog | Anyone | -- |
| Backlog -> Ready | Anyone | -- |
| Ready -> In Progress | Assignee only | Dependencies must be Done |
| Ready -> Blocked | System | Auto when deps not met |
| In Progress -> Blocked | Assignee | Reason required |
| In Progress -> Needs Review | Assignee | Completion report required |
| Blocked -> Ready | System | When blockers resolve |
| Blocked -> In Progress | Assignee | -- |
| Needs Review -> Approved | Yasmine only | -- |
| Needs Review -> In Progress | Yasmine only | Rejection with notes |
| Approved -> Done | System or Yasmine | -- |
| Done -> Backlog | Yasmine only | Reopen |

### CLI Quick Reference

The `task_manager.py` module provides the `TaskManager` class. Key methods:

```bash
# Get Ready tasks for an agent (sorted by priority, then age)
python3 -c "
from task_manager import TaskManager
tm = TaskManager()
tasks = tm.get_ready_tasks('Idris')
"

# Claim a task (Ready -> In Progress)
python3 -c "
from task_manager import TaskManager
tm = TaskManager()
tm.start_task('recXXXXXX', 'Idris')
"

# Submit for review (In Progress -> Needs Review)
python3 -c "
from task_manager import TaskManager
tm = TaskManager()
tm.submit_for_review(
    record_id='recXXXXXX',
    agent_name='Idris',
    summary='Built the dashboard component',
    files_changed=['src/dashboard.py'],
    outputs='workspace-idris/output/dashboard-2026-03-06.html',
    follow_ups=['Deploy to staging'],
)
"

# Approve a task (Needs Review -> Approved -> Done) -- Yasmine only
python3 -c "
from task_manager import TaskManager
tm = TaskManager()
tm.approve_task('recXXXXXX', notes='Looks good')
"

# Reject a task (Needs Review -> In Progress) -- Yasmine only
python3 -c "
from task_manager import TaskManager
tm = TaskManager()
tm.reject_task('recXXXXXX', notes='Missing error handling')
"

# Block a task with reason
python3 -c "
from task_manager import TaskManager
tm = TaskManager()
tm.block_task('recXXXXXX', 'Idris', 'Waiting on API credentials')
"

# Check dependencies
python3 -c "
from task_manager import TaskManager
tm = TaskManager()
print(tm.check_dependencies('recXXXXXX'))
"

# Get daily digest (all statuses summary)
python3 -c "
from task_manager import TaskManager
tm = TaskManager()
import json
print(json.dumps(tm.get_daily_digest(), indent=2))
"
```

### Setup

Run the bootstrap script to create all 6 tables with fields, views, and seed data:

```bash
python3 skills/teable/scripts/setup_task_system_v2.py
```

This creates:
- All 6 tables with correct field types and options
- Kanban views per table
- Agent records for all 16 agents
- Starter task templates

**Prerequisites:** `TEABLE_API_TOKEN` and `TEABLE_BASE_URL` must be set. The base must already exist.

### Agent Heartbeat Integration

Every agent runs the shared task runner workflow on each heartbeat:

```
shared/workflows/teable-task-runner.md
```

This workflow handles the full loop: query Ready tasks, check dependencies, claim, execute, submit for review, notify, and log. See the workflow file for the complete 12-step process.

---

## Roadmap

**v1.0** (Complete):
- CRUD operations
- Filtering and sorting
- Batch operations

**v2.0** (Current):
- 6-table task management system (Projects, Epics, Tasks, Activity Log, Templates, Agents)
- 8-state lifecycle with enforced transitions
- Approval gates (Yasmine review)
- Activity logging and audit trail
- Dependency checking
- Agent heartbeat integration
- CLI via TaskManager class
- Bootstrap script for table setup

**v2.1** (Planned):
- File upload to attachment fields
- Webhook support for real-time status updates
- Bulk import/export
- Automated daily digest Slack delivery

---

## Troubleshooting

### "Table not found" error

- Verify table ID starts with `tbl`
- Check token has access to the base
- Ensure base ID is correct

### "Field not found" error

- Field names are case-sensitive
- Use exact field name from Teable
- Or use field IDs instead

### Typecast not working

- Some field types can't auto-convert
- Check field type supports the value
- Use exact format for complex types

### Rate limits

- Cloud: ~100 requests/minute per token
- Self-hosted: No limits (depends on server)
- Add delays for batch operations

---

## Files

```
teable/
├── SKILL.md                        # This documentation
├── config/
│   ├── table_ids.json              # Teable table IDs for all 6 tables
│   └── slack_channels.json         # Agent-to-Slack-channel mapping (all 16 agents)
├── scripts/
│   ├── common.py                   # Shared utilities (TeableClient, filters, etc.)
│   ├── get_records.py              # List/search records
│   ├── create_records.py           # Create new records
│   ├── update_records.py           # Update existing records
│   ├── delete_records.py           # Delete records
│   ├── comments.py                 # Record comments CRUD
│   ├── fields.py                   # Field management
│   ├── extended.py                 # Extended API (views, attachments, sharing)
│   ├── sql_query.py                # Direct SQL queries
│   ├── task_manager.py             # Core task lifecycle module (v2)
│   ├── setup_task_system_v2.py     # Bootstrap script for 6-table system
│   ├── task_cli.py                 # CLI wrapper for task_manager.py
│   ├── daily_digest.py             # Daily digest generator
│   └── seed_templates.py           # Seed task templates
├── examples/
│   └── task_management.py          # Task CRUD examples
└── README.md                       # Quick start guide
```

---

*Teable Skill v2.0 - Built by Aaliyah for OpenClaw*
