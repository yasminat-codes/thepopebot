"""
score.py — AI Probability Scorer for de-ai-fy

Scores a piece of text on a 1-10 scale for AI probability.
Uses weighted category scoring based on the detection signatures in references/SCORING-RUBRIC.md.

Usage:
    python score.py <path-to-file>
    python score.py --text "paste text here"
    echo "text" | python score.py -
"""

import re
import sys
import argparse
from pathlib import Path

try:
    from patterns import (
        TIER1_REPLACEMENTS, TRANSITION_OPENERS, HOLLOW_OPENERS,
        HOLLOW_CLOSERS, SETUP_PHRASES, PASSIVE_PATTERNS,
        get_sentence_lengths, sentence_length_variance,
        count_contractions, word_count, EM_DASH_PATTERN, EM_DASH_THRESHOLD
    )
except ImportError:
    # Fallback if running standalone
    def get_sentence_lengths(text):
        sentences = re.split(r'[.!?]+', text)
        return [len(s.split()) for s in sentences if len(s.split()) > 2]

    def sentence_length_variance(lengths):
        if not lengths:
            return 0
        mean = sum(lengths) / len(lengths)
        return sum((l - mean) ** 2 for l in lengths) / len(lengths)

    def count_contractions(text):
        patterns = [r"\b\w+'(t|s|re|ve|ll|d|m)\b"]
        return sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)

    def word_count(text):
        return len(text.split())

    EM_DASH_PATTERN = r"—"
    EM_DASH_THRESHOLD = 3


# ─────────────────────────────────────────────
# DETECTION FUNCTIONS
# ─────────────────────────────────────────────

def count_grammar_patterns(text):
    """Count AI grammar construction hits."""
    patterns = [
        r"\bnot only\b.{1,60}\bbut also\b",
        r"^[Ww]hile .{1,80},",
        r"\bit is (?:essential|crucial|vital|important|necessary) that\b",
        r"\bit is (?:clear|evident|apparent|worth noting) that\b",
        r"\bby \w+ing .{1,60}, (?:organizations?|teams?|leaders?|companies|businesses?) can\b",
        r"\bmore .{1,20} than ever\b",
        r"\bnow more than ever\b",
        r"\bnever been more (?:important|critical|relevant|urgent)\b",
        r"\bplay(?:s|ed)? a (?:significant|key|crucial|pivotal|important) role in\b",
    ]
    count = 0
    for p in patterns:
        count += len(re.findall(p, text, re.IGNORECASE | re.MULTILINE))
    return count


def count_parallel_triplets(text):
    """Count 'X, Y, and Z' triplet constructions (AI overuses these)."""
    return len(re.findall(r'\b\w+, \w+, and \w+\b', text, re.IGNORECASE))


def has_linkedin_format(text):
    """Detect LinkedIn one-sentence-per-line formatting (5+ consecutive single-sentence lines)."""
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if len(lines) < 5:
        return False
    consecutive = 0
    max_consecutive = 0
    for line in lines:
        # A "LinkedIn line" is short (< 120 chars) and ends with punctuation or is one sentence
        sentences = re.split(r'[.!?]+', line)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) <= 1 and len(line) < 140:
            consecutive += 1
            max_consecutive = max(max_consecutive, consecutive)
        else:
            consecutive = 0
    return max_consecutive >= 5


