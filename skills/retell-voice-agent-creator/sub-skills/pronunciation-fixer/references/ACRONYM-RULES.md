# Acronym Pronunciation Rules

## Core Principle

Most acronyms are spelled letter by letter with dashes between letters. Some well-known
acronyms are pronounced as words. The industry context determines which approach to use.

## Default Rule: Letter by Letter

Spell each letter individually with a dash between them for natural pacing:

| Acronym | Spoken As |
|---------|-----------|
| API | "A-P-I" |
| SDK | "S-D-K" |
| URL | "U-R-L" |
| FAQ | "F-A-Q" |
| CEO | "C-E-O" |
| ROI | "R-O-I" |
| KPI | "K-P-I" |
| CRM | "C-R-M" |
| ETA | "E-T-A" |

## Exceptions: Pronounced as Words

These acronyms are commonly spoken as words, not spelled out:

| Acronym | Spoken As | Notes |
|---------|-----------|-------|
| NASA | "nasa" | Always a word |
| HIPAA | "hip-uh" | Medical/legal |
| SCUBA | "scoo-buh" | Always a word |
| LASER | "lay-zer" | Always a word |
| SaaS | "sass" | Tech industry |
| PaaS | "pass" | Tech industry |
| GAAP | "gap" | Finance |
| REIT | "reet" | Real estate |
| SCOTUS | "sko-tus" | Legal |
| FEMA | "fee-muh" | Government |
| OSHA | "oh-shuh" | Workplace safety |
| EBITDA | "ee-bit-dah" | Finance |

## Dual-Pronunciation Acronyms

Some acronyms can go either way. Choose based on context:

| Acronym | As Letters | As Word | Preferred |
|---------|-----------|---------|-----------|
| SQL | "S-Q-L" | "sequel" | Either, but be consistent |
| GIF | "G-I-F" | "jif" or "gif" | Context-dependent |
| ASAP | "A-S-A-P" | "ay-sap" | Formal = letters, casual = word |
| PIN | "P-I-N" | "pin" | Usually "pin" |
| SIM | "S-I-M" | "sim" | Usually "sim" |

## IPA Dictionary for Acronyms

When using ElevenLabs Turbo v2, generate IPA entries for acronyms that the TTS
engine mispronounces:

```json
{"word": "HIPAA", "alphabet": "ipa", "phoneme": "hIp@"}
{"word": "EBITDA", "alphabet": "ipa", "phoneme": "i:bItdA:"}
{"word": "SaaS", "alphabet": "ipa", "phoneme": "saes"}
```

## Prompt Template

```
ACRONYM PRONUNCIATION RULES:
{for each acronym}
- {ACRONYM}: say "{pronunciation}" ({letter-by-letter or as-a-word})
{end for}
Be consistent - always pronounce these the same way throughout the conversation.
```

## Industry-Specific Acronym Lists

### Medical
Letter-by-letter: EKG, MRI, CBC, ICU, ER, OR, IV, BP, HR, OB-GYN
As words: HIPAA ("hip-uh"), STAT ("stat"), OSHA ("oh-shuh")

### Legal
Letter-by-letter: LLC, LLP, ADA, EEOC, FMLA, FLSA, DOJ, SEC
As words: SCOTUS ("sko-tus"), RICO ("ree-ko")

### Tech
Letter-by-letter: API, SDK, DNS, SSL, SSH, TCP, IP, UI, UX, CI, CD
As words: SaaS ("sass"), PaaS ("pass"), WYSIWYG ("wiz-ee-wig"), AJAX ("ay-jax")

### Finance
Letter-by-letter: ROI, ETF, IPO, SEC, FDIC, APR, APY, IRA, 401k
As words: GAAP ("gap"), EBITDA ("ee-bit-dah"), REIT ("reet"), FICO ("fie-ko")
