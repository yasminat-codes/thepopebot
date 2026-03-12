# Vault Detection Reference

How to determine which vault to use before any operation.

---

## 1. Reading Which Vault Is Currently Open

Obsidian stores vault state at:

```
~/Library/Application Support/obsidian/obsidian.json
```

The vault with `"open": true` is the one currently open in the app.

```bash
python3 -c "
import json, os
path = os.path.expanduser('~/Library/Application Support/obsidian/obsidian.json')
with open(path) as f:
    data = json.load(f)
vaults = data.get('vaults', {})
for vid, v in vaults.items():
    if v.get('open'):
        print('Active vault:', v.get('path', ''))
"
```

This is informational only. Even if a vault is open in the app, use the routing rules below to choose the right vault for the task.

---

## 2. Yasmine's 6 Known Vaults

All vaults live under: `/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/`

| Vault Name | Folder | Primary Use |
|------------|--------|-------------|
| Yasmine-OS | `Yasmine-OS/` | Personal knowledge OS — life, learning, systems, personal projects |
| Smarterflo | `Smarterflo/` | Smarterflo AI consulting business — clients, content, decisions |
| Digital Mindspace | `Digital Mindspace/` | Older personal knowledge base |
| Life OS | `Life OS/` | Personal life planning and tracking |
| Openclaw Agents | `Openclaw Agents/` | OpenClaw platform agent notes |
| Yasmine's Digital Mind | `Yasmine's Digital Mind/` | Legacy personal vault |

**Primary vaults for new work:** Yasmine-OS and Smarterflo. Default all routing to one of these two unless the user specifies otherwise.

---

## 3. When to Ask vs When to Assume

Use the signal words in the request to infer the vault before asking.

**Assume Smarterflo when the request mentions:**
- "Smarterflo", "business", "clients", "client profile"
- "content", "LinkedIn", "social media", "post", "brand"
- "decisions log", "SOPs", "processes", "pricing"
- "competitor", "research findings", "dev context", "self-healing"

**Assume Yasmine-OS when the request mentions:**
- "Yasmine-OS", "personal OS", "personal vault", "my vault"
- "building the vault", "set up vault", "scaffold"
- "personal notes", "life", "learning"
- "dashboard", "home note", "daily note"

**Ask when:**
- The request is ambiguous (no signal words)
- The content could reasonably belong in either vault
- The user is creating a template or structural change that should go in a specific vault

---

## 4. Vault Selection Question Template

When you need to ask, use this exact pattern with AskUserQuestion:

```
Question: Which vault should this go in?

Options:
  A) Smarterflo — business, clients, content, decisions
  B) Yasmine-OS — personal OS, life, learning, systems
  C) A different vault — I'll specify

(If C is chosen, follow up with the full list of 6 vaults from the table above.)
```

Do not ask inline in response text. Always use the AskUserQuestion tool.

---

## 5. Bash: Find the Active Vault

```bash
python3 << 'EOF'
import json, os

obsidian_config = os.path.expanduser(
    "~/Library/Application Support/obsidian/obsidian.json"
)

try:
    with open(obsidian_config) as f:
        data = json.load(f)
    vaults = data.get("vaults", {})
    active = [v for v in vaults.values() if v.get("open")]
    if active:
        print("Open vault:", active[0].get("path", "unknown"))
    else:
        print("No vault currently open in Obsidian")
except FileNotFoundError:
    print("Obsidian config not found — app may not be installed or not run yet")
EOF
```
