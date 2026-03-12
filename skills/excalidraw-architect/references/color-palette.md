# Color Palette & Brand Style

**This is the single source of truth for all colors and brand-specific styles.** To customize diagrams for your own brand, edit this file — everything else in the skill is universal.

**Brand:** Smarterflo — Warm Developer Minimal
**Canvas:** Dark mode (warm charcoal)
**Color families:** Coral (action/emphasis), Teal (trust/success/AI), Amber (caution)

---

## Shape Colors (Semantic)

Colors encode meaning, not decoration. Each semantic purpose has a fill/stroke pair designed for dark canvas backgrounds.

| Semantic Purpose | Fill | Stroke | When to Use |
|------------------|------|--------|-------------|
| Primary | `#3D1A10` | `#FF6B4A` | Main shapes, default containers, most elements |
| Secondary | `#3D2218` | `#D1492F` | Supporting shapes, secondary containers |
| Tertiary | `#2E1D16` | `#E5573D` | Background groupings, subtle regions |
| Start/Trigger | `#1A3D37` | `#31645B` | Entry points, inputs, origins |
| End/Success | `#163D2E` | `#9DC4BA` | Completion, outputs, success states |
| Warning | `#3D2E00` | `#FFB800` | Caution, alerts, important notices |
| Decision | `#3D1A10` | `#FF6B4A` | Decision diamonds, branching points |
| AI/LLM | `#1A3D37` | `#9DC4BA` | AI agents, LLM calls, Claude/GPT |
| Inactive/Disabled | `#2A2622` | `#9A9590` | Disabled states (use dashed stroke) |
| Error | `#3D1410` | `#D1492F` | Error states, failures, blockers |

**Differentiating similar fills:** Primary and Decision share the same fill/stroke — Decision is always a `diamond` shape, so the shape itself distinguishes them. AI/LLM and Start/Trigger share the same fill — AI uses a slightly larger, more prominent container. End/Success uses the lighter teal stroke (`#9DC4BA`) vs Start's darker stroke (`#31645B`).

**Rule**: Always pair a bright stroke with a dark tinted fill for contrast on dark canvas.

---

## Text Colors (Hierarchy)

Use color on free-floating text to create visual hierarchy without containers.

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#FF6B4A` | Section headings, major labels |
| Subtitle | `#D1492F` | Subheadings, secondary labels |
| Body/Detail | `#9A9590` | Descriptions, annotations, metadata |
| On dark fills | `#FDFAF4` | Text inside dark-filled shapes (cream-white) |
| Emphasis | `#FFB800` | Key terms, callouts, highlighted text |

---

## Evidence Artifact Colors

Used for code snippets, data examples, and other concrete evidence inside technical diagrams.

| Artifact | Background | Text Color |
|----------|-----------|------------|
| Code snippet | `#0f0e0d` | Syntax-colored (see below) |
| JSON/data example | `#0f0e0d` | `#9DC4BA` (teal muted) |

**Syntax colors for code snippets (on `#0f0e0d` background):**

| Token Type | Color |
|------------|-------|
| Keywords | `#FF6B4A` (coral) |
| Strings | `#9DC4BA` (teal muted) |
| Functions/methods | `#FFB800` (amber) |
| Comments | `#9A9590` (muted) |
| Variables/params | `#FDFAF4` (cream) |
| Types/classes | `#D1492F` (deep coral) |

---

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Arrows | Use the stroke color of the source element's semantic purpose |
| Structural lines (dividers, trees, timelines) | `#4C463F` (warm gray) or `#9A9590` (muted) |
| Marker dots (fill + stroke) | Fill: `#FF6B4A`, Stroke: `#D1492F` |

---

## Background

| Property | Value |
|----------|-------|
| Canvas background | `#1D1A17` |
