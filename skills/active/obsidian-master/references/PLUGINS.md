# Plugin Reference

## Currently Installed Plugins in Yasmine-OS

| Plugin | Purpose | Key settings to configure |
|--------|---------|--------------------------|
| **Excalidraw** | Diagrams, drawings, visual frameworks | Template folder: `10-Templates/Excalidraw/` |
| **Templater** | Note templates with dynamic content | Template folder: `10-Templates/` — MUST set this |
| **Dataview** | SQL-like queries, dynamic dashboards | Enable JavaScript queries in settings |
| **Calendar** | Sidebar calendar, daily note navigation | Toggle week numbers in settings |
| **Style Settings** | Per-theme configuration panel | Configure after setting a theme |
| **Omnisearch** | Full-text fuzzy search across vault | Hotkey: configure Cmd+Shift+O |
| **Copilot** | AI assistant inside Obsidian | Set API key in settings |
| **Homepage** | Choose which note opens on Obsidian launch | Set to `00-Dashboard/Home.md` |
| **Tasks** | Task dates, priorities, recurrence, queries | Date format in settings should match vault convention |
| **Pexels Banner** | Banner images from Pexels for note headers | Set API key in settings |
| **Local REST API** | HTTP API for external automation (obsidian-master uses this) | Note the API key and port (default 27123) |
| **Advanced URI** | URI-based deep linking and automation | No config needed — works immediately |
| **RSS Dashboard** | Read RSS feeds inside Obsidian | Add feed URLs in plugin settings |
| **Custom Note Width** | Per-note reading width control | Set default width or use frontmatter per note |
| **Auto Classifier** | AI-assisted auto-tagging of notes | Set model + API key |

### Priority configuration after a fresh install

These settings must be configured or plugins behave incorrectly:

1. **Templater** — Settings → Templater → Template folder location → set to `10-Templates/`
2. **Homepage** — Settings → Homepage → Homepage → set to `00-Dashboard/Home.md`
3. **Daily Notes (core)** — Settings → Daily Notes → Date format `YYYY-MM-DD`, New file location `00-Dashboard/Daily/`, Template `10-Templates/Daily Note`
4. **Dataview** — Settings → Dataview → Enable JavaScript queries (needed for DataviewJS blocks)
5. **Local REST API** — Note the API key displayed in settings — obsidian-master needs this

---

## Recommended Plugins to Add

High-value plugins not currently installed:

| Plugin | Why install | Install name |
|--------|------------|-------------|
| **Kanban** | Visual task boards — lists = columns, cards = tasks | "Obsidian Kanban" |
| **Periodic Notes** | Weekly/monthly/quarterly notes with proper templates | "Periodic Notes" |
| **Quick Switcher++** | Enhanced navigation — search by heading, alias, recent | "Quick Switcher++" |
| **Tag Wrangler** | Bulk rename, merge, and manage tags across vault | "Tag Wrangler" |
| **Linter** | Auto-format frontmatter, fix spacing, standardize markdown | "Obsidian Linter" |
| **Commander** | Add custom commands to toolbar, ribbon, context menus | "Commander" |
| **Obsidian Git** | Auto-commit vault to GitHub — backup layer | "Obsidian Git" |

**Install any of these:** Settings → Community Plugins → Browse → search name → Install → Enable

---

## Plugin Troubleshooting

### Identifying a conflict

Symptom: Obsidian crashes on startup, a feature stopped working, or a specific action hangs.

Steps:
1. Settings → Community Plugins → Enable "Restricted mode" (disables ALL community plugins)
2. If problem resolves, a plugin is the cause
3. Re-enable plugins one by one, testing after each
4. The plugin that re-introduces the problem is the culprit

### Reading error logs

Open Obsidian's developer console: Ctrl+Shift+I (Windows/Linux) or Cmd+Option+I (Mac)

Console tab shows plugin errors — look for red error lines. The plugin name usually appears in the stack trace.

### Checking for updates

Settings → Community Plugins → Check for updates

Updates resolve most bugs. Run this when a plugin starts behaving unexpectedly after an Obsidian update.

### Plugin conflicts with iCloud

Some plugins write frequently to disk (Git, Dataview cache, Tasks index). This can trigger iCloud sync conflicts.

If seeing frequent `(1)` duplicates after installing a plugin:
- Check if the plugin has a cache or index folder in `.obsidian/plugins/{plugin-name}/`
- These files changing constantly = iCloud noise
- Usually harmless, but if duplicates appear in actual notes, pause the plugin and check

---

## Installing Plugins

### Community plugins (standard method)

1. Settings → Community Plugins → Browse
2. Search for the plugin name
3. Click the plugin → Install
4. Click Enable after installation

### Manual installation (for beta plugins or plugins not in community list)

**Method 1 — BRAT plugin:**
1. Install "BRAT" from community plugins
2. Settings → BRAT → Add Beta Plugin
3. Paste the GitHub URL (e.g., `https://github.com/author/repo`)
4. BRAT handles installation and auto-updates

**Method 2 — Manual file drop:**
1. Download `main.js`, `manifest.json`, `styles.css` from the GitHub release
2. Create folder: `{vault}/.obsidian/plugins/{plugin-name}/`
3. Drop the 3 files in
4. Reload Obsidian → Settings → Community Plugins → Enable the plugin

---

## Local REST API — Integration Details

The Local REST API plugin is what `obsidian-master` uses to interact with Obsidian programmatically.

**Default port:** 27123
**API key:** Found in Settings → Local REST API → API Key (copy this)

**Common endpoints obsidian-master uses:**

| Action | Method | Endpoint |
|--------|--------|----------|
| Get note content | GET | `/vault/{path}` |
| Create/update note | PUT | `/vault/{path}` |
| Append to note | POST | `/vault/{path}` |
| List files in folder | GET | `/vault/{folder}/` |
| Run command | POST | `/commands/{command-id}/execute` |
| Open note in Obsidian | POST | `/open/{path}` |
| Search vault | POST | `/search/simple/` |

The plugin must be running (Obsidian must be open) for API calls to work. For automation from Claude, always verify Obsidian is open before making API calls.
