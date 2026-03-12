# Yasmine's Vault Map

Detailed reference for the two primary vaults. Use this to route content and understand existing structure.

---

## 1. Yasmine-OS Vault

**Path:** `/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Yasmine-OS/`

**Purpose:** Personal knowledge OS — life, learning, systems, personal projects. Being built from scratch.

**Current state:** Nearly empty. Contains only `copilot/copilot-custom-prompts/`. Needs full PARA scaffolding.

**Installed plugins:**

| Plugin | Use |
|--------|-----|
| Excalidraw | Diagrams and visual thinking |
| Templater | Dynamic templates with variables and scripts |
| Dataview | SQL-like queries over vault notes |
| Calendar | Date-based navigation sidebar |
| Style Settings | Custom CSS theming |
| Omnisearch | Full-text search with fuzzy matching |
| Copilot | AI chat inside Obsidian |
| Homepage | Open a specific note on vault launch |
| Tasks | Checkbox task management with queries |
| Pexels Banner | Auto banner images for notes |
| Local REST API | HTTP API for external integrations — **port 27123** |
| Advanced URI | Deep-link into specific notes via URI |
| RSS Dashboard | RSS feed aggregator |
| Custom Note Width | Per-note reading width |
| Auto Classifier | Auto-suggest note folders on creation |

**REST API:** Enabled. Get API key:

```bash
cat "/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Yasmine-OS/.obsidian/plugins/obsidian-local-rest-api/data.json" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('apiKey',''))"
```

**Target folder structure (PARA — needs to be created):**

```
00-Dashboard/
01-Projects/
02-Areas/
03-Resources/
04-Archive/
05-Templates/
06-Inbox/
```

Use `VAULT-SCAFFOLDING.md` to run the full setup.

---

## 2. Smarterflo Vault

**Path:** `/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Smarterflo/`

**Purpose:** Smarterflo AI consulting business — clients, content, decisions, brand, strategy.

**Status:** Active, fully populated. Do not reorganize without asking.

**Folder structure:**

| Folder | Contents |
|--------|----------|
| `00-Command-Center/` | Hub note, business decisions log, quick reference |
| `02-Projects/` | Active business projects |
| `02-Projects/business/campaigns/` | Active campaigns |
| `02-Projects/business/launches/` | Product and service launches |
| `03-Areas/smarterflo/clients/` | Client profiles (use `_client-template`) |
| `03-Areas/smarterflo/processes/` | SOPs and operational workflows |
| `03-Areas/smarterflo/pricing/` | Pricing master and service offers |
| `04-Knowledge/` | Research findings, general knowledge |
| `04-Knowledge/competitors/` | Competitor profiles (use `_competitor-template`) |
| `05-Dev-Context/self-healing/` | Error patterns and dev fixes |
| `05-Dev-Context/self-healing/patterns/` | Individual self-healing pattern notes |
| `10-Templates/` | Vault templates |
| `15-Smarterflo/Brand-Strategy/` | Brand docs, positioning, identity |
| `15-Smarterflo/LinkedIn-Strategy/` | LinkedIn content, strategy, posts |
| `15-Smarterflo/Social-Profiles/` | Social media profiles and strategy |

**Key single files:**

| File | Purpose |
|------|---------|
| `00-Command-Center/Business-Decisions-Log.md` | Append all significant decisions here |
| `15-Smarterflo/Brand-Strategy/Design-System.md` | Smarterflo design system |
| `15-Smarterflo/Brand-Strategy/Canva-Branding-Plan.md` | Canva asset inventory |

---

## 3. Content Routing Rules

When writing content to a vault, use this table to determine destination.

| Content Type | Vault | Folder / File |
|-------------|-------|---------------|
| Business decision | Smarterflo | `00-Command-Center/Business-Decisions-Log.md` (append) |
| Client profile | Smarterflo | `03-Areas/smarterflo/clients/{client-name}.md` |
| Research finding | Smarterflo | `04-Knowledge/{topic}/` |
| Competitor intel | Smarterflo | `04-Knowledge/competitors/{competitor}.md` |
| SOP / process | Smarterflo | `03-Areas/smarterflo/processes/{process-name}.md` |
| Dev error pattern | Smarterflo | `05-Dev-Context/self-healing/patterns/SH-{title}.md` |
| Brand / design | Smarterflo | `15-Smarterflo/Brand-Strategy/` |
| LinkedIn content | Smarterflo | `15-Smarterflo/LinkedIn-Strategy/` |
| Active campaign | Smarterflo | `02-Projects/business/campaigns/` |
| Personal note | Yasmine-OS | `06-Inbox/` (then file during inbox processing) |
| Learning / study | Yasmine-OS | `03-Resources/{topic}/` |
| Personal project | Yasmine-OS | `01-Projects/{project-name}/` |
| Life planning | Yasmine-OS | `02-Areas/{area}/` |
| Daily note | Yasmine-OS | `00-Dashboard/` or plugin-managed |
