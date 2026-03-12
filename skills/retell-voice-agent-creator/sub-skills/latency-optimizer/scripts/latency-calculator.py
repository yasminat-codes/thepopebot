#!/usr/bin/env python3
"""
Latency Calculator for Retell AI Voice Agents

Calculates optimal latency settings (responsiveness, interruption_sensitivity,
denoising_mode, recommended LLM model) based on use case, environment, caller
type, and priority preferences.

Usage:
    python3 latency-calculator.py --use-case appointment-setter --environment mixed --caller-type normal
    python3 latency-calculator.py --json '{"use_case":"sales-agent","environment":"quiet","priority":"speed"}'
"""

import argparse
import json
import sys

# ---------------------------------------------------------------------------
# Preset profiles per template type (baseline for mixed environment, normal caller)
# ---------------------------------------------------------------------------
PRESETS = {
    "appointment-setter": {
        "responsiveness": 0.90,
        "interruption_sensitivity": 0.80,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "accurate",
        "end_call_after_silence_ms": 60000,
        "recommended_model": "gpt-4o-mini",
        "reminder_trigger_ms": 25000,
        "reminder_max_count": 2,
    },
    "sales-agent": {
        "responsiveness": 0.95,
        "interruption_sensitivity": 0.85,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "fast",
        "end_call_after_silence_ms": 30000,
        "recommended_model": "gpt-4o-mini",
        "reminder_trigger_ms": 15000,
        "reminder_max_count": 1,
    },
    "customer-support": {
        "responsiveness": 0.85,
        "interruption_sensitivity": 0.75,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "accurate",
        "end_call_after_silence_ms": 120000,
        "recommended_model": "gpt-4o",
        "reminder_trigger_ms": 30000,
        "reminder_max_count": 2,
    },
    "receptionist": {
        "responsiveness": 0.90,
        "interruption_sensitivity": 0.80,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "accurate",
        "end_call_after_silence_ms": 60000,
        "recommended_model": "gpt-4o-mini",
        "reminder_trigger_ms": 25000,
        "reminder_max_count": 2,
    },
    "personal-assistant": {
        "responsiveness": 0.85,
        "interruption_sensitivity": 0.80,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "accurate",
        "end_call_after_silence_ms": 300000,
        "recommended_model": "gpt-4o",
        "reminder_trigger_ms": 60000,
        "reminder_max_count": 2,
    },
    "lead-qualifier": {
        "responsiveness": 0.95,
        "interruption_sensitivity": 0.85,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "fast",
        "end_call_after_silence_ms": 30000,
        "recommended_model": "gpt-4o-mini",
        "reminder_trigger_ms": 15000,
        "reminder_max_count": 1,
    },
    "survey-agent": {
        "responsiveness": 0.85,
        "interruption_sensitivity": 0.75,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "accurate",
        "end_call_after_silence_ms": 60000,
        "recommended_model": "gpt-4o-mini",
        "reminder_trigger_ms": 25000,
        "reminder_max_count": 2,
    },
    "debt-collection": {
        "responsiveness": 0.85,
        "interruption_sensitivity": 0.65,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "accurate",
        "end_call_after_silence_ms": 60000,
        "recommended_model": "gpt-4o",
        "reminder_trigger_ms": 25000,
        "reminder_max_count": 2,
    },
    "real-estate": {
        "responsiveness": 0.90,
        "interruption_sensitivity": 0.80,
        "denoising_mode": "noise-cancellation",
        "stt_mode": "accurate",
        "end_call_after_silence_ms": 60000,
        "recommended_model": "gpt-4o-mini",
        "reminder_trigger_ms": 25000,
        "reminder_max_count": 2,
    },
}

# ---------------------------------------------------------------------------
# Environment adjustments (deltas applied on top of preset)
# ---------------------------------------------------------------------------
ENVIRONMENT_ADJUSTMENTS = {
    "quiet": {
        "responsiveness_delta": 0.0,
        "interruption_delta": +0.05,
        "denoising_mode": "no-denoise",
        "stt_mode_override": None,  # keep preset
    },
    "mixed": {
        "responsiveness_delta": 0.0,
        "interruption_delta": 0.0,
        "denoising_mode": "noise-cancellation",
        "stt_mode_override": "accurate",
    },
    "noisy": {
        "responsiveness_delta": 0.0,
        "interruption_delta": -0.15,
        "denoising_mode": "noise-and-background-speech-cancellation",
        "stt_mode_override": "accurate",
    },
}

# ---------------------------------------------------------------------------
# Caller-type adjustments
# ---------------------------------------------------------------------------
CALLER_ADJUSTMENTS = {
    "normal": {
        "responsiveness_delta": 0.0,
        "interruption_delta": 0.0,
        "silence_multiplier": 1.0,
    },
    "elderly": {
        "responsiveness_delta": -0.15,
        "interruption_delta": -0.10,
        "silence_multiplier": 2.0,
    },
    "fast-talker": {
        "responsiveness_delta": +0.05,
        "interruption_delta": +0.05,
        "silence_multiplier": 0.75,
    },
}

