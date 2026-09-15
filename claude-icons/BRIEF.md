# Claude icon set — build brief

Draw icons in Anthropic's own illustration language, for a Claude concept app.
Subjects come from the app lineup in `playful/icons/` (Big Green Egg, brisket, 911,
Catan hex, palm, camera…). This is a THIRD icon system — never mix it with the
`playful` clay set on one surface.

## Source of truth

Palette is read live from anthropic.com CSS variables, not eyeballed:

    slate   #141413      ivory-light  #faf9f5    ivory-med #f0eee6   ivory-dark #e8e6dc
    clay    #d97757      accent       #c6613f    kraft     #d4a27f   manilla    #ebdbbc
    oat     #e3dacc      olive        #788c5d    cactus    #bcd1ca   fig        #c46686
    heather #cbcadb      cloud-med    #b0aea5

Type: "Anthropic Serif", Georgia for body; "Anthropic Sans", Arial for headings.

## The grammar

1. **One ink weight.** 11 units on a 256 grid for every contour, 8.5 for interior
   detail. Round caps and joins. The line never tapers.
2. **A measured hand, not a shaky one.** Wobble lives in the GEOMETRY — every anchor
   nudged off true, every straight edge bowed — and only then a light noise filter on
   top. Filter-only roughening reads as a distressed vector, not a drawn line. Hold the
   amplitude LOW: this is the single dial between "considered" and "childish".
3. **The paper shape misregisters.** Exactly one flat accent per icon, unoutlined,
   offset −8/+8 like a colour plate that slipped on press. It sits BEHIND the line and
   never fills it.
4. **Every icon must work without its accent.** Ship an ink-only cut. If a subject is
   ambiguous in mono, the drawing is wrong — colour may not carry meaning.
5. **No shadows, no gradients, no second outline.** This is what separates it from the
   clay set.
6. **Built for 32px.** Nothing thinner than 8.5, no gap under 20 units. Detail earns its
   place only if it survives the 32px strip.
7. **Warm grounds.** Drawn for ivory and swatch tiles, not for white.

## How to build it

Generate from a Python script, don't hand-author SVGs — the wobble has to be
reproducible and globally tunable. Helpers:

- `curve(pts, seed, closed)` — Catmull-Rom through jittered anchors, for organic contours.
- `poly(pts, seed, bow)` — sharp corners, gently bowed edges, for hand-ruled straight lines.
- `circ(cx,cy,r,seed,k=16)` — wobbled circle.
- One module-level `W` constant scales ALL jitter and bow. ~0.36 is right; 1.0 is childish.

Per-icon SVG carries its own `<defs>` (unique filter ids) and `<style>` so files are
self-contained. Two filters: a slow large-wavelength displacement on the ink
(`baseFrequency 0.024 0.031`, `scale 2.8`) plus a faint high-frequency pass (`scale 0.9`)
for chalk edge; a softer one on the paper shape (`scale 5`).

Emit two directories: `icons/` (colour) and `icons-mono/` (accent omitted, same ink).

## Acceptance test

A gallery page that renders, in this order: the colour grid, the ink-only grid, then
strips at 32px on ivory, 32px ink-only, 32px inverted to ivory on slate, and 20px.
An icon is not done until it reads in all of them.

## Traps already hit — don't repeat these

- **High wobble amplitude is what reads as childish.** Fix it in `W`, not by redrawing.
- **A subject needing fine internal structure gets SWAPPED, not thinned.** A golf driver
  is a small oval on a stick at 32px and reads as a ladle. It became a flag pin.
- **Accents hide if centred.** They must offset far enough to be visible past the ink.
- **Food subjects drift toward "bread roll."** Brisket needs a flat bottom, a bark line
  and slice cuts; dumpling needs pleats notching DOWN from the crown, not arcs on top.
