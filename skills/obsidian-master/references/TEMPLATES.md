# Templater Reference

## 1. Templater vs Core Templates

| Feature | Core Templates | Templater |
|---------|---------------|-----------|
| Install | Built-in | Community plugin |
| Dynamic content | None — static text only | Full: dates, prompts, JS |
| Conditional logic | No | Yes — `<%* if ... %>` blocks |
| User input | No | `tp.system.prompt()`, `tp.system.suggester()` |
| Custom JS scripts | No | `tp.user.*` functions |
| Folder templates | No | Yes — auto-apply per folder |
| Async operations | No | Yes — `await` supported |
| Frontmatter access | No | `tp.frontmatter.<property>` |
| Recommendation | Only if Templater unavailable | Always use Templater |

---

## 2. Setup & Configuration

1. Settings → Community Plugins → Browse → search "Templater" → Install → Enable
2. Settings → Templater:
   - **Template folder location** — set to `10-Templates` (or your templates folder)
   - **Trigger Templater on new file creation** — Enable
   - **Enable Folder Templates** — Enable
   - **User scripts folder** — set to `10-Templates/scripts` (for `tp.user.*`)
3. **Folder Templates table** — add rows mapping folder paths to template files (see §12)
4. Hotkey (optional): Settings → Hotkeys → "Templater: Open Insert Template modal" → assign key

---

## 3. Template Syntax — All 6 Block Types

| Block | Syntax | Output | When to use |
|-------|--------|--------|-------------|
| Expression | `<% expr %>` | Rendered value | Simple value output |
| Code block | `<%* code %>` | Nothing (unless `tR +=`) | JS logic, assignments, conditionals |
| Await | `<% await expr %>` | Rendered value | Async functions (prompt, file ops) |
| Unescaped | `<%- expr %>` | HTML-unescaped | HTML content that must not be escaped |
| Trim left | `<%_ block %>` | Value, whitespace before removed | Avoid blank lines from code blocks |
| Trim right | `block _%>` | Value, whitespace after removed | Avoid trailing newlines |

**Suppress trailing newline from code block:**
```
<%* const x = "hello" -%>
```

**Output inside code block:**
```
<%* tR += "injected text" %>
```

---

## 4. tp.file Reference

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `tp.file.content` | property | Full file contents as string | `<% tp.file.content %>` |
| `tp.file.title` | property | File title (no extension) | `<% tp.file.title %>` |
| `tp.file.tags` | property | Array of tags | `<% tp.file.tags.join(", ") %>` |
| `tp.file.folder()` | `(absolute?: bool)` | Folder path. Default: relative | `<% tp.file.folder() %>` |
| `tp.file.path()` | `(relative?: bool)` | Full path. Default: absolute | `<% tp.file.path(true) %>` |
| `tp.file.creation_date()` | `(format?)` | Creation date. Default: `"YYYY-MM-DD HH:mm"` | `<% tp.file.creation_date("YYYY-MM-DD") %>` |
| `tp.file.last_modified_date()` | `(format?)` | Last modified. Default: `"YYYY-MM-DD HH:mm"` | `<% tp.file.last_modified_date() %>` |
| `tp.file.cursor()` | `(order?: number)` | Sets cursor position after template runs | `<% tp.file.cursor(1) %>` |
| `tp.file.cursor_append()` | `(content: string)` | Appends content at cursor | `<% tp.file.cursor_append("text") %>` |
| `tp.file.selection()` | `()` | Returns selected text | `<% tp.file.selection() %>` |
| `tp.file.exists()` | `async (filepath: string)` | Returns boolean | `<% await tp.file.exists("Notes/foo.md") %>` |
| `tp.file.find_tfile()` | `(filename: string)` | Returns TFile instance | `<%* const f = tp.file.find_tfile("Index") %>` |
| `tp.file.create_new()` | `async (template, filename?, open_new?, folder?)` | Creates new file | See below |
| `tp.file.move()` | `async (new_path, file_to_move?)` | Moves file | `<% await tp.file.move("Archive/" + tp.file.title) %>` |
| `tp.file.rename()` | `async (new_title: string)` | Renames current file | `<% await tp.file.rename("New Title") %>` |
| `tp.file.include()` | `async (include_link: string\|TFile)` | Embeds another template | `<% await tp.file.include("[[footer-template]]") %>` |

**tp.file.create_new() parameters:**
- `template` — TFile or string content
- `filename` — string, default `"Untitled"`
- `open_new` — boolean, default `false`
- `folder` — TFolder or string path (optional)

---

## 5. tp.date Reference

