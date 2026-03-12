#!/usr/bin/env python3
"""
generate-tests.py — Generate test scenarios for a Retell AI voice agent.

Usage:
    python3 generate-tests.py \
        --agent-config agent-config.json \
        --template appointment-setter \
        [--output test-scenarios.json]
"""

import argparse
import json
import sys

# ── Scenario templates by agent type ──────────────────────────────────────

SCENARIO_TEMPLATES = {
    "appointment-setter": {
        "happy_path": [
            {
                "name": "straightforward_booking",
                "description": "Caller knows exactly what they want and books immediately",
                "caller_persona": "Friendly, organized caller who has all information ready",
                "expected_flow": [
                    "Agent greets caller",
                    "Caller states they want to book an appointment",
                    "Caller provides name, preferred date, time, and service",
                    "Agent confirms all details",
                    "Caller confirms, call ends"
                ],
                "success_criteria": [
                    "All details captured correctly",
                    "Appointment confirmed",
                    "Call duration under 3 minutes"
                ]
            },
            {
                "name": "needs_help_choosing_time",
                "description": "Caller is flexible on scheduling and needs suggestions",
                "caller_persona": "Easygoing caller who knows the service but not the date",
                "expected_flow": [
                    "Agent greets caller",
                    "Caller asks about availability",
                    "Agent suggests available times",
                    "Caller picks a time",
                    "Agent confirms booking"
                ],
                "success_criteria": [
                    "Agent offers time suggestions naturally",
                    "Booking completed successfully"
                ]
            },
            {
                "name": "returning_patient",
                "description": "Existing patient calling for a follow-up visit",
                "caller_persona": "Returning patient who knows the process",
                "expected_flow": [
                    "Agent greets caller",
                    "Caller says they need a follow-up",
                    "Agent collects minimal info",
                    "Booking confirmed"
                ],
                "success_criteria": [
                    "Recognizes follow-up context",
                    "Efficient interaction"
                ]
            },
        ],
        "edge_case": [
            {
                "name": "changes_mind_mid_booking",
                "description": "Caller switches service type during the booking process",
                "caller_persona": "Indecisive caller who changes from cleaning to consultation",
                "expected_flow": [
                    "Agent starts booking for cleaning",
                    "Caller says 'actually, can I do a consultation instead?'",
                    "Agent adjusts without losing other details",
                    "Booking completed with new service"
                ],
                "success_criteria": [
                    "Handles change gracefully",
                    "Retains name and date preference",
                    "No confusion or restart"
                ]
            },
            {
                "name": "incomplete_information",
                "description": "Caller provides partial info, agent must prompt for the rest",
                "caller_persona": "Distracted caller who gives name and date but forgets time",
                "expected_flow": [
                    "Caller provides partial details",
                    "Agent identifies missing fields",
                    "Agent asks for missing info",
                    "Caller provides, booking confirmed"
                ],
                "success_criteria": [
                    "Agent catches missing information",
                    "Prompts naturally, not robotically"
                ]
            },
            {
                "name": "off_topic_question",
                "description": "Caller asks about something unrelated to the business",
                "caller_persona": "Caller who asks about nearby parking or restaurants",
                "expected_flow": [
                    "Agent greets caller",
                    "Caller asks an off-topic question",
                    "Agent redirects politely",
                    "Caller returns to booking or ends call"
                ],
                "success_criteria": [
                    "Polite redirection without rudeness",
                    "Stays professional"
                ]
            },
        ],
        "pronunciation": [
            {
                "name": "business_and_doctor_names",
                "description": "Caller uses business name and staff names in conversation",
                "caller_persona": "Caller asking for a specific doctor by name",
                "expected_flow": [
                    "Caller mentions business name",
                    "Agent responds using business name correctly",
                    "Caller asks for specific doctor",
                    "Agent pronounces doctor name correctly"
                ],
                "success_criteria": [
                    "Business name pronounced correctly",
                    "Doctor names pronounced correctly"
                ]
            },
            {
                "name": "medical_terminology",
                "description": "Caller uses specific service terminology",
                "caller_persona": "Informed caller who uses technical terms",
                "expected_flow": [
                    "Caller requests specific procedure by name",
                    "Agent acknowledges using correct terminology"
                ],
                "success_criteria": [
                    "Technical terms pronounced correctly",
                    "Agent does not stumble on terminology"
                ]
            },
        ],
        "emotional": [
            {
                "name": "anxious_first_timer",
                "description": "Nervous caller who has anxiety about the visit",
                "caller_persona": "First-time caller with dental anxiety, hesitant speech",
                "expected_flow": [
                    "Caller expresses nervousness",
                    "Agent responds with empathy and reassurance",
                    "Agent gently guides through booking",
                    "Caller feels reassured"
                ],
                "success_criteria": [
                    "Empathetic tone used",
                    "Patient pacing, no rushing",
                    "Reassuring language"
                ]
            },
            {
                "name": "rushed_caller",
                "description": "Caller in a hurry who wants quick service",
                "caller_persona": "Time-pressed caller speaking rapidly",
                "expected_flow": [
                    "Caller dumps info quickly",
                    "Agent captures all details efficiently",
                    "Quick confirmation",
                    "Fast call end"
                ],
                "success_criteria": [
                    "Matches caller pace",
                    "No unnecessary small talk",
                    "All info captured despite speed"
                ]
            },
        ],
    },
    "sales-outbound": {
        "happy_path": [
            {
                "name": "interested_prospect",
                "description": "Prospect is open to hearing the pitch and asks questions",
                "caller_persona": "Curious prospect who engages with the pitch",
                "expected_flow": ["Intro", "Pitch", "Questions", "Interest expressed", "Next steps agreed"],
                "success_criteria": ["Interest captured", "Next steps scheduled", "Lead score 7+"]
            },
            {
                "name": "warm_lead_followup",
                "description": "Following up with a previously interested prospect",
                "caller_persona": "Prospect expecting the call based on prior conversation",
                "expected_flow": ["Intro with context", "Updated pitch", "Close attempt"],
                "success_criteria": ["References prior interaction", "Moves to next stage"]
            },
        ],
        "edge_case": [
            {
                "name": "price_objection",
                "description": "Prospect objects to pricing",
                "caller_persona": "Interested but budget-conscious prospect",
                "expected_flow": ["Pitch", "Objection raised", "Handle objection", "Outcome"],
                "success_criteria": ["Addresses objection professionally", "Does not get flustered"]
            },
            {
                "name": "wrong_number",
                "description": "Called the wrong person",
                "caller_persona": "Person who is not the intended contact",
                "expected_flow": ["Intro", "Wrong person identified", "Apologize", "End gracefully"],
                "success_criteria": ["Graceful exit", "No pushiness"]
            },
            {
                "name": "do_not_call_request",
                "description": "Prospect immediately wants to be removed from list",
                "caller_persona": "Annoyed person requesting removal",
                "expected_flow": ["Intro", "Removal request", "Acknowledge", "End"],
                "success_criteria": ["Respects request immediately", "No pushback"]
            },
        ],
        "pronunciation": [
            {
                "name": "company_product_names",
                "description": "Agent mentions company and product names",
                "caller_persona": "Any prospect",
                "expected_flow": ["Agent introduces company and product by name"],
                "success_criteria": ["All names pronounced correctly"]
            },
        ],
        "emotional": [
            {
                "name": "skeptical_prospect",
                "description": "Prospect challenges claims and is suspicious",
                "caller_persona": "Skeptical person who questions everything",
                "expected_flow": ["Pitch", "Challenge", "Fact-based response", "Outcome"],
                "success_criteria": ["Stays calm", "Provides facts", "Not defensive"]
            },
        ],
    },
    "customer-support": {
        "happy_path": [
            {
                "name": "simple_question",
                "description": "Caller has a straightforward question",
                "caller_persona": "Calm caller with a clear question",
                "expected_flow": ["Greeting", "Question asked", "Answer given", "Confirmed", "End"],
                "success_criteria": ["Question answered correctly", "issue_resolved = true"]
            },
            {
                "name": "multi_step_troubleshoot",
                "description": "Caller needs guided troubleshooting",
                "caller_persona": "Patient caller willing to follow instructions",
                "expected_flow": ["Greeting", "Issue described", "Step 1", "Step 2", "Resolved"],
                "success_criteria": ["Patient guidance", "Issue resolved"]
            },
        ],
        "edge_case": [
            {
                "name": "angry_caller",
                "description": "Frustrated caller who is upset about repeated issues",
                "caller_persona": "Angry, raised voice, wants immediate resolution",
                "expected_flow": ["Greeting", "Caller vents", "Empathize", "Solve", "Confirm"],
                "success_criteria": ["De-escalation", "Empathy shown", "Issue addressed"]
            },
            {
                "name": "transfer_needed",
                "description": "Issue requires a human specialist",
                "caller_persona": "Caller with a complex billing dispute",
                "expected_flow": ["Greeting", "Complex issue", "Attempt help", "Transfer"],
                "success_criteria": ["Recognizes limits", "Clean transfer", "Sets expectations"]
            },
            {
                "name": "confused_caller",
                "description": "Caller cannot clearly describe their problem",
                "caller_persona": "Uncertain caller with vague symptom descriptions",
                "expected_flow": ["Greeting", "Vague description", "Clarifying questions", "Identify", "Solve"],
                "success_criteria": ["Patient questioning", "Correct diagnosis"]
            },
        ],
        "pronunciation": [
            {
                "name": "product_technical_terms",
                "description": "Agent uses product names and technical terms",
                "caller_persona": "Any caller",
                "expected_flow": ["Agent mentions product and feature names"],
                "success_criteria": ["Correct pronunciation of all terms"]
            },
        ],
        "emotional": [
            {
                "name": "tearful_caller",
                "description": "Caller upset about an issue affecting them personally",
                "caller_persona": "Emotionally distressed caller",
                "expected_flow": ["Greeting", "Emotional explanation", "Empathy", "Solution"],
                "success_criteria": ["Genuine empathy", "Does not rush", "Supportive tone"]
            },
        ],
    },
}