# ---------------------------------------------------------------------------
# Priority adjustments
# ---------------------------------------------------------------------------
PRIORITY_ADJUSTMENTS = {
    "balanced": {
        "responsiveness_delta": 0.0,
        "model_override": None,
    },
    "speed": {
        "responsiveness_delta": +0.05,
        "model_override": "gpt-4o-mini",
    },
    "accuracy": {
        "responsiveness_delta": -0.05,
        "model_override": "gpt-4o",
    },
}


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a float to [low, high] and round to 2 decimal places."""
    return round(max(low, min(high, value)), 2)


def calculate(
    use_case: str,
    environment: str = "mixed",
    caller_type: str = "normal",
    priority: str = "balanced",
) -> dict:
    """Calculate optimal latency settings and return a result dict."""

    # Resolve preset
    use_case_key = use_case.lower().strip()
    if use_case_key not in PRESETS:
        available = ", ".join(sorted(PRESETS.keys()))
        return {
            "error": f"Unknown use_case '{use_case}'. Available: {available}",
        }

    env_key = environment.lower().strip()
    if env_key not in ENVIRONMENT_ADJUSTMENTS:
        return {
            "error": f"Unknown environment '{environment}'. Use: quiet, mixed, noisy",
        }

    caller_key = caller_type.lower().strip()
    if caller_key not in CALLER_ADJUSTMENTS:
        return {
            "error": f"Unknown caller_type '{caller_type}'. Use: normal, elderly, fast-talker",
        }

    priority_key = priority.lower().strip()
    if priority_key not in PRIORITY_ADJUSTMENTS:
        return {
            "error": f"Unknown priority '{priority}'. Use: balanced, speed, accuracy",
        }

    # Start from preset
    preset = PRESETS[use_case_key].copy()
    env = ENVIRONMENT_ADJUSTMENTS[env_key]
    caller = CALLER_ADJUSTMENTS[caller_key]
    pri = PRIORITY_ADJUSTMENTS[priority_key]

    # Calculate responsiveness
    responsiveness = (
        preset["responsiveness"]
        + env["responsiveness_delta"]
        + caller["responsiveness_delta"]
        + pri["responsiveness_delta"]
    )

    # Calculate interruption sensitivity
    interruption_sensitivity = (
        preset["interruption_sensitivity"]
        + env["interruption_delta"]
        + caller["interruption_delta"]
    )

    # Denoising mode (environment overrides preset)
    denoising_mode = env["denoising_mode"]

    # STT mode (environment can override, otherwise keep preset)
    stt_mode = env["stt_mode_override"] or preset["stt_mode"]

    # Model (priority can override)
    recommended_model = pri["model_override"] or preset["recommended_model"]

    # Silence timeout (caller type scales it)
    end_call_after_silence_ms = int(
        preset["end_call_after_silence_ms"] * caller["silence_multiplier"]
    )
    # Enforce minimum
    end_call_after_silence_ms = max(10000, end_call_after_silence_ms)

    # Build explanations
    explanations = []
    explanations.append(
        f"Base preset: {use_case_key} (responsiveness={preset['responsiveness']}, "
        f"interruption={preset['interruption_sensitivity']})"
    )
    if env_key != "mixed":
        explanations.append(
            f"Environment '{env_key}': denoising={denoising_mode}, "
            f"interruption adjusted by {env['interruption_delta']:+.2f}"
        )
    if caller_key != "normal":
        explanations.append(
            f"Caller type '{caller_key}': responsiveness adjusted by "
            f"{caller['responsiveness_delta']:+.2f}, silence timeout x{caller['silence_multiplier']}"
        )
    if priority_key != "balanced":
        explanations.append(
            f"Priority '{priority_key}': responsiveness adjusted by "
            f"{pri['responsiveness_delta']:+.2f}"
            + (f", model overridden to {pri['model_override']}" if pri["model_override"] else "")
        )

    return {
        "settings": {
            "responsiveness": clamp(responsiveness),
            "interruption_sensitivity": clamp(interruption_sensitivity),
            "denoising_mode": denoising_mode,
            "stt_mode": stt_mode,
            "end_call_after_silence_ms": end_call_after_silence_ms,
            "reminder_trigger_ms": preset["reminder_trigger_ms"],
            "reminder_max_count": preset["reminder_max_count"],
        },
        "recommended_model": recommended_model,
        "inputs": {
            "use_case": use_case_key,
            "environment": env_key,
            "caller_type": caller_key,
            "priority": priority_key,
        },
        "explanations": explanations,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Calculate optimal Retell AI voice agent latency settings."
    )
    parser.add_argument(
        "--use-case",
        type=str,
        help="Agent template type (e.g., appointment-setter, sales-agent)",
    )
    parser.add_argument(
        "--environment",
        type=str,
        default="mixed",
        help="Caller environment: quiet, mixed, noisy (default: mixed)",
    )
    parser.add_argument(
        "--caller-type",
        type=str,
        default="normal",
        help="Caller demographic: normal, elderly, fast-talker (default: normal)",
    )
    parser.add_argument(
        "--priority",
        type=str,
        default="balanced",
        help="Optimization priority: balanced, speed, accuracy (default: balanced)",
    )
    parser.add_argument(
        "--json",
        type=str,
        help='JSON input: \'{"use_case":"...","environment":"...","caller_type":"...","priority":"..."}\'',
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List all available template presets and exit",
    )

    args = parser.parse_args()

    # List presets mode
    if args.list_presets:
        print(json.dumps({"available_presets": sorted(PRESETS.keys())}, indent=2))
        sys.exit(0)

    # JSON input mode
    if args.json:
        try:
            data = json.loads(args.json)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {e}"}), file=sys.stderr)
            sys.exit(1)

        result = calculate(
            use_case=data.get("use_case", ""),
            environment=data.get("environment", "mixed"),
            caller_type=data.get("caller_type", "normal"),
            priority=data.get("priority", "balanced"),
        )
    elif args.use_case:
        result = calculate(
            use_case=args.use_case,
            environment=args.environment,
            caller_type=args.caller_type,
            priority=args.priority,
        )
    else:
        parser.print_help()
        sys.exit(1)

    if "error" in result:
        print(json.dumps(result, indent=2), file=sys.stderr)
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
