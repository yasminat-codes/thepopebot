# Voice Agent Mistakes That Reveal Non-Human Identity: Comprehensive Fix Guide

Research compiled from 20+ industry sources, engineering documentation, and A/B testing data.

---

## CATEGORY 1: TIMING AND LATENCY

### Mistake #1: Response Delay Over 500ms
**What happens:** Agent pauses noticeably after the caller finishes speaking. Callers immediately register this as "talking to a computer."
**Why it matters:** Humans respond in natural conversation within 200ms of turn transitions. Anything over 500ms feels robotic.
**Exact fix:**
- Set Retell `responsiveness` to 0.8-1.0 (higher = faster response)
- Enable streaming TTS (audio starts as LLM generates tokens, not after full response)
- Keep system prompts under 500 tokens to reduce LLM processing time
- Keep conversation history to last 3-5 turns only
- Use prompt caching to eliminate redundant processing
- Target: under 300ms total response time

### Mistake #2: Uniform Response Timing
**What happens:** Every response takes exactly the same time to begin, regardless of question complexity. Humans vary response timing based on whether they need to think.
**Exact fix:**
- For simple acknowledgments ("Got it", "Sure"): target <200ms
- For complex answers: a natural 400-600ms pause actually sounds MORE human than instant responses
- Add prompt instruction: "For simple confirmations, respond immediately. For questions requiring thought, a brief natural pause is acceptable."

### Mistake #3: No Filler During Processing
**What happens:** Dead silence while the agent processes a complex question. Humans say "Hmm, let me think about that" or "So..." while formulating responses.
**Exact fix:**
- Add to system prompt: "When you need a moment to look something up or think, say brief fillers like 'Let me check on that for you' or 'Hmm, let me see' rather than going silent."
- Configure Retell backchannel words for listening acknowledgment
- Use streaming TTS so the first words arrive while the rest generates

---

## CATEGORY 2: TURN-TAKING AND INTERRUPTION HANDLING

### Mistake #4: Cutting Off the Caller Mid-Sentence
**What happens:** Agent starts responding during a natural pause when the caller was just taking a breath or gathering their thoughts.
**Why it matters:** Humans pause mid-thought constantly. A 700ms pause does NOT mean they are done speaking.
**Exact fix:**
- Set end-of-turn silence threshold to 700-1000ms minimum (industry standard)
- Use semantic endpointing when available (analyzes WHAT was said, not just silence duration)
- AssemblyAI config: `end_of_turn_confidence_threshold: 0.7`, `min_end_of_turn_silence_when_confident: 160ms`, `max_turn_silence: 2400ms`
- Add prompt instruction: "Wait for the caller to fully complete their thought before responding. If they seem to be mid-sentence, wait."

### Mistake #5: Ignoring Interruptions (Bulldozing)
**What happens:** Caller tries to interject or correct the agent, but the agent keeps talking over them, finishing its entire response.
**Why it matters:** Humans stop talking within 200ms of being interrupted. An agent that plows through signals "I am a recording."
**Exact fix:**
- Set Retell `interruption_sensitivity` to 0.7-0.9 (higher = more sensitive to interruptions)
- Enable barge-in: agent must stop speaking within 200ms of detecting caller speech
- Add to prompt: "If the caller interrupts you, stop immediately. Acknowledge with 'Sorry, go ahead' and listen."
- After interruption, DO NOT resume the previous response. Address whatever the caller said.

### Mistake #6: Not Tracking What the Caller Actually Heard
**What happens:** Agent gets interrupted mid-sentence but its internal transcript shows the full response as "sent." On the next turn, the agent references information the caller never actually heard.
**Why it matters:** This is the #1 technical cause of confused conversations after interruptions.
**Exact fix:**
- Track the "committed transcript" (what was actually spoken aloud before interruption) separately from the "generated transcript"
- Truncate conversation history to only what was audibly delivered
- After interruption, have the agent acknowledge: "I was saying..." and briefly recap if the interrupted info was important