# Default for templates not explicitly defined
DEFAULT_SCENARIOS = {
    "happy_path": [
        {
            "name": "standard_successful_call",
            "description": "Caller completes the primary flow successfully",
            "caller_persona": "Standard caller with clear intent",
            "expected_flow": ["Greeting", "Main interaction", "Successful outcome", "End"],
            "success_criteria": ["Primary goal achieved", "Natural conversation"]
        },
    ],
    "edge_case": [
        {
            "name": "unclear_intent",
            "description": "Caller is not sure what they need",
            "caller_persona": "Uncertain caller",
            "expected_flow": ["Greeting", "Vague request", "Clarification", "Redirect or help"],
            "success_criteria": ["Patient clarification", "Helpful response"]
        },
    ],
    "pronunciation": [
        {
            "name": "key_terms",
            "description": "Agent pronounces business-specific terms",
            "caller_persona": "Any caller",
            "expected_flow": ["Agent uses key terms in conversation"],
            "success_criteria": ["All terms pronounced correctly"]
        },
    ],
    "emotional": [
        {
            "name": "frustrated_caller",
            "description": "Caller who is frustrated and needs empathy",
            "caller_persona": "Frustrated caller",
            "expected_flow": ["Greeting", "Frustration expressed", "Empathy", "Resolution"],
            "success_criteria": ["Empathetic response", "Does not escalate"]
        },
    ],
}

