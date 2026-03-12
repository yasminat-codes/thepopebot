# /// script
# requires-python = ">=3.11"
# dependencies = ["yt-dlp", "openai", "anthropic", "python-dotenv"]
# ///
"""YouTube transcript fetcher and learning notes generator.

Usage:
    uv run fetch_and_learn.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
    uv run fetch_and_learn.py --url "..." --verbose
    uv run fetch_and_learn.py --url "..." --no-cache
    uv run fetch_and_learn.py --rss "https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL"
    uv run fetch_and_learn.py --rss "..." --count 3
    uv run fetch_and_learn.py --id "dQw4w9WgXcQ"
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

# Load .env from project root (yasmine-os) or current dir
def _load_env():
    candidates = [
        Path(__file__).parent.parent.parent.parent.parent / ".env",  # yasmine-os root
        Path.home() / "coding" / "yasmine-os" / ".env",
        Path.cwd() / ".env",
    ]
    for path in candidates:
        if path.exists():
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, _, val = line.partition("=")
                        os.environ.setdefault(key.strip(), val.strip())
            return

_load_env()

TRANSCRIPT_MAX_WORDS = 8000
CACHE_FILE = Path.home() / ".cache" / "yasmine-youtube" / "transcripts.json"
CACHE_TTL_DAYS = 7

# OpenRouter model chain (in order of preference)
# self-healed: 2026-03-09: updated to verified-available free model IDs
# updated: 2026-03-09: switched to paid high-quality models for 10k-word note output
OPENROUTER_MODELS = [
    "qwen/qwen3.5-plus-02-15",
    "google/gemini-3.1-flash-lite-preview",
    "openai/gpt-4.1-mini",
]


# ── Cache helpers ─────────────────────────────────────────────────────────────

def _load_cache() -> dict:
    """Read transcript cache from disk. Returns empty dict if missing or corrupt."""
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    """Write cache to disk, creating directories if needed."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, indent=2), encoding="utf-8")


def _is_cached(video_id: str, cache: dict) -> bool:
    """Return True if video_id is in cache and was processed within TTL."""
    entry = cache.get(video_id)
    if not entry:
        return False
    processed_at = entry.get("processed_at", "")
    if not processed_at:
        return False
    try:
        age = datetime.datetime.now() - datetime.datetime.fromisoformat(processed_at)
        return age.days < CACHE_TTL_DAYS
    except Exception:
        return False


def _get_cached_transcript(video_id: str, cache: dict) -> Optional[str]:
    """Return cached transcript text if available."""
    return cache.get(video_id, {}).get("transcript")


def _cache_transcript(video_id: str, transcript: str, meta: dict, cache: dict) -> None:
    """Store transcript in cache with metadata."""
    cache[video_id] = {
        "title": meta.get("title", ""),
        "channel": meta.get("channel", ""),
        "transcript_hash": hashlib.md5(transcript.encode()).hexdigest(),
        "processed_at": datetime.datetime.now().isoformat(),
        "transcript": transcript,
    }


# ── Input detection ────────────────────────────────────────────────────────

def detect_input_type(s: str) -> str:
    """Return 'rss', 'url', or 'id'."""
    s = s.strip()
    if "feeds/videos.xml" in s or ("youtube.com/feeds" in s):
        return "rss"
    if re.match(r"^https?://", s):
        return "url"
    if re.match(r"^[A-Za-z0-9_-]{11}$", s):
        return "id"
    return "url"


def normalize_to_url(s: str) -> str:
    """Convert a video ID to a full URL if needed."""
    if detect_input_type(s) == "id":
        return f"https://www.youtube.com/watch?v={s}"
    return s


def extract_video_id(url: str) -> Optional[str]:
    """Extract the 11-char video ID from a YouTube URL."""
    m = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", url)
    return m.group(1) if m else None


# ── RSS parsing ─────────────────────────────────────────────────────────────

