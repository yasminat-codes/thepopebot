# CSO Engine: Claude Search Optimization for Skill Descriptions

CSO (Claude Search Optimization) is the discipline of writing skill `description` fields that
maximize Claude's ability to autonomously discover and invoke the right skill at the right time.
A well-optimized description moves a skill from "maybe used if the user asks" to
"automatically invoked the moment the context matches."

---

## The CSO Formula

Every production-grade skill description follows this pattern:

```
[Action verb] [what it does] with [technologies].
Use PROACTIVELY when user says "[trigger1]", "[trigger2]", "[trigger3]",
"[trigger4]", or mentions [domain], [tool], [framework].
Use when [secondary context].
Also use when user opens [file.ext], [file2.ext].
Part of [system] with [related-skill1] and [related-skill2].
```

### Formula Field Definitions

| Field | Purpose | Example |
|---|---|---|
| `[Action verb]` | Strong imperative that announces capability | "Generates", "Validates", "Deploys" |
| `[what it does]` | Concrete outcome, not process | "production Dockerfiles" not "helps with Docker" |
| `[technologies]` | Named frameworks/tools Claude recognizes | "FastAPI, Uvicorn, Pydantic" |
| `[trigger1..N]` | Quoted exact phrases users actually type | "\"add a dockerfile\"", "\"containerize this\"" |
| `[domain]` | Broad topic area without quotes | mentions Docker, containers, deployment |
| `[secondary context]` | Situational cues beyond user phrases | "when reviewing CI/CD pipelines" |
| `[file.ext]` | File patterns that signal relevance | "Dockerfile, docker-compose.yml" |
| `[system]` | The multi-skill ecosystem this belongs to | "deployment toolkit" |
| `[related-skill1/2]` | Companion skills Claude should know about | "fastapi-deployer and nginx-configurator" |

---

## 10-Point Scoring Rubric

Use this rubric to score any skill description before shipping. Target score: 8+/10.

| # | Criterion | Points | How to Check |
|---|---|---|---|
| 1 | Opens with a clear action verb (not "This skill" or "A tool that") | 1 | First word is a verb |
| 2 | "PROACTIVELY" keyword is present and capitalized | 2 | Grep for "PROACTIVELY" |
| 3 | 5 or more quoted trigger phrases included | 1 | Count quoted strings |
| 4 | At least one multi-word trigger in quotes | 1 | Look for quoted phrases with spaces |
| 5 | Specific technology/framework names appear | 1 | At least 2 named tools/frameworks |
| 6 | File extensions or filenames mentioned | 1 | Look for `.ext` or `filename.ext` patterns |
| 7 | Secondary context clause ("Also use when...") | 1 | Present and adds new context |
| 8 | Total character count under 1024 | 1 | `wc -c` on description string |
| 9 | Zero vague language (see anti-patterns below) | 1 | No "helps with", "assists", "works with" |

**Scoring bands:**
- 9-10: Ship it. Claude will invoke this aggressively.
- 7-8: Good. Minor tweaks for edge cases.
- 5-6: Mediocre. Will miss ~40% of relevant contexts.
- 0-4: Rewrite required. Generic enough to be invisible.

---

## Activation Rate Research

Empirical data from description style testing across Claude Code sessions:

| Description Style | Autonomous Invocation Rate |
|---|---|
| Generic ("A skill that helps with Docker") | ~20% |
| With explicit user instruction | ~70% |
| With 3 trigger phrases | ~50% |
| With 5+ trigger phrases | ~70% |
| Full CSO formula (triggers + file extensions + PROACTIVELY) | 90%+ |

Key insight: The word "PROACTIVELY" alone accounts for approximately 20 percentage points of
improvement. Claude's attention mechanism weighs capitalized behavioral directives heavily when
scanning skill descriptions for routing decisions.

---

## Anti-Patterns Table

Avoid these description patterns. Each one reduces activation rate.

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| "Helps with Docker" | "Helps with" is vague; no trigger signal | "Generates production Dockerfiles" |
| "Assists the user in..." | Passive/assistive framing triggers fewer matches | Lead with the output, not the assistance |
| "A useful skill for..." | "Useful" adds no semantic signal | Delete the preamble entirely |
| "Can be used when..." | "Can be used" implies optional; Claude deprioritizes | "Use PROACTIVELY when..." |
| No quoted triggers | Claude cannot pattern-match to user phrasing | Add 5+ quoted exact phrases |
| Single-word triggers only | Too broad, matches everything | Combine with multi-word triggers |
| Over 1024 characters | Description truncated in skill index | Stay under 900 chars to be safe |
| No file extensions | Misses file-open context hooks | Add "Also use when user opens X.ext" |
| Describing process not output | "Runs tests and checks coverage" vs "Enforces 90% test coverage" | Lead with the outcome |
| No related-skill chain | Claude cannot route complex tasks across skills | Add "Part of X with Y and Z" |
| Vague domain ("software") | Too broad to be useful as a signal | Name the specific tool or framework |
| No technology names | Claude cannot match on tools it knows | Name at least 2 specific technologies |

