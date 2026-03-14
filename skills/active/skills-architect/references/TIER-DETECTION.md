# Tier Detection Algorithm

Auto-detection system for determining skill tier from interview answers.

---

## Detection Matrix

Map interview signals directly to tier indicators.

| Signal | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Tier 5 | Tier 6 | Tier 7 |
|---|---|---|---|---|---|---|---|
| Tool count | 0 | 2-3 | 3-5 | 5-7 | 6-9 | 8-12 | N/A (multi-skill) |
| Phase count | 0-1 | 2-3 | 3-5 | 4-6 | 5-8 | 7-12 | N/A |
| Parallel research | No | No | Maybe | Yes | Yes | Yes | Yes |
| Hooks needed | No | No | Maybe | Maybe | Yes | Yes | Yes |
| Agents needed | No | No | No | No | Yes | Yes | Yes |
| Reference files | 0 | 0-1 | 1-2 | 3-5 | 5-10 | 10-15 | Per sub-skill |
| External scripts | No | No | No | Maybe | Yes | Yes | Yes |
| Orchestration | No | No | No | No | No | Yes | Yes |
| Multi-skill pipeline | No | No | No | No | No | No | Yes |
| Output complexity | Simple | Linear | Structured | Multi-part | Rich | Enterprise | System |

---

## Scoring Formula

Assign points to each signal, sum the total, and map to a tier.

### Point Assignments

```
Tool Count
  0 tools           = 0 pts
  1 tool            = 1 pt
  2-3 tools         = 2 pts
  4-5 tools         = 4 pts
  6-7 tools         = 6 pts
  8-10 tools        = 8 pts
  11+ tools         = 10 pts

Phase Count
  0-1 phases        = 0 pts
  2-3 phases        = 2 pts
  4-5 phases        = 4 pts
  6-8 phases        = 6 pts
  9+ phases         = 8 pts

Parallelism
  None              = 0 pts
  Some (2-3)        = 3 pts
  Heavy (4+)        = 5 pts

Hooks Required
  None              = 0 pts
  1-2 hooks         = 2 pts
  3+ hooks          = 4 pts

Agent Delegation
  No agents         = 0 pts
  1 agent           = 5 pts
  2-3 agents        = 8 pts
  4+ agents         = 12 pts

Reference Files
  0 references      = 0 pts
  1-2 references    = 1 pt
  3-5 references    = 3 pts
  6-10 references   = 6 pts
  11-15 references  = 10 pts

External Scripts
  None              = 0 pts
  1-2 scripts       = 3 pts
  3+ scripts        = 6 pts

Multi-Skill Pipeline
  No                = 0 pts
  Yes               = 15 pts (forces Tier 7)
```

### Score-to-Tier Mapping

```
Score  0 -  4   →  Tier 1 (Simple Knowledge)
Score  5 - 10   →  Tier 2 (Basic Workflow)
Score 11 - 18   →  Tier 3 (Intermediate)
Score 19 - 28   →  Tier 4 (Advanced)
Score 29 - 40   →  Tier 5 (Very Advanced)
Score 41 - 55   →  Tier 6 (Ultra-Advanced Orchestrator)
Score 56+        →  Tier 7 (Skill System)
Multi-skill flag →  Tier 7 (override, always)
```

---

## Signal Weights and Thresholds

Some signals are hard gates that override scoring.

### Hard Gates (Override Everything)

```
IF multi-skill pipeline = Yes          → FORCE Tier 7
IF agent count >= 4                    → MINIMUM Tier 6
IF reference count >= 11               → MINIMUM Tier 6
IF tool count >= 11                    → MINIMUM Tier 6
IF phase count >= 9                    → MINIMUM Tier 5
IF agent count >= 1 AND tools >= 6    → MINIMUM Tier 5
```

### Soft Gates (Influence Score)

