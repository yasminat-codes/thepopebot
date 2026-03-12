Teable Skill - Quick Start
===========================

Complete Teable integration for OpenClaw agents.

## Setup (5 minutes)

### 1. Get API Token

Visit: https://app.teable.ai/setting/personal-access-token

- Click "Create Token"
- Add scopes: `table:read`, `table:write`, `record:read`, `record:write`
- Copy token (shown once!)

### 2. Configure

Add to `/home/clawdbot/shared/.env`:

```bash
TEABLE_API_TOKEN=your_token_here
TEABLE_BASE_URL=https://app.teable.ai
```

### 3. Get Table ID

- Open your table in Teable
- URL: `https://app.teable.ai/base/basXXXX/{tableId}`
- Copy the `tbl...` ID

## Quick Examples

### List tasks

```bash
cd /home/clawdbot/shared/skills/teable/scripts

python3 get_records.py \
  --table-id tblYOUR_TABLE_ID \
  --take 10 \
  --compact
```

### Create task

```bash
python3 create_records.py \
  --table-id tblYOUR_TABLE_ID \
  --records '[{"fields":{"Title":"Test task","Status":"Open"}}]' \
  --typecast
```

### Update task status

```bash
python3 update_records.py \
  --table-id tblYOUR_TABLE_ID \
  --record-id recXXXXXXXXXXXXXX \
  --fields '{"Status":"Done"}' \
  --typecast
```

### Filter by status

```bash
python3 get_records.py \
  --table-id tblYOUR_TABLE_ID \
  --filter '{"conjunction":"and","conditions":[{"fieldId":"fldStatus","operator":"is","value":"Open"}]}'
```

## Python Integration

```python
from common import client

# Get my tasks
tasks = client.get_records(
    table_id="tblYOUR_TABLE_ID",
    filter_obj={
        "conjunction": "and",
        "conditions": [
            {"fieldId": "fldAssignedTo", "operator": "is", "value": "Aaliyah"},
            {"fieldId": "fldStatus", "operator": "isNot", "value": "Done"}
        ]
    }
)

# Create task
client.create_records(
    table_id="tblYOUR_TABLE_ID",
    records=[{
        "fields": {
            "Title": "New task",
            "Status": "Open",
            "Priority": 3
        }
    }],
    typecast=True
)

# Update status
client.update_record(
    table_id="tblYOUR_TABLE_ID",
    record_id="recXXXXXXXXXXXXXX",
    fields={"Status": "Done"},
    typecast=True
)
```

## Next Steps

1. Read SKILL.md for full documentation
2. Set up your Tasks table in Teable
3. Test with the examples above
4. Integrate into agent workflows

## Extended Operations

### Field Management

```bash
# List fields
python3 scripts/fields.py list --table-id tblXXX

# Create field
python3 scripts/fields.py create \
  --table-id tblXXX \
  --name "Priority" \
  --type "number"

# Update field
python3 scripts/fields.py update \
  --table-id tblXXX \
  --field-id fldYYY \
  --name "New Name"
```

### SQL Queries

```bash
# Direct SQL access
python3 scripts/sql_query.py \
  --base-id basXXX \
  --sql "SELECT * FROM tasks WHERE status = 'Open'" \
  --format table
```

### Comments

```bash
# Add comment to record
python3 scripts/comments.py create \
  --table-id tblXXX \
  --record-id recYYY \
  --content "Task completed successfully"

# List comments
python3 scripts/comments.py list \
  --table-id tblXXX \
  --record-id recYYY
```

## Files

```
teable/
├── SKILL.md                 # Full documentation
├── README.md                # This file
├── scripts/
│   ├── common.py            # Core API client
│   ├── extended.py          # Extended API client (all endpoints)
│   ├── get_records.py       # List/search records
│   ├── create_records.py    # Create records
│   ├── update_records.py    # Update records
│   ├── delete_records.py    # Delete records
│   ├── fields.py            # Field operations
│   ├── sql_query.py         # SQL queries
│   └── comments.py          # Comment operations
└── examples/
    └── task_management.py   # Integration examples
```

## Support

- Full docs: SKILL.md
- Teable docs: https://help.teable.ai
- API reference: https://help.teable.ai/en/api-doc/overview
