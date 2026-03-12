# State-Based Flows

## What Are States in Retell AI

States are Retell's conversation flow engine. Instead of one giant prompt, you break
the conversation into phases.

> **2026 Update:** Retell now supports Flex Mode for flows under 20 nodes. See [FLEX-MODE-GUIDE.md](FLEX-MODE-GUIDE.md) for when to use Flex Mode vs Traditional States. Global Nodes are now available for always-accessible states (transfer, repeat, end). Each phase (state) has its own focused prompt, its own
tools, and explicit transitions to other states.

The LLM sees: the `general_prompt` (shared across all states) + the current state's
`prompt`. This means persona, tone, and forbidden phrases go in `general_prompt`,
while task-specific instructions go in the state prompt.

---

## State Object Format

```json
{
  "name": "state_name",
  "prompt": "Short, focused instructions for this phase (3-5 sentences max)",
  "tools": [
    {
      "type": "custom_tool",
      "name": "tool_name",
      "description": "What this tool does"
    }
  ],
  "transitions": [
    {
      "to": "next_state_name",
      "condition": "Specific, observable trigger for this transition",
      "description": "Human-readable explanation"
    }
  ]
}
```

### Rules for State Objects

- **name**: lowercase, hyphenated. E.g., `greeting`, `collect-info`, `book-appointment`.
- **prompt**: 3-5 sentences. The shorter, the better. States constrain focus.
- **tools**: Only the tools needed in THIS state. Booking tools in the booking state, not greeting.
- **transitions**: Each transition needs a `to` (target state name), a `condition` (when to move),
  and a `description` (human explanation). Conditions must be specific and observable.

---

## When to Use States

**Use states when:**
- The conversation has 3+ distinct phases (greeting, discovery, action, closing)
- Different phases need different tools (search in discovery, book in action)
- You need to prevent the agent from jumping ahead (no pitching before qualifying)
- The conversation has branching logic (qualified leads get pitch, unqualified get redirect)
- You want to reduce hallucination by constraining what the agent focuses on

**Skip states when:**
- The conversation is freeform (personal assistant, general Q&A)
- There are fewer than 3 phases
- The agent needs flexibility to jump between topics
- States would overcomplicate a simple interaction

---

## Flow Pattern 1: Linear (A -> B -> C -> D)

Simplest pattern. Each state leads to exactly one next state.

**Best for:** Surveys, scripted interviews, onboarding calls.

```json
[
  {
    "name": "intro",
    "prompt": "Introduce yourself and explain this is a quick customer satisfaction survey. Ask if they have 3 minutes.",
    "tools": [],
    "transitions": [
      {"to": "questions", "condition": "Caller agrees to participate", "description": "Start survey"}
    ]
  },
  {
    "name": "questions",
    "prompt": "Ask the survey questions one at a time. Questions: 1) How would you rate your recent visit? 2) What did you enjoy most? 3) What could we improve? 4) Would you recommend us? 5) Any other feedback? Record each answer before moving to the next question.",
    "tools": [],
    "transitions": [
      {"to": "wrap-up", "condition": "All 5 questions have been answered", "description": "Survey complete"}
    ]
  },
  {
    "name": "wrap-up",
    "prompt": "Thank the caller for their time and feedback. Mention their responses will help improve service. Say goodbye warmly.",
    "tools": [],
    "transitions": []
  }
]
```

---

## Flow Pattern 2: Branching (A -> B -> C1 or C2)

Path depends on caller answers. The agent goes to different states based on what
it learns during discovery.

**Best for:** Sales qualification, lead routing, tiered support.

```json
[
  {
    "name": "greeting",
    "prompt": "Greet the caller. Introduce yourself as Jordan from TechFlow Solutions. Ask if they have a minute to chat about their business needs.",
    "tools": [],
    "transitions": [
      {"to": "qualification", "condition": "Caller agrees to continue", "description": "Begin qualification"}
    ]
  },
  {
    "name": "qualification",
    "prompt": "Ask qualification questions: 1) What is your company size? 2) What tools do you currently use? 3) What is your biggest pain point? 4) What is your timeline for a decision? 5) What is your budget range?",
    "tools": [],
    "transitions": [
      {"to": "pitch", "condition": "Company has 10+ employees AND has a timeline within 6 months AND budget is $500+/month", "description": "Qualified lead — pitch the product"},
      {"to": "nurture", "condition": "Caller does not meet qualification criteria", "description": "Not ready — nurture"}
    ]
  },
  {
    "name": "pitch",
    "prompt": "Present TechFlow's solution tailored to their specific pain point. Highlight the relevant case study. Offer a demo. Focus on ROI and timeline to value.",
    "tools": [
      {"type": "custom_tool", "name": "schedule_demo", "description": "Book a product demo"}
    ],
    "transitions": [
      {"to": "closing", "condition": "Caller agrees to demo or wants to proceed", "description": "Close the deal"},
      {"to": "closing", "condition": "Caller declines after hearing the pitch", "description": "Graceful close"}
    ]
  },
  {
    "name": "nurture",
    "prompt": "Acknowledge their situation. Offer to send helpful resources by email. Ask if they'd like a check-in call in a few months. Be genuinely helpful, not salesy.",
    "tools": [
      {"type": "custom_tool", "name": "send_resources", "description": "Email relevant case studies and guides"}
    ],
    "transitions": [
      {"to": "closing", "condition": "Resources offered and follow-up discussed", "description": "Wrap up nurture"}
    ]
  },
  {
    "name": "closing",
    "prompt": "Summarize what was discussed. Confirm any next steps (demo booking, resources sent, follow-up call). Thank them for their time. Say goodbye naturally.",
    "tools": [],
    "transitions": []
  }
]
```

