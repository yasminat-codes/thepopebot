# TASK-TEMPLATE.md — The Non-Negotiable Task File Standard

Every file task-master generates MUST follow this standard exactly.
No section may be omitted. No section may be left empty.

---

## Section 1: The Complete Task File Template

```markdown
# Task {NNN}: {Title}
**Status:** pending
**BlockedBy:** — (or [NNN, NNN])
**Blocks:** — (or [NNN, NNN])
**Plan source:** plans/{system}/03-implementation.md § {Section heading}
**Live API:** Yes ({SERVICE_API_KEY}) | No
**Est. context:** {small | medium | large}

---

## Summary

{1–2 sentences. Describe what gets created or changed — not what the system does.
Example: "Create `.claude/skills/email-parser/references/EXTRACTION-PATTERNS.md`
covering the regex and heuristic patterns the skill uses to extract structured data."}

---

## Files to Read Before Starting

- `.claude/skills/{name}/SKILL.md` — understand the skill's tier, directives, and existing references
- `.claude/skills/{name}/references/{RELATED}.md` — most closely related existing reference file (pattern to follow)
- `.claude/MISTAKES.md` — grep for `{relevant_keyword}` before starting
- `.claude/context/CODE_QUALITY_RULES.md` — style conventions for skill/reference files

---

## Relevant Rules

- `.claude/rules/task-management.md` — task lifecycle: pending → in-progress → completed
- `.claude/rules/code-quality.md` — line limits, formatting, no placeholder content
- `.claude/rules/context-loading.md` — read file fully before editing; check MISTAKES.md
{conditional rules based on task type — see RULES-INJECTION.md §matching-matrix}

---

## Files to Modify or Create

| Action   | Path                                                        | What Changes                                         |
|----------|-------------------------------------------------------------|------------------------------------------------------|
| CREATE   | `.claude/skills/{name}/references/{FILE}.md`                | New reference file, full content                     |
| MODIFY   | `.claude/skills/{name}/SKILL.md`                            | Add `→ See references/{FILE}.md` directive           |
| MODIFY   | `.claude/skills/{name}/README.md`                           | Add row to Reference Files table                     |

---

## Implementation Checklist

- [ ] {Step 1: Create the reference file with all required sections}
      — Success: `wc -l .claude/skills/{name}/references/{FILE}.md` reports ≥ 50 lines
- [ ] {Step 2: Verify content completeness — no unfilled placeholders}
      — Success: `grep -c "{placeholder}" .claude/skills/{name}/references/{FILE}.md` returns 0
- [ ] {Step 3: Add → directive to SKILL.md}
      — Success: `grep "→ See references/{FILE}" .claude/skills/{name}/SKILL.md` returns a match
- [ ] {Step 4: Update README.md reference table}
      — Success: `grep "{FILE}" .claude/skills/{name}/README.md` returns the table row
- [ ] {Step 5: Validate task file structure}
      — Success: `bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending` exits 0

---

## Success Criteria

1. Reference file exists with content: `wc -l .claude/skills/{name}/references/{FILE}.md` ≥ 50 lines
2. SKILL.md directive present: `grep "→ See references/{FILE}" .claude/skills/{name}/SKILL.md` returns a match
3. validate-tasks.sh exits 0: `bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending` exits 0
4. SKILL.md line count within tier limit: `wc -l .claude/skills/{name}/SKILL.md` ≤ 600
5. {Skill-specific criterion — e.g., "All → See directives in SKILL.md resolve to files that exist"}

---

## Testing

### Skill Validation

**Method:** Read the generated skill file(s) and verify structural completeness
**Checks:**
- [ ] SKILL.md is within the 600-line Tier limit
- [ ] Every `→ See references/X.md` directive points to a file that exists
- [ ] Every agent listed in `## Agent Definitions` has a corresponding file in `agents/`
- [ ] Every script listed in `## Scripts` has a corresponding file in `scripts/`
- [ ] All hooks listed in `## Hooks` exist in `hooks/`

### Manual Invocation Test

**Method:** Invoke the skill with a simple test prompt and verify it completes without errors
**Pass condition:** Skill reaches its delivery report without halting on a missing file

### Live API Tests (include only when the task calls an external service)

**Requires:** `{SERVICE_API_KEY}` in `.env`
**What it validates:** {name the specific service called and what a successful response looks like}
**Stub if key missing:**
```
# BLOCKED: {SERVICE_API_KEY} not in .env
# Add to tests/test-cases.md once key is available
```

---

## Task Management

At task start, run:

