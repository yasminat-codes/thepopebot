"""
deaify.py — Main de-AI-fy processing engine

Applies automated de-AI-fy transformations to text files.
Handles Layers 1, 2, 4, and 5 automatically.
Layers 3 (structural), 6 (authenticity) require LLM-guided rewriting.

Usage:
    python deaify.py --input file.txt
    python deaify.py --input file.txt --output cleaned.txt
    python deaify.py --score-only file.txt
    python deaify.py --aggressive file.txt
    python deaify.py --vocab-only file.txt
    python deaify.py --preserve-format file.txt
    python deaify.py --linkedin file.txt
    echo "text" | python deaify.py -

Modes:
    --standard (default)   All automatable layers
    --aggressive           Maximum automated changes
    --vocab-only           Only replace banned vocabulary
    --score-only           Report only, no changes
    --preserve-format      Skip structural changes
    --linkedin             LinkedIn-specific: platform patterns + standard treatment
    --email                Email-specific: opener/body/closer patterns + standard
    --twitter              Twitter/X-specific: platform patterns + standard

Exit codes:
    0 — Text passes (score <= 3 after processing)
    1 — Text still needs manual work (score > 3)
    2 — Error
"""

import re
import sys
import argparse
from pathlib import Path
from copy import deepcopy

try:
    from patterns import (
        TIER1_REPLACEMENTS, TRANSITION_OPENERS, HOLLOW_OPENERS,
        HOLLOW_CLOSERS, SETUP_PHRASES, CONTRACTIONS,
        LINKEDIN_PATTERNS, EMAIL_OPENERS, EMAIL_BODY, EMAIL_CLOSERS,
        TWITTER_PATTERNS,
        count_contractions, word_count
    )
    from score import score_text, print_report
except ImportError:
    print("Error: Run from the scripts/ directory or ensure patterns.py and score.py are in the same folder.",
          file=sys.stderr)
    sys.exit(2)


# ─────────────────────────────────────────────
# LAYER 1: VOCABULARY PURGE
# ─────────────────────────────────────────────

def apply_vocabulary_purge(text, aggressive=False):
    """Replace Tier 1 AI vocabulary with natural equivalents."""
    result = text

    for pattern, replacement in TIER1_REPLACEMENTS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Additional aggressive replacements
    if aggressive:
        aggressive_replacements = {
            r"\bensure\b": "make sure",
            r"\bEnsure\b": "Make sure",
            r"\bprovide\b(?=\s+(?:a|an|the|some))": "give",
            r"\bsignificant(?:ly)?\b": "major",
            r"\bsubstantial(?:ly)?\b": "large",
            r"\bnotable\b": "",
            r"\bcrucial\b": "key",
            r"\bvital\b": "key",
            r"\bessential\b": "key",
            r"\bfundamental\b": "core",
            r"\bdiverse\b": "varied",
            r"\bvarious\b": "",
            r"\bnumerous\b": "many",
            r"\bdynamic\b(?!.*(?:physics|force|system))": "changing",
        }
        for pattern, replacement in aggressive_replacements.items():
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


# ─────────────────────────────────────────────
# LAYER 2: TRANSITION OPENER REMOVAL
# ─────────────────────────────────────────────

def apply_transition_cleanup(text):
    """Remove or replace AI transition openers at sentence starts."""
    result = text
    lines = result.split('\n')
    cleaned_lines = []

    for line in lines:
        cleaned_line = line
        for pattern, replacement in TRANSITION_OPENERS:
            # Apply to sentence-starting positions
            cleaned_line = re.sub(r'(?<=[.!?]\s)' + pattern[1:], replacement,
                                  cleaned_line, flags=re.IGNORECASE)
            # Apply to line starts
            cleaned_line = re.sub(pattern, replacement, cleaned_line, flags=re.IGNORECASE)
        cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)


# ─────────────────────────────────────────────
# LAYER 3: SETUP PHRASE REMOVAL
# ─────────────────────────────────────────────

def apply_setup_phrase_cleanup(text):
    """Remove hollow setup phrases that precede the actual content."""
    result = text
    for pattern, replacement in SETUP_PHRASES:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Capitalize first word if setup phrase was removed at sentence start
    result = re.sub(r'(?<=[.!?]\s)([a-z])', lambda m: m.group(1).upper(), result)

    return result


