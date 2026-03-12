# YouTube Skill — Obsidian Integration Reference

How to route YouTube learning notes into the Yasmine-OS Obsidian vault.

---

## Folder Routing

| Video topic | Destination folder |
|------------|-------------------|
| AI / ML / LLMs / tech tools | `04-Knowledge/technology/` |
| Business / marketing / sales | `04-Knowledge/business/` |
| Creator / YouTube / content strategy | `04-Knowledge/content-creation/` |
| Personal development / productivity | `04-Knowledge/learning/` |
| Smarterflo-specific / AI consulting | `03-Areas/smarterflo/` |
| Unknown / general / doesn't fit above | `04-Knowledge/` (root) |

When in doubt about routing, ask the user: "Which folder should this go into?"

---

## Tag Taxonomy Mapping

Map generated video tags to the Yasmine-OS vault taxonomy:

| Raw tag from video | Mapped vault tag |
|-------------------|-----------------|
| `#ai` | `#tech/ai` |
| `#ml` or `#machine-learning` | `#tech/ai` |
| `#business` | `#smarterflo/strategy` |
| `#marketing` | `#smarterflo/marketing` |
| `#productivity` | `#learning/productivity` |
| `#youtube` | `#content-creation/youtube` |
| `#content` | `#content-creation` |
| `#coding` or `#programming` | `#tech/dev` |
| `#startup` | `#smarterflo/strategy` |
| `#finance` | `#business/finance` |
| Other / unrecognized | Keep as-is, lowercase, no spaces |

---

## Note Filename Convention

```
YYYY-MM-DD - {Video Title}.md
```

- Use **today's date** (not the upload date)
- Sanitize title: remove characters not allowed in filenames (`/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`)
- Truncate title to 80 characters if longer
- Example: `2026-03-09 - How to Build AI Agents That Actually Work.md`

---

## Exact obsidian-master Invocation

After notes are generated and user confirms save, invoke the `obsidian-master` skill with this exact format:

```
Create note at {destination_folder}/{filename} with content:
{full_notes_markdown}
```

Example:
```
Create note at 04-Knowledge/technology/2026-03-09 - How to Build AI Agents That Actually Work.md with content:
# How to Build AI Agents That Actually Work
...
```

---

## MOC Linking

After saving, suggest adding a link to the relevant MOC file:
- `04-Knowledge/technology/` → suggest linking from `04-Knowledge/_MOC-Technology.md`
- `04-Knowledge/business/` → suggest linking from `04-Knowledge/_MOC-Business.md`
- `04-Knowledge/content-creation/` → suggest linking from `04-Knowledge/_MOC-Content.md`
- `04-Knowledge/learning/` → suggest linking from `04-Knowledge/_MOC-Learning.md`

This follows the vault's zero-orphan rule: every note should have at least one parent link.
