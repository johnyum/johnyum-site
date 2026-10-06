# johnyum-site

A static personal site plus a set of self-contained design-concept prototypes,
deployed on Vercel. No build step and no framework: each concept is a single
hand-written `index.html` with inline CSS and JS. Keep it that way unless asked —
don't introduce bundlers, npm, or a component framework.

## Layout

| Path | What it is |
|---|---|
| `index.html` | The site itself — see below |
| `Website_Images/` | The ten iPhone screens on the portfolio stage. Figma exports, 450x920 |
| `homes/` | Eichler Hunt — Bay Area listings concept |
| `multi/`, `multi2/` | Multi-guest booking concepts (Cereal type, event icons) |
| `explore/` | Explore map drill-in — see below |
| `multical/` | **Build output — never hand-edit.** The Multi-Host Calendar web app, played live inside the phone on preso slide 13. See below. |
| `recurrence/` | **Build output — never hand-edit.** The same calendar with the Repeat (recurrence) flow, from its own project. See below. |
| `api/claude.js` | **The deck's Claude** (2026-10-05): a Vercel Edge function holding `ANTHROPIC_API_KEY`, guarded by shape as the Trip Creator's functions are — see `peek/` below |
| `plush/` | johnyum.com/plush — ask for a synopsis of *Twenty Thousand Leagues* and a plush giant squid comes up behind the chat box and hugs it as Claude writes. See below |
| `rig/` | johnyum.com/rig — Rig Studio: reshape a rigged, animated character (proportions + sculpt) and send it to Peek. See below |
| `peek/` | johnyum.com/peek — a 3D furry character living in a chat UI, built from a Monsters character. See below |
| `monsters/` | johnyum.com/monsters — sketch → rigged, animated 3D character (Meshy), with `api/monsters.py`. See below |
| `bento-widgets/` | Standalone widget experiments |
| `test/` | Scratch prototypes |
| `playful/`, `claude-icons/`, `icons/` | Icon systems — see below |
| `vercel.json` | Redirects, plus rewrites proxying `/trips/` to a separate deployment |

## `index.html` — what the knock opens onto

johnyum.com goes **straight to the portfolio stage** — there is no password.
John's name and bio on the left, three columns of work on the right that animate
in on load. Built to Figma frame `5445:843924` in the *Yum Portfolio* file.

Four things sit behind flags, all switched OFF, all intact — nothing was
deleted to make room for the stage:

