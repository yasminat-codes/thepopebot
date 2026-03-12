# Tools Reference for Claude Code Skills

Complete tool selection reference for building skills at every tier.

---

## Available Tools with Signatures

### File Operations

**Read**
- Signature: `Read(file_path, offset?, limit?)`
- Use when: Reading source files, configs, existing skill files, context files
- Returns: File contents with line numbers
- Notes: Always read before editing. Supports PDF, images, notebooks

**Write**
- Signature: `Write(file_path, content)`
- Use when: Creating new files from scratch
- Returns: Confirmation
- Notes: Overwrites existing files. Prefer Edit for modifying existing files

**Edit**
- Signature: `Edit(file_path, old_string, new_string, replace_all?)`
- Use when: Modifying specific sections of existing files
- Returns: Confirmation of change
- Notes: old_string must be unique in file. Use replace_all for renaming across file

### Search Tools

**Grep**
- Signature: `Grep(pattern, path?, type?, glob?, output_mode?, context?, -A?, -B?, -i?)`
- Use when: Searching file contents by pattern, finding usages, locating definitions
- Output modes: files_with_matches (default), content, count
- Notes: Supports full regex. Use -C for context lines around matches

**Glob**
- Signature: `Glob(pattern, path?)`
- Use when: Finding files by name pattern, listing files of a type
- Returns: Matching file paths sorted by modification time
- Notes: Faster than Bash find. Use for structural discovery

**SemanticSearch**
- Signature: `SemanticSearch(query, path?)`
- Use when: Finding conceptually related code without knowing exact terms
- Returns: Semantically relevant file sections
- Notes: Tier 5+ only. Slower than Grep but finds meaning, not just text

### Shell Tools

**Bash**
- Signature: `Bash(command, description?, timeout?, run_in_background?)`
- Use when: Running commands, tests, builds, git operations, installs
- Returns: stdout + stderr
- Notes: Shell state does NOT persist between calls. Use absolute paths. Always quote paths with spaces

**BashOutput** (alias: reading Bash output into logic)
- Pattern: Capture Bash output then branch on result in next tool call
- Use when: Conditional logic based on command results (e.g., check if file exists)

**KillShell**
- Signature: `KillShell()`
- Use when: Terminating a long-running background Bash process
- Notes: Only applicable after run_in_background=true Bash calls

### Workflow Tools

**TodoWrite**
- Signature: `TodoWrite(todos: [{content, status, priority, id}])`
- Use when: Tracking multi-step progress, surfacing current state to user
- Statuses: pending, in_progress, completed
- Notes: Tier 4+ skills. Replaces narration for long workflows

**AskQuestion**
- Signature: `AskQuestion(question, options?)`
- Use when: Clarifying ambiguous user intent before proceeding
- Notes: Use sparingly. Maximum 1-2 questions per skill invocation. Prefer defaults over asking

### Web Tools

**WebSearch**
- Signature: `WebSearch(query, allowed_domains?, blocked_domains?)`
- Use when: Current versions, API documentation, recent changes, best practices
- Notes: Tier 5+ skills. Current date awareness built in. Results include URLs

**WebFetch**
- Signature: `WebFetch(url, prompt)`
- Use when: Reading specific documentation pages, fetching structured data from known URLs
- Notes: Converts HTML to markdown before processing. Caches for 15 minutes

### Agent Tools

**Task**
- Signature: `Task(subagent_type, prompt, model?, run_in_background?, isolation?)`
- Use when: Parallel workloads, isolated sub-tasks, long-running operations
- subagent_type options:
  - `general` - Standard agent for most tasks
  - `code` - Specialized for code generation and review
  - `research` - Optimized for web research and synthesis
- model options: `claude-opus-4-6` (default), `claude-sonnet-4-6`
- run_in_background: true/false - fire and forget vs. wait for result
- isolation: true = fresh context, false = inherits current context
- Notes: Tier 5+ skills. Use for parallelism, not just offloading

### Specialized Tools

**LSP**
- Signature: `LSP(action, ...args)`
- Use when: Type checking, go-to-definition, find references, symbol lookup
- Actions: hover, definition, references, diagnostics, completions
- Notes: Tier 6 only. Requires active language server. Provides IDE-level accuracy

**NotebookRead**
- Signature: `NotebookRead(notebook_path)`
- Use when: Reading Jupyter notebooks (.ipynb files)
- Returns: All cells with outputs, code, and visualizations

**NotebookEdit**
- Signature: `NotebookEdit(notebook_path, new_source, cell_id?, cell_type?, edit_mode?)`
- Use when: Modifying, inserting, or deleting notebook cells
- edit_mode: replace (default), insert, delete

**GenerateImage**
- Signature: `GenerateImage(prompt, output_path)`
- Use when: Creating diagrams, mockups, or visual assets as part of skill output
- Notes: Tier 5+ only. Use only when visual output explicitly requested

**ReadLints**
- Signature: `ReadLints(file_path?)`
- Use when: Checking linting errors without running a shell command
- Returns: Current lint diagnostics for file or project
- Notes: Faster than running linter via Bash for quick checks

### MCP Tools

**Pattern:** `mcp__serverName__toolName(params)`

**Examples:**
- `mcp__github__search_repositories` - Search GitHub repos
- `mcp__postgres__query` - Run database queries
- `mcp__slack__send_message` - Send Slack messages
- `mcp__stripe__list_customers` - Query Stripe API