### Mistake #7: No Backchannel During Caller's Long Turns
**What happens:** Caller speaks for 15-30 seconds explaining a problem. The agent is completely silent the entire time. Caller asks "Are you there?" or "Hello?"
**Exact fix:**
- Enable Retell backchannel: `enable_backchannel: true`
- Set `backchannel_frequency` to medium (not too frequent or it sounds manic)
- Configure `backchannel_words`: ["uh-huh", "I see", "mm-hmm", "okay", "right"]
- These should fire every 5-8 seconds of continuous caller speech

### Mistake #8: Talking Over Background Noise
**What happens:** Agent hears background noise (TV, traffic, other people) and interprets it as the caller speaking, triggering false interruptions or responses.
**Why it matters:** Causes 3.5x more false interruptions. 50% more call abandonment.
**Exact fix:**
- Enable noise cancellation in the audio pipeline (pre-VAD)
- Increase VAD threshold sensitivity for noisy environments
- OpenAI Realtime API: increase `threshold` parameter to reduce false positives
- Add ambient sound to the agent side (`ambient_sound: "office"`) to mask processing artifacts

---

## CATEGORY 3: RESPONSE PHRASING AND LENGTH

### Mistake #9: Responses That Are Too Long
**What happens:** Agent delivers 3-4 sentences in a single turn. By sentence two, the caller has tuned out or is trying to interrupt.
**Why it matters:** Humans speak at ~150 words per minute. A 100-word response takes 40 seconds to deliver. Nobody waits that long.
**Exact fix:**
- Add to system prompt: "Keep every response under 2 sentences. Maximum 30 words per turn. If you need to convey more information, break it across multiple conversational turns."
- For complex explanations: "Would you like me to explain the details?" then deliver in chunks
- Never list more than 2 items verbally without pausing for confirmation

### Mistake #10: Perfect Grammar and Complete Sentences
**What happens:** Agent speaks in flawless, formal English. "I would be happy to assist you with that inquiry. Let me locate the relevant information." No human talks like this on the phone.
**Exact fix:**
- Add to system prompt: "Speak naturally and conversationally. Use contractions (you're, I'll, that's, we've, can't). Use casual transitions (so, actually, basically, well). Keep sentences short and simple."
- Example good phrasing: "Got it, let me pull that up for you."
- Example bad phrasing: "Certainly, I will retrieve that information for you now."
- Prompt instruction: "Start sentences with natural openers like 'got it', 'sure thing', 'okay so', 'makes sense', 'oh', 'right' -- choose whichever fits the conversation."

### Mistake #11: Repetitive Acknowledgment Phrases
**What happens:** Agent says "That's a great question!" or "I understand" or "Absolutely!" in the exact same way every time. Callers notice the pattern after 2-3 occurrences.
**Exact fix:**
- Add to system prompt: "Vary your acknowledgments. Don't use the same phrase twice in a call. Rotate between: 'got it', 'sure', 'okay', 'makes sense', 'right', 'mm-hmm', 'yeah', 'of course', 'for sure'."
- Never use: "That's a great question!" (dead giveaway)
- Never use: "Absolutely!" repeatedly
- Never use: "I'd be happy to help with that!" (too polished)

### Mistake #12: Using Visual/Text Formatting in Speech
**What happens:** Agent says things like "Here are three options: one, two, three" in a list format, or references "clicking a link" or uses language that implies visual formatting.
**Exact fix:**
- Add to system prompt: "Never use bullet points, numbered lists, or formatted text. Never reference visual elements. Instead of listing items, weave them into natural sentences."
- Bad: "You have three options. Option 1: the basic plan. Option 2: the pro plan. Option 3: the enterprise plan."
- Good: "So your best bet is probably the pro plan, but there's also a basic tier if you want something simpler, or enterprise if you need more."

### Mistake #13: Not Using Hedging Language
**What happens:** Agent states everything with 100% certainty. Humans naturally hedge: "I think...", "If I remember right...", "It should be...", "Usually..."
**Exact fix:**
- Add to system prompt: "When you're not completely certain, use natural hedging: 'I believe', 'I think', 'it should be', 'typically', 'from what I can see'. Don't state everything as absolute fact."
- When confidence is 70-89%: "Based on what I'm seeing..." or "From the information I have..."
- When confidence is below 70%: "I'm not 100% sure on that, let me connect you with someone who can confirm."

---