# ─────────────────────────────────────────────
# LAYER 4: HOLLOW OPENER/CLOSER REMOVAL
# ─────────────────────────────────────────────

def apply_hollow_opener_cleanup(text):
    """Remove AI compliment openers."""
    result = text
    for pattern in HOLLOW_OPENERS:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE)

    # Clean up any resulting double spaces or leading whitespace
    result = re.sub(r'^\s+', '', result)
    result = re.sub(r'\n{3,}', '\n\n', result)

    # Capitalize first letter after removal
    if result and result[0].islower():
        result = result[0].upper() + result[1:]

    return result


def apply_hollow_closer_cleanup(text):
    """Remove AI sign-off phrases."""
    result = text
    for pattern in HOLLOW_CLOSERS:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.MULTILINE)

    result = result.rstrip()
    return result


# ─────────────────────────────────────────────
# LAYER 5: CONTRACTION CONVERSION
# ─────────────────────────────────────────────

def apply_contractions(text, context="conversational"):
    """Convert formal uncontracted forms to natural contractions."""
    if context not in ("conversational", "informal", "blog", "social", "email"):
        return text  # Don't apply to formal/technical contexts

    result = text
    for pattern, replacement in CONTRACTIONS:
        result = re.sub(pattern, replacement, result)

    return result


# ─────────────────────────────────────────────
# LAYER 4b: LINKEDIN-SPECIFIC PATTERNS
# ─────────────────────────────────────────────

def apply_linkedin_patterns(text):
    """Apply LinkedIn-specific AI pattern removal."""
    result = text
    lines = result.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_line = line
        for pattern, replacement in LINKEDIN_PATTERNS:
            cleaned_line = re.sub(pattern, replacement, cleaned_line,
                                  flags=re.IGNORECASE | re.MULTILINE)
        cleaned_lines.append(cleaned_line)
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result


def apply_email_patterns(text):
    """Apply email-specific AI pattern removal (openers, body phrases, closers)."""
    result = text

    # Openers: apply to start of text
    for pattern, replacement in EMAIL_OPENERS:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE | re.MULTILINE)

    # Body phrases: apply everywhere
    for pattern, replacement in EMAIL_BODY:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Closers: apply to end of text
    for pattern, _ in EMAIL_CLOSERS:
        result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.MULTILINE)

    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()


def apply_twitter_patterns(text):
    """Apply Twitter/X-specific AI pattern removal."""
    result = text
    lines = result.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_line = line
        for pattern, replacement in TWITTER_PATTERNS:
            cleaned_line = re.sub(pattern, replacement, cleaned_line,
                                  flags=re.IGNORECASE | re.MULTILINE)
        cleaned_lines.append(cleaned_line)
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()


# ─────────────────────────────────────────────
# EM-DASH REDUCTION
# ─────────────────────────────────────────────

def apply_em_dash_reduction(text, words):
    """Reduce em-dash overuse in long texts."""
    dash_count = len(re.findall(r'—', text))
    per_500 = dash_count / max(words / 500, 1)

    if per_500 <= 2:
        return text  # Fine

    # Replace excess em-dashes with comma or period (heuristic)
    # This is a best-effort reduction — full fix requires LLM
    result = text
    replacements_made = 0
    max_to_replace = max(0, dash_count - int(words / 500) * 2)

    for _ in range(max_to_replace):
        # Replace em-dash between clauses with comma
        match = re.search(r'(\w)\s*—\s*(\w)', result)
        if not match:
            break
        result = result[:match.start(1)+1] + ', ' + result[match.end(2)-1:]
        replacements_made += 1

    return result


# ─────────────────────────────────────────────
# CLEANUP UTILITIES
# ─────────────────────────────────────────────

def clean_rewrite_markers(text):
    """Remove [REWRITE: ...] markers and replace with empty string for manual handling."""
    # Flag these for the report but leave as-is so user knows what needs manual work
    markers = re.findall(r'\[REWRITE: [^\]]+\]', text)
    return text, markers


