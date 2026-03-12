# Vault Operations Reference

How to interact with Obsidian vaults. Always attempt in priority order: REST API → obsidian-cli → direct file operations.

---

## 1. Execution Priority

Before any read or write, determine which method is available:

```
REST API available?  →  YES → use REST API for all operations
      ↓ NO
obsidian-cli available?  →  YES → use obsidian-cli
      ↓ NO
Direct file operations (Read/Write/Edit tools)
```

Run the availability check every session. Do not assume the API is running.

---

## 2. REST API Operations (obsidian-local-rest-api)

Yasmine-OS vault runs the REST API on port 27123.

### Get the API Key

```bash
cat "/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Yasmine-OS/.obsidian/plugins/obsidian-local-rest-api/data.json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('apiKey',''))"
```

Store the key as `OBSIDIAN_API_KEY` for the session.

### Check if API is Running

```bash
curl -s -o /dev/null -w "%{http_code}" \
  "http://localhost:27123/vault/" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY"
# 200 = running, anything else = not available
```

### List Vault Files

```bash
curl -s "http://localhost:27123/vault/" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY"
```

Returns JSON with all vault file paths.

### Read a Note

```bash
curl -s "http://localhost:27123/vault/00-Dashboard/Home.md" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY"
```

Returns raw markdown content of the note. Encode path segments with `%20` for spaces.

### Create or Overwrite a Note (PUT)

```bash
curl -s -X PUT "http://localhost:27123/vault/03-Areas/clients/acme.md" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY" \
  -H "Content-Type: text/markdown" \
  --data-binary "# Acme Corp

Client added: 2026-03-08
"
```

PUT creates the note if it does not exist, or fully replaces it if it does. Use when you want to set the complete content.

### Append to a Note (POST)

```bash
curl -s -X POST "http://localhost:27123/vault/00-Command-Center/Business-Decisions-Log.md" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY" \
  -H "Content-Type: text/markdown" \
  --data-binary "
## Decision: Switch to annual billing
**Date:** 2026-03-08
**Reasoning:** Reduces churn, improves cash flow.
"
```

POST appends to the end of an existing note. If the note does not exist, it creates it.

### Delete a Note

```bash
curl -s -X DELETE "http://localhost:27123/vault/Inbox/old-note.md" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY"
```

Returns 204 on success.

### Search Vault Content

```bash
curl -s -X POST "http://localhost:27123/search/simple/?query=Smarterflo+pricing" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY" \
  -H "Content-Type: application/json"
```

Returns list of matching notes with score and content excerpts. URL-encode the query string.

### Open a Note in Obsidian

```bash
curl -s -X POST "http://localhost:27123/open/00-Dashboard/Home.md" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY"
```

Opens the note in the Obsidian desktop app immediately.

### URL Encoding for Paths with Spaces

Paths with spaces must be percent-encoded in the URL:

```bash
# Encode path before use
NOTE_PATH="03-Areas/smarterflo/clients/Big Client.md"
ENCODED_PATH=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$NOTE_PATH")
curl -s "http://localhost:27123/vault/$ENCODED_PATH" \
  -H "Authorization: Bearer $OBSIDIAN_API_KEY"
```

---

## 3. obsidian-cli Operations (Fallback)

Use when the REST API is not running. obsidian-cli handles wikilink integrity on moves.

### Set Default Vault

```bash
obsidian-cli set-default "Yasmine-OS"
# or
obsidian-cli set-default "Smarterflo"
```

Always set before running other commands.

### Search Note Names

```bash
obsidian-cli search "client profile"
```

Returns matching note names. Does not search note content.

### Search Note Content

```bash
obsidian-cli search-content "Smarterflo pricing strategy"
```

Returns notes containing the query string in their body.

### Create a Note

```bash
obsidian-cli create "04-Knowledge/topics/ai-consulting.md" \
  --content "# AI Consulting

Notes on consulting approaches." \
  --open
```

`--open` opens the note in Obsidian after creation. Omit to create silently.

### Move a Note (Safe — Updates Wikilinks)

```bash
obsidian-cli move "Inbox/rough-idea.md" "02-Projects/q1-launch/rough-idea.md"
```

This is the only safe way to move notes. Direct file moves via bash or the Write tool will break wikilinks throughout the vault.

### Delete a Note

```bash
obsidian-cli delete "Archive/old-project.md"
```

---

## 4. Direct File Operations (Last Resort)

Use the Read, Write, and Edit tools directly on vault `.md` files when neither the REST API nor obsidian-cli is available.

**Vault base paths:**

| Vault | Base Path |
|-------|-----------|
| Yasmine-OS | `/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Yasmine-OS/` |
| Smarterflo | `/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Smarterflo/` |

**Safe operations:**
- Reading any note (Read tool)
- Creating new files that have no existing wikilinks pointing to them (Write tool)
- Editing note content in-place (Edit tool)

**Not safe:**
- Moving or renaming files — will silently break all `[[wikilinks]]` pointing to that note
- Deleting files — no undo, and leaves dangling wikilinks

**Example: read a note directly**

```
Read: /Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Smarterflo/00-Command-Center/Business-Decisions-Log.md
```

---

## 5. Pre-Write Checklist

Run through this before executing any write operation:

- [ ] Correct vault identified (see VAULT-DETECTION.md)
- [ ] Note path follows vault folder conventions (see YASMINE-VAULTS.md)
- [ ] For appends: note already exists, or creating it is intentional
- [ ] For overwrites (PUT): confirmed with user that existing content will be replaced
- [ ] For moves: using obsidian-cli, not bash mv or file tools
- [ ] API key fetched and verified if using REST API
- [ ] Path-encoded if note title contains spaces or special characters
