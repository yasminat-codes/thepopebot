# Quality Standards — LinkedIn Studio

> All quality thresholds in one place. Referenced by `ls:structure-reviewer`, `ls:humanizer`, `ls:batch-scheduler`, and the PreToolUse quality gate hook.

---

## Scoring Thresholds

| Metric                  | Threshold | Direction | Enforcement |
|-------------------------|-----------|-----------|-------------|
| Post quality score      | 75        | >= (min)  | Hard gate   |
| AI detection score      | 25        | <= (max)  | Hard gate   |
| Hook strength score     | 7/10      | >= (min)  | Hard gate   |
| Duplicate similarity    | 60%       | <= (max)  | Hard gate   |
| Structure score         | 70        | >= (min)  | Soft gate   |

---

## Word Count Ranges by Format

| Format              | Min Words | Max Words | Notes                                   |
|---------------------|-----------|-----------|------------------------------------------|
| Text post           | 150       | 300       | Sweet spot for LinkedIn algorithm         |
| Carousel slide      | --        | 40        | Per slide; aim for 20-30                  |
| Carousel total      | 100       | 250       | Across all slides combined                |
| Poll framing text   | 50        | 80        | Context before poll options               |
| Poll option          | --        | 25        | Per option; shorter is better             |
| Image post caption  | 80        | 200       | Shorter than text-only posts              |

---

## Formatting Rules

| Rule                    | Value         | Enforcement |
|-------------------------|---------------|-------------|
| Sentence length max     | 15 words      | Soft gate   |
| Paragraph max           | 2 lines       | Soft gate   |
| Hashtag count           | 3-5           | Hard gate   |
| Hook word count         | max 15 words  | Hard gate   |
| Line breaks between paragraphs | required | Hard gate   |
| Emoji usage             | 0-2 max       | Soft gate   |
| All-caps words          | 0-1 max       | Soft gate   |

---

## CTA Requirements

| Rule                                     | Enforcement |
|------------------------------------------|-------------|
| CTA present in every post                | Hard gate   |
| CTA must be specific, not generic        | Soft gate   |
| CTA placed in last 2 lines              | Soft gate   |
| No more than 1 CTA per post             | Soft gate   |

**Good CTAs:** "DM me 'FRAMEWORK' and I will send it over", "Comment 'YES' if you want the template"
**Bad CTAs:** "Let me know what you think", "Follow for more", "Share if you agree"

---

## Scheduling Constraints

| Rule                    | Value             | Enforcement |
|-------------------------|-------------------|-------------|
| Minimum gap between posts | 20 hours        | Hard gate   |
| Maximum posts per week  | 5                 | Hard gate   |
| Optimal posting days    | Tue, Wed, Thu     | Soft gate   |
| Optimal posting time    | 8:00-9:00 AM EST | Soft gate   |
| Weekend posts           | max 1 per weekend | Soft gate   |

---

## Gate Enforcement Definitions

### Hard Gates (block -- cannot override)

Hard gates prevent the action from completing. The skill must fix the issue before proceeding.

1. Post quality score < 75
2. AI detection score > 25
3. Hook strength < 7/10
4. Duplicate similarity > 60%
5. Hashtag count outside 3-5 range
6. Hook exceeds 15 words
7. No CTA present in post
8. No line breaks between paragraphs
9. Post scheduled within 20 hours of another post
10. More than 5 posts scheduled in a single week

### Soft Gates (warn -- can continue)

Soft gates log a warning and flag the post for review, but do not block scheduling.

1. Structure score < 70
2. Sentence longer than 15 words detected
3. Paragraph exceeds 2 lines
4. More than 2 emoji used
5. More than 1 all-caps word
6. CTA is generic (pattern-matched against bad CTA list)
7. CTA not in last 2 lines
8. More than 1 CTA in post
9. Post scheduled on Monday or Friday
10. Post scheduled outside 8-9 AM EST window
11. Weekend post when 1 weekend post already scheduled
