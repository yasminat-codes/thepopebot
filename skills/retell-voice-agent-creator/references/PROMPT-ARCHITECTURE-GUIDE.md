# Prompt Architecture Guide

Research-validated prompt architecture from OpenAI, Retell, and Vapi for building
voice agent system prompts. This is the correct structure.

## Canonical Prompt Structure

```
## Identity
[Name, role, company, 1-sentence personality]

## Style Guardrails
[Tone: 3-5 adjectives]
[What to avoid: jargon, monologues, robotic language]
[Contractions always]

## Response Guidelines
[NEVER speak more than 2 sentences at a time]
[NEVER type a number — always spell it in words]
[NEVER reference visual elements — this is a phone call]
[Ask one question at a time]
[Confirm understanding by paraphrasing]
[After asking a question — wait for user response]

## Task Instructions
[Specific to the agent's job — numbered steps]
[Insert <wait for user response> between steps]

## Tools
[For each tool: name, exact trigger condition, preamble phrase to say first]
[READ operations: proactive allowed]
[WRITE operations: require verbal confirmation first]

## Objection Handling
[Common objections with response patterns]

## Escalation
[When to transfer to human: after 2 failed attempts, explicit request, safety concern]
[Transfer preamble: "Let me connect you with someone who can help with that"]

## Forbidden
[Topics, phrases, behaviors — use caps: NEVER say "As an AI"]
```

## The 500-Token Rule

Keep system prompts under 500 tokens for optimal latency.

- Every 100 extra tokens adds approximately 50ms latency
- Move detailed knowledge to dynamic context injection per call
- The system prompt defines behavior; the dynamic context provides data
- If a prompt exceeds 500 tokens, extract knowledge/FAQ content into a
  Knowledge Base or dynamic variables

## Critical Prompt Instructions

Always include these in every voice agent prompt:

```
If the user says "hold on", "one second", or similar — output NO_RESPONSE_NEEDED and wait.
```

```
DO NOT repeat the caller's answer back to them. Always proceed to the next step.
```

```
Before calling any function, say a brief phrase: "Let me check that for you" or "One moment."
```

```
NEVER ask more than one question per turn.
```

```
DO NOT sound like you are reading from a script.
```

## Caps Emphasis

Models respond strongly to capitalized directives. Use uppercase for non-negotiable
rules throughout the prompt:

- `DO NOT` — for prohibited actions
- `NEVER` — for absolute restrictions
- `ALWAYS` — for mandatory behaviors
- `MUST` — for required conditions

Lowercase instructions are treated as suggestions. Uppercase instructions are
treated as rules. Use this intentionally.

## Deliberate Imperfection Protocol

Perfect speech sounds robotic. Controlled imperfection sounds human.

**Filler words:**
- 1 filler word per 4-5 sentences (not every sentence)
- Too many fillers sound nervous; too few sounds scripted

**Self-corrections:**
- Self-correct once per minute maximum
- Pattern: "actually, scratch that — " followed by corrected statement
- Makes the agent sound like it's thinking in real time

**Discourse markers for topic transitions:**
- "so," "now," "anyway," "here's the thing"
- Use at natural topic boundaries, not mid-thought

**Sample phrase bank for acknowledgments:**
- "makes sense"
- "got it"
- "oh"
- "hmm"
- "right"
- "sure"
- "okay"

Vary these — never use the same acknowledgment twice in a row.

## Tool Call Preamble Pattern

Every tool call needs a spoken preamble so the caller does not hear silence.

**Pattern:**
```
Tool: check_availability
Trigger: when the caller asks about available times
Preamble: "Let me check what we have open"
```

```
Tool: book_appointment
Trigger: when the caller confirms a time slot
Preamble: "Great, let me get that booked for you"
Confirm before write: YES — "Just to confirm, [date] at [time] — should I go ahead?"
```

**Rules:**
- READ operations (lookups, searches): preamble only, no confirmation needed
- WRITE operations (bookings, updates, payments): require verbal confirmation first
- NEVER call a tool silently — always say something first

## Objection Handling Pattern

Structure objections as condition-response pairs:

```
## Objection Handling

If the caller says they're not interested:
"I totally understand. Just so you know, [one-sentence value prop]. Would it help
if I sent over some quick info you could look at on your own time?"

If the caller says it's too expensive:
"That's fair. Most of our clients felt the same way initially. What they found
was [specific ROI point]. Would it help to walk through the numbers?"

If the caller says they need to think about it:
"Of course, take your time. Can I send a quick summary to your email so you have
everything in one place? What's the best email for you?"
```

## Escalation Rules

Always include an escalation path:

```
## Escalation

Transfer to a human agent when:
- The caller explicitly asks to speak to a person
- You have failed to resolve the same issue after 2 attempts
- The caller expresses frustration or anger that is escalating
- A safety or legal concern arises
- The request is outside your defined scope

Transfer preamble (ALWAYS say before transferring):
"Let me connect you with someone who can help with that. One moment."

NEVER hang up without offering a transfer option first.
```

## Dynamic Context Injection

Instead of bloating the system prompt with data, inject context per call:

```json
{
  "dynamic_variables": {
    "caller_name": "Sarah",
    "account_status": "active",
    "last_interaction": "called about billing on March 10"
  }
}
```

Reference these in the prompt:
```
The caller's name is {{caller_name}}. Their account is {{account_status}}.
Their last interaction: {{last_interaction}}.

Greet them by name. Do not ask for information you already have.
```

This keeps the system prompt short and the agent context-aware.
