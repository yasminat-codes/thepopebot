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

This skill works on any codebase regardless of language, framework, or age. It auto-detects
the project's characteristics and applies universally applicable patterns. No project-specific
configuration is required.

**Guaranteed to work on:** Any directory containing code files
**Adapts to:** Language, framework, test runner, package manager, CI system
**Does not modify:** Source files (read-only analysis by default)

---

## Auto-Detection Sequence

Run all detectors in parallel. Build a project profile before taking any action.

### Detector 1: Project Type

```bash
# Monorepo detection
[ -f "pnpm-workspace.yaml" ] && echo "monorepo:pnpm"
[ -f "lerna.json" ] && echo "monorepo:lerna"
[ -f "nx.json" ] && echo "monorepo:nx"
[ -f "turbo.json" ] && echo "monorepo:turbo"

# Single app
[ -f "package.json" ] && ! [ -f "pnpm-workspace.yaml" ] && echo "single:node"
[ -f "pyproject.toml" ] && echo "single:python"
[ -f "go.mod" ] && echo "single:go"
[ -f "Cargo.toml" ] && echo "single:rust"
[ -f "Gemfile" ] && echo "single:ruby"
```

### Detector 2: Package Manager

```bash
[ -f "pnpm-lock.yaml" ] && echo "pnpm"
[ -f "yarn.lock" ] && echo "yarn"
[ -f "bun.lockb" ] && echo "bun"
[ -f "package-lock.json" ] && echo "npm"
[ -f "poetry.lock" ] && echo "poetry"
[ -f "Pipfile.lock" ] && echo "pipenv"
[ -f "uv.lock" ] && echo "uv"
```

### Detector 3: Test Runner

```bash
PACKAGE=$(cat package.json 2>/dev/null || echo "{}")
echo "$PACKAGE" | grep -q '"vitest"' && echo "vitest"
echo "$PACKAGE" | grep -q '"jest"' && echo "jest"
echo "$PACKAGE" | grep -q '"mocha"' && echo "mocha"
[ -f "pytest.ini" ] || [ -f "pyproject.toml" ] && grep -q "pytest" pyproject.toml && echo "pytest"
[ -f "go.mod" ] && echo "go-test"
```

### Detector 4: CI System

```bash
[ -d ".github/workflows" ] && echo "github-actions"
[ -f ".gitlab-ci.yml" ] && echo "gitlab-ci"
[ -f ".circleci/config.yml" ] && echo "circleci"
[ -f "Jenkinsfile" ] && echo "jenkins"
[ -f ".travis.yml" ] && echo "travis"
[ -f "bitbucket-pipelines.yml" ] && echo "bitbucket"
```

### Detector 5: Code Size

```bash
# Get line count across all source files
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.py" -o -name "*.go" \) \
    ! -path "*/node_modules/*" ! -path "*/.git/*" ! -path "*/dist/*" ! -path "*/__pycache__/*" \
    | head -500 | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}'
```

Size buckets:
- < 1,000 lines: Micro project
- 1,000-10,000 lines: Small project
- 10,000-50,000 lines: Medium project
- 50,000-200,000 lines: Large project
- > 200,000 lines: Enterprise/monorepo

---

## Phase 1: Project Profile Construction

{{PHASES}}

After running all detectors, build the project profile:

```
PROJECT PROFILE
================
Type:           {monorepo | single-app | library | cli-tool}
Language(s):    {primary language + secondary}
Framework:      {framework or "none"}
Package Mgr:    {detected manager}
Test Runner:    {detected runner or "unknown"}
CI:             {detected CI or "none"}
Size:           {micro | small | medium | large | enterprise}
Age:            {estimated from git log or "unknown"}
Health:         {preliminary assessment}
```

If detection is ambiguous, note the ambiguity. Do not guess — surface uncertainty.

---

## Phase 2: Universal Analysis

Apply checks that work regardless of language or framework.

### Check: File Structure Hygiene

```bash
# Files that should not be committed
find . -name "*.env" ! -name ".env.example" ! -name ".env.template" -not -path "*/.git/*"
find . -name "*.pem" -o -name "*.key" -not -path "*/.git/*"
find . -name "*.log" -not -path "*/.git/*" -not -path "*/logs/*"
```

### Check: Dependency Manifest Health

```bash
# Outdated lockfile detection
[ package.json -nt package-lock.json ] && echo "WARN: package.json newer than lockfile"
[ pyproject.toml -nt poetry.lock ] && echo "WARN: pyproject.toml newer than lockfile"

# Missing lockfile
[ -f "package.json" ] && ! [ -f "package-lock.json" ] && ! [ -f "yarn.lock" ] && \
    ! [ -f "pnpm-lock.yaml" ] && ! [ -f "bun.lockb" ] && echo "WARN: No lockfile found"
```

