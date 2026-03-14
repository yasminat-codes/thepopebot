# Hook Patterns for Claude Code Skills

## All 14 Hook Events

| Event | Phase | Fires When |
|---|---|---|
| `PreToolUse` | Before tool execution | Any tool is about to run |
| `PostToolUse` | After tool execution | Any tool has completed |
| `Notification` | Async | Claude sends a notification |
| `Stop` | End of turn | Claude finishes responding |
| `SubagentStop` | Subagent end | A spawned subagent finishes |
| `SessionStart` | Session init | Claude Code session begins |
| `SessionEnd` | Session teardown | Claude Code session ends |
| `UserPromptSubmit` | Prompt received | User submits a message |
| `AssistantResponse` | Response generated | Claude emits a response |
| `ToolError` | Tool failure | A tool returns an error |
| `MemoryLoad` | Memory read | Claude reads memory files |
| `MemorySave` | Memory write | Claude writes memory files |
| `SkillLoad` | Skill invoked | A skill is being loaded |
| `AgentHandoff` | Agent transition | Control passes to subagent |

### When to Use Each Event

- `PreToolUse` - Validate inputs, check permissions, enforce locks before execution
- `PostToolUse` - Run linters, log actions, checkpoint state after execution
- `Stop` - Quality gates, test runners, summary generation at turn end
- `SubagentStop` - Checkpoint subagent output, aggregate results, log completion
- `SessionStart` - Load context, check environment, set up resources once
- `SessionEnd` - Cleanup, final logging, release locks
- `UserPromptSubmit` - Input sanitization, rate limiting, routing
- `Notification` - Async side effects (Slack, logging) that must not block

## 4 Hook Types

### 1. command
Runs a shell command. Most common type.
```yaml
hooks:
  PreToolUse:
    - type: command
      command: /path/to/hook.sh
      blockOnFailure: true
```

### 2. remote
Calls an HTTP endpoint.
```yaml
hooks:
  PostToolUse:
    - type: remote
      url: https://audit.internal/log
      method: POST
      blockOnFailure: false
```

### 3. prompt
Injects a system prompt fragment into Claude's context.
```yaml
hooks:
  SessionStart:
    - type: prompt
      text: "Always explain your reasoning before executing commands."
```

### 4. agent
Spawns a subagent to handle the hook event.
```yaml
hooks:
  Stop:
    - type: agent
      agent: quality-gate-agent
      blockOnFailure: true
```

## Hook Configuration in SKILL.md Frontmatter

Hooks are declared in the skill's `SKILL.md` frontmatter under the `hooks` key. Skill-scoped hooks only fire when the skill is active.

```yaml
---
name: my-skill
version: 1.0.0
description: Example skill with hooks
hooks:
  PreToolUse:
    - type: command
      command: .claude/skills/my-skill/hooks/pre-tool.sh
      matcher: "^(Bash|Write|Edit)$"
      blockOnFailure: true
  PostToolUse:
    - type: command
      command: .claude/skills/my-skill/hooks/post-tool.sh
      matcher: "^(Write|Edit)$"
      blockOnFailure: false
  SessionStart:
    - type: command
      command: .claude/skills/my-skill/hooks/session-start.sh
      once: true
---
```

## Hook Script Template with Safety Patterns

```bash
#!/bin/bash
set -euo pipefail

# Read hook input from stdin (always JSON)
INPUT=$(cat)

# Extract fields safely with defaults
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
TOOL_INPUT=$(echo "$INPUT" | jq -r '.tool_input // {}')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
EVENT_TYPE=$(echo "$INPUT" | jq -r '.event_type // empty')

# Log to stderr (never stdout - stdout is reserved for JSON output)
log() { echo "[$(date -u +%H:%M:%S)] $*" >&2; }

log "Hook fired: event=$EVENT_TYPE tool=$TOOL_NAME"

# Validation logic here
if [[ -z "$TOOL_NAME" ]]; then
  log "No tool name provided, allowing"
  exit 0
fi

# Return structured JSON response (optional, for context injection)
# echo '{"context": "additional context here"}'

exit 0  # allow (non-zero = block if blockOnFailure: true)
```

## 8 Production-Ready Hook Patterns

### 1. Bash Command Validator (Block Dangerous Commands)