def clean_artifacts(text):
    """Fix common artifacts from automated replacements."""
    result = text
    # Fix double spaces
    result = re.sub(r'  +', ' ', result)
    # Fix space before punctuation
    result = re.sub(r'\s+([.,;:!?])', r'\1', result)
    # Fix multiple blank lines
    result = re.sub(r'\n{3,}', '\n\n', result)
    # Fix " ," and " ." artifacts
    result = re.sub(r'\s+,', ',', result)
    result = re.sub(r'\s+\.', '.', result)
    # Capitalize sentence starts after transition cleanup
    result = re.sub(r'([.!?]\s+)([a-z])', lambda m: m.group(1) + m.group(2).upper(), result)
    return result.strip()


# ─────────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────────

def process_text(text, mode="standard", context="conversational"):
    """
    Run the automated de-AI-fy pipeline on text.

    Applies:
    - Layer 1: Vocabulary purge
    - Layer 2: Transition opener removal
    - Layer 3: Setup phrase cleanup
    - Layer 4: Hollow opener/closer removal
    - Layer 5: Contraction conversion
    - Layer 5: Em-dash reduction

    Does NOT apply:
    - Layer 3: Structural flattening (requires LLM judgment)
    - Layer 6: Authenticity injection (requires LLM judgment)
    """
    if mode == "score-only":
        return text, []

    # Score before
    score_before = score_text(text)

    result = text
    changes = []

    # Layer 1: Vocabulary
    if mode != "preserve-format" or True:  # Vocab always runs
        vocab_cleaned = apply_vocabulary_purge(result, aggressive=(mode == "aggressive"))
        if vocab_cleaned != result:
            changes.append("Vocabulary: replaced AI terms")
        result = vocab_cleaned

    # Layer 2: Transitions
    if mode in ("standard", "aggressive", "linkedin", "email", "twitter"):
        trans_cleaned = apply_transition_cleanup(result)
        if trans_cleaned != result:
            changes.append("Structure: removed AI transition openers")
        result = trans_cleaned

    # Layer 3: Setup phrases
    if mode in ("standard", "aggressive", "linkedin", "email", "twitter"):
        setup_cleaned = apply_setup_phrase_cleanup(result)
        if setup_cleaned != result:
            changes.append("Tone: removed hollow setup phrases")
        result = setup_cleaned

    # Layer 4: Hollow openers/closers
    if mode in ("standard", "aggressive", "linkedin", "email", "twitter"):
        opener_cleaned = apply_hollow_opener_cleanup(result)
        if opener_cleaned != result:
            changes.append("Tone: removed hollow compliment opener")
        result = opener_cleaned

        closer_cleaned = apply_hollow_closer_cleanup(result)
        if closer_cleaned != result:
            changes.append("Tone: removed AI sign-off closer")
        result = closer_cleaned

    # Layer 4b: Platform-specific patterns
    if mode == "linkedin":
        platform_cleaned = apply_linkedin_patterns(result)
        if platform_cleaned != result:
            changes.append("LinkedIn: removed platform-specific AI patterns")
        result = platform_cleaned
    elif mode == "email":
        platform_cleaned = apply_email_patterns(result)
        if platform_cleaned != result:
            changes.append("Email: removed email-specific AI patterns")
        result = platform_cleaned
    elif mode == "twitter":
        platform_cleaned = apply_twitter_patterns(result)
        if platform_cleaned != result:
            changes.append("Twitter: removed platform-specific AI patterns")
        result = platform_cleaned

    # Layer 5: Contractions (standard+ only)
    if mode in ("standard", "aggressive", "linkedin", "email", "twitter") and context in ("conversational", "blog", "email", "social"):
        if count_contractions(result) == 0:
            contracted = apply_contractions(result, context)
            if contracted != result:
                changes.append("Structure: added natural contractions")
            result = contracted

    # Em-dash reduction
    words = word_count(result)
    dash_cleaned = apply_em_dash_reduction(result, words)
    if dash_cleaned != result:
        changes.append("Rhythm: reduced em-dash overuse")
    result = dash_cleaned

    # Cleanup artifacts
    result = clean_artifacts(result)

    # Collect rewrite markers (items needing manual attention)
    result, manual_items = clean_rewrite_markers(result)

    # Score after
    score_after = score_text(result)

    return result, {
        "changes": changes,
        "manual_items": manual_items,
        "score_before": score_before["final"],
        "score_after": score_after["final"],
        "score_after_full": score_after,
    }


