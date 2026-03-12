#!/usr/bin/env python3
"""
Humanization Calculator for Retell AI Voice Agents.

Takes a humanization level (1-10) and optional template name, outputs complete
humanization configuration including Retell API parameters and prompt instructions.

Usage:
    python3 humanization-calculator.py --level 6
    python3 humanization-calculator.py --level 7 --template Sales --provider Cartesia
    python3 humanization-calculator.py --template "Personal Assistant"
"""

import json
import sys
import argparse

# Template default humanization levels
TEMPLATE_DEFAULTS = {
    "sales": 6,
    "support": 5,
    "appointment": 5,
    "receptionist": 4,
    "personal assistant": 7,
    "lead qualifier": 4,
    "survey": 3,
    "debt collection": 3,
    "real estate": 7,
}

# Template emotion mappings
TEMPLATE_EMOTIONS = {
    "sales": "happy",
    "support": "sympathetic",
    "appointment": "calm",
    "receptionist": "calm",
    "personal assistant": "happy",
    "lead qualifier": "calm",
    "survey": None,
    "debt collection": "calm",
    "real estate": "happy",
}

# Template ambient sound mappings
TEMPLATE_AMBIENT = {
    "sales": "coffee-shop",
    "support": None,
    "appointment": None,
    "receptionist": None,
    "personal assistant": "coffee-shop",
    "lead qualifier": None,
    "survey": None,
    "debt collection": None,
    "real estate": "coffee-shop",
}

# Providers that support voice_emotion
EMOTION_PROVIDERS = {"cartesia", "minimax"}

# Backchannel word sets by level range
BACKCHANNEL_WORDS = {
    3: ["mhm"],
    4: ["mhm", "I see"],
    5: ["mhm", "yeah", "I see"],
    6: ["mhm", "yeah", "I see", "right"],
    7: ["mhm", "yeah", "I see", "right", "oh okay", "got it"],
    8: ["mhm", "yeah", "I see", "right", "oh okay", "got it"],
    9: ["mhm", "yeah", "I see", "right", "oh okay", "got it", "uh-huh", "for sure"],
    10: ["mhm", "yeah", "I see", "right", "oh okay", "got it", "uh-huh", "for sure", "totally"],
}

# Prompt templates by level range
PROMPT_TEMPLATES = {
    (1, 2): (
        "Speak clearly and precisely. Do not use filler words. "
        "Respond promptly and professionally."
    ),
    (3, 4): (
        "Speak in a professional and warm tone. You may occasionally pause briefly "
        "before sharing important information. Use transitional phrases like \"So,\" "
        "and \"Well,\" sparingly."
    ),
    (5, 6): (
        "Speak naturally, like a friendly professional. Use occasional filler words "
        "like \"um\" and \"well\" to sound more human. Pause briefly when thinking. "
        "Show warmth in your voice. You can say things like \"That's a great question, "
        "let me think about that for a moment.\""
    ),
    (7, 8): (
        "Speak like a real person having a genuine conversation. Use filler words "
        "naturally -- \"um\", \"uh\", \"you know\", \"let me see\". Pause when thinking. "
        "Occasionally correct yourself: \"The appointment is at 3 -- actually, 3:30.\" "
        "Show genuine emotion and interest. React naturally to what the caller says. "
        "Take your time responding, as if you are actually thinking about the answer."
    ),
    (9, 10): (
        "Speak exactly like a real person. Use lots of natural fillers -- \"um\", \"uh\", "
        "\"like\", \"you know what I mean\". Pause frequently. Correct yourself sometimes. "
        "Occasionally stumble slightly on words. React with genuine surprise, empathy, "
        "or enthusiasm. Take your time, think out loud: \"Hmm, let me pull that up... "
        "okay so... yeah, I see it here.\" Sound like you are multitasking. Be casual "
        "and authentic above all else."
    ),
}


def get_prompt_template(level):
    """Get the prompt template for a given humanization level."""
    for (low, high), template in PROMPT_TEMPLATES.items():
        if low <= level <= high:
            return template
    return PROMPT_TEMPLATES[(5, 6)]