## CATEGORY 4: EMOTIONAL INTELLIGENCE AND TONE

### Mistake #14: Flat/Monotone Delivery With No Emotional Variation
**What happens:** Agent delivers good news and bad news in the exact same tone. "Your appointment is confirmed" sounds the same as "Unfortunately we need to cancel."
**Why it matters:** Monotonous prosody is the #1 indicator of synthetic speech.
**Exact fix:**
- Use voice temperature setting of 1.0-1.25 for expressiveness (A/B test data: 1.25+ increases engagement but risks pronunciation issues)
- Add emotional cues in the prompt: "Match your energy to the situation. Sound genuinely pleased when sharing good news. Sound empathetic and slightly slower when delivering bad news."
- Configure TTS to apply pitch variation for questions (rising intonation) vs. statements

### Mistake #15: No Empathy Response to Caller Frustration
**What happens:** Caller says "This is so frustrating, I've been dealing with this for weeks" and the agent responds with "I can help you with that. What is your account number?"
**Why it matters:** Skipping the emotional acknowledgment is the #1 caller complaint about AI agents.
**Exact fix:**
- Add sentiment detection to the prompt: "If the caller sounds frustrated, upset, or angry, ALWAYS acknowledge their emotion FIRST before moving to resolution. Say things like 'I totally get that, that sounds really frustrating' or 'I'm sorry you've been dealing with that, let's get this sorted out right now.'"
- Frustrated caller protocol: empathize > validate > solve (never skip steps 1 and 2)
- After 3+ consecutive turns of negative sentiment, offer human escalation

### Mistake #16: Inappropriate Energy Matching
**What happens:** Caller is quiet and subdued (maybe it is a sensitive topic like billing issues or medical). Agent responds with chipper, upbeat energy.
**Exact fix:**
- Add to prompt: "Mirror the caller's energy level. If they're speaking quietly and seriously, respond in a calm, measured tone. If they're upbeat and chatty, match that energy. Don't be overly enthusiastic when the situation doesn't call for it."
- Tone adaptation rules in prompt:
  - Frustrated caller -> empathetic, calm, solution-focused
  - Confused caller -> patient, clear, step-by-step
  - Happy/satisfied caller -> warm, efficient, positive
  - Quiet/subdued caller -> gentle, respectful, measured

---

## CATEGORY 5: CONVERSATION FLOW AND MEMORY

### Mistake #17: Asking for Information the Caller Already Provided
**What happens:** Caller says "Hi, I'm calling about my order #12345" and two turns later the agent asks "Can I get your order number?"
**Why it matters:** This is the single most rage-inducing experience for callers. It signals the agent is not listening.
**Exact fix:**
- Implement conversation memory that tracks ALL entities mentioned: names, numbers, dates, account IDs
- Add to prompt: "Never ask for information the caller has already provided. If they mentioned their name, order number, or any detail earlier in the call, use it."
- Use slot-filling logic to track what information has been collected
- Validate with: "I have your order number as 12345, is that right?" (confirms without re-asking)

### Mistake #18: Inability to Handle Topic Switches
**What happens:** Caller is discussing topic A, then says "Oh wait, actually I also wanted to ask about..." and the agent either ignores the switch or gets confused and loops back to topic A.
**Exact fix:**
- Add to prompt: "If the caller changes topics, acknowledge the shift: 'Sure, let's talk about that instead' or 'Oh got it, let me switch gears.' You can always circle back: 'And did you still want to finish up with [previous topic]?'"
- Design intent linking so the agent can pivot between conversation branches without losing state

### Mistake #19: Repeating the Same Clarification Loop
**What happens:** Agent doesn't understand what the caller said, asks for clarification, still doesn't understand, asks the same clarification question in the same words. After 2-3 loops, caller hangs up.
**Exact fix:**
- Add multi-level fallback to prompt: "If you don't understand, first rephrase your question differently. On the second attempt, offer specific options: 'Are you asking about X, Y, or something else?' On the third attempt, say 'I want to make sure I get this right for you -- let me connect you with a specialist.'"
- Never repeat the exact same question twice
- Escalate to human after 3 failed understanding attempts