def parse_rss_feed(url: str, limit: int = 10) -> list[dict]:
    """
    Fetch a YouTube RSS feed and return list of video dicts.
    Each dict: {title, url, id, published, description}
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()
    except Exception as e:
        print(f"ERROR: Could not fetch RSS feed: {e}", file=sys.stderr)
        sys.exit(1)

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "yt": "http://www.youtube.com/xml/schemas/2015",
        "media": "http://search.yahoo.com/mrss/",
    }

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"ERROR: Could not parse RSS XML: {e}", file=sys.stderr)
        sys.exit(1)

    entries = root.findall("atom:entry", ns)
    videos = []
    for entry in entries[:limit]:
        video_id = entry.findtext("yt:videoId", namespaces=ns) or ""
        title = entry.findtext("atom:title", namespaces=ns) or "Untitled"
        published = entry.findtext("atom:published", namespaces=ns) or ""
        published = published[:10] if published else ""
        description = ""
        media_group = entry.find("media:group", ns)
        if media_group is not None:
            desc_el = media_group.find("media:description", ns)
            if desc_el is not None and desc_el.text:
                description = desc_el.text[:200].replace("\n", " ")

        videos.append({
            "id": video_id,
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
            "published": published,
            "description": description,
        })

    return videos


# ── yt-dlp metadata ─────────────────────────────────────────────────────────

def fetch_video_metadata(url: str) -> dict:
    """Use yt-dlp --dump-json to get video metadata."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-warnings", url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return {"title": "Unknown", "channel": "Unknown", "upload_date": "", "duration": 0}
        data = json.loads(result.stdout.strip().split("\n")[0])
        upload_date = data.get("upload_date", "")
        date_str = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:8]}" if len(upload_date) == 8 else ""
        duration_s = data.get("duration", 0) or 0
        minutes, seconds = divmod(int(duration_s), 60)
        return {
            "title": data.get("title", "Unknown"),
            "channel": data.get("channel") or data.get("uploader", "Unknown"),
            "upload_date": date_str,
            "duration": f"{minutes}:{seconds:02d}",
            "url": url,
        }
    except Exception:
        return {"title": "Unknown", "channel": "Unknown", "upload_date": "", "duration": "?", "url": url}


# ── VTT cleaning ─────────────────────────────────────────────────────────────

def _vtt_timestamp_to_seconds(ts: str) -> int:
    """Convert VTT timestamp HH:MM:SS.mmm or MM:SS.mmm to integer seconds."""
    ts = ts.split(".")[0]  # drop milliseconds
    parts = ts.split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    return int(parts[0]) * 60 + int(parts[1])


def _format_timestamp(seconds: int) -> str:
    """Format seconds as [H:MM:SS] or [M:SS]."""
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"[{h}:{m:02d}:{s:02d}]"
    return f"[{m}:{s:02d}]"


def _clean_vtt(vtt_text: str, timestamp_interval: int = 60) -> str:
    """
    Convert VTT subtitle format to clean plaintext with periodic timestamp markers.
    Injects a [M:SS] marker whenever the cue time advances by timestamp_interval seconds.
    """
    # Parse VTT cues: (start_seconds, text)
    cue_pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d{3}|\d{2}:\d{2}\.\d{3})\s*-->\s*\S+[^\n]*\n([\s\S]*?)(?=\n\n|\Z)",
        re.MULTILINE,
    )
    cues = []
    for m in cue_pattern.finditer(vtt_text):
        ts_str, raw_text = m.group(1), m.group(2)
        start = _vtt_timestamp_to_seconds(ts_str)
        text = re.sub(r"<[^>]+>", "", raw_text).strip()
        if text:
            cues.append((start, text))

    if not cues:
        # fallback: strip everything
        text = re.sub(r"^WEBVTT.*?\n\n", "", vtt_text, flags=re.DOTALL)
        text = re.sub(r"\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\S+.*\n", "", text)
        text = re.sub(r"<[^>]+>", "", text)
        return re.sub(r"\s+", " ", text).strip()

    # Deduplicate adjacent identical lines and inject timestamps
    output_parts: list[str] = []
    last_ts_injected = -timestamp_interval  # force first marker at 0
    prev_line = ""
    for start, text in cues:
        if start - last_ts_injected >= timestamp_interval:
            output_parts.append(_format_timestamp(start))
            last_ts_injected = start
        if text != prev_line:
            output_parts.append(text)
            prev_line = text

    cleaned = re.sub(r"\s+", " ", " ".join(output_parts)).strip()
    return cleaned


