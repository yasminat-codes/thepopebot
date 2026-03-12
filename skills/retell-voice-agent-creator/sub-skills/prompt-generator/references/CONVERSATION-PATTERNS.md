# Conversation Patterns

## The 4 Conversation Phases

Every voice agent conversation, regardless of template, follows four fundamental
phases. Even freeform conversations hit these phases — the difference is whether
you enforce them with states or let them flow naturally.

---

## Phase 1: Opening

**Purpose:** Establish identity, build rapport, set expectations.

**Duration:** 5-15 seconds (1-2 agent turns).

**What happens:**
- Agent introduces self and company
- Agent sets the context for the call (or asks the caller's reason)
- Caller understands who they are talking to and what the agent can do

**Patterns:**

Outbound (agent calls the person):
```
"Hey {name}, this is {agent_name} from {company}. Got a minute?"
"Hi {name}, {agent_name} here from {company}. I'm calling about {reason}."
```

Inbound (person calls the agent):
```
"Hi, thanks for calling {company}. I'm {agent_name} — how can I help?"
"Good morning, {company}, this is {agent_name}. What can I do for you?"
```

User-speaks-first (begin_message = ""):
```
[Agent waits silently]
Caller: "Hi, I'm calling about..."
Agent: "Hey! Thanks for calling. I'm {agent_name}. Let me help with that."
```

**Rules:**
- Keep the opening under 2 sentences for outbound calls
- Never start with a long explanation of what the agent can do
- For outbound calls, always ask permission: "Got a minute?" or "Is this a good time?"
- Match formality to the template: casual for personal assistant, formal for debt collection

---

## Phase 2: Discovery

**Purpose:** Understand the caller's need. Gather information required for the next phase.

**Duration:** 30 seconds to 3 minutes depending on complexity.

**What happens:**
- Agent asks targeted questions (one at a time)
- Agent confirms understanding before proceeding
- Agent identifies which action path to take

**Patterns:**

Single-question discovery (receptionist):
```
Agent: "What can I help you with today?"
Caller: "I need to schedule an appointment."
Agent: "Got it — let me get you set up."
```

Multi-question discovery (sales qualifier):
```
Agent: "Tell me about your current setup — what tools are you using?"
Caller: [answers]
Agent: "Interesting. And roughly how many people on your team?"
Caller: [answers]
Agent: "Got it. And what's the biggest headache with your current system?"
```

Confirmation pattern:
```
Agent: "So just to make sure I've got this right — you're looking for a
cleaning appointment for next Tuesday, preferably morning. That right?"
```

**Rules:**
- Ask ONE question at a time. Never stack: "What's your name and when would you like to come in and is this your first visit?"
- Acknowledge each answer before asking the next question: "Got it" or "Perfect"
- Use the confirmation pattern before transitioning to the action phase
- If the caller gives partial info, follow up: "And what time works best?"
- If the caller goes off-topic, gently redirect: "I can help with that too — but first, let me finish getting you scheduled."

---

## Phase 3: Action

**Purpose:** Execute the primary task — book the appointment, give the answer, make the pitch, record the response.

**Duration:** 30 seconds to 2 minutes.

**What happens:**
- Agent performs the core task using available tools
- Agent communicates results to the caller
- Agent handles complications (slot unavailable, question too complex, caller objects)

**Patterns:**

Successful action:
```
Agent: "I've got you booked for Tuesday at 10am with Dr. Chen. You'll get a
confirmation text shortly."
```

Action with complication:
```
Agent: "Hmm, Tuesday morning is full. I've got openings Tuesday at 2pm or
Wednesday at 9am — which works better?"
```

Action requiring transfer:
```
Agent: "That's a really specific question about your insurance coverage. Let me
transfer you to someone who can look that up — one sec."
```

**Rules:**
- Communicate what you're doing: "Let me check that for you" (not just silence)
- State results clearly and concisely
- If the action fails, offer alternatives immediately — never just say "I can't do that"
- For tools that take time, use filler: "One sec, I'm pulling that up..."

---

## Phase 4: Closing

**Purpose:** Summarize, confirm next steps, end the call naturally.

**Duration:** 10-20 seconds.

**What happens:**
- Agent summarizes what was accomplished
- Agent confirms any follow-up actions
- Agent offers chance for additional questions
- Natural goodbye

**Patterns:**

Quick close:
```
Agent: "You're all set for Tuesday at 10am. Anything else?"
Caller: "Nope, that's it."
Agent: "Great — see you Tuesday! Bye."
```

Summary close (for complex interactions):
```
Agent: "Okay, so to recap: I've booked your cleaning for Tuesday at 10am with
Dr. Chen. You'll get a text confirmation, and remember to bring your insurance
card. Anything else I can help with?"
```

Handoff close:
```
Agent: "I'm transferring you to our billing team now. They'll have all the info
from our chat. Thanks for calling, and have a great day!"
```

**Rules:**
- Always offer "anything else?" before closing — but say it casually, not robotically
- Keep the summary to one sentence for simple calls
- Use 2-3 sentences for complex calls with multiple action items
- End naturally: "Take care!" or "Have a great day!" — not "Thank you for contacting us."

---

## Handling Mid-Conversation Topic Changes

Callers do not follow scripts. They will ask about insurance during the booking phase,
switch from scheduling to billing, or go off-topic entirely.

**Pattern: Acknowledge and Redirect**
```
Caller: "Oh, and actually, can you tell me about your whitening options?"
Agent: "Yeah, we do offer whitening! I can give you a quick rundown after we
finish getting your appointment set. Sound good?"
```

**Pattern: Quick Answer and Return**
```
Caller: "Wait, what are your hours again?"
Agent: "We're open Monday through Friday, 8 to 5. So, back to your
appointment — did you say Tuesday works?"
```

**Pattern: Graceful Off-Topic Deflection**
```
Caller: "Can you recommend a good restaurant nearby?"
Agent: "Ha, I wish I could help with that! I'm really just the scheduling
expert here. But let's get your appointment locked in — what day works?"
```

**Rules:**
- Never ignore the topic change — always acknowledge it
- If the answer is quick (hours, location), answer it and return to the flow
- If the answer is complex, park it: "Let me get you scheduled first, then we can talk about that"
- In state-based flows, topic changes can trigger backward transitions (e.g., ACTION back to DISCOVERY)
