# Phase 0: Codebase Scan Procedures

Phase 0 runs before the interview begins. Its job is to gather facts so interview questions arrive pre-filled with accurate defaults. All results are stored as internal context — never shown to the user verbatim.

---

## Scan Targets

### 1. Language Detection

Glob for the following files in order of priority:

| File | Language Detected |
|------|------------------|
| `pyproject.toml`, `requirements.txt`, `setup.py` | Python |
| `package.json` | JavaScript / TypeScript |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `build.gradle`, `pom.xml` | Java / Kotlin |
| `pubspec.yaml` | Dart / Flutter |

If multiple are found, record all. Primary language = the one whose files are most numerous in `src/` or root.

If version is needed: read `pyproject.toml` for `python_requires`, `package.json` for `engines.node`, `go.mod` for `go` directive.

### 2. Framework Detection

After language is confirmed, read the detected config files for framework names:

**Python:** Read `pyproject.toml` dependencies section and `requirements.txt` for:
- `fastapi` → FastAPI
- `django` → Django
- `flask` → Flask
- `starlette` → Starlette
- `pydantic-ai` → Pydantic AI agent project

**JavaScript / TypeScript:** Read `package.json` dependencies for:
- `next` → Next.js
- `express` → Express
- `fastify` → Fastify
- `react` (without next) → React SPA
- `vue` → Vue
- `@anthropic-ai/claude-code` → Claude Code plugin project

**Go:** Read `go.mod` require block for:
- `github.com/gin-gonic/gin` → Gin
- `github.com/labstack/echo` → Echo
- `net/http` only → Standard library

**Rust:** Read `Cargo.toml` dependencies for:
- `actix-web` → Actix
- `axum` → Axum
- `warp` → Warp

### 3. Existing Skills Inventory

Glob for all existing skill definitions:

```
.claude/skills/*/SKILL.md          (project-scoped)
~/.claude/skills/*/SKILL.md        (global, if present)
```

For each found SKILL.md, extract:
- Skill name (from directory name)
- Tier (scan for `tier:` in frontmatter)
- Primary tool types (scan for Read, Write, Bash, Glob, Grep mentions in first 50 lines)

Record total count and names. This prevents duplicate skill creation and informs orchestrator detection (if 3+ skills exist covering related domains, the new skill may be an orchestrator).

### 4. Test Patterns

Glob for test infrastructure:

| Pattern | Framework Detected |
|---------|-------------------|
| `**/test_*.py`, `**/tests/*.py`, `pytest.ini`, `pyproject.toml` [tool.pytest] | Pytest |
| `**/*.test.ts`, `**/*.spec.ts`, `jest.config.*` | Jest (TypeScript) |
| `**/*.test.js`, `**/*.spec.js` | Jest (JavaScript) |
| `**/*_test.go` | Go test |
| `**/tests/` directory | Generic test directory |
| `Makefile` with `test:` target | Make-based test runner |

Also check for coverage configuration:
- `.coveragerc`, `pyproject.toml` [tool.coverage] → Python coverage
- `jest.config.*` with `coverageThreshold` → JS coverage

### 5. Code Style

Read these files if they exist (do not error if missing):

| File | What to Extract |
|------|----------------|
| `tsconfig.json` | `strict`, `target`, `moduleResolution` |
| `ruff.toml` or `pyproject.toml` [tool.ruff] | `line-length`, `select`, `ignore` |
| `.eslintrc`, `.eslintrc.js`, `.eslintrc.json` | `extends`, `rules` summary |
| `.prettierrc`, `prettier.config.js` | `printWidth`, `singleQuote`, `semi` |
| `mypy.ini`, `pyproject.toml` [tool.mypy] | `strict`, `disallow_untyped_defs` |

### 6. Project Context

Read `CLAUDE.md` at root or `.claude/CLAUDE.md` if it exists. Extract:
- Any listed conventions relevant to skill writing
- Task lifecycle stages if defined
- Coverage minimums if specified
- Any custom tool restrictions

Also read `.claude/context/PROJECT_CONTEXT.md` and `.claude/context/SDK_PATTERNS.md` if present (these are high-signal files).

---

## Scan Output Format (Internal Context)

After all scans complete, construct this internal summary block. This is never shown to the user — it pre-fills interview defaults.

```
SCAN RESULTS:
- Language: Python 3.12
- Framework: FastAPI
- Test Framework: Pytest
- Coverage Config: pyproject.toml [tool.coverage], threshold 90%
- Existing Skills: 3 (skills-architect, linkedin-studio, ai-humanizer)
- Style: Ruff with line-length=100, select=["E","F","I"]
- TypeScript Strict: N/A (Python project)
- Conventions: From CLAUDE.md — snake_case, task lifecycle 5 stages,
    coverage >90% tools >85% agents, skills via Skill tool only
- Project Type: Claude Agent SDK agent project
```

---

## Framework-Specific Recommendations

| Framework | Recommended Tier | Key Skill Patterns |
|-----------|-----------------|-------------------|
| FastAPI | mid-tool or advanced-multi-tool | API client, async patterns, Pydantic models |
| Next.js | branching-workflow | Server vs client component awareness |
| Django | sequential-workflow | ORM patterns, migration awareness |
| Pydantic AI | orchestrator | Agent-to-agent handoff patterns |
| Go / Gin | scripts-cli | Binary invocation, stdout parsing |
| Standard library | codebase-agnostic | Language-neutral patterns |
| No framework detected | question-heavy-interview | Gather more before designing |

---

## How Scan Results Feed Into Interview Questions

Each scan result maps to a specific interview question default:

| Scan Result | Interview Question Affected | Default Set To |
|-------------|---------------------------|----------------|
| Language: Python | "What language does this skill target?" | Python (skip or confirm) |
| Framework: FastAPI | "Any framework-specific patterns needed?" | Yes, FastAPI async patterns |
| Test Framework: Pytest | "How should tests be structured?" | Pytest with fixtures |
| Coverage threshold found | "What coverage minimum?" | Extracted value (e.g. 90%) |
| Existing skills > 5 | "Should this orchestrate existing skills?" | Present list, ask |
| Ruff config found | "Code style preferences?" | Ruff (show line-length) |
| No CLAUDE.md found | "Any project conventions I should follow?" | Open question, no default |

---

## Error Handling

**No config files found at all:**
- Do not assume a language
- Set all interview defaults to open questions
- Begin interview with: "I couldn't detect a language or framework. What language and stack is this skill for?"

**Conflicting signals (e.g., both package.json and pyproject.toml):**
- Record both
- Ask during interview: "I see both Python and Node.js files. Which language should this skill target?"

**CLAUDE.md parse failure (malformed):**
- Skip CLAUDE.md extraction
- Continue with remaining scan results
- Do not block on this failure

**Glob finds 0 existing skills:**
- Note "no existing skills" in scan results
- During interview, do not suggest orchestrator tier unless user explicitly requests it