def count_tier1_hits(text):
    """Count Tier 1 AI vocabulary hits."""
    tier1_words = [
        # Corporate AI words
        r"\bdelve(?: into)?\b", r"\butilize[sd]?\b", r"\butiliz(?:es|ing|ation)\b",
        r"\bsynerg(?:y|ies)\b", r"\bholistic approach\b", r"\bparadigm shift\b",
        r"\bgame[- ]changer\b", r"\bdeep dive\b", r"\bcircle back\b", r"\btouch base\b",
        r"\bvalue[- ]add\b", r"\bactionable insights\b", r"\bseamless(?:ly)?\b",
        r"\bcutting[- ]edge\b", r"\bstate[- ]of[- ]the[- ]art\b",
        r"\bpain points\b", r"\blow[- ]hanging fruit\b", r"\bmove the needle\b",
        r"\bmoving the needle\b", r"\bthink outside the box\b",
        r"\bin today's .{0,30} landscape\b",
        r"\bit'?s worth noting that\b", r"\bit is worth noting that\b",
        r"\bit'?s important to note that\b", r"\bit is important to note that\b",
        r"\bat the end of the day\b", r"\bgoing forward\b", r"\bmoving forward\b",
        r"\bleverage[sd]?\b(?=\s+(?:the|this|these|our|your|a|an))",
        r"\bfoster(?:ed|ing|s)?\b(?!.*(?:parent|child|adopt))",
        r"\bfacilitate[sd]?\b", r"\bempower(?:ed|ing|s)?\b",
        r"\brobust\b", r"\bstreamline[sd]?\b", r"\boptimize[sd]?\b",
        r"\bstakeholders\b", r"\bdeliverables\b", r"\btransformative\b",
        r"\binnovative\b", r"\bscalable\b", r"\bcomprehensive\b",
        # Poetic AI words (v2 additions)
        r"\btapestry\b", r"\bvibrant\b", r"\brealm\b", r"\bbeacon\b",
        r"\bbustling\b", r"\bnestled\b", r"\bdaunting\b", r"\bpivotal\b",
        r"\bmeticulous(?:ly)?\b", r"\bembark\b", r"\ba testament to\b",
        r"\bever[- ]evolving\b", r"\bunprecedented\b", r"\bspearhead\b",
        r"\bpave the way\b", r"\bnuanced\b", r"\bimpactful\b", r"\btreasure trove\b",
        r"\bshed light on\b", r"\bharnessing\b", r"\bunleash\b", r"\bunlock\b",
        r"\belevate\b", r"\baugment\b", r"\breimag(?:ine|ined|ining)\b",
        r"\bunderscores?\b", r"\bshowcas(?:e|ing)\b", r"\baligns with\b",
        # Missing buzzwords (v2.1 additions)
        r"\bplethora\b", r"\bmyriad\b", r"\blearnings\b", r"\bgroundbreaking\b",
        r"\boverarching\b", r"\bsalient\b", r"\bmultifaceted\b", r"\bnoteworthy\b",
        r"\bideation\b", r"\bgranular\b", r"\bforward[- ]thinking\b",
        r"\bfuture[- ]proof\b", r"\bworld[- ]class\b", r"\bbest[- ]in[- ]class\b",
        r"\bindustry[- ]leading\b", r"\bthought leadership\b",
        # Startup/strategy jargon (v2.3 additions)
        r"\bdemocratize[sd]?\b", r"\bflywheel\b", r"\binflection point\b",
        r"\bnorth star\b", r"\blean into\b", r"\btable stakes\b",
        r"\bvalue proposition\b", r"\bbespoke\b", r"\bcurated\b",
        r"\bevangelize[sd]?\b", r"\bmission[- ]critical\b", r"\bgo[- ]to[- ]market\b",
        r"\bgrowth mindset\b", r"\bstep[- ]change\b", r"\bmission[- ]driven\b",
        r"\bdata[- ]driven\b", r"\bpurpose[- ]driven\b", r"\bcore competenc(?:y|ies)\b",
        r"\bno[- ]brainer\b",
        # GPTZero statistical hard-bans
        r"\bplay(?:s|ed)? a (?:significant|key|crucial|pivotal) role in\b",
        r"\baims to explore\b",
        # Grammar AI constructions
        r"\bnot only\b.{1,40}\bbut also\b",
        r"\bmore .{1,15} than ever\b",
        r"\bnever been more (?:important|critical|relevant)\b",
        r"\bit is (?:essential|crucial|vital|important) that\b",
    ]
    count = 0
    for pattern in tier1_words:
        matches = re.findall(pattern, text, re.IGNORECASE)
        count += len(matches)
    return count


def count_transitions(text):
    """Count AI transition openers."""
    transitions = [
        "Furthermore", "Additionally", "Moreover", "In addition",
        "Nevertheless", "Nonetheless", "Consequently", "Subsequently",
        "Therefore", "Thus", "Hence", "Indeed", "Certainly", "Undoubtedly",
        "Importantly", "Interestingly", "Notably"
    ]
    count = 0
    for t in transitions:
        # Count both sentence-start and anywhere
        count += len(re.findall(r'\b' + t + r'\b', text, re.IGNORECASE))
    return count


