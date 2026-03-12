# Obsidian Workflows

Seven end-to-end workflows for Yasmine. Each is a numbered sequence — not general advice.

---

## 1. Morning Routine

1. Open Yasmine-OS vault
2. Open or create today's Daily Note — Templater auto-applies the Daily Note template (date, intentions, tasks query, yesterday's reflection prompt)
3. Check the Tasks query block at the top of the Daily Note — shows all tasks due today or overdue across the vault
4. Switch to Calendar plugin (sidebar) — confirm scheduled events, deadlines, or blocks
5. Write 3 intentions for the day in the Intentions section of the Daily Note
6. Check Inbox folder — if any notes landed overnight from clips, voice memos, or Claude output, log them as items to process in today's note
7. Close and begin work

---

## 2. Capture → Process → File

### Capture (anytime)
1. Create a new note in `00-Inbox/` — title is temporary, content is raw
2. Tag it `#inbox` — no other processing at capture time
3. If captured via web clip (Obsidian Web Clipper): it lands in `00-Inbox/` automatically

### Process (once daily — during morning routine or end of day)
1. Open `00-Inbox/` — review every note tagged `#inbox`
2. For each note, decide:
   - Is it actionable? → Add task(s), keep note or move to appropriate PARA folder
   - Is it a project? → Move to `02-Projects/`
   - Is it an area of ongoing responsibility? → Move to `03-Areas/`
   - Is it reference material? → Move to `04-Resources/`
   - Is it pure archival? → Move to `05-Archive/`
   - Is it noise? → Delete
3. Remove `#inbox` tag after filing
4. Inbox should be empty at end of each process pass

---

## 3. Research Workflow

1. Capture raw content — web clip, paste, or manual notes → lands in `00-Inbox/` or `04-Resources/`
2. Create a **Literature Note** in `04-Resources/` — title: `LIT - [Source Title]`, frontmatter: `type: literature`, `source:`, `author:`, `date_read:`
3. Summarize key ideas in your own words in the Literature Note — do not quote extensively
4. Create a **Permanent Note** in `04-Resources/knowledge/` or appropriate subfolder — title: your own insight or synthesis
5. In the Permanent Note:
   - Write your own analysis — not a summary of the source
   - Add `[[wikilinks]]` to related existing notes
   - Add relevant tags from the vault tag taxonomy
6. Back in the Literature Note: add `[[wikilink]]` to the Permanent Note(s) it generated
7. Open the Graph View — verify the new note connects to at least 2 existing nodes; if it floats isolated, add more links or reconsider filing location

---

## 4. Client Work Workflow

1. Create a **Client Profile Note** in `03-Areas/smarterflo/clients/` using the `_client-template` — fill in: name, company, contact, status, engagement type
2. Create a **Project Note** in `02-Projects/` — frontmatter: `client: [[Client Name]]`, `status: active`, `type: client-project`
3. Link the Project Note back to the Client Profile with a `[[wikilink]]`
4. For the discovery call: create a **Meeting Note** in `02-Projects/[project-name]/meetings/` — use the Meeting Note template, record date, attendees, key points, open questions
5. In the Meeting Note: add all action items as Tasks plugin checkboxes: `- [ ] Task description [due:: YYYY-MM-DD]`
6. Log all decisions made in the meeting in a **Decisions** section — each decision as a bullet with rationale
7. Update the Project Note frontmatter `status:` as the engagement progresses: `active` → `in-review` → `completed`
8. After each client touchpoint: run a quick pass on the Client Profile to keep it current

---

## 5. Content Creation Workflow

1. Capture content idea using the Content Idea template in `03-Areas/smarterflo/content/ideas/` — fields: topic, angle, platform, hook, status: `idea`
2. When ready to draft: change `status: draft`, move to `03-Areas/smarterflo/content/drafts/`
3. Write the full draft in Obsidian — use the platform's format (LinkedIn post, email, short-form, etc.)
4. Self-review against brand voice — check: is this Yasmine's voice, or does it sound like an AI?
5. **Mandatory before publishing:** Pass through `de-ai-fy` skill — `Skill(skill: "de-ai-fy", args: "[content]")`
6. Get humanized version back — update the note with the final copy, change `status: ready-to-publish`
7. Publish to platform (manually or via scheduling tool)
8. After publishing: change `status: published`, add `published_date:` frontmatter, move to `03-Areas/smarterflo/content/published/`

---

## 6. Weekly Review

1. Open the Weekly Note via Periodic Notes plugin — Templater auto-applies the Weekly Review template
2. Run the Dataview query block in the Weekly Note — shows: all notes created this week, tasks completed, tasks still open
3. Review tasks completed vs. pending:
   - For each completed task: confirm it's marked done (`- [x]`)
   - For each pending task: is it still valid? Reschedule or cancel
4. Review project statuses:
   - Open each active Project Note — update `status:` frontmatter if changed
   - Any project completed? Move to `05-Archive/`
5. Review content created this week — any drafts that should be moved to `ready-to-publish`?
6. Set next week priorities — write 3–5 priority items in the Weekly Note's "Next Week" section
7. Create or update tasks for next week's priorities with `[due:: YYYY-MM-DD]` tags
8. Close the review — save the Weekly Note, confirm Inbox is empty

---

## 7. AI Output → Vault

### Short outputs (decisions, research findings, meeting summaries)
1. Claude generates content
2. obsidian-master saves to correct vault folder:
   - Decisions → `00-Command-Center/Business-Decisions-Log.md` (append)
   - Research findings → `04-Resources/` appropriate subfolder (new note)
   - Competitor intelligence → `04-Resources/competitors/` (competitor profile note)
3. obsidian-master confirms path and note title with Yasmine before writing

### Long documents (reports, SOPs, proposals, strategy docs)
1. Claude generates content
2. obsidian-master creates note in Obsidian first (correct vault + folder)
3. Ask Yasmine: "Do you want this in Google Docs for sharing?"
4. If yes: signal google-workspace skill → create Google Doc → return link → obsidian-master writes `gdoc_link: [url]` in note frontmatter
5. If document is client-facing or outward-facing: **run through de-ai-fy before Google Docs creation**

### Outward-facing content (posts, emails, copy)
1. Claude generates content
2. obsidian-master saves draft to vault in appropriate folder
3. **Before any further action:** run through de-ai-fy skill — non-negotiable
4. Get humanized version → update note → mark `status: ready-to-publish`
5. Ask Yasmine: "Do you want to save this to Obsidian? Which folder?" (unless auto-destination is clear)

### Decision log entries (auto-sync, no confirmation needed)
1. Append to `00-Command-Center/Business-Decisions-Log.md` with: date, decision, rationale, outcome expected
2. No confirmation required for this destination
