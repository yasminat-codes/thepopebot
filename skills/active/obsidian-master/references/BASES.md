# Obsidian Bases — Reference

## 1. What is Obsidian Bases

Released in 2025 as a core Obsidian feature. No plugin required — built into Obsidian itself starting from v1.8+. Bases provides native database-like views powered by frontmatter properties. Think of it as a spreadsheet/table view where each row is a note and each column is a property.

Bases files use the `.base` extension and live in the vault alongside your `.md` notes.

---

## 2. Bases vs Dataview

| Feature | Bases | Dataview |
|---------|-------|---------|
| Setup | Core feature — built in, no install | Community plugin required |
| Syntax | Visual GUI — no code | DQL (Dataview Query Language) or JavaScript |
| Performance | Faster — native indexing | Slower on large vaults (plugin overhead) |
| Flexibility | Lower — set of supported views | High — any query logic expressible in DQL or JS |
| DataviewJS | No JavaScript support | Full JS via `dataviewjs` blocks |
| Formulas | Limited (basic computed fields) | Full expression language |
| Grouping | Visual group-by in GUI | `GROUP BY` clause or JS |
| Aggregation | Basic (count) | Full (sum, average, min, max, any JS) |
| Learning curve | Low — point and click | Medium–High |
| Cross-folder queries | Supported (via filters) | Supported (`FROM` + `OR`) |
| Inline rendering | Not supported | Inline queries via `` `= field` `` |
| Live in reading view | Yes | Yes (renders in preview) |
| Export | No native export | No native export |

---

## 3. When to Use Bases

Use Bases when:
- You want a spreadsheet view of notes without writing code
- Use case is simple: see all items in a folder, filter by one property, sort by a column
- You want a non-technical team member (or future you) to maintain the view
- Speed matters — Bases is measurably faster than Dataview on the same query in large vaults
- You want to edit properties directly in the table (Bases supports inline editing)

---

## 4. When to Use Dataview

Use Dataview when:
- You need multi-folder or multi-tag sources combined
- Query requires computed fields (days until deadline, % complete)
- You need GROUP BY with aggregation (count clients by status)
- You want DataviewJS dashboards with conditional rendering
- Query needs logic: `WHERE status != "completed" AND deadline < date(today)`
- You need inline values rendered inside prose (`= this.status`)
- You're building a business dashboard (client pipeline, content tracker, decision log)

---

## 5. Setting Up a Base

1. Create a new file with the `.base` extension: `Clients.base` in your vault
2. Obsidian opens the Base editor automatically
3. **Set the source**: click "Source" → choose a folder (e.g. `03-Areas/smarterflo/clients`) or a tag (e.g. `#client`)
4. **Configure columns**: each column maps to a frontmatter property
   - Click "+" to add a column
   - Select the property name (auto-suggested from your vault's properties)
   - Set the column type: Text, Number, Date, Checkbox, List, Link
5. **Add filters**: click "Filter" → choose property → set condition and value
6. **Sort**: click any column header to sort ascending/descending
7. **Group by**: click "Group" → choose a property (e.g. group clients by `status`)

Bases auto-saves and re-renders when notes are created or modified.

---

## 6. Bases Formula Syntax

Bases supports a limited set of computed columns using formula syntax. Add a formula column in the Base editor.

```
# Simple field reference
prop("status")

# Conditional
if(prop("status") == "active", "Yes", "No")

# String concatenation
concat(prop("first_name"), " ", prop("last_name"))

# Date — today's date
now()

# Date difference (days between deadline and today)
dateDiff(now(), prop("deadline"), "days")
```

Formulas are evaluated per-row. Not all JavaScript functions are available — Bases formulas are a constrained expression language, not full JS.

---

## 7. Migration Path — Dataview to Bases

These Dataview patterns convert cleanly to Bases:

| Dataview Pattern | Bases Equivalent |
|-----------------|-----------------|
| `TABLE status, client FROM "03-Areas/clients"` | Source: `03-Areas/clients`, columns: status, client |
| `WHERE status = "active"` | Filter: status equals "active" |
| `SORT deadline ASC` | Sort: deadline column ascending |
| `FROM #client` | Source: tag `#client` |
| `LIMIT 20` | Not supported — Bases shows all matching rows |
| `GROUP BY status` | Group by: status |

These Dataview patterns do NOT convert to Bases — keep them as Dataview:
- `GROUP BY` with `length(rows)` aggregate counts
- `WHERE deadline < date(today)` (date comparisons require Dataview)
- DataviewJS blocks (any JavaScript)
- `FLATTEN` for list expansion
- Multi-source: `FROM "01-Projects" OR "02-Areas"`
- Computed fields beyond basic formulas

---

## 8. Recommendation for Yasmine

**Use Bases for:**
- Client tracker (simple table of all clients in `03-Areas/smarterflo/clients` — status, contact, company)
- Project status board (all projects in `02-Projects/business` sorted by deadline)
- Content inventory (all posts in `15-Smarterflo` filtered by platform)
- Quick read-only reference views you want fast and visual

**Use Dataview for:**
- Business dashboard with counts, computed days-until-deadline, and multi-source rollup
- Self-healing pattern library query (cross-folder + category grouping)
- Content pipeline tracker with status badges and JS conditional rendering
- Weekly review rollup (tasks completed, notes created, decisions made)
- Any query where you need to compute, aggregate, or combine sources

**Rule of thumb:** If you can build it by clicking in the Bases GUI without writing a line of code, use Bases. If you need logic — use Dataview.
