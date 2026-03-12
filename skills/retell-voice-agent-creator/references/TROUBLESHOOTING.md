# Troubleshooting Guide

Common issues encountered when building and deploying Retell AI voice agents,
with symptoms, causes, fixes, and reference links.

## Authentication Issues

### 401 Unauthorized

**Symptom:** API calls return `{"error": "Unauthorized"}` with status 401.

**Cause:** Missing, invalid, or expired RETELL_API_KEY.

**Fix:**
1. Verify the key is set: `echo $RETELL_API_KEY`
2. Verify the key format: must start with `key_`
3. Test connectivity: `curl -s -H "Authorization: Bearer $RETELL_API_KEY" https://api.retellai.com/list-agents`
4. If using client mode, verify the client's API key is correct
5. Regenerate the key from the Retell Dashboard if needed

**Reference:** [ENV-VARS.md](ENV-VARS.md)

### 403 Forbidden

**Symptom:** API calls return 403 for specific operations.

**Cause:** API key does not have permissions for the requested operation.
This can happen with restricted client keys.

**Fix:**
1. Check if the key has full permissions in the Retell Dashboard
2. For client deployments, ensure the client has not restricted their key

## Configuration Issues

### 422 Unprocessable Entity (Invalid Config)

**Symptom:** Agent creation or update returns 422 with validation errors.

**Cause:** The agent-config.json or llm-config.json has invalid or missing fields.

**Fix:**
1. Check the error message — it usually identifies the invalid field
2. Common missing fields: `voice_id`, `response_engine.type`, `response_engine.llm_id`
3. Common type errors: `responsiveness` must be number (0-2), `interruption_sensitivity` must be number (0-1)
4. Validate against the schema in `assets/schemas/`
5. Use the agent-config-builder sub-skill to regenerate

**Reference:** [API-QUICK-REFERENCE.md](API-QUICK-REFERENCE.md)

### Voice Not Found

**Symptom:** Agent creation fails with "voice_id not found" or similar.

**Cause:** The specified voice_id does not exist or is not available in the account.

**Fix:**
1. List available voices: `curl -s -H "Authorization: Bearer $RETELL_API_KEY" https://api.retellai.com/list-voices | jq '.[] | .voice_id'`
2. Verify the voice_id matches exactly (case-sensitive)
3. If using ElevenLabs custom voice, ensure it is shared with Retell
4. Use the voice-selector sub-skill to browse and select a valid voice

**Reference:** [VOICE-PROVIDER-COMPARISON.md](VOICE-PROVIDER-COMPARISON.md)

## Voice Quality Issues

### Agent Sounds Robotic

**Symptom:** Deployed agent sounds stiff, unnatural, or obviously AI-generated.

**Cause:** Humanization level too low or humanization step was skipped entirely.

**Fix:**
1. Run humanization-engine in SINGLE mode: "humanize this agent"
2. Set humanization level to 7+ for natural-sounding agents
3. Enable specific elements: fillers, pauses, backchannel, breathing
4. Verify the voice provider supports emotion (ElevenLabs is best for this)
5. Re-deploy the updated prompt

**Reference:** Sub-skill `sub-skills/humanization-engine/SKILL.md`

### Pronunciation Still Wrong After Fix

**Symptom:** Agent mispronounces words despite having a pronunciation dictionary.

**Cause:** Multiple possible causes.

**Fix:**
1. **Wrong voice provider:** Pronunciation dictionaries only work with ElevenLabs
   Turbo v2 and later. Other providers ignore dictionaries.
2. **Invalid IPA format:** Verify IPA transcription is correct. Use an IPA
   validator or the pronunciation-fixer sub-skill.
3. **Dictionary not applied:** Confirm the dictionary was included in the
   agent config (check `pronunciation_dictionary` field).
4. **Inline approach:** As a fallback, add phonetic respelling directly in the
   prompt: "Xeroflux (say: ZEER-oh-flux)".
5. Test with a call to verify the fix.

