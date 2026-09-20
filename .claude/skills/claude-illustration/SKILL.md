---
name: claude-illustration
description: Draw icons, illustrations, spot art, empty-state art, or blog-card art in Claude's/Anthropic's visual language for this repo. Use whenever the user asks for an icon, illustration, drawing, graphic, symbol, or artwork for a Claude or Anthropic concept surface — including "draw me a…", "I need an icon for…", "make some spot art", or "give me an illustration of…". Also use before editing anything under claude-icons/.
---

# Drawing in Claude's visual language

Everything drawn in this language is **generated from Python, never hand-authored**,
so the hand stays reproducible and globally tunable. The shared drawing helpers live
in `claude-icons/draw.py`. Read that file first — it is short, and it is the language.

## 1. Pick the tier

| | **Icon** | **Illustration** |
|---|---|---|
| Lives in | `claude-icons/icons/` + `icons-mono/` | `claude-icons/illustrations/` |
| Built by | `claude-icons/build.py` | `claude-icons/illustrations.py` |
| Line weight | 11 contour / 8.5 detail | 7.5 contour / 5.5 detail |
| Grid | 256 | 256 (thinner relative line) |
| Must survive | 32px | read large; no size floor |
| Subject | concrete objects — a grill, a car, a watch | humanistic motifs — hands, profiles, knots, botanicals |
| Composition | fills its box evenly | can sit off-centre, run out of frame |

Ambiguous asks resolve like this: **"an icon for X"** or anything going in a list,
toolbar, button or dense UI → icon. **"an illustration", "spot art", "artwork for
this card / empty state / header"** → illustration. If the request names a concrete
object from the app lineup in `playful/icons/`, it is almost always an icon.

Ask which tier only if the answer genuinely changes the work. Otherwise pick and say
which you picked.

## 2. Draw it

Add a function plus a list entry in the relevant build script, then run it:

```bash
python3 claude-icons/build.py          # icons  → icons/ + icons-mono/ + index.html
python3 claude-icons/illustrations.py  # illos  → illustrations/ + its index.html
```

Both scripts rewrite their whole output directory and gallery together. Each function
returns `(ink, accent)` and is registered in the `ICONS` / `PIECES` list with a name,
label and accent swatch.

Compose from the helpers in `draw.py` rather than raw path strings — raw `d=` data gets
the noise filter but **not** the geometry wobble, which is where most of the hand lives:

- `curve(pts, seed, closed, amt, t)` — organic contours. `t` under 1 tightens corners.
- `poly(pts, seed, closed, amt, bow)` — sharp corners, bowed edges. Rectangles, hexes.
- `circ(cx, cy, r, seed)` — wobbled circle.
- `scribble(cx, cy, r, seed)` — a knot of overlapping loops.
- `I(d)` ink, `I(d,"ink-thin")` interior detail, `A(d)` accent, `S(d)` solid fill.

**Never hand-edit files in `icons/`, `icons-mono/` or `illustrations/`.** They are build
output and the next run overwrites them.

## 3. Non-negotiables

- **One ink weight per tier.** Round caps and joins. The line never tapers.
- **Wobble lives in the geometry**, scaled by the global `W` (~0.36) in `draw.py`,
  with only a light noise filter on top. Raising `W` is what makes the work look
  childish; filter-only roughening looks like a distressed vector, not a drawn line.
  If something reads as too shaky or too stiff, change `W` — do not redraw.
- **One flat accent per piece**, unoutlined, offset −8/+8 like a colour plate that
  slipped on press. Behind the line, never filling it.
- **Every piece must read with its accent removed.** Both scripts emit a mono cut.
  If the mono version is ambiguous, the drawing is wrong — colour never carries meaning.
- **No shadows, no gradients, no second outline.** That is what separates this from
  the `playful` clay set. Never mix the two systems on one surface.
- **Palette is fixed** — the `SW` table in `draw.py`, read from anthropic.com's live
  CSS variables. Don't invent colours.

## 4. Motif vocabulary

Anthropic's illustration language is humanistic and literary, not technological.
**Reach for a hand before you reach for a gear.** Hands carry the human–AI
collaboration idea the whole identity rests on. Then: profiles in silhouette, old-world
bulbs, open books, botanicals, knots and threads, node constellations, paper cut-out
geometry. Warm grounds, never white.

## 5. Verify before reporting done

Open the gallery the script just rebuilt and actually look at it:

- Icons: read at **32px colour, 32px mono, and inverted on slate** — all three strips
  are in `claude-icons/index.html`.
- Illustrations: read large, and read in the ink-only grid.

## Traps already hit — don't repeat them

- **High wobble amplitude is the childishness.** Fix in `W`, not by redrawing.
- **A subject needing fine internal detail gets swapped, not thinned.** A golf driver
  is a small oval on a stick at 32px and reads as a ladle. It became a flag pin.
- **Centred accents disappear** behind the ink. They must offset far enough to show.
- **Food drifts toward "bread roll."** Brisket needs a flat bottom, a bark line and
  slice cuts; a dumpling needs pleats notching *down* from the crown, not arcs on top.
- **Abstract motifs make weak icons and strong illustrations.** A cupped-hands or
  tangle drawing that fails at 32px is usually in the wrong tier, not badly drawn.
