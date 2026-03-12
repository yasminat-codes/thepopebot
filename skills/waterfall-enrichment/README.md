# Waterfall Enrichment

Multi-source lead enrichment pipeline for cold email campaigns. Cascades through 7 email finders, verifies with Reoon, resolves catchall with Email Verify. Optimized for <3% bounce rate and cost efficiency.

## Architecture

```
FINDERS (cascade — stop on first find):
  Tomba → Muraena → Icypeas → Voila Norbert → Nimbler → Anymailfinder → Findymail

VERIFIERS (every found email):
  Reoon (primary — mandatory) → Email Verify (catchall only — recommended)
```

## Quick Start

```bash
# Set API keys (Reoon required + at least 1 finder)
export REOON_API_KEY="your-key"
export TOMBA_API_KEY="your-key"
export TOMBA_SECRET="your-secret"

# Install dependencies
pip install requests

# Single lead
python3 scripts/enrich.py --first-name John --last-name Doe --domain example.com

# Batch from CSV
python3 scripts/enrich.py --input leads.csv --output enriched.csv

# Resume interrupted batch
python3 scripts/enrich.py --input leads.csv --output enriched.csv --resume

# Split large files first
python3 scripts/split_csv.py --input big_list.csv --chunk-size 5000

# Generate report
python3 scripts/report.py --input enriched.csv
```

## Flow Per Lead

1. Try finders in cascade order until one returns an email
2. Verify found email with Reoon
3. Valid → DB (confidence 90-100)
4. Catchall → Email Verify → Valid (70-85) or Risky (50-69) or Discard (0)
5. Not found → mark as not_found, move to next lead

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill documentation — full architecture and workflow |
| `scripts/enrich.py` | Enrichment engine (find → verify → catchall pipeline) |
| `scripts/report.py` | Report generator (finder + verifier performance) |
| `scripts/split_csv.py` | Split large CSVs into chunks for batch processing |
| `assets/config.json` | Default configuration (finders, verifiers, costs, limits) |
| `assets/schemas/` | JSON schemas for input and output formats |
| `references/PROVIDER-API-REFERENCE.md` | All 9 provider API docs (7 finders + 2 verifiers) |
| `references/ERROR-HANDLING.md` | Error codes, retry logic, graceful degradation |
| `references/REPORTING.md` | Report format, metrics, benchmarks |
| `references/CATCH-ALL-GUIDE.md` | Catchall domain handling and campaign strategy |
| `references/COST-OPTIMIZATION.md` | Cost tracking, optimization strategies, batch estimates |
| `examples/sample-enrichment.md` | End-to-end usage examples |

## API Keys

```bash
# FINDERS (at least 1 required — more = better coverage)
TOMBA_API_KEY=         TOMBA_SECRET=
MURAENA_API_KEY=
ICYPEAS_API_KEY=
VOILANORBERT_API_KEY=
NIMBLER_API_KEY=
ANYMAILFINDER_API_KEY=
FINDYMAIL_API_KEY=

# VERIFIERS
REOON_API_KEY=          # REQUIRED — primary verifier
EMAILVERIFY_API_KEY=    # Recommended — catchall resolver
```
