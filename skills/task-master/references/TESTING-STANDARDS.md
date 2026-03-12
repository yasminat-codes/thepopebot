# Testing Standards Reference

Every task file that task-master generates MUST include a fully populated Testing section.
This file defines the exact format, rules, and anti-patterns for that section.

---

## Section 1: Testing Section Template

The following is the exact format for the `## Testing` section in every generated task file.
Fill in all `{placeholders}`. Do not leave any placeholder unfilled.

```markdown
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

### Pressure Test (for Tier 4+ skills)
**File:** `tests/pressure-tests.md` (if exists)
**Method:** Dispatch a subagent using `testing-skills-with-subagents` skill
**Pass condition:** All scenarios in `tests/test-cases.md` produce expected outputs

### Live API Tests (include only when the task calls an external service)
**Requires:** `{SERVICE_API_KEY}` in `.env`
**What it validates:** {name the specific service called and what a successful response looks like}
**Stub if key missing:**
```
# BLOCKED: {SERVICE_API_KEY} not in .env
# Add to tests/test-cases.md once key is available
```
```

---

## Section 2: Live API Test Requirements

### When to include a live API test

All three conditions must be true:

1. The skill or task calls an external service (OpenRouter, Neon, Metricool, OpenAI, etc.)
2. The `.env` key for that service was found by task-master during Phase 0 discovery
3. The task is not purely a reference file or documentation change

### Integration → .env key mapping

When task-master scans `.env` in Phase 0, use this table to match integrations to keys:

| Integration              | Expected `.env` key           |
|--------------------------|-------------------------------|
| OpenRouter / LLM routing | `OPENROUTER_API_KEY`          |
| OpenAI direct            | `OPENAI_API_KEY`              |
| Neon database            | `DATABASE_URL`                |
| Metricool analytics      | `METRICOOL_API_KEY`           |
| Reddit API               | `REDDIT_CLIENT_SECRET`        |
| Google Drive / Sheets    | `GOOGLE_SERVICE_ACCOUNT_JSON` |
| Stripe payments          | `STRIPE_SECRET_KEY`           |

### What the live test MUST verify

- Minimum: the call returns the expected response or exit 0
- Preferred: the response matches the expected structure documented in the skill
- Never: the test must not modify production data — use sandbox keys or test-mode endpoints

### Stub pattern when key is absent

If task-master cannot find the required key in `.env`, add the stub as a comment in
`tests/test-cases.md` with a `# BLOCKED: {KEY} not in .env` marker — not a failing test
and not a skipped pytest decorator. The marker must name the specific missing key.

---

## Section 3: Anti-Patterns to Avoid

task-master MUST NOT generate task files that contain any of the following:

### 1. Empty testing section
Even for "simple" tasks (adding a reference file, editing a directive), at minimum include
one skill validation check. There is no task too small for a structural verification.

### 2. Live API stub without a reason comment
Always explain why the test is blocked. Use the exact format:
```
# BLOCKED: {SERVICE_API_KEY} not in .env
```
An unexplained stub is not acceptable.

### 3. Validation checks that assert nothing meaningful
A check that only verifies a file exists provides minimal value.
Every check must assert on at least one property of the content:
```
# Bad
[ -f ".claude/skills/{name}/references/{FILE}.md" ]

# Good
wc -l .claude/skills/{name}/references/{FILE}.md  ≥ 50 lines
grep "→ See references/{FILE}" .claude/skills/{name}/SKILL.md  returns a match
```

### 4. Hardcoded API keys in test-cases.md
All keys must come from `.env` via the pattern documented in `.env.example`.
Use `$KEY_NAME` references — never a literal key value.

### 5. Circular → See directives between reference files
Each reference file may link to SKILL.md or to external docs, but two reference files
must not reference each other in a way that creates a circular dependency
(e.g., A says "→ See B" and B says "→ See A" with no other content).

---

## Section 4: Skill Test File Conventions

| Test Type             | File Path                                              |
|-----------------------|--------------------------------------------------------|
| Test cases (manual)   | `.claude/skills/{name}/tests/test-cases.md`            |
| Pressure tests        | `.claude/skills/{name}/tests/pressure-tests.md`        |
| Subagent test runner  | Invoke `testing-skills-with-subagents` skill via Skill |

### Naming rules

- Test cases are markdown files — not Python files
- Each scenario in `test-cases.md` has: input, expected output, pass condition
- `pressure-tests.md` covers edge cases, large inputs, and adversarial prompts
- Skill invocation tests are triggered by running the skill with a simple prompt, not via pytest
