# Template Examples — Part 1 (Templates 1–4)

Ready-to-use Templater templates for Yasmine's vaults.
Save each to `10-Templates/` in the vault, then configure Folder Templates in Templater settings.

---

## 1. Daily Note

Save as: `10-Templates/daily-note.md`
Folder trigger: `00-Daily-Notes/`

```markdown
<%*
const today = tp.date.now("YYYY-MM-DD");
const dayName = tp.date.now("dddd");
const displayDate = tp.date.now("MMMM D, YYYY");
const weekLabel = tp.date.now("YYYY-[W]WW");
const weekNote = weekLabel + " Weekly Review";
await tp.file.rename(today);
-%>
---
date: <% today %>
day: <% dayName %>
type: daily-note
tags: [daily]
energy:
mood:
intention:
week_link: "[[<% weekNote %>]]"
---

# <% displayDate %>

## Morning Check-In

**Energy (1–10):**
**Mood:**
**Intention:**
**Win condition:**

---

## Today's Focus

### Must Do
- [ ]
- [ ]
- [ ]

### Should Do
- [ ]
- [ ]

### If Time
- [ ]

---

## Notes & Captures

---

## Evening Reflection

**Wins:**

**What didn't happen, and why:**

**Carry forward:**

**Gratitude:**

---

## Links

- Week: [[<% weekNote %>]]
```

---

## 2. Meeting Note

Save as: `10-Templates/meeting-note.md`
Folder trigger: `03-Areas/smarterflo/meetings/`

```markdown
<%*
const title = await tp.system.prompt("Meeting title or client name");
const date = tp.date.now("YYYY-MM-DD");
const time = tp.date.now("HH:mm");
const fileName = date + " " + title;

const callType = await tp.system.suggester(
  ["Discovery", "Check-in", "Strategy", "Demo", "Follow-up", "Internal"],
  ["discovery", "check-in", "strategy", "demo", "follow-up", "internal"]
);
const status = await tp.system.suggester(
  ["Scheduled", "Completed", "Cancelled"],
  ["scheduled", "completed", "cancelled"]
);

// Select parent client profile to link to
const clientFiles = app.vault.getMarkdownFiles()
  .filter(f => f.path.startsWith("03-Areas/smarterflo/clients/"))
  .map(f => f.basename);
const parentClient = clientFiles.length > 0
  ? await tp.system.suggester(clientFiles, clientFiles, false, "Link to client profile (Esc to skip)")
  : null;

await tp.file.rename(fileName);
await tp.file.move("/03-Areas/smarterflo/meetings/" + fileName);
-%>
---
date: <% date %>
time: <% time %>
type: meeting
client: <% title %>
participants:
call_type: <% callType %>
status: <% status %>
tags: [meeting]
---

# <% title %> — <% tp.date.now("MMMM D, YYYY") %>

<%* if (parentClient) { %>
> Client: [[<% parentClient %>]]
<%* } %>

## Context

**Client / Company:** <%* if (parentClient) { %>[[<% parentClient %>]]<%* } else { tR += title; } %>
**Call type:** `= this.call_type`
**Participants:**

---

## Agenda

1.
2.
3.

---

## Key Points

-
-
-

---

## Pain Points / Decisions Made

**Pain points:**
**Decisions:**

## Action Items

| Action | Owner | Due |
|--------|-------|-----|
|  |  |  |

## Follow-Up

**Next meeting:**
**Send:**

## Raw Notes

## Links

<%* if (parentClient) { %>- Client: [[<% parentClient %>]]<%* } %>
- [[_MOC-Clients]]
```

---

## 3. Client Profile

Save as: `10-Templates/client-profile.md`
Folder trigger: `03-Areas/smarterflo/clients/`

