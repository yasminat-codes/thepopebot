# Skill Integrations

obsidian-master integrates with 4 other skills. Always offer integration explicitly before triggering. Never invoke silently.

---

## 1. google-workspace

**When to trigger:**
- Long documents created in Obsidian that need to be shared externally
- Client reports, proposals, SOPs, strategy docs, anything sent to a non-Obsidian reader

**Trigger keywords:** "share with client", "create Google Doc", "send this", "make shareable", "put this in Drive"

**Handoff protocol:**

| Step | Action |
|------|--------|
| 1 | obsidian-master creates or confirms the note exists in Obsidian |
| 2 | Ask Yasmine: "Would you like me to push this to Google Docs for sharing?" |
| 3 | If yes: invoke `Skill(skill: "google-workspace", args: "create doc: [title], content: [note content]")` |
| 4 | google-workspace returns Google Doc URL |
| 5 | obsidian-master writes `gdoc_link: [url]` into the note's frontmatter |
| 6 | Confirm to Yasmine: "Google Doc created: [url] — link saved to note frontmatter." |

**Note:** If the document is client-facing, run de-ai-fy **before** the Google Docs handoff.

---

## 2. de-ai-fy

**When to trigger:**
- Any vault content going to LinkedIn, email, social media, or any external audience
- Note has `status: ready-to-publish` frontmatter
- User says "publish", "send this", "post this", "share this", or "draft email"

**Mandatory for:**
- LinkedIn posts and comments
- Cold email drafts
- Client-facing documents
- Any social media content captured in the vault
- Newsletters and announcements

**Protocol:**

| Step | Action |
|------|--------|
| 1 | Content written and saved in vault |
| 2 | obsidian-master detects outward-facing intent (status or keyword) |
| 3 | Proactively remind: "This content is going external — it needs to go through de-ai-fy first." |
| 4 | Invoke `Skill(skill: "de-ai-fy", args: "[content]")` |
| 5 | Receive humanized version |
| 6 | Update the vault note with the humanized copy |
| 7 | Set `status: ready-to-publish` in frontmatter |

**Do not skip this step.** If Yasmine says "just publish it", remind her that de-ai-fy is non-negotiable for brand integrity, then proceed if she confirms.

---

## 3. densify

**When to trigger:**
- Long vault notes (>60 lines) being fed into other Claude sessions or LLM pipelines
- User asks to "summarize this note for Claude", "densify this", "condense for LLM", "prepare this for an agent"
- Research notes, decision logs, or long-form drafts being used as LLM input

**Protocol:**

| Step | Action |
|------|--------|
| 1 | obsidian-master reads the note |
| 2 | Confirm with Yasmine: "This note is [N] lines — would you like me to densify it for LLM use?" |
| 3 | If yes: invoke `Skill(skill: "densify", args: "[file-path or content]")` |
| 4 | Receive condensed version from densify |
| 5 | Show condensed version to Yasmine |
| 6 | Offer to save as a separate note: `[original-name]-condensed.md` in same folder |
| 7 | If Yasmine approves: write the condensed note |

The original note is never modified by densify unless Yasmine explicitly requests in-place overwrite.

---

## 4. task-master

**When to trigger:**
- A vault note contains action items that need tracking outside Obsidian
- User says "extract tasks from this note", "send to task master", "track these action items", "put these in the task system"

**Protocol:**

| Step | Action |
|------|--------|
| 1 | obsidian-master reads the note and identifies all checkbox items (`- [ ]`) and action-oriented text |
| 2 | Preview extracted action items for Yasmine's confirmation |
| 3 | If confirmed: invoke `Skill(skill: "task-master", args: "create tasks: [list of tasks with due dates]")` |
| 4 | task-master returns task IDs or confirmation |
| 5 | obsidian-master optionally embeds task links back in the note if task-master provides them |

---

## 5. Invocation Pattern

All integrations are Claude Code skills. Use the Skill tool:

```
Skill(skill: "google-workspace", args: "...")
Skill(skill: "de-ai-fy", args: "...")
Skill(skill: "densify", args: "...")
Skill(skill: "task-master", args: "...")
```

**Rule:** Always explicitly offer each integration before triggering. No silent invocations.

Example offer pattern:
- "Would you like me to also push this to Google Docs?"
- "This note is going external — I'll run it through de-ai-fy first."
- "There are 4 action items here — want me to route them to task-master?"