| Function | Signature | Purpose | Example |
|----------|-----------|---------|---------|
| `tp.date.now()` | `(format?, offset?, reference?, reference_format?)` | Current date/time | `<% tp.date.now("YYYY-MM-DD") %>` |
| `tp.date.tomorrow()` | `(format?)` | Tomorrow. Default: `"YYYY-MM-DD"` | `<% tp.date.tomorrow() %>` |
| `tp.date.yesterday()` | `(format?)` | Yesterday. Default: `"YYYY-MM-DD"` | `<% tp.date.yesterday() %>` |
| `tp.date.weekday()` | `(format?, weekday, reference?, reference_format?)` | Weekday of current/specified week | `<% tp.date.weekday("YYYY-MM-DD", 0) %>` |

**tp.date.now() offset:**
- Number = days (`1` = tomorrow, `-7` = last week)
- ISO 8601 duration string: `"P1M"` = +1 month, `"P-1Y"` = -1 year, `"P1W"` = +1 week

**tp.date.weekday() weekday param:**
- `0–6` = this week's Monday–Sunday
- `7` = next week's same day
- `-7` = previous week's same day

### Moment.js Format Tokens

| Token | Output | Example |
|-------|--------|---------|
| `YYYY` | 4-digit year | `2026` |
| `YY` | 2-digit year | `26` |
| `MM` | Month 01–12 | `03` |
| `MMMM` | Full month name | `March` |
| `MMM` | Short month | `Mar` |
| `DD` | Day 01–31 | `08` |
| `Do` | Day with ordinal | `8th` |
| `dddd` | Full weekday | `Sunday` |
| `ddd` | Short weekday | `Sun` |
| `HH` | Hour 00–23 | `14` |
| `hh` | Hour 01–12 | `02` |
| `mm` | Minute 00–59 | `30` |
| `ss` | Second 00–59 | `00` |
| `WW` | ISO week number | `10` |
| `[W]` | Literal "W" | `W` |

**ISO week example:** `<% tp.date.now("YYYY-[W]WW") %>` → `2026-W10`

---

## 6. tp.system Reference

| Function | Signature | Returns | Use case |
|----------|-----------|---------|----------|
| `tp.system.clipboard()` | `()` | string | Insert clipboard content into template |
| `tp.system.prompt()` | `async (prompt_text?, default_value?, throw_on_cancel?, multiline?)` | string \| null | Single-line or multiline text input |
| `tp.system.suggester()` | `async (text_items, items, throw_on_cancel?, placeholder?, limit?)` | T \| null | Pick one item from a list |
| `tp.system.multi_suggester()` | `async (text_items, items, throw_on_cancel?, title?, limit?)` | T[] \| null | Pick multiple items from a list |

**tp.system.prompt() parameters:**
- `throw_on_cancel` — boolean, default `false` (null returned on cancel if false)
- `multiline` — boolean, default `false`

**tp.system.suggester() parameters:**
- `text_items` — `string[]` or `function(item) => string` for display labels
- `items` — `T[]` — actual values returned
- `throw_on_cancel` — boolean, default `false`
- `placeholder` — string prompt text shown in suggester
- `limit` — max items shown

**Examples:**
```
<%* const name = await tp.system.prompt("Note title", tp.file.title) -%>
<%* const choice = await tp.system.suggester(["Draft", "Published"], ["draft", "published"]) -%>
<%* const tags = await tp.system.multi_suggester(["AI", "Strategy", "Operations"], ["ai", "strategy", "ops"]) -%>
```

---

## 7. tp.frontmatter Reference

Access frontmatter properties by name — no special function needed.

```
<% tp.frontmatter.title %>
<% tp.frontmatter.status %>
<% tp.frontmatter.tags %>
```

**Modify frontmatter from a template** — use a code block with `app.fileManager.processFrontMatter()`:
```
<%*
await app.fileManager.processFrontMatter(tp.file.find_tfile(tp.file.title), (fm) => {
  fm["status"] = "active";
  fm["created"] = tp.date.now("YYYY-MM-DD");
});
-%>
```

**Read frontmatter conditionally:**
```
<%* if (tp.frontmatter.type === "client") { %>
## CRM Fields
<%* } %>
```

---

## 8. tp.hooks Reference

| Hook | Signature | When it runs |
|------|-----------|-------------|
| `tp.hooks.on_all_templates_executed` | `(callback: () => void)` | After all templates in the current run have executed |

**Pattern — run code after full template execution:**
```
<%*
tp.hooks.on_all_templates_executed(async () => {
  // e.g. move the file after all content is rendered
  await tp.file.move("03-Areas/clients/" + tp.file.title);
});
-%>
```

Use this when a post-processing action depends on the fully rendered state of the note (e.g., rename based on prompted input, move to a folder after frontmatter is set).

---

## 9. tp.user Scripts

User scripts make reusable JS functions callable as `tp.user.<filename>(args)`.

**Setup:**
1. Settings → Templater → User scripts folder → set to `10-Templates/scripts`
2. Create `.js` files in that folder — each filename becomes the function name
3. Desktop only — not supported on mobile

