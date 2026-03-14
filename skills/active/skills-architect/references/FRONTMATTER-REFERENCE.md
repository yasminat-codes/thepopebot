# Frontmatter Reference: Complete Claude Code Skill Specification

This document covers all 14+ frontmatter fields for Claude Code skill files. Use it as the
authoritative reference when writing, auditing, or migrating skill frontmatter.

---

## Group 1: Base Spec Fields

These fields form the core identity and capability declaration of a skill.

### `name`

| Property | Value |
|---|---|
| Type | string |
| Required | Yes |
| Max length | 64 characters |
| Default | None |
| Pattern | `[a-z][a-z0-9-]*` (lowercase, hyphens only) |

**Rules:**
- Must be unique within its namespace
- Use hyphens, not underscores
- Namespaced skills use colon: `namespace:skill-name`
- The name appears in the skill index Claude reads at startup

**Examples:**
```yaml
name: docker-configurator
name: yasmine:develop-sdk-agent
name: coolify:health-check
```

---

### `description`

| Property | Value |
|---|---|
| Type | string |
| Required | Yes |
| Max length | 1024 characters (hard limit, truncated beyond this) |
| Default | None |
| Target | 800-950 characters for safety margin |

**Rules:**
- Apply full CSO formula (see CSO-ENGINE.md)
- Must contain "PROACTIVELY" if Claude should auto-invoke
- Must contain quoted trigger phrases
- No vague language ("helps with", "assists", "works with")

**Example:**
```yaml
description: |
  Generates production Dockerfiles and docker-compose configs for FastAPI and Node.js.
  Use PROACTIVELY when user says "add a dockerfile", "containerize this",
  "set up docker", "write a compose file", or mentions Docker, Coolify, containers.
  Also use when user opens Dockerfile, docker-compose.yml, or .dockerignore.
  Part of deployment toolkit with coolify-deployer and nginx-configurator.
```

---

### `allowed-tools`

| Property | Value |
|---|---|
| Type | array of strings |
| Required | No |
| Default | All tools available to Claude |
| Effect | Restricts which built-in tools the skill can use |

**Rules:**
- Use to enforce principle of least privilege
- Omitting allows all tools (risky for automated skills)
- Tool names are exact: `Read`, `Write`, `Edit`, `Bash`, `Glob`, `Grep`, `WebFetch`, `WebSearch`

**Examples:**
```yaml
allowed-tools:
  - Read
  - Glob
  - Grep

allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
```

---

### `license`

| Property | Value |
|---|---|
| Type | string |
| Required | No (recommended for shared skills) |
| Default | None |
| Format | SPDX identifier preferred |

**Examples:**
```yaml
license: MIT
license: Apache-2.0
license: proprietary
```

---

### `compatibility`

| Property | Value |
|---|---|
| Type | object |
| Required | No |
| Default | All versions |

**Fields:**
```yaml
compatibility:
  claude-code: ">=1.0.0"   # Minimum Claude Code version
  model: "claude-3-5-*"    # Model pattern (glob)
```

---

### `metadata`

| Property | Value |
|---|---|
| Type | object |
| Required | No |
| Default | Empty |

**Common keys:**

| Key | Type | Purpose |
|---|---|---|
| `version` | string (semver) | Skill version for changelog tracking |
| `author` | string | Creator identifier |
| `tags` | array | Categorization labels |
| `category` | string | Skill category (deployment, testing, planning) |
| `created` | string (ISO date) | Creation date |
| `updated` | string (ISO date) | Last update date |
| `test-coverage` | number | Percentage of scenarios tested |
| `stability` | string | stable, beta, experimental |

**Example:**
```yaml
metadata:
  version: "2.1.0"
  author: yasmine
  tags: [docker, deployment, fastapi]
  category: deployment
  stability: stable
  updated: "2026-02-28"
```

---

## Group 2: Claude Code Extension Fields

These fields control how Claude Code specifically handles skill invocation and execution.

### `disable-model-invocation`

| Property | Value |
|---|---|
| Type | boolean |
| Required | No |
| Default | `false` |
| Effect | When `true`, Claude will NOT auto-invoke this skill based on context |

**Rules:**
- Set to `true` for skills that should only run when explicitly called by the user or composed
  into another skill
- Set to `false` (default) for skills Claude should invoke autonomously

**Examples:**
```yaml
disable-model-invocation: false   # Claude auto-invokes (default)
disable-model-invocation: true    # User must call explicitly
```

---

### `user-invocable`

| Property | Value |
|---|---|
| Type | boolean |
| Required | No |
| Default | `true` |
| Effect | When `false`, skill does not appear in skill index for user selection |

