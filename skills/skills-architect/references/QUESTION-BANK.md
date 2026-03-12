# Skills Architect — Question Bank

100+ pre-written questions across 5 interview rounds.
Each question is a specification for an AskUserQuestion tool call.
Selection logic governs when each question is included or skipped.

---

## §1 — Round 1: Identity (Q1.1–Q1.6)

### Q1.1 — Purpose / Problem
**ID:** Q1.1
**Include:** Always — first question in every interview.
**Header:** `What it does`
**Question text:**
> What problem does this skill solve? What does it DO?
> Describe the core job in one sentence, then pick the closest category.

**Options:**
1. (Recommended) **Workflow Automation** — Orchestrates multi-step processes: reads inputs, runs tools, writes outputs. Best starting point; covers 70% of skill use-cases. Pick this if unsure.
2. **Code Generation** — Produces new files, boilerplate, scaffolding, or patches based on templates or analysis.
3. **Quality Enforcement** — Audits code, configs, or artifacts against rules; blocks on failure; generates reports.
4. **Research / Analysis** — Gathers information from the codebase, web, or APIs and synthesises a structured report.

---

### Q1.2 — Skill Name
**ID:** Q1.2
**Include:** Always — follows Q1.1.
**Header:** `Skill name`
**Question text:**
> What should this skill be called?
> The name becomes the folder name, the slash command trigger, and the frontmatter `name` field.
> Use kebab-case, lowercase, no spaces (e.g. `api-doc-generator`).

**Options:**
1. (Recommended) **Auto-suggest from purpose** — Derive name from Q1.1 answer and project context (e.g. "workflow-automation" → `{verb}-{noun}`). You confirm or edit.
2. **I'll type the name** — Provide an exact kebab-case name right now.
3. **Namespace it** — Prefix with owner namespace (e.g. `yasmine:skill-name`) for global vs project scoping.
4. **Reuse existing name** — Map to an existing skill found in `.claude/skills/` and extend it instead.

---

### Q1.3 — Trigger Context
**ID:** Q1.3
**Include:** Always — determines how the skill surfaces to the user.
**Header:** `When triggers`
**Question text:**
> When should this skill activate? What would the user be doing when they need it?
> This controls the `triggers` frontmatter array.

**Options:**
1. (Recommended) **Explicit command only** — User types `/skill-name` or `/namespace:skill-name`. Zero surprise activations. Best for destructive or long-running skills.
2. **Auto-trigger on file types** — Skill activates when Claude opens or edits certain extensions (e.g. `.py`, `.yaml`). Good for formatters and linters.
3. **Auto-trigger on user phrases** — Skill activates when user says phrases like "review my code" or "generate tests". Good for research and analysis skills.
4. **Always available** — Skill is loaded as ambient context for every conversation. Use only for lightweight skills (< 50 lines of instructions).

---

### Q1.4 — Target Users
**ID:** Q1.4
**Include:** Always — shapes tone, complexity, and defaults.
**Header:** `Who uses it`
**Question text:**
> Who will use this skill day-to-day?
> This affects default verbosity, approval gates, and whether the skill asks questions or acts silently.

**Options:**
1. (Recommended) **Solo developer (you)** — Minimal confirmation prompts, opinionated defaults, fast iteration. Skill trusts the user.
2. **Development team** — Adds approval gates before destructive actions, outputs shareable reports, follows team conventions from context files.
3. **CI/CD pipeline** — Fully non-interactive; all inputs via arguments or env vars; exits with a code; no AskUserQuestion calls at runtime.
4. **Open-source community** — Maximum documentation, safe defaults, no assumptions about environment, extensive --help text.

---

### Q1.5 — Framework-Specific
**ID:** Q1.5
**Include:** When a framework is detected in the project (Next.js, FastAPI, Django, etc.). Skip for greenfield or polyglot repos.
**Header:** `Framework fit`
**Question text:**
> A framework was detected in this project: **{detected}**.
> Should this skill adapt its behaviour specifically for {detected}?

**Options:**
1. (Recommended) **Yes — framework-specific** — Skill reads {detected} conventions, config files, and idioms. Produces output that fits the project out of the box.
2. **Framework-agnostic** — Skill works identically regardless of framework. Choose this if you plan to reuse the skill across many projects.
3. **Support multiple frameworks** — Skill detects the framework at runtime and switches behaviour. Adds complexity; use only if you work across 3+ stacks regularly.

---