```bash
mv tasks/_pending/{NNN}-{slug}.md tasks/_in-progress/{NNN}-{slug}.md
```

At task complete (all checks pass), run:

```bash
mv tasks/_in-progress/{NNN}-{slug}.md tasks/_completed/{NNN}-{slug}.md
```

---

## Definition of Done

- [ ] All items in Implementation Checklist are checked
- [ ] All Success Criteria are met (commands verified, not assumed)
- [ ] `bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending` exits 0
- [ ] SKILL.md line count ≤ 600 (Tier limit)
- [ ] All `→ See references/X.md` directives resolve to files that exist on disk
- [ ] No broken agent paths (every agent in `## Agent Definitions` has a file)
- [ ] Mistakes logged (if any): append to `.claude/MISTAKES.md` — format:
  `### [DATE] <title> | Wrong: <1 line> | Fix: <1 line> | Rule: <1 imperative>`
  Skip entirely if no bugs or wrong approaches were encountered.
- [ ] Task file moved to `tasks/_completed/`
```

---

## Section 2: Writing Rules

These eight rules are non-negotiable. Violating any of them is a defect in the generated task file.

**Rule 1: Every checklist item ends with a Success criterion.**
Format: `— Success: {verifiable command or specific observable result}`.
"It works" is not a success criterion. `uv run pytest tests/unit/test_foo.py -v` exits 0 is.

**Rule 2: Testing section MUST include a live API test if an integration service is referenced AND the .env key exists.**
If a task touches Stripe, OpenAI, Redis, Twilio, or any third-party, look for the key in `.env`.
If the key is present: write a real `@pytest.mark.live` test.
If the key is absent: include the stub block marked `# BLOCKED: {KEY} not in .env`.

**Rule 3: No task file exceeds ~100 lines.**
If the implementation requires more than ~100 lines of task description, the task is too large.
Split it: create sub-tasks named `{NNN}a`, `{NNN}b`, etc., each within the line limit.
The parent task file should list the sub-tasks in its Summary and have BlockedBy logic updated.

**Rule 4: All file paths must be relative to skill root.**
Write `.claude/skills/{name}/references/FOO.md`, not `./references/FOO.md` or absolute paths.
The skill root is the `.claude/` directory.

**Rule 5: Success Criteria item 3 is always the validate-tasks.sh check.**
Exactly: `bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending` exits 0`.
This is always item 3. Items 1, 2, 4, 5 are task-specific.

**Rule 6: Summary describes files created or changed, not system behavior.**
Bad: "This task adds extraction patterns to the skill."
Good: "Create `.claude/skills/email-parser/references/EXTRACTION-PATTERNS.md` covering
the regex and heuristic patterns used to extract structured data from email bodies."

---

## Section 3: Complete Worked Example

```markdown
# Task 003: Add Extraction Patterns Reference to email-parser Skill
**Status:** pending
**BlockedBy:** [001, 002]
**Blocks:** [004]
**Plan source:** plans/email-parser/03-implementation.md § Phase 2: Reference Files
**Live API:** No
**Est. context:** small

---

## Summary

Create `.claude/skills/email-parser/references/EXTRACTION-PATTERNS.md` documenting
the regex and heuristic patterns the skill uses to extract structured data (subject,
sender, dates, action items) from raw email bodies.

---

## Files to Read Before Starting

- `.claude/skills/email-parser/SKILL.md` — skill tier, existing → directives, line budget
- `.claude/skills/email-parser/references/OUTPUT-SCHEMA.md` — existing reference to follow as pattern
- `.claude/MISTAKES.md` — grep for "email-parser" or "reference" before starting
- `.claude/context/CODE_QUALITY_RULES.md` — style conventions for reference files

---

## Relevant Rules

- `.claude/rules/task-management.md` — task lifecycle: pending → in-progress → completed
- `.claude/rules/code-quality.md` — line limits, formatting, no placeholder content
- `.claude/rules/context-loading.md` — read file fully before editing; check MISTAKES.md
- `.claude/rules/research-first.md` — search codebase + GREP MCP before writing new reference

---

## Files to Modify or Create

| Action   | Path                                                              | What Changes                                        |
|----------|-------------------------------------------------------------------|-----------------------------------------------------|
| CREATE   | `.claude/skills/email-parser/references/EXTRACTION-PATTERNS.md`  | New reference file, full extraction pattern content |
| MODIFY   | `.claude/skills/email-parser/SKILL.md`                           | Add `→ See references/EXTRACTION-PATTERNS.md` line  |
| MODIFY   | `.claude/skills/email-parser/README.md`                          | Add row to Reference Files table                    |

---

