# Email Pronunciation Rules

## Core Rules

Transform any email address into a speakable format that a voice agent can pronounce clearly.

### Symbol Replacements

| Symbol | Spoken As |
|--------|-----------|
| `@` | "at" |
| `.` | "dot" |
| `_` | "underscore" |
| `-` | "dash" |
| `+` | "plus" |

### Character Handling

- **Common words** in the email (info, admin, support, hello, contact) are spoken as words
- **Common domains** (gmail, yahoo, outlook, hotmail, icloud) are spoken as words
- **Common TLDs** (com, org, net, edu, gov) are spoken as words
- **Ambiguous segments** are spelled letter by letter with dashes: `nk` -> "n-k"
- **Numbers** in emails are spoken digit by digit: `john42` -> "john four two"

### Grouping Rules

1. Split the email at `@` into username and domain
2. Split username at `.`, `_`, `-` into segments
3. For each segment, decide: pronounce as word or spell out
4. Split domain at `.` into domain name and TLD
5. Pronounce domain name as word if recognizable, spell out if not


## Examples

### Simple Email
**Input:** `john.smith@gmail.com`
**Output:** "john dot smith at gmail dot com"

### Complex Email
**Input:** `j.nguyen_dev@nklaundry.co.uk`
**Output:** "j dot nguyen underscore dev at n-k-laundry dot co dot u-k"

### Email with Numbers
**Input:** `support42@company.io`
**Output:** "support four two at company dot i-o"

### Email with Plus Addressing
**Input:** `user+tag@domain.com`
**Output:** "user plus tag at domain dot com"


## Prompt Template

Inject this into the agent prompt when the agent needs to say an email address:

```
IMPORTANT PRONUNCIATION RULE FOR EMAILS:
When you need to say the email address "{email}", pronounce it as:
"{spoken_version}"
Say it slowly and clearly. Pause briefly between each segment.
If the caller asks you to repeat it, say it even more slowly.
```

### Example Prompt Injection

```
IMPORTANT PRONUNCIATION RULE FOR EMAILS:
When you need to say the email address "j.nguyen@smarterflo.com", pronounce it as:
"j dot nguyen at smarter-flo dot com"
Say it slowly and clearly. Pause briefly between each segment.
If the caller asks you to repeat it, say it even more slowly.
```


## Edge Cases

- **All-numeric username:** `12345@domain.com` -> "one two three four five at domain dot com"
- **Single letter segments:** `a.b.c@domain.com` -> "a dot b dot c at domain dot com"
- **Subdomain emails:** `user@mail.company.com` -> "user at mail dot company dot com"
- **Hyphenated domains:** `user@my-company.com` -> "user at my dash company dot com"
- **Unusual TLDs:** `.agency`, `.dental`, `.restaurant` -> pronounce as words


## Common Domain Pronunciations

These domains are always spoken as whole words, never spelled out:

| Domain | Pronunciation |
|--------|--------------|
| gmail | "gmail" |
| yahoo | "yahoo" |
| outlook | "outlook" |
| hotmail | "hotmail" |
| icloud | "i-cloud" |
| proton | "proton" |
| aol | "A-O-L" |
