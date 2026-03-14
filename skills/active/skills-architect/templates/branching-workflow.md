---
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
version: {{VERSION}}
author: {{AUTHOR}}
category: {{CATEGORY}}
allowed-tools: {{TOOLS}} Bash Glob Grep Read
---

# {{SKILL_NAME}}

{{DESCRIPTION}}

## Overview

This skill detects the current language, framework, or platform and branches into the
correct implementation path. All branches converge to the same output contract, so callers
always receive a consistent result regardless of which path was taken.

**Detection strategy:** File signatures, config files, dependency manifests
**Supported platforms:** [LIST SUPPORTED PLATFORMS HERE]
**Fallback:** Generic/universal path when no platform is detected

---

## Detection Engine

Run all detection checks in parallel. The first match wins. Detection is non-destructive —
no files are modified during this phase.

### Detect: Language

```bash
# Python
[ -f "pyproject.toml" ] || [ -f "requirements.txt" ] || [ -f "setup.py" ] && echo "python"

# Node.js / TypeScript
[ -f "package.json" ] && echo "node"

# Go
[ -f "go.mod" ] && echo "go"

# Rust
[ -f "Cargo.toml" ] && echo "rust"

# Ruby
[ -f "Gemfile" ] && echo "ruby"

# Java / Kotlin
[ -f "pom.xml" ] || [ -f "build.gradle" ] && echo "jvm"
```

### Detect: Framework (Node.js subtree)

```bash
# Check package.json for framework signatures
PACKAGE_JSON=$(cat package.json 2>/dev/null || echo "{}")

echo "$PACKAGE_JSON" | grep -q '"next"' && echo "nextjs"
echo "$PACKAGE_JSON" | grep -q '"nuxt"' && echo "nuxtjs"
echo "$PACKAGE_JSON" | grep -q '"@sveltejs/kit"' && echo "sveltekit"
echo "$PACKAGE_JSON" | grep -q '"astro"' && echo "astro"
echo "$PACKAGE_JSON" | grep -q '"remix"' && echo "remix"
echo "$PACKAGE_JSON" | grep -q '"vite"' && ! echo "$PACKAGE_JSON" | grep -q '"next"' && echo "vite-spa"
```

### Detect: Framework (Python subtree)

```bash
PYPROJECT=$(cat pyproject.toml 2>/dev/null || echo "")
REQUIREMENTS=$(cat requirements.txt 2>/dev/null || echo "")
COMBINED="$PYPROJECT $REQUIREMENTS"

echo "$COMBINED" | grep -qi "fastapi" && echo "fastapi"
echo "$COMBINED" | grep -qi "django" && echo "django"
echo "$COMBINED" | grep -qi "flask" && echo "flask"
echo "$COMBINED" | grep -qi "starlette" && ! echo "$COMBINED" | grep -qi "fastapi" && echo "starlette"
```

### Detect: Deploy Target

```bash
[ -f "Dockerfile" ] && echo "docker"
[ -f ".railway.json" ] || [ -f "railway.toml" ] && echo "railway"
[ -f "vercel.json" ] && echo "vercel"
[ -f "netlify.toml" ] && echo "netlify"
[ -f ".coolify" ] || [ -f "docker-compose.coolify.yml" ] && echo "coolify"
[ -f ".github/workflows/" ] && echo "github-actions"
```

---

## Detection Result

After running detection, construct the platform signature:

```
LANGUAGE:   python | node | go | rust | ruby | jvm | unknown
FRAMEWORK:  fastapi | django | nextjs | nuxtjs | sveltekit | astro | remix | none
DEPLOY:     docker | railway | vercel | netlify | coolify | github-actions | none
```

**If no detection succeeds:** Use the `generic` branch and note what was detected vs expected.

---

## Branch Router

{{PHASES}}

Route to the correct implementation branch based on detection result:

```
if LANGUAGE == "python":
    if FRAMEWORK == "fastapi":   → Branch: Python/FastAPI
    if FRAMEWORK == "django":    → Branch: Python/Django
    else:                        → Branch: Python/Generic

if LANGUAGE == "node":
    if FRAMEWORK == "nextjs":    → Branch: Node/Next.js
    if FRAMEWORK == "nuxtjs":    → Branch: Node/Nuxt
    else:                        → Branch: Node/Generic

if LANGUAGE == "go":             → Branch: Go/Generic
if LANGUAGE == "rust":           → Branch: Rust/Generic
if LANGUAGE == "unknown":        → Branch: Universal/Generic
```

---

## Branch Implementations

Each branch follows this internal contract:
1. Load branch-specific configuration
2. Execute the core operation for that platform
3. Run branch-specific validation
4. Return result in the universal output format

### Branch: Python/FastAPI

```
# Core operation for FastAPI projects
- Read app/main.py or main.py for entry point
- Detect async vs sync handler patterns
- Apply FastAPI-specific {{SKILL_NAME}} logic
- Validate against FastAPI conventions
```

FastAPI-specific patterns to apply:
- Use `async def` for all route handlers
- Dependency injection via `Depends()`
- Pydantic models for request/response validation
- HTTPException for error responses

### Branch: Node/Next.js

```
# Core operation for Next.js projects
- Detect App Router vs Pages Router (check src/app/ vs pages/)
- Detect TypeScript vs JavaScript (check tsconfig.json)
- Apply Next.js-specific {{SKILL_NAME}} logic
- Validate against Next.js conventions
```

Next.js-specific patterns to apply:
- Server Components by default, `"use client"` only when needed
- Route handlers in `app/api/` directory
- `next/navigation` for routing (not `next/router` in App Router)
- `generateMetadata` for dynamic metadata

### Branch: Go/Generic

```
# Core operation for Go projects
- Read go.mod for module name and dependencies
- Detect web framework (gin, echo, chi, stdlib)
- Apply Go-specific {{SKILL_NAME}} logic
- Validate against Go conventions
```

### Branch: Universal/Generic

```
# Fallback — works on any codebase
- Use only file system operations
- Apply language-agnostic {{SKILL_NAME}} logic
- Flag that detection failed and why
- Output may be less specific than platform branches
```

---

## Output Contract

All branches must produce output in this format regardless of which path was taken:

```markdown
## {{SKILL_NAME}} Result

**Detected Platform:** {LANGUAGE}/{FRAMEWORK}
**Deploy Target:** {DEPLOY}
**Branch Used:** {branch-name}

---

{CORE OUTPUT — specific to what this skill does}

---

## Platform Notes

{Any platform-specific caveats or follow-up steps}

## Confidence

{High | Medium | Low} — {reason if not High}
```

---

## Quality Gates

{{QUALITY_GATES}}

Before presenting output:
- [ ] Detection ran completely (not short-circuited)
- [ ] Correct branch was selected (verify against detection result)
- [ ] Output format matches the universal contract
- [ ] Platform-specific conventions were applied, not just generic logic
- [ ] Low-confidence results are flagged with explanation

---

## Adding New Platform Support

To add support for a new platform:

1. Add detection logic to the Detection Engine section
2. Add the branch route to the Branch Router table
3. Create a Branch Implementation section
4. Verify the output still matches the universal contract
5. Update the "Supported platforms" list in Overview

---

*Tier 3-4 skill — detection-first branching. For fixed linear execution, see mid-tool template.
For parallel research across sources, see advanced-multi-tool template.*