```
IF parallel research = Yes             → +3 to score
IF hooks required = Yes                → +2 to score
IF output is multi-file                → +2 to score
IF user requests CI/CD integration    → +3 to score
IF skill needs to call other skills   → +5 to score
```

---

## Worked Examples

### Example 1: Static Reference Skill

User says: "I just need a file that documents the naming conventions for our project. No tools, no logic."

```
Tool count:     0         = 0 pts
Phase count:    0         = 0 pts
Parallelism:    None      = 0 pts
Hooks:          None      = 0 pts
Agents:         None      = 0 pts
References:     0         = 0 pts
Scripts:        None      = 0 pts
Multi-skill:    No        = 0 pts

Total: 0 pts → Tier 1
```

**Result:** Tier 1 (Simple Knowledge)

---

### Example 2: Simple File Generator

User says: "I want a skill that reads a template file and writes a new file using Bash. Two steps."

```
Tool count:     2 (Read, Bash)  = 2 pts
Phase count:    2               = 2 pts
Parallelism:    None            = 0 pts
Hooks:          None            = 0 pts
Agents:         None            = 0 pts
References:     1               = 1 pt
Scripts:        None            = 0 pts
Multi-skill:    No              = 0 pts

Total: 5 pts → Tier 2
```

**Result:** Tier 2 (Basic Workflow)

---

### Example 3: 5 Tools + 3 Phases + No Agents

User says: "I need to fetch data from an API, parse it, run some checks, write a report, and send a Slack message. Three phases, no agents."

```
Tool count:     5 (Fetch, parse, check, write, Slack)  = 4 pts
Phase count:    3                                        = 2 pts
Parallelism:    None                                     = 0 pts
Hooks:          None                                     = 0 pts
Agents:         None                                     = 0 pts
References:     2                                        = 1 pt
Scripts:        None                                     = 0 pts
Multi-skill:    No                                       = 0 pts

Total: 7 pts → Tier 2
```

Wait — 5 tools suggests Tier 3-4. Apply soft gate: tool count 4-5 = 4 pts (not 2).

```
Recalculated tool count:  5 tools = 4 pts
Phase count:              3       = 2 pts
References:               2       = 1 pt

Total: 7 pts → Tier 2

Apply check: 5 tools with 3 phases... meets Tier 3 threshold.
Soft bump: output is multi-part (report + Slack) = +2

Total: 9 pts → Tier 2 (still, borderline Tier 3)
```

**Result:** Tier 3 — use tool count hard check: 4-5 tools with references = floor Tier 3.

**Presenter says:** "This lands at Tier 3 — Intermediate. You have 5 tools and structured output across 3 phases, which pushes past basic workflow."

---

### Example 4: Advanced with Parallel Research

User says: "I need 6 tools, 5 phases, parallel web research in phase 2, and I'll need 4 reference files."

```
Tool count:     6-7      = 6 pts
Phase count:    5        = 4 pts
Parallelism:    Some     = 3 pts
Hooks:          None     = 0 pts
Agents:         None     = 0 pts
References:     4        = 3 pts
Scripts:        None     = 0 pts
Multi-skill:    No       = 0 pts

Total: 16 pts → Tier 3

Soft bump: parallel research = +3
Total: 19 pts → Tier 4
```

**Result:** Tier 4 (Advanced)

---

### Example 5: Agent + Scripts

User says: "I need an orchestrator that spawns a sub-agent to handle the data processing, plus a shell script for cleanup."

```
Tool count:     7        = 6 pts
Phase count:    6        = 6 pts
Parallelism:    Heavy    = 5 pts
Hooks:          2        = 2 pts
Agents:         1        = 5 pts
References:     6        = 6 pts
Scripts:        1        = 3 pts
Multi-skill:    No       = 0 pts

Total: 33 pts → Tier 5
Hard gate: agent >= 1 AND tools >= 6 → minimum Tier 5 confirmed
```

**Result:** Tier 5 (Very Advanced)

---

### Example 6: Full Orchestrator

