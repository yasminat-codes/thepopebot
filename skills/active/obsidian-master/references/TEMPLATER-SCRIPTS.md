# Templater User Scripts — Reference

User scripts extend Templater with reusable JavaScript logic. All scripts here are tuned to Yasmine's vaults.

**Vaults:**
- Smarterflo: `/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Smarterflo/`
- Yasmine-OS: `/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Yasmine-OS/`

---

## 1. Setup

### Configure the Scripts Folder

1. Settings → Community Plugins → Templater → open settings
2. Scroll to **Script files folder location**
3. Type: `10-Templates/scripts`
4. Create the folder in the vault if it does not exist

Once configured, any `.js` file placed in `10-Templates/scripts/` is available as `tp.user.<filename>(tp)`.

### Naming Convention

| File | Call in template |
|------|-----------------|
| `auto-linker.js` | `tp.user["auto-linker"](tp)` |
| `tag-picker.js` | `tp.user["tag-picker"](tp)` |
| `folder-router.js` | `tp.user["folder-router"](tp, type)` |
| `moc-linker.js` | `tp.user["moc-linker"](tp, mocName)` |
| `date-range.js` | `tp.user["date-range"](tp)` |
| `status-picker.js` | `tp.user["status-picker"](tp, options, labels)` |

Hyphenated filenames require bracket notation: `tp.user["script-name"]`. Single-word filenames can use dot notation: `tp.user.scriptname`.

### Script File Structure

Every user script must export a single async function that accepts `tp` as its first argument:

```javascript
module.exports = async (tp) => {
  // your code here
  return "output string";
};
```

`tp` provides full access to all Templater modules: `tp.file`, `tp.date`, `tp.system`, `tp.app`, `tp.web`, `tp.user`.

Scripts that have side effects only (e.g. moving a file, appending to a MOC) return nothing or `undefined` — callers should not use `tR +=` on them.

---

## 2. Script: auto-linker.js

Lets the user pick a parent note from all vault files. Returns a wikilink to the selected note.

**File:** `10-Templates/scripts/auto-linker.js`

```javascript
module.exports = async (tp) => {
  const files = tp.app.vault.getMarkdownFiles()
    .filter(f => !f.path.startsWith('10-Templates'));

  const parent = await tp.system.suggester(
    item => `${item.basename} (${item.parent.name})`,
    files,
    false,
    "Select parent note..."
  );

  if (!parent) return "";
  return `[[${parent.basename}]]`;
};
```

**Usage in template:**

```
<%* const parentLink = await tp.user["auto-linker"](tp) %>
parent: <% parentLink %>
```

**Notes:**
- Templates folder is excluded from the suggester list to avoid picking template files as parents.
- Returns an empty string if the user cancels — safe to use in YAML frontmatter.
- The `false` third argument means cancellation does not throw an error.

---

## 3. Script: tag-picker.js

Multi-tag selection from a predefined list. Returns a YAML-array string.

**File:** `10-Templates/scripts/tag-picker.js`

```javascript
module.exports = async (tp) => {
  const tagOptions = [
    "meeting", "client", "project", "research", "decision",
    "daily", "weekly-review", "content", "linkedin", "process",
    "reference", "resource", "task", "idea", "template"
  ];

  const selected = await tp.system.multi_suggester(
    item => item,
    tagOptions,
    false,
    "Select tags (space to select, enter to confirm)"
  );

  if (!selected || selected.length === 0) return "[]";
  return `[${selected.join(", ")}]`;
};
```

**Usage in template:**

```yaml
tags: <%* tR += await tp.user["tag-picker"](tp) %>
```

**Notes:**
- `tp.system.multi_suggester` is a Templater v1.16+ feature. Confirm Templater version is up to date if this errors.
- Returns `[]` on empty selection — valid YAML, safe in frontmatter.
- Add or remove tags from `tagOptions` as Yasmine's content categories evolve.