**Rules:**
- Set to `false` for internal/helper skills used only by other skills
- Set to `true` (default) for any skill users should be able to invoke by name

---

### `context`

| Property | Value |
|---|---|
| Type | array of strings |
| Required | No |
| Default | Empty |
| Effect | Files Claude automatically reads before running the skill |

**Rules:**
- Paths relative to project root
- Supports glob patterns
- Claude reads these files silently before executing skill body
- Use for project-specific context the skill always needs

**Examples:**
```yaml
context:
  - .claude/context/PROJECT_CONTEXT.md
  - .claude/context/SDK_PATTERNS.md
  - specs/agents/*.yaml
```

---

### `agent`

| Property | Value |
|---|---|
| Type | string (agent name) or inline object |
| Required | No |
| Default | Uses default Claude agent |
| Effect | Specifies which agent configuration to use for this skill |

**Rules:**
- Can reference a named agent defined elsewhere
- Can be an inline agent definition (see custom agent frontmatter section)
- When omitted, skill runs under the invoking Claude session's agent

**Example (reference):**
```yaml
agent: research-agent
```

---

### `model`

| Property | Value |
|---|---|
| Type | string |
| Required | No |
| Default | Inherits from calling session |
| Effect | Overrides which Claude model executes this skill |

**Rules:**
- Only specify when skill requires a specific model capability
- Current valid IDs: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-3-5`
- Opus for complex reasoning; Sonnet for balanced; Haiku for fast/cheap tasks

**Examples:**
```yaml
model: claude-opus-4-6      # Maximum reasoning for architecture design
model: claude-haiku-3-5     # Fast execution for simple transformations
```

---

### `argument-hint`

| Property | Value |
|---|---|
| Type | string |
| Required | No |
| Default | None |
| Effect | Shown to user as argument prompt when invoking the skill |
| Max length | 128 characters |

**Examples:**
```yaml
argument-hint: "agent-name (e.g., payment-processor)"
argument-hint: "[audit|update|security|full]"
argument-hint: "path/to/spec.yaml or leave blank for interactive mode"
```

---

### `hooks`

| Property | Value |
|---|---|
| Type | object |
| Required | No |
| Default | None |
| Effect | Shell scripts that run at lifecycle events |

**Hook events:**

| Event | When it runs | Use for |
|---|---|---|
| `pre-invoke` | Before skill body executes | Validation, environment checks |
| `post-invoke` | After skill completes successfully | Cleanup, notifications, logging |
| `on-error` | When skill throws an error | Error logging, rollback |

**Example:**
```yaml
hooks:
  pre-invoke: .claude/hooks/check-git-clean.sh
  post-invoke: .claude/hooks/notify-complete.sh
  on-error: .claude/hooks/log-failure.sh
```

---

## Invocation Control Matrix

The combination of `disable-model-invocation` and `user-invocable` determines all possible
invocation behaviors.

| `disable-model-invocation` | `user-invocable` | Can Claude auto-invoke? | Can user call by name? | Use case |
|---|---|---|---|---|
| `false` | `true` | Yes | Yes | Standard skills (DEFAULT) |
| `false` | `false` | Yes | No | Background helper, auto-only |
| `true` | `true` | No | Yes | Explicit-only skill, user must ask |
| `true` | `false` | No | No | Inert; composed into other skills only |

---

## Built-in Agent Types

When using the `agent` field without a custom definition, these built-in types are available.

| Agent Type | Description | Best for |
|---|---|---|
| `general-purpose` | Default Claude behavior, full context access | Most skills |
| `Explore` | Read-only mode, no file writes | Research, analysis, auditing |
| `Plan` | Produces structured plans, limited actions | Architecture, spec generation |

---

## Custom Agent Frontmatter

When a skill needs a fully custom agent, define it inline under the `agent` key. Custom agents
support 10 fields.

```yaml
agent:
  name: string                    # Internal agent identifier
  description: string             # What this agent does
  model: string                   # Model ID override
  allowed-tools: [string]         # Built-in tools this agent can use
  tools: [string]                 # MCP tool names available
  disallowedTools: [string]       # Explicitly blocked tools
  permissionMode: string          # How permissions are granted
  mcpServers: {object}            # MCP server configs keyed by name
  skills: [string]                # Sub-skills this agent can invoke
  memory: string                  # Memory scope for this agent
  maxTurns: number                # Max conversation turns before stopping
