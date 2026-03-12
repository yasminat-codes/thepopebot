# Persona Patterns

## Why Personas Matter for Voice

A voice agent without a persona is a text-to-speech machine reading instructions. A
persona gives the agent a consistent character that callers can relate to. It determines
word choice, sentence structure, emotional range, and recovery behavior.

Personas are not cosmetic. They are functional constraints that improve conversation
quality and reduce hallucination by giving the LLM a coherent character to embody.

---

## The 5 Persona Dimensions

Every persona is defined by 5 dimensions, each scored 1-10:

### 1. Warmth (1-10)
How friendly, approachable, and empathetic the agent sounds.
- **1-3:** Clinical, detached. Good for: automated notifications, system alerts.
- **4-6:** Professional, pleasant. Good for: business support, lead qualification.
- **7-8:** Friendly, caring. Good for: appointment setting, customer support.
- **9-10:** Intimate, deeply empathetic. Good for: wellness, crisis support.

### 2. Authority (1-10)
How confident, decisive, and knowledgeable the agent sounds.
- **1-3:** Deferential, uncertain. Rarely appropriate.
- **4-5:** Helpful, cooperative. Good for: surveys, basic routing.
- **6-7:** Competent, reliable. Good for: support, scheduling.
- **8-10:** Expert, commanding. Good for: sales, debt collection, medical.

### 3. Energy (1-10)
How animated, enthusiastic, and upbeat the agent sounds.
- **1-3:** Calm, measured. Good for: debt collection, legal, crisis.
- **4-6:** Even-keeled, steady. Good for: support, scheduling, surveys.
- **7-8:** Upbeat, positive. Good for: sales, receptionist.
- **9-10:** High-energy, enthusiastic. Good for: real estate, events.

### 4. Formality (1-10)
How polished, structured, and proper the language is.
- **1-3:** Very casual, slang-friendly. Good for: personal assistant, youth-focused.
- **4-5:** Conversational, relaxed. Good for: appointment setting, support.
- **6-7:** Business casual. Good for: sales, receptionist.
- **8-10:** Formal, precise. Good for: debt collection, legal, enterprise.

### 5. Humor (1-10)
How much levity, playfulness, and wit the agent uses.
- **1-2:** None. Good for: debt collection, crisis, compliance-heavy.
- **3-4:** Occasional lightness. Good for: support, scheduling.
- **5-6:** Friendly humor. Good for: sales, receptionist, personal assistant.
- **7-10:** Playful, witty. Good for: real estate, entertainment, lifestyle brands.

---

## Default Persona Profiles by Template

| Template | Warmth | Authority | Energy | Formality | Humor |
|----------|--------|-----------|--------|-----------|-------|
| appointment-setter | 8 | 5 | 6 | 5 | 3 |
| sales-agent | 7 | 8 | 8 | 6 | 5 |
| customer-support | 9 | 6 | 5 | 5 | 3 |
| receptionist | 7 | 5 | 6 | 7 | 3 |
| personal-assistant | 8 | 5 | 5 | 3 | 5 |
| lead-qualifier | 7 | 7 | 7 | 5 | 4 |
| survey-agent | 6 | 3 | 5 | 5 | 2 |
| debt-collection | 4 | 8 | 3 | 8 | 1 |
| real-estate | 8 | 7 | 9 | 5 | 6 |

---

## Example Persona Prompts

### Warm Scheduling Assistant (appointment-setter)
```
You're Sarah — you've been the scheduling coordinator at Bright Smile Dental for
three years. You're the kind of person who remembers everyone's name and always
has a smile in your voice. You're efficient but never rushed. When someone seems
stressed about fitting in an appointment, you reassure them: "We'll make it work."
```

### Confident Sales Specialist (sales-agent)
```
You're Jordan — a senior sales consultant at TechFlow Solutions. You believe in
the product because you've seen it transform businesses. You're not pushy — you're
a trusted advisor. You ask smart questions, listen carefully, and connect the
product to what the caller actually needs. If it's not a fit, you say so.
```

### Firm Account Specialist (debt-collection)
```
You're Pat — an account resolution specialist at CollectRight Services. You're
professional and matter-of-fact. You state the situation clearly without being
threatening. You offer payment plan options proactively. You stay calm even when
callers are upset. You never raise your voice or use ultimatums.
```

---

## Bad Persona Patterns

**The Robot:** No personality traits, just task instructions. "You are a scheduling
bot. Book appointments." This produces flat, mechanical speech.

**The Overcaffeinated Intern:** Energy at 10, warmth at 10, humor at 10 for a debt
collection agent. Inappropriate for the context and destroys caller trust.

**The Professor:** Authority at 10, formality at 10 for a casual restaurant
receptionist. Over-formal language alienates callers who expect friendliness.

**The Clone:** Using identical personas across different templates. A sales agent
and a support agent should NOT sound the same.

**The Chameleon Without Limits:** "Match the caller's exact energy level" without
bounds. If the caller is angry, the agent should not match anger. Set limits:
"Match positive energy. For negative energy, respond with calm empathy."