```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')

[[ "$TOOL_NAME" != "Bash" ]] && exit 0

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

DANGEROUS_PATTERNS=(
  "rm -rf /"
  "rm -rf ~"
  "> /dev/sda"
  "dd if=/dev/zero"
  "fork bomb"
  ":(){ :|:& };"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qF "$pattern"; then
    echo "BLOCKED: Dangerous command pattern detected: $pattern" >&2
    exit 1
  fi
done

exit 0
```

Config:
```yaml
hooks:
  PreToolUse:
    - type: command
      command: .claude/hooks/bash-validator.sh
      matcher: "^Bash$"
      blockOnFailure: true
```

### 2. Auto-Linter on File Save (PostToolUse on Write/Edit)

```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')

[[ -z "$FILE_PATH" ]] && exit 0

case "$FILE_PATH" in
  *.py)
    command -v ruff &>/dev/null && ruff check --fix "$FILE_PATH" >&2 || true
    command -v ruff &>/dev/null && ruff format "$FILE_PATH" >&2 || true
    ;;
  *.ts|*.tsx|*.js|*.jsx)
    command -v eslint &>/dev/null && eslint --fix "$FILE_PATH" >&2 || true
    ;;
  *.go)
    command -v gofmt &>/dev/null && gofmt -w "$FILE_PATH" >&2 || true
    ;;
esac

exit 0
```

Config:
```yaml
hooks:
  PostToolUse:
    - type: command
      command: .claude/hooks/auto-linter.sh
      matcher: "^(Write|Edit)$"
      blockOnFailure: false
```

### 3. Audit Logger (PostToolUse, Async)

```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)
LOG_FILE="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/logs/audit.jsonl"
mkdir -p "$(dirname "$LOG_FILE")"

ENTRY=$(echo "$INPUT" | jq --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '{timestamp: $ts, event: .event_type, tool: .tool_name, session: .session_id}')

echo "$ENTRY" >> "$LOG_FILE"
exit 0  # Never block on audit logging
```

Config:
```yaml
hooks:
  PostToolUse:
    - type: command
      command: .claude/hooks/audit-logger.sh
      blockOnFailure: false  # NEVER block on logging
```

### 4. Pre-Flight Environment Checker (SessionStart)

```bash
#!/bin/bash
set -euo pipefail
ERRORS=()

# Check required env vars
for var in DATABASE_URL OPENAI_API_KEY; do
  [[ -z "${!var:-}" ]] && ERRORS+=("Missing required env var: $var")
done

# Check required tools
for tool in jq python3 docker; do
  command -v "$tool" &>/dev/null || ERRORS+=("Required tool not found: $tool")
done

# Check .env file exists
[[ ! -f ".env" ]] && ERRORS+=("Missing .env file - copy from .env.example")

if [[ ${#ERRORS[@]} -gt 0 ]]; then
  echo "Pre-flight check failed:" >&2
  printf '  - %s\n' "${ERRORS[@]}" >&2
  exit 1
fi

echo "Pre-flight checks passed" >&2
exit 0
```

Config:
```yaml
hooks:
  SessionStart:
    - type: command
      command: .claude/hooks/preflight.sh
      blockOnFailure: true
      once: true
```

### 5. Context Loader (SessionStart, once: true)

```bash
#!/bin/bash
set -euo pipefail
CONTEXT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/context"

if [[ ! -d "$CONTEXT_DIR" ]]; then
  echo "No context directory found, skipping" >&2
  exit 0
fi

# Output context as JSON for Claude to consume
CONTEXT_FILES=()
while IFS= read -r -d '' file; do
  CONTEXT_FILES+=("$file")
done < <(find "$CONTEXT_DIR" -name "*.md" -print0 2>/dev/null)

if [[ ${#CONTEXT_FILES[@]} -eq 0 ]]; then
  exit 0
fi

echo "Loading ${#CONTEXT_FILES[@]} context files" >&2
exit 0
```

Config:
```yaml
hooks:
  SessionStart:
    - type: command
      command: .claude/hooks/context-loader.sh
      once: true
      blockOnFailure: false
```

### 6. Deployment Lock Checker (PreToolUse on Bash)

```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')
LOCK_FILE="/tmp/deploy.lock"

# Only gate deployment commands
echo "$COMMAND" | grep -qE "(deploy|kubectl apply|helm upgrade|docker push)" || exit 0

if [[ -f "$LOCK_FILE" ]]; then
  LOCKER=$(cat "$LOCK_FILE")
  echo "Deployment locked by: $LOCKER" >&2
  echo "Remove $LOCK_FILE to proceed" >&2
  exit 1
fi

echo "$(whoami) at $(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT
exit 0
```

