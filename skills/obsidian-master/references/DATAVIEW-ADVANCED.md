# Dataview Advanced — DataviewJS and Complex Queries

## 1. Advanced Clauses

### GROUP BY

Groups results by a field value. Results available via `rows` variable.

````markdown
```dataview
TABLE rows.file.link AS "Notes", length(rows) AS "Count"
FROM "03-Areas/smarterflo/clients"
GROUP BY status
```
````

`rows` is an array of all notes in that group. Use `length(rows)` for count, `rows.field` to access fields across the group.

### FLATTEN

Expands a list field into individual rows — one row per list item.

````markdown
```dataview
TABLE tag
FROM "01-Projects"
FLATTEN file.tags AS tag
WHERE tag != "#project"
```
````

Use case: if a note has `tags: [#client, #active, #q1]`, FLATTEN produces one row per tag.

### LIMIT + OFFSET — pagination

````markdown
```dataview
TABLE file.name, status
FROM "01-Projects"
SORT file.mtime DESC
LIMIT 10
OFFSET 10
```
````

OFFSET skips the first N results. Combine with LIMIT for page 2, page 3, etc.

---

## 2. DataviewJS — Full JavaScript API

Enable with `dataviewjs` code block (requires JavaScript queries enabled in Dataview settings).

````markdown
```dataviewjs
// Your JS here
```
````

### Core API Methods

| Method | Description |
|--------|-------------|
| `dv.pages(from)` | Query pages. `from` is optional DQL source string: `'"folder"'`, `'#tag'` |
| `dv.table(headers, rows)` | Render a table. `headers` = string array, `rows` = array of arrays |
| `dv.list(items)` | Render a bullet list |
| `dv.taskList(tasks, grouped)` | Render tasks. `grouped = true` groups by file |
| `dv.header(level, text)` | Add an H1-H6 header |
| `dv.paragraph(text)` | Add a paragraph of text |
| `dv.span(text)` | Inline text span |
| `await dv.io.load(path)` | Load file content as string. Must use `await` |
| `dv.current()` | The current note's page object |
| `dv.date(text)` | Parse a date string into a Luxon DateTime |
| `dv.duration(text)` | Parse a duration string |
| `dv.fileLink(path, embed, display)` | Create a file link object |

### dv.pages() — the main query method

```javascript
// All pages in a folder
const pages = dv.pages('"03-Areas/smarterflo/clients"');

// All pages with a tag
const clients = dv.pages('#client');

// All pages in folder AND with tag
const active = dv.pages('"01-Projects" and #active');

// All pages — no argument queries everything (use carefully in large vaults)
const all = dv.pages();
```

Pages returns an array of page objects. Each page has all frontmatter fields plus implicit `file.*` fields.

### Filtering, sorting, mapping

```javascript
const pages = dv.pages('"01-Projects"')
  .where(p => p.status !== "completed")
  .sort(p => p.deadline, "asc")
  .limit(10);
```

---

## 3. Useful DataviewJS Patterns

### Aggregate stats — count, sum, average

```javascript
const pages = dv.pages('"03-Areas/smarterflo/clients"');
const active = pages.where(p => p.status === "active").length;
const total = pages.length;
dv.paragraph(`**${active} active clients** out of ${total} total`);
```

### Multi-source queries

```javascript
const projects = dv.pages('"01-Projects"');
const areas = dv.pages('"02-Areas"');
const combined = [...projects, ...areas]
  .filter(p => p.status === "active")
  .sort((a, b) => (a.file.mtime < b.file.mtime ? 1 : -1));
dv.table(["Note", "Status", "Modified"], combined.map(p => [p.file.link, p.status, p.file.mtime]));
```

### Date calculations

```javascript
const today = dv.date("today");
const pages = dv.pages('"01-Projects"')
  .where(p => p.deadline)
  .map(p => {
    const deadline = dv.date(p.deadline);
    const daysUntil = deadline.diff(today, "days").days;
    return [p.file.link, p.deadline, Math.round(daysUntil) + " days"];
  });
dv.table(["Project", "Deadline", "Time Left"], pages);
```

### Conditional rendering

```javascript
const pages = dv.pages('"03-Areas/smarterflo/clients"');
if (pages.length === 0) {
  dv.paragraph("No clients found.");
} else {
  dv.table(["Client", "Status"], pages.map(p => [p.file.link, p.status ?? "—"]));
}
```

---

## 4. Five Advanced DataviewJS Examples for Yasmine

### Business Dashboard (clients, active projects, decisions)