### Mistake #20: No Graceful Recovery from Errors
**What happens:** Agent says something wrong, caller corrects them, and the agent either ignores the correction or doesn't acknowledge the mistake.
**Exact fix:**
- Add to prompt: "If the caller corrects you, immediately acknowledge: 'Oh, my mistake' or 'Sorry about that, you're right' -- then correct course. Don't just silently change your answer without acknowledging the error."
- Self-correction phrases: "Oh wait, let me correct that", "Sorry, I misspoke", "You're right, my bad"

---

## CATEGORY 6: VOICE AND AUDIO QUALITY

### Mistake #21: Wrong Voice-Brand Match
**What happens:** Using a TTS voice that doesn't match the brand context. Young tech startup using an authoritative news-anchor voice. Medical office using a casual surfer-dude voice.
**Exact fix:**
- A/B test male vs. female voices (data shows perception varies by demographic: some find male more authoritative, female more empathetic)
- Test voice speed: 0.9x (slower, better comprehension) vs. 1.1x (faster, feels more natural)
- Match voice age/style to brand persona
- Test with real callers, not just internal team

### Mistake #22: No Ambient Sound
**What happens:** The audio is perfectly clean and sterile. No background noise at all. Real call centers and offices have ambient sound. Perfect silence signals "this is synthesized."
**Exact fix:**
- Enable Retell `ambient_sound`: "office" at low volume (0.1-0.3)
- Options: office, coffee-shop, or custom ambient
- Set `ambient_sound_volume` to subtle (too loud is distracting, but a hint of background makes it feel real)

### Mistake #23: Audible Artifacts (Clicks, Glitches, Unnatural Breaths)
**What happens:** TTS produces audible clicks between sentences, unnatural breath sounds, abrupt volume changes, or echo/double-read artifacts.
**Test for it:** Listen continuously for 5+ minutes. Artifacts become obvious with extended listening (the "auditory fatigue test").
**Exact fix:**
- Run MOS-Lite quality check: target average score 4.0+ out of 5.0 (below 3.5 = critical failure)
- Test prosody with sentence pairs: statements vs. questions should have different pitch contours
- Test homograph pronunciation: "I read the book" vs. "I will read the book" (target: 99%+ accuracy)
- Check for clean audio: no clicks, hisses, volume jumps, or echo artifacts

### Mistake #24: Mispronouncing Numbers, Emails, and URLs
**What happens:** Agent says "four-one-five-eight-nine-two-three-two-four-five" as one continuous string instead of grouped naturally. Or says "at sign" instead of "at" for email addresses.
**Exact fix:**
- Phone numbers: "four one five - eight nine two - three two four five" (grouped with dashes/pauses)
- Emails: "name at company dot com" (spell unusual parts letter by letter)
- URLs: "en-kay-laundry dot com" (single letters spelled out, recognizable words spoken normally)
- Times: "three thirty PM" not "fifteen thirty" or "3:30 PM"
- Always confirm numbers by repeating: "That's 5-5-5, 1-2-3, 4-5-6-7, right?"
- Add pronunciation guide to prompt for brand-specific terms

---

## CATEGORY 7: CONVERSATION BOUNDARIES AND ESCALATION

### Mistake #25: No Human Escalation Path
**What happens:** Caller explicitly says "I want to talk to a real person" and the agent either ignores it, tries to handle it anyway, or says "I'm sorry, I can't do that."
**Why it matters:** This is the #1 trust destroyer. Callers who feel trapped with a bot become hostile.
**Exact fix:**
- Add to prompt: "If the caller asks to speak with a human, a real person, a manager, or a supervisor, immediately say 'Of course, let me transfer you right now' and execute the transfer function. Never try to convince them to stay."
- Automatic escalation triggers:
  - Caller explicitly requests human
  - 3+ turns of negative sentiment
  - Question outside knowledge base scope
  - Compliance/legal concern raised
  - Agent confidence below 70% for 2+ consecutive turns

### Mistake #26: Lying About Being Human
**What happens:** Caller asks "Am I talking to a robot?" and the agent says "No, I'm a real person" or deflects.
**Why it matters:** If discovered (and it will be), trust is permanently destroyed. Many jurisdictions require disclosure.
**Exact fix:**
- Add to prompt: "If asked whether you are AI, a bot, or a robot, be honest: 'I'm an AI assistant for [company name]. But I can help with most things -- and if there's something I can't handle, I'll get you to a real person right away.' Never claim to be human."