### Q1.6 — Existing Skills
**ID:** Q1.6
**Include:** When 1+ skills are found in `.claude/skills/`. Skip if the skills directory is empty.
**Header:** `Relation to existing`
**Question text:**
> The following skills already exist in this project: **{list}**.
> How does this new skill relate to them?

**Options:**
1. (Recommended) **Standalone — no relation** — New skill is independent. Architect will still check for naming conflicts.
2. **Extends an existing skill** — New skill adds phases or tools to an existing one. Architect will suggest a shared interface.
3. **Replaces an existing skill** — New skill supersedes one on the list. Architect will flag the old skill for deprecation.
4. **Part of a pipeline** — New skill is one step in a sequence with existing skills. Architect will generate handoff contracts.

---

## §2 — Round 2: Behavior (Q2.1–Q2.8)

### Q2.1 — Workflow Type
**ID:** Q2.1
**Include:** Always — determines the top-level structure of SKILL.md.
**Header:** `Workflow type`
**Question text:**
> How should the skill's internal logic flow?
> This determines the phase structure and branching rules in the generated SKILL.md.

**Options:**
1. (Recommended) **Linear** — Phases execute in fixed order (Phase 1 → 2 → 3). Simple, predictable, easy to debug. Good for 80% of skills.
2. **Branching** — Phases fork based on detected conditions or user input (e.g. "if TypeScript, go to Phase 3A; else Phase 3B"). Use when outputs vary significantly by context.
3. **Interview-driven** — Skill asks the user a series of questions before doing any work, then executes based on answers. Good for scaffolding and code-gen skills.
4. **Orchestrator** — Skill spawns sub-agents or calls other skills and aggregates their results. Use for Tier 5+ complexity only.

---

### Q2.2 — Tools Needed
**ID:** Q2.2
**Include:** Always — drives the `tools` section of SKILL.md.
**Header:** `Tools needed`
**Question text:**
> Which tool tiers does this skill need?
> Higher tiers add power but require more review. Select the highest tier you actually need.

**Options:**
1. (Recommended) **Tier 1 — Read-only** — Read, Glob, Grep, Bash (read-only). Safe for analysis and reporting. No side effects.
2. **Tier 2 — File writing** — Adds Write, Edit, NotebookEdit. Creates or modifies files. Recommend approval gate before first write.
3. **Tier 3 — Web + external APIs** — Adds WebFetch, WebSearch, mcp__grep__searchGitHub. Requires network access.
4. **Tier 4 — System + processes** — Adds Bash (write-mode), background jobs, subprocess spawning. Requires careful scoping.

---

### Q2.3 — User Interaction
**ID:** Q2.3
**Include:** Always — determines how many AskUserQuestion calls appear in the skill.
**Header:** `Interaction mode`
**Question text:**
> How much should the skill talk to the user during a run?

**Options:**
1. (Recommended) **Guided** — Skill asks 1–3 key questions at the start, then runs to completion silently. Balances speed with user control.
2. **Silent** — Skill runs entirely without asking questions. All decisions are made automatically from context. Best for CI/CD or expert users.
3. **Interview-driven** — Skill asks questions at multiple phases, waiting for approval before proceeding. Best for destructive or high-stakes skills.
4. **Streaming progress** — Skill prints a live progress log as it runs (no questions). Good for long-running skills where the user needs feedback.

---

### Q2.4 — Output Artifacts
**ID:** Q2.4
**Include:** Always — determines what the skill produces and where it writes.
**Header:** `Output artifacts`
**Question text:**
> What does this skill produce when it finishes?
> Select all that apply — pick the primary output type.

**Options:**
1. (Recommended) **Modified source files** — Skill edits existing code files in the project. Changes are visible in git diff.
2. **New files generated** — Skill creates new files (specs, configs, reports). Specify target directory in the next phase.
3. **Terminal report only** — Skill prints a summary to the conversation. Nothing is written to disk.
4. **Mixed — files + report** — Skill writes files AND prints a summary. Use for audit/quality skills that need both a record and a diff.

---

### Q2.5 — Phase Dependencies
**ID:** Q2.5
**Include:** When workflow type is branching or orchestrator (Q2.1 options 2 or 4). Skip for linear and interview-driven.
**Header:** `Phase deps`
**Question text:**
> Which phases depend on the output of earlier phases?
> This determines which phases can be retried independently vs which must re-run from the start.