**Script structure:**
```javascript
// 10-Templates/scripts/slugify.js
module.exports = async (tp, text) => {
  return text.toLowerCase().replace(/\s+/g, "-").replace(/[^\w-]/g, "");
};
```

**Invocation in template:**
```
<%* const slug = await tp.user.slugify(tp.file.title) -%>
```

**Script receives:** `tp` as first arg always, then any additional args passed in the template call.

**Async scripts:** Use `async` and `await` — Templater supports it natively.

---

## 10. Auto-linking Pattern

Let the user pick a parent note from the vault for linking:

```
<%*
const files = tp.app.vault.getMarkdownFiles();
const parent = await tp.system.suggester(
  (f) => f.basename,
  files,
  false,
  "Select parent note"
);
const parentLink = parent ? `[[${parent.basename}]]` : "";
-%>
parent: <% parentLink %>
```

**Scoped to a folder:**
```
<%*
const clients = tp.app.vault.getMarkdownFiles().filter(f =>
  f.path.startsWith("03-Areas/smarterflo/clients/")
);
const client = await tp.system.suggester((f) => f.basename, clients, false, "Select client");
-%>
```

---

## 11. Auto-tagging Pattern

Multi-select tags from a predefined list:

```
<%*
const tagOptions = ["ai", "strategy", "client", "research", "operations", "content", "linkedin"];
const selected = await tp.system.multi_suggester(tagOptions, tagOptions, false, "Select tags");
const tagYaml = selected ? selected.map(t => `  - ${t}`).join("\n") : "";
-%>
---
tags:
<% tagYaml %>
---
```

**Dynamic tags from vault** (reads all existing tags):
```
<%*
const allTags = Object.keys(tp.app.metadataCache.getTags() || {})
  .map(t => t.replace(/^#/, ""));
const selected = await tp.system.multi_suggester(allTags, allTags, false, "Select tags");
-%>
```

---

## 12. Folder Templates

Folder templates auto-apply a template when a new note is created in a mapped folder.

**Setup:**
1. Settings → Templater → Enable Folder Templates → toggle on
2. In the Folder Templates table, click "Add new" for each mapping:

| Folder | Template |
|--------|---------|
| `03-Areas/smarterflo/clients/` | `10-Templates/_client-template.md` |
| `04-Knowledge/competitors/` | `10-Templates/_competitor-template.md` |
| `05-Dev-Context/self-healing/patterns/` | `10-Templates/self-healing-pattern.md` |
| `00-Daily-Notes/` | `10-Templates/daily-note.md` |
| `04-Knowledge/` | `10-Templates/research-note.md` |
| `02-Projects/business/` | `10-Templates/project-note.md` |
| `15-Smarterflo/LinkedIn-Strategy/` | `10-Templates/content-idea.md` |

**Rules:**
- Folder path must be exact (no trailing slash needed, but be consistent)
- Only triggers on new note creation — moving an existing note does not trigger
- Most specific folder path wins if multiple patterns could match
- Template file must exist or Templater silently skips

---

## 13. QuickAdd Integration

QuickAdd chains captures, template-based note creation, and macros from the command palette.

**Install:** Settings → Community Plugins → search "QuickAdd" → Install → Enable

### Three Modes

| Mode | What it does | When to use |
|------|-------------|-------------|
| Capture | Appends/prepends text to a specific existing note | Inbox, task list, decision log |
| Template | Creates a new note from a template in a folder | Client notes, content ideas, research |
| Macro | Runs multiple QuickAdd choices in sequence | Multi-step workflows |

**Setup:**
1. Settings → QuickAdd → "Add Choice" → name it → choose type
2. Configure the choice (capture target, template path, folder, naming format)
3. Toggle "Add to command palette" — makes it accessible via Cmd+P

### Common QuickAdd Recipes

| Choice name | Type | Config |
|-------------|------|--------|
| Add task | Capture | Appends `- [ ] {{VALUE}}` to `00-Command-Center/Tasks.md` |
| New client | Template | Template: `_client-template.md`, Folder: `03-Areas/smarterflo/clients/` |
| Log decision | Capture | Appends `{{DATE}} — {{VALUE}}` to `00-Command-Center/Business-Decisions-Log.md` |
| Content idea | Template | Template: `content-idea.md`, Folder: `15-Smarterflo/LinkedIn-Strategy/ideas/` |
| New competitor | Template | Template: `_competitor-template.md`, Folder: `04-Knowledge/competitors/` |

**QuickAdd + Templater:** When QuickAdd creates a note from a template, Templater processes the template's `<% %>` blocks normally. Both work together — QuickAdd handles the trigger and folder targeting, Templater handles the dynamic content.

**Macro example — new project flow:**
1. Macro step 1: Template choice → create project note
2. Macro step 2: Capture choice → log to decisions log
3. Macro step 3: Template choice → create first task note
