# Phone Number Pronunciation Rules

## Core Principle

Phone numbers must ALWAYS be read digit by digit, never as large integers. Group digits
naturally with pauses between groups.

## Digit Pronunciation

Each digit is spoken as its word form:

| Digit | Spoken As |
|-------|-----------|
| 0 | "zero" or "oh" (use "oh" in casual, "zero" in formal) |
| 1 | "one" |
| 2 | "two" |
| 3 | "three" |
| 4 | "four" |
| 5 | "five" |
| 6 | "six" |
| 7 | "seven" |
| 8 | "eight" |
| 9 | "nine" |

## Pause Notation

- Single dash `-` between groups = short pause
- Double dash `--` = medium pause (after area code)
- Triple dash `---` = long pause (between major sections)

## US Phone Number Format

**Standard: (XXX) XXX-XXXX**

**Input:** `(415) 892-3245`
**Output:** "four one five -- eight nine two -- three two four five"

**With country code: +1 (XXX) XXX-XXXX**

**Input:** `+1 (415) 892-3245`
**Output:** "plus one --- four one five -- eight nine two -- three two four five"

### US Grouping Rules

1. Area code (3 digits) -- pause
2. First group (3 digits) -- pause
3. Second group (4 digits)

## International Formats

### UK: +44 XXXX XXXXXX

**Input:** `+44 7911 123456`
**Output:** "plus four four --- seven nine one one -- one two three four five six"

### Australian: +61 X XXXX XXXX

**Input:** `+61 4 1234 5678`
**Output:** "plus six one --- four -- one two three four -- five six seven eight"

### Indian: +91 XXXXX XXXXX

**Input:** `+91 98765 43210`
**Output:** "plus nine one --- nine eight seven six five -- four three two one zero"

## Toll-Free Numbers

**Input:** `1-800-FLOWERS`
**Process:** Convert letters to digits using phone keypad, then speak digit by digit.
**Letter mapping:** F=3, L=5, O=6, W=9, E=3, R=7, S=7
**Output:** "one eight hundred -- three five six nine three seven seven"

Alternative: Say the vanity word directly: "one eight hundred flowers"
Recommend including BOTH in the prompt so the agent can use either.

## Extensions

**Input:** `(415) 892-3245 ext. 102`
**Output:** "four one five -- eight nine two -- three two four five --- extension one zero two"

## Prompt Template

```
IMPORTANT PRONUNCIATION RULE FOR PHONE NUMBERS:
Always say phone numbers digit by digit, never as a large number.
When saying the phone number "{phone}", say it as:
"{spoken_version}"
Pause briefly between each group of digits.
If asked to repeat, say it more slowly with longer pauses.
```

### Example Prompt Injection

```
IMPORTANT PRONUNCIATION RULE FOR PHONE NUMBERS:
Always say phone numbers digit by digit, never as a large number.
Our office number (415) 892-3245 should be said as:
"four one five -- eight nine two -- three two four five"
Pause briefly between each group of digits.
```

## Edge Cases

- **All same digit:** `(888) 888-8888` -> "eight eight eight -- eight eight eight -- eight eight eight eight"
- **Short numbers:** `911` -> "nine one one" (no grouping needed)
- **Mixed format:** `415.892.3245` -> same as `(415) 892-3245`, dots are just separators
- **No formatting:** `4158923245` -> detect as US number, apply standard grouping
- **International prefix:** `011-44-...` -> "zero one one --- four four ---..."
