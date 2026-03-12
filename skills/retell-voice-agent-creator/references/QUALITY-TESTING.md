# Quality Testing Framework

Framework for validating that a voice agent achieves human-like quality before
deployment. Run all tests before any production launch.

## Test 1: MOS-Lite Score (Target: 4.0+)

Mean Opinion Score proxy. Have 5 test listeners rate naturalness on a 1-5 scale.
Average the scores.

| Score Range | Assessment | Action |
|-------------|------------|--------|
| Below 3.5 | Major issues | Full humanization rework needed |
| 3.5 - 4.0 | Minor issues | Targeted adjustments to specific areas |
| Above 4.0 | Production ready | Proceed to deployment |

**How to run:** Play 5 different agent responses to each listener. Have them rate
naturalness without knowing which is AI. Average all ratings.

## Test 2: Prosody Variation Test

Record 10 responses on varied topics (greeting, question, empathy, excitement,
routine information). Analyze each:

- Does pitch vary between and within sentences?
- Does speed vary based on content importance?
- Are there natural pauses at clause boundaries?
- Does emphasis land on the right words?

**Flat delivery = fail.** If the agent sounds the same regardless of topic or
emotion, increase `voice_temperature` (1.0-1.25) and add emotion guidance to
the prompt.

**Tool:** Audacity or any waveform viewer. Look for consistent amplitude and
frequency patterns (bad) vs varied patterns (good).

## Test 3: Homograph Pronunciation Test

Test words whose pronunciation depends on context:

| Word | Context A | Context B |
|------|-----------|-----------|
| lead | "I'll lead the meeting" (verb: leed) | "a lead pipe" (noun: led) |
| live | "we're going live" (adjective: lyve) | "I live here" (verb: liv) |
| read | "please read this" (present: reed) | "I read it yesterday" (past: red) |
| project | "the project is done" (noun: PROJ-ect) | "we project growth" (verb: pro-JECT) |
| record | "a new record" (noun: REC-ord) | "please record this" (verb: re-CORD) |
| close | "close the door" (verb: cloze) | "that was close" (adjective: cloce) |

**If the agent mispronounces based on context:** Add explicit phonetic guidance
in the prompt or pronunciation dictionary for problem words.

## Test 4: Artifact Detection Test

Listen for audio artifacts across a minimum of 20 test calls:

- Robotic stuttering or repeated syllables
- TTS glitches (sudden pitch jumps, metallic sounds)
- Unnatural breath patterns (too regular, too loud, or absent)
- Clicking or popping sounds
- Audio clipping (distortion on loud sounds)
- Unnatural word boundaries (sounds chopped between words)

**Fail threshold:** Any artifact in more than 5% of calls (more than 1 in 20).
If failing, try a different voice, adjust voice settings, or switch providers.

## Test 5: Auditory Fatigue Test

Listen to 30 continuous minutes of the agent handling calls.

**Assess:**
- Does the voice become tiring to listen to?
- Is the delivery monotone over extended listening?
- Does the agent use enough variety in phrasing and tone?

Monotone delivery causes listener fatigue. Varied prosody, phrasing, and
acknowledgment words sustain engagement. If fatigue sets in before 30 minutes,
revisit humanization settings.

## Retell Simulation Testing

Use Retell's built-in simulation feature for automated testing:

1. Open the Simulation tab in the Retell dashboard
2. Create test scenarios with specific personas:
   - **Happy path:** Cooperative caller who follows the flow
   - **Objector:** Pushes back on pricing, timing, or value
   - **Angry caller:** Frustrated, interrupts, demands human
   - **Confused caller:** Asks for repetition, goes off-topic
   - **Rushed caller:** Gives short answers, wants to finish quickly
3. Run a batch of 20-50 simulated conversations
4. Review transcripts for:
   - Correct state transitions at every node
   - No hallucinations (agent stays within defined knowledge)
   - Proper escalation triggers when needed
   - Accurate pronunciation of numbers, emails, and URLs

## Retell Assure (AI QA)

Enable after deployment for ongoing quality monitoring:

1. Enable Retell Assure in the dashboard
2. Configure thresholds:
   - Hallucination detection sensitivity
   - Topic adherence scoring
   - Escalation accuracy
3. Review weekly summary reports
4. Flag calls scoring below threshold for human review
5. Use flagged calls to identify prompt improvements

## The 29-Mistake Checklist

Run through all 29 identified common mistakes (documented in TROUBLESHOOTING.md).
For each mistake:

1. Listen to 5 test calls specifically checking for that mistake
2. Document whether it occurs and at what frequency
3. Fix any mistake occurring in more than 10% of calls before launch

## Pre-Launch Gate Checklist

All items must pass before production deployment:

- [ ] MOS-Lite score is 4.0 or above
- [ ] Zero audio artifacts in 20 consecutive test calls
- [ ] All 5 simulation personas handled correctly
- [ ] Pronunciation test: 100% accuracy on numbers, emails, and URLs
- [ ] No repeated identical phrases across 10 consecutive calls
- [ ] Emotional range validated across 5 emotional caller types
  (happy, frustrated, confused, rushed, neutral)
- [ ] Response length under 2 sentences per turn in 95%+ of responses
- [ ] Single-question rule followed in 100% of turns
- [ ] Escalation path works correctly for all trigger conditions
- [ ] Tool preambles present for every tool call (no silent processing)
