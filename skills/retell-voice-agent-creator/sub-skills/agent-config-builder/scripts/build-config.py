#!/usr/bin/env python3
"""
build-config.py — Assemble Retell AI agent configuration from sub-skill outputs.

Usage:
    python3 build-config.py \
        --voice-config voice_config.json \
        --prompt-config prompt_config.json \
        [--pronunciation pronunciation_dict.json] \
        [--humanization humanization_config.json] \
        [--latency latency_config.json] \
        --template appointment-setter \
        --business-info business_info.json \
        [--output-dir .]

Produces: llm-config.json, agent-config.json
"""

import argparse
import json
import os
import sys

# ── Template-specific post-call analytics ──────────────────────────────────

UNIVERSAL_ANALYTICS = [
    {
        "name": "call_summary",
        "type": "string",
        "description": "Summarize the call in 2-3 sentences. Include the caller's main request, the outcome, and any follow-up needed."
    },
    {
        "name": "user_sentiment",
        "type": "enum",
        "description": "Overall caller sentiment. Options: positive, neutral, negative."
    }
]

TEMPLATE_ANALYTICS = {
    "appointment-setter": [
        {"name": "appointment_booked", "type": "boolean", "description": "Was an appointment successfully booked during this call?"},
        {"name": "appointment_date", "type": "string", "description": "Date and time of the booked appointment. Return 'none' if not booked."},
        {"name": "appointment_type", "type": "string", "description": "Type of service or appointment requested."},
    ],
    "sales-outbound": [
        {"name": "did_express_interest", "type": "boolean", "description": "Did the prospect express interest in the product or service?"},
        {"name": "lead_score", "type": "number", "description": "Rate lead quality 1-10. 1 = not interested, 10 = ready to buy."},
        {"name": "objections_raised", "type": "string", "description": "List objections raised. Return 'none' if no objections."},
        {"name": "next_steps", "type": "string", "description": "What follow-up actions are needed?"},
    ],
    "sales-inbound": [
        {"name": "did_express_interest", "type": "boolean", "description": "Did the prospect express interest in the product or service?"},
        {"name": "lead_score", "type": "number", "description": "Rate lead quality 1-10. 1 = not interested, 10 = ready to buy."},
        {"name": "objections_raised", "type": "string", "description": "List objections raised. Return 'none' if no objections."},
        {"name": "next_steps", "type": "string", "description": "What follow-up actions are needed?"},
    ],
    "customer-support": [
        {"name": "issue_resolved", "type": "boolean", "description": "Was the caller's issue fully resolved during this call?"},
        {"name": "issue_category", "type": "enum", "description": "Issue category. Options: billing, technical, account, general, other."},
        {"name": "escalation_needed", "type": "boolean", "description": "Does this need escalation to a human agent?"},
    ],
    "lead-qualifier": [
        {"name": "is_qualified", "type": "boolean", "description": "Does the lead meet qualification criteria?"},
        {"name": "budget_range", "type": "string", "description": "Stated or implied budget. Return 'not disclosed' if unknown."},
        {"name": "timeline", "type": "string", "description": "When does the prospect want to proceed?"},
        {"name": "decision_maker", "type": "boolean", "description": "Is the caller the decision maker?"},
    ],
    "survey": [
        {"name": "survey_completed", "type": "boolean", "description": "Did the caller complete all survey questions?"},
        {"name": "responses", "type": "string", "description": "Summarize all survey responses."},
    ],
    "reminder": [
        {"name": "reminder_acknowledged", "type": "boolean", "description": "Did the caller confirm the reminder?"},
        {"name": "reschedule_requested", "type": "boolean", "description": "Did the caller ask to reschedule?"},
    ],
    "receptionist": [
        {"name": "call_purpose", "type": "string", "description": "Why did the caller call? One sentence."},
        {"name": "transferred", "type": "boolean", "description": "Was the call transferred?"},
        {"name": "message_taken", "type": "string", "description": "Message left for staff. Return 'none' if no message."},
    ],
    "custom": [],
}

# ── Default values ─────────────────────────────────────────────────────────

AGENT_DEFAULTS = {
    "voice_temperature": 1.0,
    "voice_speed": 1.0,
    "enable_dynamic_voice_speed": False,
    "responsiveness": 0.8,
    "interruption_sensitivity": 0.7,
    "enable_backchannel": True,
    "backchannel_frequency": 0.5,
    "normalize_for_speech": True,
    "language": "en-US",
    "denoising_mode": "noise-cancellation",
    "end_call_after_silence_ms": 30000,
    "max_call_duration_ms": 900000,
    "data_storage_setting": "everything",
}

LLM_DEFAULTS = {
    "start_speaker": "agent",
    "model": "gpt-4.1",
    "model_temperature": 0.4,
}


def load_json(path):
    """Load a JSON file, returning None if path is None or file missing."""
    if not path:
        return None
    if not os.path.isfile(path):
        print(f"WARNING: {path} not found, skipping.", file=sys.stderr)
        return None
    with open(path, "r") as f:
        return json.load(f)


