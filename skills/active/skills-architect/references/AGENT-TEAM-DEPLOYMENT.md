# Agent Team Deployment — Fan-Out Parallel File Generation

> Deploy a team of writing agents in ONE message for maximum speed.
> All agents run simultaneously. A Tier 6 skill that takes 10+ minutes
> sequentially completes in 2-3 minutes with parallel agents.

## The Fan-Out Rule

**ALL Task calls for file generation MUST be dispatched in a SINGLE message.**

One message → multiple Task calls → true parallel execution.
Multiple messages → sequential execution → slow.

```
WRONG (sequential):
  Message 1: Task(write SKILL.md) → wait
  Message 2: Task(write references) → wait
  Message 3: Task(write scripts) → wait

RIGHT (parallel):
  Message 1: Task(write SKILL.md) + Task(write refs batch 1) + Task(write refs batch 2) + Task(write scripts)
  → all run simultaneously → collect results
```

## Team Configurations by Tier

### Tier 1-3: 2 Agents (Simple Skills)

| Agent | Writes | Model |
|-------|--------|-------|
| A: Skill Writer | SKILL.md | sonnet |
| B: Docs Writer | README.md + CHANGELOG.md | haiku |

Estimated time: ~30 seconds parallel vs ~60 seconds sequential.

### Tier 4-5: 4 Agents (Advanced Skills)

| Agent | Writes | Model |
|-------|--------|-------|
| A: Skill Writer | SKILL.md (with all directives) | sonnet |
| B: Refs Writer 1 | First half of reference files | sonnet |
| C: Refs Writer 2 | Second half of reference files | sonnet |
| D: Support Writer | scripts/ + README.md + CHANGELOG.md | sonnet |

Estimated time: ~90 seconds parallel vs ~5 minutes sequential.

### Tier 6-7: 6 Agents (Orchestrators & Systems)

| Agent | Writes | Model |
|-------|--------|-------|
| A: Skill Writer | SKILL.md (orchestrator template + directives) | sonnet |
| B: Phase Refs | Phase/workflow reference files | sonnet |
| C: Pattern Refs | Quality/pattern reference files | sonnet |
| D: Advanced Refs | Integration/advanced reference files | sonnet |
| E: Scripts Writer | All scripts/ + chmod +x | sonnet |
| F: Docs + Agents | Agent YAML + README.md + CHANGELOG.md | sonnet |

Estimated time: ~2-3 minutes parallel vs ~10+ minutes sequential.

## Agent Prompt Template

Each agent receives a detailed prompt with ALL context needed to write independently:

```markdown
You are writing files for a new Claude Code skill called "{{SKILL_NAME}}".

## Context from Interview
- Purpose: {{PURPOSE}}
- Tier: {{TIER}}
- Tools: {{TOOLS}}
- Workflow: {{WORKFLOW_TYPE}}
- Phases: {{PHASE_LIST}}
- CSO Description: {{DESCRIPTION}}
- Frontmatter: {{FRONTMATTER_YAML}}

## Your Assignment
Write the following files to {{OUTPUT_PATH}}:

### File 1: {{FILE_PATH}}
- Purpose: {{FILE_PURPOSE}}
- Line target: {{LINE_ESTIMATE}}
- Content requirements: {{CONTENT_SPEC}}

### File 2: {{FILE_PATH}}
...

## Quality Rules
- Maximum lines per file: 400 (references), 500/600 (SKILL.md)
- Include → See directives for every reference (SKILL.md writer only)
- Scripts must have #!/bin/bash and set -euo pipefail
- Use the Write tool to create each file
```

## Task Tool Call Pattern

```javascript
// Dispatch ALL agents in ONE message — this is CRITICAL for parallelism
Task({
  subagent_type: "general-purpose",
  description: "Write SKILL.md for {{name}}",
  prompt: "...",  // Full prompt with all context
  model: "sonnet",
  run_in_background: true
})

Task({
  subagent_type: "general-purpose",
  description: "Write references batch 1 for {{name}}",
  prompt: "...",
  model: "sonnet",
  run_in_background: true
})

// ... more Task calls in the SAME message
```

## File Assignment Strategy

### How to Split References Across Agents

Split by logical concern, NOT alphabetically:

**Batch 1 — Workflow References:**
- Phase-specific files (PHASE-1.md, PHASE-2.md, ...)
- Workflow files (WORKFLOW.md, SEQUENTIAL-STEPS.md)
- Interview/question files (QUESTIONS.md)

**Batch 2 — Quality References:**
- Quality gates (QUALITY-GATES.md)
- Error handling (ERROR-HANDLING.md)
- Validation (VALIDATION.md)
- Testing (TESTING.md)

**Batch 3 — Pattern References (Tier 6+ only):**
- Advanced patterns (PATTERNS.md)
- Orchestration (ORCHESTRATION.md)
- Integration (INTEGRATION.md)
- Memory (MEMORY.md)

### How to Handle Dependencies Between Agents

Agents write files independently — no cross-agent dependencies.

The SKILL.md writer (Agent A) generates all `→ See` directives based on the
planned file list, NOT by reading the actual reference files. Reference writers
follow the content spec without needing to read SKILL.md.

This is possible because the folder structure and file list are determined
BEFORE agent deployment (in Phase 7).

## Collecting Results

After all agents complete:

1. Verify all expected files exist (Glob for expected paths)
2. Count lines per file (check against estimates)
3. Run orphan check (every reference has a directive)
4. If any agent failed, re-dispatch ONLY that agent
5. Present file list + line counts to user

## Error Recovery

| Failure | Recovery |
|---------|----------|
| Agent times out | Re-dispatch with same prompt |
| Agent writes wrong path | Move file to correct path |
| Agent exceeds line limit | Re-dispatch with stricter limit |
| Agent misses a file | Dispatch single-file agent |
| All agents fail | Fall back to sequential writing |

## Performance Benchmarks

| Tier | Files | Sequential | Parallel | Speedup |
|------|-------|-----------|----------|---------|
| 1-2 | 2-3 | ~45s | ~25s | 1.8x |
| 3 | 4-6 | ~2m | ~50s | 2.4x |
| 4 | 8-12 | ~5m | ~1.5m | 3.3x |
| 5 | 12-18 | ~8m | ~2m | 4x |
| 6 | 20-30 | ~12m | ~3m | 4x |
| 7 | 30+ | ~15m+ | ~3.5m | 4.3x |

These are typical observed times, NOT guarantees.