**Reference:** Sub-skill `sub-skills/pronunciation-fixer/SKILL.md`

## Performance Issues

### High Latency / Slow Responses

**Symptom:** Agent takes 2+ seconds to respond. Callers notice awkward pauses.

**Cause:** Model too large, responsiveness setting too conservative, or network issues.

**Fix:**
1. Lower the `responsiveness` value (0 = fastest, 2 = most careful)
2. Switch to a faster model (gpt-4o-mini instead of gpt-4o)
3. Switch to a lower-latency voice provider (Deepgram, OpenAI, Cartesia)
4. Reduce system prompt length (shorter prompts process faster)
5. Check Retell status page for platform-level latency issues

**Reference:** Sub-skill `sub-skills/latency-optimizer/SKILL.md`

### Agent Cuts Off the Caller

**Symptom:** Agent starts talking while the caller is still speaking.

**Cause:** `interruption_sensitivity` too low or `responsiveness` too aggressive.

**Fix:**
1. Increase `interruption_sensitivity` toward 1.0 (more sensitive to caller speech)
2. Increase `responsiveness` toward 2 (waits longer before responding)
3. Enable `enable_backchannel` so agent uses "mhm" sounds while listening

### Agent Does Not Respond / Long Silence

**Symptom:** Agent goes silent after caller finishes speaking.

**Cause:** Endpointing misconfigured or model processing too slow.

**Fix:**
1. Lower `responsiveness` toward 0 (triggers response sooner)
2. Check if the prompt is causing the model to "think" too long
3. Verify the LLM is not rate-limited

### Background Noise Issues

**Symptom:** Agent misinterprets caller speech in noisy environments.

**Cause:** Denoising not enabled or ambient sound settings interfering.

**Fix:**
1. Set `ambient_sound` to "off" if background sounds are enabled but unwanted
2. Lower `ambient_sound_volume` if background sounds are needed but too loud
3. If caller environment is noisy, recommend they use a quieter location
4. Consider adjusting endpointing settings to handle noise better

## Deployment Issues

### Deployment to Client Account Fails

**Symptom:** Agent creation returns errors when using a client's API key.

**Cause:** Client API key has insufficient permissions, is expired, or is invalid.

**Fix:**
1. Verify the client key format (starts with `key_`)
2. Test the key independently: `curl -s -H "Authorization: Bearer $CLIENT_KEY" https://api.retellai.com/list-agents`
3. Ensure the client has not restricted their key's permissions
4. Ask the client to regenerate their key if needed

**Reference:** [MULTI-ACCOUNT-GUIDE.md](MULTI-ACCOUNT-GUIDE.md)

### deploy.sh Script Fails

**Symptom:** `scripts/deploy.sh` exits with an error.

**Cause:** Various — missing dependencies, invalid config, API errors.

**Fix:**
1. Run pre-flight check first: `scripts/verify.sh`
2. Check that `output/llm-config.json` and `output/agent-config.json` exist and are valid JSON
3. Verify with `jq . output/agent-config.json` (should parse without errors)
4. Check the error message from the script — it identifies the failing step
5. If retry limit exceeded, the script saves configs locally for manual retry

### Test Call Not Connecting

**Symptom:** `scripts/test-agent.sh` triggers a call but it does not connect.

**Cause:** No phone number assigned, or Twilio credentials missing.

**Fix:**
1. Verify the agent has a phone number assigned
2. Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are set
3. Verify the phone number is active in Twilio
4. Try a web-based test call from the Retell Dashboard instead

## Pre-Flight Diagnostic

Run `scripts/verify.sh` to check all prerequisites at once. It validates:
- Required tools (curl, jq, python3)
- RETELL_API_KEY is set and valid
- API connectivity
- Optional tools and credentials (with warnings, not failures)

## The 29 Most Common Voice Agent Mistakes

Organized into 8 categories with specific fixes for each. Use this as a
pre-launch checklist — listen to 5 test calls per mistake and fix any occurring
in more than 10% of calls.

### 1. Timing/Latency (3 mistakes)