# ── Transcript fetching ──────────────────────────────────────────────────────

def fetch_transcript(video_url: str) -> Optional[str]:
    """
    Download auto-generated subtitles via yt-dlp and return cleaned plaintext.
    Returns None if no captions are available.
    """
    video_id = extract_video_id(video_url) or "video"
    with tempfile.TemporaryDirectory() as td:
        cmd = [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "--skip-download",
            "--no-warnings",
            "-o", f"{td}/{video_id}",
            video_url,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        vtt_files = list(Path(td).glob("*.vtt"))
        if not vtt_files:
            return None
        raw = vtt_files[0].read_text(encoding="utf-8", errors="replace")
        text = _clean_vtt(raw)
        words = text.split()
        if len(words) > TRANSCRIPT_MAX_WORDS:
            text = " ".join(words[:TRANSCRIPT_MAX_WORDS]) + "\n\n[transcript truncated at 8,000 words]"
        return text


# ── AI analysis ──────────────────────────────────────────────────────────────

NOTE_TEMPLATE = """\
# {Video Title}

**Channel:** {channel} | **Published:** {date} | **Duration:** {duration}
**URL:** {url}

---

## TL;DR
{2-3 sentences: the core argument or insight, stated opinionatedly}

## Key Takeaways
- {specific takeaway 1}
- {specific takeaway 2}
- {specific takeaway 3}

## Core Concepts [placeholder — keep for backward compat]

### {Concept Name}
{Explanation}

## Actionable Insights
- {concrete thing to do, grounded in the video}

## Memorable Quotes
> "{near-verbatim quote that crystallises the point}"

## Questions This Raises
- {open question worth exploring}

## Tags
#{topic} #{subtopic}
"""

MOC_MAP = {
    "technology": ("_MOC-Technology", "Technology"),
    "business": ("_MOC-Business", "Business"),
    "content-creation": ("_MOC-Content", "Content Creation"),
    "learning": ("_MOC-Learning", "Learning"),
    "smarterflo": ("_MOC-Smarterflo", "Smarterflo"),
}


def _extract_moc(notes: str) -> str:
    """Parse moc: field from YAML frontmatter in generated notes."""
    m = re.search(r'^moc:\s*(\S+)', notes, re.MULTILINE)
    if m:
        return m.group(1).strip().lower()
    return "technology"


def _build_prompt(meta: dict, transcript: str) -> str:
    today = datetime.date.today().isoformat()
    title = meta.get('title', 'Unknown')
    channel = meta.get('channel', 'Unknown')
    pub_date = meta.get('upload_date', 'Unknown')
    duration = meta.get('duration', 'Unknown')
    url = meta.get('url', '')

    return f"""You are an expert learning-notes generator. Your job is to produce exhaustive, deeply detailed notes from this YouTube transcript. The reader should understand the video's content as well as if they watched it twice and took notes both times. Do not summarise — expand every point fully.

VIDEO METADATA:
Title: {title}
Channel: {channel}
Published: {pub_date}
Duration: {duration}
URL: {url}

OUTPUT — start with the YAML frontmatter block (raw, no code fences), then the note body. Do NOT wrap output in code fences.

---
type: youtube-note
source: {url}
channel: {channel}
published: {pub_date}
duration: "{duration}"
processed: {today}
speaker:
  - FILL: main host/presenter name(s) from the transcript
tags:
  - FILL: choose 2-5 from: tech/ai, tech/dev, smarterflo/strategy, smarterflo/marketing, learning/productivity, content-creation/youtube, business/finance, business/automation
moc: FILL: choose ONE: technology | business | content-creation | learning | smarterflo
status: new
topics:
  - FILL: 6-12 specific topic keyword strings extracted from the content (e.g. "TikTok draft posting", "sub-agent architecture", "model routing cost optimisation")
people:
  - FILL: every named individual mentioned in the video (host, guests, people referenced)
tools:
  - FILL: every tool, app, platform, or product mentioned (e.g. OpenClaw, WhatsApp, yt-dlp, Canva, Anthropic)
related: []
---

# {title}

**Channel:** {channel} | **Published:** {pub_date} | **Duration:** {duration}
**URL:** [Watch here]({url})

---

## TL;DR

[5-7 dense, opinionated sentences. State the core argument the video makes, what the speaker is claiming and why, the single most important insight, who this is most valuable for, and what it changes or updates about how you think. Be specific — name numbers, tools, outcomes.]

---

## Key Takeaways

[12-18 specific, factual bullet points. Each one should be a complete, standalone insight — not a topic label. Include numbers, names, mechanisms, and caveats where present. If a takeaway can be stated more specifically, state it more specifically.]

- [takeaway]
- [takeaway]
- [continue until all major points are captured]

---

## Full Breakdown

[This is the core section. Cover EVERY major topic or segment the video addresses. For a 15-minute video expect 5-8 sections. For a 30-60 minute video expect 10-15 sections. Each section should be 8-15 sentences — dense enough to serve as a standalone reference. Include what was said, how it works, why it matters, specific examples given, caveats raised, and any numbers or data points mentioned.]

### [Segment title from the video] [M:SS]

[Full paragraph(s). 8-15 sentences. Expand every point made. Include examples. Include the "why" behind claims.]

### [Segment title 2] [M:SS]

[Full paragraph(s). Same depth.]

[Continue for every major topic the video addresses. Do not skip any segment.]

---

## Core Concepts & Definitions

[Define every non-obvious term, tool, framework, or platform introduced. If the video introduces 12 concepts, define all 12.]

### [Term or Tool Name]

**What it is:** [1-3 sentence definition — precise, not vague]
**Why it matters:** [practical significance — what changes if you use/know this]
**How it works:** [mechanism, architecture, process — as described in the video]
**Limitations or caveats:** [anything the speaker flagged as a constraint or edge case]

### [Term or Tool Name 2]

[Same structure. Repeat for every concept.]

---

## Step-by-Step Implementation

[Include this section if the video is a tutorial, walkthrough, or demonstrates a process. Reproduce every step faithfully — do not skip or merge steps. Each step should say what to do AND why.]

1. **[Step name]** — [what to do, exact commands or configurations if mentioned, and why this step matters]
2. **[Step name]** — [continue]
[Continue for all steps]

---

## Actionable Insights

[Minimum 10 items. Each one should be a specific, immediately applicable action grounded in what was actually said. Not generic advice — specific mechanics, thresholds, configurations, or decisions the speaker demonstrated or recommended. Format: state the action, then the reasoning behind it.]

- **[Action]:** [What to do exactly + why, grounded in what the speaker said]
- **[Action]:** [Continue]

---

## Failures, Pitfalls & What NOT To Do

[Extract every warning, failure mode, mistake, or anti-pattern the speaker mentioned or implied. Include why it fails and what to do instead. Minimum 4 items.]

- **[Pitfall]:** [What goes wrong and why. What to do instead.]

---

## Memorable Quotes

[Pull 4-8 lines that crystallise a key point. Verbatim or near-verbatim.]

> "[quote]"

> "[quote]"

---

## Connections & Context

[5-8 sentences. What does this video relate to, build on, update, or contradict? What prior knowledge unlocks it fully? What broader trend or pattern does it fit into? What would change your mind on the claims made?]

---

## Open Questions & Follow-Up Research

[6-10 specific questions this video raises that are worth investigating further. Not throwaway observations — specific tensions, gaps, or threads worth pulling.]

- [Question]

---

## Tags

#[tag1] #[tag2] #[tag3]

---

MANDATORY DEPTH REQUIREMENTS — short output is a failure:
- Total note body: target 6,000-10,000 words. Write until the content is fully covered.
- TL;DR: 5-7 sentences minimum. Opinionated. Specific.
- Key Takeaways: 12-18 bullet points. Each one a complete insight, not a topic label.
- Full Breakdown: cover EVERY segment. 8-15 sentences per section. No skipping.
- Core Concepts: define every non-obvious term with what/why/how/limitations.
- Step-by-Step: reproduce ALL steps if the video is a tutorial.
- Actionable Insights: 10+ items. Specific mechanics, not generic advice.
- Failures & Pitfalls: minimum 4 items.
- Quotes: 4-8 pulled lines.
- Open Questions: 6-10 specific follow-up threads.

TIMESTAMPS:
- The transcript contains [M:SS] or [H:MM:SS] markers showing when content occurs.
- Add the relevant timestamp to each Full Breakdown section heading: ### Section Name [M:SS]

RULES:
- Output ONLY the note starting from the opening ---. No preamble, no meta-commentary.
- Replace ALL FILL placeholders with actual extracted values from the transcript.
- people: and tools: must be plain names only (no wikilinks — those are added in post-processing).
- related: must remain as an empty list [].

TRANSCRIPT:
{transcript}
"""


# ── Linking helpers ───────────────────────────────────────────────────────────

def _parse_yaml_list_field(notes: str, key: str) -> list[str]:
    """Extract a YAML list field from frontmatter, returning plain-text items."""
    pattern = rf'^{re.escape(key)}:\s*\n((?:[ \t]+-[ \t]*.+\n?)*)'
    m = re.search(pattern, notes, re.MULTILINE)
    if not m:
        return []
    items = re.findall(r'-\s*(.+)', m.group(1))
    cleaned = []
    for item in items:
        item = item.strip().strip('"\'')
        # Skip placeholder text the AI left unfilled
        if item and item.upper() != "FILL" and not item.startswith("FILL:"):
            cleaned.append(item)
    return cleaned


def _create_stub_note(vault_path: Path, name: str, note_type: str) -> str:
    """
    Create a stub note in the vault if one doesn't exist.
    Returns the vault-relative path without .md extension (for wikilinks).
    note_type: 'person' | 'tool'
    """
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    folder_map = {"person": "06-People", "tool": "04-Knowledge/tools"}
    parent_map = {"person": "06-People/_MOC-People|People", "tool": "04-Knowledge/tools/_MOC|Tools"}
    folder = folder_map.get(note_type, "04-Knowledge/misc")
    parent_link = parent_map.get(note_type, f"{folder}/_MOC|{note_type.capitalize()}")
    rel_path = f"{folder}/{slug}"
    note_path = vault_path / f"{rel_path}.md"
    if not note_path.exists():
        note_path.parent.mkdir(parents=True, exist_ok=True)
        note_path.write_text(
            f"---\ntype: {note_type}\nname: {name}\n---\n\n"
            f"# {name}\n\n"
            f"<!-- stub — fill in details -->\n\n"
            f"**Parent:** [[{parent_link}]]\n",
            encoding="utf-8",
        )
    return rel_path


def _linkify_yaml_list_field(notes: str, key: str, link_map: dict[str, str]) -> str:
    """Replace plain names inside a YAML list field with [[wikilinks]]."""
    pattern = rf'^({re.escape(key)}:\s*\n(?:[ \t]+-[ \t]*.+\n?)*)'

    def replace_block(m: re.Match) -> str:
        block = m.group(1)
        for name, link in link_map.items():
            # Only replace if not already wikilinked
            if name in block and "[[" not in block.split(name)[0].rsplit("\n", 1)[-1]:
                block = block.replace(
                    f"- {name}", f"- [[{link}|{name}]]", 1
                )
        return block

    return re.sub(pattern, replace_block, notes, flags=re.MULTILINE)


def _linkify_body_first_mentions(notes: str, link_map: dict[str, str]) -> str:
    """
    Wikilink the first mention of each name in the note body (after frontmatter).
    Only links names >= 4 chars to avoid false-positive short words.
    """
    # Find end of frontmatter (second ---)
    fm_match = re.search(r'^---\s*\n', notes[3:], re.MULTILINE)
    if not fm_match:
        return notes
    fm_end = 3 + fm_match.end()
    frontmatter = notes[:fm_end]
    body = notes[fm_end:]

    for name, link in sorted(link_map.items(), key=lambda x: -len(x[0])):
        if len(name) < 4:
            continue
        # Match name not already inside [[...]]
        pattern = rf'(?<!\[\[)(?<!\|)\b{re.escape(name)}\b(?!\|)(?!\]\])'
        replacement = f'[[{link}|{name}]]'
        new_body = re.sub(pattern, replacement, body, count=1)
        if new_body != body:
            body = new_body

    return frontmatter + body


def generate_notes(meta: dict, transcript: str, verbose: bool = False) -> tuple[str, str]:
    """
    Generate learning notes via provider chain:
    1. OpenRouter (5 cheap model fallbacks)
    2. ZAI (GLM)
    3. Anthropic claude-haiku
    4. OpenAI gpt-4o-mini
    Returns (notes_markdown, provider_label).
    """
    prompt = _build_prompt(meta, transcript)

    # 1. OpenRouter — 5 cheap model fallbacks
    openrouter_key = os.environ.get("OPENROUTER_API_KEY")
    if openrouter_key:
        from openai import OpenAI
        or_client = OpenAI(
            api_key=openrouter_key,
            base_url="https://openrouter.ai/api/v1",
        )
        for model in OPENROUTER_MODELS:
            try:
                resp = or_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=16000,
                )
                result = resp.choices[0].message.content
                if result and result.strip():
                    if verbose:
                        print(f"[PROVIDER] OpenRouter {model}", file=sys.stderr)
                    return result.strip(), f"OpenRouter {model}"
            except Exception as e:
                print(f"[OpenRouter {model}] failed: {e}", file=sys.stderr)
                continue
        print("[OpenRouter] all models failed — trying ZAI", file=sys.stderr)

    # 2. ZAI (GLM)
    zai_key = os.environ.get("ZAI_API_KEY")
    if zai_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=zai_key,
                base_url="https://open.bigmodel.cn/api/paas/v4/",
            )
            resp = client.chat.completions.create(
                model="glm-4-plus",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=6000,
            )
            if verbose:
                print("[PROVIDER] ZAI glm-4-plus", file=sys.stderr)
            return resp.choices[0].message.content.strip(), "ZAI glm-4-plus"
        except Exception as e:
            print(f"[ZAI] failed: {e} — trying Anthropic", file=sys.stderr)

    # 3. Anthropic
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
            )
            if verbose:
                print("[PROVIDER] Anthropic claude-haiku-4-5-20251001", file=sys.stderr)
            return msg.content[0].text.strip(), "Anthropic claude-haiku-4-5-20251001"
        except Exception as e:
            print(f"[Anthropic] failed: {e} — trying OpenAI", file=sys.stderr)

    # 4. OpenAI
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=16000,
            )
            if verbose:
                print("[PROVIDER] OpenAI gpt-4o-mini", file=sys.stderr)
            return resp.choices[0].message.content.strip(), "OpenAI gpt-4o-mini"
        except Exception as e:
            print(f"[OpenAI] failed: {e}", file=sys.stderr)

    sys.exit("ERROR: All AI providers failed. Check API keys in .env.")


