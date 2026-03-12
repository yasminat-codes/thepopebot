# Pipeline Gate Definitions

## Gate Types

| Type | On Failure                                            | Override Allowed |
|------|-------------------------------------------------------|------------------|
| Hard | Stage halted — post does not advance                  | No               |
| Soft | Warning recorded — post advances with flag            | Yes              |

---

## Gates by Stage

### RESEARCH Stage

#### G-R1 — Minimum Topics Returned

| Field          | Value                                         |
|----------------|-----------------------------------------------|
| Type           | Hard                                          |
| Trigger        | RESEARCH stage completes and returns results  |
| Pass condition | At least 1 topic angle is present in output   |
| Fail condition | `research_angles` array is empty or absent    |
| Override       | No                                            |
| Recovery       | Re-run RESEARCH with broader keywords or extended `time_range` |

---

### WRITE Stage

#### G-W1 — Content Length

| Field          | Value                                               |
|----------------|-----------------------------------------------------|
| Type           | Hard                                                |
| Trigger        | WRITE stage produces `post_text`                   |
| Pass condition | `len(post_text)` is between 150 and 3000 (inclusive) |
| Fail condition | Content is shorter than 150 or longer than 3000 chars |
| Override       | No                                                  |
| Recovery       | Regenerate post targeting the 800–1500 char sweet spot |

#### G-W2 — Hook Length

| Field          | Value                                                      |
|----------------|------------------------------------------------------------|
| Type           | Hard                                                       |
| Trigger        | WRITE stage produces `hook`                               |
| Pass condition | `hook` is 20 words or fewer                               |
| Fail condition | `hook` exceeds 20 words                                   |
| Override       | No                                                         |
| Recovery       | Rewrite hook to a single punchy sentence under 20 words   |

#### G-W3 — Content Pillar Assigned

| Field          | Value                                                           |
|----------------|-----------------------------------------------------------------|
| Type           | Hard                                                            |
| Trigger        | WRITE stage completes                                          |
| Pass condition | `content_pillar` is a non-empty string matching a known pillar |
| Fail condition | `content_pillar` is null, empty, or unrecognized               |
| Override       | No                                                              |
| Recovery       | Re-classify the post against the defined pillar list           |

---

### HUMANIZE Stage

#### G-H1 — AI Score Reduced

| Field          | Value                                                              |
|----------------|--------------------------------------------------------------------|
| Type           | Soft                                                               |
| Trigger        | HUMANIZE stage produces `ai_score`                                |
| Pass condition | `ai_score` after humanization is lower than `ai_score` at intake  |
| Fail condition | Score did not decrease (humanization had no measurable effect)    |
| Override       | Yes                                                                |
| Recovery       | Run an additional humanization pass targeting conversational tone |

#### G-H2 — Brand Vocabulary Present

| Field          | Value                                                                  |
|----------------|------------------------------------------------------------------------|
| Type           | Soft                                                                    |
| Trigger        | HUMANIZE stage completes                                               |
| Pass condition | At least one word from `brand_voice_profile.vocabulary` appears in content |
| Fail condition | No vocabulary match found                                              |
| Override       | Yes                                                                     |
| Recovery       | Inject a brand vocabulary word naturally into the content              |

#### G-H3 — Avoid-Words Absent

| Field          | Value                                                                  |
|----------------|------------------------------------------------------------------------|
| Type           | Hard                                                                    |
| Trigger        | HUMANIZE stage completes                                               |
| Pass condition | No word from `brand_voice_profile.avoid_words` is present in content  |
| Fail condition | One or more avoid-words detected                                       |
| Override       | No                                                                      |
| Recovery       | Replace the offending words and re-run the avoid-word check            |

---

### STRUCTURE Stage

#### G-S1 — Quality Score Threshold

| Field          | Value                                      |
|----------------|--------------------------------------------|
| Type           | Hard                                       |
| Trigger        | STRUCTURE stage scores the post            |
| Pass condition | `quality_score` >= 70                      |
| Fail condition | `quality_score` < 70                       |
| Override       | No                                         |
| Recovery       | Return post to WRITE stage for a rewrite   |