**Options:**
1. (Recommended) **All phases depend on Phase 1** — Phase 1 is the discovery/read phase. All later phases use its output. Standard pattern.
2. **Each phase is independent** — Phases share no state. Each can be re-run in isolation. Good for modular skills.
3. **Fan-out then fan-in** — Phase 1 fans out to parallel phases; a final phase aggregates. Use for multi-file analysis skills.
4. **Custom dependency graph** — I'll describe the dependencies explicitly. Architect will generate a DAG diagram.

---

### Q2.6 — Parallel Opportunities
**ID:** Q2.6
**Include:** When the skill has 4+ phases or processes multiple files/agents. Skip for simple 2–3 phase skills.
**Header:** `Parallelism`
**Question text:**
> Are there phases or operations that could run simultaneously to save time?
> Parallel phases are annotated with `[PARALLEL]` in the generated SKILL.md.

**Options:**
1. (Recommended) **Yes — parallel file analysis** — When processing multiple files, analyse them in parallel. Standard optimisation for code-analysis skills.
2. **Yes — parallel tool calls** — Run independent tool calls (e.g. Grep + WebSearch) simultaneously within a single phase.
3. **Yes — parallel sub-agents** — Spawn multiple sub-agents in parallel (Tier 5+ only). Each agent handles a subset of the work.
4. **No — sequential only** — All operations run in order. Simpler to reason about; choose for skills with strong data dependencies.

---

### Q2.7 — Script Needs
**ID:** Q2.7
**Include:** When target user is team or CI/CD (Q1.4 options 2 or 3), or when quality gates are selected. Skip for solo-dev silent skills.
**Header:** `Scripts needed`
**Question text:**
> Does this skill need companion shell scripts for validation, deployment, or cleanup?
> Scripts are generated in `.claude/skills/{name}/scripts/`.

**Options:**
1. (Recommended) **Validation script** — A `validate.sh` that checks prerequisites before the skill runs (e.g. correct Node version, required env vars present).
2. **CI integration script** — A `ci.sh` designed to be called from GitHub Actions, GitLab CI, or a Makefile target.
3. **Cleanup / rollback script** — A `rollback.sh` that undoes changes made by the skill if a later phase fails.
4. **No scripts needed** — Skill is self-contained; all logic lives in SKILL.md instructions.

---

### Q2.8 — Subagent Design
**ID:** Q2.8
**Include:** When workflow type is orchestrator (Q2.1 option 4) or when Tier 5+ is selected. Skip otherwise.
**Header:** `Subagent design`
**Question text:**
> How should sub-agents be structured?
> This only applies to orchestrator-pattern skills that spawn child agents.

**Options:**
1. (Recommended) **Specialised agents in parallel** — Each sub-agent has one job (e.g. one for linting, one for type-checking). They run simultaneously and report back.
2. **Sequential pipeline agents** — Sub-agents hand off to each other in a chain. Output of Agent A is input to Agent B.
3. **Dynamic agent pool** — A router agent decides which specialist agents to invoke based on the task. Most flexible; most complex.
4. **Single sub-agent with context** — One sub-agent runs in a fork with a different model (e.g. Opus for reasoning). Simpler than a pool.

---

## §3 — Round 3: Architecture (Q3.1–Q3.6)

### Q3.1 — Context Mode
**ID:** Q3.1
**Include:** Always — one of the most consequential architecture decisions.
**Header:** `Context mode`
**Question text:**
> Should this skill run in its own isolated context (fork) or share the current conversation context (inline)?
>
> **Fork:** Skill gets a clean context. No conversation history leaks in. Slower to start. Required for long-running or destructive skills.
> **Inline:** Skill runs inside the current conversation. Faster. Can read what the user just said. Risk of context pollution for complex skills.

**Options:**
1. (Recommended) **Fork (isolated)** — Skill runs in its own context with only its SKILL.md and explicitly passed arguments. Safest choice for production skills.
2. **Inline (shared context)** — Skill reads the current conversation. Use only for lightweight analysis skills that need to reference what the user just typed.
3. **Fork with injected summary** — Skill forks, but the orchestrator injects a compressed summary of the current conversation as context. Balances isolation and awareness.

---

### Q3.2 — Model Override
**ID:** Q3.2
**Include:** Always — controls cost, speed, and capability.
**Header:** `Model choice`
**Question text:**
> Which model should run this skill?
> Overrides the session default. Leave on Inherit to use whatever the user has selected.