def count_setup_phrases(text):
    """Count hollow setup phrases."""
    setups = [
        r"it'?s important to (?:note|understand|recognize)",
        r"it'?s worth (?:noting|mentioning|considering|highlighting)",
        r"it should be noted",
        r"it'?s crucial to (?:note|understand)",
        r"with that in mind",
        r"that being said",
        r"having said that",
        r"without further ado",
        r"at this juncture",
        r"as we can see",
        r"as previously mentioned",
        r"needless to say",
        r"it goes without saying",
    ]
    count = 0
    for pattern in setups:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def count_passive(text):
    """Estimate passive voice constructions."""
    passive_patterns = [
        r"\b(?:is|are|was|were|been|be|being)\s+\w+ed\b",
        r"\b(?:has|have|had)\s+been\s+\w+ed\b",
        r"\bcan\s+be\s+\w+ed\b",
        r"\bshould\s+be\s+\w+ed\b",
        r"\bwill\s+be\s+\w+ed\b",
    ]
    count = 0
    for pattern in passive_patterns:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count


def count_em_dashes(text):
    """Count em-dashes."""
    return len(re.findall(r'—', text))


def count_headers(text):
    """Count markdown headers."""
    return len(re.findall(r'^#{1,6}\s+.+$', text, re.MULTILINE))


def count_bullets(text):
    """Count bullet points."""
    return len(re.findall(r'^[\s]*[-*•]\s+', text, re.MULTILINE))


def has_key_takeaways(text):
    """Check for AI summary sections."""
    patterns = [
        r'##?\s+(?:key\s+)?takeaways?\b',
        r'##?\s+(?:in\s+)?conclusion\b',
        r'##?\s+(?:to\s+)?summarize?\b',
        r'##?\s+summary\b',
        r'##?\s+introduction\b',
        r'##?\s+overview\b',
    ]
    for p in patterns:
        if re.search(p, text, re.IGNORECASE):
            return True
    return False


def has_hollow_opener(text):
    """Check if text opens with AI compliment."""
    patterns = [
        r'^(?:Great|Excellent|Wonderful|Fantastic|Perfect|Amazing)\s+(?:question|point|observation)',
        r'^(?:Absolutely|Certainly|Of course)[!.]',
        r'^I\'?d be happy to (?:help|assist)',
        r'^That\'?s? (?:a )?(?:great|excellent|wonderful|interesting)\s+(?:question|point)',
    ]
    first_para = text[:200]
    for p in patterns:
        if re.search(p, first_para, re.IGNORECASE):
            return True
    return False


def has_hollow_closer(text):
    """Check if text ends with AI sign-off."""
    patterns = [
        r'I hope this (?:helps|clarifies)',
        r'Feel free to (?:reach out|ask)',
        r'Please don\'?t hesitate to',
        r'I look forward to hearing',
        r'Have a (?:great|wonderful|nice) day',
        r'It has been (?:a )?pleasure (?:assisting|helping)',
    ]
    last_para = text[-200:]
    for p in patterns:
        if re.search(p, last_para, re.IGNORECASE):
            return True
    return False


# ─────────────────────────────────────────────
# SCORING ENGINE
# ─────────────────────────────────────────────

def score_vocabulary(text, words):
    """Score vocabulary category (0-10)."""
    hits = count_tier1_hits(text)
    per_500 = hits / max(words / 500, 1)
    if per_500 == 0:
        return 1
    elif per_500 < 2:
        return 2
    elif per_500 < 4:
        return 4
    elif per_500 < 6:
        return 6
    elif per_500 < 10:
        return 7
    elif per_500 < 15:
        return 8
    elif per_500 < 20:
        return 9
    return 10


