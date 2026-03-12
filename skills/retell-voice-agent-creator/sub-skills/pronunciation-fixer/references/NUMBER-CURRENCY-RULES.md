# Number and Currency Pronunciation Rules

## First Line of Defense: normalize_for_speech

Retell's `normalize_for_speech` parameter (boolean, default false) handles many common cases
automatically. Enable it first, then add prompt instructions for specific formatting needs.

**What normalize_for_speech handles:**
- Basic numbers: 42 -> "forty-two"
- Simple currency: $100 -> "one hundred dollars"
- Common formats: dates, times, simple percentages

**What it does NOT handle well:**
- Precise decimal currency: $42.01 -> needs "forty-two dollars and one cent"
- Phone-number-like sequences that should be read as digits
- Numbers that should be ordinal: "1st", "2nd", "3rd"
- Year-format numbers: 2024 should be "twenty twenty-four" not "two thousand twenty-four"


## Currency Rules

### US Dollar Amounts

| Input | Spoken As |
|-------|-----------|
| $5 | "five dollars" |
| $42 | "forty-two dollars" |
| $42.00 | "forty-two dollars" |
| $42.01 | "forty-two dollars and one cent" |
| $42.50 | "forty-two fifty" or "forty-two dollars and fifty cents" |
| $1,250 | "one thousand two hundred fifty dollars" or "twelve fifty" (context-dependent) |
| $1,250.75 | "one thousand two hundred fifty dollars and seventy-five cents" |
| $1M | "one million dollars" |
| $2.5B | "two point five billion dollars" |

### Other Currencies

| Input | Spoken As |
|-------|-----------|
| EUR 50 | "fifty euros" |
| GBP 100 | "one hundred pounds" |
| AUD 75.50 | "seventy-five dollars and fifty cents" (Australian dollars) |
| JPY 10,000 | "ten thousand yen" |

### Prompt Template for Currency

```
CURRENCY PRONUNCIATION:
- Always say the full currency amount clearly
- For amounts with cents, say "X dollars and Y cents"
- For round amounts, just say "X dollars"
- For large amounts, use shorthand: $1.5M = "one point five million dollars"
```


## Number Formats

### Phone Numbers vs Regular Numbers

Context determines pronunciation:
- "Your order number is 4158923245" -> digit by digit (it is an ID)
- "We have 42 items in stock" -> "forty-two" (it is a quantity)
- "Call us at 4158923245" -> digit by digit (it is a phone number)

### Dates

| Input | Spoken As |
|-------|-----------|
| 01/15/2025 | "January fifteenth, twenty twenty-five" |
| 2025-01-15 | "January fifteenth, twenty twenty-five" |
| 15/01/2025 | "fifteenth of January, twenty twenty-five" (UK format) |
| Jan 15 | "January fifteenth" |
| 2024 | "twenty twenty-four" (as a year) |
| 1990 | "nineteen ninety" (as a year) |
| 2000 | "two thousand" (as a year) |
| 2001 | "two thousand one" or "two thousand and one" |

### Percentages

| Input | Spoken As |
|-------|-----------|
| 5% | "five percent" |
| 3.5% | "three point five percent" |
| 0.5% | "half a percent" or "zero point five percent" |
| 100% | "one hundred percent" |
| 99.9% | "ninety-nine point nine percent" |

### Large Numbers

| Input | Spoken As |
|-------|-----------|
| 1,000 | "one thousand" |
| 10,000 | "ten thousand" |
| 100,000 | "one hundred thousand" |
| 1,000,000 | "one million" |
| 1,500,000 | "one point five million" or "one million five hundred thousand" |
| 1,234,567 | "one million two hundred thirty-four thousand five hundred sixty-seven" |

### Ordinal Numbers

| Input | Spoken As |
|-------|-----------|
| 1st | "first" |
| 2nd | "second" |
| 3rd | "third" |
| 21st | "twenty-first" |
| 100th | "one hundredth" |

### Time

| Input | Spoken As |
|-------|-----------|
| 9:00 AM | "nine A-M" |
| 2:30 PM | "two thirty P-M" |
| 12:00 PM | "noon" or "twelve P-M" |
| 12:00 AM | "midnight" or "twelve A-M" |
| 14:30 | "two thirty P-M" (convert from 24h) |


## Prompt Template

```
NUMBER AND CURRENCY PRONUNCIATION:
- Say dollar amounts clearly: "$42.50" = "forty-two dollars and fifty cents"
- Say dates in natural format: "01/15/2025" = "January fifteenth, twenty twenty-five"
- Say percentages clearly: "3.5%" = "three point five percent"
- For order numbers, confirmation codes, or IDs, read them digit by digit
- For quantities and measurements, say them as normal numbers
```


## Integration with normalize_for_speech

**Recommended approach:**

1. Set `normalize_for_speech: true` in the agent config
2. Add specific prompt instructions for edge cases
3. Test with real conversations to catch any remaining issues

```json
{
  "normalize_for_speech": true
}
```

Combined with prompt:
```
Even though numbers are normalized automatically, please follow these specific rules:
- Our pricing: $49.99/month = "forty-nine ninety-nine per month"
- Year references: say "twenty twenty-five" not "two thousand twenty-five"
- Order IDs: always read digit by digit
```