**Mistake 1: Response delay over 500ms**
Callers perceive delays over 500ms as awkward silence.
**Fix:** Set `responsiveness` to 0.8-1.0. Keep system prompts under 500 tokens.
Use a faster model for simple nodes (gpt-4.1-nano).

**Mistake 2: Uniform response timing**
Every response takes the same amount of time, regardless of complexity. Feels
mechanical.
**Fix:** Vary timing by complexity. Simple acknowledgments should be near-instant.
Complex answers can take a natural beat. Per-node LLM selection helps here.

**Mistake 3: Dead silence during processing**
Agent goes quiet while calling a tool or processing a complex request.
**Fix:** Add tool preambles to every function call. "Let me check that for you"
or "One moment while I look that up." Never let the caller hear silence.

### 2. Turn-Taking (5 mistakes)

**Mistake 4: Cutting off the caller mid-sentence**
Agent starts speaking before the caller finishes.
**Fix:** Set end-of-turn detection threshold to 700-1000ms. Increase
`responsiveness` toward 1.5-2.0 for longer wait times.

**Mistake 5: Bulldozing through interruptions**
Caller tries to interrupt but agent keeps talking.
**Fix:** Set `interruption_sensitivity` to 0.7-0.9. Agent should stop speaking
within 200ms of detecting an interruption.

**Mistake 6: Not tracking what the caller heard**
After an interruption, agent does not know what the caller actually heard vs
what was cut off.
**Fix:** Use committed transcript tracking. Only reference information the caller
confirmed hearing.

**Mistake 7: No backchannel during long caller turns**
Caller speaks for 15+ seconds with no acknowledgment from the agent.
**Fix:** Enable `enable_backchannel`. Set backchannel frequency to 0.5-0.7. Agent
will produce "mhm," "right," "I see" while listening.

**Mistake 8: False triggers from background noise**
Agent responds to background noise, TV, or side conversations.
**Fix:** Enable denoising. Raise the VAD (Voice Activity Detection) threshold.
Test in noisy environments before deployment.

### 3. Phrasing/Length (5 mistakes)

**Mistake 9: Responses too long**
Agent speaks for 30+ seconds per turn. Callers zone out or interrupt.
**Fix:** Add to prompt: "NEVER speak more than 2 sentences at a time. Keep
responses under 50 words." Split complex answers across multiple turns.

**Mistake 10: Perfect grammar**
No human speaks in perfect grammar on a phone call. It sounds scripted.
**Fix:** Use the Deliberate Imperfection Protocol. 1 filler per 4-5 sentences.
Occasional self-corrections. Discourse markers at topic transitions.

**Mistake 11: Repetitive acknowledgments**
Agent says "Great!" after every caller response. Or "I understand" every time.
**Fix:** Use a varied phrase bank: "got it," "makes sense," "sure," "okay,"
"right," "perfect." Never use the same acknowledgment twice in a row.

**Mistake 12: Visual formatting in speech**
Agent outputs bullet points, numbered lists, markdown, or links.
**Fix:** Follow the Write-for-the-Ear rules. Add to prompt: "NEVER use bullet
points, numbered lists, or any visual formatting. This is a phone call."
See WRITE-FOR-THE-EAR.md for complete rules.

**Mistake 13: No hedging or uncertainty**
Agent speaks with absolute confidence about everything. Sounds unnatural.
**Fix:** Add occasional hedging: "I think," "I believe," "if I'm not mistaken."
Use when appropriate — not on facts the agent is certain about.

### 4. Emotional Intelligence (3 mistakes)

**Mistake 14: Flat emotional delivery**
Agent sounds the same whether the caller is happy, upset, or confused.
**Fix:** Set `voice_temperature` to 1.0-1.25. Add an emotional range section to
the prompt specifying how to respond to different caller emotions.

**Mistake 15: No empathy response**
Caller expresses frustration or sadness and agent ignores the emotion.
**Fix:** Add to prompt: "When the caller expresses a negative emotion, acknowledge
it before responding to the content. Example: 'I'm sorry to hear that. Let me
see what I can do.'"

