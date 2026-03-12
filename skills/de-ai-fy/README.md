# de-ai-fy

Wipes AI fingerprints from text. Makes writing sound like a real person wrote it.

## What It Does

Applies 6 transformation layers to any text:

1. **Vocabulary** — kills "delve into", "utilize", "leverage", "synergy" + 100 more
2. **Sentence Structure** — breaks uniform length, adds fragments, kills passive flood
3. **Formatting** — flattens headers and bullets in conversational content
4. **Tone** — strips hedging, hollow openers, performative balance
5. **Rhythm** — varies sentence length, kills transition sequences
6. **Authenticity** — injects direct opinion, specifics, human voice

## Quick Start

```bash
# Score text for AI probability
python scripts/score.py input.txt

# Run full automated pipeline
python scripts/deaify.py --input input.txt --output clean.txt

# Aggressive mode
python scripts/deaify.py --aggressive --input input.txt

# Pipe mode
cat input.txt | python scripts/deaify.py -
```

## Modes

| Flag | What It Does |
|------|-------------|
| (default) | Standard: all automatable layers |
| `--aggressive` | Maximum changes |
| `--vocab-only` | Vocabulary replacement only |
| `--score-only` | Score and report, no changes |
| `--preserve-format` | Skip structural changes |

## Files

```
de-ai-fy/
├── SKILL.md                  Navigation hub + full documentation
├── references/
│   ├── AI-VOCABULARY.md      Complete banned word list
│   ├── SENTENCE-PATTERNS.md  AI sentence structure guide
│   ├── STRUCTURAL-PATTERNS.md Formatting guide
│   ├── TONE-AND-VOICE.md     Tone detox playbook
│   ├── DETECTION-SIGNATURES.md All AI tells + severity
│   ├── REWRITE-TECHNIQUES.md Humanization techniques
│   ├── BEFORE-AFTER-EXAMPLES.md Real transformations
│   └── SCORING-RUBRIC.md     AI probability scoring
├── scripts/
│   ├── deaify.py             Main pipeline
│   ├── patterns.py           Pattern definitions
│   └── score.py              Scorer
└── assets/word-lists/
    ├── ai-words.json         Machine-readable banned list
    └── replacements.json     Replacement map
```

## AI Score Scale

| Score | Label | Action |
|-------|-------|--------|
| 1-3 | Human-readable | Minor pass only |
| 4-5 | Moderate AI | Standard treatment |
| 6-7 | Heavy AI | Full 6-layer treatment |
| 8-9 | Very heavy | Full treatment + manual rewrite |
| 10 | Archetypal AI | Start over |