# ─────────────────────────────────────────────
# DIFF SUMMARY
# ─────────────────────────────────────────────

def print_summary(original, result, meta):
    print("\n" + "═" * 50)
    print("  DE-AI-FY COMPLETE")
    print("═" * 50)
    print(f"  Score before:  {meta['score_before']}/10")
    print(f"  Score after:   {meta['score_after']}/10")
    delta = meta['score_before'] - meta['score_after']
    print(f"  Improvement:   -{delta:.1f} points")
    print("─" * 50)

    if meta['changes']:
        print("  AUTOMATED CHANGES APPLIED:")
        for change in meta['changes']:
            print(f"    ✓ {change}")
    else:
        print("  No automated changes needed.")

    if meta['manual_items']:
        print("─" * 50)
        print("  MANUAL REWRITE NEEDED:")
        for item in meta['manual_items']:
            print(f"    ⚠ {item}")

    if meta['score_after'] > 5:
        print("─" * 50)
        print("  ⚠  Score still elevated. Manual rewrite needed for:")
        remaining = meta['score_after_full']['fingerprints']
        for fp in remaining:
            print(f"     • {fp}")

    print("═" * 50 + "\n")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="De-AI-fy text: strip AI fingerprints automatically"
    )
    parser.add_argument("input", nargs="?", default="-",
                        help="Input file path, or - for stdin")
    parser.add_argument("--output", "-o",
                        help="Output file path (default: print to stdout)")
    parser.add_argument("--score-only", action="store_true",
                        help="Score only, no changes")
    parser.add_argument("--aggressive", action="store_true",
                        help="Maximum automated changes")
    parser.add_argument("--vocab-only", action="store_true",
                        help="Vocabulary replacement only")
    parser.add_argument("--preserve-format", action="store_true",
                        help="Skip structural/formatting changes")
    parser.add_argument("--linkedin", action="store_true",
                        help="LinkedIn mode: apply platform-specific patterns + standard treatment")
    parser.add_argument("--email", action="store_true",
                        help="Email mode: opener/body/closer patterns + standard treatment")
    parser.add_argument("--twitter", action="store_true",
                        help="Twitter/X mode: platform patterns + standard treatment")
    parser.add_argument("--context", default="conversational",
                        choices=["conversational", "blog", "email", "social", "technical", "formal"],
                        help="Writing context (affects contraction application)")
    parser.add_argument("--quiet", "-q", action="store_true",
                        help="Suppress summary output")
    args = parser.parse_args()

    # Read input
    try:
        if args.input == "-" or not args.input:
            text = sys.stdin.read()
        else:
            text = Path(args.input).read_text(encoding="utf-8")
    except (FileNotFoundError, IOError) as e:
        print(f"Error reading input: {e}", file=sys.stderr)
        return 2

    # Determine mode
    if args.score_only:
        mode = "score-only"
    elif args.aggressive:
        mode = "aggressive"
    elif args.vocab_only:
        mode = "vocab-only"
    elif args.preserve_format:
        mode = "preserve-format"
    elif args.linkedin:
        mode = "linkedin"
    elif args.email:
        mode = "email"
    elif args.twitter:
        mode = "twitter"
    else:
        mode = "standard"

    # Score-only mode
    if mode == "score-only":
        result = score_text(text)
        print_report(result)
        return 0 if result['final'] <= 3 else 1

    # Process
    cleaned, meta = process_text(text, mode=mode, context=args.context)

    # Output
    if args.output:
        Path(args.output).write_text(cleaned, encoding="utf-8")
        if not args.quiet:
            print(f"Output written to: {args.output}")
    else:
        print(cleaned)

    # Summary
    if not args.quiet:
        print_summary(text, cleaned, meta)

    return 0 if meta['score_after'] <= 3 else 1


if __name__ == "__main__":
    sys.exit(main())