VAULT_ROOT = Path.home() / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents" / "Yasmine-OS"


def _ensure_channel_note(channel_link: str, channel_name: str, sample_url: str) -> None:
    """
    Create a stub channel note in the Obsidian vault if one doesn't already exist.
    channel_link e.g. "04-Knowledge/youtube/channels/greg-isenberg"
    """
    note_path = VAULT_ROOT / f"{channel_link}.md"
    if note_path.exists():
        return
    note_path.parent.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    note_path.write_text(
        f"---\n"
        f"type: youtube-channel\n"
        f"channel: {channel_name}\n"
        f"created: {today}\n"
        f"tags:\n"
        f"  - type/youtube-channel\n"
        f"---\n\n"
        f"# {channel_name}\n\n"
        f"**Focus:** <!-- describe what this channel covers -->\n\n"
        f"---\n\n"
        f"## All Videos\n\n"
        f"```dataview\n"
        f"TABLE WITHOUT ID\n"
        f"  link(file.link, file.name) AS \"Title\",\n"
        f"  published AS \"Published\",\n"
        f"  duration AS \"Duration\"\n"
        f"FROM \"04-Knowledge/youtube/videos\"\n"
        f"WHERE type = \"youtube-note\" AND channel = \"{channel_name}\"\n"
        f"SORT published DESC\n"
        f"```\n\n"
        f"## Recent Videos (Last 5)\n\n"
        f"```dataview\n"
        f"TABLE WITHOUT ID\n"
        f"  link(file.link, file.name) AS \"Title\",\n"
        f"  published AS \"Published\"\n"
        f"FROM \"04-Knowledge/youtube/videos\"\n"
        f"WHERE type = \"youtube-note\" AND channel = \"{channel_name}\"\n"
        f"SORT published DESC\n"
        f"LIMIT 5\n"
        f"```\n\n"
        f"---\n\n"
        f"**Parent:** [[04-Knowledge/youtube/_MOC|YouTube Knowledge]]\n",
        encoding="utf-8",
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def process_video(url: str, verbose: bool = False, no_cache: bool = False) -> str:
    """Fetch transcript + metadata and return generated learning notes."""
    url = normalize_to_url(url)
    video_id = extract_video_id(url) or url

    print(f"Fetching metadata: {url}", file=sys.stderr)
    meta = fetch_video_metadata(url)

    cache = _load_cache()

    if not no_cache and _is_cached(video_id, cache):
        transcript = _get_cached_transcript(video_id, cache)
        if verbose:
            print(f"[CACHE HIT] video_id={video_id}", file=sys.stderr)
    else:
        if verbose:
            print(f"[CACHE MISS] Fetching transcript from YouTube...", file=sys.stderr)
        else:
            print(f"Fetching transcript...", file=sys.stderr)
        transcript = fetch_transcript(url)
        if transcript:
            _cache_transcript(video_id, transcript, meta, cache)
            _save_cache(cache)

    if not transcript:
        return (
            f"# {meta.get('title', 'Unknown')}\n\n"
            f"**URL:** {url}\n\n"
            "> No captions available for this video. "
            "Try a video with closed captions or auto-generated subtitles enabled.\n\n"
            "> **Tip:** Use the `last30days` skill to research this topic instead."
        )

    word_count = len(transcript.split())
    if verbose:
        print(f"[TRANSCRIPT] {word_count} words", file=sys.stderr)
    else:
        print(f"Generating notes ({word_count} words)...", file=sys.stderr)

    notes, provider = generate_notes(meta, transcript, verbose=verbose)

    # Strip code fences if model wrapped output in ``` blocks
    if notes.startswith("```"):
        notes = re.sub(r'^```[^\n]*\n', '', notes)
        notes = re.sub(r'\n```\s*$', '', notes)

    # Build channel slug for per-channel MOC link
    # e.g. "Greg Isenberg" -> "greg-isenberg"
    channel_name = meta.get("channel", "unknown")
    channel_slug = re.sub(r"[^a-z0-9]+", "-", channel_name.lower()).strip("-")
    channel_link = f"04-Knowledge/youtube/channels/{channel_slug}"

    # Ensure channel note exists in Obsidian vault (stub if missing)
    _ensure_channel_note(channel_link, channel_name, meta.get("url", ""))

    # Inject video_id and ai_provider into frontmatter (after processed: line)
    vid_id = extract_video_id(url) or ""
    notes = re.sub(
        r'(processed:\s*\S+)',
        lambda m: m.group(0) + f"\nai_provider: \"{provider}\"" + (f"\nvideo_id: {vid_id}" if vid_id else ""),
        notes,
        count=1,
    )

    # Build people + tools stub notes and wikilink maps
    people = _parse_yaml_list_field(notes, "people")
    tools = _parse_yaml_list_field(notes, "tools")

    people_map: dict[str, str] = {}
    for person in people:
        link = _create_stub_note(VAULT_ROOT, person, "person")
        people_map[person] = link

    tools_map: dict[str, str] = {}
    for tool in tools:
        link = _create_stub_note(VAULT_ROOT, tool, "tool")
        tools_map[tool] = link

    link_map = {**people_map, **tools_map}

    # Linkify people and tools inside their YAML list fields
    if people_map:
        notes = _linkify_yaml_list_field(notes, "people", people_map)
    if tools_map:
        notes = _linkify_yaml_list_field(notes, "tools", tools_map)

    # Linkify first body mentions
    if link_map:
        notes = _linkify_body_first_mentions(notes, link_map)

    # Populate related: [] with generated links (people + tools + channel)
    all_related = list(people_map.values()) + list(tools_map.values())
    if all_related:
        related_lines = "\n".join(f'  - "[[{lnk}]]"' for lnk in all_related[:12])
        notes = re.sub(
            r'^related:\s*\[\]',
            f"related:\n{related_lines}",
            notes,
            flags=re.MULTILINE,
            count=1,
        )

    # Inject video embed after **URL:** line (done here, not in AI prompt, for provider consistency)
    if vid_id:
        title = meta.get("title", "")
        embed_line = f"\n\n![{title}]({url})"
        notes = re.sub(
            r'(\*\*URL:\*\*[^\n]+)',
            lambda m: m.group(0) + embed_line,
            notes,
            count=1,
        )

    # Append provider attribution + channel parent link (anti-orphan)
    notes = notes.rstrip() + (
        f"\n\n---\n*Generated by {provider} · yt-dlp transcript*\n\n"
        f"**Channel:** [[{channel_link}]]\n"
    )

    # Auto-save to Obsidian vault
    published = meta.get("upload_date", "") or meta.get("published", "")
    date_prefix = published[:10] if published else "unknown-date"
    title = meta.get("title", "untitled")
    # Sanitize title for filesystem
    safe_title = re.sub(r'[\\/:*?"<>|]', "", title).strip()
    note_filename = f"{date_prefix} - {safe_title}.md"
    note_path = VAULT_ROOT / "04-Knowledge" / "youtube" / "videos" / note_filename
    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(notes, encoding="utf-8")
    print(f"[SAVED] {note_path}", file=sys.stderr)

    return notes


def main():
    parser = argparse.ArgumentParser(
        description="Fetch YouTube transcript and generate structured learning notes."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", metavar="URL", help="YouTube video URL or video ID")
    group.add_argument("--id", metavar="ID", dest="video_id", help="11-char YouTube video ID")
    group.add_argument("--rss", metavar="RSS_URL", help="YouTube RSS feed URL")
    parser.add_argument(
        "--count", type=int, default=0, metavar="N",
        help="With --rss: process top N videos automatically (no prompt)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print debug info to stderr: provider used, cache hit/miss, word count"
    )
    parser.add_argument(
        "--no-cache", action="store_true", dest="no_cache",
        help="Force fresh transcript fetch even if cached within 7 days"
    )
    args = parser.parse_args()

    if args.url:
        print(process_video(args.url, verbose=args.verbose, no_cache=args.no_cache))

    elif args.video_id:
        url = f"https://www.youtube.com/watch?v={args.video_id}"
        print(process_video(url, verbose=args.verbose, no_cache=args.no_cache))

    elif args.rss:
        videos = parse_rss_feed(args.rss, limit=10)
        if not videos:
            print("ERROR: No videos found in RSS feed.", file=sys.stderr)
            sys.exit(1)

        if args.count > 0:
            to_process = videos[: args.count]
            for i, v in enumerate(to_process, 1):
                print(f"\n{'='*60}", file=sys.stderr)
                print(f"[{i}/{len(to_process)}] {v['title']}", file=sys.stderr)
                print(process_video(v["url"], verbose=args.verbose, no_cache=args.no_cache))
                if i < len(to_process):
                    print("\n---\n")
        else:
            print("Recent videos from feed:\n")
            for i, v in enumerate(videos, 1):
                date = f" ({v['published']})" if v['published'] else ""
                print(f"  {i:2}. {v['title']}{date}")
                print(f"      {v['url']}")
            print(
                "\nRun with --url <URL> to process a specific video, "
                "or --count N to process the top N automatically."
            )


if __name__ == "__main__":
    main()
