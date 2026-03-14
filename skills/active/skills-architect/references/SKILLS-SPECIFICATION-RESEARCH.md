# Skills Specification Research — Docs Loading & Live Fetch

> Load the latest skill specification from local docs AND live Anthropic documentation.
> This ensures skills-architect NEVER creates skills based on stale patterns.

## Why This Matters

- Claude Code skill specification evolves regularly
- New frontmatter fields, hook events, and tool capabilities are added
- Skills created with outdated knowledge will fail validation or underperform
- Local docs may be more detailed; live docs may be more current
- Both sources together give the most complete picture

## Phase 0 — Step 3: Load Local Docs

### Location Detection

Check for skills documentation in order:
1. `docs/claude-skills/` in current project (preferred — curated by project owner)
2. `.claude/docs/skills/` in current project (alternative location)
3. Skip if neither exists (rely on web-fetch + training knowledge)

### Files to Read (Priority Order)

Read these files if they exist in the docs directory:

| Priority | File | What to Extract |
|----------|------|----------------|
| 1 | `01-frontmatter-complete.md` | All frontmatter fields, types, defaults, validation rules |
| 2 | `02-description-engineering.md` | CSO formula, 10-point rubric, trigger patterns |
| 3 | `07-folder-structure.md` | Tier structures, line limits, naming conventions |
| 4 | `03-tools-and-permissions.md` | Available tools, scoped Bash, MCP patterns |
| 5 | `08-orchestrator-skills.md` | Task tool patterns, parallel dispatch, quality gates |
| 6 | `05-hooks-system.md` | All 14 hook events, 4 hook types, matcher syntax |
| 7 | `00-overview.md` | High-level architecture, skill components |
| 8 | `09-advanced-patterns.md` | Composition, circuits, memory, idempotency |
| 9 | `04-arguments-and-context.md` | $ARGUMENTS, dynamic injection, context fork |
| 10 | `06-scripts-and-cli.md` | Script safety, validation gates, distribution |
| 11 | `10-skill-tiers-examples.md` | Complete tier examples |
| 12 | `SKILL-CREATION-CHECKLIST.md` | 12-phase creation checklist |

### What to Extract

For each file, extract and store:
- **New fields** not in skills-architect's existing references
- **Changed defaults** or rules that differ from current knowledge
- **New patterns** or anti-patterns discovered
- **Updated line limits** or tier definitions

### Conflict Resolution

If local docs conflict with skills-architect's built-in references:
- Local docs WIN for project-specific conventions
- Built-in references WIN for universal best practices
- Note conflicts for user review in Phase 7 (Expert Suggestions)

## Phase 0 — Step 4: Web-Fetch Live Anthropic Docs

### URLs to Fetch

```javascript
// Primary — Claude Code skills specification
WebFetch({
  url: "https://docs.anthropic.com/en/docs/claude-code/skills",
  prompt: "Extract: all frontmatter fields with types and defaults, line count limits, folder structure rules, progressive disclosure requirements, any new features or fields not commonly known"
})

// Secondary — Claude Code hooks system
WebFetch({
  url: "https://docs.anthropic.com/en/docs/claude-code/hooks",
  prompt: "Extract: all hook event names, hook types (command/remote/prompt/agent), matcher syntax, blockOnFailure behavior, environment variables available to hooks, any new events or features"
})
```

### When to Fetch

| Condition | Fetch? |
|-----------|--------|
| Creating a skill with hooks | Always fetch hooks docs |
| Creating Tier 4+ skill | Always fetch both URLs |
| Creating Tier 1-3 skill | Fetch skills doc only |
| MIGRATE mode | Fetch both (need latest spec to audit against) |
| AUDIT mode | Fetch both (need latest spec for scoring) |
| Local docs are comprehensive | Skip web-fetch (local is sufficient) |
| Network unavailable | Skip gracefully, use local + built-in knowledge |

### Error Handling

```
If WebFetch fails:
  1. Log: "Live docs unavailable — using local docs + built-in knowledge"
  2. Continue without live data
  3. Note in delivery report: "Created without live spec verification"

If WebFetch returns unexpected format:
  1. Extract whatever is parseable
  2. Fall back to built-in references for missing sections
```

### What to Look For in Live Docs

- **New frontmatter fields** added since skills-architect was last updated
- **Changed field names** or deprecated fields
- **New hook events** beyond the 14 currently known
- **New tool names** or tool capability changes
- **Updated line limits** or tier definitions
- **New agent types** beyond general-purpose, Explore, Plan
- **Breaking changes** that would invalidate existing skills

### Storing Findings

Store all findings as internal context with tags:

```
[FROM: local-docs] New field: "max-context-tokens" — limits context window usage
[FROM: web-fetch] Hook event "PreModelCall" — new event for intercepting model calls
[FROM: web-fetch] Tool "CodeAnalysis" — new built-in tool for static analysis
[CONFLICT] Line limit: local says 500, web says 600 for Tier 5 — using local (stricter)
```

These findings feed into:
- Phase 6: Frontmatter auto-decision (apply new fields)
- Phase 7: Expert suggestions (recommend new features)
- Phase 8: File generation (use latest patterns)
- Phase 9: Validation (score against current spec)

## Keeping Skills-Architect Updated

After each run, if significant new findings were discovered:

1. Note in delivery report: "Discovered N new spec changes"
2. Suggest updating skills-architect's own references
3. Save findings to memory for future runs:
   ```
   ## skills-architect spec-updates
   - [date]: Discovered new field "max-context-tokens" from live docs
   - [date]: Hook event "PreModelCall" now available
   ```