Config:
```yaml
hooks:
  PreToolUse:
    - type: command
      command: .claude/hooks/deploy-lock.sh
      matcher: "^Bash$"
      blockOnFailure: true
```

### 7. Test Runner Gate (Stop Event, blockOnFailure)

```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)

# Only run if Python files were modified this session
MODIFIED=$(echo "$INPUT" | jq -r '.modified_files // [] | .[] | select(endswith(".py"))' 2>/dev/null || echo "")

[[ -z "$MODIFIED" ]] && exit 0

echo "Running test suite after modifications..." >&2

if command -v pytest &>/dev/null; then
  pytest --tb=short -q 2>&1 | tail -20 >&2
  exit "${PIPESTATUS[0]}"
fi

exit 0
```

Config:
```yaml
hooks:
  Stop:
    - type: command
      command: .claude/hooks/test-gate.sh
      blockOnFailure: true
```

### 8. Subagent Output Checkpointer (SubagentStop)

```bash
#!/bin/bash
set -euo pipefail
INPUT=$(cat)
CHECKPOINT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}/.claude/checkpoints"
mkdir -p "$CHECKPOINT_DIR"

AGENT_ID=$(echo "$INPUT" | jq -r '.agent_id // "unknown"')
TIMESTAMP=$(date -u +%Y%m%dT%H%M%SZ)
CHECKPOINT_FILE="$CHECKPOINT_DIR/${AGENT_ID}-${TIMESTAMP}.json"

echo "$INPUT" | jq '{
  agent_id: .agent_id,
  completed_at: now | todate,
  output_summary: .output[:500],
  status: .status
}' > "$CHECKPOINT_FILE"

echo "Checkpointed agent $AGENT_ID to $CHECKPOINT_FILE" >&2
exit 0
```

Config:
```yaml
hooks:
  SubagentStop:
    - type: command
      command: .claude/hooks/checkpoint.sh
      blockOnFailure: false
```

## blockOnFailure Effect by Event Table

| Event | blockOnFailure: true effect | blockOnFailure: false effect |
|---|---|---|
| `PreToolUse` | Tool execution is cancelled | Tool runs regardless |
| `PostToolUse` | Turn is halted with error | Continues normally |
| `Stop` | Response is suppressed | Response delivered anyway |
| `SubagentStop` | Parent agent receives error | Parent continues |
| `SessionStart` | Session refuses to start | Session starts anyway |
| `UserPromptSubmit` | Prompt is rejected | Prompt processed |

## Matcher Regex Patterns

```yaml
# Match specific tools
matcher: "^Bash$"
matcher: "^(Write|Edit|MultiEdit)$"
matcher: "^(Read|Glob|Grep)$"

# Match all file-writing tools
matcher: "^(Write|Edit|MultiEdit|NotebookEdit)$"

# Match agent tools
matcher: "^(Task|Agent)$"

# Match everything (omit matcher field for global)
# No matcher = fires on all tools for that event
```

## Environment Variables Available to Hook Scripts

```bash
CLAUDE_PROJECT_DIR    # Absolute path to project root
CLAUDE_SESSION_ID     # Unique session identifier
CLAUDE_MODEL          # Model being used (e.g. claude-sonnet-4-6)
CLAUDE_SKILL_NAME     # Active skill name (if skill-scoped hook)
CLAUDE_HOOK_EVENT     # Current event type
CLAUDE_TOOL_NAME      # Tool being used (PreToolUse/PostToolUse only)
```

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Missing shebang (`#!/bin/bash`) | Undefined shell behavior | Always add `#!/bin/bash` as line 1 |
| No `set -euo pipefail` | Silent failures, unset vars ignored | Add immediately after shebang |
| Writing to stdout for logging | Interferes with JSON response parsing | Always log to stderr: `echo "msg" >&2` |
| `blockOnFailure: true` on async work | Blocks Claude for slow operations | Use `blockOnFailure: false` for I/O hooks |
| Calling external APIs synchronously | Network latency blocks every tool call | Use async via background processes or `blockOnFailure: false` |
| Hardcoded paths | Breaks on other machines | Use `$CLAUDE_PROJECT_DIR` or `$(pwd)` |
| No input validation | Crashes on unexpected hook payloads | Always use `// empty` or `// {}` defaults in jq |
| Blocking `Stop` hooks with tests | Makes every turn slow | Only run tests when relevant files changed |
