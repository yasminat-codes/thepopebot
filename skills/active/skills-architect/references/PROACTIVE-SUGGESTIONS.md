# Proactive Suggestions Engine

Expert suggestion engine — things users don't think of. Present after Phase 4 (Structure Design), before writing SKILL.md.

---

## When to Use This File

Load this file when presenting enhancement suggestions to the user. After analyzing the skill's type, tier, and tools, generate a list of applicable suggestions from the 8 categories below, then present them as a multiSelect AskUserQuestion.

---

## Suggestion Category 1: Hooks

Recommend hooks based on what the skill does.

**Code-generating skills** (tools include Write, Edit, or Bash with file creation):
- `post-tool-use` hook → run linter on newly created/modified files
- Example: `ruff check {file}` for Python, `eslint {file}` for JS/TS
- Surfaces syntax errors before the skill completes

**Deployment skills** (tools include Bash with docker/kubectl/ssh or deploy patterns):
- `pre-tool-use` hook → production environment lock check
- Block if `APP_ENV=production` and branch is not `main`
- Prevents accidental production deploys from feature branches

**Any skill** (universal recommendation):
- `post-tool-use` hook → audit logging
- Append to `.claude/logs/{skill-name}-audit.log`: timestamp, tool used, file affected
- Provides traceability without slowing down the skill

**Presentation:**
- List recommended hooks with one-line rationale each
- Include the hook script stub so user sees the implementation cost

---

## Suggestion Category 2: Pressure Test Scenarios

Recommend pressure test generation based on tier.

**Tier 3 skills:** Recommend 3 pressure test scenarios
**Tier 4 skills:** Recommend 4 pressure test scenarios
**Tier 5+ skills:** Recommend 5 pressure test scenarios

**What to say to user:**
> "Pressure tests verify your skill follows its own quality gates even when there's an incentive to skip them. For a Tier N skill, I recommend generating N scenarios. These live in `references/TESTING-SCENARIOS.md`."

**Load TESTING-GENERATION.md for full scenario templates.**

---

## Suggestion Category 3: Memory Integration

Recommend preference persistence for skills used more than once.

**Three-tier memory pattern:**
```
Project memory:  .claude/memory/MEMORY.md          (this project only)
Global memory:   ~/.claude/projects/-Users-yasmineseidu/memory/MEMORY.md   (all projects)
Skill memory:    .claude/memory/{skill-name}.md     (skill-specific log)
```

**What to recommend:**
- Save user overrides between runs (e.g., preferred tier, preferred CSO elements)
- Load global preferences at Phase 0 so defaults reflect past choices
- Priority: project memory > global memory > built-in defaults

**Example addition to SKILL.md:**
```yaml
memory:
  load:
    - path: .claude/memory/skills-architect.md
      section: "## preferences"
      on: phase_start
  save:
    - path: .claude/memory/skills-architect.md
      content: user_overrides
      on: completion
```

**When to recommend:**
- Tier 3+ skills that ask users recurring questions
- Skills with configurable defaults (tier selection, output format, etc.)

---

## Suggestion Category 4: CSO Anti-Patterns to Avoid

Flag common description mistakes before the user writes their description.

**Anti-pattern 1: Weak opening verb**
- Bad: "Helps with skill creation", "Assists in migrating"
- Fix: Start with action verb — "Creates", "Migrates", "Audits", "Validates"

**Anti-pattern 2: Missing PROACTIVELY keyword**
- Claude uses this keyword to decide when to invoke skills without being asked
- Fix: Add "PROACTIVELY invokes when..." before the trigger list

**Anti-pattern 3: Too few triggers (under 5)**
- Claude needs multiple patterns to recognize the right moment
- Fix: List 5+ distinct trigger phrases or user intents

**Anti-pattern 4: Over 1024 characters**
- Description is truncated in Claude's context window at 1024 chars
- Fix: Move examples and details to `references/`; keep description concise

**Anti-pattern 5: Vague triggers**
- Bad: "when the user wants to work on skills"
- Fix: "when user says 'create a skill', 'build a new skill', 'I need a skill for X'"

**Present these as a checklist** the user can review before writing their description. Offer to auto-check their draft description once written.

