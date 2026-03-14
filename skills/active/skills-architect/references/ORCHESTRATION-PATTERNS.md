# Orchestration Patterns for Skills

## What Makes a Skill an Orchestrator

A skill is an orchestrator when it:
1. Dispatches subagents via the `Task` tool (never executes work itself)
2. Tracks progress across phases (reads/writes state files)
3. Enforces quality gates that BLOCK continuation on failure
4. Aggregates results from multiple agents into a coherent output
5. Manages dependencies between phases (what can run parallel vs sequential)

Non-orchestrators implement work directly. Orchestrators delegate everything and coordinate.

## Task Tool Usage

```javascript
// Basic subagent dispatch
Task({
  subagent_type: "general-purpose",  // or custom agent filename (no .yml)
  prompt: "Analyze the authentication module in src/auth/ and report all security issues.",
  description: "Auth security scan"   // Short label shown in UI
})

// With model selection
Task({
  subagent_type: "general-purpose",
  prompt: "...",
  description: "Deep analysis",
  model: "opus"                        // opus | sonnet | haiku
})

// Background (parallel) dispatch
Task({
  subagent_type: "general-purpose",
  prompt: "...",
  description: "Background worker",
  run_in_background: true              // Returns immediately, result delivered later
})

// With custom agent
Task({
  subagent_type: "security-auditor",   // Matches .claude/agents/security-auditor.yml
  prompt: "Audit the payments module.",
  description: "Payments security audit",
  model: "opus"
})
```

## Sequential vs Parallel Execution Rules

### Sequential: One Task Per Message

Use when the next phase depends on the previous phase's output.

```markdown
<!-- SKILL.md sequential pattern -->

Step 1: Read the spec file at specs/agents/my-agent.yaml.
Use Task tool with subagent_type "fast-researcher" to analyze the spec.
WAIT for the result before continuing.

Step 2: Based on the research output, use Task tool with subagent_type
"code-generator" to implement the agent.
WAIT for implementation to complete.

Step 3: Use Task tool with subagent_type "code-reviewer" to review
the implementation.
If review fails, STOP and report the failures. Do NOT continue.
```

### Parallel: ALL Independent Tasks in ONE Message

Use when phases do not depend on each other's output. Sending all Task calls in a single message triggers parallel execution.

```markdown
<!-- SKILL.md parallel pattern -->

Dispatch ALL of the following in a single response (parallel execution):

1. Task: subagent_type "fast-researcher", prompt "Analyze src/auth/"
2. Task: subagent_type "fast-researcher", prompt "Analyze src/payments/"
3. Task: subagent_type "fast-researcher", prompt "Analyze src/users/"

Send all three Task calls in ONE message. Wait for all three to complete
before proceeding to the implementation phase.
```

**Critical rule:** Never send sequential Tasks when they can be parallel. Never send parallel Tasks in separate messages - that forces sequential execution.

## The Triple Parallel Review Pattern

Three Opus reviewers run simultaneously, each with a different review lens. Used for high-stakes code before production deployment.

```markdown
<!-- In orchestrator SKILL.md, Review Phase -->

Dispatch THREE simultaneous code review agents in ONE message:

Task 1 - Security Reviewer:
  subagent_type: "general-purpose"
  model: "opus"
  prompt: |
    Review [IMPLEMENTATION_PATH] for security vulnerabilities only.
    Focus: injection, auth bypass, secrets exposure, input validation.
    Output: SECURITY_PASS or SECURITY_FAIL with findings.

Task 2 - Performance Reviewer:
  subagent_type: "general-purpose"
  model: "opus"
  prompt: |
    Review [IMPLEMENTATION_PATH] for performance issues only.
    Focus: N+1 queries, blocking I/O, memory leaks, inefficient algorithms.
    Output: PERF_PASS or PERF_FAIL with findings.

Task 3 - Architecture Reviewer:
  subagent_type: "general-purpose"
  model: "opus"
  prompt: |
    Review [IMPLEMENTATION_PATH] for architecture and pattern adherence.
    Focus: SOLID principles, project conventions, test coverage, coupling.
    Output: ARCH_PASS or ARCH_FAIL with findings.

GATE: ALL three must return PASS. Any single FAIL blocks deployment.
Aggregate all findings into a single review report.
```

## Quality Gate Implementation