---

## Flow Pattern 3: Looping (A -> B -> C -> back to B)

Allows the conversation to revisit a state when the first attempt does not succeed.

**Best for:** Appointment setting (first slot unavailable), data collection (missing info),
troubleshooting (first fix didn't work).

```json
[
  {
    "name": "greeting",
    "prompt": "Greet the caller warmly. Introduce yourself as Riley from Bright Smile Dental. Ask what they need — scheduling, rescheduling, or information.",
    "tools": [],
    "transitions": [
      {"to": "collect-info", "condition": "Caller wants to schedule or reschedule", "description": "Start scheduling"},
      {"to": "general-help", "condition": "Caller wants general information", "description": "Answer questions"}
    ]
  },
  {
    "name": "collect-info",
    "prompt": "Collect: 1) Type of appointment (cleaning, filling, consultation, etc.) 2) Preferred date and time 3) Patient name 4) Whether they are a new or returning patient. Ask one question at a time.",
    "tools": [],
    "transitions": [
      {"to": "book-appointment", "condition": "All required info collected: appointment type, date/time preference, patient name, and new/returning status", "description": "Attempt booking"}
    ]
  },
  {
    "name": "book-appointment",
    "prompt": "Check availability for the requested slot. If available, confirm the booking. If not available, suggest the 2-3 nearest alternatives and ask the caller to pick one.",
    "tools": [
      {"type": "custom_tool", "name": "check_availability", "description": "Check calendar for open slots"},
      {"type": "custom_tool", "name": "create_booking", "description": "Book the appointment"}
    ],
    "transitions": [
      {"to": "closing", "condition": "Appointment is confirmed and booked", "description": "Booking successful"},
      {"to": "collect-info", "condition": "No suitable slot found and caller wants to try different dates", "description": "Try different dates"}
    ]
  },
  {
    "name": "closing",
    "prompt": "Confirm appointment details: date, time, type, and any preparation instructions. Ask if they need anything else. Say goodbye warmly.",
    "tools": [],
    "transitions": [
      {"to": "collect-info", "condition": "Caller wants to schedule another appointment", "description": "Schedule another"},
      {"to": "general-help", "condition": "Caller has a question before hanging up", "description": "Answer question"}
    ]
  },
  {
    "name": "general-help",
    "prompt": "Answer common questions about services, hours, location, insurance accepted, and parking. Keep answers brief and helpful. If the question is too complex, offer to transfer to the office manager.",
    "tools": [],
    "transitions": [
      {"to": "collect-info", "condition": "Caller wants to schedule an appointment", "description": "Start scheduling"},
      {"to": "closing", "condition": "Question answered and caller is satisfied", "description": "Wrap up"}
    ]
  }
]
```

---

## State Design Best Practices

1. **Keep state prompts under 500 characters.** The state constrains focus — it should
   not be a complete prompt by itself. Shared behavior belongs in `general_prompt`.

2. **One responsibility per state.** A state named `collect-info-and-book` is trying to
   do two things. Split into `collect-info` and `book-appointment`.

3. **Transition conditions must be observable.** Bad: "When appropriate." Good: "When the
   caller has provided their name, preferred date, and appointment type."

4. **Always include backward transitions.** Callers change their mind. If someone is in
   the booking state and says "actually, wait — can I ask about your hours first?",
   the flow needs a path back.

5. **Terminal states have empty transitions.** The last state (usually `closing`) has
   `"transitions": []`. The call ends naturally or the agent says goodbye.

6. **Limit to 3-5 states for most agents.** If you have 8+ states, the flow is probably
   over-engineered. Consider merging states or using conditional logic within a state
   instead of splitting into separate states.

---

## When States Reduce Hallucination

States reduce hallucination by limiting the LLM's scope. In a single-prompt sales agent,
the LLM might jump to pitching before qualifying the caller. With states, the qualification
state has no access to the pitch content — the LLM is physically constrained.

This matters most when:
- The agent must follow a specific sequence (regulatory compliance, scripts)
- The agent has access to tools that should only be used at certain points
- The conversation has high stakes (debt collection, medical intake)

## When States Overcomplicate

States add complexity. For a personal assistant or general receptionist where the caller
might ask anything in any order, states create friction. The agent gets stuck in a state
when the caller wants to talk about something else.

If the conversation is naturally freeform, use a rich `general_prompt` with all 8 sections
and skip the state machine entirely.

## Per-Node LLM Selection (Cost Optimization)

Assign different LLM models per node to balance cost and quality:

| Node Type | Recommended Model | Reasoning |
|-----------|------------------|-----------|
| Greeting / opening | gpt-4.1-nano | Simple, scripted — cheap |
| Routing / intent detection | gpt-4.1-mini | Light reasoning needed |
| Data collection | gpt-4.1-mini | Structured, predictable |
| Complex reasoning / objections | gpt-4.1 or claude-4.5-sonnet | Full intelligence needed |
| Closing / farewell | gpt-4.1-nano | Simple, scripted — cheap |

Cost impact: Using nano for simple nodes saves 60-80% on those turns.
