# CHANGELOG — de-ai-fy

## 3.0.0 — 2026-02-22

### Zero-Point Protocol — targeting 0.x (genuinely undetectable)

**New target:** 0.x on GPTZero, Originality.ai, Copyleaks, Winston AI, Turnitin — not just "low AI signal", undetectable.

**New file: references/ZERO-POINT-PROTOCOL.md**
- 7-step injection sequence that closes the gap from 1-2/10 → 0.x
- ZP-1: Lexical surprise injection — unexpected verb/adjective swaps (50+ word swap table)
- ZP-2: Burstiness formula — exact sentence length distribution for beating GPTZero
- ZP-3: Specificity injection — how to ground claims in concrete details (with placeholder system)
- ZP-4: Incomplete thought technique — breaking AI's "everything resolved" completeness pattern
- ZP-5: Voice fingerprinting — personal stance markers, attitude words, asides
- ZP-6: Structural disruption — breaking topic-sentence-first paragraph structure
- ZP-7: Natural error pass — comma splices, sentence-starting conjunctions, informal constructions
- Detector-specific notes for each major AI detector
- Full before/after showing 1.8/10 → 0.x transformation
- 0.x final checklist (10 boxes to check before calling it done)

**SKILL.md:**
- Iron Law updated: 7 layers → 7 layers + ZP
- Target changed: "≤ 3/10" → "0.x — undetectable"
- Workflow Phase 3: now runs ZP-1 through ZP-7 explicitly
- Scoring reference: added 0.x row, all recommendations now reference ZP

**score.py:**
- Recommendations updated to reference Zero-Point Protocol

---

## 2.3.0 — 2026-02-22

### Critical gap fixes: grammar automation + 50 more patterns

**patterns.py:**
- Added startup/strategy jargon: democratize, flywheel, inflection point, north star, lean into, table stakes, value proposition, bespoke, curated, evangelize, socialize (verb), whitespace (opportunity), mission-critical, go-to-market, growth mindset, fail fast, step-change, mission-driven, data-driven, purpose-driven, core competency, no-brainer, at a high level, drill down, peel back, boil the ocean, net net, 10x (verb), more X than ever, never been more X
- Added GPTZero statistical hard-bans: "play a significant role in", "aims to explore", "notable works include"
- Added grammar AI constructions: "not only X but also Y" → rewrite flag, "it is [adj] that" → strip prefix, "it is clear/evident that" → strip, "now more than ever" → cut
- TIER1_REPLACEMENTS: 196 → 244 patterns

**score.py — new detection functions:**
- `count_grammar_patterns()`: detects 9 AI grammar constructions (not only/but also, while X Y opener, it is [adj] that, by [gerund] X can, more than ever, never been more, play a role in, aims to explore)
- `count_parallel_triplets()`: flags "X, Y, and Z" overuse (>2 per 500 words)
- `has_linkedin_format()`: detects 5+ consecutive single-sentence lines (LinkedIn one-sentence-per-line formatting)
- Contraction scoring: improved from binary (0 = flag) to rate-based (<0.5 per 100 words = flag)
- All new detectors integrated into `score_structure()`, `score_text()`, and fingerprint reporting

---

## 2.2.0 — 2026-02-22

### Platform modes expansion: Email, Twitter, LinkedIn overhaul

**patterns.py:**
- LINKEDIN_PATTERNS expanded: 18 → 60 patterns across 6 categories (announcement openers, "here's" setups, opinion labels, story labels, engagement bait, closing patterns)
- Added EMAIL_OPENERS: 15 patterns (greetings, "I wanted to reach out", formal introductions)
- Added EMAIL_BODY: 18 patterns ("Please be advised", "kindly", "pursuant to", "with regard to", etc.)
- Added EMAIL_CLOSERS: 13 patterns ("I hope this helps", "I look forward to hearing from you", etc.)
- Added TWITTER_PATTERNS: 17 patterns (thread openers, "Hot take:", "That's it! Follow me", etc.)

**deaify.py:**
- Added `--email` mode: applies EMAIL_OPENERS + EMAIL_BODY + EMAIL_CLOSERS + standard treatment
- Added `--twitter` mode: applies TWITTER_PATTERNS + standard treatment
- `apply_email_patterns()` function added
- `apply_twitter_patterns()` function added
- `EMAIL_OPENERS`, `EMAIL_BODY`, `EMAIL_CLOSERS`, `TWITTER_PATTERNS` imported and wired