**Wildcard reference in skill files:** `mcp__*` means "any MCP tool available in this environment"

**When to use:** Only when the skill explicitly requires external service integration. Document which MCP servers are required in the skill's SKILL.md frontmatter.

---

## Tier-Based Tool Patterns

| Tier | Recommended Tools | Notes |
|------|-------------------|-------|
| 1 | (none) | Information only, no tool calls |
| 2 | Read, Grep, Glob | Read-only analysis and discovery |
| 3 | Read, Write, Edit, Grep, Glob, Bash | Standard file manipulation and shell |
| 4 | Read, Write, Edit, Grep, Glob, Bash, TodoWrite, AskQuestion | Multi-step workflows with progress tracking |
| 5 | + Task, WebSearch, WebFetch | Parallel agents, web research |
| 6 | + LSP (all tools available) | Full IDE-level capabilities, complex orchestration |

### Tier 1: Reference Only
No tool calls. Pure instructional content. Output is human-readable guidance only.

### Tier 2: Read-Only Analysis
```
Read → Grep → Glob → (synthesize and report)
```
Never modifies files. Used for audits, reports, reviews.

### Tier 3: Standard Implementation
```
Glob → Read → (plan) → Edit/Write → Bash(validate)
```
The baseline for most feature-building skills.

### Tier 4: Managed Workflow
```
TodoWrite(init) → AskQuestion(clarify) → Read/Write/Edit → Bash → TodoWrite(update)
```
Tracks progress explicitly. Suitable for multi-phase skills.

### Tier 5: Orchestrated
```
WebSearch(research) → Task(parallel:subagent1) + Task(parallel:subagent2) → merge → Write
```
Spawns subagents for parallelism. Uses web for current data.

### Tier 6: Full Capability
```
LSP(diagnostics) → Read → Edit → Bash(test) → LSP(verify) → TodoWrite(done)
```
All tools available. Used for complex refactoring, ecosystem-level changes.

---

## Scoped Bash Patterns

Bash can be scoped to specific command families for precision and safety.

| Pattern | Meaning | Example Commands |
|---------|---------|-----------------|
| `Bash(git:*)` | Any git operation | git status, git log, git diff |
| `Bash(npm:test)` | npm test specifically | npm test, npm run test:coverage |
| `Bash(npm:*)` | Any npm operation | npm install, npm run build |
| `Bash(docker:build)` | Docker build only | docker build -t name . |
| `Bash(docker:*)` | Any docker operation | docker ps, docker exec, docker logs |
| `Bash(python:*)` | Any python operation | python -m pytest, pip install |
| `Bash(read-only)` | Non-mutating shell | ls, cat, which, env, pwd |

**Why scope matters:** Scoped permissions reduce blast radius for skills that should not run arbitrary commands. When writing SKILL.md, document which Bash scopes the skill uses.

---

## Permission Interaction Table

| Tool | Reads Files | Writes Files | Runs Shell | Network | Spawns Agents |
|------|-------------|--------------|------------|---------|---------------|
| Read | Yes | No | No | No | No |
| Write | No | Yes | No | No | No |
| Edit | Yes | Yes | No | No | No |
| Grep | Yes | No | No | No | No |
| Glob | No | No | No | No | No |
| Bash | Yes | Yes | Yes | Yes | No |
| WebSearch | No | No | No | Yes | No |
| WebFetch | No | No | No | Yes | No |
| Task | Depends | Depends | Depends | Depends | Yes |
| LSP | Yes | No | No | No | No |
| TodoWrite | No | Internal | No | No | No |
| AskQuestion | No | No | No | No | No |

---

## Anti-Patterns

### Over-Provisioning
**Problem:** Giving a Tier 2 skill access to Bash, Write, and Task.
**Why it hurts:** Increases risk surface, confuses implementers, slows audits.
**Fix:** Match tool set to actual skill tier. If you do not need it, do not list it.

### Under-Provisioning
**Problem:** A Tier 4 skill that never uses TodoWrite or AskQuestion.
**Why it hurts:** Users lose progress visibility. Ambiguous inputs cause silent wrong behavior.
**Fix:** Add TodoWrite for any skill with 3+ distinct phases. Add AskQuestion for skills with ambiguous required inputs.

### Bash as a Crutch
**Problem:** Using Bash to find files instead of Glob, or to search content instead of Grep.
**Why it hurts:** Slower, less readable, bypasses built-in tool optimizations.
**Fix:** Prefer Grep/Glob for search. Use Bash only for operations those tools cannot perform (running tests, git commands, installs).

### Missing Bash Descriptions
**Problem:** `Bash("npm install")` with no description.
**Why it hurts:** Users cannot review what the skill is doing.
**Fix:** Always include a clear description: `Bash("npm install", "Install project dependencies")`

### Spawning Tasks for Simple Work
**Problem:** Using Task (subagent) for single-file edits.
**Why it hurts:** Agent spawning has overhead. Simple tasks do not benefit.
**Fix:** Reserve Task for genuinely parallel workloads or long-running isolation needs.

### Forgetting MCP Dependencies
**Problem:** Skill uses `mcp__stripe__*` but does not document Stripe MCP as a requirement.
**Why it hurts:** Skill silently fails in environments without that MCP server.
**Fix:** List all required MCP servers in SKILL.md under a `## Requirements` section.
