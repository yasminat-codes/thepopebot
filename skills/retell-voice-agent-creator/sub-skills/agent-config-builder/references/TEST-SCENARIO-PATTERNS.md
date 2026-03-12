# Test Scenario Patterns

Template-specific test scenario patterns used by
[generate-tests.py](../scripts/generate-tests.py) to create tailored test suites.

---

## Scenario Structure

Each generated scenario follows this format:

```json
{
  "name": "scenario_name",
  "category": "happy_path|edge_case|pronunciation|emotional",
  "description": "What this scenario tests",
  "caller_persona": "Description of the caller's personality and situation",
  "expected_flow": ["Step 1", "Step 2", "Step 3"],
  "success_criteria": ["Criterion 1", "Criterion 2"],
  "scoring_dimensions": {
    "pronunciation_accuracy": 8,
    "response_latency": 7,
    "conversational_tone": 9,
    "interruption_handling": 6,
    "fallback_behavior": 7
  }
}
```

## Scoring Dimensions

| Dimension | Weight | 1-3 (Poor) | 4-6 (Acceptable) | 7-10 (Good) |
|-----------|--------|------------|-------------------|-------------|
| Pronunciation Accuracy | 20% | Multiple mispronunciations | Minor issues | All terms correct |
| Response Latency | 20% | Long pauses, awkward timing | Occasional delays | Natural pacing |
| Conversational Tone | 25% | Robotic, off-brand | Adequate but flat | Natural, on-brand |
| Interruption Handling | 15% | Ignores or crashes | Handles awkwardly | Graceful recovery |
| Fallback Behavior | 20% | No response or wrong topic | Generic redirect | Helpful redirect |

## Template: appointment-setter

### Happy Path Scenarios

**1. Straightforward booking**
- Persona: Friendly caller who knows exactly what they want
- Flow: Greeting -> provide name, date, time, service -> confirm -> end
- Success: Appointment booked, all details captured correctly

**2. Caller needs help choosing a time**
- Persona: Caller knows the service but is flexible on scheduling
- Flow: Greeting -> state service -> discuss availability -> pick time -> confirm
- Success: Agent suggests times, caller picks one, booking confirmed

**3. Returning patient**
- Persona: Existing patient calling for follow-up
- Flow: Greeting -> "I need a follow-up" -> provide name -> confirm details -> end
- Success: Recognizes follow-up request, collects minimal info needed

**4. Caller books then asks a question**
- Persona: Books appointment then asks about preparation
- Flow: Greeting -> booking flow -> "What should I bring?" -> answer -> end
- Success: Handles both booking and FAQ in one call

### Edge Case Scenarios

**5. Caller changes mind mid-booking**
- Persona: Starts booking a cleaning then switches to consultation
- Flow: Greeting -> start booking cleaning -> "Actually, can I do a consultation?" -> restart
- Success: Handles service change without losing other details

**6. Caller provides incomplete info**
- Persona: Gives name and date but forgets time
- Flow: Greeting -> partial info -> agent prompts for missing time -> complete
- Success: Agent identifies and requests missing information

**7. Off-topic question**
- Persona: Asks about something unrelated to the business
- Flow: Greeting -> off-topic question -> redirect -> back to booking
- Success: Politely redirects without being rude

### Pronunciation Scenarios

**8. Business name and doctor names**
- Persona: Asks "Is Dr. Patel available?" using the business name
- Success: Pronounces all proper nouns correctly

**9. Service-specific terminology**
- Persona: Uses dental terms (periodontal, endodontic, etc.)
- Success: Pronounces medical terms correctly

### Emotional Scenarios

**10. Anxious first-time caller**
- Persona: Nervous about visiting, hesitant speech
- Flow: Greeting -> caller expresses anxiety -> empathetic response -> gentle booking
- Success: Agent uses empathetic tone, patient pacing

**11. Rushed caller**
- Persona: In a hurry, speaks fast, wants quick booking
- Flow: Greeting -> rapid info dump -> confirm -> end quickly
- Success: Matches pace, efficient confirmation

## Template: sales-outbound

### Happy Path

**1. Interested prospect**
- Persona: Open to hearing the pitch, asks questions
- Flow: Intro -> pitch -> questions -> express interest -> next steps
- Success: Interest captured, lead score 7+

**2. Warm lead follow-up**
- Persona: Previously expressed interest, expecting the call
- Flow: Intro -> reference previous contact -> updated pitch -> close
- Success: Moves to next stage

### Edge Cases

**3. Objection handler**
- Persona: Interested but has price objections
- Flow: Intro -> pitch -> "too expensive" -> handle objection -> next steps
- Success: Addresses objection professionally

**4. Wrong number**
- Persona: Not the intended contact
- Flow: Intro -> "You have the wrong person" -> apologize -> end
- Success: Graceful exit, no pushiness

**5. Do-not-call request**
- Persona: Immediately asks to be removed from list
- Flow: Intro -> "Take me off your list" -> acknowledge -> end
- Success: Respects request immediately

### Pronunciation / Emotional

**6. Company name mention**
- Success: Pronounces company and product names correctly

**7. Skeptical prospect**
- Persona: Suspicious, challenges claims
- Success: Stays calm, provides facts, does not get defensive

## Template: customer-support

### Happy Path

**1. Simple question**
- Persona: Has a straightforward question about hours or services
- Flow: Greeting -> question -> answer -> confirm satisfied -> end
- Success: Question answered, issue_resolved = true

**2. Multi-step troubleshooting**
- Persona: Has a technical issue requiring several steps
- Flow: Greeting -> describe issue -> step 1 -> step 2 -> resolved -> end
- Success: Walks through steps patiently

### Edge Cases

**3. Angry caller**
- Persona: Frustrated with repeated issues, raised voice
- Flow: Greeting -> vent frustration -> empathize -> solve -> end
- Success: De-escalates without being dismissive

**4. Transfer needed**
- Persona: Issue requires human specialist
- Flow: Greeting -> describe complex issue -> attempt help -> transfer
- Success: Recognizes limits, transfers cleanly

**5. Confused caller**
- Persona: Not sure what their problem is, describes symptoms vaguely
- Flow: Greeting -> vague description -> clarifying questions -> identify issue -> solve
- Success: Patient questioning, correct diagnosis

### Pronunciation / Emotional

**6. Technical terms**
- Success: Pronounces product names and technical terms correctly

**7. Tearful caller**
- Persona: Upset about account issue affecting them personally
- Success: Shows genuine empathy, does not rush

## Retell Simulation Testing (Batch Testing)

Run 20-50 automated conversation simulations before going live.

**Setup in Dashboard:**
1. Navigate to Testing -> Simulation
2. Create synthetic caller personas:
   - **Happy Path**: Cooperative caller, clear intent, standard flow
   - **Objector**: Pushes back on price, timing, or solution
   - **Angry Caller**: Starts frustrated, escalates if not handled well
   - **Confused Caller**: Unclear intent, multiple topic switches
   - **Rushed Caller**: Short responses, wants quick resolution
3. Define success criteria per persona:
   - Happy Path: reaches intended outcome in <3 minutes
   - Objector: handled without escalation in >80% of runs
   - Angry: de-escalated and resolved or transferred appropriately
4. Run batch of 20+ per persona
5. Review transcripts for state transition accuracy, hallucinations, pronunciation errors

**Pass/Fail Thresholds:**
- Happy Path success rate: >=95%
- Objector handled without escalation: >=80%
- Angry de-escalation: >=70%
- Confused resolved without 3+ clarification loops: >=75%
- Rushed resolved in <90 seconds: >=85%
