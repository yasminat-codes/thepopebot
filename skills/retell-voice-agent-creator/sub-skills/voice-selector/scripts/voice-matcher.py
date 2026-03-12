#!/usr/bin/env python3
"""
Voice Matcher for Retell AI Voice Agents

Matches voice requirements to a curated catalog and returns
the top 3 recommended voices with scores and reasoning.

Usage:
    python3 voice-matcher.py '{
        "gender": "female",
        "age_range": "25-35",
        "tone": "warm",
        "accent": "american",
        "provider_preference": "elevenlabs",
        "emotion_needed": false,
        "budget": "standard",
        "use_case": "sales"
    }'
"""

import json
import sys

# --- Voice Catalog ---

VOICE_CATALOG = [
    # ElevenLabs
    {"voice_id": "21m00Tcm4TlvDq8ikWAM", "name": "Rachel", "provider": "elevenlabs", "gender": "female", "age_range": "25-35", "accent": "american", "tones": ["warm", "conversational", "friendly"], "use_cases": ["sales", "receptionist", "real_estate", "personal_assistant"], "emotion": False, "cost": "premium"},
    {"voice_id": "EXAVITQu4vr4xnSDxMaL", "name": "Bella", "provider": "elevenlabs", "gender": "female", "age_range": "25-35", "accent": "american", "tones": ["friendly", "natural", "warm"], "use_cases": ["personal_assistant", "support", "wellness"], "emotion": False, "cost": "premium"},
    {"voice_id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "provider": "elevenlabs", "gender": "female", "age_range": "20-28", "accent": "american", "tones": ["calm", "clear", "young"], "use_cases": ["support", "survey", "appointment"], "emotion": False, "cost": "premium"},
    {"voice_id": "ThT5KcBeYPX3keUQqHPh", "name": "Dorothy", "provider": "elevenlabs", "gender": "female", "age_range": "45-60", "accent": "british", "tones": ["warm", "refined", "authoritative"], "use_cases": ["healthcare", "legal", "receptionist", "luxury"], "emotion": False, "cost": "premium"},
    {"voice_id": "oWAxZDx7w5VEj9dCyTzz", "name": "Grace", "provider": "elevenlabs", "gender": "female", "age_range": "30-40", "accent": "american", "tones": ["calm", "soothing", "measured"], "use_cases": ["healthcare", "wellness", "therapy"], "emotion": False, "cost": "premium"},
    {"voice_id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "provider": "elevenlabs", "gender": "male", "age_range": "30-40", "accent": "american", "tones": ["professional", "deep", "steady"], "use_cases": ["sales", "financial", "insurance"], "emotion": False, "cost": "premium"},
    {"voice_id": "ErXwobaYiN019PkySvjV", "name": "Antoni", "provider": "elevenlabs", "gender": "male", "age_range": "25-35", "accent": "american", "tones": ["confident", "articulate", "energetic"], "use_cases": ["sales", "product_demos", "outreach"], "emotion": False, "cost": "premium"},
    {"voice_id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "provider": "elevenlabs", "gender": "male", "age_range": "30-40", "accent": "american", "tones": ["confident", "clear", "professional"], "use_cases": ["lead_qualifier", "b2b", "professional_services"], "emotion": False, "cost": "premium"},
    {"voice_id": "yoZ06aMxZJJ28mfd3POQ", "name": "Sam", "provider": "elevenlabs", "gender": "male", "age_range": "30-45", "accent": "american", "tones": ["authoritative", "composed", "professional"], "use_cases": ["consulting", "corporate", "professional_services"], "emotion": False, "cost": "premium"},
    {"voice_id": "2EiwWnXFnvU5JabPnv8n", "name": "Clyde", "provider": "elevenlabs", "gender": "male", "age_range": "35-50", "accent": "american", "tones": ["deep", "authoritative", "firm"], "use_cases": ["debt_collection", "legal", "insurance"], "emotion": False, "cost": "premium"},
    # OpenAI
    {"voice_id": "openai-coral", "name": "Coral", "provider": "openai", "gender": "female", "age_range": "25-35", "accent": "american", "tones": ["warm", "professional", "friendly"], "use_cases": ["receptionist", "appointment", "support"], "emotion": False, "cost": "budget"},
    {"voice_id": "openai-nova", "name": "Nova", "provider": "openai", "gender": "female", "age_range": "25-35", "accent": "american", "tones": ["warm", "friendly", "approachable"], "use_cases": ["personal_assistant", "wellness", "support"], "emotion": False, "cost": "budget"},
    {"voice_id": "openai-sage", "name": "Sage", "provider": "openai", "gender": "female", "age_range": "30-40", "accent": "american", "tones": ["clear", "measured", "professional"], "use_cases": ["survey", "data_collection", "formal"], "emotion": False, "cost": "budget"},
    {"voice_id": "openai-shimmer", "name": "Shimmer", "provider": "openai", "gender": "female", "age_range": "28-38", "accent": "american", "tones": ["clear", "professional", "polished"], "use_cases": ["receptionist", "corporate", "enterprise_support"], "emotion": False, "cost": "budget"},
    {"voice_id": "openai-echo", "name": "Echo", "provider": "openai", "gender": "male", "age_range": "30-40", "accent": "american", "tones": ["warm", "resonant", "engaging"], "use_cases": ["sales", "outreach", "relationship"], "emotion": False, "cost": "budget"},
    {"voice_id": "openai-ash", "name": "Ash", "provider": "openai", "gender": "male", "age_range": "30-40", "accent": "american", "tones": ["steady", "professional", "composed"], "use_cases": ["lead_qualifier", "b2b", "consulting"], "emotion": False, "cost": "budget"},
    {"voice_id": "openai-onyx", "name": "Onyx", "provider": "openai", "gender": "male", "age_range": "35-50", "accent": "american", "tones": ["deep", "authoritative", "commanding"], "use_cases": ["legal", "financial", "debt_collection"], "emotion": False, "cost": "budget"},
    {"voice_id": "openai-alloy", "name": "Alloy", "provider": "openai", "gender": "neutral", "age_range": "25-35", "accent": "american", "tones": ["versatile", "balanced", "clear"], "use_cases": ["survey", "general", "assistant"], "emotion": False, "cost": "budget"},
    # Cartesia
    {"voice_id": "63ff761f-c1e8-414b-b969-ae73f7e1b90c", "name": "Sweet Lady", "provider": "cartesia", "gender": "female", "age_range": "25-35", "accent": "american", "tones": ["warm", "gentle", "soothing"], "use_cases": ["healthcare", "wellness", "therapy"], "emotion": True, "cost": "standard"},
    {"voice_id": "79a125e8-cd45-4c13-8a67-188112f4dd22", "name": "Commercial Lady", "provider": "cartesia", "gender": "female", "age_range": "28-38", "accent": "american", "tones": ["clear", "professional", "confident"], "use_cases": ["receptionist", "corporate", "sales"], "emotion": True, "cost": "standard"},
    {"voice_id": "248be419-c632-4f23-adf1-5324ed7dbf1d", "name": "Professional Woman", "provider": "cartesia", "gender": "female", "age_range": "30-40", "accent": "american", "tones": ["professional", "calm", "measured"], "use_cases": ["healthcare", "appointment", "legal"], "emotion": True, "cost": "standard"},
    {"voice_id": "c8605446-247c-4f39-993c-f49145efdab7", "name": "Commercial Man", "provider": "cartesia", "gender": "male", "age_range": "30-40", "accent": "american", "tones": ["professional", "steady", "clear"], "use_cases": ["b2b", "consulting", "corporate"], "emotion": True, "cost": "standard"},
    {"voice_id": "bd9120b6-7761-47a6-a446-77ca49132781", "name": "Narrator Man", "provider": "cartesia", "gender": "male", "age_range": "35-45", "accent": "american", "tones": ["authoritative", "steady", "composed"], "use_cases": ["tutorials", "professional", "corporate"], "emotion": True, "cost": "standard"},
    {"voice_id": "fb26447f-308b-471e-8b00-341d93412d00", "name": "Sportsman", "provider": "cartesia", "gender": "male", "age_range": "25-35", "accent": "american", "tones": ["energetic", "confident", "warm"], "use_cases": ["sales", "fitness", "outreach"], "emotion": True, "cost": "standard"},
    # Deepgram
    {"voice_id": "deepgram-aura-asteria-en", "name": "Asteria", "provider": "deepgram", "gender": "female", "age_range": "28-38", "accent": "american", "tones": ["professional", "clear", "steady"], "use_cases": ["receptionist", "appointment", "corporate"], "emotion": False, "cost": "standard"},
    {"voice_id": "deepgram-aura-luna-en", "name": "Luna", "provider": "deepgram", "gender": "female", "age_range": "25-35", "accent": "american", "tones": ["warm", "friendly", "calm"], "use_cases": ["support", "personal_assistant", "wellness"], "emotion": False, "cost": "standard"},
    {"voice_id": "deepgram-aura-orion-en", "name": "Orion", "provider": "deepgram", "gender": "male", "age_range": "30-40", "accent": "american", "tones": ["professional", "steady", "clear"], "use_cases": ["b2b", "lead_qualifier", "consulting"], "emotion": False, "cost": "standard"},
    {"voice_id": "deepgram-aura-perseus-en", "name": "Perseus", "provider": "deepgram", "gender": "male", "age_range": "35-45", "accent": "american", "tones": ["deep", "authoritative", "firm"], "use_cases": ["debt_collection", "legal", "insurance"], "emotion": False, "cost": "standard"},
    # MiniMax
    {"voice_id": "minimax-Calm_Woman", "name": "Calm Woman", "provider": "minimax", "gender": "female", "age_range": "30-40", "accent": "american", "tones": ["calm", "soothing", "gentle"], "use_cases": ["healthcare", "wellness", "therapy"], "emotion": True, "cost": "standard"},
    {"voice_id": "minimax-Inspirational_girl", "name": "Inspirational Girl", "provider": "minimax", "gender": "female", "age_range": "22-30", "accent": "american", "tones": ["energetic", "warm", "motivating"], "use_cases": ["sales", "fitness", "coaching"], "emotion": True, "cost": "standard"},
    {"voice_id": "minimax-Patient_Man", "name": "Patient Man", "provider": "minimax", "gender": "male", "age_range": "30-40", "accent": "american", "tones": ["calm", "steady", "patient"], "use_cases": ["support", "appointment", "onboarding"], "emotion": True, "cost": "standard"},
    {"voice_id": "minimax-Deep_Voice_Man", "name": "Deep Voice Man", "provider": "minimax", "gender": "male", "age_range": "35-50", "accent": "american", "tones": ["deep", "commanding", "authoritative"], "use_cases": ["legal", "debt_collection", "executive"], "emotion": True, "cost": "standard"},
]

# --- Scoring Weights ---

WEIGHTS = {
    "gender": 30,
    "provider": 20,
    "tone": 20,
    "use_case": 15,
    "accent": 10,
    "age_range": 5,
    "emotion": 10,
    "budget": 10,
}

# --- Age Range Helpers ---

def parse_age_range(age_str):
    """Parse '25-35' into (25, 35)."""
    try:
        parts = age_str.split("-")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return 25, 40  # default

def age_overlap(range1, range2):
    """Return overlap ratio between two age ranges (0.0 to 1.0)."""
    low1, high1 = parse_age_range(range1)
    low2, high2 = parse_age_range(range2)
    overlap = max(0, min(high1, high2) - max(low1, low2))
    span = max(high1 - low1, high2 - low2, 1)
    return min(overlap / span, 1.0)

# --- Scoring ---

def score_voice(voice, requirements):
    """Score a voice against requirements. Returns (score, reasons)."""
    score = 0
    reasons = []

    # Gender match (hard filter unless not specified)
    req_gender = requirements.get("gender", "").lower()
    if req_gender:
        if voice["gender"] == req_gender:
            score += WEIGHTS["gender"]
            reasons.append(f"Gender match ({voice['gender']})")
        elif voice["gender"] == "neutral":
            score += WEIGHTS["gender"] * 0.5
            reasons.append("Neutral gender (partial match)")
        else:
            return 0, ["Gender mismatch"]  # Hard disqualify

    # Provider preference
    req_provider = requirements.get("provider_preference", "").lower()
    if req_provider:
        if voice["provider"] == req_provider:
            score += WEIGHTS["provider"]
            reasons.append(f"Preferred provider ({voice['provider']})")
        else:
            score += WEIGHTS["provider"] * 0.3
            reasons.append(f"Alternative provider ({voice['provider']})")

    # Tone match
    req_tone = requirements.get("tone", "").lower()
    if req_tone:
        if req_tone in voice["tones"]:
            score += WEIGHTS["tone"]
            reasons.append(f"Tone match ({req_tone})")
        else:
            # Check for related tones
            tone_families = {
                "warm": ["friendly", "conversational", "gentle", "approachable"],
                "professional": ["clear", "steady", "composed", "polished", "measured"],
                "authoritative": ["commanding", "deep", "firm", "confident"],
                "calm": ["soothing", "measured", "steady", "patient", "gentle"],
                "energetic": ["confident", "engaging", "motivating", "dynamic"],
                "friendly": ["warm", "approachable", "natural", "conversational"],
            }
            related = tone_families.get(req_tone, [])
            matched_related = [t for t in voice["tones"] if t in related]
            if matched_related:
                score += WEIGHTS["tone"] * 0.6
                reasons.append(f"Related tone ({matched_related[0]})")

    # Use case match
    req_use_case = requirements.get("use_case", "").lower().replace(" ", "_")
    if req_use_case:
        if req_use_case in voice["use_cases"]:
            score += WEIGHTS["use_case"]
            reasons.append(f"Use case match ({req_use_case})")

    # Accent match
    req_accent = requirements.get("accent", "").lower()
    if req_accent:
        if voice["accent"] == req_accent:
            score += WEIGHTS["accent"]
            reasons.append(f"Accent match ({req_accent})")
        elif req_accent == "american" and voice["accent"] == "neutral":
            score += WEIGHTS["accent"] * 0.7

    # Age range match
    req_age = requirements.get("age_range", "")
    if req_age:
        overlap = age_overlap(req_age, voice["age_range"])
        age_score = WEIGHTS["age_range"] * overlap
        score += age_score
        if overlap > 0.5:
            reasons.append(f"Age range match ({voice['age_range']})")

    # Emotion requirement
    if requirements.get("emotion_needed"):
        if voice["emotion"]:
            score += WEIGHTS["emotion"]
            reasons.append("Supports voice emotion")
        else:
            score -= WEIGHTS["emotion"] * 0.5
            reasons.append("No emotion support (penalty)")

    # Budget match
    req_budget = requirements.get("budget", "").lower()
    if req_budget == "budget" and voice["cost"] == "budget":
        score += WEIGHTS["budget"]
        reasons.append("Budget-friendly")
    elif req_budget == "budget" and voice["cost"] == "premium":
        score -= WEIGHTS["budget"] * 0.5
        reasons.append("Premium cost (penalty)")

    return score, reasons


def find_fallbacks(primary, all_voices, requirements):
    """Find 2 fallback voices from different providers."""
    primary_provider = primary["provider"]
    primary_gender = primary["gender"]
    candidates = [
        v for v in all_voices
        if v["provider"] != primary_provider
        and v["gender"] == primary_gender
        and v["voice_id"] != primary["voice_id"]
    ]
    scored = []
    for v in candidates:
        s, r = score_voice(v, requirements)
        scored.append((s, v, r))
    scored.sort(key=lambda x: x[0], reverse=True)

    fallbacks = []
    used_providers = {primary_provider}
    for s, v, r in scored:
        if v["provider"] not in used_providers:
            fallbacks.append({"voice_id": v["voice_id"], "name": v["name"], "provider": v["provider"], "score": s})
            used_providers.add(v["provider"])
        if len(fallbacks) >= 2:
            break
    return fallbacks


def match_voices(requirements):
    """Match requirements to catalog and return top 3 with fallbacks."""
    scored_voices = []
    for voice in VOICE_CATALOG:
        score, reasons = score_voice(voice, requirements)
        if score > 0:
            scored_voices.append((score, voice, reasons))

    scored_voices.sort(key=lambda x: x[0], reverse=True)

    if not scored_voices:
        return {
            "error": "No matching voices found. Try relaxing requirements (remove gender, accent, or provider constraints).",
            "recommendations": [],
        }

    results = []
    for score, voice, reasons in scored_voices[:3]:
        fallbacks = find_fallbacks(voice, VOICE_CATALOG, requirements)
        results.append({
            "rank": len(results) + 1,
            "voice_id": voice["voice_id"],
            "name": voice["name"],
            "provider": voice["provider"],
            "gender": voice["gender"],
            "age_range": voice["age_range"],
            "accent": voice["accent"],
            "tones": voice["tones"],
            "supports_emotion": voice["emotion"],
            "score": score,
            "reasons": reasons,
            "fallbacks": fallbacks,
        })

    return {"recommendations": results}


# --- Main ---

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: voice-matcher.py '<json_requirements>'")
        print()
        print("Example:")
        print('  voice-matcher.py \'{"gender":"female","tone":"warm","use_case":"sales"}\'')
        sys.exit(1)

    try:
        requirements = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    results = match_voices(requirements)
    print(json.dumps(results, indent=2))