**Options:**
1. (Recommended) **Inherit from session** — Uses the model the user currently has active. Most flexible; no surprise cost changes.
2. **claude-sonnet-4-6 (balanced)** — Sonnet: fast, capable, moderate cost. Good for most workflow and code-gen skills.
3. **claude-opus-4-6 (powerful)** — Opus: highest reasoning, highest cost. Reserve for architecture design, complex analysis, or orchestrator agents.
4. **claude-haiku-3-5 (fast/cheap)** — Haiku: fastest, cheapest. Good for high-frequency, low-complexity tasks (e.g. formatting, summarising).

---

### Q3.3 — Hooks Needed
**ID:** Q3.3
**Include:** Always — determines whether a hooks section is generated.
**Header:** `Hooks needed`
**Question text:**
> Does this skill need lifecycle hooks to validate, block, or observe its actions?
>
> Common use-cases: block writes to production files, enforce test coverage before commit, log all tool calls.

**Options:**
1. (Recommended) **Yes — validation hooks** — Add hooks that check preconditions and block the skill if they fail. Most skills benefit from at least one pre-run hook.
2. **Yes — observation hooks** — Add hooks that log or notify without blocking. Good for audit trails and team visibility.
3. **Yes — both** — Validation hooks for quality gates, observation hooks for logging. Use for high-stakes skills on team projects.
4. **No hooks** — Skill runs without lifecycle checks. Choose only for throwaway or read-only skills.

---

### Q3.4 — Hook Events
**ID:** Q3.4
**Include:** When Q3.3 is not "No hooks". Skip otherwise.
**Header:** `Hook events`
**Question text:**
> Which lifecycle events should trigger hooks?
> Select the events relevant to this skill's risk surface.

**Options:**
1. (Recommended) **PreToolUse + PostToolUse** — Hook fires before and after every tool call. Catches all file writes and shell commands. Most comprehensive.
2. **PreToolUse only** — Hook fires before tool calls. Use to block; not needed if you only want to observe.
3. **Stop (post-run)** — Hook fires when the skill finishes. Use to validate final state (e.g. tests must pass, lint must be clean).
4. **Notification** — Hook fires to send a message (Slack, email) when the skill completes or fails. Use for long-running CI skills.

---

### Q3.5 — Block on Failure
**ID:** Q3.5
**Include:** When Q3.3 is not "No hooks". Skip otherwise.
**Header:** `Block on fail`
**Question text:**
> Which hook failures should block the skill from continuing?
> Blocking hooks return a non-zero exit code; the skill halts and reports the failure.

**Options:**
1. (Recommended) **Block on any validation failure** — If any PreToolUse hook fails, halt immediately. Strictest; safest for production skills.
2. **Block on critical failures only** — Define a list of critical hooks (e.g. "no writes to /prod") that block; others warn only.
3. **Warn but continue** — All hook failures are logged as warnings. Skill continues regardless. Use for observation-only hooks.
4. **Ask user on failure** — Hook failure triggers an AskUserQuestion: "Validation failed. Continue anyway?" Use for interactive skills.

---

### Q3.6 — Custom Agents
**ID:** Q3.6
**Include:** When workflow type is orchestrator or subagent design was selected. Skip for single-agent skills.
**Header:** `Agent design`
**Question text:**
> How should custom sub-agents be defined?
> Each agent gets its own SKILL.md-style system prompt and tool restrictions.

**Options:**
1. (Recommended) **Inline agent definitions** — Agent prompts are written directly inside the orchestrator SKILL.md. Simpler; all logic in one file.
2. **Separate SKILL.md per agent** — Each agent lives in its own subdirectory with its own SKILL.md, tools list, and model override. Better for complex agents.
3. **Shared agent library** — Agents are defined once in a shared library and reused across multiple skills. Good for large systems with 5+ skills.
4. **Dynamic agent prompts** — Orchestrator generates agent prompts at runtime based on task inputs. Most flexible; hardest to test.

---

## §4 — Round 4: Quality (Q4.1–Q4.5)

### Q4.1 — Quality Gates
**ID:** Q4.1
**Include:** Always — every skill should have at least one quality gate.
**Header:** `Quality gates`
**Question text:**
> Which phases should have a blocking quality gate before proceeding?
> A quality gate runs a check (test, lint, type-check) and halts if it fails.

**Options:**
1. (Recommended) **After every phase that writes files** — Any phase that creates or edits files gets a gate. Tests must pass before the next phase starts. Standard professional default.
2. **Final phase only** — One gate at the very end. Faster iteration; riskier mid-run.
3. **User-defined checkpoints** — I'll specify which phases get gates. Architect generates gate instructions for each.
4. **No quality gates** — Skill runs to completion regardless of intermediate failures. Only for throwaway or read-only skills.