#### G-S2 — Hook Strength Threshold

| Field          | Value                                               |
|----------------|-----------------------------------------------------|
| Type           | Hard                                                |
| Trigger        | STRUCTURE stage scores the hook                    |
| Pass condition | `hook_score` >= 7                                  |
| Fail condition | `hook_score` < 7                                   |
| Override       | No                                                  |
| Recovery       | Rewrite hook; use `hook_suggestions` from RESEARCH |

#### G-S3 — CTA Present

| Field          | Value                                                             |
|----------------|-------------------------------------------------------------------|
| Type           | Soft                                                              |
| Trigger        | STRUCTURE stage review completes                                 |
| Pass condition | CTA signal detected in reviewed content                          |
| Fail condition | No CTA signal found                                              |
| Override       | Yes                                                               |
| Recovery       | Append a contextually appropriate CTA from `cta_suggestions`    |

---

### VISUAL Stage

#### G-V1 — Visual Asset Present

| Field          | Value                                                              |
|----------------|--------------------------------------------------------------------|
| Type           | Soft                                                               |
| Trigger        | VISUAL stage completes                                            |
| Pass condition | `media_urls` has at least 1 entry OR `visual_type` is `"canva"`  |
| Fail condition | `media_urls` is empty AND `visual_type` is `"none"`              |
| Override       | Yes                                                                |
| Recovery       | Generate an image prompt and attempt asset creation              |

---

### CALENDAR Stage

#### G-C1 — Scheduled Time in Future

| Field          | Value                                                           |
|----------------|-----------------------------------------------------------------|
| Type           | Soft                                                            |
| Trigger        | CALENDAR stage assigns `scheduled_at`                          |
| Pass condition | `scheduled_at` is strictly after the current UTC timestamp     |
| Fail condition | `scheduled_at` is in the past or equals current time          |
| Override       | Yes                                                             |
| Recovery       | Re-assign `scheduled_at` to the next available slot           |

---

### SCHEDULE Stage

#### G-SC1 — Metricool API Success

| Field          | Value                                                                   |
|----------------|-------------------------------------------------------------------------|
| Type           | Hard                                                                    |
| Trigger        | POST /social/metricool/post call returns                               |
| Pass condition | Response status code is `200`                                          |
| Fail condition | Any non-200 response (400, 401, 422, 429, 5xx)                        |
| Override       | No                                                                      |
| Recovery       | 400/422 → fix payload fields. 401 → check API key. 429 → wait and retry. 5xx → circuit breaker handles retry. |

---

## Gate Summary Table

| Gate  | Stage     | Type | Threshold / Condition                       | Override |
|-------|-----------|------|---------------------------------------------|----------|
| G-R1  | RESEARCH  | Hard | >= 1 topic angle returned                   | No       |
| G-W1  | WRITE     | Hard | 150–3000 chars                              | No       |
| G-W2  | WRITE     | Hard | Hook <= 20 words                            | No       |
| G-W3  | WRITE     | Hard | Content pillar assigned                     | No       |
| G-H1  | HUMANIZE  | Soft | AI score decreased                          | Yes      |
| G-H2  | HUMANIZE  | Soft | Brand vocabulary present                    | Yes      |
| G-H3  | HUMANIZE  | Hard | No avoid-words present                      | No       |
| G-S1  | STRUCTURE | Hard | quality_score >= 70/100                     | No       |
| G-S2  | STRUCTURE | Hard | hook_score >= 7/10                          | No       |
| G-S3  | STRUCTURE | Soft | CTA signal present                          | Yes      |
| G-V1  | VISUAL    | Soft | >= 1 asset URL or Canva design              | Yes      |
| G-C1  | CALENDAR  | Soft | scheduled_at in future                      | Yes      |
| G-SC1 | SCHEDULE  | Hard | Metricool API returns 200                   | No       |
