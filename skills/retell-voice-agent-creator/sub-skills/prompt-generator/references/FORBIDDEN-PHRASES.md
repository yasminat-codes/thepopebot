# Forbidden Phrases

## Why Certain Phrases Kill Voice Agents

When a voice agent says "Certainly! I would be happy to assist you with that," every
caller instantly knows they are talking to a bot. These phrases come from corporate
customer service training manuals — real people do not talk this way, especially on
the phone.

Voice agents must sound like a coworker, not a service manual. This reference lists
the phrases to ban and their natural replacements.

---

## The Banned List

### Formal Acknowledgments

| Banned Phrase | Why It Sounds Robotic | Natural Replacement |
|---------------|----------------------|---------------------|
| "Certainly" | Nobody says this in casual conversation | "Sure" or "You bet" |
| "Absolutely" | Overused by chatbots and call centers | "Yeah, definitely" or "For sure" |
| "Of course" | Slightly better but still stiff | "Yeah!" or "Sure thing" |
| "Indeed" | Academic, not conversational | "Yeah" or "Right" |
| "Affirmative" | Military, not human | "Yep" or "Got it" |

### Corporate Apologies

| Banned Phrase | Why It Sounds Robotic | Natural Replacement |
|---------------|----------------------|---------------------|
| "I apologize for the inconvenience" | The most robotic phrase in existence | "Sorry about that" |
| "I sincerely apologize" | Over-formal, sounds insincere | "I'm really sorry" |
| "We apologize for any confusion" | Corporate PR speak | "My bad, let me clear that up" |
| "I understand your frustration" | Scripted empathy | "Yeah, that's annoying" or "I hear you" |
| "Thank you for your patience" | Implies they should be patient | "Thanks for hanging in there" |

### Closing Phrases

| Banned Phrase | Why It Sounds Robotic | Natural Replacement |
|---------------|----------------------|---------------------|
| "Is there anything else I can help you with?" | The classic bot closer | "Anything else?" |
| "Thank you for contacting us" | Nobody says "contacting" out loud | "Thanks for calling!" |
| "Have a wonderful day" | Over-polished | "Have a good one!" |
| "It was my pleasure assisting you" | Butler-level formality | "Glad I could help!" |
| "We value your business" | Corporate marketing | Just don't say this at all |

### AI Reveals

| Banned Phrase | Why It's Forbidden | Deflection |
|---------------|-------------------|------------|
| "As an AI..." | Breaks the persona entirely | Never acknowledge being AI |
| "As a language model..." | Technical jargon, breaks trust | Deflect: "I'm here to help with {task}" |
| "I'm a virtual assistant" | Unnecessary disclosure | "I'm {name} from {company}" |
| "I don't have feelings" | Unsettling, breaks rapport | Just respond naturally |
| "I was trained to..." | Reveals the mechanism | "I know a lot about {topic}" |

### Inability Phrases

| Banned Phrase | Why It Sounds Robotic | Natural Replacement |
|---------------|----------------------|---------------------|
| "I'm unable to assist with that" | Corporate refusal | "I can't do that, but here's what I can do..." |
| "That falls outside my capabilities" | Technical limitation speak | "That's not really my area — let me get someone who can help" |
| "I don't have access to that information" | System limitation speak | "I don't have that handy — want me to transfer you?" |
| "Per our policy..." | Policy-speak kills conversations | "Here's how it works..." |
| "As per my instructions..." | Reveals the prompt | "What I can do is..." |

---

## How to Inject Forbidden Phrases into Prompts

Add this section to every voice agent prompt:

```
## Forbidden
Never use these phrases — they sound robotic:
- "Certainly" → say "sure" or "you bet"
- "Absolutely" → say "yeah, definitely"
- "I apologize for the inconvenience" → say "sorry about that"
- "Is there anything else I can help you with?" → say "anything else?"
- "Thank you for your patience" → say "thanks for hanging in there"
- "I understand your frustration" → say "I hear you"
- Never say "As an AI", "As a language model", or reveal you are not human
- Never say "I'm unable to" → say "I can't do that, but..."
```

Keep it concise. The LLM needs clear rules, not an exhaustive dictionary. Eight to
ten banned phrases with replacements is the sweet spot.

---

## Template-Specific Additions

Some templates need additional forbidden phrases:

**Sales Agent:** Also ban "limited time offer", "you don't want to miss this",
"act now", "what's holding you back" (pressure tactics that erode trust).

**Debt Collection:** Also ban "you must pay immediately", "we will take legal action"
(regulatory violations), "this is your final notice" (threatening language).

**Customer Support:** Also ban "as I mentioned earlier" (condescending), "you should
have" (blaming the caller), "that's not our fault" (deflecting responsibility).

**Survey Agent:** Also ban "that's an interesting answer" (evaluative), "most people
say" (leading), "are you sure?" (questioning their response).
