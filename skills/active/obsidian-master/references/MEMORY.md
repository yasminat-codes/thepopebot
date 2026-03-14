# Session Memory Protocol

How obsidian-master persists knowledge between sessions so Yasmine is never asked the same question twice.

---

## 1. What to Remember

| Item | Why it matters |
|------|----------------|
| Last active vault (Yasmine-OS or Smarterflo) | Skip the "which vault?" question on return |
| Confirmed vault paths | Avoid re-deriving paths from scratch |
| Templates built this session (name, path, date) | Track what exists; don't recreate |
| Plugin preferences (rejected suggestions) | Never recommend a plugin Yasmine already said no to |
| PARA folder mappings per vault | Route content correctly without asking |
| Custom CSS snippets created (name, what it does) | Reference existing work before creating new |

---

## 2. Where to Save

**File:** `~/.claude/projects/-Users-yasmineseidu/memory/MEMORY.md`

**Section header:** `## obsidian-master`

**Format:**

```
## obsidian-master

Last vault: Yasmine-OS
Yasmine-OS path: /Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Yasmine-OS/
Smarterflo path: /Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Smarterflo/
Templates built:
  - Daily Note | 05-Templates/Daily Note.md | 2026-03-08 | Yasmine-OS
  - Meeting Note | 05-Templates/Meeting Note.md | 2026-03-08 | Yasmine-OS
Plugin prefs (rejected):
  - Rejected: Kanban (prefers Tasks plugin)
PARA confirmed: yes (00-06 numbering)
CSS snippets:
  - minimal-headers.css | Removes H1 underlines | Yasmine-OS
```

---

## 3. When to Save

| Trigger | Action |
|---------|--------|
| Vault confirmed | Save `Last vault:` + confirmed path |
| Template created | Append to `Templates built:` table |
| Plugin suggestion rejected by Yasmine | Append to `Plugin prefs (rejected):` |
| New folder created (PARA or otherwise) | Note in memory if structurally significant |
| CSS snippet created | Append to `CSS snippets:` |
| End of any substantial session | Full save/update of section |

Save proactively — do not wait until end of session. If a template is created mid-session and the session ends unexpectedly, the record still exists.

---

## 4. How to Read on Session Start

1. Read `~/.claude/projects/-Users-yasmineseidu/memory/MEMORY.md`
2. Find the `## obsidian-master` section
3. **If found:**
   - Use `Last vault:` as the default — do not ask which vault again
   - Load confirmed paths — do not re-derive
   - Load rejected plugins — never suggest these again
   - Load templates built — reference before creating new ones
4. **If section not found:**
   - Ask which vault Yasmine wants to work in
   - Save the answer immediately after she responds

---

## 5. Template Registry Format

Track every template created under `Templates built:` using this table format:

| Template | Path | Created | Vault |
|----------|------|---------|-------|
| Daily Note | 05-Templates/Daily Note.md | 2026-03-08 | Yasmine-OS |
| Weekly Review | 05-Templates/Weekly Review.md | 2026-03-08 | Yasmine-OS |
| Meeting Note | 05-Templates/Meeting Note.md | 2026-03-08 | Smarterflo |
| Client Profile | 05-Templates/_client-template.md | 2026-03-08 | Smarterflo |

Before creating any template: check this registry. If one already exists at that path, confirm with Yasmine before overwriting.

---

## 6. Scripts Registry Format

Track every Templater user script created under `Scripts built:`:

| Script | Path | Purpose |
|--------|------|---------|
| auto-linker.js | 10-Templates/scripts/auto-linker.js | Parent note selection via suggester |
| tag-picker.js | 10-Templates/scripts/tag-picker.js | Multi-tag selection |
| folder-router.js | 10-Templates/scripts/folder-router.js | Auto-move note to PARA folder |
| moc-linker.js | 10-Templates/scripts/moc-linker.js | Append link to MOC file |

Before creating any script: check this registry. Scripts in `10-Templates/scripts/` are invoked as `tp.user["script-name"](tp)`.

---

## 7. Anti-Orphan Status

Track vault health state:

```
Anti-orphan status:
  Automatic Linker installed: yes/no
  Script folder configured: yes/no (10-Templates/scripts/)
  Last orphan audit: 2026-03-08
  Orphans found: 0
```

Update after every vault operation or weekly review.