Quality gates BLOCK, they do not WARN. If a gate fails, the orchestrator stops and surfaces the failure clearly.

```markdown
<!-- Gate pattern in SKILL.md -->

After receiving all review results, apply the quality gate:

QUALITY GATE CHECK:
- If any reviewer returned FAIL: Output "GATE FAILED" with all findings.
  Do NOT proceed to the next phase. Stop and wait for human resolution.
- If all reviewers returned PASS: Output "GATE PASSED" and continue.

This is not advisory. A single failure halts the entire workflow.
```

Gate categories by severity:
| Gate Type | On Failure |
|---|---|
| Test coverage < threshold | BLOCK - do not proceed |
| Security audit FAIL | BLOCK - do not proceed |
| Type checking errors | BLOCK - do not proceed |
| Linting errors | BLOCK - fix before proceeding |
| Code review WARN | LOG - proceed with note |
| Documentation missing | LOG - proceed, create task |

## Skill Chaining (Calling Skill Tool from Within a Skill)

Orchestrator skills can invoke other skills using the Skill tool. This composes specialized skills into a larger workflow.

```markdown
<!-- In orchestrator SKILL.md -->

Phase 2: Database Setup
Use the Skill tool to invoke "backend-database-architect".
Pass the spec file path as context.
Wait for the skill to complete before proceeding to Phase 3.

Phase 3: Agent Implementation
Use the Skill tool to invoke "sdk-agent-implementer".
The implementer skill will handle all agent code generation.

Phase 4: Security Review
Use the Skill tool to invoke "sdk-agent-security-reviewer".
If security review returns issues, halt and report.
```

Skill chaining rules:
- Each skill runs to completion before the next starts (sequential by default)
- Skills cannot be called in parallel via the Skill tool (use Task for parallel)
- Pass context between skills via files, not return values

## Distributed Task Queue Pattern for 10+ Workers

For large-scale parallel work (10+ independent units), use a queue file to coordinate.

```markdown
<!-- Distributed queue pattern -->

Phase 1: Build the work queue.
Write all work items to .claude/queue/pending.json as an array.
Each item: {id, type, input_path, output_path, status: "pending"}

Phase 2: Dispatch worker batch 1 (first 5 items).
Read items 1-5 from pending.json.
Dispatch ALL 5 as parallel Task calls in ONE message.
Each worker reads its item, processes it, writes result to output_path,
then updates its status to "complete" in pending.json.

Phase 3: After batch 1 completes, dispatch batch 2 (items 6-10).
Continue until all items are processed.

Phase 4: Aggregate all outputs from output_path locations.
Generate summary report.
```

Queue file format:
```json
[
  {"id": "1", "type": "analyze", "input": "src/auth.py", "output": ".claude/results/auth.json", "status": "pending"},
  {"id": "2", "type": "analyze", "input": "src/payments.py", "output": ".claude/results/payments.json", "status": "pending"}
]
```

## Approval Gate Pattern with AskUserQuestion

For irreversible actions, pause and require explicit human approval before proceeding.

```markdown
<!-- Approval gate pattern in SKILL.md -->

Before executing any deployment or destructive action:

1. Present a clear summary of what will happen:
   - Files that will be deleted/overwritten
   - Services that will restart
   - Database migrations that will run
   - Estimated downtime

2. Use AskUserQuestion with these exact options:
   - "Approve" - proceed with the action as described
   - "Modify" - I want to change something before proceeding
   - "Cancel" - abort the workflow entirely

3. Wait for the response:
   - Approve: proceed immediately
   - Modify: ask what to change, update the plan, present again
   - Cancel: output "WORKFLOW CANCELLED by user" and stop all work

NEVER skip this gate for: production deployments, database migrations,
file deletions, secret rotations, or any action that cannot be undone.
```

## Memory-Aware Orchestration

Large workflows that span multiple sessions need persistent state.

```markdown
<!-- State file pattern in SKILL.md -->

At the start of each run:
1. Check if .claude/workflow-state.json exists.
2. If it exists, read it and resume from the last completed phase.
3. If it does not exist, start from Phase 1 and create the state file.

State file structure:
{
  "workflow_id": "unique-id",
  "started_at": "ISO timestamp",
  "last_updated": "ISO timestamp",
  "current_phase": 3,
  "completed_phases": [1, 2],
  "failed_phases": [],
  "phase_outputs": {
    "1": {"status": "complete", "result_path": ".claude/outputs/phase1.json"},
    "2": {"status": "complete", "result_path": ".claude/outputs/phase2.json"}
  }
}

After each phase completes: update the state file immediately.
If a phase fails: mark it in failed_phases, write error details, stop.
```

