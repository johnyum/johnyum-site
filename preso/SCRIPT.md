# The script

What John says over the deck — the voiceover, kept beside the slides rather than on them. Lines that come off a slide land
here so nothing is lost. Rough, and growing.

## Case Study 1 — Transportation
The card: "Case Study 1 · Transportation: Designing the dream Airbnb cancelled." (was "having a dream and getting it crushed") Then the Forbes piece, the spoiler card ("Spoiler alert. The “experiment” was selling plane tickets." — the headline's own word), the flight search, the
other-thing card ("Secretly, I built what my vision was for transportation:"), then the trip creator (trains, flights, New York, Williamsburg). Airbnb was publicly building transportation in 2019; the bet
was real, and it was cancelled — then the closing card ("It went all the way to Brian. He loved it. / Then COVID.").

### The other thing (09bz — before the trip creator)

The beats behind the card, to say (John, 2026-10-06):

1. I wasn't satisfied learning how to sell plane tickets. I did it anyway — learnt the flight APIs, made the designs.
2. But I had something else in mind. In my free time I started building a way to make transportation fit Airbnb's ethos:
   travel anywhere, to unique places, to adventurous places.
3. Transportation as a gateway to cool and interesting places — walking, riding, or a train. That's the trip creator.
4. I built a prototype in Principle, painstakingly, and grassrooted it — because I thought it was such a huge miss that we
   were just selling tickets. The prototype proved the concept.
5. Eventually I got leadership involved, and it went all the way to Brian Chesky. He was super excited. We finally had
   something that was viable, and actually unique in this space.
6. This was 2019 — the Forbes piece is February 2019. Then COVID killed all of it. (The what-crushed-it beat; the card
   after the trip creator, 09cz, says it.)

## Case Study 2 — Host only fee

### Why the host-only fee (09d01)

The slide is one sentence: **We had to tell 5 million hosts: "You pay the guests' fees now."** (earlier cuts: "…they'd now pay the guests' fees too." / "…that they will now pay for both their AND the guest fees." / "…that they are going to pay all service fees going forward.") The beats behind it, to say:

1. Guests hated the sticker shock of fees at checkout.
2. To fix it, we had to move all service fees to be paid by the host. All 5+ million.
3. We built a tool to auto-raise prices so host earnings don't change.
4. The math was very difficult to explain:
   - Split fee — guest pays $100 + $14 = $114; host earns $100 − $3 = $97.
   - Host-only fee — guest pays $115 = $115; host earns $115 − $17.83 = $97.17.
5. We had to get ahead of the backlash.

### What it taught (09dl — the lessons slide)

The slide is one line now — **"Be honest and own it because your users can smell BS."** — and these are the beats behind it, to say:

1. **Make the call. Own it.**  *(the long form: In a no-win scenario, make the call and own it.)*
   One price fixed it for guests, and moved the cost to hosts. The work was making that trade honestly, not pretending it
   wasn't one.

2. **Hosts can smell BS.**  *(the long form: People forgive bad news. They don't forgive feeling tricked.)*
   Every version we tested that buried the change to soften the blow drew more backlash, not less.

3. **Don't just explain. Give a fix.**  *(the long form: Give solutions, not just an explanation.)*
   Tone and delivery only go so far. Giving hosts a tool to raise their prices and keep their earnings, in one tap, is what
   let them act on it.

## Case Study 3 — Host calendar

### Why the calendar (12a)

The slide is one sentence: **Calendar is where Airbnb hosts run their business, selling nights.** (John, 2026-10-03.) The beats it carried, to say:

1. Calendar is where Airbnb hosts run their business.
2. Each night is inventory for sale, with its own price and rules — Price · Weekend price · Smart Pricing · Cleaning fee ·
   Pet fee · Extra guest fee · Other fees · Discounts · Availability · Min / max nights · Advance notice · Prep time ·
   Booking window · Check-in / checkout days · Cancellation · Repeat rules · Events and holidays · Gap nights.
3. The old calendar was too simple for the tooling hosts needed. *(Its three screens — month, edit, details — are in
   `slides/assets/old-calendar/`.)*
4. So we rebuilt from scratch.

### The verdict (12bs — the two ✓ and the ⨉s)

> Testing told us two things. Hosts found it easy to use — but it was missing what they need every day. So here's how I
> answered each one.

Then one short line as each ⨉ is crossed out. *(To write: a line per ⨉.)*

### What it taught (12dl — the lesson, after the library of components)

The slide is one line: **"Users can handle complexity when it's built the way they think."** (John, 2026-10-04.) The
thread of the case study is trust — clarity and transparency at every step. The beats behind it, to say:

1. The calendar didn't get simpler. It got much more powerful, and hosts still found it easy.
2. That's because it was built from listening: their needs, given back in a system that makes sense to them.
3. I'm a host too. I know how hosts think about their nights, and we built it around that.

## Multi calendar — Now scale it 100x

The bones, from the 2026-10-06 critique John kept. The AI story is threaded through this case, not kept for a chapter of its
own: the multi calendar's V1 shipped in the same four months John was learning AI.

1. **THE NUMBER is its own card now (12ds, after the board of forked builds): "Single Cal took a year to ship. Multi Cal took
   3.5 months."** Say it once, as written, and let it sit. Before the $0→$200 roll it needn't be said again. Then: "And I did this one differently. I built it with Claude —
   the live calendar you're looking at is that build." The room watches an AI-built prototype without being told it's a demo of AI.
   If asked about the year: it's where the system came from — the multi calendar was fast because the single one had settled the
   hard questions. Be exact about the four months: prototype to shipped V1, the prototype as the spec, the team building from it.
2. The $0→$200, the 7, the 3: the same system at 100x. What hosts said (the checks first, then the ✕s): real feedback from
   last week on a shipped V1.
3. **The design-system sheet (12d1)** is the proof of the method, not just a library: one system, built fast, and it didn't
   get sloppy. The host quotes are right behind it for anyone wondering whether fast meant worse.
4. Only the unassailable claim about the ship: if engineers built V1 from the prototype, say so — "my prototype was the spec;
   the team shipped V1 in four months." The deck is grounded everywhere else; one overstated line is what gets remembered.

## Process — three cards, after the multi calendar's lesson

What John said it's for (2026-10-06): how he used to design, and how he designs now.

1. **Process** (12dp) — the card. One word, then the two pictures.
2. **The Figma** (12dq) — the Yum page of the Multi Calendar file, a grid of frames. *This is how I used to work: flats in
   Figma, a clicking prototype on top, one screen at a time.*
   **The side studies** (12dq1) — the studies built on the side of the calendar, live, one to a tap: cell animations, the
   graph five ways, the cell system, the tip cards, the chat-to-dates motion, the Repeat review and mock. *And all the way
   through I'm building side studies — different models, graphs, the deck, iterations of the quick actions — to look at a
   question rather than argue it.*
3. **The web calendar, then the board** (12dr) — the live build, then one tap and every iteration tiles round it. *Now I design
   the whole flow, end to end, as a working thing. Then I hand it to the whole team and ask them to fork it and run with it.*
   Over the board: *The work is enormous. There are so many edge cases that all of us had to kill our egos. I run ahead — I set
   the pace, the parameters, the foundation — and then we come together and work the solutions out as a team.*

The beat to land: the board is not a gallery, it's the evidence of the method — the number of iterations is what "fork it and
run with it" produces. Keep "kill our egos" in; it pairs with the ego card later.

## A.I. — built with Claude

The A.I. card and "built with Claude" are a reveal: not just that the deck was made with Claude, but the product too. Peek is
"what I did when nobody was asking me to" — the trip app, the monsters, the hundred throwaways. Keep the section the same shape
as the three cases: a why, the live thing, a lesson. Candidate lessons, in John's own words: "Make it do something useful, not
just something" / "A glance, not a flow." The trash heap is sincere, not a gag — the retired cast, the thermometer, the digital
timer detour, the character: most of what you can build with this, you shouldn't. A count, then a beat of silence.

### The 3D chat (12fg) — the five scenes, in the order they play

The phone is live: the real app's chat, Claude answering for real (Opus 5), the keyboard typing each question in. One scene
per idea; a new chat between them (the new-chat mark is tapped, the greeting comes fresh). What to say over each, roughly:

1. **Tide pool** (2 taps). "My daughter is learning about tide pools…" — as Claude names each creature it drops into the chat
   as a plush and piles on the box. Tilt the Mac and the pile shifts; tap one and its sentences highlight. Second tap: "Create a
   little game for her" — the creatures hop into the box, the cards drop in, the game opens. The point: the answer became a
   thing she can hold, not a wall of text.
2. **The insurance call** (2 taps, then a third to rush). "The phone call nobody wants to make." The EOB goes in as a PDF;
   Claude reads it and asks two real questions; the answer is typed in; a red rotary phone drops in and the call runs — the
   menu, the keypad, the hold (sped up and said so), then Denise. Tap again and the call speeds to its end: it hangs up, the
   phone goes in a puff of smoke, and the receipt drops in. $340 struck, $40, a reference number. The agent did the work; the
   chat just shows it.
3. **Brisket** (4 taps). "Give me the best recipe for Texas style brisket on the Big Green Egg." The answer streams; when it's
   done a cookbook drops in, already filled — one page, one word a step, a picture each. Second tap: the book opens. Third: Start smoke, the book goes back and the
   stopwatch drops in. Fourth: it opens — the cook is running. The tap after closes it and moves on. "A
   glance, not a flow": the useful thing is not scrolling the chat up and down looking for step four.
4. **Moby-Dick** (2 taps). "Tell me the story of Moby Dick." The moment the whale is named, a wood engraving develops round the
   chat box — the sea, the tail, the boat and its crew flung into the air — and settles over seven seconds. Second tap: "Who are the main characters?" — the keyboard
   comes up over the plate, the answer streams, the plate stays, and three engraved portraits hang under it —
   Ishmael, Ahab, the whale's flukes. Tap one: it grows, its name comes up, and every sentence about it goes yellow. The answer goes under the art. The quiet one: the interface can be a picture of what you're reading.
5. **Spider-Man** (1 tap). "Tell me all you know about Spider-Man." — he bounds in, webs up, and hangs there till you do
   something. Then it's the mouse: drag him and he dangles; fling him into a side and he takes it as a wall, climbs to the top
   corner and spins his web there; tap him for a trick. The fun one, last: a character that lives in the interface.

Then the ego card has already landed; this is what it was for. The trash heap, if it's built, sits after this: most of what you
can build with this, you shouldn't.

## The team — the Principal proof (John, 2026-10-06)

Not a card; a thing to say, probably in Why Anthropic right before "four months". When John came back from leave the team was
afraid of AI. Five minutes with Claude Code and he could see the power; nobody had asked him to fix the gap, he picked it. He
built and shared, built and shared, until the team took it and ran — the same move as "fork it and run with it", on the team's
habits instead of a calendar. "People are still working in Figma, which is fine" — keep the generosity; the point is the gap he
chose to stand in. Have one concrete after (a designer who shipped a build instead of flats; a review on a prototype instead of a
frame). The line: "and then I turned around and brought the team with me."

## Why Anthropic?

**Built 2026-10-06 — three cards after Why Anthropic?, in John's words, one line each (12ga, 12gb, 12gc):** "I picked up Claude
Code four months ago." → "One session, and everything I'd spent years mastering disappeared overnight." → "It's been the most joyous time of my career." Tap through them at the pace they're said; the third is the turn, loss then joy. Then Thanks. The
earlier plan below is kept for what to say; "For myself, and for her" is cut as a card (too private to read cold — say it, with
Roma's name, if at all), and "Then I brought the team with me" / "I did all of this in four months" can follow as cards if wanted.

John's story, to say over the cards. Sincere. The earlier five-card plan, one line each, the mono, same rag:

1. **Why Anthropic?** — the card.
2. **"Everything I spent eleven years mastering disappeared overnight."** — I left to have a baby. Sketch, Figma, Adobe,
   production design, pixel-perfect — the craft of eleven years. I came back to a different future than the one I left. One
   sentence on the fear, fast, then move: "I came back scared. I didn't know what my skills were for anymore."
3. **"One session of Claude Code. More power than eleven years."** — I jumped in head first. More power in my fingertips in
   that first session than in the last eleven years of shaping product. Creativity exploded: building, testing, learning, a
   hundred things made and thrown away. (The trash heap can sit here.) Once I'd touched this I couldn't un-see how much more
   there was to make — never "my world at Airbnb got small".
4. **"For myself, and for her."** — Airbnb taught me how to communicate, how to make, how to ship; I'll always treasure it. Now
   I want to use those skills properly, on the thing that matters most, responsibly — for myself and for my daughter. (Roma is
   already on slide 2 and the ego card; don't explain the line.) Cut "the best of the best / the hive mind / the cutting edge":
   every candidate says it; the deck has already shown why.
5. **"I did all of this in four months."** — and stop. It does double work: the Airbnb ship and everything after it.

Then Thanks. Consider "High conviction, held loosely." as the last word, after four months — the humility that lets the boast
land.
