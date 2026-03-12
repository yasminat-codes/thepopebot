---
name: ls:visual-prompter
description: PROACTIVELY generates structured, copy-pasteable JSON image prompts for AI generation tools (DALL-E 3, Imagen, Midjourney, Stable Diffusion) across 4 LinkedIn visual formats — image post, infographic, carousel slides, quote graphic — with platform-specific variations ready for n8n/Make automation or direct API calls.
model: sonnet
context: agent
allowed-tools: Read Write Bash mcp__ide__getDiagnostics
metadata:
  version: "2.0.0"
---

# ls:visual-prompter

Generates structured JSON prompts for AI image generation tools. Takes post content as input and outputs ready-to-use JSON prompt sets for DALL-E 3, Google Imagen, Midjourney, or Stable Diffusion.

## Supported Formats

| Format | Dimensions | Use Case |
|--------|-----------|----------|
| image_post | 1080x1080 | Single hero image |
| infographic | 1080x1350 | Data / multi-point content |
| carousel_slide | 1080x1080 (series) | Multi-slide narrative |
| quote_graphic | 1080x1080 | Pull quote / insight |

## Supported Platforms

| Platform Key | Tool |
|---|---|
| `dalle3` | DALL-E 3 via OpenAI API |
| `imagen` | Google Imagen via Vertex AI |
| `midjourney` | Midjourney (prompt text only) |
| `stable_diffusion` | SDXL / SD3 API |

---

## Pipeline

### Phase 1 — Input Post Content

Accept one of:
- Full post text (copy-paste)
- Post ID → look up in `content_queue` Neon table
- Raw topic/hook only

Extract: hook sentence, key points (max 5), tone, content pillar.

### Phase 2 — Format Selection

Ask user to select format or auto-suggest based on content:

- Long-form / multi-point → carousel_slide
- Data-heavy / how-to → infographic
- Single insight / bold statement → image_post
- Direct quote → quote_graphic

If carousel selected: confirm slide count (default: 5 slides).

### Phase 3 — Generate Complete JSON Prompt Set

Build one JSON object per visual asset. All fields required.

**Base structure:**
```json
{
  "platform": "dalle3",
  "format": "carousel_slide",
  "slide_number": 1,
  "dimensions": "1080x1080",
  "style": "clean professional minimal",
  "background": "#1a1a2e",
  "text_overlay": "...",
  "visual_description": "...",
  "brand_colors": ["#...", "#..."],
  "font_style": "modern sans-serif",
  "mood": "authoritative yet approachable",
  "negative_prompt": "stock photo, generic, clipart, busy"
}
```

**Field rules:**
- `visual_description`: 2-4 sentences. Concrete, visual. No abstract nouns.
- `text_overlay`: Exact copy from post. 10 words max per slide for carousel.
- `negative_prompt`: Always include. Suppress generic/stock aesthetics.
- `mood`: Derived from content pillar. See → `references/MOOD-MAP.md`
- `style`: Pulled from `brand_voice_profile.visual_style` if available, else default.

### Phase 4 — Platform-Specific Variations

For each prompt, generate a variation tuned to the target platform's strengths:

- **DALL-E 3**: JSON as-is. Visual description → `prompt` field. Negative prompt dropped (unsupported).
- **Imagen**: Add `aspect_ratio`, `guidance_scale: 7.5`. Rephrase negative as `disallowed_text`.
- **Midjourney**: Convert to `--v 6 --ar 1:1 --style raw` suffix format. Text overlay removed.
- **Stable Diffusion**: Add `cfg_scale: 7`, `steps: 30`, `sampler: "DPM++ 2M Karras"`.

→ See `references/PLATFORM-ADAPTERS.md` for full conversion logic.

### Phase 5 — Export as Copyable Block

Output format:

```
╔══════════════════════════════════════════╗
║  VISUAL PROMPTS — [POST TITLE / TOPIC]   ║
║  Format: carousel_slide (5 slides)       ║
║  Platform: dalle3                        ║
╚══════════════════════════════════════════╝

--- SLIDE 1 ---
[JSON block]

--- SLIDE 2 ---
[JSON block]

... etc.

--- MIDJOURNEY VARIATIONS ---
/imagine [converted prompt text] --v 6 --ar 1:1 --style raw
```

Offer to write JSON to a local file: `visual-prompts-[slug]-[timestamp].json`.

---

## Brand Defaults

When `brand_voice_profile` is accessible in Neon:
- Pull `brand_colors` array
- Pull `visual_style` string
- Pull `font_preferences`

Fallback defaults (when Neon unavailable):
```
brand_colors: ["#1a1a2e", "#4a4a8a", "#ffffff"]
style: "clean professional minimal"
font_style: "modern sans-serif"
mood: "authoritative yet approachable"
```

---

## Content Pillar → Mood Map

| Pillar | Mood | Style Hint |
|--------|------|-----------|
| Thought Leadership | visionary, bold | dark bg, single focal point |
| Education | clear, structured | light bg, grid layout |
| Social Proof | warm, credible | testimonial frame, muted palette |
| CTA | urgent, direct | high contrast, action-oriented |

→ Full mood rules: `references/MOOD-MAP.md`

---

## Error Handling

| Condition | Action |
|-----------|--------|
| No post content provided | Prompt user to paste text or enter post ID |
| Neon unavailable | Use brand defaults, continue |
| content_queue post_id not found | Warn, ask for manual content input |
| Carousel > 10 slides | Cap at 10, warn user |

---

## Output Checklist

Before returning output, verify:
- [ ] Every JSON object has all required fields
- [ ] `text_overlay` is under 10 words per slide
- [ ] `negative_prompt` is present on all DALL-E / SD prompts
- [ ] Platform variations generated for selected target
- [ ] Copyable block formatted cleanly with slide separators

---

## References

- `references/MOOD-MAP.md` — Pillar-to-mood-to-style mapping table
- `references/PLATFORM-ADAPTERS.md` — Per-platform JSON conversion logic
- `references/FORMAT-SPECS.md` — Dimension specs and format guidelines
