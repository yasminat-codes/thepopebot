# QUICKSTART — de-ai-fy

## Fastest Path: Paste and Go

1. Invoke the `de-ai-fy` skill
2. Paste your text
3. The skill will score it, identify fingerprints, and rewrite it

Done.

---

## Script Path

```bash
# Score only (no changes)
python {baseDir}/scripts/score.py input.txt

# Full automated pass
python {baseDir}/scripts/deaify.py --input input.txt --output output.txt

# Check the result
python {baseDir}/scripts/score.py output.txt
```

---

## What "Automated" vs "Manual" Means

The scripts handle:
- ✓ Vocabulary replacement (delve, utilize, leverage, etc.)
- ✓ Transition opener removal (Furthermore, Additionally, etc.)
- ✓ Setup phrase cleanup (It's worth noting that...)
- ✓ Hollow opener/closer removal (Great question! / I hope this helps!)
- ✓ Contraction conversion in conversational contexts
- ✓ Em-dash overuse reduction

The scripts **can't** handle (needs LLM or manual rewrite):
- ✗ Structural flattening (header/bullet → prose)
- ✗ Sentence length variation
- ✗ Authenticity injection (opinions, specific details)
- ✗ Full paragraph reconstruction

For those — paste text into the skill and ask for full de-AI-fy treatment.

---

## Decision Tree

```
Is the text AI-generated?
├─ Score <= 3 → Already clean. Skip.
├─ Score 4-5 → Run scripts. Check output. Done.
├─ Score 6-7 → Run scripts + paste into skill for manual layers.
├─ Score 8-9 → Full treatment + authenticity injection needed.
└─ Score 10  → Rewrite from scratch. Use AI text as notes only.
```

---

## Common Issues

**`[REWRITE: ...]` markers in output?**
These are items the script flagged for manual rewriting. Replace each with natural human phrasing.

**Score didn't improve much?**
Run the script first, then paste the result into the skill for the layers that need LLM judgment.

**Context flag not working?**
Set `--context` to match your content: `conversational`, `blog`, `email`, `social`, `technical`, `formal`.