```javascript
dv.header(2, "Smarterflo Dashboard");

// Active clients
const clients = dv.pages('"03-Areas/smarterflo/clients"').where(p => p.status === "active");
dv.header(3, `Active Clients (${clients.length})`);
dv.table(["Client", "Contact", "Next Action"],
  clients.sort(p => p.file.name).map(p => [p.file.link, p.contact ?? "—", p.next_action ?? "—"])
);

// Active projects
const projects = dv.pages('"02-Projects/business"').where(p => p.status === "active");
dv.header(3, `Active Projects (${projects.length})`);
dv.table(["Project", "Deadline", "Status"],
  projects.sort(p => p.deadline).map(p => [p.file.link, p.deadline ?? "—", p.status])
);

// Pending decisions
const decisions = dv.pages('"00-Command-Center"').where(p => p.status === "pending" && p.decision);
dv.header(3, `Pending Decisions (${decisions.length})`);
if (decisions.length > 0) {
  dv.list(decisions.map(p => `${p.file.link} — ${p.decision}`));
}
```

### Content Pipeline Tracker with Status Badges

```javascript
const statusBadge = (s) => {
  const map = { "idea": "🔵 Idea", "draft": "🟡 Draft", "ready": "🟢 Ready", "published": "✅ Published" };
  return map[s] ?? s;
};

const content = dv.pages('"15-Smarterflo/LinkedIn-Strategy"')
  .where(p => p.content_type && p.file.name !== "_template")
  .sort(p => p.publish_date, "asc");

dv.table(
  ["Title", "Platform", "Type", "Status", "Publish Date"],
  content.map(p => [
    p.file.link,
    p.platform ?? "—",
    p.content_type ?? "—",
    statusBadge(p.status),
    p.publish_date ?? "—"
  ])
);
```

### Weekly Review Rollup

```javascript
const weekStart = dv.date("today").startOf("week");
const weekEnd = dv.date("today").endOf("week");

dv.header(2, `Week of ${weekStart.toFormat("MMMM d")}`);

// Notes created this week
const newNotes = dv.pages().where(p => dv.date(p.file.ctime) >= weekStart);
dv.header(3, `Notes Created (${newNotes.length})`);
dv.list(newNotes.sort(p => p.file.ctime, "desc").map(p => p.file.link));

// Tasks completed this week (requires inline Due:: field)
const completedTasks = dv.pages().file.tasks
  .where(t => t.completed && t.completion >= weekStart);
dv.header(3, `Tasks Completed (${completedTasks.length})`);
dv.taskList(completedTasks);
```

### Self-Healing Pattern Library Query

```javascript
const patterns = dv.pages('"05-Dev-Context/self-healing/patterns"')
  .where(p => p.file.name !== "_MOC-Self-Healing");

dv.header(2, `Self-Healing Patterns (${patterns.length})`);

// Group by category
const categories = [...new Set(patterns.map(p => p.category).filter(Boolean))].sort();

for (const cat of categories) {
  const catPatterns = patterns.where(p => p.category === cat);
  dv.header(3, cat + ` (${catPatterns.length})`);
  dv.table(["Pattern", "Severity", "Last Occurred"],
    catPatterns.map(p => [p.file.link, p.severity ?? "—", p.last_occurred ?? "—"])
  );
}
```

### Task Burndown by Area

```javascript
const areas = ["01-Projects", "02-Areas/smarterflo", "02-Areas/personal"];
dv.header(2, "Task Burndown by Area");

for (const area of areas) {
  const tasks = dv.pages(`"${area}"`).file.tasks;
  const open = tasks.where(t => !t.completed).length;
  const done = tasks.where(t => t.completed).length;
  const total = tasks.length;
  if (total > 0) {
    const pct = Math.round((done / total) * 100);
    dv.paragraph(`**${area}** — ${done}/${total} done (${pct}%)`);
  }
}
```

---

## 5. Inline Dataview Queries

Inline queries render values inside prose without a code block.

**Inline DQL** — renders a single computed value:

```
Today is `= date(today)`.
This note was modified `= this.file.mtime`.
Status: `= this.status`
```

**Inline JS** — full JavaScript, renders a value:

```
Word count: `$= dv.current().file.size`
Days since created: `$= Math.round(dv.date("today").diff(dv.date(dv.current().file.ctime), "days").days)`
```

`this` in DQL refers to the current note. `dv.current()` in JS is the same.

---

## 6. Performance Tips for Large Vaults

| Problem | Solution |
|---------|----------|
| Slow queries across all notes | Always use `FROM "folder"` or `FROM #tag` to scope — never query the whole vault without a source |
| Dashboard note loading slowly | Split into multiple notes; one heavy DataviewJS block per note |
| `dv.pages()` with no argument | Avoid in vaults over 500 notes — scopes every note |
| Re-rendering on every keystroke | Enable "Refresh Interval" in Dataview settings (500ms+ reduces thrash) |
| Async io.load in a loop | Use `Promise.all()` for parallel loads instead of sequential awaits |
| Complex JS that runs slowly | Cache intermediate results with `const` — avoid recomputing inside `.map()` |