### Mistake #27: Not Knowing When to Stop
**What happens:** Agent keeps trying to be helpful when the caller clearly wants to end the call. "Is there anything else I can help you with? Are you sure? Let me know if..."
**Exact fix:**
- Add to prompt: "When the caller says goodbye, thanks you and sounds like they're wrapping up, or says they're all set, give a brief friendly closing and end the call. Don't ask more than once if there's anything else. Example: 'Awesome, glad I could help. Have a great day!'"

---

## CATEGORY 8: SILENCE AND HOLD HANDLING

### Mistake #28: Not Handling Caller Silence Correctly
**What happens:** Caller goes silent (thinking, distracted, or put the phone down). Agent either immediately speaks or waits too long.
**Exact fix:**
- Silence escalation protocol:
  - 3 seconds: "Are you still there?"
  - 6 seconds: "I'm here whenever you're ready."
  - 10 seconds: "If we got disconnected, I'll try calling you back."
  - 15 seconds: End call gracefully
- Add to prompt for non-reasoning models: use `NO_RESPONSE_NEEDED` stop sequence when caller says "hold on" or "give me a sec"
- For reasoning models: "When the caller asks you to hold or wait, simply stay quiet until they speak again."

### Mistake #29: No Acknowledgment When Returning from a Lookup
**What happens:** Agent goes to look something up, goes silent, then comes back with the answer without signaling the transition.
**Exact fix:**
- Before lookup: "Let me pull that up real quick."
- During lookup (if >2 seconds): streaming filler so the line isn't dead
- After lookup: "Okay, so I found..." or "Alright, got it --"

---

## A/B TESTING INSIGHTS: WHAT ACTUALLY MOVES THE NEEDLE

Based on published A/B testing data from Regal.ai and Canonical.chat:

| Test Variable | Winning Config | Impact |
|---|---|---|
| Voice temperature | 1.0-1.25 (expressive) vs. <0.6 (flat) | Higher engagement, longer conversations, more natural feel |
| Voice speed | 0.95-1.05x vs. 1.2x | Slower improved comprehension; slight slowdown beats default speed |
| Scripted vs. flexible phrasing | "Say something like..." examples | Flexible phrasing outperforms rigid scripts -- use examples not exact words |
| Response length | Under 2 sentences per turn | Dramatically reduces caller interruptions and abandonment |
| Conversational openers | Varied natural openers per turn | Eliminates "broken record" perception |
| Ambient office sound | Enabled at low volume | Callers less likely to ask "am I talking to a bot?" |
| Backchannel enabled | Yes, medium frequency | Reduces "are you there?" questions by significant margin |
| Noise cancellation pre-VAD | Enabled | 3.5x reduction in false interruptions, 30% higher CSAT |
| Personality warmup | Adding casual opener ("How's your day?") | No statistically significant improvement -- skip it, get to the point |

---

## QUALITY TESTING CHECKLIST (5 Tests Every Agent Must Pass)

1. **MOS-Lite Score:** Have 5+ people rate the voice 1-5. Target: 4.0+ average. Below 3.5 = rebuild.
2. **Prosody Test:** Does "Really?" sound different from "Really." ? Questions must have rising intonation.
3. **Homograph Test:** "I read a book yesterday" vs. "I will read a book tomorrow" -- correct pronunciation without phonetic hints? Target: 99%+.
4. **Artifact Test:** Listen for 5+ continuous minutes. Any clicks, hisses, volume jumps, or echo = fail.
5. **Fatigue Test:** Can you listen for 5 minutes without the voice becoming grating? If no = change voice or reduce temperature.

---

## RETELL-SPECIFIC PARAMETER QUICK REFERENCE