---

### Q4.2 — Error Recovery
**ID:** Q4.2
**Include:** Always — determines how the skill behaves when something goes wrong.
**Header:** `Error recovery`
**Question text:**
> When a phase fails, what should the skill do?

**Options:**
1. (Recommended) **Fail fast** — Halt immediately on first error. Log the error clearly. Leave files in last-known-good state. Easiest to debug.
2. **Retry with backoff** — Retry the failed operation up to 3 times with exponential backoff. Use for network or API calls that may be flaky.
3. **Degrade gracefully** — Skip the failed phase and continue with reduced output. Use when partial results are better than no results.
4. **Escalate to user** — On failure, ask the user what to do: retry, skip, or abort. Use for interactive skills on high-stakes tasks.

---

### Q4.3 — Approval Gates
**ID:** Q4.3
**Include:** When output artifacts include file writes (Q2.4 options 1, 2, or 4) or when target user is team (Q1.4 option 2).
**Header:** `Approval gates`
**Question text:**
> Before which side effects should the skill pause and ask for user approval?
> Approval gates use AskUserQuestion to show a preview and get a confirm/abort decision.

**Options:**
1. (Recommended) **Before first file write** — Show a preview of what will be created/modified, then ask: "Proceed?" Standard for any skill that writes files.
2. **Before destructive operations** — Only gate on deletes, overwrites, or force-pushes. Allow non-destructive writes to proceed silently.
3. **Before external API calls** — Gate on any call that costs money or has side effects (Stripe, SendGrid, Twilio). Silent for read-only API calls.
4. **No approval gates** — Trust the skill to do the right thing. Choose only for fully reversible or read-only skills.

---

### Q4.4 — Circuit Breakers
**ID:** Q4.4
**Include:** When tools needed include Tier 3 or Tier 4 (external APIs or system commands). Skip for read-only skills.
**Header:** `Circuit breakers`
**Question text:**
> Should the skill include circuit breakers for external services?
> A circuit breaker stops calling a failing service after N errors and waits before retrying.

**Options:**
1. (Recommended) **Yes — per external service** — Each external API (OpenAI, GitHub, Stripe) gets its own circuit breaker with configurable threshold and timeout.
2. **Yes — global circuit breaker** — One circuit breaker covers all external calls. Simpler; less granular.
3. **No — rely on retry only** — Use retry with backoff but no circuit breaker. Acceptable for low-frequency external calls.
4. **No external services** — Skill is fully local; no circuit breakers needed.

---

### Q4.5 — Retry Strategy
**ID:** Q4.5
**Include:** When Q4.2 is "Retry with backoff" or Q4.4 is "Yes". Skip for fail-fast skills.
**Header:** `Retry strategy`
**Question text:**
> How should retries be configured?

**Options:**
1. (Recommended) **Exponential backoff with jitter** — Wait 1s, 2s, 4s, 8s between retries. Add random jitter (±20%) to avoid thundering herd. Max 3 retries. Production standard.
2. **Fixed interval** — Retry every N seconds up to M times. Simpler; less optimal under load.
3. **Linear backoff** — Wait 1s, 2s, 3s, 4s. Gentler than exponential; better for rate-limited APIs with predictable windows.
4. **Custom** — I'll define the retry parameters explicitly. Architect will generate the exact retry logic.

---

## §5 — Round 5: Polish (Q5.1–Q5.4)

### Q5.1 — Memory Persistence
**ID:** Q5.1
**Include:** When target user is solo developer or team (Q1.4 options 1 or 2). Skip for CI/CD skills.
**Header:** `Memory persist`
**Question text:**
> Should this skill remember user preferences between runs?
> Memory persistence saves choices (e.g. preferred output format, last directory used) so the skill doesn't re-ask on the next run.

**Options:**
1. (Recommended) **Yes — save key preferences** — Skill writes a small config to `.claude/skills/{name}/prefs.json` after the first run. Subsequent runs load and apply saved preferences silently.
2. **Yes — full session state** — Skill saves complete run state, enabling resume from the last successful phase if interrupted.
3. **No — stateless** — Skill starts fresh every run. Simpler; no stale preferences to manage. Good for skills run infrequently.

---

### Q5.2 — Complementary Skills
**ID:** Q5.2
**Include:** When 1+ existing skills are found in `.claude/skills/`. Skip for the first skill in a project.
**Header:** `Pairs with`
**Question text:**
> Which existing skills pair well with this one?
> Architect can generate a pipeline spec showing how skills chain together.

