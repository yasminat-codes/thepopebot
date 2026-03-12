# Write for the Ear

Complete guide for writing prompts that generate spoken speech, not written text.

## The Core Principle

Everything the agent outputs will be heard, not read. Any visual assumption in
the output breaks the experience. Write every instruction as if the caller is
blind and the agent has no screen.

## Number Rules (CRITICAL)

Numbers are the most common source of broken voice output. Every number in agent
output must be spelled out in words.

### Phone Numbers
- NEVER: "Call us at 415-555-1234"
- ALWAYS: "Call us at four one five, five five five, one two three four"
- Use dash-space groups for natural pacing

### Currency
- NEVER: "$1,500"
- ALWAYS: "fifteen hundred dollars" or "one thousand five hundred dollars"

### Percentages
- NEVER: "3.5%"
- ALWAYS: "three point five percent"

### Dates
- NEVER: "3/15/25"
- ALWAYS: "March fifteenth, twenty twenty-five"

### Times
- NEVER: "3:30 PM"
- ALWAYS: "three thirty PM"
- Always include AM or PM

### Quarters/Periods
- NEVER: "Q2 2026"
- ALWAYS: "the second quarter of twenty twenty-six"

### Email Addresses
- Spell character by character: "n-a-m-e at company dot com"

### URLs
- Phonetic pronunciation: "smarterflow dot a-i slash consulting"

### Codes and Ticket Numbers
- Spell out: "T K dash four four nine two"

### In the Prompt
Add this instruction to every voice agent prompt:
```
NEVER output a digit. Always spell numbers in words. Phone numbers: spell each
digit with pauses. Currency: use words. Dates: use full month names.
```

## Visual Formatting — Never in Output

The following must NEVER appear in agent output:

- **Bullet points** — say "first... second... and third..."
- **Numbered lists** — say "there are three things. One is... two is... and the third is..."
- **Markdown headers or bold text** — TTS reads asterisks or ignores formatting
- **Links** — say the URL phonetically
- **Tables** — describe the data conversationally
- **Parenthetical asides** — restructure as separate sentences
- **Abbreviations** — spell out: "for example" not "e.g."

## Response Length Rules

Voice has strict length constraints that do not apply to text.

- **Maximum 2 sentences per turn** (under 50 words)
- **Under 20 words per sentence** where possible
- At 150 words per minute speaking rate, 50 words takes 20 seconds — already long
- Complex answers: split across multiple turns with questions between them
- If an answer requires more than 2 sentences, say the first part, then ask
  "Would you like me to continue?" or "Should I go into more detail?"

## Single-Question Rule

Voice cannot process multiple questions at once the way text can.

- NEVER stack questions: "Can I get your name, and what's the best number to
  reach you, and what's the issue?"
- ALWAYS one question per turn: "What's your name?" then wait, then "And the
  best number to reach you?" then wait

Add this to every prompt:
```
NEVER ask more than one question per turn. Ask one question, then wait for the
caller to respond before asking the next.
```

## Sentence Construction for Voice

Write for natural speech rhythm:

- Write short sentences
- Like this
- Then explain with one longer sentence that provides the context the caller needs
- Vary sentence length — monotonous length sounds robotic
- Front-load the important information ("Your appointment is Tuesday" not
  "So what I've done is gone ahead and looked at the schedule and it looks like
  the next available time would be Tuesday")

## Anti-Artifact Rules

Add these to every voice agent prompt to prevent common TTS artifacts:

```
NEVER produce sound effects or onomatopoeic expressions in text.
NEVER produce markdown formatting in output.
NEVER produce JSON, HTML, or code in output.
NEVER use asterisks, brackets, or special characters.
NEVER use ellipsis (...) — pause naturally instead.
```

## Prompt Template for Write-for-Ear Compliance

Include this block in the Response Guidelines section of every prompt:

```
## Response Guidelines
- Speak in short sentences. Maximum 2 sentences per response.
- NEVER use digits — spell all numbers in words.
- NEVER use bullet points, numbered lists, or any visual formatting.
- NEVER reference anything visual — no "as you can see" or "click here."
- Spell out email addresses character by character.
- Spell out URLs phonetically.
- Ask only one question per turn, then wait.
- Keep responses under 50 words.
```
