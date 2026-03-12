# Validation Engine

5-point validation engine with auto-fix capability. Run after every skill creation or migration.

---

## Check 1: Line Count

**Purpose:** Enforce the 500/600 line limit to maintain skill scannability.

**Procedure:**
```bash
wc -l .claude/skills/{skill-name}/SKILL.md
```

**Thresholds:**
- Tier 1-5: max 500 lines
- Tier 6 (complex orchestrators): max 600 lines

**Fail condition:** Line count exceeds tier threshold.

**Auto-fix procedure:**
1. Read SKILL.md and identify all sections using `## Section` headers
2. Flag any section exceeding 30 lines as a candidate for extraction
3. For each flagged section:
   - Create `references/{SECTION-NAME}.md` with the full section content
   - Replace the section body in SKILL.md with a directive block:
     ```yaml
     - file: references/{SECTION-NAME}.md
       load: when {trigger derived from section name}
       contains: {one-line description of content}
     ```
4. Re-run `wc -l` to confirm the new count is within threshold
5. If still over limit, repeat extraction on next largest section

---

## Check 2: YAML Frontmatter Parse

**Purpose:** Ensure frontmatter is valid and complete before the skill runs.

**Procedure:**
1. Extract content between first `---` and second `---` delimiter
2. Parse as YAML
3. Check required fields exist and have correct types

**Required fields:**
| Field | Type | Example |
|---|---|---|
| `name` | string | `"my-skill"` |
| `description` | string | `"Analyzes..."` |
| `tools` | list of strings | `["Read", "Bash"]` |
| `version` | string | `"1.0.0"` |

**Optional fields with type enforcement:**
| Field | Type |
|---|---|
| `confirmation_required` | boolean (not string) |
| `hooks` | map |
| `memory` | map |

**Fail conditions:**
- Missing `name` or `description`
- Wrong type (e.g., `confirmation_required: "true"` instead of `true`)
- Malformed YAML that cannot be parsed

**Auto-fix procedure:**
1. **Missing quotes on strings with special chars:** wrap value in double quotes
2. **Bad indentation:** normalize to 2-space indent
3. **Boolean as string:** `"true"` → `true`, `"false"` → `false`
4. **Missing required field:** add placeholder and emit warning:
   ```
   WARNING: Added placeholder for missing field `name`. Update before use.
   ```
5. Re-parse after fixes to confirm validity

---

## Check 3: Orphan Reference Check

**Purpose:** Every file in `references/` and `scripts/` must be referenced in SKILL.md, and every directive must point to an existing file.

**Procedure:**

**Step A — Find orphaned files (file exists, no directive):**
1. List all files: `ls references/ scripts/`
2. For each file, search SKILL.md for its filename
3. Flag any file with no matching reference in SKILL.md

**Step B — Find broken directives (directive exists, no file):**
1. Extract all `file:` values from directive blocks in SKILL.md
2. For each path, check if the file exists
3. Flag any `file:` entry pointing to a non-existent path

**Fail conditions:**
- Any file in `references/` or `scripts/` has no directive in SKILL.md
- Any directive in SKILL.md points to a file that does not exist

**Auto-fix procedure:**

For orphaned files (Step A):
```yaml
# Add to SKILL.md directives section:
- file: references/{orphan-file}.md
  load: when {keyword derived from filename}
  contains: See file for details
```

For broken directives (Step B):
- If file path is a typo, attempt to find closest match in `references/` and correct the path
- If no match found, remove the directive and emit:
  ```
  WARNING: Removed directive for missing file `references/{path}`. Re-add when file is created.
  ```

---

## Check 4: Directive Completeness

**Purpose:** Every directive must have a trigger condition and a description so Claude knows when and why to load it.

**Directive schema (all fields required):**
```yaml
- file: references/FILENAME.md
  load: when {specific trigger condition}
  contains: {one-sentence description of what is in the file}
```

