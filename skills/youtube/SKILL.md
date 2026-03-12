---
name: youtube
description: >
  Generate structured learning notes from YouTube videos or RSS feeds.
  Accepts video URL, video ID, or channel/playlist RSS URL. Fetches
  transcript via yt-dlp, analyses with AI, outputs formatted markdown.
  Triggers: youtube, transcript, video notes, learning notes, channel feed.
argument-hint: <video-url | rss-url | video-id>
disable-model-invocation: true
allowed-tools: Bash, Read
metadata:
  version: "2.0.1"
  author: yasmine-seidu
  category: learning
context: fork
agent: general-purpose
---

# YouTube Learning Notes

Convert YouTube content into structured learning notes. Accepts a video URL, video ID, or RSS feed URL.

---

## Input Types

| Input | Example |
|-------|---------|
| RSS feed URL | `https://www.youtube.com/feeds/videos.xml?channel_id=UCxyz` |
| Playlist RSS | `https://www.youtube.com/feeds/videos.xml?playlist_id=PLxyz` |
| Video URL | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` |
| Short URL | `https://youtu.be/dQw4w9WgXcQ` |
| Video ID | `dQw4w9WgXcQ` (11-char alphanumeric) |

---

## Execution Protocol

### Step 1 — Locate the script

```bash
SCRIPT=""
for candidate in \
    "$(pwd)/.claude/skills/youtube/scripts/fetch_and_learn.py" \
    "$HOME/coding/yasmine-os/.claude/skills/youtube/scripts/fetch_and_learn.py"; do
    if [ -f "$candidate" ]; then
        SCRIPT="$candidate"
        break
    fi
done

if [ -z "$SCRIPT" ]; then
    echo "ERROR: fetch_and_learn.py not found"
    exit 1
fi
```

### Step 2 — Run based on input type

**RSS feed** (lists recent videos for selection):
```bash
cd $HOME/coding/yasmine-os
uv run "$SCRIPT" --rss "RSS_FEED_URL"
```

The script prints a numbered list of up to 10 recent videos. Ask the user which number(s) to process, or `all`. Then run:
```bash
uv run "$SCRIPT" --url "CHOSEN_VIDEO_URL"
```

**RSS with auto-batch** (process N without prompting — cap at 5 unless user requests more):
```bash
uv run "$SCRIPT" --rss "RSS_FEED_URL" --count 3
```

**Video URL or ID**:
```bash
uv run "$SCRIPT" --url "VIDEO_URL_OR_ID"
```

**With verbose output** (shows AI provider used, cache hit/miss, word count):
```bash
uv run "$SCRIPT" --url "VIDEO_URL_OR_ID" --verbose
```

**Force fresh fetch** (bypass 7-day transcript cache):
```bash
uv run "$SCRIPT" --url "VIDEO_URL_OR_ID" --no-cache
```

### Step 3 — Output

- Print the generated markdown notes to the user
- Check note footer for AI provider attribution line
- **Always auto-save to Obsidian** — every YouTube note is saved to the Smarterflo vault. No need to ask. See Integration Protocol below.

---

## Expert Principles

Rules embedded from operational experience — follow without exception:

1. **Never refetch** a transcript cached within the last 7 days. Use `--no-cache` only if the user explicitly asks for a fresh fetch.
2. **Always show provider** — the note footer shows which AI provider was used. If `--verbose` shows CACHED, notes were generated from a prior transcript.
3. **Always auto-save to Obsidian** after every successful note generation. Save to Smarterflo vault `04-Knowledge/youtube/videos/`. Do not ask — just save.
4. **When no captions exist**, suggest `last30days` skill as an alternative: "This video has no captions. You can research this topic with the `last30days` skill instead."
5. **RSS batch cap**: Do not process more than 5 videos automatically unless the user explicitly passes `--count N` with N > 5.

---

## Memory & Caching Protocol

- **Cache location:** `~/.cache/yasmine-youtube/transcripts.json`
- **Cache keys:** `video_id → {title, channel, transcript_hash, processed_at}`
- **TTL:** 7 days — after that, treated as cache miss
- **Cache hit indicator:** `--verbose` prints `[CACHE HIT]` to stderr before note generation
- **Bypass:** `--no-cache` forces fresh transcript fetch regardless of cache age
- **Cache inspect:** `cat ~/.cache/yasmine-youtube/transcripts.json | python3 -m json.tool`

---

## Guardrails — What This Skill Does NOT Do

- Does not support non-English transcripts (yt-dlp set to `en` only)
- Does not handle private or age-restricted videos
- Auto-saves all notes to Yasmine-OS vault `04-Knowledge/youtube/videos/` — no confirmation needed
- Does not batch more than 5 videos without `--count N` flag
- Does not generate notes without a transcript (no summarization from title/description alone)
- Does not create new Obsidian folders; routes to existing folders only
- Does not guarantee transcript quality for auto-generated captions on heavily accented speech

---

## Integration Protocol

### After generating notes, always auto-save:

**Default destination:** Yasmine-OS vault → `04-Knowledge/youtube/videos/{YYYY-MM-DD} - {Video Title}.md`

Save every note automatically — do not ask. Write the file directly to:
```
/Users/yasmineseidu/Library/Mobile Documents/iCloud~md~obsidian/Documents/Yasmine-OS/04-Knowledge/youtube/videos/{YYYY-MM-DD} - {Video Title}.md
```

Add YAML frontmatter: `type: youtube-note`, `source:`, `channel:`, `published:`, `duration:`, `processed:`, `tags:[]`

Add parent link at bottom: `**Parent:** [[_MOC|YouTube Knowledge]]`

Map video tags → Obsidian tag taxonomy: see [references/OBSIDIAN-INTEGRATION.md](references/OBSIDIAN-INTEGRATION.md)

### Filename convention

`YYYY-MM-DD - {Video Title}.md` (use today's date, not upload date)

---

## Requirements

- `yt-dlp` installed: `brew install yt-dlp` or `pip install yt-dlp`
- `OPENROUTER_API_KEY` in `.env` (primary — 5 free model fallbacks); or any of: `ZAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
- `uv` installed: `brew install uv` or `pip install uv`

Full API setup guide: [references/API-SETUP.md](references/API-SETUP.md)

---

## Error Quick-Reference

| Problem | Likely Cause | Quick Fix |
|---------|-------------|-----------|
| "No subtitles found" | No English captions | Suggest `last30days` skill for topic research instead |
| All AI providers failed | Missing/expired API keys | Check `.env` — see [API-SETUP.md](references/API-SETUP.md) |
| RSS parse error | Malformed feed URL | Verify URL matches `feeds/videos.xml?channel_id=` pattern |

Full error table (8 errors, root causes, recovery steps): [references/ERROR-RECOVERY.md](references/ERROR-RECOVERY.md)

---

## Note Format

See [references/note-template.md](references/note-template.md) — the AI is instructed to produce notes in this exact structure.

---

## Self-Healing Protocol

When a new error occurs during execution:

1. Fix the immediate issue so the current run succeeds
2. Check if the error is in [references/ERROR-RECOVERY.md](references/ERROR-RECOVERY.md)
3. If not → add a new row: Error, Root Cause, What You See, Prevention, Recovery
4. If it requires a script fix → update `scripts/fetch_and_learn.py`, add comment `# self-healed: YYYY-MM-DD: <description>`
5. Bump SKILL.md version in frontmatter to next patch increment (e.g. 2.0.0 → 2.0.1)
6. Log the pattern in `~/.claude/self-healing/patterns/skills.md`