**references/PLATFORM-PATTERNS.md:**
- Full rewrite — 3x more content
- LinkedIn: 40+ phrases in vocabulary table, 5 format templates documented, per-format-type AI tells
- Email: 20+ openers, 25+ body phrases, 20+ closers, cold email AI tells, email-by-type matrix
- Twitter/X: 20+ pattern table, per-tweet-format AI tells, AI vocab specific to Twitter
- Slack and Reports sections preserved

**SKILL.md:**
- Mode table updated with email and twitter entries
- Layer application table updated with platform modes

---

## 2.1.0 — 2026-02-22

### Patch: vocabulary expansion + LinkedIn wiring

**patterns.py:**
- Added 30+ missing AI buzzwords to TIER1_REPLACEMENTS: resonate, plethora, myriad, learnings, groundbreaking, overarching, salient, multifaceted, noteworthy, alignment, cadence, cross-functional, ideation, granular, pivot, traction, scale (verb), buy-in, touchpoints, iterate, forward-thinking, future-proof, world-class, best-in-class, industry-leading, thought leadership, truly, simply put, at its core

**score.py:**
- `count_tier1_hits()` now detects all poetic AI words (tapestry, vibrant, realm, beacon, daunting, pivotal, meticulous, embark, testament, etc.) + all new v2.1 buzzwords
- Detection coverage expanded from ~35 → 60+ patterns

**deaify.py:**
- Added `--linkedin` mode: applies LINKEDIN_PATTERNS + standard treatment
- LINKEDIN_PATTERNS now wired into pipeline (was defined in patterns.py but never imported)
- `apply_linkedin_patterns()` function added for line-by-line LinkedIn pattern removal

**SKILL.md:**
- Fixed layer count inconsistency: "The 6 Transformation Layers" → "The 7 Transformation Layers"
- Fixed inline reference: "Apply all 6 layers" → "Apply all 7 layers"

**New files:**
- `references/GRAMMAR-PATTERNS.md`: AI grammar constructions (not X but Y, while X Y openers, gerund bullets, definitional chains, parallel triplet overuse)

---

## 2.0.0 — 2026-02-22

### Major expansion: research-backed vocabulary + Layer 7 (Statistical)

**patterns.py:**
- Added Poetic AI words section: tapestry, vibrant, realm, beacon, bustling, nestled, daunting, pivotal, meticulous, embark, testament, ever-evolving, etc. (40+ new patterns)
- Added LINKEDIN_PATTERNS: 18 platform-specific regex patterns

**score.py:**
- Fixed stdin double-read bug
- Fixed `seamless` pattern (`seamlessly?` → `seamless(?:ly)?`)

**references/ new files:**
- PERPLEXITY-BURSTINESS.md: Full Layer 7 documentation (255 lines)
- PLATFORM-PATTERNS.md: LinkedIn, email, blog, Twitter, Slack patterns (270 lines)
- BEFORE-AFTER-EXAMPLES.md: 2 new examples (LinkedIn post, aggressive mode think piece)

**assets/word-lists/ai-words.json:**
- v2.0: 320+ entries across 7 tiers including GPTZero statistical frequency data

---

## 1.0.0 — 2026-02-22

### Initial release

**Skill:**
- SKILL.md: 6-layer transformation framework
- Full scoring rubric (1-10 AI probability scale)
- Context-aware mode selection
- Complete de-AI-fy workflow

**References:**
- AI-VOCABULARY.md: 200+ banned words + contextual replacements
- SENTENCE-PATTERNS.md: 10 AI sentence structure patterns + fixes
- STRUCTURAL-PATTERNS.md: 9 formatting anti-patterns + flatten guide
- TONE-AND-VOICE.md: 9 tone problems + detox techniques
- DETECTION-SIGNATURES.md: Complete fingerprint catalog with severity levels
- REWRITE-TECHNIQUES.md: 10 humanization techniques with worked examples
- BEFORE-AFTER-EXAMPLES.md: 6 full before/after transformations across content types
- SCORING-RUBRIC.md: Weighted category scoring system

**Scripts:**
- deaify.py: Main pipeline (Layers 1, 2, 4, 5 automated)
- patterns.py: Pattern definitions + regex library
- score.py: AI probability scorer with fingerprint reporting

**Assets:**
- ai-words.json: Machine-readable banned vocabulary (6 tiers, 150+ entries)
- replacements.json: Contextual replacement map (100+ entries with multiple options)
