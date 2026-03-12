# Neon PostgreSQL Skill

**Production-ready skill for Neon serverless PostgreSQL database**

Comprehensive tooling for Neon's Management API, Data API, and direct SQL access.

---

## Quick Start

### 1. Setup Environment Variables

Add to `~/shared/.env`:

```bash
# Neon Management API
NEON_API_KEY=neon_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Neon Data API (get from Neon Console → Data API page)
NEON_DATA_API_URL=https://ep-xxx.apirest.us-east-1.aws.neon.tech/neondb/rest/v1
NEON_JWT_TOKEN=your_jwt_token_here

# Neon Auth (if using Neon Auth)
NEON_AUTH_URL=https://ep-xxx.neonauth.us-east-1.aws.neon.tech/neondb/auth

# Direct SQL Connection (get from Neon Console → Connection Details)
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/neondb?sslmode=require

# For Management API operations
NEON_PROJECT_ID=your-project-id
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Make Scripts Executable

```bash
chmod +x scripts/*.py
```

---

## Scripts

### query.py - Data API Queries

```bash
# Select all published posts
python scripts/query.py posts --filter "is_published=eq.true" --order "created_at.desc"

# Insert a post
python scripts/query.py posts --insert --data '{"content": "Hello", "is_published": false}'

# Update a post
python scripts/query.py posts --update --filter "id=eq.1" --data '{"is_published": true}'

# Delete a post
python scripts/query.py posts --delete --filter "id=eq.1"

# Call stored procedure
python scripts/query.py --rpc get_user_stats --data '{"user_id": "123"}'
```

### execute.py - Direct SQL

```bash
# Run a query
python scripts/execute.py "SELECT * FROM posts WHERE is_published = true"

# Query with parameters (safe from SQL injection)
python scripts/execute.py "SELECT * FROM posts WHERE user_id = %s" --params '["user-123"]'

# Run migration file
python scripts/execute.py --file migrations/001_initial_schema.sql
```

### manage.py - Neon Management API

```bash
# List all projects
python scripts/manage.py list-projects

# Create a branch
python scripts/manage.py create-branch --project-id PROJECT_ID --name dev-feature --parent main

# Get connection string
python scripts/manage.py get-connection-string --project-id PROJECT_ID --branch main

# Delete a branch
python scripts/manage.py delete-branch --project-id PROJECT_ID --branch-id BRANCH_ID
```

---

## Documentation

- **[SKILL.md](./SKILL.md)** - Complete usage guide (25KB, comprehensive)
- **[examples/](./examples/)** - Real-world code examples
- **[examples/migrations/](./examples/migrations/)** - Database migration examples

---

## Examples

### CRUD Operations

See `examples/crud_operations.py` for:
- Data API CRUD
- Direct SQL CRUD
- Bulk inserts
- Complex queries
- Transactions
- Connection pooling
- Error handling

### Row-Level Security (RLS)

See `examples/rls_setup.sql` for:
- Basic RLS patterns
- Team-based access
- Time-based access
- Role-based access (RBAC)
- Conditional visibility
- Soft delete with RLS
- Testing and debugging

### Migrations

See `examples/migrations/` for:
- 001_initial_schema.sql - Users, posts, comments with RLS
- 002_add_tags.sql - Tags system with many-to-many
- 003_add_analytics.sql - Views, likes, and statistics

### Integration Patterns

See `examples/integration_patterns.py` for:
- API endpoint patterns
- Background workers
- Webhook handlers
- Real-time change data capture (CDC)
- Multi-tenancy with branches
- Connection pool management
- ETL pipelines

### n8n Workflow

See `examples/n8n_workflow.json` for:
- Data API integration
- Management API automation
- Scheduled statistics refresh
- Branch creation/deletion

---

## Architecture

```
neon/
├── SKILL.md                      # Complete usage guide (25KB)
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── scripts/
│   ├── query.py                  # Data API queries (CRUD)
│   ├── execute.py                # Direct SQL execution
│   └── manage.py                 # Management API operations
└── examples/
    ├── crud_operations.py        # CRUD examples
    ├── rls_setup.sql             # RLS policy patterns
    ├── integration_patterns.py   # Real-world integrations
    ├── n8n_workflow.json         # n8n automation
    └── migrations/
        ├── 001_initial_schema.sql
        ├── 002_add_tags.sql
        └── 003_add_analytics.sql
```

---

## When to Use What

| Need | Tool | Why |
|------|------|-----|
| **Frontend queries** | Data API | JWT auth, RLS enforcement, no connection management |
| **Complex SQL** | Direct SQL | Full PostgreSQL features, transactions, performance |
| **Manage infrastructure** | Management API | Create branches, projects, get connection strings |
| **Migrations** | Direct SQL | Schema changes, data transformations |
| **Background jobs** | Direct SQL | Connection pooling, batch operations |
| **Real-time updates** | Direct SQL + NOTIFY/LISTEN | Change data capture |

---

## Best Practices

1. **Always enable RLS** on user-facing tables
2. **Use parameterized queries** to prevent SQL injection
3. **Refresh schema cache** after schema changes (Data API)
4. **Use connection pooling** for backend services
5. **Test RLS policies** with `SET LOCAL request.jwt.claims`
6. **Use branches** for dev/staging/testing
7. **Monitor rate limits** and implement backoff
8. **Never commit secrets** - use environment variables

---

## Rate Limits

- **Management API**: ~100 requests/minute
- **Data API**: Depends on compute size
- **Direct SQL**: Connection limits based on compute

Always implement exponential backoff for retries.

---

## Security Notes

1. **JWT tokens** must include `sub` claim for RLS
2. **Connection strings** contain credentials - never commit to git
3. **RLS policies** are enforced at database level (Data API)
4. **Management API keys** have full access - rotate regularly
5. **Use HTTPS** for all API calls

---

## Troubleshooting

### Schema cache not updating

```bash
# Refresh via console or:
curl -X PATCH "https://console.neon.tech/api/v2/projects/$PROJECT_ID/branches/$BRANCH_ID/data-api/$DATABASE" \
  -H "Authorization: Bearer $NEON_API_KEY" -d '{}'
```

### RLS blocking queries

```sql
-- Check policies
SELECT * FROM pg_policies WHERE tablename = 'your_table';

-- Test as user
SET LOCAL request.jwt.claims TO '{"sub": "user-123"}';
SELECT * FROM your_table;
RESET request.jwt.claims;
```

### Connection pool exhausted

```python
# Use connection pooling
from psycopg2 import pool
connection_pool = pool.SimpleConnectionPool(1, 10, dsn=DATABASE_URL)
```

---

## Additional Resources

- [Neon Documentation](https://neon.com/docs)
- [Neon API Reference](https://api-docs.neon.tech/reference/getting-started-with-neon-api)
- [PostgREST Documentation](https://postgrest.org/en/stable/)
- [PostgreSQL RLS Guide](https://neon.com/postgresql/postgresql-administration/postgresql-row-level-security)

---

## Support

For issues or questions:
1. Check SKILL.md for detailed documentation
2. Review examples/ for patterns
3. Consult Neon documentation
4. Contact Omar (Automation Specialist)

---

**Version**: 1.0  
**Created**: 2026-02-23  
**Maintainer**: Omar (Automation Specialist)  
**Status**: Production Ready ✅
