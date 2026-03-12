# Pause Timing Guide

## Overview

Pauses in Retell AI voice agents are controlled through two mechanisms:
1. **Dash patterns in the prompt** -- Physical pauses encoded as dashes
2. **responsiveness parameter** -- Controls overall response speed

## Dash Patterns

Dashes in the agent's prompt text or knowledge base create spoken pauses:

| Pattern | Duration | Use Case |
|---------|----------|----------|
| `-` | Short pause (~0.3s) | Between list items, slight breath |
| `--` | Medium pause (~0.6s) | After questions, between thoughts |
| `---` | Long pause (~1.0s) | Before important info, topic shifts |
| `----` | Extended pause (~1.5s) | Dramatic effect, long thinking |

### Examples

**Short pause (list delivery):**
```
We offer three plans - Basic - Professional - and Enterprise.
```

**Medium pause (after question):**
```
Could you give me your email address? -- I'll make sure to send that over.
```

**Long pause (before important info):**
```
After reviewing your account --- I can see that your payment is overdue.
```

**Thinking pause:**
```
Let me check on that for you ---- Okay, I found your reservation.
```


## Responsiveness Parameter

- **Type:** float, range [0, 1]
- **Default:** 1
- **Effect:** Controls how quickly the agent responds after the caller stops speaking

| Value | Behavior | Feel |
|-------|----------|------|
| 1.0 | Immediate response | Fast, efficient, slightly robotic |
| 0.9 | Very brief delay | Professional, attentive |
| 0.8 | Short delay | Natural conversational pace |
| 0.7 | Noticeable delay | Thoughtful, considering |
| 0.6 | Moderate delay | Deliberate, careful |
| 0.5 | Longer delay | Slow, contemplative |
| 0.3-0.4 | Long delay | Very slow, may feel sluggish |

### By Humanization Level

| Level | responsiveness | Perceived Effect |
|-------|---------------|------------------|
| 1-2 | 1.0 | Instant, no delay |
| 3-4 | 0.9 | Barely perceptible delay |
| 5-6 | 0.8 | Natural thinking time |
| 7-8 | 0.6-0.7 | Noticeable thinking |
| 9-10 | 0.4-0.5 | Slow, deliberate |


## When to Use Pauses

### After Questions
Give the caller a moment before continuing:
```
What time works best for you? --
```

### Before Important Information
Build slight anticipation:
```
Your total comes to --- forty-two dollars and fifty cents.
```

### During Topic Transitions
Mark the shift between subjects:
```
Great, I've got that noted. --- Now, let me ask about your availability.
```

### Thinking Moments
When the agent is "looking something up":
```
Let me pull up your account --- okay, I can see your order here.
```

### After Empathetic Statements
Let emotional moments breathe:
```
I'm sorry to hear that. -- Let me see what I can do to help.
```


## Interruption Sensitivity

Related to pauses, `interruption_sensitivity` controls how easily the caller can
interrupt the agent mid-speech:

- **Type:** float, range [0, 1]
- **Default:** 1

| Value | Behavior |
|-------|----------|
| 1.0 | Very sensitive, agent stops immediately when caller speaks |
| 0.7-0.8 | Natural sensitivity, agent stops after brief overlap |
| 0.5 | Moderate, agent may finish a phrase before stopping |
| 0.3 | Low sensitivity, agent tends to finish its point |

### By Humanization Level

| Level | interruption_sensitivity |
|-------|------------------------|
| 1-3 | 0.8-1.0 |
| 4-6 | 0.7-0.8 |
| 7-8 | 0.6-0.7 |
| 9-10 | 0.5-0.6 |


## Combining Pauses with Fillers

The most natural speech combines pauses and fillers:

```
Hmm -- let me check on that -- okay so -- I see your appointment is Thursday at 2 PM.
```

This creates the feeling of a person actually thinking and looking things up.