| Flag | Where | What it brings back |
|---|---|---|
| `GATE_ENABLED` | `<head>` | the password curtain (`KnockKnock`; spaces stripped, so "Knock Knock" also lands) |
| `FILM_ENABLED` | `<head>` | the play button and the portfolio film |
| `PILE_ENABLED` | the Matter.js block | the falling-work pile (retired 2026-08-30) |
| `WORK_ENABLED` | `<head>` | the three columns of work beside the words (off 2026-10-04: the page is the info alone, at every width, and the screens aren't fetched) |

The first two are declared in the `<head>` rather than beside their code for one
reason: `GATE_ENABLED` puts `nogate` on `<html>`, and that has to land **before
the first paint** or the password line and the wordmark bar flash up for a frame
on a site that no longer has a password.

With the gate off, nothing learns a second way in — the page fires the same
`unlocked` event the password would have fired, on `DOMContentLoaded`, and the
one path runs.

The stage's geometry is the frame's, not invented: a flat **120px gutter**, an
854-wide text column, and three 180-wide columns of work ending 120 from the
right edge. The gaps are **28 between the columns and 24 down each one** — half
the frame's own 56/48, tightened on purpose. All of these are flat; only the
phone width scales with the viewport. `space-between` reproduces the frame's own
174 between the words and the work, so that number is never typed in. All three
columns are centred on the same middle line — the taller middle column just
bleeds further off the top and bottom, and that overflow is the design.

Under 1100px **the work comes off** and the page is the words alone, centred:
the name, the bio, the teams, then the contact on two lines — the standing offer
on its own, the email and phone side by side beneath it. The screens are not
merely hidden; the script never fetches them below that width, so a phone
downloads **none** of the 2.3MB. Widen past it and they load then.

The narrow type is set small and quiet — the name carries the page at 30, the
blurb sits at 14 and the teams and contact a step under it at 11, so they never
outrank the thing they qualify. The block **snaps back to centre** above 420px
tall, where the words fit outright and a snap can only return a rubber-band
drag; below that they genuinely have to scroll and any snap fights the reader
for the last line, so there is none.

The rag on narrow is deliberate, because centred text shows a bad break far more
plainly than ragged-right does. The short blocks take `text-wrap: balance` and
the bio `pretty`; and every interpunct in the teams list is bound to the word
before it with `&nbsp;`, so a line can only break *after* a separator — lines
end with `·` and never start with one.

The ten PNGs load as soon as the page does, and the film is `preload="none"` —
it is never fetched for a stage nobody is going to see. (With `GATE_ENABLED`
on, the PNGs instead wait for the first keystroke, so a visitor who never types
never pays for them.)

Type is **Anton** (the name) and **IBM Plex Sans** (everything else), both
open-licence, off Google Fonts. Not to be confused with the Anthropic faces
below, which must never be vendored here.

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

### Recurrence, merged in as an add-on (2026-10-01)

The Repeat flow is now IN the `multical/` app too, added on without changing what was there: `src/data/repeat.ts` puts the
recurrence model onto `Model.prototype` (model.ts untouched; the price / promo / min / availability setters are wrapped to
keep the books, and for the host — every write the deck makes — they behave exactly as before), and `src/ui/recur/` holds
the new quick actions + Repeat flow in their own **shadow root**, so their styles and the app's never meet. `Root.tsx` shows
them only while `model.recurQA` is on (`setRecurQA(true)` from a beat); off, the app is exactly as it was. Checked against
a recorded fingerprint of all 35 steps of the bland run (12bs) before and after: identical. The pre-merge project is kept
at `~/Documents/multi-host-calendar-web-backup-2026-10-01`. The date cells follow an open Repeat draft live (price and its
±%, min N, closed, the rule's colour ring + 10% fill) and keep a saved rule's colour; a value set by hand on a night is never
overridden. With no draft and no rule, the cells are exactly as before — the 35-step fingerprint still matches.

**What slide 13's Repeat beats lean on (2026-10-02)** — all in the app source, none in the upstream zip:
`window.__repeat` (Repeat.tsx: the flow's step, cadence, values, colour and save, as `__model` is the app's);
`src/data/presoStays.ts` (`model.addStay` — the October guest, request-to-book and "Cancelled by you" pills, shown even
when the bland run's stays layer is off, cleared by `clearAll`); `recurEpoch` (bumped by `clearAll`, keys the recurrence
layer so every replay remounts the Repeat flow fresh); the jump arrow's Repeat mode in Single.tsx (white, down to next
year's run, back up to the first); and no dates pill beside the ⨉ in RecurQA. The pre-change source is kept at
`~/Documents/multi-host-calendar-web-src-backup-2026-10-02`.

## `recurrence/` — the calendar with the Repeat flow

Build output, like `multical/`, from its own project at `~/Documents/multi-host-calendar-recurrence` — a copy of
`multi-host-calendar-web` with `recurrence-single.zip` (from `multi-host-calendar-native` @ f3f8ca0) laid over it.
`multical/` and its project were left exactly as they were: the intake's model has none of the preso hooks the deck's
slide 13 drives, so it lives beside it, not in it.

```bash
cd ~/Documents/multi-host-calendar-recurrence
npx vite build --base=/recurrence/ --outDir ~/Documents/johnyum-site/recurrence --emptyOutDir
```

Cereal comes from the copy `multical/` already serves (`base.css` points at `/multical/fonts/`); the project's own
font files sit outside `public/`, in `handoff/cereal-not-published/`, so a build never ships a second copy (and
`recurrence/fonts/` is gitignored besides).

What the intake needed to run, all outside the zip's own files: `src/data/compat.ts` (puts back the ~30 model members
this project's other screens read — `layers`, the wand and tips sheets, the stay sheet, list/year/day — with the old
model's own definitions), `src/base.ts` (the `BASE` the native files import), `DayCell` / `CellData` exported from
`Single.tsx` again (the cell sampler imports them), `fixtures/scripts.json` (the native name for `dialog.json`), and
`icons/ev-pride-rainbow.png` (the rainbow from `preso/slides/assets/pride.png`). The zip as delivered is kept in that
project's `handoff/recurrence-single-original/`. The quick actions (and so the Repeat flow) appear with `?preso=1`.

## `explore/` — the map drill-in

A self-contained Mapbox concept, built to three Figma frames in the *Yum Portfolio*
file (`5480:1004947` continent, `5480:1004952` city, `2337:45802` neighbourhood).
Own build, own folder, one hand-written `index.html` — **it shares no code with
`/trips/`**, which is a separate deployment this repo only proxies. What it took
from Trips is the recipe, not the source: Mapbox GL 3.13, the Standard basemap
configured day + `faded` with every POI/landmark/transit label off, and the same
public `pk.*` token (a public token ships to the browser by design — restrict it
by URL in the Mapbox account, and see `~/Documents/Trips/config.js` for the last
rotation and what a dead token looks like).

Three beats, and one move between any two of them:

| Beat | Camera | Card | What is on the map |
|---|---|---|---|
| `usa` | z3.42 over the continent | 380×504 | 11 priced city pills, 14 bare pins, the traveller's own pin on SF |
| `nyc` | z10.05 over New York | 380×576 | 6 borough pills (Brooklyn is the way down), 3 blue airport cards |
| `hood` | z13.75 over Williamsburg | 716×822 | 23 price pills, the neighbourhood masked in |

`go(next)` runs all three at once — the field of markers clears, the camera
flies, the card morphs — and the card starts **180ms after** the camera, so the
eye is already travelling when the panel changes under it. Start them together
and it reads as two cuts. Going deeper, the marker you aimed at is the last to
let go; coming back out, everything leaves together.

Things that were learned the hard way and should not be undone:

- **A named marker is one piece.** The red head sits ON the pill, in the inset
  the pill's own left padding leaves for it, with only the stem carrying on out
  the bottom — so the pin markup comes *after* the pill and carries a `z-index`,
  or the white lands over the red and the pin reads as a separate dot beside the
  label. Unnamed pins stand alone; that is the only case where one floats free.
- **An unnamed pin is its own smaller component**, not the named one with the
  label taken off: a 10 head on a 1px stem, 15 tall, centred in a 28×36 box
  (frame `5474:537243`), with nothing in the head — a 6px plane inside a 10px
  circle is a smudge, not a plane. And named markers outrank unnamed ones in `z-index`,
  so a stray pin can never come down on top of the LaGuardia card.
- **The traveller's pin is a disc with a point, not a disc with a diamond.** Its
  tail is drawn BEFORE the disc and tucked to y 28.7, where the circle is still
  wider than the square — sit it lower or draw it later and both side corners
  of the rotated square show.
- **`p { margin: 0 }`** — the browser's 1em default is what pushed the two lines
  of the city title 26px apart; they sit 2 apart.
- **`.mk { position: absolute }`.** This stylesheet loads after `mapbox-gl.css`
  and `.mk` has the same specificity as `.mapboxgl-marker`, so `relative` here
  silently wins and every marker drops back into document flow — pins stack down
  the page and drift further from their coordinate the further down the list.
- **Markers are revealed immediately, not on `load` or `style.load`.** They are
  DOM over the canvas and need neither. The Standard style's imports can leave
  both events late or unfired, and the card then sits over an empty map. Only the
  Williamsburg mask needs the style, and it retries until the style takes it.
- **`projection: 'mercator'`** — Standard defaults to the globe, and a curved
  limb behind the pins is a different drawing.
- **The camera is padded, not re-centred.** The card eats the left column, so
  `PAD()` carries it (428 wide, 764 on the neighbourhood beat).
- **The Williamsburg outline is real data**, not a sketch: the union of the
  Williamsburg (BK0102) and South Williamsburg (BK0103) Neighborhood Tabulation
  Areas from NYC Open Data, simplified to 3e-6 degrees (about a third of a
  screen pixel at z13.8). Hand-drawn chords read as wrong here because the
  streets and the shoreline are visible underneath them. The price pills are
  scattered inside that polygon — regenerate them if the boundary ever changes.
- **The Figma icon exports carry `preserveAspectRatio="none"`**, so putting one
  in a box of the wrong ratio silently stretches it: the 22.5×19.66 wishlist
  heart in a 24×24 box was 22% too tall. The like button is the Trips one,
  inline (the fill has to change when saved), and the star is sized to its own
  7.88×7.52.
- **The frames' pins are placed by hand in Figma, not projected**, so their
  positions are approximate. The composition is matched; the coordinates are real.
- `cam()` gives back one octave of zoom per halving of viewport width, so a phone
  sees the same ground rather than a sliver of it.

Hovering whichever marker is the way down draws the leg you would travel, the
way the Trips build draws one: a `[2,2]` dashed line in `#222` plus the frames'
own black `Traffic` chip (12 clock, 10/14 bold white). Two kinds of leg, drawn
differently because they are different:

- **The flight** (SF→New York on the continent) is a quadratic bezier. There is
  no road under it. A straight segment between two pins reads as a ruler; the
  bow is what makes it read as a journey, and at 0.24 of the leg's own length it
  climbs over the plains rather than skimming the pins it passes.
- **The drives** (all three airports→Brooklyn, in the city) come back from the
  **Mapbox Directions API** on the `driving-traffic` profile: the real road
  geometry, and the duration traffic is giving it right now. Guessing the shape
  is not an option on a map that is drawing the roads underneath. A bezier
  stand-in with a typical-traffic label paints instantly so the hover is never
  dead, and each leg is replaced the moment its road lands; answers are cached
  for the session, and a `hoverGen` counter stops a fetch painting after the
  hover that asked for it has ended.

Each chip rides the halfway point **by length**, not the middle of the point
list — a road route is densely sampled through turns and sparsely down a
straight. A beat change clears everything: a leg belongs to the beat that drew
it.

`?state=nyc` / `?state=hood` opens straight on a beat, and `window.__explore`
exposes `{ map, go, at }` the way `multical/` exposes its model — a deck can step
it without faking clicks.

## `monsters/` — sketch to 3D character (johnyum.com/monsters)

Draw something simple, or upload a picture of a drawing; get a textured, rigged, animated
3D character. One hand-written `index.html` (three.js 0.170 off jsDelivr) and, unusually for
this repo, **a server half** — still no npm, no build, stdlib Python only. Four Meshy tasks,
each handed the previous one's **task id**, never a URL: `image-to-image` (the sketch
restyled, as **three views** — `generate_multi_view`) → `multi-image-to-3d` (2k geometry, 4k PBR
textures, no remesh; A-pose only for a kit character with arms and legs)
→ `rigging` → `animations` (Idle 0, Wave 28, Dance 22, Jump 466, plus the rig's walk + run).

The page only ever talks to **`/api/monsters?p=…`**, and two things answer it:

| Where | What | Key from | Gate |
|---|---|---|---|
| johnyum.com | `api/monsters.py`, a Vercel Python function | Vercel env `MESHY_API_KEY` | `MONSTERS_PASSCODE` (env) — every call; `MONSTERS_DAILY_CAP` builds a day, only if set (unset: no limit — the passcode is the only guard) |
| the Mac | `monsters/serve.py` (`python3 monsters/serve.py`, port 5320) | `monsters/.env` (gitignored), or the page's key box | none |

`serve.py` imports the Meshy helpers from `api/monsters.py`, so there is one proxy, not two.

- **`api/monsters.py` beats the `/api/*` → Trips rewrite** because Vercel checks the
  filesystem before rewrites. Don't rename it to anything a Trips route might also want.
- **The cap is counted from Meshy's own task list** (last 100 `image-to-image` /
  `image-to-3d`, created in the past 24h), so it covers local builds too and needs no store.
- **Meshy's files send no CORS header, and a Vercel response stops at 4.5MB.** So hosted,
  a model comes through `p=asset` in 4MB `Range` slices, fetched in parallel and stitched
  back in the page (`bytes()`); images and the download link use Meshy's URL directly,
  which needs no CORS. Locally `serve.py` hands over the whole file from `monsters/.cache/`.
- **Meshy's links expire after a few days.** Locally the cache keeps a shelf monster
  opening for good; hosted there's no cache, so an old shelf entry stops loading.
- **Test on `monsters-mock` (port 5321), never 5320.** With a key saved, 5320 is live and
  every test spends real credits. `MONSTERS_MOCK=1` forces mock and refuses the key box;
  `MONSTERS_MOCK_RIGFAIL=1` fakes a rig failure.
- **Stop can't call back a running step.** Meshy answers a DELETE on a running task with
  409 and charges for it anyway; Stop only keeps the later, dearer steps from starting.
- **Rigging only takes bipeds.** A blob fails step 3 — it keeps the procedural layer
  (breath, turning to the pointer, a squash when tapped) that runs on top of every clip.
- **Blobs** is the second mode (Draw | Blobs): a **monster kit**, Monsters, Inc. in spirit. Pick
  one of eight organic **bodies** (Round, Gumdrop, Hunch, Bell, Peanut, Noodle, Slug, Mochi) and
  build on it with twelve **parts** (Eyes, Smile, Blush, Nose, Horn, Ear, Antenna, Arm, Leg,
  Tentacle, Lump, Spots). **Everything is pitched cute, cuddly and simple** — John's call after
  the first real build came back grotesque (wet realistic eyeballs, warts, teeth): eyes are glossy
  plush-toy beads, the mouth is a small smile, every finish is toy-like (Plush / Vinyl / Clay /
  Fuzzy — there is no photoreal one), and every prompt carries `CUTE`, which rules out veins,
  wrinkles, teeth and realistic eyeballs. Don't add parts or finishes that pull the other way. All signed distance fields, smooth-unioned and raymarched in one
  `ShaderMaterial`; each sub-shape melts by its own `k` × the Melt slider, so an eye stays crisp
  and an arm melts in. **A part stores a direction from the body's centre, not a position**: it
  sits where that direction meets the body (`anchor()`), pointing out along the normal — so
  swapping or stretching the body re-seats every part, and dragging a part slides it over the
  surface. A mirror twin is the reflection, anchored on its own. `prim()` exists twice, in JS
  (anchoring, picking) and GLSL — **change one, change both**. The default parts' `dir`s are
  where a face wants them (eye high-front, mouth below it, legs underneath).
- Two earlier versions were built and dropped on 2026-10-02, both in git history: **Evolve**
  (procedural "bug" creatures on a 3×3 breeding grid — John didn't want ready-made creatures) and
  plain geometric blobs (ball, cube, ring… — too abstract; he wanted friendly bodies to build on).
- `BODIES`, `PARTS`, `prim()` and anchoring live in **`monsters/kit.js`**, shared with `peek/`.
- `window.__monsters` exposes `{ play, still, clips, playing, setMode, addPart, setBody, select, shapes, selected }`,
  the way `explore/` does.

## `plush/` — the answer becomes the story (johnyum.com/plush)

One element done beautifully, John's direction after a plush cast felt too childish: as the canned
*Twenty Thousand Leagues* synopsis streams, a single arm tip creeps out from under the chat box at
"a mysterious sea creature", and at "giant squid" the squid rises from behind the box — eyes just
over its top edge — and hugs it: arms round both ends and tucked under, one draped over the top,
one waving. **The chat itself never changes** (white background, no card round the answer) — only
the squid arrives. Arms stay clear of the + and send buttons.

- **The body is a generated image** (OpenAI `gpt-image-1`, transparent background): a refined
  plush, embroidered eyes, muted coral/oxblood/cream felt — "15% less kid-like, still friendly".
  `peek/plush/squid-hug.webp`. The other plush in `peek/plush/` are from the first pass (a whole
  cast on a stage), kept but unused.
- **The arms are drawn live on canvas** in matching felt (shading passes, a grain pattern, a brass
  seam, cream suckers toward the tips) from points relative to the chat box's rect, so they follow
  the real box and breathe. `#back` sits between the conversation and the box, `#front` over it.
- **The tide pool** is the page's second ask: each creature the answer names drops in from the
  top as its plush (`peek/plush/*.webp`) and tumbles onto the chat box — Matter.js, the same
  recipe as the retired phone pile in `index.html` (sleeping on, two half-steps a frame, a speed
  cap, a soft tilt limit). The box is a static body kept where the box really is; grab one to fling
  it (a spring from the finger); a tap pops its name in a bubble. The chat stays default.
- The OpenAI key lives in `~/.zshrc` (`OPENAI_API_KEY`); its safety filter once refused a plain
  "Atlantis ruins" prompt — reword rather than retry.

## `peek/` — a character that lives in the interface (johnyum.com/peek)

**Status (2026-10-04): the character is retired — John: "the dead end design".** It's hidden behind
`CHARACTER` (on only with `?character` in the URL); everything below is kept, not deleted. What
the page does now, in the app (embed) and the demo, is **the tide pool**: when Claude's real
answer names a tide-pool creature (anemone, starfish, crab, nudibranch, urchin, sea cucumber,
sculpin, octopus, and — so a looser answer still has something to drop — mussels, barnacles, limpet,
periwinkle snail, chiton, shrimp, kelp/seaweed, sand dollar, sea sponge, jellyfish; `POOL`, matched as the text streams), its plush (`peek/plush/*.webp`) drops in
and piles onto the chat box with the plush page's physics; fling them, tap for a name; they clear
on the next send. Their rects are reported to the app so they take touches.
**The timer** (2026-10-04): ask about the Big Green Egg, barbecue, brisket, smoking or grilling and a
wind-up kitchen timer drops into the same pile — the cute one: a generated 3D render, pure white
with a steel bezel and its own red pointer (`plush/timer.webp`; `FACE` is where its face sits in the square
element). **The dial is simple** (`dialSVG()`): a clean white face, a ring of minute ticks (no numbers — "too much")
that turns under the pointer (what's under it is the time left, 0–60 min), a long raised white grip
across the middle that turns with the ring (a silver ball there "sucked"), no digital readout. **This is where John landed after a long detour (2026-10-03)** — cream faces,
LED screens, red light through metal, silver knobs, a black glass puck with seven-segment digits, a
titanium rim, Antonio digits — he called the end of it "a digital mess" and asked for the cute timer with a
simple dial back. Judge the whole object, not one detail at a time. **It comes set from the answer** (`firstCookTime()`): the first time in a sentence with a cooking cue
("smoke the brisket for 6 to 8 hours" → 6:00:00; ranges take the low end), else the first time anywhere;
it follows the answer until you wind it yourself (`T.user`). **Tap it** and it becomes a small column in
the middle of the screen: the timer as a 64×64 icon, the time under it at 80px `00:00:00` in Sofia Sans Condensed counting down
live (the column — icon, time, button — centred on the screen), and a 48×48 round button under that — black with a play, red with a pause, no shadow. You can still
twist the little icon to wind it (up to 12h). The backdrop is a light, well-blurred white (42% over a 22px blur) so the chat shows through; the
close X is the top nav's glass button (44px, white glass, its halo), bottom centre, 48px up, and a tap or a swipe down on the backdrop also closes it. Opening and closing are one time-based smootherstep
(~560ms open, ~480ms close); the time and button rise and fade in a beat behind the icon and leave first;
closing sets it back down exactly where it was in the pile, at rest — never tossed. **Physics is shared**: the timer has the creatures' exact
restitution/friction/air/density (`feel` in `poolDrop`), only a boxy outline. At zero it chimes (WebAudio, unlocked by the
tap) and shakes. Tap outside and it shrinks back into the pile, still counting. While it runs, the time left (`00:00:00`) rides in a bubble above it in the pile (`c.tb`). A running timer
survives the next send; leaving the chat clears it.
**The thermometer** (2026-10-03, **switched off 2026-10-04** — John: remove it; its `POOL` entry has `re: null`, give it
the timer's regex to bring it back): a classic analog dial meat thermometer (after a Taylor dial John
pointed at), rendered in the timer's style — steel bezel, blank white face, a probe out the bottom
(`plush/thermo.webp`; an orange instant-read came first and was swapped). Drawn on the face (`TFACE`,
`thermoLCD()`): ticks on a 100–220°F sweep, a red needle that springs to the answer's done temperature —
the highest one in a sentence about pulling/probing/reaching, ≤212 (`thermoRead()`; brisket → 203°) — and
that number small under the hub. Tapped, it grows like a creature and the app highlights every temperature
in the answer (`c.terms`; the app's highlighter uses lookaround word edges so "203°" matches).
**Parts of a machine** (2026-10-04): the same tap-to-highlight as the tide pool with a car engine's parts (piston,
spark plug, crankshaft, valve, camshaft, fuel injector; product renders like the timer). Pride and Prejudice's felt
figurines were removed 2026-10-05 (John: "get rid of it" — Jane caught Mary Jane in a Spider-Man answer).
**The useful things** (2026-10-03, after John: "the egg timer is legit something I want"): each drops in
when the answer calls for it, filled in from it, and does something when tapped (renders in the timer's
style: `plush/clipboard|groceries|calendar|pin.webp`; code under "the useful things", `toolsHear()`):
- **Checklist clipboard** — when you asked how to do something (`HOWTO` on your message, `lastAsk`) and the
  answer has 3+ numbered steps (`stepsOf()`): the steps are written on its paper (`PAPER`, ticks and a
  count); tapped, it opens like the timer into a checklist you tick off (remembered in localStorage).
- **Recipe card** — a how-to that's cooking (recipe/cook/bake/smoke/grill/oven… in your question or the
  answer's start) gets an old-school recipe card instead of the clipboard (`plush/recipe.webp`): the dish's
  name typed above its red rule (Haiku names it, `recipeTitle()`), the steps typed on its lines (Special Elite). Opened, it's the same simple checklist as the others (John
  rejected a cream card with big number tiles): one line of action per stage, and under it that stage's temp and
  time — Haiku boils the finished answer down to that (`recipeCore()`); until then `stageOf()` lifts them out.
- **The BBQ cookbook and the brisket pictures** (2026-10-04): barbecue (brisket, smoking, the Egg, ribs…) gets — only once the
  answer is done, already filled (John: "don't bring in the cookbook until you can actually fill it") — a made-up
  hardcover, *How to Brisket* (`plush/cookbook.webp`, charcoal bookcloth, cream title, ember grill mark, red ribbon) in place
  of the recipe card; it opens to the same checklist (`isRecipe()`). For a brisket each step has its picture
  (`peek/bbq/*.webp`, matched by `BBQ_PICS`): simple friendly 3D (Airbnb-icon-like, simpler, real but quiet texture, not plush) —
  **one brisket, exactly the same size and place in every picture**, with what's happening around it: base, trim, rub, smoke,
  fatdown (the same brisket flipped, fat cap on the grate), bark, wrap (creased paper, grease spots), probe, rest (a towel
  draped loose, steam lines), slice; the Egg its true deep green with the glaze's pebbled texture (a bright green was "way too vibrant"); plus the gear in the same style (egg, charcoal, paper, cooler, thermo). Made with
  gpt-image-1 *edits* of one base image (`input_fidelity: high`), then each scaled so its brisket matches the base and all
  cropped to one shared square — the model drifts the size by up to 25%, so the normalising step is not optional.
  **Opened, a recipe is one white page that scrolls whole** (`.tui.page`): 24 a side, page to page, two columns — the book
  (64, centred, 48 under the island — the game icon's spot; the flying book lands in the head's slot and hands over to the page's copy) over the
  title Claude gives it (`recipeCore`: what a cookbook would call it, e.g. "Big Green Egg Perfect Brisket", Source Serif 26),
  (no title or rule under it now — just the book, 48 to the steps; John asked for both and then took them out) then the steps, arriving one by one, each picture (56) beside its words, the rule under the words only.
  **Each step is one word** — Trim, Season, Light, Smoke, Wrap, Finish, Rest, Serve (John: "just one word if we can";
  "Trim it" came first; each name carries its number when the step has one — "Light · 250°", "Smoke · 250°" (the cooker's, carried), "Wrap · 165°", "Finish · 203°", "Rest · 2–4 hr", temperature first, `tagSteps()`) — with the specifics, temperatures and times in 13px grey under it. Names in the serif (Source Serif 4, 17), specifics in the sans (Schibsted 13) — after trying all-serif; a range and its unit never break (`keepTogether()`).
  Each step takes only the temperature that belongs to it: the cooker's (200–350) for Light, the stall's (150–185) for
  Wrap, done (190–215) for Finish; Rest is told by its time — Claude folds steps together ("wrap… back on until 203°F").
  Smoke shows how long to smoke before wrapping ("Smoke · 6 hr" — John: 250° there is wrong, it's the Egg's, on Light).
  Prepare (plate setter, filling the charcoal) is its own word, before Light. Their pictures: `bbq/prepare.webp` (the Egg
  open, plate setter and grate in) and `bbq/light.webp` (open, coals lit) — so the Egg is never the same picture twice.
  Claude writes both (`recipeCore`: a one-word name + detail under 11 words); until then `stepName()` / `stepDetail()` read them off
  the streamed step's whole line (`stepsOf(text, true)`), and the picture comes from the name first, then the detail.
  **The whole page scrolls, the book with it** (64, where the game's icon sits, the steps 32 under it) up under white
  fade-and-blur scrims top and bottom, after ChatGPT's header (`.tui.page::before/::after`) — no shrinking or pinning
  (John: "no more weird scale changes"; a 120-wide book was tried and reverted). Always 1px taller than the screen so
  even a short recipe can be pulled and springs back.
  A held 340 column (edge to edge read as a screen; the tighter page felt nicer). **It aims to fit on one screen** — John: what's
  useful is not scrolling the chat up and down to find the recipe again, so the page is a glance, not a scroll. **No
  step-by-step / cook-along mode** — John rejected it: "I don't work that way, I don't think many people do."
- **The cook stopwatch** (2026-10-05): a long cook is a stopwatch, not a countdown — the egg timer no longer drops for
  barbecue. A vintage stopwatch (`plush/stopwatch.webp`, after an estate Heuer John pointed at: chrome bow and crown,
  pusher, black bezel, white dial, 30-minute sub-dial) with live blued hands drawn over it (`watchSVG()`, `WATCH`). The
  cookbook's page has **Start smoke** beside the X (black, 48 tall, the pair centred 8 apart): it closes the book and the
  stopwatch drops into the pile, its bubble counting from 0:00 (`ticking()`); once going the button reads "Smoking ·
  3:12", ticking with the stopwatch, and opens it. Tapped, it's as simple as the egg timer: the count up and ONE 16px serif
  line (18px) of what to expect now (`cookNow()`): "Fat cap down, lid shut at 250°." / "Check back in 6 hours." (two lines); when a check comes due it
  chimes and shakes and says "Check the bark. Set, and 165° or higher? Wrap it." Under it two 14px words, not buttons:
  Pause (black; Resume when paused) · End the cook (red).
  The checks come from Claude (`recipeCore` → `checks`) or, until then, `cookChecks()` off the steps. The cook lives in
  localStorage (`peek-cook`) and comes back into the pile after a reload or a new chat; "End the cook" (tap twice) ends it.
  A step's own bold label names it ("**Smoke.** Unwrapped…" is Smoke, not Wrap); Smoke's picture is the brisket on the
  grate, Claude's "Setup" the lit Egg; Rest takes its hours, not the minutes it vents.
  The page can't chime while Peek is closed — real phone notifications for the checks would need the app.
  The recipe page's pull-down is plain: iOS's own bounce, and past 90 the page closes (no growing book — John: janky).
- **Shopping list** — an ingredient list (`groceriesOf()`, bullets under an Ingredients/shopping heading):
  a simple yellow legal pad (`plush/groceries.webp`; was a grocery bag, then a notepad with a pencil), the items written on its page
  (`SHOPPAPER`); tapped, the same checklist.
- **Desk calendar** — a day/time in your own message only (`parseWhen(lastAsk)`; the answer's times are steps, not events): shown on its page
  (weekday on the red band, month, day, time); tapped, `{type:'calendar'}` → the app's EventKitUI editor,
  filled in (no permission needed). Haiku names the event (`calTitle()`).
- **Map** — on `replied`, if places are in play (`PLACES`), Haiku lists the recommended places as JSON
  (`pinsFor()`) and ONE folded map drops in (`plush/map.webp`; a pin per place was "bad"); tapped, the simple
  list — name, area, an arrow — and a place tapped opens Maps (`{type:'open'}`).
The app's demos live in the chat's ⋯ menu, under a line after Delete (`PeekDemos` in ChatPanel.swift; the
numbered header buttons are gone): Tide pool, Brisket, Moby-Dick, Spider-Man (2026-10-05; Engine, Pride and
Prejudice, Sourdough, Lasagna, Dinner party, Coffee spots and the separate Tide pool game were removed — "pretty much solved").
**Moby-Dick** (2026-10-05, redone twice — the plush whale, then a five-layer cut-out plate, both retired; John: the layers
looked like paper cut-outs rubbing together, and the horizon line was unnecessary): when the answer first names the whale
(`WHALE_RE`), ONE wood engraving framing the chat box develops around it, filigree-light: the white whale's tail big at
the right, rising from behind the chat bar and running off the screen's edge; a whaleboat at the left, its sailors large
and flung into the air; open white space between them for the answer; an airy engraved sea at the box, wrapping its sides
and fizzling out below with its texture kept (gpt-image-1 edit of the filigree plate John liked; `peek/moby/print.webp`).
**The answer goes UNDER the art** (John): the water, the boat and crew and the tail each carry a white body under their
lines (the dense drawing, closed up; the water filled down from its surface), so scrolled text disappears behind them;
thin oars and spray stay ink on the page. The water's flat far edge dissolves in the open middle only (~36px). Placed
108% of the screen wide, a touch off the left (`PRINT`); the chat keeps 170 above the box (`PRINT.room`) so the last line
clears the crew. Tried and dropped, in order: the plush whale; a five-layer cut-out plate ("paper cut-outs rubbing
together", a needless horizon); a long low whale; a tail slap as a heavy black slab; a moving-water shimmer (seams); a
filigree sea with tiny tail and boat. Ink only, no paper (mapped to nothing *locally*, so no grey rectangle). Cut around
the box's rounded rect. It develops up out of the box like a print off the block, then holds still till the next send.
While the keyboard is up (the box has risen) it fades away and the chat stops keeping room for it — that space is for
reading while you write (John: "taking up too much space where it's valuable").
**Now in layers (2026-10-05):** John capped every piece at ~60% of the old tail's height above the water, turned the tail
toward the horizontal (keeping its size and detail rather than shrinking it) and the boat a little left, then asked for a
slow settle. The engraving is cut into `moby/sea.webp` (the water painted back by a gpt-image-1 masked edit where the tail
and hull were), `tail.webp`, `boat.webp`, `flyer.webp`, and `head.webp` (off: `showHead` — Moby Dick's head just breaking the surface beside the boat, facing it, eye up — John's sketch; generated with the tail as the style reference, the gaps between its lines filled white; a white sketchy whale was rejected: "destroyed the wood relief style"); `MOBY` holds each one's rest pose (tail −60° about its base and mirrored, so it leans right with the flukes opening right —
John turned it back from a left lean; a plain right turn laid the stem flat on the water — moved 150 left — far right, its flukes cut off by the screen's edge (John) — sunk 74; its spray fades out before the layer's edges so no splash is cut; boat group ×.85, −10°). `mobySettle()`: the tail rises into its lean, the boat rocks and eases still, the flyer
comes down, all slowing over ~7s, then the exact final picture holds. `print.webp` is kept, unused.
**Spider-Man** (2026-10-05): ask about Spider-Man (`SPIDEY_RE`) and the classic Spider-Man comes into the chat in 3D and
lives there — a Meshy-rigged model from John's Downloads (`spiderman-moves/`), the rig and twelve moves merged into one
file (`peek/spidey/spidey.glb`, 3.5MB: Idle, Jump, Hang, Run, Land, Backflip, Kick, WallFlip, Crawl, Climb, Roll, Walk —
each Meshy move ships as a whole GLB, so the merge copies only the animation data, re-pointed by bone name). His own
module and scene (`spScene`) on the old character's canvas and ortho camera (one unit, one pixel, y up). He bounds in
onto the box, webs up from just off the top edge and hangs upside down — and **just hangs till you do something; nothing
loops** (John: an endless run-around loop wasn't wanted). **He reacts to you**: send a follow-up and he jumps down onto the
chat box and watches the answer come in (`spToBox()`); when it's done he webs back up (landing on your bubble was tried
and dropped — `spToBubble()` is kept, unused). **Push him into a side** — let go against the screen's edge, or fling him
into it — and he takes it as a wall (`spGrabWall()`): climbs to the top, perches, spins the corner web, and stays. **Ask him things** (`spAsk()`,
`SP_ASK`): "swing" — across the screen on a web, letting go over the far side (sometimes in a backflip); "climb the
wall" — runs to an end, leaps onto the screen's own edge (flush, `wallX`) and climbs it facing the wall, his hands on the screen's edge (body 28 off it climbing, 14 perched — measured from his hand bones), perches and **spins a
web in that top corner** (an SVG drawn line by line, cut away round the app's ☰/⋯ buttons so they sit over it, while the status bar is see-through and the web shows behind it; kept till the chat changes), then swings; "backflip", "kick", "crawl", "roll", "run", "come down", "hang".
He stays with the chat (talking to him doesn't send him off); switching chats does. **Tap him** for a trick
(backflip / wall flip / kick on the box; a spin on his web hanging); **press and drag** and he dangles from your finger;
let go and he drops. **The Hang move is already upside down** (and starts upright, gripping the web — that early part is his swinging grip):
hanging, it's begun at 45% and held at 75%, the model offset to hang from his toes (`SP_TOE`); swinging, from his raised
hand (`SP_HAND`). Climb, Crawl and Roll carry him forward in the clip and snap back on the loop, so their travel is
taken out (`spInPlace()`) and he's moved at the clip's speed (`SP_SPEED`). He takes touches (his box is in the rects).
The hidden test tab throttles timers to 1s, so tests step him by hand (`__peek.spStep(dt, n)`).
**The insurance call** (2026-10-05, the first agent demo — "the phone call nobody wants to make"): the ⋯ menu's
Insurance call sends "Can you dispute this $340 charge with my insurance?…" and **the page writes the whole chat**: a
`scripted` demo hands its chat to the page (Store `scriptNext`/`pageScripted`; Claude is held back and the page's
`{type:'reply', text}` streams in as Claude's; 10s with no reply and Claude answers after all), and `{type:'draft'}`
fills the box. **The EOB "you sent" is a real PDF attachment in the app** (2026-10-05, John: not a picture that pops down, a normal
PDF drop-in): the demo's `attach` names `Larkspur_EOB_Sep2026.pdf`, bundled in the app (two US-letter pages, printed with
headless Chrome from the page's own statement — `eobHTML()`, lifted into a standalone HTML with its `INSF`/`LARK`/dates;
the first lift cut `INSF` short and every print came out blank), drawn as a card above the bubble (`AttachmentCard` in
Attachment.swift, `ChatMessage.attachment`) and opened in Quick Look. Nothing drops into the pile for it
(`plush/eob.webp` and `eobMini()` are kept, unused). Claude asks two real questions; the box holds the answer; sent, a
**red rotary phone with a white dial** (`plush/phone.webp` — John asked for exactly that; an all-red one and a white
push-button one came first) drops in with "Calling…" (its dots taking turns) above it, and doesn't open on its own;
tapped, it opens like the egg timer: "Calling…" then the call's clock, a waveform (no status line under the clock — John:
not needed; the wave is quiet and rides the words: each word said is a beat that swells it and eases away over a slow
drift, bars eased frame to frame — the fast shimmer was "way too fast"), the transcript as it's
said (phone menu, keypad, hold sped up and said so, then Denise), filling the screen down to a pair at the bottom — the
red round hang-up beside the tuck-away chevron (the `go` pairing, 8 apart; the hang-up was in the column and landed on
the chevron). Closed, it goes on in the pile with its status above it. "Listen in" (ringback, DTMF, hold music, speech
voices) is still in the code, its button gone. **Done, the call collapses into the small phone, a puff of smoke
(`poolPuff()`: nine soft grey clouds swelling out and thinning while the phone shrinks into them) takes the phone away,
and THEN the receipt drops in** (John, 2026-10-05); an ended phone never carries a time bubble. Hung up by you, no receipt. Hung up, a receipt drops in (`$340` struck, `$40`, the reference number); tapped, one white page: what they agreed and a
follow-up date whose Add opens the app's Calendar editor. All fictional: Larkspur Health, Mission Bay Dermatology,
Dr. Okafor, Denise, a 555 number; dates hang off today. The script lives in the page (`insReply`, `insScript`), so it
changes with a deploy; it names John and avoids pronouns for him. Code under "The call".
**Everything belongs to its chat** (2026-10-05, John: the tide pool and the timer were "sharing icons" across chats): the
app sends `event('chat', id)` when the open chat changes; the page clears the pile, the whale and Spider-Man then. A cook
remembers its chat (`cook.chat`) and its stopwatch only comes back there (`cookHere()`); a cook from before this, with no
chat, stays hidden until its cookbook's Smoking button adopts it. "Doctor Octopus" doesn't drop the octopus.
**Tap a creature** and it eases up to 2× — body and all (`poolSize()`, `Body.scale`), shoving the
others aside — and the page tells the app `{type:'highlight', terms}` (each `POOL` entry's `terms`): the
app marks every mention in the answers with a highlighter yellow (`PeekHighlight`, `MarkdownText.marked`)
and glides the chat to it, its subhead first (MessagesView). Tap again, or another, and it eases back.
**The phone's motion moves the pile** (2026-10-04): while there's a pile, the page asks the app for motion
(`{type:'motion', on}`); the app's CoreMotion gravity comes back as `peek.tilt(x, y)` (sets the world's
gravity — never under 0.25 g down) and a hard shake as `peek.shake()` (everything jumps).
**The tide pool game (2026-10-04):** ask for a game after (or about) the tide pool and an icon drops in — a little
fanned stack of felt picture cards (`plush/pail.webp`, the file name kept; a sand pail was "weird") — tap it and the
full-screen game opens: solid white, a clue a child can follow (`CLUES`, written in the page — instant), three
creatures in white rounded boxes, each name inside its box under the picture in serif (black ring when picked;
sticker outlines were tried and dropped), five rounds (no progress dots); good rag throughout — clues balanced, their last two words bound, "Who am I?" never split,
list rows `text-wrap: pretty`, Play again, the X to close. The pile flushes away (below).
John tried and rejected: the game opening on its own, and a clue card on the pile instead of the full screen.
After the Tide pool demo's answer the app fills the box with the game question, ready to send.
Tapping a creature shows its name above it — only the tapped one — while it's enlarged: a 40px white glass pill,
no pointer under it; on white it's held by a hairline ring and a two-layer soft shadow, never one dark drop (black
glass was tried). **The game question flushes the pile** (`poolFlush()`): each creature hops and drops through
everything into the chat box (a layer clipped at the box's top swallows it), one after another; then the cards
drop in from the top, straight down to the middle where the pile was. In the open game the icon sits up top, 48 under the Dynamic Island (`ISLAND`).
**The close X is the page's** (`.tclose`): 48 round, black with a white X 12 × 12, 48 up from the bottom of the screen,
in the app too. A native glass one (`PeekCloseButton`, asked for with `{type:'close', on}`) is still in the app but
the page no longer asks for it. The game's question and choices sit centred on the screen; only the icon is up top.
**The highlight (2026-10-04, John: make it consistent, like a real highlighter pass — snappy):** once an
answer is done the page asks Haiku for each dropped thing's own sentences (`askSpans()`, `spansFor`), and a tap
sends them with the terms; the app marks exactly those (`PeekHighlight.ranges`), falling back to the term rules.
In the app each paragraph is a `PeekPara`: the yellow is drawn behind the text and swept on left to right in
one 0.34s stroke across all its lines at once, once per tap, only once it's on screen (so a paragraph the chat
scrolls to still gets it); clearing fades. The old background-colour attribute animated only sometimes.
**Every body is its picture's outline** (`HULLS`, convex hulls traced from the webps) pushed out 2px
(`POOL_GAP`), so stacked pieces keep ≥4px apart and never overlap; the picture turns about the body's
centroid (`c.ox/oy`). **The app has demo buttons 1 2 3** top right of the chat (`PeekDemoButtons` in
ChatPanel.swift): each starts a fresh chat and sends a prompt — tide pool, brisket on the Egg, Moby-Dick.
The page also tells the app how tall the pile is (`{type:'inset'}`) so the chat makes room at its end —
only once the pile has come to rest and changed by 16px+: reporting it mid-bounce re-padded and scrolled
the chat every few frames, which is what made the text jitter as things dropped in.
The app reports only the composer's frame now (`.peekPlatform("composer")`): the per-message platforms the
retired character stood on were measured every frame while streaming and scrolling, and that churn —
preference updates up through the chat plus a JS call per frame — was the rest of the jitter. Don't put
`.peekPlatform` back on message rows.
**The chat's scrolling (2026-10-04, measured from a screen recording):** MessagesView stays at the end with
`.defaultScrollAnchor(.bottom, for: .sizeChanges)` — no `scrollTo` per streamed word. A scrollTo per word
plus an animated one when the pile's room changed fought frame by frame (the chat flipping ±30pt), and
jumping while the last paragraph was still being measured flashed the content 80–110pt for a frame. The
pile's room is the height of the end marker (`id("bottom")`), not padding after it; the app glides there
once when the room changes — never while streaming, never while a creature is highlighted. Each chat gets
its own scroll view (`.id(convo.id)`), or a new chat started from a long one sat off-screen, blank.
A tap on a creature is a real `pointerup` near where it went down (<8px, <320ms); a `pointercancel` (iOS
taking the swipe to scroll) used to count, and grew it. The page shows a debug readout when it's served
from localhost inside the app — point the simulator build at it with `SIMCTL_CHILD_PEEK_PAGE`.

A 3D character that runs around a chat UI the way a game character runs around a level:
it stands on message bubbles, runs along the chat box, jumps between suggestion pills, sits on
a reply while it "thinks", hangs from a pill and swings, peeks up from behind the input
gripping its edge, pops in from the right with gritted teeth when you swear at it, and holds
up tip cards. One `index.html`, three.js; the chat is canned.

- **One pixel, one unit.** A transparent full-window WebGL canvas with an orthographic camera
  (y flipped), so an element's `getBoundingClientRect().top` *is* a floor. Feet re-read their
  element's rect every frame, so scrolling and reflow carry the character along.
- **"Behind an element" is an occluder**: a depth-only plane over the element's rect, drawn
  first and closer to the camera. **Fur is shell texturing** — 16 offset copies of a mesh cut to
  strands by a 3D hash, dragged against the motion; it runs short (`uBald`) round the eyes,
  mouth and cheeks so a face stays a face. Jumps are ballistic, the hang is a real pendulum
  (a cursor swept past pushes it), squash, lean and ears are springs.
- **The character comes from Monsters.** Blobs mode's "Bring it into Peek" packs the kit
  character into the link (`/peek/#c=…`, `pack()`/`unpack()`), and Peek meshes it with three's
  `MarchingCubes` from the same distance functions. Parts get jobs: eyes blink/look/squint,
  the smile becomes the mood mouth, blush flushes, arms pump and hang, legs run (no legs: it
  hops), ears/antennae/tentacles spring; a character with no arms is lent small ones to hang
  and hold. No link: a default green gumdrop.
- **A drawn character comes too.** Draw mode's finished model gets a "Bring it into Peek" link
  (`#m=…`: the Meshy GLB, rigged one and moves). Peek loads it through `/api/monsters` (whole
  from `serve.py`, 4MB slices with the passcode on johnyum.com), plays its own clips — Idle,
  Run/Walk, Jump, Wave on a tap — and puts **the kit's live face on it**: it feels across the
  model's front for the face (`faceOnModel()`), sizes eyes and mouth to the head and attaches
  them to the head bone, so every mood works. That's why Draw mode's **"Blank face"** box is on
  by default: it asks Meshy for a featureless face, or the painted one shows under the live one.
  Face-finding takes the front-most point of the upper body — fine on a blank face, fooled by
  anything that sticks out further (goggles, a snout).
- **`monsters/kit.js` is shared by both pages** — bodies, parts, `prim()`, anchoring. The
  Monsters shader still has its own GLSL `prim()`: change one, change both.
- **It has a heart** (2026-10-03): every message — yours and Claude's — gets an instant on-device
  read (`sense()`, word lists) and then Haiku's (`read()`), asked through the host app: the page
  posts `{ type: 'ask', id, system, user }`, the app calls Haiku and answers on `peek.answer()`.
  **The prompt lives in the page**, so its feelings change with a deploy, not a rebuild. Twelve
  feelings (`FEELS`) each have a performance in `perform()`; a swear at the code is sympathy, at
  us it's hurt. Hurt builds and fades (`heart`): grumble, sting, then it sulks out of sight till
  you say sorry. While you type, its face follows the draft (`watching()`); the app sends the draft
  text and Claude's finished answer for this. Commands (jump, dance, wave, come, go away, sleep).
- **It has a home** (2026-10-03): tucked behind the right end of the chat box, head and paws over
  the edge (`homeward()`, `HOME` = .6 of it showing). Every move ends back there — `act()` sends it
  home once its queue runs dry — and a peek holds on to its element (`C.held`), so the keyboard
  rising carries it along. It leans up while you type, sinks while it sulks, and a tap pops it
  right out of the box (`popUp()`). The touch rect it reports stops at the box's top edge, so the
  Send button under it stays tappable.
- **Pick it up** (2026-10-03): drag it (`grab()`) and it hangs under your finger; let go (`drop()`)
  and it falls onto the first thing under it — any message, a pill — stands, then sits. Dropped on
  the box (or nowhere), it goes home. A grab interrupts whatever it was doing: `wait()` and
  `tween()` throw `STOP` once `epoch` moves on. Where you put it, it stays (`C.perched`) and reacts
  in place (`inPlace()`); a tap there stands it up or sits it down. The app reports every message as
  `msg-<uuid>` (the bubble, or the answer's text) for this.
- **It doesn't talk** (2026-10-03, John's call): Claude talks in the chat; the character only reacts,
  with its face and body. `say()` is off behind `TALKS = false`, and Haiku isn't asked for a line.
- **Made characters** (2026-10-04): `#p=paper` (a jointed cut-out — ivory pieces with a cut edge and
  a shadow, kraft pins, slit eyes) and `#p=line` (ink head and limbs over one flat clay body), in
  `peek/puppets.js`. One rig under both, every joint a spring — poses are only targets, so nothing
  snaps. Both are flat, so **every pose is designed in the picture plane** (elbows and knees fold
  sideways; a nod is the head sinking) — a pose that leans toward the camera reads as nothing.
  Joint positions go through `relTo()`, never the world matrix: at scale 0 it's singular, and one
  NaN poisons the paper rig's remembered limb angles. `?big` draws the character 3× to judge it.
  The app's builder has a "Made" tab that picks them.
- **Its job is the work** (2026-10-04, John's call after "what's the value?"): in the app it shows how
  Claude's reply is going, at a glance, from its spot behind the box — thinking (scratching its
  head), writing (low at the box, an arm lifting only as words land), stalled after 1.6s (still),
  then sure / unsure (a shrug) / asking (a hand up) / failed (sunk). Driven only by the real stream
  (`work*()` in index.html, poses in puppets.js `MOOD`) — never a loop, which is what makes Muse's
  Jolly feel canned. The app's send / stream / thinking / replied events all go to it; the older
  reply gestures, sitting on the reply and wandering off are no longer called in embed mode.
  John rejected the iOS Live Activity version: it belongs in the app, not the Dynamic Island.
- **The demo page is drawn like the Claude clone** (2026-10-04): Schibsted Grotesk + Source Serif 4,
  round header buttons, spark over a serif greeting, the clone's composer. Its canned replies stream
  word by word (a `‖` in one is a 2.6s stall) through the same `work*()` calls the app makes, and it
  opens on the paper figure. The sidebar, director buttons and pills are gone from view (the pills
  stay in the DOM, hidden, for old code paths); the away-life (`awake()`) and idle wandering are off.
- **On the demo page it lives in the thread, not over it** (2026-10-04): drawn at text size
  (`IN_SIZE`), it stands beside the greeting, then in Claude's reply — a strip reserved under the
  words (`.msg.bot.here`) — following the end of the text as it streams (`C.anchor`, read from a
  zero-width `.caret` after the words), and stays at the end of the answer. The canvas is clipped
  to the chat area (`clipToLog()`), so it scrolls under the header and the box. The app (embed)
  still uses the home spot behind the box.
- **Drop it anywhere and it goes home** (2026-10-04, John's spec): it falls onto the top of the chat
  box, runs along it to its spot on the right, hops down behind it there and pokes its head back up
  (`drop()`). Dropping onto messages (perching, carrying) is gone from this path. The default
  character is the original fluffy kit gumdrop again (the app keeps a Rig Studio save if there is
  one); the bone-posing layer for rigged critters (`poseRigged()`) is off — it pulled them out of shape.
- Its frame loop is `frame()`, exposed on `window.__peek` — a hidden tab pauses
  `requestAnimationFrame`, so a test drives frames by hand.

## `peek/?preso=1` — the 3D chat in the deck (2026-10-05/06)

Preso slide `12fg.html` (after the ego card) is `/peek/?preso=1` live inside the drawn phone every build uses (13.html's chrome)
with an iPhone 17 Pro Max's 440 x 956 inside it. **The phone (embed mode) never takes any of this** — every deck thing is behind
`PRESO` / `html.preso`. The page is its own host there (`presoHost`: inset, highlight, draft, reply, ask), and the app's native chat
is ported into it number for number from the Swift (ClaudeClone-peek: rows, composer, EdgeFade built as four blur layers,
IconGlassButton, ThinkingRow, the top-right capsule drawn to John's grab of the Claude app, SF Symbols rendered off the Mac into
`peek/sf/` at the app's sizes). The chat frame runs to the screen's top; the slide draws the status glyphs over it on a clear band.

**Scenes** (`SCENES`, `window.__demo.play(name, turn)`): tidepool (2 turns), insurance (2 — the page writes this chat itself,
`insReply`; the EOB is a PDF card above the bubble; the drafted answer is typed in), brisket (1), spiderman (3: in, climb the wall,
swing). A scene change taps the new-chat mark and clears to a fresh greeting (not the first). Each turn: the iOS keyboard
(`peek/sf/keyboard.png`, lifted from the Simulator; every key measured, each presses and pops its letter) rises, the words type
in, it sends; Thinking… stays until the first words; the answer streams from **Claude for real** through `/api/claude`
(Opus 5, the app's own system prompt held on the server; Haiku answers the page's six asks). `?live=0`, no function, or a failed
call → the scene's written answer plays. No map ever in the deck. **Physics is stepped by the clock, not the frame** (it ran 2x on
a 120 Hz Mac); in the deck gravity is a held phone (.8 g), the pointer over the phone is the tilt, S shakes.

**`api/claude.js`** takes only `{kind:'chat'}` whose first message is one of the deck's openers (`OPENERS`) and `{kind:'ask'}` whose
system prompt is one of the page's (`ASK`, lifted from the page's source when the file is written — a changed prompt means
re-lifting it, or a 403). Same site only, token caps. Env: `ANTHROPIC_API_KEY` (and `ANTHROPIC_WORKSPACE_ID` for an org key).
`GET /api/claude` reports readiness and the key's shape, never its contents. No passcode (John: guarded like Trips, nothing to type).

## `rig/` — Rig Studio (johnyum.com/rig)

Reshape a rigged, animated character without breaking it, then send it to Peek. Thirteen CC0
models by Quaternius (`rig/models/LICENSE.txt`): nine critters from the **Ultimate Monsters
Bundle** (Bunny — the default — Cat, Yeti, Pink Blob, Mushnub, Birb, Frog, Cactoro, Green
Blob; `.fbx`, loaded with three's FBXLoader) and four mechs from the **Animated Mech Pack**
(`.gltf`). Bunny and Frog have full skeletons (3-bone ears on the bunny) and Idle / Walk / Run /
Jump / Wave / Yes / No; the blobs have 4-bone rigs with Idle / Walk / Jump / Yes / No / Dance.

- **`rig/rig.js` is shared with `peek/`.** Proportions are bone scales applied *after* the
  animation each frame, each bone's factor divided out of its children (`shape()`); sliders show
  only for bones a model has (`hasProp`). Sculpt is offsets in the rest pose, per **weld group**
  (vertices at one position) so seams never tear; hard-edged indexed meshes (mechs) recompute
  facets, smooth non-indexed ones (critters) get welded smooth normals.
- **Fluff** is shell fur on the *skinned* mesh: 12 `SkinnedMesh` shells sharing geometry and
  skeleton, a ShaderMaterial with three's skinning chunks, strands from a hash of the rest
  position, kept short round the eyes. Only Main/Secondary paint grows fur.
- **Moods are the character's own eyes, never a pasted face** (John's call — he didn't want the
  Monsters kit face mixed onto these). `setEyes({ open, lookX, lookY, lift })` rewrites the
  Eye_White / Eye_Black vertices each frame: blink, pupils on the pointer, `MOODS` (wide,
  squint, crescents, half-shut). Body language comes from the clips: No for the ugh, Yes when
  pleased, Wave/Hello on a tap.
- **three.js strips the dots from bone names** (`UpperArm.L` → `UpperArmL`); FBX clip names come
  as `Armature|Walk` and are trimmed.
- `groundLift()` re-grounds from the feet in the rest pose when proportions change.
- A character is JSON (`{ v, model, prop, colors, fur, sculpt }`). **Save file** downloads it;
  Claude can read it from Downloads, change it, and write a version to load. **Bring it into
  Peek** gzips it into `/peek/#r=…`.

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