**Fail conditions:**
- `load:` field is missing or value is empty
- `load:` value is generic ("always", "sometimes", "if needed") without specificity
- `contains:` field is missing or value is empty

**Auto-fix procedure:**
1. For missing `load:` field — derive trigger from filename:
   - `VALIDATION-ENGINE.md` → `when running validation checks`
   - `TESTING-GENERATION.md` → `when generating pressure tests`
   - `PROACTIVE-SUGGESTIONS.md` → `when presenting enhancement suggestions`
   - `MEMORY-INTEGRATION.md` → `when loading or saving memory`
   - Unknown filename → `when this capability is needed` (emit warning to review)
2. For missing `contains:` — read first non-blank line of the referenced file and use it as the description (truncated to 120 chars)
3. Re-check all directives after fixes

---

## Check 5: CSO Score

**Purpose:** The description field must score at least 9/10 on the Claude Skill Optimization rubric to ensure Claude recognizes when to invoke the skill.

**Scoring rubric (1 point each):**
1. Starts with an action verb (not "Helps", "Assists", "Used for")
2. Contains PROACTIVELY keyword
3. Lists 5+ trigger phrases or contexts
4. Mentions specific file types or extensions it operates on (if applicable)
5. Mentions what it produces (output artifact or behavior)
6. Under 1024 characters
7. No filler words ("comprehensive", "powerful", "seamlessly")
8. Includes at least one negative trigger (when NOT to use)
9. References the skill's tier or complexity level
10. Contains at least one concrete example or pattern

**Fail condition:** Score below 9/10.

**Auto-fix procedure:**
1. Score the existing description against rubric — note which points fail
2. For each failing point, apply the corresponding fix:
   - Point 1: Replace leading word with action verb ("Creates", "Analyzes", "Validates")
   - Point 2: Insert "PROACTIVELY" before the first trigger list
   - Point 3: Expand trigger list to 5+ items using skill's phase list as source
   - Point 4: Add file extensions from the skill's `tools` list context
   - Point 5: Add "producing {output}" clause
   - Point 6: Trim description, moving details to `references/`
   - Point 7: Remove filler adjectives
   - Point 8: Add "Do NOT invoke for..." clause
   - Point 9: Add "(Tier N skill)" annotation
   - Point 10: Add one inline example pattern
3. Re-score. If still below 9/10, flag for manual review.

---

## Validation Report Template

```
=== SKILL VALIDATION REPORT ===
Skill: {skill-name}
Date: {date}
Tier: {tier}

CHECK 1: Line Count
  Status: PASS | FAIL
  Count: {N} / {max} lines
  Auto-fixed: YES | NO | N/A

CHECK 2: YAML Frontmatter
  Status: PASS | FAIL
  Issues: {list or "none"}
  Auto-fixed: YES | NO | N/A

CHECK 3: Orphan References
  Status: PASS | FAIL
  Orphaned files: {list or "none"}
  Broken directives: {list or "none"}
  Auto-fixed: YES | NO | N/A

CHECK 4: Directive Completeness
  Status: PASS | FAIL
  Incomplete directives: {list or "none"}
  Auto-fixed: YES | NO | N/A

CHECK 5: CSO Score
  Status: PASS | FAIL
  Score: {N}/10
  Failing points: {list or "none"}
  Auto-fixed: YES | NO | N/A

OVERALL: PASS | FAIL
Exit code: 0 (all pass) | 1 (failures remain after auto-fix)
```

---

## Auto-Fix Procedure (Full Run)

1. Run all 5 checks, collect results
2. For each failed check, apply its auto-fix procedure
3. Re-run all 5 checks on the modified files
4. If all checks now pass: exit 0, output PASS report
5. If any check still fails after auto-fix: exit 1, output FAIL report with details on stderr

**Exit codes:**
- `0` — All 5 checks pass (after auto-fix if needed)
- `1` — One or more checks still failing; details on stderr
