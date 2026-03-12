# Quality Gates Reference

## Gate Types

| Type | Behavior on Failure                                        |
|------|------------------------------------------------------------|
| Hard | Post is **excluded** from the batch — cannot be overridden |
| Soft | Post is **flagged with a warning** but still included      |

---

## Gate Definitions

### G1 — Length

- **Type:** Hard
- **Rule:** Post content must be between 150 and 3000 characters (inclusive).
- **Edge case — Carousel slides:** Each slide uses a tighter range of 50–150 characters. Standard G1 bounds do not apply to carousel slide content.
- **Failure behavior:** Post excluded from batch.

---

### G2 — Hook

- **Type:** Hard
- **Rule:** The first line (up to the first line break or sentence end) must be 20 words or fewer.
- **Edge case — Question hooks:** A hook phrased as a question may run slightly over 20 words if the question structure requires it. Apply judgment; do not auto-fail on 21–22 word question hooks.
- **Failure behavior:** Post excluded from batch.

---

### G3 — CTA

- **Type:** Soft
- **Rule:** Content should contain a recognizable call-to-action signal. Detection patterns include:
  - Imperative verbs: "comment", "share", "follow", "DM", "subscribe", "click", "drop", "tag"
  - Question prompts at the end: "What do you think?", "Have you tried this?"
  - Link invitations: "link in comments", "full post in bio"
- **Failure behavior:** Post included in batch with a `cta_warning: true` flag. Not blocked.

---

### G4 — Visual

- **Type:** Soft
- **Rule:** At least one of the following must be present: `media_urls` (non-empty array) or `canva_design_url` (non-null string).
- **Failure behavior:** Post included in batch with a `visual_warning: true` flag. Not blocked.

---

### G5 — Schedule

- **Type:** Hard
- **Rule:** `scheduled_at` must be a valid ISO 8601 datetime that is strictly in the future relative to the moment of batch submission.
- **Failure behavior:** Post excluded from batch. No override allowed.

---

## Override Rules

| Scenario                              | Allowed? |
|---------------------------------------|----------|
| Override a soft gate (G3, G4) failure | Yes      |
| Override a hard gate (G1, G2, G5) failure | No   |

When a soft gate override is applied, the post is included in the batch and the `overridden: true` flag is set alongside the original warning flag.

---

## Batch Behavior Summary

| Gate | Type | Batch outcome on failure         | Override |
|------|------|----------------------------------|----------|
| G1   | Hard | Post excluded                    | No       |
| G2   | Hard | Post excluded                    | No       |
| G3   | Soft | Post included with warning flag  | Yes      |
| G4   | Soft | Post included with warning flag  | Yes      |
| G5   | Hard | Post excluded                    | No       |

---

## Batch Result Shape

Each post in the batch result carries a gate summary:

```json
{
  "post_id": "p_001",
  "included": true,
  "gates": {
    "G1": "pass",
    "G2": "pass",
    "G3": "warn",
    "G4": "pass",
    "G5": "pass"
  },
  "flags": {
    "cta_warning": true,
    "overridden": false
  }
}
```

Excluded posts:

```json
{
  "post_id": "p_002",
  "included": false,
  "excluded_reason": "G1_length_fail",
  "gates": {
    "G1": "fail",
    "G2": "pass",
    "G3": "pass",
    "G4": "warn",
    "G5": "pass"
  }
}
```