def calculate_humanization(level, template_name=None, provider=None):
    """Calculate complete humanization configuration.

    Args:
        level: Humanization level 1-10
        template_name: Optional template name for context-specific defaults
        provider: Optional voice provider name

    Returns:
        Complete humanization configuration dict
    """
    template_key = template_name.lower() if template_name else None
    provider_key = provider.lower() if provider else None

    # Clamp level
    level = max(1, min(10, level))

    # Backchannel
    if level <= 2:
        enable_backchannel = False
        backchannel_frequency = None
        backchannel_words_list = None
    else:
        enable_backchannel = True
        freq_map = {3: 0.2, 4: 0.3, 5: 0.5, 6: 0.6, 7: 0.7, 8: 0.8, 9: 0.9, 10: 1.0}
        backchannel_frequency = freq_map.get(level, 0.5)
        backchannel_words_list = BACKCHANNEL_WORDS.get(level, BACKCHANNEL_WORDS[6])

    # Temperature
    temp_map = {1: 0.3, 2: 0.4, 3: 0.5, 4: 0.6, 5: 0.7, 6: 0.8, 7: 0.9, 8: 1.1, 9: 1.3, 10: 1.5}
    voice_temperature = temp_map.get(level, 0.7)

    # Responsiveness
    resp_map = {1: 1.0, 2: 1.0, 3: 0.9, 4: 0.9, 5: 0.8, 6: 0.8, 7: 0.7, 8: 0.6, 9: 0.5, 10: 0.4}
    responsiveness = resp_map.get(level, 0.8)

    # Interruption sensitivity
    int_map = {1: 1.0, 2: 0.9, 3: 0.9, 4: 0.8, 5: 0.8, 6: 0.7, 7: 0.7, 8: 0.6, 9: 0.5, 10: 0.5}
    interruption_sensitivity = int_map.get(level, 0.7)

    # Ambient sound
    if level <= 3:
        ambient_sound = None
        ambient_sound_volume = None
    elif level <= 5:
        ambient_sound = TEMPLATE_AMBIENT.get(template_key) if template_key else None
        ambient_sound_volume = 0.4 if ambient_sound else None
    elif level <= 7:
        ambient_sound = (TEMPLATE_AMBIENT.get(template_key) or "coffee-shop") if template_key else "coffee-shop"
        vol_map = {6: 0.5, 7: 0.6}
        ambient_sound_volume = vol_map.get(level, 0.5)
    else:
        ambient_sound = (TEMPLATE_AMBIENT.get(template_key) or "coffee-shop") if template_key else "coffee-shop"
        vol_map = {8: 0.8, 9: 1.0, 10: 1.3}
        ambient_sound_volume = vol_map.get(level, 0.8)

    # Voice emotion (only for supported providers)
    voice_emotion = None
    if provider_key in EMOTION_PROVIDERS and level >= 4:
        if template_key and template_key in TEMPLATE_EMOTIONS:
            voice_emotion = TEMPLATE_EMOTIONS[template_key]
        elif level >= 6:
            voice_emotion = "happy"
        else:
            voice_emotion = "calm"

    # Build config params
    config_params = {
        "voice_temperature": voice_temperature,
        "responsiveness": responsiveness,
        "interruption_sensitivity": interruption_sensitivity,
    }

    if enable_backchannel:
        config_params["enable_backchannel"] = True
        config_params["backchannel_frequency"] = backchannel_frequency
        config_params["backchannel_words"] = backchannel_words_list
    else:
        config_params["enable_backchannel"] = False

    if ambient_sound:
        config_params["ambient_sound"] = ambient_sound
        config_params["ambient_sound_volume"] = ambient_sound_volume

    if voice_emotion:
        config_params["voice_emotion"] = voice_emotion

    # Build lever summary
    bc_summary = f"on (freq {backchannel_frequency}, {len(backchannel_words_list)} words)" if enable_backchannel else "off"
    filler_labels = {1: "none", 2: "none", 3: "rare", 4: "rare", 5: "occasional",
                     6: "occasional", 7: "regular", 8: "regular-to-frequent",
                     9: "frequent", 10: "very frequent"}
    ambient_summary = f"{ambient_sound} at {ambient_sound_volume}" if ambient_sound else "none"
    emotion_summary = voice_emotion if voice_emotion else "none (provider unsupported)" if provider_key and provider_key not in EMOTION_PROVIDERS else "none"

    lever_summary = {
        "backchannel": bc_summary,
        "fillers": filler_labels.get(level, "occasional"),
        "pauses": f"responsiveness {responsiveness}",
        "ambient": ambient_summary,
        "emotion": emotion_summary,
        "temperature": str(voice_temperature),
    }

    # Build notes
    notes_parts = [f"Level {level}"]
    if template_name:
        notes_parts.append(f"template: {template_name}")
    if provider:
        notes_parts.append(f"provider: {provider}")
        if provider_key not in EMOTION_PROVIDERS:
            notes_parts.append("voice_emotion not supported by this provider")
    notes = ". ".join(notes_parts) + "."

    return {
        "config_params": config_params,
        "prompt_instructions": get_prompt_template(level),
        "humanization_level": level,
        "lever_summary": lever_summary,
        "notes": notes,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate humanization settings for Retell AI voice agents"
    )
    parser.add_argument(
        "--level", "-l", type=int,
        help="Humanization level (1-10)"
    )
    parser.add_argument(
        "--template", "-t",
        help="Template name (e.g., Sales, Support, Receptionist)"
    )
    parser.add_argument(
        "--provider", "-p",
        help="Voice provider (e.g., ElevenLabs, Cartesia, OpenAI)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: stdout)"
    )

    args = parser.parse_args()

    # Determine level
    if args.level:
        level = args.level
    elif args.template:
        template_key = args.template.lower()
        level = TEMPLATE_DEFAULTS.get(template_key)
        if level is None:
            print(f"Error: Unknown template '{args.template}'", file=sys.stderr)
            print(f"Available templates: {', '.join(TEMPLATE_DEFAULTS.keys())}", file=sys.stderr)
            sys.exit(1)
    else:
        print("Error: Must specify --level or --template", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

    result = calculate_humanization(level, args.template, args.provider)
    output_json = json.dumps(result, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
        print(f"Written to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