## Implementation Checklist

- [ ] Create `EXTRACTION-PATTERNS.md` with sections: subject extraction, sender parsing, date detection, action item heuristics
      — Success: `wc -l .claude/skills/email-parser/references/EXTRACTION-PATTERNS.md` ≥ 60 lines
- [ ] Verify no unfilled placeholders remain in the file
      — Success: `grep -c "{placeholder}" .claude/skills/email-parser/references/EXTRACTION-PATTERNS.md` returns 0
- [ ] Add directive to SKILL.md under Reference Files Manifest
      — Success: `grep "→ See references/EXTRACTION-PATTERNS" .claude/skills/email-parser/SKILL.md` returns a match
- [ ] Add row to README.md Reference Files table
      — Success: `grep "EXTRACTION-PATTERNS" .claude/skills/email-parser/README.md` returns the table row
- [ ] Run validate-tasks.sh to confirm task file is still well-formed
      — Success: `bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending` exits 0

---

## Success Criteria

1. Reference file exists with content: `wc -l .claude/skills/email-parser/references/EXTRACTION-PATTERNS.md` ≥ 60 lines
2. SKILL.md directive present: `grep "→ See references/EXTRACTION-PATTERNS" .claude/skills/email-parser/SKILL.md` returns a match
3. validate-tasks.sh exits 0: `bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending` exits 0
4. SKILL.md line count within tier limit: `wc -l .claude/skills/email-parser/SKILL.md` ≤ 600
5. All → See directives in SKILL.md resolve to files that exist: `grep "→ See references/" .claude/skills/email-parser/SKILL.md | while read -r line; do file=$(echo "$line" | grep -oP "references/[^\s]+"); [ -f ".claude/skills/email-parser/$file" ] || echo "MISSING: $file"; done` outputs nothing

---

## Testing

### Skill Validation

**Method:** Read the generated skill file(s) and verify structural completeness
**Checks:**
- [ ] SKILL.md is within the 600-line Tier limit (`wc -l` ≤ 600)
- [ ] Every `→ See references/X.md` directive points to a file that exists
- [ ] No placeholder text `{...}` remains in `EXTRACTION-PATTERNS.md`
- [ ] README.md table row for EXTRACTION-PATTERNS.md is present

### Manual Invocation Test

**Method:** Invoke the email-parser skill with a sample email prompt and verify it references extraction patterns correctly
**Pass condition:** Skill produces structured output and does not halt on a missing reference

### Live API Tests

No external service required for this reference file task.

---

## Task Management

At task start, run:

```bash
mv tasks/_pending/003-extraction-patterns-reference.md tasks/_in-progress/003-extraction-patterns-reference.md
```

At task complete (all checks pass), run:

```bash
mv tasks/_in-progress/003-extraction-patterns-reference.md tasks/_completed/003-extraction-patterns-reference.md
```

---

## Definition of Done

- [ ] All Implementation Checklist items checked
- [ ] All 5 Success Criteria verified by running the listed commands
- [ ] `bash .claude/skills/task-master/scripts/validate-tasks.sh tasks/_pending` exits 0
- [ ] `wc -l .claude/skills/email-parser/SKILL.md` ≤ 600
- [ ] All `→ See references/X.md` directives in SKILL.md resolve to files on disk
- [ ] No `{placeholder}` content in any created file
- [ ] Mistakes logged (if any): `### [2026-03-04] directive format | Wrong: used "See:" prefix | Fix: use "→ See references/" format | Rule: Always match existing directive format in SKILL.md`
  Skip if no bugs encountered.
- [ ] Task file moved to `tasks/_completed/`
```

---

## Section 4: Anti-Patterns Table

| Anti-Pattern                              | Why It's a Defect                                                                 | Correct Approach                                                                 |
|-------------------------------------------|-----------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| Empty or skeletal Testing section         | Tests can't be written without test names and scenarios; task is incomplete       | Always provide named test functions and their expected behavior per subsection  |
| Vague success criteria ("it should work") | Not verifiable; leaves the engineer guessing what "done" means                    | Every criterion must map to a runnable command that exits 0 or a grep assertion |
| Missing file paths in "Files to Modify"   | Engineer must hunt for the right file; increases error rate and context waste     | Every file touched must be listed with its path relative to project root        |
| Task too large for one context window     | LLM loses context mid-task; partial implementations leak into the next session    | Split into sub-tasks at the 100-line boundary; each sub-task is self-contained  |
| Missing live API test when service present| Integration silently untested; bugs surface in production instead of development  | Always include live test stub (BLOCKED) or full live test if key exists in .env |