```
Agent Configuration:
  responsiveness: 0.8 - 1.0          # How fast agent responds (higher = faster)
  interruption_sensitivity: 0.7 - 0.9 # How easily caller can interrupt (higher = easier)
  enable_backchannel: true
  backchannel_frequency: "medium"      # low / medium / high
  backchannel_words: ["uh-huh", "I see", "mm-hmm", "okay", "right", "got it"]
  ambient_sound: "office"
  ambient_sound_volume: 0.1 - 0.3     # Subtle background
  voice_temperature: 1.0 - 1.25       # Expressiveness (higher = more varied)
  voice_speed: 0.95 - 1.05            # Slightly under default often sounds most natural

System Prompt Must Include:
  - "Keep responses under 2 sentences"
  - "Use contractions and casual language"
  - "Start sentences with natural openers: got it, sure, okay, makes sense, right"
  - "Never repeat the same acknowledgment phrase twice in a row"
  - "If interrupted, stop immediately and listen"
  - "If caller sounds frustrated, acknowledge emotion before solving"
  - "Never ask for information already provided"
  - "If asked whether you're AI, be honest"
  - "Spell out phone numbers in groups, emails as name-at-domain-dot-com"
  - "If you don't understand after 2 tries, rephrase then offer options then escalate"
```

---

## Sources

- [Top 8 Mistakes to Avoid When Creating an AI Voice Agent](https://binarymarvels.com/mistakes-to-avoid-when-creating-an-ai-voice-agent/)
- [AI Voice Agent Challenges Explained](https://justcall.io/blog/ai-voice-agent-challenges.html)
- [Common Voice AI Agent Challenges and How to Fix Them](https://www.beconversive.com/blog/voice-ai-challenges)
- [Where AI Voice Agents Fail the Most Today](https://voice-ai-newsletter.krisp.ai/p/where-ai-voice-agents-fail-the-most)
- [Why Interruptions Break Voice AI Systems](https://medium.com/@raghavgarg.work/why-interruptions-break-voice-ai-systems-5bde68ed60f5)
- [Troubleshooting Common Issues in Voice Agent Development - Retell AI](https://www.retellai.com/blog/troubleshooting-common-issues-in-voice-agent-development)
- [Voice AI Prompt Engineering Complete Guide - VoiceInfra](https://voiceinfra.ai/blog/voice-ai-prompt-engineering-complete-guide)
- [How to Build a Good AI Voice Agent - Retell AI](https://www.retellai.com/blog/how-to-build-a-good-voice-agent)
- [Retell AI Prompt Situation Guide](https://docs.retellai.com/build/prompt-situation-guide)
- [5 Must Run A/B Tests for Your AI Voice Agent - Regal.ai](https://www.regal.ai/blog/a-b-tests-for-ai-voice-agent)
- [How to Run A/B Testing for Voice AI Agents - Canonical.chat](https://canonical.chat/blog/ab_testing_voice_ai_agents)
- [Why Most AI Voices Still Sound Robotic - Trillet](https://www.trillet.ai/blogs/human-like-voice-ai)
- [Why Your Voice AI Sounds Robotic and How to Fix It - Optimize Smart](https://www.optimizesmart.com/why-your-voice-ai-sounds-robotic-and-how-to-fix-it/)
- [5 Tests to Stop AI Voice Sounding Like a Robot](https://www.softwaretestingmagazine.com/knowledge/how-to-stop-the-ai-voice-from-sounding-like-a-robot-5-easy-tests-for-naturalness/)
- [Voice AI Prompting Guide - Layercode](https://layercode.com/blog/how-to-write-prompts-for-voice-ai-agents)
- [How Backchanneling Improves UX in AI Voice Agents - Retell AI](https://www.retellai.com/blog/how-backchanneling-improves-user-experience-in-ai-powered-voice-agents)
- [Retell AI Create Agent API Reference](https://docs.retellai.com/api-references/create-agent)
- [Turn Detection and Endpointing - AssemblyAI](https://www.assemblyai.com/blog/turn-detection-endpointing-voice-agent)
- [Using Transformers to Improve End-of-Turn Detection - LiveKit](https://blog.livekit.io/using-a-transformer-to-improve-end-of-turn-detection/)
- [How to Make AI Voice Sound Less Robotic - Murf.ai](https://murf.ai/blog/how-to-make-ai-voice-sound-less-robotic)
- [Angry Callers Accusing Real Support Staff of Being AI - Futurism](https://futurism.com/callers-accusing-customer-support-ai)