**Options:**
1. (Recommended) **Auto-detect from skill outputs** — Architect analyses existing skills' output artifacts and suggests natural pairings (e.g. a generator skill + a validator skill).
2. **I'll specify the pipeline** — I know which skills come before and after this one. I'll describe the chain.
3. **Standalone — no pipeline** — This skill is independent and does not chain with others.

---

### Q5.3 — Pressure Tests
**ID:** Q5.3
**Include:** Always — pressure tests reveal design gaps before implementation.
**Header:** `Pressure tests`
**Question text:**
> What adversarial scenarios should this skill handle gracefully?
> Select the scenarios most relevant to this skill's risk surface.

**Options:**
1. (Recommended) **Empty or missing inputs** — Skill is invoked with no arguments or on an empty directory. Should fail gracefully with a clear error, not a crash.
2. **Large codebase (1000+ files)** — Skill runs on a very large project. Should paginate, stream, or filter rather than loading everything into context at once.
3. **Conflicting user input** — User provides contradictory answers to questions. Skill should detect and resolve the conflict by asking a clarifying follow-up.
4. **External service down** — The API or service the skill depends on is unavailable. Skill should apply circuit breaker, retry, and degrade gracefully.

---

### Q5.4 — Pipeline Position
**ID:** Q5.4
**Include:** When Q5.2 is not "Standalone". Skip for standalone skills.
**Header:** `Pipeline step`
**Question text:**
> Where does this skill sit in the overall skill pipeline?
> This generates handoff contract documentation showing what this skill expects as input and what it passes to the next skill.

**Options:**
1. (Recommended) **Entry point (Step 1 of N)** — This skill is the first in a pipeline. It accepts raw user input and produces structured artifacts for downstream skills.
2. **Middle step (Step N of M)** — This skill transforms artifacts from a previous skill and passes results to the next. Architect will generate input/output contracts.
3. **Terminal step (Last step)** — This skill is the final consumer. It reads upstream artifacts and produces the end deliverable (report, deployment, commit).
4. **Flexible position** — This skill can be inserted at any point. It declares both what it needs and what it produces, and the pipeline router places it appropriately.

---

## Selection Logic Summary

| Question | Include When | Skip When |
|----------|-------------|-----------|
| Q1.1 | Always | — |
| Q1.2 | Always | — |
| Q1.3 | Always | — |
| Q1.4 | Always | — |
| Q1.5 | Framework detected in project | No framework detected |
| Q1.6 | Existing skills found | `.claude/skills/` is empty |
| Q2.1 | Always | — |
| Q2.2 | Always | — |
| Q2.3 | Always | — |
| Q2.4 | Always | — |
| Q2.5 | Branching or orchestrator workflow | Linear or interview-driven |
| Q2.6 | 4+ phases or multi-file processing | Simple 2–3 phase skills |
| Q2.7 | Team or CI/CD target user | Solo dev, silent skills |
| Q2.8 | Orchestrator workflow or Tier 5+ | Single-agent skills |
| Q3.1 | Always | — |
| Q3.2 | Always | — |
| Q3.3 | Always | — |
| Q3.4 | Q3.3 is not "No hooks" | Q3.3 is "No hooks" |
| Q3.5 | Q3.3 is not "No hooks" | Q3.3 is "No hooks" |
| Q3.6 | Orchestrator workflow or subagents | Single-agent skills |
| Q4.1 | Always | — |
| Q4.2 | Always | — |
| Q4.3 | File writes or team target user | Read-only or CI/CD |
| Q4.4 | Tier 3 or Tier 4 tools | Read-only skills |
| Q4.5 | Retry strategy or circuit breakers | Fail-fast skills |
| Q5.1 | Solo dev or team target user | CI/CD skills |
| Q5.2 | Existing skills found | First skill in project |
| Q5.3 | Always | — |
| Q5.4 | Q5.2 is not "Standalone" | Standalone skills |

---

## Usage Notes for Skills Architect

- Ask questions in round order (§1 → §2 → §3 → §4 → §5).
- Apply selection logic before each question — skip silently if the condition is not met.
- Replace `{detected}` and `{list}` placeholders with actual values from codebase discovery before presenting questions.
- Never present all questions at once; pace one question per AskUserQuestion call unless the user asks for a batch.
- The first option in every question is (Recommended). Pre-select it as the default but allow the user to override.
- After all applicable questions are answered, summarise the configuration before generating the skill.