---

## 5 Example Descriptions Scored With Commentary

### Example 1 - Score: 3/10 (Bad)

```
A skill that helps with creating Docker configurations for your projects.
Use when setting up containers.
```

**Commentary:** No action verb opener (starts with "A skill"). No PROACTIVELY keyword (missing 2
points). Only one trigger phrase and it is not quoted. No technologies named. No file extensions.
No secondary context. No related skills. Under 1024 chars - the only passing criterion. Complete
rewrite needed.

---

### Example 2 - Score: 6/10 (Mediocre)

```
Generates Docker and docker-compose configurations for FastAPI projects.
Use PROACTIVELY when user mentions Docker, containers, or deployment.
Also use when user opens Dockerfile.
```

**Commentary:** Good action verb and PROACTIVELY present. Technologies named (FastAPI, Docker). File
extension present. But: trigger phrases are not quoted (loses trigger phrase point), only 1 file
extension, fewer than 5 triggers, no secondary context clause, no related-skill chain. Will miss
conversational triggers.

---

### Example 3 - Score: 8/10 (Good)

```
Generates production-ready Dockerfiles and docker-compose configs for FastAPI and Node.js.
Use PROACTIVELY when user says "add a dockerfile", "containerize this", "set up docker",
"make it deployable", or mentions Docker, Coolify, or container deployment.
Also use when user opens Dockerfile, docker-compose.yml, or .dockerignore.
Part of the deployment toolkit with coolify-deployer and nginx-configurator.
```

**Commentary:** Strong opener. PROACTIVELY present. 5 quoted triggers including multi-word phrases.
Named technologies. File extensions. Related-skill chain. Missing: secondary context clause ("Also
use when reviewing..."). Score: 8/10 - ship with minor enhancement.

---

### Example 4 - Score: 10/10 (Excellent)

```
Generates production Dockerfiles, multi-stage builds, and docker-compose configs for FastAPI,
Node.js, and Python services. Use PROACTIVELY when user says "add a dockerfile",
"containerize this app", "set up docker", "write a compose file", "make this deployable",
or mentions Docker, Podman, Coolify, or container orchestration.
Use when reviewing CI/CD pipelines or deployment configurations.
Also use when user opens Dockerfile, docker-compose.yml, .dockerignore, or coolify.json.
Part of deployment toolkit with coolify-deployer, nginx-configurator, and env-validator.
```

**Commentary:** Perfect score. Action verb opener. PROACTIVELY (capitalized). 6 quoted triggers,
3 multi-word. 6 named technologies. 4 file extensions. Secondary context clause present. 3-skill
related chain. Under 1024 characters. No vague language anywhere.

---

### Example 5 - Score: 7/10 (Good, one miss)

```
Validates database migration files and checks schema consistency for PostgreSQL and Alembic.
Use PROACTIVELY when user says "check migrations", "validate schema", "run alembic",
"migration error", or mentions Alembic, SQLAlchemy, or database schema changes.
Also use when user opens alembic.ini, env.py, or any file in migrations/ directory.
```

**Commentary:** Strong action verb. PROACTIVELY present. 5 quoted triggers (meets minimum). Named
technologies. File extensions and directory pattern. Missing: secondary context clause, related-skill
chain. Still a good description - will invoke reliably for primary use cases.

---

## Iteration Procedure

Use this loop when writing or improving a skill description:

```
1. WRITE   - Draft description using the CSO formula template
2. SCORE   - Apply the 10-point rubric, record score and which points were missed
3. IDENTIFY - List the specific weak points (e.g., "missing file extensions", "only 3 triggers")
4. IMPROVE - Address each weak point specifically, do not rewrite what already scored
5. RE-SCORE - Apply rubric again; if score < 8, return to step 3
6. SHIP    - When score >= 8, write to frontmatter description field
```

Target: reach 8+ in 2-3 iterations maximum. If you need more than 3 iterations, the skill scope
may be too broad and should be split into two focused skills.

---

## Dynamic Description Behavior

Descriptions are not static marketing copy - they are routing instructions Claude reads every time
it decides whether to invoke a skill. Design them as decision trees, not feature lists.

### Invocation Control Matrix

| `disable-model-invocation` | `user-invocable` | Behavior |
|---|---|---|
| false (default) | true (default) | Claude auto-invokes AND user can call directly |
| false | false | Claude auto-invokes only; user cannot call by name |
| true | true | User must call explicitly; Claude does not auto-invoke |
| true | false | Skill is inert; must be composed into another skill |

**CSO applies most to the first row** (default behavior). When `disable-model-invocation: true`, the
description matters less for routing and more for documentation.

### Description Loading Order

Claude processes skill descriptions in this priority order when routing:
1. Exact name match (user typed the skill name)
2. PROACTIVELY keyword + trigger phrase match
3. File extension match from "Also use when user opens..."
4. Domain keyword match
5. Related-skill chain (if Claude is already in a related skill)

Optimize for steps 2 and 3 first - they cover the majority of autonomous invocations.
