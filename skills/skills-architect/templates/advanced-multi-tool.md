---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
version: {{VERSION}}
author: {{AUTHOR}}
category: {{CATEGORY}}
allowed-tools: {{TOOLS}} WebSearch WebFetch Bash Read Glob Grep
context: fork
model: claude-opus-4-5
---

# {{SKILL_NAME}}

{{DESCRIPTION}}

## Overview

This is a Tier 4 skill that runs parallel research across multiple sources, synthesizes
findings, and produces a comprehensive report with concrete recommendations. It uses 5+ tools
and forks a context for deep analysis without polluting the main conversation.

**Model:** claude-opus-4-5 (deep reasoning required)
**Context:** Forked (isolated from main conversation)
**Typical runtime:** 5-15 minutes
**Tools used:** {{TOOLS}} WebSearch WebFetch Bash Read Glob Grep

---

## When to Invoke

Use this skill when:
- A decision requires research across multiple dimensions
- The answer will significantly affect architecture or tooling choices
- You need an evidence-based recommendation, not just an opinion
- Multiple stakeholders need to see a reasoned, citable analysis

Do NOT use this skill for:
- Simple one-question lookups (use mid-tool template)
- Decisions already made (use verification instead)
- Time-critical operations where 5-15 min is too long

---

## Phase 1: Problem Scoping

{{PHASES}}

Before any research, lock in the exact problem to solve. Vague questions produce vague answers.

**Scoping questions to answer internally:**
1. What is the specific decision being made?
2. What are the constraints (budget, team skill, existing stack, timeline)?
3. What does "success" look like for this recommendation?
4. What are the non-negotiables that would eliminate a candidate?

**Output of this phase:** A crisp one-paragraph problem statement that guides all subsequent
research. If the user's request is ambiguous, ask one clarifying question before proceeding.

---

## Phase 2: Parallel Research Dispatch

Dispatch all research tracks simultaneously. Do not wait for one to complete before starting
the next.

### Track A: Current State Research

```
WebSearch: "{{SKILL_NAME}} best practices 2026"
WebSearch: "{{CATEGORY}} comparison 2026"
WebFetch: [official documentation URLs]
```

Parse results for:
- Current recommended approaches
- Known pitfalls and anti-patterns
- Community consensus and controversy points
- Version / release recency

### Track B: Codebase Analysis

```
Glob: "**/*.{json,toml,yaml,lock}" — dependency manifests
Glob: "**/*.{ts,tsx,js,py,go,rs}" — source files (sample)
Grep: pattern for existing usage of related tools
Read: key configuration files
```

Parse results for:
- What is already in use
- What would conflict with a new addition
- Existing patterns to follow or replace
- Current version constraints

### Track C: Competitive Landscape

```
WebSearch: "[option A] vs [option B] vs [option C] 2026"
WebFetch: [comparison articles, benchmarks]
```

Parse results for:
- Head-to-head comparisons
- Benchmark data (performance, bundle size, etc.)
- Migration cost from current solution
- Ecosystem health (downloads, GitHub stars, issues)

### Track D: Risk Assessment

```
WebSearch: "{{SKILL_NAME}} security vulnerabilities 2026"
WebSearch: "{{SKILL_NAME}} production issues migration problems"
```

Parse results for:
- Known CVEs or security concerns
- Breaking change history
- Community-reported production incidents
- Maintenance / abandonment signals

---

## Phase 3: Synthesis

Consolidate all research tracks into a structured findings matrix.

### Findings Matrix

| Dimension | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| Maturity | | | |
| Performance | | | |
| DX Score | | | |
| Security | | | |
| Migration Cost | | | |
| Ecosystem | | | |
| Fit to Constraints | | | |
| **Overall Score** | | | |

**Scoring:** 1-5 scale where 5 = best. Weight by constraint priority.

### Conflict Detection

Before recommending, check for conflicts:
- Does this conflict with anything already in the codebase?
- Does this require a version bump that breaks other dependencies?
- Does this overlap with an existing tool (redundancy)?

---

## Phase 4: Recommendation

{{QUALITY_GATES}}

Structure the recommendation as:

```markdown
## Recommendation: [CHOSEN OPTION]

**Confidence:** High / Medium / Low
**Rationale:** [2-3 sentences summarizing why this wins]

### Why Not [Option B]
[1-2 sentences on the deciding factor]

### Why Not [Option C]
[1-2 sentences on the deciding factor]

### Trade-offs Accepted
- [Trade-off 1]: [Mitigation]
- [Trade-off 2]: [Mitigation]

### Implementation Path
1. [First concrete step]
2. [Second concrete step]
3. [Validation step]

### Success Metrics
- [Measurable outcome 1]
- [Measurable outcome 2]
```

**Quality gates before presenting:**
- [ ] All research tracks completed (no skipped tracks)
- [ ] At least 3 sources cited per major claim
- [ ] Conflicts with existing codebase checked
- [ ] A clear winner identified (not "it depends" without follow-up)
- [ ] Implementation path is actionable (not abstract)

---

## Phase 5: Evidence Appendix

{{REFERENCES}}

Include a structured list of all sources consulted:

```markdown
## Sources

### Official Documentation
- [Tool Name Docs](url) — accessed [date]

### Comparisons & Benchmarks
- [Article Title](url) — key finding: X

### Community Signals
- [Forum/Issue/Discussion](url) — sentiment: positive/negative

### Security
- [CVE or Advisory](url) — status: patched/open
```

Do not include sources that were not actually consulted. Do not fabricate citations.

---

## References Directory

The `references/` directory contains pre-loaded reference material for common domains:

```
.claude/skills/{{SKILL_NAME}}/
├── SKILL.md
└── references/
    ├── known-patterns.md       # Established patterns in this domain
    ├── anti-patterns.md        # Things to avoid and why
    ├── version-matrix.md       # Compatibility table for common versions
    └── benchmark-data.md       # Cached benchmark comparisons
```

When `references/` files exist, read them first before web research. They may already
contain the answer and save significant time.

---

## Failure Modes

| Failure | Detection | Recovery |
|---------|-----------|---------|
| Web search returns no results | Empty result set | Use alternative search terms, fall back to knowledge |
| Conflicting sources | Contradictory data | Cite the conflict, weight by source authority |
| No clear winner | All options score similarly | Present trade-off framework for user to decide |
| Codebase unreadable | Glob/Grep timeout | Sample top-level files only |
| Research timeout | Phase 2 exceeds 5 min | Complete available tracks, note what was skipped |

---

*Tier 4 skill — parallel research, forked context, deep synthesis. For orchestrating other
skills, see orchestrator template.*