## Navigation Hub Pattern

The top-level `SKILL.md` is a navigation hub only. It dispatches, never executes.

```markdown
<!-- Navigation hub SKILL.md structure -->

# my-orchestrator

## What This Skill Does
[One paragraph description]

## Phase Map
Phase 1: Research      → fast-researcher agents (parallel)
Phase 2: Planning      → Skill tool: planning-generator
Phase 3: Implement     → code-generator agents (parallel per module)
Phase 4: Review        → Triple parallel review pattern (Opus)
Phase 5: Security      → Skill tool: security-auditor
Phase 6: Deploy        → Approval gate → deploy agents

## Execution Rules
- This skill NEVER writes code directly
- This skill NEVER reads implementation files directly
- This skill ONLY dispatches agents and skills, then aggregates results
- Every phase transition requires explicit completion verification

## Start Here
Check for existing .claude/workflow-state.json.
If found: resume from last phase.
If not found: begin Phase 1.
```

## Phase Dependency Analysis for Parallel Batching

Before designing the orchestration flow, map phase dependencies:

```
Independent (can ALL run in parallel):
  Research A, Research B, Research C

Fan-in (wait for all research):
  Planning (depends on: Research A + B + C)

Fan-out (planning done, these are independent):
  Implement Module X, Implement Module Y, Implement Module Z

Fan-in again:
  Integration test (depends on: Module X + Y + Z)

Sequential chain:
  Security review -> Approval gate -> Deploy
```

Draw the dependency graph first. Any node with no incoming edges from unresolved nodes can run in parallel with its siblings.

## Complete Orchestrator Example (10-Phase with Quality Gates)

```markdown
# sdk-agent-full-builder
Full 10-phase orchestrator: requirements through deployment.

## Phase 1: Requirements Research (PARALLEL)
Dispatch 3 fast-researcher agents simultaneously:
- Agent 1: Analyze existing codebase patterns
- Agent 2: Read all spec files in specs/agents/
- Agent 3: Check .claude/context/ files for conventions
All 3 in ONE message. Wait for all.

## Phase 2: Architecture Design (SEQUENTIAL)
Use Skill tool: "sdk-agent-architecture-designer"
Input: Phase 1 research outputs
GATE: Architecture must include agent diagram and tool list.

## Phase 3: Database Schema (SEQUENTIAL, if needed)
Use Skill tool: "backend-database-architect"
Input: Architecture from Phase 2
GATE: Schema must have migration files.

## Phase 4: Implementation (PARALLEL)
Dispatch code-generator agents, one per module (all in ONE message):
- Core agent class
- Tools module
- API layer
- Tests module
Wait for all. GATE: All must return IMPLEMENTATION COMPLETE.

## Phase 5: Test Validation (SEQUENTIAL)
Use Skill tool: "sdk-agent-tester-validator"
Run full test suite. GATE: Coverage >90% tools, >85% agents.
BLOCK if below threshold.

## Phase 6: Triple Parallel Review (PARALLEL)
Dispatch 3 Opus reviewers in ONE message:
- Security reviewer
- Performance reviewer
- Architecture reviewer
GATE: ALL three must return PASS.

## Phase 7: Security Audit (SEQUENTIAL)
Use Skill tool: "sdk-agent-security-reviewer"
GATE: Zero CRITICAL findings. Zero HIGH findings.

## Phase 8: Documentation (PARALLEL)
Dispatch 2 agents in ONE message:
- API documentation generator
- README generator
Wait for both.

## Phase 9: Approval Gate
Present deployment summary to user.
AskUserQuestion: Approve / Modify / Cancel
Wait for explicit approval before Phase 10.

## Phase 10: Deployment (SEQUENTIAL)
Use Skill tool: "sdk-agent-infrastructure-builder"
Write final state to .claude/workflow-state.json as COMPLETE.
Output: WORKFLOW COMPLETE with all artifact paths.
```