---

## Suggestion Category 5: Complementary Skills

Recommend skills that pair well with the one being created.

**For skills that generate code:**
- Pair with: `testing-skills-with-subagents` (auto-test what was created)
- Pair with: `writing-plans` (create a plan before generating code)

**For skills that create files or modify the codebase:**
- Pair with: `verification-before-completion` (verify before claiming done)
- Pair with: `requesting-code-review` (get review after changes)

**For skills used in deployment workflows:**
- Pair with: `deploy-readiness-validator` (pre-deployment safety check)
- Pair with: `security-auditor` (security review before ship)

**For skills that orchestrate other skills:**
- Pair with: `skill-orchestrator` (route to correct skill intelligently)
- Pair with: `dispatching-parallel-agents` (run sub-skills in parallel)

**Presentation:** List 2-3 recommended pairings with one-sentence rationale. Offer to add cross-references to SKILL.md directives.

---

## Suggestion Category 6: Circuit Breakers

Recommend circuit breakers when the skill calls external services.

**When to recommend:**
- Skill uses `WebFetch` tool
- Skill uses `Bash` with curl, wget, or API calls
- Skill's phase descriptions mention "fetch", "call", "request", or an external service name

**Circuit breaker pattern:**
```markdown
State file: .claude/circuit-breakers/{service-name}.json
{
  "state": "closed",          // closed = healthy, open = failing, half-open = testing
  "failures": 0,
  "last_failure": null,
  "cooldown_until": null
}

Thresholds:
- Open after: 3 consecutive failures
- Cooldown: 60 seconds
- Half-open test: 1 request, if success → close, if fail → reopen
```

**What to add to SKILL.md:**
- Phase 0 check: read circuit breaker state, skip external call if open
- After each external call: update failure/success count
- On open state: surface clear error to user with cooldown remaining

---

## Suggestion Category 7: Approval Gates

Recommend approval gates before irreversible actions.

**When to recommend:**
- Skill uses `Write` tool (creates or overwrites files)
- Skill uses `Bash` with `rm`, `git push`, `docker deploy`, or database commands
- Skill uses `Task` tool to spawn sub-agents that take actions

**Approval gate pattern:**
```markdown
Before [irreversible action], ask:
  "About to [describe action]. This cannot be undone.
   Options:
   1. Approve — proceed
   2. Modify — change [what can change]
   3. Cancel — stop here"
```

**When NOT to add approval gates:**
- Read-only operations (Read, Glob, Grep)
- Operations already inside an approved workflow step
- Tier 1-2 skills where the action is the entire point

---

## Suggestion Category 8: Learning Patterns

Recommend learning from corrections for repeatedly-used skills.

**When to recommend:**
- Tier 4+ skills (high complexity, used repeatedly)
- Skills with multiple configurable options
- Skills where user corrections during a run indicate a mismatch with defaults

**Learning pattern:**
```markdown
When user overrides a recommendation:
  Save to .claude/memory/{skill-name}.md:
  `[date]: User prefers [override] over [default] for [context]`

Next run:
  Load corrections from memory
  Apply as new defaults before presenting options
  Inform user: "Applied your saved preference: [X]"
```

**Implementation in SKILL.md:**
- Phase 0: load corrections file, apply to defaults map
- Phase N (wherever user overrides happen): detect deviation, log it
- Phase 10: write updated corrections to memory file

---

## Presenting Suggestions

After generating the applicable suggestions (filter by skill type, tier, and tools), present them as a multiSelect:

```
I have N enhancement suggestions for this skill. Select which to include:

[ ] Hooks — {specific hook recommendation for this skill}
[ ] Pressure Tests — {N} scenarios for Tier {N} quality gates
[ ] Memory Integration — save preferences between runs
[ ] CSO Anti-Patterns — pre-check description before writing
[ ] Complementary Skills — {specific skill pairings for this skill}
[ ] Circuit Breakers — for {specific external service detected}
[ ] Approval Gates — before {specific irreversible action detected}
[ ] Learning Patterns — save corrections for next run

Select: (comma-separated numbers, or "all", or "none")
```

Apply only selected suggestions. Do not add suggestions the user did not select.
