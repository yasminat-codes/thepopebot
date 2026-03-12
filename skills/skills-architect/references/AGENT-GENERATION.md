# Custom Agent YAML Generation for Tier 5+ Skills

## Agent File Location

All custom agents live at:
```
.claude/agents/{agent-name}.yml
```

Subagent files are loaded automatically when referenced in `Task` calls. The filename (without `.yml`) is the `subagent_type` value used in `Task({subagent_type: "agent-name"})`.

## All 10 Frontmatter Fields

```yaml
# Required
name: string                    # Unique identifier, kebab-case, matches filename
description: string             # One-line purpose (shown in agent picker)

# Model selection
model: string                   # claude-opus-4-6 | claude-sonnet-4-6 | claude-haiku-3-5
                                # Default: claude-sonnet-4-6

# Permissions
permissionMode: string          # default | acceptEdits | bypassPermissions | plan
                                # Default: default

# Turn limits
maxTurns: integer               # Maximum back-and-forth turns before forced stop
                                # Default: 30

# Memory
memory:
  scope: string                 # user | project | local
                                # user: persists across projects
                                # project: scoped to this project
                                # local: session only, no persistence

# Tool restrictions
tools:
  - string                      # List of allowed tools (omit = all tools allowed)
                                # Restricts what the subagent can call

# Skills preloading
skills:
  - string                      # Skill names to load into agent context

# System prompt (replaces default)
system: string                  # Custom system prompt (multi-line YAML block)

# Metadata
version: string                 # Semantic version (1.0.0)
tags:
  - string                      # Categorization tags
```

## permissionMode Selection Guide (Least-Privilege Principle)

| Mode | Access Level | When to Use |
|---|---|---|
| `default` | Standard Claude Code permissions, prompts for approval | Most agents - safe default |
| `acceptEdits` | Auto-accepts file edits without prompting | Code generators that write many files |
| `bypassPermissions` | Full access, no prompts | Trusted orchestrators only - use sparingly |
| `plan` | Read-only planning mode, no execution | Researchers, reviewers, planners |

**Rule:** Always start with `default`. Escalate only when the agent genuinely needs it. Never use `bypassPermissions` for read-only tasks.

## maxTurns Guidelines

| Agent Role | Recommended maxTurns | Reasoning |
|---|---|---|
| Fast researcher | 10 | Read files, summarize, done |
| Code reviewer | 15 | Read code, check patterns, output review |
| Security auditor | 20 | Scan multiple files, verify findings |
| Code generator | 30 | Plan + write + verify multiple files |
| Integration builder | 40 | Cross-system work, more coordination |
| Orchestrator worker | 50-100 | Manages phases, spawns subagents |
| Full system builder | 100+ | Only for top-level orchestrators |

**Rule:** Set maxTurns to the minimum needed. High maxTurns on leaf agents wastes tokens and can loop. Low maxTurns on orchestrators causes incomplete work.

## Memory Scope Selection

```yaml
# user scope: persists across ALL projects
# Use for: learned preferences, personal context, cross-project state
memory:
  scope: user

# project scope: persists within this project only
# Use for: project state, task progress, accumulated findings
memory:
  scope: project

# local scope: session only, cleared when session ends
# Use for: temporary computation, scratch work, one-shot analysis
memory:
  scope: local
```

## tools Field for Restricting Subagent Spawning

```yaml
# Read-only agent - can only read, search, list
tools:
  - Read
  - Glob
  - Grep
  - Bash(find:*, ls:*, cat:*)

# Code writer - can write but not execute
tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Glob
  - Grep

# Bash-restricted agent - grep and find only
tools:
  - Read
  - Glob
  - Grep
  - Bash(grep:*, find:*, ls:*)

# No subagent spawning (omit Task from tools)
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash

# Allow subagent spawning (include Task)
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
```

## skills Field for Preloading Knowledge

```yaml
# Preload domain knowledge into agent context before it starts
skills:
  - sdk-patterns          # Loads SDK_PATTERNS.md
  - testing-rules         # Loads TESTING_RULES.md
  - security-auditor      # Loads security patterns
```

Skills listed here are injected as context before the agent's first turn. Useful for domain-specific subagents that need specialized knowledge without a long system prompt.

## 5 Agent Templates

### Template 1: Fast Researcher

Purpose: Rapidly reads and summarizes files. Read-only. Cheap and fast.

```yaml
name: fast-researcher
description: Quickly reads files and produces summaries. No writes, no execution.
version: 1.0.0
model: claude-haiku-3-5
permissionMode: plan
maxTurns: 10
memory:
  scope: local
tools:
  - Read
  - Glob
  - Grep
  - Bash(find:*, ls:*)
tags:
  - research
  - read-only
  - fast
system: |
  You are a fast research agent. Your only job is to read files, search for
  patterns, and produce concise summaries. You NEVER modify files. You NEVER
  execute code. You output findings in structured markdown.

  When done, end with: RESEARCH COMPLETE: [one-line summary]
```

### Template 2: Code Reviewer

Purpose: Reviews code quality, security, and patterns. Uses Opus for depth.