SCORING_RUBRIC = {
    "dimensions": [
        {"name": "pronunciation_accuracy", "weight": 0.20, "description": "Business names and terms pronounced correctly"},
        {"name": "response_latency", "weight": 0.20, "description": "Appropriate pause lengths, no awkward delays"},
        {"name": "conversational_tone", "weight": 0.25, "description": "Natural, matches configured personality"},
        {"name": "interruption_handling", "weight": 0.15, "description": "Graceful response to caller interruptions"},
        {"name": "fallback_behavior", "weight": 0.20, "description": "Handles off-topic or unclear input gracefully"},
    ],
    "scale": "1-10 per dimension. 1-3 = poor, 4-6 = acceptable, 7-10 = good."
}


def generate_scenarios(template_name, agent_config):
    """Generate test scenarios for the given template."""
    templates = SCENARIO_TEMPLATES.get(template_name, DEFAULT_SCENARIOS)

    scenarios = []
    for category in ["happy_path", "edge_case", "pronunciation", "emotional"]:
        category_scenarios = templates.get(category, DEFAULT_SCENARIOS.get(category, []))
        for scenario in category_scenarios:
            scenario_entry = dict(scenario)
            scenario_entry["category"] = category
            # Add default scoring expectations
            scenario_entry["scoring_dimensions"] = {
                "pronunciation_accuracy": 8,
                "response_latency": 7,
                "conversational_tone": 8,
                "interruption_handling": 7,
                "fallback_behavior": 7,
            }
            # Adjust scores by category
            if category == "pronunciation":
                scenario_entry["scoring_dimensions"]["pronunciation_accuracy"] = 9
            elif category == "emotional":
                scenario_entry["scoring_dimensions"]["conversational_tone"] = 9
            elif category == "edge_case":
                scenario_entry["scoring_dimensions"]["fallback_behavior"] = 8
                scenario_entry["scoring_dimensions"]["interruption_handling"] = 8

            scenarios.append(scenario_entry)

    return scenarios


def main():
    parser = argparse.ArgumentParser(description="Generate test scenarios for Retell agent.")
    parser.add_argument("--agent-config", required=True, help="Path to agent-config.json")
    parser.add_argument("--template", required=True, help="Template name")
    parser.add_argument("--output", default="test-scenarios.json", help="Output file path")
    args = parser.parse_args()

    try:
        with open(args.agent_config, "r") as f:
            agent_config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot read {args.agent_config}: {e}", file=sys.stderr)
        sys.exit(1)

    scenarios = generate_scenarios(args.template, agent_config)

    output = {
        "template": args.template,
        "total_scenarios": len(scenarios),
        "categories": {
            "happy_path": len([s for s in scenarios if s["category"] == "happy_path"]),
            "edge_case": len([s for s in scenarios if s["category"] == "edge_case"]),
            "pronunciation": len([s for s in scenarios if s["category"] == "pronunciation"]),
            "emotional": len([s for s in scenarios if s["category"] == "emotional"]),
        },
        "scoring_rubric": SCORING_RUBRIC,
        "scenarios": scenarios,
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Generated {len(scenarios)} test scenarios for template '{args.template}'")
    print(f"  Happy path:    {output['categories']['happy_path']}")
    print(f"  Edge cases:    {output['categories']['edge_case']}")
    print(f"  Pronunciation: {output['categories']['pronunciation']}")
    print(f"  Emotional:     {output['categories']['emotional']}")
    print(f"Written to: {args.output}")


if __name__ == "__main__":
    main()
