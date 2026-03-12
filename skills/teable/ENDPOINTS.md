# Teable API - Complete Endpoint Reference

Comprehensive list of all Teable API endpoints covered by this skill.

---

## ✅ Records (CRUD) — Core Operations

| Method | Endpoint | Description | CLI | Python |
|--------|----------|-------------|-----|--------|
| GET | `/api/table/{tableId}/record` | List records | `get_records.py` | `client.get_records()` |
| GET | `/api/table/{tableId}/record/{recordId}` | Get single record | `get_records.py` | `client.get_record()` |
| POST | `/api/table/{tableId}/record` | Create records | `create_records.py` | `client.create_records()` |
| PATCH | `/api/table/{tableId}/record/{recordId}` | Update record | `update_records.py` | `client.update_record()` |
| PATCH | `/api/table/{tableId}/record` | Update multiple | `update_records.py` | `client.update_records()` |
| DELETE | `/api/table/{tableId}/record` | Delete records | `delete_records.py` | `client.delete_records()` |

**Features:**
- Filtering (complex JSON filters with AND/OR)
- Sorting (multi-field)
- Pagination (take/skip, max 1000 per request)
- Field projection (select specific fields)
- Typecast (auto-convert field values)
- View-based queries

---

## ✅ Fields — Schema Management

| Method | Endpoint | Description | CLI | Python |
|--------|----------|-------------|-----|--------|
| GET | `/api/table/{tableId}/field` | List fields | `fields.py list` | `extended_client.list_fields()` |
| GET | `/api/table/{tableId}/field/{fieldId}` | Get field | `fields.py get` | `extended_client.get_field()` |
| POST | `/api/table/{tableId}/field` | Create field | `fields.py create` | `extended_client.create_field()` |
| PATCH | `/api/table/{tableId}/field/{fieldId}` | Update field | `fields.py update` | `extended_client.update_field()` |
| PUT | `/api/table/{tableId}/field/{fieldId}/convert` | Convert type | `fields.py convert` | `extended_client.convert_field()` |
| DELETE | `/api/table/{tableId}/field/{fieldId}` | Delete field | `fields.py delete` | `extended_client.delete_field()` |
| POST | `/api/table/{tableId}/field/{fieldId}/duplicate` | Duplicate field | `fields.py duplicate` | `extended_client.duplicate_field()` |

**Field Types Supported:**
- singleLineText, longText
- number, rating, percent, currency, duration
- singleSelect, multipleSelect
- checkbox, date, createdTime, lastModifiedTime
- link (to another record), rollup, lookup, formula
- attachment, user, autoNumber

---

## ✅ Views — Display Configuration

| Method | Endpoint | Description | Python |
|--------|----------|-------------|--------|
| GET | `/api/table/{tableId}/view` | List views | `extended_client.list_views()` |
| GET | `/api/table/{tableId}/view/{viewId}` | Get view | `extended_client.get_view()` |
| POST | `/api/table/{tableId}/view` | Create view | `extended_client.create_view()` |
| PATCH | `/api/table/{tableId}/view/{viewId}` | Update view | `extended_client.update_view()` |
| DELETE | `/api/table/{tableId}/view/{viewId}` | Delete view | `extended_client.delete_view()` |

**View Types:**
- grid (spreadsheet)
- form (data entry)
- kanban (board)
- gallery (cards)
- calendar (timeline)

**View Configuration:**
- Filter (same as record queries)
- Sort (multi-field ordering)
- Group (by field values)
- Hidden fields
- Field order/width

---

## ✅ Comments — Collaboration

| Method | Endpoint | Description | CLI | Python |
|--------|----------|-------------|-----|--------|
| GET | `/comment/{tableId}/{recordId}/list` | List comments | `comments.py list` | `extended_client.list_comments()` |
| GET | `/comment/{commentId}` | Get comment | `comments.py get` | `extended_client.get_comment()` |
| POST | `/comment/{tableId}/{recordId}/create` | Create comment | `comments.py create` | `extended_client.create_comment()` |
| PATCH | `/comment/{commentId}` | Update comment | `comments.py update` | `extended_client.update_comment()` |
| DELETE | `/comment/{commentId}` | Delete comment | `comments.py delete` | `extended_client.delete_comment()` |

**Features:**
- Markdown support in comments
- @mentions (user references)
- Timestamps (created/updated)
- Author tracking

---

## ✅ Attachments — File Management

| Method | Endpoint | Description | Python |
|--------|----------|-------------|--------|
| POST | `/api/table/{tableId}/record/{recordId}/attachments` | Upload file | `extended_client.upload_attachment()` |