---

## 4. Script: folder-router.js

Auto-moves the current note to the correct PARA folder based on note type. No return value — side effect only.

**File:** `10-Templates/scripts/folder-router.js`

```javascript
module.exports = async (tp, noteType) => {
  const folderMap = {
    "daily": "00-Command-Center",
    "meeting": "03-Areas/smarterflo/meetings",
    "client": "03-Areas/smarterflo/clients",
    "project": "02-Projects/business",
    "research": "04-Knowledge",
    "decision": "00-Command-Center/decisions",
    "content": "15-Smarterflo/LinkedIn-Strategy/ideas",
    "process": "03-Areas/smarterflo/processes",
    "competitor": "04-Knowledge/competitors",
    "self-healing": "05-Dev-Context/self-healing/patterns"
  };

  const targetFolder = folderMap[noteType];
  if (targetFolder) {
    await tp.file.move(`/${targetFolder}/${tp.file.title}`);
  }
};
```

**Usage in template:**

```
<%* await tp.user["folder-router"](tp, "meeting") %>
```

**Notes:**
- `tp.file.move()` path must start with `/` (vault-relative, not filesystem).
- The target folder must exist before calling — Obsidian will not create missing folders automatically.
- Call this near the top of the template so the move happens before other content is written.
- Folder Templates (configured in Templater settings) handle most routing automatically. Use this script only when you need programmatic routing based on a value chosen at note-creation time.

**Adding new types:** Extend `folderMap` with any new folder as the vault grows. Keep keys lowercase with hyphens.

---

## 5. Script: moc-linker.js

Appends a backlink to the current note into a named MOC file, then returns a wikilink to that MOC.

**File:** `10-Templates/scripts/moc-linker.js`

```javascript
module.exports = async (tp, mocName) => {
  const mocFile = tp.file.find_tfile(mocName);
  if (!mocFile) return `[[${mocName}]]`;

  const currentTitle = tp.file.title;
  const mocContent = await tp.app.vault.read(mocFile);

  if (!mocContent.includes(`[[${currentTitle}]]`)) {
    const newContent = mocContent + `\n- [[${currentTitle}]]`;
    await tp.app.vault.modify(mocFile, newContent);
  }

  return `[[${mocName}]]`;
};
```

**Usage in template:**

```
<%* tR += await tp.user["moc-linker"](tp, "_MOC-Clients") %>
```

**Notes:**
- `tp.file.find_tfile(name)` searches by filename without extension. Pass the exact MOC filename.
- If the MOC does not exist yet, the script still returns a wikilink — Obsidian will create an unresolved link shown in graph view.
- Duplicate check (`includes`) prevents the same link from being appended twice if the template is re-applied.
- The MOC file must be open in the vault (not just on disk) for `vault.modify` to work correctly on iCloud-backed vaults.

**Smarterflo MOC names to reference:**
- `_MOC-Clients`
- `_MOC-Self-Healing`
- `_MOC-Projects`
- `_MOC-Knowledge`

---

## 6. Script: date-range.js

Returns a formatted date range string for the current ISO week (Monday–Friday).

**File:** `10-Templates/scripts/date-range.js`

```javascript
module.exports = async (tp) => {
  const startOfWeek = tp.date.weekday("YYYY-MM-DD", 1); // Monday
  const endOfWeek = tp.date.weekday("YYYY-MM-DD", 5);   // Friday
  return `${startOfWeek} → ${endOfWeek}`;
};
```

**Usage in template:**

```yaml
week: <%* tR += await tp.user["date-range"](tp) %>
```

**Output example:** `2026-03-09 → 2026-03-13`

**Notes:**
- `tp.date.weekday` uses ISO weekday numbering: 1 = Monday, 7 = Sunday.
- This outputs the current week regardless of what day the note is created — useful for weekly review notes.
- To get the full week including weekend, change `5` to `7`.

---