### Check: Git Health

```bash
# Uncommitted changes
git status --porcelain 2>/dev/null | wc -l

# Large files that should be in .gitignore
git ls-files | xargs ls -la 2>/dev/null | awk '$5 > 1048576 {print $5, $9}' | sort -rn | head -10

# Secrets potentially committed (pattern scan)
git log --all --full-history --oneline 2>/dev/null | wc -l
```

### Check: Documentation Coverage

```bash
# Core documentation presence
[ -f "README.md" ] && echo "README: present" || echo "README: MISSING"
[ -f "CHANGELOG.md" ] && echo "CHANGELOG: present" || echo "CHANGELOG: missing"
[ -f "CONTRIBUTING.md" ] && echo "CONTRIBUTING: present" || echo "CONTRIBUTING: missing"
[ -f "LICENSE" ] || [ -f "LICENSE.md" ] && echo "LICENSE: present" || echo "LICENSE: MISSING"
[ -f ".env.example" ] && echo "ENV example: present" || echo "ENV example: missing"
```

### Check: Security Surface

```bash
# Hardcoded credential patterns (non-destructive scan)
grep -rI --include="*.{ts,tsx,js,py,go,rb,java}" \
    -E "(password|secret|api_key|apikey|auth_token)\s*=\s*['\"][^'\"]{8,}" \
    --exclude-dir={node_modules,.git,dist,build,__pycache__} \
    . 2>/dev/null | head -20
```

---

## Phase 3: Language-Adaptive Deep Checks

Based on detected language, apply deeper checks:

### If Python detected:

```bash
# Type annotation coverage (sample)
grep -rL "def.*->.*:" --include="*.py" --exclude-dir=__pycache__ . | head -20

# Async/sync mixing anti-pattern
grep -rn "asyncio.run" --include="*.py" . | head -10

# Missing __init__.py in packages
find . -type d -not -path "*/.git/*" -not -path "*/node_modules/*" | while read d; do
    [ -f "$d/__init__.py" ] || echo "No __init__.py: $d"
done | head -20
```

### If Node.js detected:

```bash
# Console.log left in production code
grep -rn "console\.log" --include="*.{ts,tsx,js}" \
    --exclude-dir={node_modules,dist,build} . | wc -l

# TODO/FIXME density
grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.{ts,tsx,js}" \
    --exclude-dir={node_modules,dist,build} . | wc -l
```

---

## Phase 4: Findings Report

{{QUALITY_GATES}}

Structure all findings into severity tiers:

```markdown
# {{SKILL_NAME}} Analysis Report

**Project:** {name from package.json or directory name}
**Analyzed:** {timestamp}
**Profile:** {TYPE} | {LANGUAGE} | {FRAMEWORK} | {SIZE}

---

## Critical (Fix Immediately)

| # | Issue | Location | Impact |
|---|-------|----------|--------|
| 1 | [issue] | [file:line] | [impact] |

## High (Fix Before Next Release)

| # | Issue | Location | Effort |
|---|-------|----------|--------|
| 1 | [issue] | [file:line] | [S/M/L] |

## Medium (Backlog)

| # | Issue | Recommendation |
|---|-------|----------------|
| 1 | [issue] | [fix] |

## Low (Nice-to-Have)

- [item 1]
- [item 2]

---

## Summary Scorecard

| Dimension | Score | Details |
|-----------|-------|---------|
| Security | {A-F} | {brief} |
| Documentation | {A-F} | {brief} |
| Code Quality | {A-F} | {brief} |
| Dependency Health | {A-F} | {brief} |
| Git Hygiene | {A-F} | {brief} |
| **Overall** | **{A-F}** | |

---

## Top 3 Recommended Actions

1. **{Action 1}** — {why this first}
2. **{Action 2}** — {impact}
3. **{Action 3}** — {impact}
```

---

## References

{{REFERENCES}}

---

## Extending for New Languages

This skill can be extended to provide deeper analysis for additional languages by adding:
1. A new detector in Phase 1
2. A language-specific check block in Phase 3
3. Updated scoring weights in the Summary Scorecard

The report format and severity tiers remain the same for all extensions.

---

*Tier 3-4 skill — codebase-agnostic, auto-detecting, read-only analysis. For platform-specific
branching logic, see branching-workflow template.*