**Mistake 16: Mismatched energy**
Caller is excited and agent is flat. Or caller is calm and agent is hyper.
**Fix:** Add tone adaptation rules: "Match the caller's energy level. If they are
enthusiastic, be upbeat. If they are subdued, be calm and measured."

### 5. Conversation Flow (4 mistakes)

**Mistake 17: Re-asking information already provided**
Caller gave their name earlier and agent asks for it again.
**Fix:** Inject caller data dynamically via `dynamic_variables`. Add to prompt:
"NEVER ask for information you already have."

**Mistake 18: Poor topic switching**
Agent jumps between topics without transition, confusing the caller.
**Fix:** Use discourse markers: "so," "now," "moving on," "here's the thing,"
"one more thing." These signal topic boundaries naturally.

**Mistake 19: Repetitive clarification loops**
Agent asks "Could you repeat that?" three or more times in a row.
**Fix:** Track misunderstanding count in the prompt logic. After 2 failed
clarification attempts, try rephrasing the question or escalate to human.

**Mistake 20: No error recovery**
Agent gets stuck when something unexpected happens and has no fallback.
**Fix:** Add a fallback section to the prompt: "If you cannot understand the
caller after 2 attempts, say: 'I want to make sure I get this right. Let me
connect you with someone who can help.'"

### 6. Voice/Audio Quality (4 mistakes)

**Mistake 21: Wrong voice for the brand**
A luxury brand using a casual young voice, or a tech startup using a formal
corporate voice.
**Fix:** Use the voice-selector sub-skill to match voice characteristics to
brand identity. Consider age, gender, accent, and energy level.

**Mistake 22: No ambient sound**
Complete digital silence between words feels unnatural on a phone call.
**Fix:** Enable `ambient_sound` at 0.2-0.4 volume. Use "office" or "café"
ambient for natural phone call feel.

**Mistake 23: Audible TTS artifacts**
Clicking, stuttering, metallic sounds, or unnatural breath patterns.
**Fix:** Run the Artifact Detection Test (20 calls minimum). If artifacts appear
in more than 5% of calls, try a different voice or switch providers.

**Mistake 24: Mispronounced numbers, emails, and URLs**
Agent says "four hundred fifteen" instead of "four one five" for a phone number.
**Fix:** Follow Write-for-the-Ear rules. Add explicit number formatting rules to
the prompt. Add a pronunciation dictionary for brand-specific terms.

### 7. Escalation (3 mistakes)

**Mistake 25: No human handoff option**
Caller asks to speak to a person and agent has no path to do so.
**Fix:** Add a Global Node for transfer to human. Include in prompt: "If the
caller asks to speak to a person, ALWAYS transfer them. Never refuse."

**Mistake 26: Lying about being AI**
Caller asks "Am I talking to a robot?" and agent denies it or deflects.
**Fix:** Always disclose. Frame it as a feature: "I'm an AI assistant for
[company]. I can help with most things, and I can also connect you with a
team member if you prefer."

**Mistake 27: Not knowing when to stop**
Agent keeps trying to resolve an issue it clearly cannot handle.
**Fix:** Add escalation rules: "After 2 failed attempts to resolve the same
issue, transfer to a human agent. Say: 'Let me connect you with someone who
can help with that.'"

### 8. Silence/Hold (2 mistakes)

**Mistake 28: Wrong response to silence**
Caller says "hold on" or "one second" and agent keeps talking or asks
"Are you still there?" too quickly.
**Fix:** Add to prompt: "If the caller says 'hold on,' 'one second,' 'give me
a moment,' or similar — output NO_RESPONSE_NEEDED and wait silently. Do not
speak again until the caller speaks."

**Mistake 29: No transition signals**
Agent processes a request with no verbal signal, leaving the caller in silence.
**Fix:** Add tool preambles for every function call. Before any processing that
takes more than 1 second, say "One moment" or "Let me look into that."
