# APPEARANCE.md — Themes, CSS, Callouts, and Fonts Reference

## 1. Themes

Install via: Settings → Appearance → Themes → Browse

After install, select the theme in the dropdown and reload if prompted.

### Recommended for Yasmine's aesthetic (clean, minimal, Stripe/Vercel-like)

| Theme | Style | Notes |
|-------|-------|-------|
| **Minimal** | Clean whitespace, subtle typography, highly configurable | Best overall for Yasmine's aesthetic; pairs perfectly with Style Settings |
| **Things** | Warm, minimal, inspired by Things 3 | Good dark mode; slightly warmer than Minimal |
| **Ebb & Flow** | Flowing typography, elegant spacing | Softer feel; good for reading-heavy vaults |
| **AnuPpuccin** | Pastel palette, clean layout | More colorful but still elegant; popular for PARA vaults |

**Recommendation:** Start with Minimal. It is the most configurable via Style Settings and matches Stripe/Vercel's clean, typography-first aesthetic most closely.

### Style Settings plugin (installed in Yasmine-OS)

After applying a theme, Style Settings adds a panel at Settings → Style Settings with per-theme options:
- Toggle features on/off (e.g., image width, header colors, sidebar style)
- Set custom accent colors
- Choose font size, line height, and reading width
- Most Minimal theme customization happens here, not in CSS

---

## 2. CSS Snippets

Surgical styling — change one thing without touching the whole theme.

**Location:** `.obsidian/snippets/` inside the vault directory.

**Enable:** Settings → Appearance → scroll to CSS Snippets → toggle the snippet on.

**Create a snippet:**
1. Write a `.css` file in the snippets folder
2. Open Settings → Appearance → CSS Snippets → click the reload icon
3. Toggle the snippet on

**Snippet vs theme:** use snippets for targeted changes (one element, one component). Use theme settings for global aesthetic changes.

**Tip:** CSS snippets are vault-specific. A snippet in the Smarterflo vault won't affect Yasmine-OS vault.

See CSS-SNIPPETS.md for a ready-to-use library of snippets for Yasmine's vaults.

---

## 3. Key Obsidian CSS Variables

Target these variables in snippets to control global appearance without fragile selectors.

| Variable | Controls |
|----------|---------|
| `--color-base-00` | Darkest background |
| `--color-base-10` through `--color-base-100` | Background shades (light to dark) |
| `--color-accent` | Accent/highlight color throughout the UI |
| `--color-accent-h`, `--color-accent-s`, `--color-accent-l` | Accent color HSL components |
| `--font-text-theme` | Body/prose font |
| `--font-interface-theme` | UI font (sidebar, menus) |
| `--font-monospace-theme` | Code font |
| `--font-text-size` | Base font size (default: 16px) |
| `--line-height-normal` | Body text line height |
| `--content-width` | Max width of the note content area |
| `--sidebar-width` | Left/right sidebar width |

**Example — change accent color:**
```css
:root {
  --color-accent-h: 215;
  --color-accent-s: 90%;
  --color-accent-l: 55%;
}
```

---

## 4. Callout Types (Built-in)

Callouts are styled blockquotes. Syntax:

```markdown
> [!NOTE]
> Content goes here.
```

### All built-in types

| Type | Default color | Icon |
|------|--------------|------|
| `[!NOTE]` | Blue | Info circle |
| `[!INFO]` | Blue | Info circle |
| `[!TIP]` | Teal/green | Flame |
| `[!SUCCESS]` | Green | Checkmark |
| `[!WARNING]` | Orange | Triangle |
| `[!CAUTION]` | Orange | Fire |
| `[!DANGER]` | Red | Lightning |
| `[!FAILURE]` | Red | X |
| `[!BUG]` | Red | Bug |
| `[!EXAMPLE]` | Purple | List |
| `[!QUOTE]` | Gray | Quote marks |
| `[!ABSTRACT]` | Teal | Clipboard |
| `[!TODO]` | Blue | Checkbox |
| `[!QUESTION]` | Orange | Question mark |

### Foldable callouts

```markdown
> [!NOTE]+
> Starts expanded.

> [!NOTE]-
> Starts collapsed.
```

### Custom callouts (via CSS snippet — see CSS-SNIPPETS.md)

Define your own type with a custom color and icon. Examples for Yasmine: `[!DECISION]`, `[!CLIENT]`, `[!INSIGHT]`.

---

## 5. Font Configuration

Three independent font slots in Settings → Appearance:
- **Interface font** — sidebar, menus, panel labels
- **Editor font** — what you type in the editor
- **Monospace font** — code blocks and inline code

**Custom fonts:**
1. Drop `.ttf` or `.woff2` files into a folder inside the vault (e.g., `assets/fonts/`)
2. Reference in a CSS snippet:

```css
@font-face {
  font-family: "Bricolage Grotesque";
  src: url("assets/fonts/BricolageGrotesque-Regular.ttf");
}

body {
  --font-text-theme: "Bricolage Grotesque", sans-serif;
}
```

**Yasmine's brand fonts:** Bricolage Grotesque (headings/display), Manrope (body), IBM Plex Mono (code). These are already in Canva — if you want them in Obsidian, add the font files to the vault's assets folder.

---

## 6. Pexels Banner Plugin (Installed in Yasmine-OS)

Adds a banner image to the top of a note. Set in frontmatter:

```yaml
---
banner: https://images.pexels.com/photos/12345/pexels-photo-12345.jpeg
banner_height: 200
---
```

**Where to get URLs:** pexels.com → find image → right-click the image → "Copy image address".

**banner_height:** pixels. 150–250 is a good range for a header-style banner without taking over the note.

**No banner:** simply omit the `banner` frontmatter field.

**Tip for Yasmine:** use banners on hub notes, project notes, and MOCs for visual differentiation. Keep daily notes and atomic notes banner-free for speed.

---

## 7. Custom Note Width

The **Custom Note Width** plugin (or the `cssclasses` system) lets specific notes use a wider layout.

### Via cssclasses (built-in Obsidian)

Add to frontmatter:
```yaml
cssclasses: [wide]
```

Then in a CSS snippet, define `.wide`:
```css
.wide .markdown-source-view,
.wide .markdown-reading-view {
  max-width: 1200px;
}
```

**Good for:** Dataview tables, project dashboards, canvas-adjacent notes where content is wide.

**Default reading width:** set globally in Settings → Appearance → "Readable line length" toggle. When on, notes are capped at a comfortable reading width (~700px). The `wide` class overrides this per note.