```yaml
name: code-reviewer
description: Reviews code for quality, security issues, and pattern adherence.
version: 1.0.0
model: claude-opus-4-6
permissionMode: plan
maxTurns: 15
memory:
  scope: local
tools:
  - Read
  - Glob
  - Grep
  - Bash(grep:*, find:*)
skills:
  - security-auditor
tags:
  - review
  - quality
  - security
system: |
  You are an expert code reviewer. Analyze code for:
  1. Security vulnerabilities (injection, auth bypass, secrets in code)
  2. Performance issues (N+1 queries, blocking I/O, memory leaks)
  3. Pattern adherence (project conventions from context files)
  4. Test coverage gaps

  Output format:
  ## CRITICAL (must fix)
  ## WARNINGS (should fix)
  ## SUGGESTIONS (nice to have)
  ## PASSED (what looks good)

  End with: REVIEW COMPLETE: [PASS|FAIL] - [reason]
```

### Template 3: Code Generator

Purpose: Implements features based on specs. Writes multiple files. Standard access.

```yaml
name: code-generator
description: Implements features from specs. Writes production-ready code.
version: 1.0.0
model: claude-sonnet-4-6
permissionMode: acceptEdits
maxTurns: 30
memory:
  scope: project
tools:
  - Read
  - Write
  - Edit
  - MultiEdit
  - Glob
  - Grep
  - Bash(python3:*, pytest:*, ruff:*, mypy:*)
skills:
  - testing-rules
tags:
  - implementation
  - code-generation
system: |
  You are a code generator. You implement features based on specifications.

  Before writing any code:
  1. Read the relevant spec files
  2. Read existing code to understand patterns
  3. Plan your implementation (list files to create/modify)

  After writing code:
  1. Run linters (ruff check, mypy)
  2. Run tests if they exist
  3. Fix any failures before finishing

  End with: IMPLEMENTATION COMPLETE: [files created/modified]
```

### Template 4: Security Auditor

Purpose: Deep security scanning. Read-only with grep. Uses Opus for thoroughness.

```yaml
name: security-auditor
description: Deep security audit - finds vulnerabilities, secrets, and attack vectors.
version: 1.0.0
model: claude-opus-4-6
permissionMode: plan
maxTurns: 20
memory:
  scope: local
tools:
  - Read
  - Glob
  - Grep
  - Bash(grep:*, find:*, git:*)
tags:
  - security
  - audit
  - read-only
system: |
  You are a security auditor. Perform comprehensive security analysis.

  SCAN FOR:
  - Hardcoded secrets: API keys, passwords, tokens assigned to variables
  - SQL injection: string formatting used to build raw query strings
  - Authentication bypass: missing auth checks on sensitive routes
  - Insecure deserialization: unsafe loading of serialized data from untrusted input
  - Path traversal: user input used directly in file path construction
  - SSRF: user-controlled URLs passed to HTTP client calls
  - Dependency vulnerabilities: check requirements.txt and package.json versions
  - Sensitive data exposure: secrets or PII written to log statements

  SEARCH PATTERNS TO CHECK (use Grep tool):
  - "password" near assignment operators
  - "api_key" near assignment operators
  - "secret" near assignment operators
  - raw query construction with string formatting
  - open() calls where argument contains request data
  - Hardcoded localhost or internal IPs in production code

  Output: Severity (CRITICAL/HIGH/MEDIUM/LOW) + File + Line + Description + Fix

  End with: AUDIT COMPLETE: [N] critical, [N] high, [N] medium, [N] low
```

### Template 5: Orchestrator Worker

Purpose: Manages multi-phase work, spawns subagents. High maxTurns. Task access.

```yaml
name: orchestrator-worker
description: Manages complex multi-phase tasks by coordinating specialized subagents.
version: 1.0.0
model: claude-sonnet-4-6
permissionMode: default
maxTurns: 50
memory:
  scope: project
tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
tags:
  - orchestrator
  - multi-agent
  - workflow
system: |
  You are an orchestrator. You coordinate specialized subagents to complete
  complex multi-phase tasks.

  PRINCIPLES:
  1. Dispatch independent work in PARALLEL (all Task calls in one message)
  2. Run dependent phases SEQUENTIALLY (wait for result before next)
  3. Enforce quality gates - BLOCK progress if gates fail
  4. Checkpoint progress in .claude/checkpoints/
  5. Never do work yourself that a specialist can do better

  DISPATCH PATTERN:
  - Research phase: fast-researcher agents (parallel)
  - Implementation: code-generator agents (parallel per module)
  - Review: code-reviewer agents (parallel per component)
  - Security: security-auditor agent (after implementation)

  End with: ORCHESTRATION COMPLETE: [phases completed] / [phases failed]
```

## Integration with SKILL.md

Reference agents in your skill's Task calls. The `subagent_type` must match the agent filename:

```markdown
<!-- In SKILL.md, Phase 3: Implementation -->

For each module to implement, dispatch a code-generator subagent:

Use the Task tool with subagent_type "code-generator" and provide:
- The spec file path
- The target directory
- Existing patterns to follow

Dispatch ALL independent modules in ONE message for parallel execution.
Wait for all implementations to complete before proceeding to review.

<!-- Phase 4: Review -->

Dispatch a code-reviewer subagent on the implementation output.
Use Task tool with subagent_type "code-reviewer".
If review returns FAIL, halt and report issues. Do NOT proceed to deployment.
```

Custom agents are referenced by their filename. If your agent file is `.claude/agents/data-pipeline-builder.yml`, reference it as:

```javascript
Task({
  subagent_type: "data-pipeline-builder",
  prompt: "Build the ETL pipeline for the orders table...",
  description: "ETL pipeline implementation"
})
```