def build_llm_config(prompt_config):
    """Build llm-config.json from prompt-generator output."""
    config = {}

    # Start with defaults
    for key, val in LLM_DEFAULTS.items():
        config[key] = val

    if not prompt_config:
        return config

    # Map fields from prompt_config
    field_map = [
        "start_speaker", "general_prompt", "begin_message", "model",
        "model_temperature", "states", "general_tools", "knowledge_base_ids",
        "guardrail_config",
    ]

    for field in field_map:
        if field in prompt_config and prompt_config[field] is not None:
            config[field] = prompt_config[field]

    return config


def build_agent_config(voice_config, humanization_config, latency_config,
                       pronunciation_dict, template_name):
    """Build agent-config.json by merging sub-skill outputs."""
    config = {}

    # Start with defaults
    for key, val in AGENT_DEFAULTS.items():
        config[key] = val

    # Layer 1: Voice config (base)
    if voice_config:
        if "voice_id" in voice_config:
            config["voice_id"] = voice_config["voice_id"]
        if "fallback_voice_ids" in voice_config:
            config["fallback_voice_ids"] = voice_config["fallback_voice_ids"]
        if "voice_model" in voice_config and voice_config["voice_model"]:
            config["voice_model"] = voice_config["voice_model"]

    # Layer 2: Humanization config (experience settings)
    if humanization_config:
        humanization_fields = [
            "enable_backchannel", "backchannel_frequency", "backchannel_words",
            "voice_emotion", "ambient_sound", "ambient_sound_volume",
            "voice_temperature",
        ]
        for field in humanization_fields:
            if field in humanization_config and humanization_config[field] is not None:
                config[field] = humanization_config[field]

    # Layer 3: Latency config (performance — highest priority)
    if latency_config:
        latency_fields = [
            "responsiveness", "interruption_sensitivity", "voice_speed",
            "enable_dynamic_voice_speed",
        ]
        for field in latency_fields:
            if field in latency_config and latency_config[field] is not None:
                config[field] = latency_config[field]

    # Pronunciation dictionary
    if pronunciation_dict and isinstance(pronunciation_dict, list) and len(pronunciation_dict) > 0:
        config["pronunciation_dictionary"] = pronunciation_dict

    # Post-call analytics
    analytics = list(UNIVERSAL_ANALYTICS)
    template_key = template_name if template_name in TEMPLATE_ANALYTICS else "custom"
    analytics.extend(TEMPLATE_ANALYTICS[template_key])
    config["post_call_analysis_data"] = analytics

    return config


def main():
    parser = argparse.ArgumentParser(description="Build Retell AI agent config files.")
    parser.add_argument("--voice-config", required=True, help="Path to voice_config.json")
    parser.add_argument("--prompt-config", required=True, help="Path to prompt_config.json")
    parser.add_argument("--pronunciation", default=None, help="Path to pronunciation_dict.json")
    parser.add_argument("--humanization", default=None, help="Path to humanization_config.json")
    parser.add_argument("--latency", default=None, help="Path to latency_config.json")
    parser.add_argument("--template", required=True, help="Template name")
    parser.add_argument("--business-info", default=None, help="Path to business_info.json")
    parser.add_argument("--output-dir", default=".", help="Output directory")
    args = parser.parse_args()

    # Load all inputs
    voice_config = load_json(args.voice_config)
    prompt_config = load_json(args.prompt_config)
    pronunciation_dict = load_json(args.pronunciation)
    humanization_config = load_json(args.humanization)
    latency_config = load_json(args.latency)

    if not voice_config:
        print("ERROR: voice_config.json is required.", file=sys.stderr)
        sys.exit(1)
    if not prompt_config:
        print("ERROR: prompt_config.json is required.", file=sys.stderr)
        sys.exit(1)
    if "voice_id" not in voice_config:
        print("ERROR: voice_id missing from voice_config.json.", file=sys.stderr)
        sys.exit(1)

    # Build configs
    llm_config = build_llm_config(prompt_config)
    agent_config = build_agent_config(
        voice_config, humanization_config, latency_config,
        pronunciation_dict, args.template
    )

    # Write outputs
    os.makedirs(args.output_dir, exist_ok=True)

    llm_path = os.path.join(args.output_dir, "llm-config.json")
    with open(llm_path, "w") as f:
        json.dump(llm_config, f, indent=2)
    print(f"Written: {llm_path}")

    agent_path = os.path.join(args.output_dir, "agent-config.json")
    with open(agent_path, "w") as f:
        json.dump(agent_config, f, indent=2)
    print(f"Written: {agent_path}")

    # Summary
    print(f"\nTemplate: {args.template}")
    print(f"Voice: {agent_config.get('voice_id', 'unknown')}")
    print(f"Model: {llm_config.get('model', 'unknown')}")
    print(f"Analytics variables: {len(agent_config.get('post_call_analysis_data', []))}")
    if pronunciation_dict:
        print(f"Pronunciation entries: {len(pronunciation_dict)}")
    print("\nReady for validation: python3 validate-config.py --llm-config llm-config.json --agent-config agent-config.json")


if __name__ == "__main__":
    main()
