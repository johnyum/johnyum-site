# johnyum-site

A static personal site plus a set of self-contained design-concept prototypes,
deployed on Vercel. No build step and no framework: each concept is a single
hand-written `index.html` with inline CSS and JS. Keep it that way unless asked —
don't introduce bundlers, npm, or a component framework.

## Layout

| Path | What it is |
|---|---|
| `index.html` | The site itself |
| `homes/` | Eichler Hunt — Bay Area listings concept |
| `multi/`, `multi2/` | Multi-guest booking concepts (Cereal type, event icons) |
| `multical/` | **Build output — never hand-edit.** The Multi-Host Calendar web app, played live inside the phone on preso slide 13. See below. |
| `bento-widgets/` | Standalone widget experiments |
| `test/` | Scratch prototypes |
| `playful/`, `claude-icons/`, `icons/` | Icon systems — see below |
| `vercel.json` | Redirects, plus rewrites proxying `/trips/` to a separate deployment |

## `multical/` — the live calendar on slide 13

The one place in this repo with a build step, and it runs **outside** the repo.
The source is a React + TypeScript + Vite app that lives in its own project at
`~/Documents/multi-host-calendar-web` (intaken from `multi-host-calendar-web.zip`,
a 1:1 web replica of the native iOS host calendar). `multical/` is only its
output — **never hand-edit anything in it; the next build overwrites the lot.**

To take in a new build of the app:

```bash
cd ~/Documents/multi-host-calendar-web
npx vite build --base=/multical/ --outDir ~/Documents/johnyum-site/multical --emptyOutDir
```

`--base` is not optional: the app resolves its fixtures, icons and fonts off
`import.meta.env.BASE_URL`, and its `base.css` font URLs are root-absolute, so
without it everything 404s under `/multical/`.

Two things that project needs and this one does not: Node (there is none on the
Mac's PATH — `export PATH="$HOME/.local/node/bin:$PATH"`), and an Airbnb-internal
npm registry for its `@irbnb/kyber-*` packages, whose auth token in `.npmrc`
expires hourly. Neither matters once the build is in here: the output is plain
static files. The only thing that needs the internal proxy at runtime is
free-text Ask, which falls back gracefully.

Slide 13 iframes it and steps it through a Keynote-style build — see the notes in
that file for the 430pt scaling, the clicker relay and how a beat is written.

**The app source carries one line for this deck**, in `src/App.tsx`:

```js
(window as any).__model = model;
```

That is what lets a beat call the app's own model instead of faking taps at
coordinates. It is not in the upstream zip, so **re-apply it after taking in a
new build** — otherwise slide 13 loads, looks right, and silently refuses to
step (`apply()` returns false and the deck walks off the slide instead).

## Drawing in Claude's visual language

**If you are asked for an icon, illustration, spot art or any drawing for a Claude
or Anthropic surface, the `claude-illustration` skill covers it — it triggers on
its own.** What follows is the short version.

Everything in this language is **generated from Python, never hand-authored.**
The shared drawing helpers are in `claude-icons/draw.py`; that file *is* the
language. Two tiers:

- **Icons** — `claude-icons/build.py` → `icons/` (colour) + `icons-mono/` (ink only).
  11 contour / 8.5 detail on a 256 grid. Concrete objects. Must survive 32px.
- **Illustrations** — `claude-icons/illustrations.py` → `illustrations/`.
  7.5 contour / 5.5 detail. Humanistic motifs — hands, profiles, knots, botanicals.
  Read large, composed rather than contained.

```bash
python3 claude-icons/build.py          # icons
python3 claude-icons/illustrations.py  # illustrations
```

Each script rewrites its whole output directory and gallery together.
**Never hand-edit files in `icons/`, `icons-mono/` or `illustrations/`** — they are
build output and the next run overwrites them. Full spec in `claude-icons/BRIEF.md`.

## Icon systems — read before making or using any icon

Three sets exist. They are **different visual systems and must never be mixed on
one surface.** If a surface needs an icon that doesn't exist, draw it in the set
that surface already uses. Never borrow across sets.

### 1. `claude-icons/` — Anthropic's visual language

Use this for anything meant to feel like Claude or Anthropic.

| File | What it is |
|---|---|
| `draw.py` | Shared drawing helpers. The language itself. |
| `build.py` | Icon generator → `icons/`, `icons-mono/`, `index.html` |
| `illustrations.py` | Illustration generator → `illustrations/` |
| `BRIEF.md` | Full spec: palette, grammar, traps already hit |
| `icons/` | Colour cut — feature and marketing moments |
| `icons-mono/` | Ink-only cut — dense UI, lists, toolbars, print |
| `illustrations/` | Spot art — blog cards, empty states, headers |

To add or change something: read `BRIEF.md`, add a draw function and a list entry
in the relevant script, then run it. Compose from the `draw.py` helpers rather
than raw path strings — raw `d=` data gets the noise filter but **not** the
geometry wobble, which is where most of the hand lives.

Non-negotiables:

- 11 units contour / 8.5 interior detail on a 256 grid. Round caps. No taper.
- Wobble lives in the **geometry** — jittered anchors, bowed edges — scaled by the
  global `W` constant (~0.36), with only a light noise filter on top. Raising `W`
  is what makes the set look childish; filter-only roughening looks like a
  distressed vector rather than a drawn line.
- One flat accent per icon, offset −8/+8 behind the line, never filling it.
- No shadows, no gradients, no second outline. That is what separates this from
  the `playful` set.
- Every icon must read with its accent removed. Colour never carries meaning.
- Built for 32px. A subject needing fine internal detail gets **swapped, not
  thinned** — a golf driver reads as a ladle at icon size, so it became a flag.
- Not done until it reads at 32px colour, 32px mono, and inverted on slate.
  Open `claude-icons/index.html` to check all three.
- Abstract motifs make weak icons and strong illustrations. A drawing that fails
  at 32px is usually in the wrong tier, not badly drawn.

Icon subjects are drawn from the app lineup in `playful/icons/`. Illustration
motifs are humanistic and literary, not technological — reach for a hand before
you reach for a gear.

### 2. `playful/` — clay/textural set

90 **hand-authored** SVGs on a 256 grid plus a gallery. Filled colour shapes with
an offset shadow. Edit the SVG files directly; there is no generator here, and
that's fine — the two sets are deliberately built differently, because
reproducible wobble is the whole point of `claude-icons` and isn't a concern here.

### 3. `icons/` — legacy

An older Trips catalog page. Don't extend it.

## Typography

Anthropic Sans / Serif / Mono are proprietary and self-hosted on anthropic.com —
**don't pull the woff2 files into this repo.** `claude-icons/index.html` declares
them and falls back to Georgia. Schibsted Grotesk + Newsreader are reasonable
free substitutes if a page needs to actually look like the system it documents.

Anthropic's earlier (2023) identity by Geist paired Styrene (Commercial Type)
with Tiempos (Klim); the current site no longer uses those.

## Palette

`claude-icons` uses Anthropic's live swatch values, read from anthropic.com CSS
variables — keep these exact:

```
slate   #141413    ivory-light #faf9f5   ivory-med #f0eee6   ivory-dark #e8e6dc
clay    #d97757    accent      #c6613f   kraft     #d4a27f   manilla    #ebdbbc
oat     #e3dacc    olive       #788c5d   cactus    #bcd1ca   fig        #c46686
heather #cbcadb    cloud-med   #b0aea5
```