**Supported:**
- Upload from URL
- Multiple attachments per record
- File metadata (name, size, type, URL)

**File Types:**
- Images (jpg, png, gif, svg)
- Documents (pdf, doc, xls, ppt)
- Archives (zip, tar)
- Any file type (with mime type)

---

## ✅ SQL Queries — Direct Database Access

| Method | Endpoint | Description | CLI | Python |
|--------|----------|-------------|-----|--------|
| POST | `/api/base/{baseId}/sql-query` | Execute SQL | `sql_query.py` | `extended_client.sql_query()` |

**Capabilities:**
- SELECT queries (read-only)
- JOINs across tables
- Aggregations (SUM, AVG, COUNT, etc.)
- GROUP BY, ORDER BY
- WHERE conditions
- LIMIT/OFFSET

**Example:**
```sql
SELECT 
  assigned_to,
  COUNT(*) as task_count,
  SUM(CASE WHEN status = 'Done' THEN 1 ELSE 0 END) as completed
FROM tasks
WHERE created_at > '2026-02-01'
GROUP BY assigned_to
ORDER BY task_count DESC
```

---

## ✅ Aggregations — Statistics

| Method | Endpoint | Description | Python |
|--------|----------|-------------|--------|
| GET | `/api/table/{tableId}/aggregation` | Get aggregation | `extended_client.get_aggregation()` |
| GET | `/aggregation/{tableId}/{viewId}/row-count` | Row count | `extended_client.get_row_count()` |
| GET | `/aggregation/{tableId}/{viewId}/group-points` | Group stats | `extended_client.get_group_points()` |

**Aggregation Functions:**
- sum, avg, min, max
- count, countEmpty, countNonEmpty
- percentEmpty, percentNonEmpty
- earliest, latest (for dates)

**Use Cases:**
- Total pipeline value
- Average task completion time
- Record counts by status
- Team workload distribution

---

## ✅ Bases & Tables — Structure

| Method | Endpoint | Description | Python |
|--------|----------|-------------|--------|
| GET | `/api/space/{spaceId}/base` | List bases | `extended_client.list_bases()` |
| GET | `/api/base/{baseId}` | Get base | `extended_client.get_base()` |
| POST | `/api/base/{baseId}/table` | Create table | `extended_client.create_table()` |
| PATCH | `/api/table/{tableId}` | Update table | `extended_client.update_table()` |
| DELETE | `/api/table/{tableId}` | Delete table | `extended_client.delete_table()` |

**Base Info:**
- Name, description
- Tables list
- Permissions
- Created/modified dates

**Table Management:**
- Create with initial fields
- Update metadata
- Delete (permanent)

---

## ✅ Sharing — Public Access

| Method | Endpoint | Description | Python |
|--------|----------|-------------|--------|
| POST | `/api/share/{tableId}/view` | Create share link | `extended_client.create_share_view()` |
| GET | `/api/share/{shareId}/view` | Get share info | `extended_client.get_share_view()` |
| DELETE | `/api/share/{shareId}` | Delete share | `extended_client.delete_share_view()` |

**Share Features:**
- Password protection (optional)
- Read-only or form submit
- Expiration dates
- Copy/embed options
- View-specific (filter/sort preserved)

**Use Cases:**
- Client portals
- Public forms
- Embed in websites
- Team collaboration

---

## 🔄 Coming Soon (Not Yet Implemented)

These endpoints exist in Teable API but aren't in the skill yet:

### Automation Workflows
- Trigger actions on record changes
- Multi-step workflows
- Webhook notifications

### Authority Matrix
- Role-based permissions
- Field-level access control
- Row-level security

### AI Features
- Auto-fill fields with AI
- Smart suggestions
- Data enrichment

### Import/Export
- Bulk CSV/Excel import
- Export entire bases
- Schema migration

### Plugins
- Custom dashboard widgets
- Extensions marketplace
- API integrations

### Advanced
- Record history/versions
- Undo/redo operations
- Trash management
- Audit logs

---

## Summary

**Currently Implemented:**
- ✅ Records (CRUD) — 6 endpoints
- ✅ Fields — 7 endpoints
- ✅ Views — 5 endpoints
- ✅ Comments — 5 endpoints
- ✅ Attachments — 1 endpoint
- ✅ SQL Queries — 1 endpoint
- ✅ Aggregations — 3 endpoints
- ✅ Bases & Tables — 5 endpoints
- ✅ Sharing — 3 endpoints

**Total: 36 endpoints covered**

**Coverage:** ~40% of total Teable API
**Focus:** Most useful operations for task management and automation

---

**Last updated:** 2026-02-24
**Skill version:** 1.1.0 (Extended)