User says: "I need 10 tools, 3 agents, 12 reference files, hooks for validation, and it needs to orchestrate a full pipeline."

```
Tool count:     10+      = 8 pts
Phase count:    9        = 8 pts
Parallelism:    Heavy    = 5 pts
Hooks:          3+       = 4 pts
Agents:         3        = 8 pts
References:     12       = 10 pts
Scripts:        3+       = 6 pts
Multi-skill:    No       = 0 pts

Total: 49 pts → Tier 6
Hard gates: agent >= 4? No (3 agents). reference >= 11? Yes → minimum Tier 6 confirmed.
```

**Result:** Tier 6 (Ultra-Advanced Orchestrator)

---

### Example 7: Multi-Skill System

User says: "Actually this should be three separate skills that call each other — a planner, an executor, and a validator."

```
Multi-skill flag: Yes → FORCE Tier 7 regardless of score
```

**Result:** Tier 7 (Skill System)

---

## Override Rules

Users may request a tier override. These are valid but require justification.

### Bumping Up (User wants higher tier than detected)

Acceptable reasons:
- "I know this will grow significantly"
- "I want room for future phases"
- "I want to include agent support even if not used yet"

Action: Accept the bump. Document it. Note the detected tier vs chosen tier in the SKILL.md frontmatter.

### Bumping Down (User wants lower tier than detected)

Acceptable reasons:
- "Keep it simple, I'll refactor later"
- "This is a prototype, not production"
- "I don't need all those features right now"

Action: Accept the bump with a warning. Note features that will be unavailable at the lower tier.

### Override Documentation

Add to SKILL.md frontmatter:
```yaml
tier: 4
tier_detected: 3
tier_override_reason: "User requested room for future agent expansion"
```

---

## Presentation Template

Use this exact format when presenting the detected tier to the user.

```
Based on your answers, this is a Tier N skill because:

- You need X tools (signals: ...)
- You described Y phases (signals: ...)
- [Any other key signals that drove the tier]

Tier N skills typically run [line-count range] lines and include:
  - [Feature 1]
  - [Feature 2]
  - [Feature 3]

Folder structure for Tier N:
  [Show the abbreviated tree from TIER-STRUCTURES.md]

Does this match your expectations, or would you like to adjust the tier?
```

### Example Presentation (Tier 4)

```
Based on your answers, this is a Tier 4 skill because:

- You need 6 tools across 5 phases
- You described parallel research in phase 2
- You referenced 4 external reference files

Tier 4 skills typically run 200-400 lines and include:
  - Multi-phase execution with parallel tool calls
  - 3-5 reference files for domain knowledge
  - Structured, multi-part output
  - Optional hook integration

Folder structure for Tier 4:
  my-skill/
  ├── SKILL.md          (~250-350 lines)
  ├── references/
  │   ├── REF-1.md
  │   ├── REF-2.md
  │   ├── REF-3.md
  │   └── REF-4.md
  └── tests/
      └── test-cases.md

Does this match your expectations, or would you like to adjust the tier?
```

---

## Tier Summary Reference

| Tier | Name | Tools | Phases | Lines | Key Marker |
|---|---|---|---|---|---|
| 1 | Simple Knowledge | 0 | 0-1 | 50-150 | Pure reference, no execution |
| 2 | Basic Workflow | 2-3 | 2-3 | 100-200 | Linear, no branching |
| 3 | Intermediate | 3-5 | 3-5 | 150-300 | 1-2 references, some logic |
| 4 | Advanced | 5-7 | 4-6 | 200-400 | Parallel research, 3-5 refs |
| 5 | Very Advanced | 6-9 | 5-8 | 300-500 | Agents, scripts, 5-10 refs |
| 6 | Ultra-Advanced | 8-12 | 7-12 | 400-600 | Orchestration, 10-15 refs |
| 7 | Skill System | N/A | N/A | N/A | Multi-skill pipeline |
