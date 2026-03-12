# LinkedIn Studio — Quality Gate Hooks

This directory contains the five quality gate hook scripts for the `linkedin-studio` plugin. Each script is a standalone bash program that validates one dimension of post quality before it advances through the content pipeline.

---

## Hook Overview

| Script | Gate Name | Position in Pipeline | Blocks on |
|---|---|---|---|
| `pre-schedule-validator.sh` | Pre-Schedule Validation | Final gate before Metricool | Any single check failure |
| `humanizer-gate.sh` | AI Detection | After content-writer, before structure-reviewer | 3+ AI signals |
| `hook-strength.sh` | Hook Quality Scorer | After structure-reviewer, before approval | Score below 70/100 |
| `structure-compliance.sh` | Structure Compliance | After content-writer | Any structural violation |
| `duplicate-detector.sh` | Duplicate Content | Before content-writer (early gate) | 60%+ trigram overlap |

---

## Individual Hook Reference

### `pre-schedule-validator.sh`

The final gate that every post must pass before being handed to Metricool for scheduling. Run this last.

**Input environment variables:**

| Variable | Required | Description |
|---|---|---|
| `POST_TEXT` | Yes | Full post content |
| `POST_STATUS` | Yes | Must be `approved` to pass |
| `METRICOOL_ID` | No | Must be empty (post not yet scheduled) |
| `IS_CAROUSEL_SLIDE` | No | `true` applies shorter word count range (50–150 words) |

**Checks:**
1. Post text is not empty
2. Word count: 150–300 words (standard) or 50–150 words (carousel slide)
3. CTA present — final content line ends with `?` or starts with an imperative verb
4. Hashtag count: 3–5 hashtags (`#word` format)
5. Status is `approved`, not `draft`
6. No `METRICOOL_ID` set (not already scheduled)

**Exit:** `0` = PASSED, `1` = BLOCKED

---

### `humanizer-gate.sh`

Catches AI-generated language that the humanizer agent missed. Runs early in the pipeline to avoid wasted work.

**Input environment variables:**

| Variable | Required | Description |
|---|---|---|
| `POST_TEXT` | Yes | Full post content |

**Checks:**
- **Phase 1:** Scans for 25 banned AI phrases (`leverage`, `delve into`, `in conclusion`, `moreover`, `nevertheless`, `game-changer`, `from a * perspective`, etc.)
- **Phase 2:** Detects 3+ consecutive sentences starting with the same word (over-parallel structure)
- **Phase 3:** Flags excessive em-dashes (>3) or bullet points (>5 lines)

**Thresholds:**

| Total issues | Outcome |
|---|---|
| 0 | PASSED |
| 1–2 | WARNING (not blocked, but flagged) |
| 3+ | BLOCKED |

**Exit:** `0` = PASSED or WARNING, `1` = BLOCKED

---

### `hook-strength.sh`

Scores the first paragraph of the post (everything before the first blank line) against six proven LinkedIn hook criteria.

**Input environment variables:**

| Variable | Required | Description |
|---|---|---|
| `POST_TEXT` | Yes | Full post content |

**Scoring rubric (max 100 pts):**

| Criterion | Points |
|---|---|
| Contains a number or statistic | +20 |
| Contains a question mark | +20 |
| Under 12 words | +15 |
| Contains a power word (`mistake`, `secret`, `truth`, `warning`, `failed`, `earned`, `lost`, `changed`, etc.) | +20 |
| Opens with `I `, `My `, or `We ` | +15 |
| Ends with `...` or `:` | +10 |

**Threshold:** 70/100 to pass.

On failure, the script outputs the score and specific suggestions for each missed criterion.

**Exit:** `0` = score >= 70, `1` = score < 70

---

### `structure-compliance.sh`

Validates post formatting against LinkedIn readability standards. Produces line-number-specific violation messages.

**Input environment variables:**

| Variable | Required | Description |
|---|---|---|
| `POST_TEXT` | Yes | Full post content |

**Checks:**
1. No paragraph runs longer than 3 consecutive non-empty lines
2. No sentence longer than 25 words (soft warning at 20 words)
3. Hashtags appear only at the end of the post, not embedded in the body
4. Post does not start with the word `I`
5. Last line does not end with a period (must be CTA or hashtags)

Warnings are reported but do not block. Violations block.

**Exit:** `0` = PASSED, `1` = BLOCKED

---

### `duplicate-detector.sh`

Prevents recycled or near-duplicate content from being scheduled. Uses trigram overlap (3-word sequences) to measure similarity against recent posts.

**Input environment variables:**

| Variable | Required | Description |
|---|---|---|
| `POST_TEXT` | Yes | Full post content |
| `NEON_DATABASE_URL` | No | PostgreSQL connection string for Neon DB |

**Data sources (checked in order):**
1. **Neon database** — queries `content_queue` for posts from the last 30 days if `NEON_DATABASE_URL` is set and `psql` is available
2. **Local cache** — reads `~/.linkedin-studio-cache/recent-posts.txt` (base64-encoded posts, one per line) if no database

**Thresholds:**

| Trigram overlap | Outcome |
|---|---|
| < 40% | PASSED |
| 40–59% | WARNING (not blocked) |
| 60%+ | BLOCKED |

**Requirements:** Python 3 is required for trigram computation. `psql` is required for database mode.

**Seeding the local cache:**
```bash
# Encode and append a post to the local cache
mkdir -p ~/.linkedin-studio-cache
echo "Your recent post text here..." | base64 >> ~/.linkedin-studio-cache/recent-posts.txt
```

**Exit:** `0` = unique or WARNING, `1` = BLOCKED

---

## Pipeline Integration

The recommended hook execution order, mapped to pipeline stages:

```
content-writer
    |
    v
[duplicate-detector]      ← prevents wasted work on recycled topics
    |
    v
[humanizer-gate]          ← catches AI language early
    |
    v
structure-reviewer
    |
    v
[structure-compliance]    ← validates formatting
    |
    v
[hook-strength]           ← validates the opening hook
    |
    v
approval stage
    |
    v
[pre-schedule-validator]  ← final gate before Metricool
    |
    v
Metricool scheduling
```

---

## Running Hooks Manually

All scripts read input from environment variables. Example:

```bash
export POST_TEXT="I made a mistake that cost me $47k in my first year of consulting.

Here's what I learned — and what I'd tell every founder before they sign their first contract:

1. Never quote a flat fee without a scope document.
2. Revisions are unlimited without a defined process.
3. Clients expand scope when there are no consequences.

Save this post before your next client call.

#consulting #freelance #business"

export POST_STATUS="approved"
export METRICOOL_ID=""
export IS_CAROUSEL_SLIDE="false"

bash ./pre-schedule-validator.sh
bash ./humanizer-gate.sh
bash ./hook-strength.sh
bash ./structure-compliance.sh
```

---

## Permissions

All scripts must be executable. Set permissions after any new file creation:

```bash
chmod +x /Users/yasmineseidu/.claude/plugins/linkedin-studio/hooks/*.sh
```

---

## Requirements

| Requirement | Used by |
|---|---|
| `bash` 3.2+ | All scripts |
| `python3` | `duplicate-detector.sh`, `structure-compliance.sh` (sentence splitting) |
| `psql` | `duplicate-detector.sh` (database mode only) |
| `grep` with `-P` (Perl regex) | `humanizer-gate.sh`, `pre-schedule-validator.sh` |

On macOS, install `grep` with Perl support via Homebrew if needed:
```bash
brew install grep
```