def score_structure(text, words):
    """Score sentence structure category (0-10)."""
    points = 0

    # Sentence length variance
    lengths = get_sentence_lengths(text)
    if lengths:
        variance = sentence_length_variance(lengths)
        if variance < 15:
            points += 3
        elif variance < 30:
            points += 1

    # Contractions (low rate = AI signal in conversational text)
    contraction_count = count_contractions(text)
    if words > 200:
        contraction_rate = contraction_count / max(words / 100, 1)
        if contraction_rate == 0:
            points += 2
        elif contraction_rate < 0.5:
            points += 1

    # Transition openers
    transitions = count_transitions(text)
    per_500 = transitions / max(words / 500, 1)
    if per_500 >= 4:
        points += 3
    elif per_500 >= 2:
        points += 2

    # Passive voice
    passive = count_passive(text)
    per_500_passive = passive / max(words / 500, 1)
    if per_500_passive >= 5:
        points += 2
    elif per_500_passive >= 3:
        points += 1

    # Em-dash overuse
    dashes = count_em_dashes(text)
    per_500_dash = dashes / max(words / 500, 1)
    if per_500_dash >= 3:
        points += 1

    # Grammar patterns (AI constructions)
    grammar_hits = count_grammar_patterns(text)
    per_500_grammar = grammar_hits / max(words / 500, 1)
    if per_500_grammar >= 3:
        points += 2
    elif per_500_grammar >= 1:
        points += 1

    # Parallel triplet overuse
    triplets = count_parallel_triplets(text)
    per_500_triplets = triplets / max(words / 500, 1)
    if per_500_triplets >= 3:
        points += 1

    # LinkedIn one-sentence-per-line format
    if has_linkedin_format(text):
        points += 2

    return min(10, max(1, points))


def score_formatting(text, words):
    """Score formatting category (0-10)."""
    points = 0
    headers = count_headers(text)
    bullets = count_bullets(text)

    # Headers in short content
    if headers > 2 and words < 1000:
        points += 3
    elif headers > 0 and words < 500:
        points += 2

    # Bullet overuse
    bullet_ratio = bullets / max(words / 10, 1)
    if bullet_ratio > 0.3:
        points += 2
    elif bullet_ratio > 0.2:
        points += 1

    # Key takeaways / conclusion headers
    if has_key_takeaways(text):
        points += 2

    return min(10, max(1, points))


def score_tone(text, words):
    """Score tone category (0-10)."""
    points = 0

    if has_hollow_opener(text):
        points += 3

    if has_hollow_closer(text):
        points += 2

    setups = count_setup_phrases(text)
    per_500 = setups / max(words / 500, 1)
    if per_500 >= 4:
        points += 3
    elif per_500 >= 2:
        points += 2

    # Vague expert appeal
    vague_patterns = [
        r"\bexperts? (?:agree|say|note|suggest|recommend)\b",
        r"\bstudies? (?:show|suggest|indicate|demonstrate|have shown)\b",
        r"\bresearch (?:suggests?|indicates?|shows?)\b",
        r"\bmany (?:experts?|studies?|researchers?|people)\b",
    ]
    vague_count = sum(len(re.findall(p, text, re.IGNORECASE)) for p in vague_patterns)
    if vague_count >= 3:
        points += 2
    elif vague_count >= 1:
        points += 1

    return min(10, max(1, points))


def compute_final_score(vocab, structure, formatting, tone):
    """Compute weighted final score."""
    return (vocab * 0.25 + structure * 0.20 + formatting * 0.20 + tone * 0.20
            + (vocab + structure) / 2 * 0.15)


