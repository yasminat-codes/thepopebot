# Changelog

All notable changes to the Retell AI Voice Agent Creator skill.

## [v0.1.0] - 2026-02-24

### Added
- Parent orchestrator SKILL.md with 8-step chain flow
- 7 sub-skills: voice-selector, prompt-generator, pronunciation-fixer,
  humanization-engine, latency-optimizer, agent-config-builder, retell-api-wrapper
- 9 industry templates: sales, support, appointment, receptionist,
  personal-assistant, lead-qualifier, survey, debt-collection, real-estate
- Routing table with CHAIN, SINGLE, and PARALLEL execution modes
- Enterprise interview system (25 questions across 10 rounds)
- Pre-flight verification script (verify.sh)
- Full deployment script with retry logic (deploy.sh)
- Test call script with transcript retrieval (test-agent.sh)
- Reference documents: API quick reference, env vars, examples, interview
  questions, multi-account guide, orchestration logic, template catalog,
  troubleshooting, user intent map, voice provider comparison
- Internal vs client deployment support (multi-account)
- Template auto-detection from natural language
- Output folder structure with deployment receipts
