# Sync & Backup

## Yasmine's Current Setup: iCloud Sync

**Vault location:**
```
/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Smarterflo/
```

iCloud syncs automatically between Mac and iPhone — no configuration needed. Obsidian Mobile on iPhone opens the same vault from iCloud and works natively.

### What syncs via iCloud

- All markdown files and folders
- Attachments (images, PDFs)
- `.obsidian/` folder — plugin configs, hotkeys, theme, graph settings
- Canvas files
- Excalidraw files

### Known iCloud limitations

| Issue | What happens | How to handle |
|-------|-------------|--------------|
| Conflict copies | `Note (1).md` duplicate appears | Manual merge (see below) |
| Sync delay | Changes take 30-120s to appear on other device | Wait before editing same file |
| Large vaults | Sync slows above ~10k files | Keep attachments lean |
| First sync | Can take hours on a new device | Leave app open, let it complete |

### iCloud conflict resolution

Symptom: You see `Note (1).md` or `Note (2).md` alongside the original.

Steps:
1. Open both files
2. Identify which has the most recent or correct content
3. Copy any unique content from the duplicate into the original
4. Delete the duplicate

Prevention: Always close Obsidian fully on one device before editing the same note on another. Especially important for frequently-updated notes like daily notes and the capture inbox.

---

## Recommended: Obsidian Git (Not Installed)

Obsidian Git auto-commits your vault to a private GitHub repo on a schedule. This is a backup layer on top of iCloud — iCloud can lose data in edge cases, Git cannot.

**Setup:**
1. Settings → Community Plugins → Browse → install "Obsidian Git"
2. Open terminal in vault directory: `cd "/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Smarterflo"`
3. `git init && git remote add origin https://github.com/yasmineseidu/obsidian-vault-private.git`
4. In plugin settings: auto-pull interval = 10 min, auto-push interval = 30 min, auto-commit message = `vault: {{date}}`

Recommended private GitHub repo — not public.

---

## Core File Recovery Plugin (Built In)

Settings → Core Plugins → File Recovery → Enable

Keeps rolling snapshots of every note you edit. Independent of iCloud or Git.

| Setting | Recommended |
|---------|------------|
| Snapshot interval | Every 5 minutes |
| History length | 30 days |

**To recover a previous version:**
1. Settings → File Recovery
2. Select the note from the list
3. Browse snapshots by timestamp
4. Click "Restore" to roll back

This is the fastest recovery option for accidental edits — does not require any external service.

---

## Manual Backup Script

For a local time-stamped snapshot of the vault (complements iCloud + Git):

```bash
#!/bin/bash
# Save as: ~/scripts/backup-obsidian.sh
# Make executable: chmod +x ~/scripts/backup-obsidian.sh

VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Smarterflo"
BACKUP_DIR="$HOME/Desktop/obsidian-backups"
TIMESTAMP=$(date +%Y-%m-%d)
DEST="$BACKUP_DIR/$TIMESTAMP"

mkdir -p "$DEST"
rsync -av --exclude='.obsidian' "$VAULT/" "$DEST/"
echo "Backup complete: $DEST"
```

Run before major restructuring (bulk renames, folder moves, plugin changes).

Add to cron for automation:
```bash
# Run daily at 11pm — paste into: crontab -e
0 23 * * * /bin/bash ~/scripts/backup-obsidian.sh
```

---

## Recovery Priority Order

When something goes wrong, try in this order:

| Priority | Method | Recovery speed | Data coverage |
|----------|--------|----------------|--------------|
| 1 | File Recovery plugin | Instant | Last 30 days, 5-min intervals |
| 2 | iCloud version history | 1-2 min | 30 days of iCloud history |
| 3 | Git history | 5 min | Full history if set up |
| 4 | Manual backup | 5 min | Last time script ran |

**iCloud version history** (built into macOS):
1. Right-click the file in Finder
2. "Revert to" → "Browse All Versions"
3. Time Machine-style UI — navigate to the version you want
4. Click "Restore"

---

## iPhone Sync Notes

- Obsidian Mobile reads from iCloud natively — same vault, same plugins (if mobile-compatible)
- Some plugins don't work on mobile (anything using shell scripts or Node.js)
- Settings sync: `.obsidian/` folder syncs, so hotkeys and theme will match
- Mobile-specific setting: Settings → Mobile → "Capture" shortcut can open a new note directly from iPhone home screen via Shortcut
- Avoid editing the same daily note on both devices simultaneously — iCloud will create a conflict copy
