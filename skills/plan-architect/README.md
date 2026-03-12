# Plan Architect

> Intelligent systems architect that takes your ideas from 3/10 to 10/10.

## What It Does

Plan-architect creates comprehensive, actionable implementation plans by:

1. **Understanding your codebase** — scans project structure, patterns, and integrations
2. **Expert interview** — probes with intelligent questions, fills gaps from expertise
3. **Parallel research** — dispatches 3 agents (codebase, web, MCP) simultaneously
4. **Synthesis** — connects dots, detects anti-patterns, scores complexity
5. **Battle-tested plans** — includes resilience, fallbacks, success criteria, grep patterns

## Usage

```bash
/plan-architect build a webhook processing system for Stripe events
/plan-architect automate niche research and content generation
/plan-architect design a real-time dashboard for pipeline status
```

## Output

Plans are written to `plans/` directory:
```
plans/
├── webhook-processing-stripe.md
├── niche-research-automation.md
└── archive/
    └── webhook-processing-stripe-v1.md
```

## Pipeline

```
/plan-architect → /extract-tasks → /specs-to-commit → implementation
```

## Features

- **Expert interview engine** — domain-specific questions with gap-filling
- **Parallel research agents** — 3 agents search simultaneously
- **Anti-pattern detection** — catches common planning mistakes
- **Complexity scoring** — 1-5 per section for effort estimation
- **Plan versioning** — diffs and archives when updating existing plans
- **Grep enforcement** — ensures codebase patterns are searched before planning
- **Context loading suggestions** — tells implementers which files to read first

## Configuration

- **Model:** Opus (forced for expert-level planning)
- **Tier:** 5 (Very Advanced)
- **Context:** Inline (uses conversation context)
- **Hooks:** None

## Author

yasmine — v1.0.0