## 7. Script: status-picker.js

Reusable single-select status picker. Accepts custom option lists so one script handles all status fields.

**File:** `10-Templates/scripts/status-picker.js`

```javascript
module.exports = async (tp, options, labels) => {
  const displayLabels = labels || options;
  return await tp.system.suggester(
    displayLabels,
    options,
    false,
    "Select status..."
  );
};
```

**Usage in templates:**

```yaml
# Project status
status: <%* tR += await tp.user["status-picker"](tp, ["active", "on-hold", "completed", "archived"], ["Active", "On Hold", "Completed", "Archived"]) %>

# Client status
status: <%* tR += await tp.user["status-picker"](tp, ["prospect", "active", "churned"], ["Prospect", "Active", "Churned"]) %>

# Content status
status: <%* tR += await tp.user["status-picker"](tp, ["idea", "drafting", "review", "scheduled", "published"]) %>
```

**Notes:**
- First argument to `tp.system.suggester` is display labels (what the user sees), second is return values (what gets written).
- When `labels` is omitted, values are displayed as-is — works fine for single-word statuses.
- Returns the raw value string directly — wrap in quotes in YAML if the value contains spaces.

---

## 8. Calling Scripts from Templates

### Rules

| Rule | Detail |
|------|--------|
| Always `await` | All `tp.system.*` and `tp.user.*` calls are async |
| Use `tR +=` to append output | String-returning scripts need `tR +=` to write to the note |
| Side-effect scripts need no `tR` | `folder-router` and `moc-linker` — just `await`, no assignment |
| Use `<%* ... %>` blocks | Execute-only blocks (with asterisk) — no output unless you use `tR +=` |
| Bracket notation for hyphens | `tp.user["script-name"]` not `tp.user.script-name` |

### Pattern Reference

```
# String output — appended to note
<%* tR += await tp.user["tag-picker"](tp) %>

# String output — stored in variable, used later
<%* const link = await tp.user["auto-linker"](tp) %>
parent: <% link %>

# Side-effect only — no return value needed
<%* await tp.user["folder-router"](tp, "client") %>

# Conditional use of return value
<%*
const status = await tp.user["status-picker"](tp, ["active", "archived"]);
if (status === "archived") {
  await tp.user["folder-router"](tp, "archive");
}
tR += status;
%>
```

---

## 9. Debugging Scripts

**Developer tools:** Cmd+Option+I (Mac) opens the developer console inside Obsidian. `console.log()` output appears here.

**Test before embedding:** Use a QuickAdd macro to call the script in isolation before wiring it into a template.

**Common errors:**

| Error | Cause | Fix |
|-------|-------|-----|
| `tp.user["name"] is not a function` | Script file not found or scripts folder not configured | Check `10-Templates/scripts/` folder path in Templater settings |
| `Cannot read properties of undefined` | Missing `await` on async tp call | Add `await` before `tp.system.*` calls |
| File not moved | Target folder does not exist | Create the folder in the vault first |
| MOC not updated | iCloud file not synced locally | Wait for sync or open the file manually first |
| `multi_suggester is not a function` | Outdated Templater version | Update Templater in Community Plugins |
| Script runs but outputs nothing | Used `tR =` instead of `tR +=` | Always use `+=` to append |

**Reload scripts:** After editing a `.js` file, use "Templater: Reload system files" from the command palette. Scripts are cached per session.

---

## 10. Quick Reference

| Script | Returns | Side effects |
|--------|---------|--------------|
| `auto-linker` | `[[parent]]` wikilink string | None |
| `tag-picker` | `[tag1, tag2]` array string | None |
| `folder-router` | Nothing | Moves file to PARA folder |
| `moc-linker` | `[[MOC-name]]` wikilink string | Appends link to MOC file |
| `date-range` | `YYYY-MM-DD → YYYY-MM-DD` | None |
| `status-picker` | Selected status string | None |