```markdown
<%*
const company = await tp.system.prompt("Company name");
const contact = await tp.system.prompt("Primary contact name");
const contactEmail = await tp.system.prompt("Contact email");
const contactRole = await tp.system.prompt("Contact role / title");

const status = await tp.system.suggester(
  ["Prospect", "Active", "Paused", "Completed", "Lost"],
  ["prospect", "active", "paused", "completed", "lost"]
);
const source = await tp.system.suggester(
  ["Referral", "LinkedIn", "Inbound", "Cold Outreach", "Event", "Other"],
  ["referral", "linkedin", "inbound", "cold-outreach", "event", "other"]
);

await tp.file.rename(company);
-%>
---
company: <% company %>
contact: <% contact %>
contact_email: <% contactEmail %>
contact_role: <% contactRole %>
status: <% status %>
source: <% source %>
start_date: <% tp.date.now("YYYY-MM-DD") %>
contract_value:
next_action:
next_action_date:
type: client-profile
tags: [client]
---

# <% company %>

[[_MOC-Clients]]

## Overview

**Company:** <% company %>
**Primary contact:** <% contact %>
**Email:** <% contactEmail %>
**Role:** <% contactRole %>
**Status:** `= this.status`
**Source:** `= this.source`

---

## Project / Engagement

**What we're doing:**
**Contract value:**
**Key deliverables:**

## Communication Log

| Date | Type | Summary |
|------|------|---------|
| <% tp.date.now("YYYY-MM-DD") %> | Initial note | Profile created |

## Key Context

**Goals:**
**Pain points:**
**What they care about:**
**Red flags:**

## Notes

## Links

- [[_MOC-Clients]]
```

---

## 4. Project Note

Save as: `10-Templates/project-note.md`
Folder trigger: `02-Projects/business/`

```markdown
<%*
const projectName = await tp.system.prompt("Project name");

const status = await tp.system.suggester(
  ["Planning", "Active", "On Hold", "Completed", "Cancelled"],
  ["planning", "active", "on-hold", "completed", "cancelled"]
);
const startDate = tp.date.now("YYYY-MM-DD");
const client = await tp.system.prompt("Client or stakeholder (leave blank if internal)");

// Select parent note to link to
const parentCandidates = app.vault.getMarkdownFiles()
  .filter(f =>
    f.path.startsWith("03-Areas/smarterflo/clients/") ||
    f.path.startsWith("00-Command-Center/")
  )
  .map(f => f.basename);
const parent = parentCandidates.length > 0
  ? await tp.system.suggester(parentCandidates, parentCandidates, false, "Link to parent note (Esc to skip)")
  : null;

// Auto-route to campaigns or launches folder
const projectType = await tp.system.suggester(
  ["General project", "Campaign", "Launch"],
  ["business", "campaigns", "launches"]
);
const destFolder = "02-Projects/" + projectType + "/" + projectName;
await tp.file.rename(projectName);
await tp.file.move(destFolder);
-%>
---
project: <% projectName %>
status: <% status %>
start_date: <% startDate %>
deadline:
client: <% client %>
type: project
tags: [project]
parent: <%* if (parent) { tR += '"[[' + parent + ']]"'; } %>
---

# <% projectName %>

<%* if (parent) { %>
> Parent: [[<% parent %>]]
<%* } %>

## Summary

**Status:** `= this.status`
**Deadline:**
**Client / stakeholder:** <%* if (client) { tR += client; } %>
<%* if (parent) { %>**Parent:** [[<% parent %>]]<%* } %>

---

## Objectives

1.
2.
3.

---

## Milestones

| Milestone | Target Date | Done |
|-----------|-------------|------|
|  |  | [ ] |
|  |  | [ ] |
|  |  | [ ] |

---

## Tasks

```dataview
TASK
FROM [[<% projectName %>]]
WHERE !completed
SORT file.mtime DESC
```

---

## Resources & References

-

## Notes & Decisions

## Links

<%* if (parent) { %>- Parent: [[<% parent %>]]<%* } %>
- [[00-Command-Center/Business-Decisions-Log]]
```

→ See TEMPLATES-EXAMPLES-2.md for Templates 5–8