```

### `permissionMode` Values

| Value | Behavior |
|---|---|
| `default` | Standard permission prompting |
| `acceptEdits` | Auto-accepts file edits without prompting |
| `bypassPermissions` | Skips all permission checks (use carefully) |
| `restricted` | Extra-strict, prompts for every action |

### `memory` Scopes

| Scope | What is remembered |
|---|---|
| `none` | No memory; each invocation is fresh |
| `session` | Remembers within current Claude Code session |
| `project` | Remembers across sessions within the project |
| `global` | Remembers across all projects (user-level) |

### `maxTurns` Guidelines

| Skill complexity | Recommended maxTurns |
|---|---|
| Simple (read + respond) | 5-10 |
| Moderate (read, analyze, write) | 15-25 |
| Complex (multi-step workflow) | 30-50 |
| Orchestrator (delegates to sub-agents) | 50-100 |

---

## Complete Working Examples

### Simple Skill (Minimal Frontmatter)

```yaml
---
name: env-validator
description: >
  Validates .env files against .env.example and reports missing or extra variables.
  Use PROACTIVELY when user says "check env", "missing env vars", "env validation",
  or opens .env, .env.example, .env.local.
allowed-tools:
  - Read
  - Glob
---
```

---

### Intermediate Skill (With Context and Metadata)

```yaml
---
name: migration-checker
description: >
  Validates Alembic migration files for schema consistency and ordering errors in
  PostgreSQL projects. Use PROACTIVELY when user says "check migrations", "migration error",
  "run alembic", "validate schema", or mentions Alembic, SQLAlchemy, or schema drift.
  Use when reviewing database changes or opening alembic.ini, env.py, or versions/*.py.
  Part of database toolkit with schema-refiner and seed-generator.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
argument-hint: "path/to/alembic directory (default: ./alembic)"
metadata:
  version: "1.2.0"
  author: yasmine
  tags: [database, alembic, postgresql, migrations]
  category: database
  stability: stable
  updated: "2026-02-28"
compatibility:
  claude-code: ">=1.0.0"
---
```

---

### Advanced Skill (Custom Agent, Hooks, Full Config)

```yaml
---
name: sdk-agent-production-builder
description: >
  Builds production-ready Claude Agent SDK agents with full test suites, Docker configs,
  and Coolify deployment files. Use PROACTIVELY when user says "build the agent",
  "make it production ready", "finalize the agent", "deploy the agent", "ship this agent",
  or mentions production deployment of a Claude SDK agent.
  Also use when user opens agent.py, main.py, or any file in agents/ directory.
  Part of SDK agent toolkit with sdk-agent-implementer and sdk-agent-security-reviewer.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
argument-hint: "agent-name (must match existing spec in specs/agents/)"
context:
  - .claude/context/SDK_PATTERNS.md
  - .claude/context/CODE_QUALITY_RULES.md
  - .claude/context/TESTING_RULES.md
model: claude-opus-4-6
agent:
  name: production-builder-agent
  description: Builds and validates production agent implementations
  permissionMode: acceptEdits
  memory: session
  maxTurns: 50
  disallowedTools:
    - WebSearch
hooks:
  pre-invoke: .claude/hooks/check-spec-exists.sh
  post-invoke: .claude/hooks/run-tests.sh
  on-error: .claude/hooks/log-build-failure.sh
metadata:
  version: "3.0.0"
  author: yasmine
  tags: [sdk, agent, production, docker, coolify]
  category: agent-development
  stability: stable
  test-coverage: 94
  updated: "2026-02-28"
license: MIT
compatibility:
  claude-code: ">=1.2.0"
  model: "claude-opus-4-6"
---
```

---

## Field Quick Reference

| Field | Group | Required | Type | Key Rule |
|---|---|---|---|---|
| `name` | Base | Yes | string | lowercase, hyphens, max 64 chars |
| `description` | Base | Yes | string | CSO formula, max 1024 chars |
| `allowed-tools` | Base | No | array | Least privilege; omit = all tools |
| `license` | Base | No | string | SPDX identifier preferred |
| `compatibility` | Base | No | object | semver for claude-code, glob for model |
| `metadata` | Base | No | object | version, author, tags, stability |
| `disable-model-invocation` | Extension | No | boolean | false = auto-invoke (default) |
| `user-invocable` | Extension | No | boolean | true = user can call (default) |
| `context` | Extension | No | array | Relative paths, glob supported |
| `agent` | Extension | No | string or object | Built-in name or custom definition |
| `model` | Extension | No | string | Override only when necessary |
| `argument-hint` | Extension | No | string | Max 128 chars, shown at invocation |
| `hooks` | Extension | No | object | pre-invoke, post-invoke, on-error |
