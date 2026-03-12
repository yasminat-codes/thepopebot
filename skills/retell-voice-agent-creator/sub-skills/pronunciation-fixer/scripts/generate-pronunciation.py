#!/usr/bin/env python3
"""
Generate IPA pronunciation dictionary entries for Retell AI voice agents.

Takes a JSON file with words and optional phonetic hints, and produces
pronunciation_dictionary entries compatible with Retell's API.

Usage:
    python3 generate-pronunciation.py --input words.json --output pronunciations.json
    python3 generate-pronunciation.py --word "Nguyen" --hint "win"

Input JSON format:
{
  "words": [
    {"word": "Nguyen", "hint": "win"},
    {"word": "Siobhan", "hint": "shuh-vawn"}
  ]
}

Output JSON format:
{
  "pronunciation_dictionary": [
    {"word": "Nguyen", "alphabet": "ipa", "phoneme": "wIn"}
  ]
}
"""

import json
import sys
import argparse
from pathlib import Path

# Mapping of common phonetic hint patterns to IPA symbols
PHONETIC_TO_IPA = {
    # Vowels
    "ee": "i:",
    "ih": "I",
    "ay": "eI",
    "eh": "E",
    "ah": "A:",
    "uh": "@",
    "oh": "oU",
    "oo": "u:",
    "aw": "O:",
    "oy": "OI",
    "ow": "aU",
    "eye": "aI",
    "ur": "3:",
    "air": "E@",
    "ear": "I@",
    # Consonants
    "sh": "S",
    "zh": "Z",
    "ch": "tS",
    "th": "T",
    "dh": "D",
    "ng": "N",
    "j": "dZ",
    "y": "j",
}

# Single character mappings
CHAR_TO_IPA = {
    "a": "ae",
    "b": "b",
    "c": "k",
    "d": "d",
    "e": "E",
    "f": "f",
    "g": "g",
    "h": "h",
    "i": "I",
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "o": "O:",
    "p": "p",
    "r": "r",
    "s": "s",
    "t": "t",
    "u": "V",
    "v": "v",
    "w": "w",
    "x": "ks",
    "z": "z",
}

# Known pronunciations for common names and terms
KNOWN_PRONUNCIATIONS = {
    "nguyen": "wIn",
    "siobhan": "SI.vO:n",
    "niamh": "ni:v",
    "saoirse": "sEr.S@",
    "aoife": "i:.f@",
    "bjorn": "bjO:rn",
    "joaquin": "wA:.ki:n",
    "priyanka": "pri:.jAN.k@",
    "dmitri": "dmI.tri:",
    "xiaoming": "SaU.mIN",
    "tsuyoshi": "tsu.jo.SI",
    "rahul": "rA:.hUl",
    # Tech terms
    "saas": "saes",
    "paas": "paes",
    "hipaa": "hIp@",
    "ebitda": "i:bItdA:",
    "gaap": "gaep",
    "reit": "ri:t",
    "scotus": "skoU.t@s",
    "gif": "dZIf",
    "sql": "si:.kwEl",
    "wysiwyg": "wIz.i:.wIg",
    "ajax": "eI.dZaeks",
    "fema": "fi:.m@",
    "osha": "oU.S@",
    "fico": "faI.koU",
    "rico": "ri:.koU",
    "nasa": "naes@",
    "scuba": "sku:.b@",
}


def hint_to_ipa(hint):
    """Convert a phonetic hint string to IPA notation.

    Processes the hint from left to right, matching the longest possible
    phonetic pattern first, then falling back to single characters.

    Args:
        hint: A phonetic hint string like "win", "shuh-vawn"

    Returns:
        An IPA string approximation
    """
    hint = hint.lower().strip()
    # Remove hyphens used as syllable separators but note positions
    syllables = hint.split("-")
    ipa_parts = []

    for syllable in syllables:
        ipa = ""
        i = 0
        while i < len(syllable):
            matched = False
            # Try matching 3-char patterns first, then 2-char, then 1-char
            for length in [3, 2]:
                if i + length <= len(syllable):
                    chunk = syllable[i:i + length]
                    if chunk in PHONETIC_TO_IPA:
                        ipa += PHONETIC_TO_IPA[chunk]
                        i += length
                        matched = True
                        break
            if not matched:
                char = syllable[i]
                if char in CHAR_TO_IPA:
                    ipa += CHAR_TO_IPA[char]
                elif char.isalpha():
                    # Unknown letter, pass through
                    ipa += char
                i += 1
        ipa_parts.append(ipa)

    return ".".join(ipa_parts) if len(ipa_parts) > 1 else ipa_parts[0]


def generate_entry(word, hint=None, alphabet="ipa"):
    """Generate a pronunciation dictionary entry.

    Args:
        word: The word to generate pronunciation for
        hint: Optional phonetic hint
        alphabet: "ipa" or "cmu"

    Returns:
        A dictionary with word, alphabet, and phoneme keys
    """
    word_lower = word.lower()

    # Check known pronunciations first
    if word_lower in KNOWN_PRONUNCIATIONS and not hint:
        return {
            "word": word,
            "alphabet": "ipa",
            "phoneme": KNOWN_PRONUNCIATIONS[word_lower],
        }

    # If a hint is provided, convert it to IPA
    if hint:
        phoneme = hint_to_ipa(hint)
        return {
            "word": word,
            "alphabet": "ipa",
            "phoneme": phoneme,
        }

    # No known pronunciation and no hint -- return a basic attempt
    phoneme = hint_to_ipa(word_lower)
    return {
        "word": word,
        "alphabet": "ipa",
        "phoneme": phoneme,
    }


def process_input_file(input_path):
    """Process an input JSON file and generate pronunciation entries.

    Args:
        input_path: Path to the input JSON file

    Returns:
        A dictionary with pronunciation_dictionary array
    """
    with open(input_path, "r") as f:
        data = json.load(f)

    entries = []
    for item in data.get("words", []):
        word = item.get("word", "")
        hint = item.get("hint", None)
        if word:
            entry = generate_entry(word, hint)
            entries.append(entry)

    return {"pronunciation_dictionary": entries}


def main():
    parser = argparse.ArgumentParser(
        description="Generate IPA pronunciation dictionary entries for Retell AI"
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to input JSON file with words"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to output JSON file (default: stdout)"
    )
    parser.add_argument(
        "--word", "-w",
        help="Single word to generate pronunciation for"
    )
    parser.add_argument(
        "--hint",
        help="Phonetic hint for the word (used with --word)"
    )

    args = parser.parse_args()

    if args.word:
        # Single word mode
        entry = generate_entry(args.word, args.hint)
        result = {"pronunciation_dictionary": [entry]}
    elif args.input:
        # File mode
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        result = process_input_file(input_path)
    else:
        parser.print_help()
        sys.exit(1)

    # Output
    output_json = json.dumps(result, indent=2)

    if args.output:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            f.write(output_json)
        print(f"Written {len(result['pronunciation_dictionary'])} entries to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
