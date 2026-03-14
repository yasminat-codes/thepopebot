# Skills Architect

**Auto-design production-ready Claude Code skills with intelligent tiering, progressive disclosure, and quality gates.**

## What It Does

Skills Architect is a 5-round expert interview system that transforms simple skill concepts into production-grade Claude Code skills. It analyzes complexity, suggests best practices, and generates ready-to-deploy SKILL.md files with validation.

### 4 Operating Modes

| Mode | Use Case | Output |
|------|----------|--------|
| **CREATE** | New skill from scratch | Full SKILL.md + validation |
| **MIGRATE** | Upgrade existing skill to Tier 3+ | Migration plan + refactored SKILL.md |
| **AUDIT** | Health check existing skills | Report + improvement tasks |
| **SYSTEM** | Multi-skill ecosystem design | Architecture + dependency graph |

## Quick Start

```bash
# Interactive mode (guided interviews)
/skills-architect

# Create new skill
/skills-architect create my-deployment-tool

# Upgrade existing skill
/skills-architect migrate .claude/skills/old-skill

# Audit all skills in directory
/skills-architect audit .claude/skills/

# Design multi-skill system
/skills-architect system cold-email-pipeline
```

## Key Features

- **5-round expert interview** - Progressive questioning (scope → complexity → patterns → testing → performance)
- **7-tier auto-detection** - Classifies skills by complexity: 1=trivial to 7=distributed system
- **CSO descriptions** - 10-point scoring rubric ensures clarity and completeness
- **Proactive suggestions** - AI recommends enhancements across 8 categories (core, advanced, patterns, integrations, etc.)
- **9 SKILL.md templates** - Framework-specific (SDK, Pydantic AI, bash, etc.)
- **Progressive disclosure** - Reference docs loaded on-demand for specific patterns
- **Validation with auto-fix** - 5-point validation catches common mistakes automatically
- **Pressure test generation** - Creates edge case test suites for Tier 3+ skills
- **Dependency wiring** - Detects and connects related skills automatically
- **Dry-run preview** - Review generated skill before writing to disk
- **Memory tracking** - Logs all created skills for discovery and learning

## Architecture

```
skills-architect/
├── README.md                    # This file
├── CHANGELOG.md                 # Version history
├── SKILL.md                     # Skill implementation
├── hooks/
│   ├── skills-architect-pre.sh # Input validation
│   ├── skills-architect-post.sh # Output verification
│   └── dry-run-preview.sh       # Preview generation
├── templates/                   # 9 SKILL.md templates
│   ├── sdk-skill.template.md
│   ├── pydantic-ai-skill.template.md
│   ├── bash-wrapper.template.md
│   ├── research-skill.template.md
│   ├── validation-skill.template.md
│   ├── workflow-skill.template.md
│   ├── integration-skill.template.md
│   ├── multi-agent-skill.template.md
│   └── data-processing-skill.template.md
├── rubrics/
│   ├── cso-scoring-rubric.md   # 10-point CSO evaluation
│   ├── tier-detection.md       # 7-tier classification logic
│   └── validation-rules.md     # 5-point validation rules
└── references/
    ├── sdk-patterns/           # SDK-specific patterns
    ├── common-mistakes/        # Auto-fix templates
    ├── testing-patterns/       # Test framework patterns
    ├── performance-patterns/   # Optimization examples
    └── integration-patterns/   # Third-party integrations
```

## Interview Rounds

| Round | Focus | Questions | Output |
|-------|-------|-----------|--------|
| 1 | **Scope** | What, who, when, why | Skill definition, audience |
| 2 | **Complexity** | Dependencies, integrations, state | Initial tier estimate |
| 3 | **Patterns** | Testing, error handling, performance | Pattern requirements |
| 4 | **Quality** | Validation, hooks, monitoring | Quality gate definitions |
| 5 | **Integration** | Dependencies, handoffs, ecosystem | Skill wiring + recommendations |

## Tier System

| Tier | Name | Examples | Complexity | Line Count |
|------|------|----------|-----------|-----------|
| 1 | **Trivial** | Simple formatters, hello-world | Single function | <50 |
| 2 | **Basic** | Single API calls, file operations | Single service | 50-150 |
| 3 | **Standard** | Multi-step workflows, validation | 2-3 services | 150-400 |
| 4 | **Advanced** | Stateful processing, complex APIs | 4+ services | 400-800 |
| 5 | **Expert** | Multi-agent systems, optimization | Complex architecture | 800-1500 |
| 6 | **Enterprise** | Distributed systems, resilience | Advanced patterns | 1500-3000 |
| 7 | **Architectural** | Multi-service ecosystems | Full platform | 3000+ |

## Line Count Limits

```
Tier 1: <50 lines
Tier 2: 50-150 lines
Tier 3: 150-400 lines
Tier 4: 400-800 lines
Tier 5: 800-1500 lines
Tier 6: 1500-3000 lines
Tier 7: 3000+ lines
```

## Progressive Disclosure

Skills Architect uses a smart progressive disclosure system - reference documents and templates are loaded only when relevant to the skill being designed. For example, a Tier 3 skill that uses async I/O only loads async patterns; a Tier 5 multi-agent skill loads distributed system patterns. This keeps the context focused and prevents information overload.

## Version Information

- **Version:** 1.0.0
- **Author:** yasmine
- **Platform:** Claude Code
- **Minimum Claude Version:** 4.5
- **Status:** Production Ready