def score_text(text):
    """Full scoring analysis. Returns score dict and overall score."""
    words = word_count(text)

    vocab_score = score_vocabulary(text, words)
    struct_score = score_structure(text, words)
    format_score = score_formatting(text, words)
    tone_score = score_tone(text, words)
    final = round(compute_final_score(vocab_score, struct_score, format_score, tone_score), 1)
    final = min(10, max(1, final))

    fingerprints = []
    tier1_hits = count_tier1_hits(text)
    if tier1_hits:
        fingerprints.append(f"AI vocabulary: {tier1_hits} hits")
    transitions = count_transitions(text)
    if transitions:
        fingerprints.append(f"Transition openers: {transitions}")
    setups = count_setup_phrases(text)
    if setups:
        fingerprints.append(f"Setup phrases: {setups}")
    if has_hollow_opener(text):
        fingerprints.append("Hollow compliment opener")
    if has_hollow_closer(text):
        fingerprints.append("AI sign-off closer")
    headers = count_headers(text)
    if headers and words < 1000:
        fingerprints.append(f"Headers in short content: {headers}")
    if has_key_takeaways(text):
        fingerprints.append("Key Takeaways/Summary section")
    dashes = count_em_dashes(text)
    per_500 = dashes / max(words / 500, 1)
    if per_500 >= EM_DASH_THRESHOLD:
        fingerprints.append(f"Em-dash overuse: {dashes} in {words} words")
    contraction_count = count_contractions(text)
    if words > 200:
        contraction_rate = contraction_count / max(words / 100, 1)
        if contraction_rate < 0.5:  # less than 0.5 contractions per 100 words
            fingerprints.append(f"Very few contractions ({contraction_count} in {words} words)")

    grammar_hits = count_grammar_patterns(text)
    if grammar_hits:
        fingerprints.append(f"AI grammar constructions: {grammar_hits} hits (not only/but also, while X Y, it is [adj] that...)")

    triplets = count_parallel_triplets(text)
    per_500_triplets = triplets / max(words / 500, 1)
    if per_500_triplets >= 2:
        fingerprints.append(f"Parallel triplet overuse: {triplets} in {words} words (X, Y, and Z pattern)")

    if has_linkedin_format(text):
        fingerprints.append("LinkedIn one-sentence-per-line formatting detected")

    return {
        "final": final,
        "vocabulary": vocab_score,
        "structure": struct_score,
        "formatting": format_score,
        "tone": tone_score,
        "word_count": words,
        "fingerprints": fingerprints,
    }


# ─────────────────────────────────────────────
# REPORTING
# ─────────────────────────────────────────────

def label(score):
    labels = {
        1: "Undetectable", 2: "Near-human", 3: "Lightly marked",
        4: "Noticeable", 5: "Moderate", 6: "Strong signal",
        7: "Heavy", 8: "Very heavy", 9: "Textbook AI", 10: "Archetypal AI"
    }
    return labels.get(round(score), "Unknown")


def print_report(result):
    print("\n" + "─" * 50)
    print(f"  AI PROBABILITY SCORE: {result['final']}/10 — {label(result['final'])}")
    print("─" * 50)
    print(f"  Vocabulary:  {result['vocabulary']}/10")
    print(f"  Structure:   {result['structure']}/10")
    print(f"  Formatting:  {result['formatting']}/10")
    print(f"  Tone:        {result['tone']}/10")
    print(f"  Word count:  {result['word_count']}")
    print("─" * 50)
    if result['fingerprints']:
        print("  FINGERPRINTS DETECTED:")
        for fp in result['fingerprints']:
            print(f"    • {fp}")
    else:
        print("  No significant fingerprints detected.")
    print("─" * 50)

    score = result['final']
    if score < 1.5:
        rec = "Run Zero-Point Protocol to reach 0.x. → references/ZERO-POINT-PROTOCOL.md"
    elif score <= 3:
        rec = "Vocabulary pass + Zero-Point Protocol."
    elif score <= 5:
        rec = "Layers 1-4 + Zero-Point Protocol."
    elif score <= 7:
        rec = "Full 7-layer treatment + Zero-Point Protocol."
    elif score <= 9:
        rec = "Full treatment + authenticity injection + ZP."
    else:
        rec = "Reconstruct from scratch using Zero-Point principles."

    print(f"  RECOMMENDATION: {rec}")
    print("─" * 50 + "\n")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Score text for AI probability (1-10)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("file", nargs="?", help="Path to text file (or - for stdin)")
    group.add_argument("--text", "-t", help="Text to score directly")
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif args.file == "-":
        text = sys.stdin.read()
    elif not sys.stdin.isatty() and not args.file:
        text = sys.stdin.read()
    elif args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        parser.print_help()
        sys.exit(1)

    result = score_text(text)
    print_report(result)
    return 0 if result['final'] <= 3 else 1


if __name__ == "__main__":
    sys.exit(main())
