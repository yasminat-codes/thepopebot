# Canvas & Visual Thinking

## Canvas Basics

Canvas is an infinite whiteboard built into Obsidian core — no plugin required. Saves as a `.canvas` JSON file in your vault.

**Create a canvas:**
- Right-click in file explorer → New canvas
- Command palette → "Canvas: Create new canvas"
- Or from a note: command palette → "Canvas: Open as canvas"

### Card Types

| Type | How to add | Best for |
|------|-----------|---------|
| Text card | Double-click canvas | Raw ideas, notes, labels |
| Note card | Drag note from file explorer onto canvas | Linking existing vault content |
| Web page card | Paste a URL onto canvas | Reference external content |
| Image card | Drag image file onto canvas | Visual references |

### Core interactions

- **Add card**: Double-click empty space on canvas
- **Connect cards**: Hover a card edge until arrow appears → drag to another card
- **Add label to arrow**: Double-click any arrow
- **Group cards**: Select multiple → right-click → Create group
- **Zoom to fit**: Cmd+Shift+H
- **Zoom to selection**: Cmd+Shift+I
- **Collapse/expand note cards**: Toggle to show full note or just title

---

## Canvas Workflow Patterns

**Brainstorming:**
1. Open blank canvas
2. Text cards for raw ideas — don't edit, just dump
3. Draw arrows between related ideas
4. Select related clusters → Create group, label the theme
5. Turn surviving ideas into note cards (right-click card → Convert to file)

**Project planning:**
- One note card per phase or deliverable
- Arrows = dependencies (A → B means B needs A done first)
- Group by sprint or timeline zone
- Color-code by status (Canvas supports card color)

**Mind mapping:**
- Central concept as a large text card
- Radiate sub-topics outward
- Second level = branches, third level = details
- Use groups to collapse entire branches

**Decision mapping:**
- Options as separate cards
- Connect pros/cons text cards to each option
- Add a "Decision" card with the outcome once decided

---

## Excalidraw (Installed in Yasmine-OS)

Excalidraw is a drawing tool with a hand-drawn or clean geometric aesthetic. Unlike Canvas, it's for original drawings — not linking existing notes.

**Create a drawing:**
- Command palette → "Excalidraw: Create new drawing"
- Or: command palette → "Excalidraw: Create new drawing in current folder"

**Key features:**
- Shapes, arrows, text, freehand drawing
- Two styles: "Hand-drawn" (Virgil font) or "Architect" (clean geometric)
- Color fill, stroke width, opacity controls
- Frames for multi-page layouts
- Libraries for reusable shapes

**Saves as `.md`** with embedded SVG — the file is a regular markdown note, fully searchable, and syncs via iCloud.

**Embed into a note:**
```markdown
![[My System Diagram.excalidraw]]
```

Add dimensions to resize:
```markdown
![[My System Diagram.excalidraw|600]]
```

**Best uses for Excalidraw:**
- System architecture diagrams
- Process flows and SOPs
- Client-facing frameworks and models
- Conceptual sketches for proposals
- Visual frameworks you want to reuse (save to library)

---

## Canvas vs Excalidraw: When to Use Which

| Need | Use |
|------|-----|
| Spatial arrangement of existing vault notes | Canvas |
| Exploring relationships between ideas | Canvas |
| Project overview linking to deliverable notes | Canvas |
| Drawing a diagram from scratch | Excalidraw |
| Creating a system architecture visual | Excalidraw |
| Reusable visual framework or model | Excalidraw |
| Embedding a visual inside a note | Excalidraw |
| Free brainstorm dump with no structure | Either |

Rule of thumb: Canvas = thinking with your notes. Excalidraw = thinking with shapes.

---

## Storing Visual Files

| Type | Suggested location |
|------|-------------------|
| Canvas files | `02-Areas/visuals/` or `01-Projects/{project}/` |
| Excalidraw drawings | `02-Areas/visuals/` or alongside the note it supports |
| Excalidraw library | Auto-managed by plugin at `05-Templates/Excalidraw/` |

Keep canvases near the project they belong to — a canvas for a client proposal lives in `01-Projects/client-name/`, not in a generic folder.
