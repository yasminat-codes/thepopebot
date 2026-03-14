# Changelog

All notable changes to skills-architect will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-28

### Added
- **Phase 0 — Docs Loading**: Reads local `docs/claude-skills/` (12 files in priority order) for latest skill specification before creating any skill
- **Phase 0 — Live Spec Fetch**: WebFetch of Anthropic's live skill and hooks documentation to catch spec changes
- **Phase 8 — Agent Team Deployment**: Fan-out parallel file generation using 2/4/6 agents by tier (up to 4.3x speedup)
- **Phase 9 — Post-Creation Self-Audit**: Automatic 100-point health scoring after creation (line count 20 + CSO 30 + frontmatter 20 + disclosure 20 + orphans 10)
- **Phase 8 — Interactive Preview**: File-by-file approval gate for Tier 5+ skills before final write

### New Reference Files
- `references/AGENT-TEAM-DEPLOYMENT.md` — Fan-out parallel agent coordination, team configs, prompt templates, performance benchmarks
- `references/SKILLS-SPECIFICATION-RESEARCH.md` — Docs loading procedure, WebFetch URLs, conflict resolution, error handling

### Changed
- Phase 0 expanded from 2 steps to 4 steps (added docs reading + web-fetch)
- Phase 8 rewritten with parallel agent deployment pattern (replaces sequential file writing)
- Phase 9 enhanced with automatic self-audit (replaces manual-only validation)

---

## [1.0.0] - 2026-02-28

### Added
- Initial release of skills-architect
- **4 operating modes:** CREATE, MIGRATE, AUDIT, SYSTEM
- **5-round expert interview system** with 100+ question bank covering scope, complexity, patterns, quality, and integration
- **7-tier auto-detection algorithm** for skill classification (Tier 1: Trivial to Tier 7: Architectural)
- **CSO description engine** with 10-point scoring rubric for clarity and completeness
- **5-point validation system** with intelligent auto-fix for common mistakes
- **9 SKILL.md templates** for different skill types (SDK, Pydantic AI, bash, research, validation, workflow, integration, multi-agent, data processing)
- **19 reference files** for progressive disclosure (patterns, templates, rubrics, common mistakes)
- **3 validation hooks** (pre-validation, post-validation, dry-run preview)
- **Proactive expert suggestion engine** across 8 enhancement categories (core, advanced, patterns, integrations, testing, performance, monitoring, scaling)
- **Pressure test generation** for Tier 3+ skills with edge case coverage
- **Memory integration** with creation logging for skill discovery and learning
- **Dry-run preview support** to review generated skills before writing to disk
- **Skill dependency detection** and automatic wiring for multi-skill systems
- **Live documentation fetching** for framework-specific skills (SDK, Pydantic AI, etc.)
- **Full semantic versioning** with automated version calculation and CHANGELOG generation

### Technical Details
- Python-based implementation with asyncio support
- Comprehensive error handling with actionable error messages
- Support for both interactive and command-line modes
- Automated SKILL.md generation with proper formatting
- Integration with Claude Code's skill ecosystem
- Token-efficient interview progression (40-60 tokens per round)

---

For information about versions prior to 1.0.0, see the development history.
