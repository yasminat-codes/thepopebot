# URL Pronunciation Rules

## Core Principle

URLs must be broken into natural spoken segments. Pronounce recognizable words as words,
spell out ambiguous character sequences letter by letter.

## Symbol Replacements

| Symbol | Spoken As |
|--------|-----------|
| `.` | "dot" |
| `/` | "slash" |
| `-` | "dash" |
| `_` | "underscore" |
| `://` | (skip, start after protocol) |
| `www.` | "w-w-w dot" or "triple-w dot" |
| `?` | "question mark" (usually omit query strings entirely) |
| `=` | "equals" |
| `&` | "and" |

## Segment Identification

1. **Remove protocol** -- Do not say "h-t-t-p-s colon slash slash"
2. **Handle www** -- Say "w-w-w dot" if present, or skip if the domain works without it
3. **Domain name** -- Pronounce as word(s) if recognizable, spell out if not
4. **TLD** -- Common TLDs are spoken as words (.com, .org, .net)
5. **Path segments** -- Pronounce each segment naturally
6. **Query strings** -- Usually omit unless specifically needed

## Examples

### Simple URL
**Input:** `www.google.com`
**Output:** "w-w-w dot google dot com"

### Business URL
**Input:** `www.nklaundry.com`
**Output:** "w-w-w dot n-k-laundry dot com"
Note: "nk" is ambiguous so spell it out, "laundry" is a word so pronounce it.

### URL with Path
**Input:** `smarterflo.com/pricing`
**Output:** "smarter-flo dot com slash pricing"

### URL with Subdomain
**Input:** `app.smarterflo.com`
**Output:** "app dot smarter-flo dot com"

### Complex URL
**Input:** `docs.example.com/api/v2/users`
**Output:** "docs dot example dot com slash A-P-I slash v-two slash users"

### URL with Hyphens
**Input:** `my-dental-clinic.com`
**Output:** "my dash dental dash clinic dot com"

## Deciding: Spell Out vs Pronounce

| Segment | Decision | Reasoning |
|---------|----------|-----------|
| `google` | Pronounce | Recognizable word/brand |
| `nk` | Spell out | Not a pronounceable segment |
| `laundry` | Pronounce | Common English word |
| `api` | Spell out | Acronym, say "A-P-I" |
| `docs` | Pronounce | Short for "documents" |
| `flo` | Pronounce | Short word, sounds clear |
| `xq7` | Spell out | Random character sequence |

### Rules of Thumb

- 1-2 consonants with no vowels -> spell out (nk, pt, dg)
- 3+ letters that form a word -> pronounce (app, dev, api as spelled-out)
- Known abbreviations -> spell out (api, sdk, url, faq)
- Known brand names -> pronounce as the brand says (not phonetically)

## Prompt Template

```
IMPORTANT PRONUNCIATION RULE FOR URLS:
When you need to say the website address "{url}", pronounce it as:
"{spoken_version}"
Do not say "h-t-t-p" or "colon slash slash". Start with the domain name.
Say it slowly and clearly. Offer to spell it out if the caller needs.
```

### Example Prompt Injection

```
IMPORTANT PRONUNCIATION RULE FOR URLS:
Our website is nklaundry.com. When saying it, pronounce it as:
"n-k-laundry dot com"
Spell out "n-k" letter by letter, then say "laundry" as a word.
```

## Edge Cases

- **IP addresses:** `192.168.1.1` -> "one nine two dot one six eight dot one dot one"
- **Ports:** `localhost:3000` -> "localhost colon three thousand" or "localhost colon three zero zero zero"
- **Unusual TLDs:** `.io` -> "dot i-o", `.ai` -> "dot A-I", `.dev` -> "dot dev"
- **Long paths:** Only say the domain; offer to send the full link via text/email instead
- **Encoded characters:** `%20` -> skip these, simplify the URL for speech
