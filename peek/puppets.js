// Peek's made characters: a folded paper figure and a hand-drawn ink figure.
//
// Neither is a creature with a face. Both are things — a figure folded from the chat's own
// ivory paper, a figure drawn in one weight of ink with a flat clay accent behind it, the way
// Claude's illustrations are drawn — and both feel things with their bodies: a slump, a recoil,
// a spring up, a head that tilts. Two small eyes for where it's looking; no mouth, no blush.
//
// One rig under both. Every joint angle is a spring chasing a target, never set: a pose is only
// ever a set of targets, so moods and moves blend into each other with weight and follow-through
// — the head lags the body, the arms lag the shoulders, nothing cuts.
//
//   makePuppet(kind, THREE) → { group, height, update(dt, ctx), mood(m) }
//   ctx: { t, mode, running, phase, vx, vy, ax, yaw, arms, grabbed, blink, look: {x, y}, swing }

const PAPER = '#f4f1e8', CREASE = '#cfc6b3', INK = '#141413', CLAY = '#d97757';

// A spring per value: stiffness k, damping ratio z (under 1 overshoots a touch — that's the life).
function spring(x = 0, k = 140, z = .72) {
  return { x, v: 0, k, z, to: x,
    step(dt) { const f = this.k * (this.to - this.x) - 2 * Math.sqrt(this.k) * this.z * this.v; this.v += f * dt; this.x += this.v * dt; return this.x; } };
}

// Where a joint is in `frame`'s own space, by its chain of local transforms — never through the
// world matrix, which is singular whenever the character is scaled to nothing (popping in or out).
function relTo(THREE) {
  const m = new THREE.Matrix4(), inv = new THREE.Matrix4(), v = new THREE.Vector3();
  return (o, top, frame) => {
    m.identity();
    for (let p = o; p && p !== top; p = p.parent) { p.updateMatrix(); m.premultiply(p.matrix); }
    v.setFromMatrixPosition(m);
    if (frame && frame !== top) { frame.updateMatrix(); v.applyMatrix4(inv.copy(frame.matrix).invert()); }
    return v;
  };
}

// Proportions: a small head on a real body — about a quarter of its height, not half.
const D = { hip: .44, chest: .35, neck: .045, head: .145, sh: .155, upper: .175, fore: .165, hipW: .072, thigh: .215, shin: .215 };

// Body language. Each mood is a set of targets; anything left out is neutral.
//   lean: forward (+) / back · side: toward screen-right (+) · drop: crouch · stretch: taller
//   nod: head down (+) · tilt · turn: head away · out: arms away from the body · fwd: arms forward
//   bend: elbows · a/b suffixes: the screen-right / screen-left arm, when they differ
const MOOD = {
  // Every pose is drawn in the picture's own plane — both figures are flat, so a body that leans
  // toward you says nothing. Big shapes: a Y for surprise, a droop for sad, clasped for love.
  happy:     { outA: .2, outB: .1, bendA: .35, bendB: .15, side: .03, tilt: .07 },   // weight on one leg, never square-on
  curious:   { tilt: .38, side: .07, outA: .3, bendA: .9, outB: .08, bendB: .2 },
  thinking:  { tilt: .3, outA: .6, bendA: 1.85, outB: 2.4, bendB: -1.6, side: -.04, nod: -.2 },   // a hand on the hip, the other scratching its head
  surprised: { outA: 2.35, outB: 2.35, bendA: .35, bendB: .35, stretch: .07, eyes: 1.5 },
  love:      { out: .25, bend: 1.2, tilt: .32, sway: 1, knee: .1 },   // bashful: hands clasped low in front, swaying
  sleepy:    { tilt: .5, drop: .035, side: .05, out: -.02, bend: .05, knee: .15 },
  ugh:       { out: .3, bend: -.12, nod: .45, side: -.1, tremble: 1, stretch: -.03, slump: .5 },   // rigid arms, head sunk, shaking
  sad:       { tilt: .28, nod: .75, drop: .05, side: -.05, out: -.07, bend: .1, knee: .22, slump: 1 },

  // The work: how Claude's reply is going, from behind the chat box, its forearms on the edge
  // like a desk. These keep their own arms (own) instead of the plain lean-on-the-sill.
  pondering: { own: 1, outB: 2.4, bendB: -1.6, outA: .3, bendA: .4, tilt: .3, nod: -.15, eyes: .6 },  // scratching its head
  working:   { own: 1, out: .35, bend: .55, nod: .35, eyes: .7, work: 1 },                              // low at the box, hands down at it — one lifts as words land
  paused:    { own: 1, outA: .75, bendA: 2.65, outB: .15, bendB: .2, nod: -.35, eyes: 1.15 },           // stopped: hand to its chin, looking up
  sure:      { own: 1, out: .14, bend: .2, tilt: .06 },                                                 // done: standing tall and easy
  unsure:    { own: 1, out: 1.25, bend: -1.25, tilt: .26, eyes: .85 },                                  // done, a shrug
  asking:    { own: 1, outA: 2.6, bendA: .3, outB: .95, bendB: 2.1, tilt: .1, eyes: 1.15 },             // done, a hand up: your turn
  failed:    { own: 1, out: .45, bend: .9, nod: .55, tilt: .15, eyes: .35, slump: 1 },                  // couldn't
};
const EYES = { happy: 1, curious: 1.15, thinking: .7, surprised: 1.5, love: .25, sleepy: .15, ugh: .35, sad: .55 };
const KEYS = ['slump', 'lean', 'side', 'drop', 'stretch', 'nod', 'tilt', 'turn', 'outA', 'outB', 'fwdA', 'fwdB', 'bendA', 'bendB',
  'hipA', 'hipB', 'kneeA', 'kneeB', 'eyes'];

export function makePuppet(kind, THREE) {
  const group = new THREE.Group();
  const skel = new THREE.Group(); group.add(skel);
  const piv = (parent, x, y, z = 0) => { const g = new THREE.Group(); g.position.set(x, y, z); parent.add(g); return g; };

  // The skeleton: hips → spine → chest → neck → head; shoulders → elbows → hands; hips → knees → feet.
  const hips = piv(skel, 0, D.hip), chest = piv(hips, 0, D.chest), neck = piv(chest, 0, D.neck), head = piv(neck, 0, D.head * .95);
  const arm = (s) => { const sh = piv(chest, s * D.sh, -.03), el = piv(sh, 0, -D.upper), hand = piv(el, 0, -D.fore); return { s, sh, el, hand }; };
  const leg = (s) => { const hp = piv(hips, s * D.hipW, 0), kn = piv(hp, 0, -D.thigh), ft = piv(kn, 0, -D.shin); return { s, hp, kn, ft }; };
  const A = arm(1), B = arm(-1), LA = leg(1), LB = leg(-1);
  const eyeAt = [-1, 1].map((s) => piv(head, s * .055, .015, D.head * .93));

  // Springs. The head and arms are a little looser than the trunk: they arrive late, and settle.
  const sp = {};
  for (const k of KEYS) sp[k] = spring(k === 'eyes' ? 1 : k === 'stretch' ? 0 : 0, k.startsWith('fwd') || k.startsWith('out') || k.startsWith('bend') ? 95 : k === 'nod' || k === 'tilt' || k === 'turn' ? 80 : 150, k === 'eyes' ? .9 : .66);
  let moodNow = 'happy';

  const look = (() => {
    if (kind === 'line') return makeLine(THREE, group, { hips, chest, neck, head, A, B, LA, LB, eyeAt });
    return makePaper(THREE, { hips, chest, neck, head, A, B, LA, LB, eyeAt });
  })();

  function targets(c) {
    const m = MOOD[moodNow] || MOOD.happy, g = (k, d = 0) => m[k] ?? d;
    const T = { lean: g('lean'), side: g('side'), drop: g('drop'), stretch: g('stretch'), nod: g('nod'), tilt: g('tilt'), turn: g('turn'),
      outA: g('outA', g('out', .12)), outB: g('outB', g('out', .12)), fwdA: g('fwdA', g('fwd')), fwdB: g('fwdB', g('fwd')),
      bendA: g('bendA', g('bend', .2)), bendB: g('bendB', g('bend', .2)), hipA: 0, hipB: 0, kneeA: g('knee'), kneeB: g('knee'),
      eyes: c.blink ? .08 : m.eyes ?? EYES[moodNow] ?? 1 };
    const t = c.t;
    if (m.sway) T.side += Math.sin(t * 2.2) * .06;
    if (m.work) { const odd = (c.beat || 0) % 2; if (odd) { T.outA += .35; T.bendA += .9; } else { T.outB += .35; T.bendB += .9; } T.tilt += odd ? .06 : -.06; }
    T.slump = m.slump || 0;
    if (m.tremble) T.side += Math.sin(t * 55) * .025;
    // Breathing: always, a little — a still figure reads as a picture, not a thing that's alive.
    T.stretch += Math.sin(t * 2.4) * .008;
    // And a slow shift of weight from foot to foot, so it's never a statue.
    T.side += Math.sin(t * .7) * .02; T.tilt += Math.sin(t * .53 + 1) * .03;

    if (c.grabbed) {
      // Held by the scruff: everything hangs, and swings behind the way you move it.
      Object.assign(T, { lean: 0, drop: 0, stretch: .03, outA: .05, outB: .05, fwdA: 0, fwdB: 0, bendA: .1, bendB: .1, hipA: .1, hipB: -.05, kneeA: .25, kneeB: .15 });
      T.side = Math.max(-.5, Math.min(.5, -c.vx * .0009));
    } else if (c.running) {
      const p = c.phase, s = Math.sin(p);
      Object.assign(T, { lean: .22, fwdA: -s * .75, fwdB: s * .75, bendA: 1, bendB: 1, outA: .12, outB: .12,
        hipA: s * .8, hipB: -s * .8, kneeA: Math.max(0, -s) * 1.3 + .15, kneeB: Math.max(0, s) * 1.3 + .15 });
      T.drop = -Math.abs(Math.cos(p)) * .02;
    } else if (c.mode === 'air') {
      Object.assign(T, { hipA: .7, hipB: .55, kneeA: 1.2, kneeB: 1, outA: .95, outB: .95, bendA: .3, bendB: .3, stretch: .04 });
    } else if (c.mode === 'sit') {
      // On the edge, legs over the front, kicking a little; hands down beside it on the ledge.
      // Seen from the front, sitting on a ledge is legs hanging down over its face, swinging.
      const k = Math.sin(t * 3.2) * .3;
      Object.assign(T, { hipA: 0, hipB: 0, kneeA: .25 + k, kneeB: .25 - k, outA: .42, outB: .42, bendA: -.25, bendB: -.25 });
      T.drop += D.hip - .03;
    } else if (c.mode === 'peek' && !m.own) {
      // Behind the box: forearms up on its top edge, like leaning on a windowsill.
      Object.assign(T, { fwdA: 0, fwdB: 0, outA: .95, outB: .95, bendA: 2.1, bendB: 2.1 });
      if (moodNow === 'surprised') { T.outA = T.outB = 2.3; T.bendA = T.bendB = .3; }
    } else if (c.mode === 'hang' || c.arms === 'up' || c.arms === 'hold') {
      Object.assign(T, { outA: Math.PI - .35, outB: Math.PI - .35, fwdA: 0, fwdB: 0, bendA: c.arms === 'hold' ? .5 : .05, bendB: c.arms === 'hold' ? .5 : .05 });
      if (c.mode === 'hang') { const k = Math.sin(c.swing * 2) * .35; T.hipA = .2 + k; T.hipB = .2 - k; T.kneeA = T.kneeB = .3; }
    }
    // Follow-through: the trunk leans into a sudden change of speed, and the arms trail it.
    T.side += Math.max(-.12, Math.min(.12, -c.ax * .00003));
    return T;
  }

  function update(dt, c) {
    const T = targets(c);
    for (const k of KEYS) { sp[k].to = T[k]; sp[k].step(dt); }
    const v = (k) => sp[k].x;
    hips.position.y = D.hip - v('drop');
    hips.rotation.set(v('lean') * .45, 0, -v('side') * .8);
    chest.rotation.set(v('lean') * .55, 0, -v('side') * .5);
    chest.scale.y = 1 + v('stretch') - v('slump') * .06;
    for (const L of [A, B]) L.sh.position.y = -.03 - v('slump') * .03;
    neck.rotation.set(v('nod') * .4, v('turn') * .4, -v('tilt') * .4);
    head.rotation.set(v('nod') * .7, v('turn') * .7, -v('tilt') * .7);
    head.position.y = D.head * .95 - Math.max(0, v('nod')) * .055;   // seen flat, a nod is the head sinking
    // Elbows and knees fold in the picture plane — an elbow folds the forearm in across the body,
    // a knee kicks the shin out — with a little depth kept so a turned figure still bends.
    for (const [L, a] of [[A, 'A'], [B, 'B']]) {
      L.sh.rotation.set(-v('fwd' + a), 0, L.s * v('out' + a));
      L.el.rotation.set(-v('bend' + a) * .2, 0, -L.s * v('bend' + a) * .95);
    }
    for (const [L, a] of [[LA, 'A'], [LB, 'B']]) {
      L.hp.rotation.set(-v('hip' + a), 0, L.s * (.04 + v('knee' + a) * .35));
      L.kn.rotation.set(v('knee' + a) * .3, 0, -L.s * v('knee' + a) * .8);
    }
    look.update(dt, c, v('eyes'), sp);
  }

  return { group, height: D.hip + D.chest + D.neck + D.head * 1.95, update, mood(m) { moodNow = m; look.mood?.(m); } };
}

/* ─────────────── paper: a jointed cut-out ───────────────
   A paper doll held together with pins, like Lotte Reiniger's silhouettes: flat pieces of the
   chat's own ivory, each with a thin edge and a soft shadow where it lifts off the page, kraft
   pins at the joints, two punched holes for eyes. It works in its own flat plane, so it turns the
   way paper does — narrowing to an edge — and a blow crinkles it: every piece knocked askew,
   then easing back flat. */
function makePaper(THREE, R) {
  // Paper grain: faint fibres, so the ivory reads as stock, not as flat colour.
  const tex = (() => {
    const c = document.createElement('canvas'); c.width = c.height = 128; const g = c.getContext('2d');
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, 128, 128);
    for (let i = 0; i < 900; i++) { g.fillStyle = `rgba(120,100,70,${Math.random() * .05})`; g.fillRect(Math.random() * 128, Math.random() * 128, 1 + Math.random() * 3, 1); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.colorSpace = THREE.SRGBColorSpace; return t;
  })();
  // On a white chat, paper only exists by its cut edge and its shadow — both have to be crisp.
  const face = new THREE.MeshStandardMaterial({ color: '#f3efe5', map: tex, roughness: 1, side: THREE.DoubleSide });
  const edge = new THREE.MeshBasicMaterial({ color: '#b9ab92', side: THREE.DoubleSide });
  const shade = new THREE.MeshBasicMaterial({ color: '#3b3226', transparent: true, opacity: .2, depthWrite: false, side: THREE.DoubleSide });
  const pinM = new THREE.MeshStandardMaterial({ color: '#c39a6b', roughness: .45, metalness: .35 });
  const hole = new THREE.MeshBasicMaterial({ color: '#2a2622' });

  const flat = new THREE.Group(); R.hips.parent.parent.add(flat);   // in the figure's own plane, beside the skeleton
  // A piece: its shape, a hair-thin edge round it, and its shadow below-right on the page.
  // The same outline pushed out by e, for the cut edge.
  function grow(shape, e) {
    const pts = shape.getPoints(24), n = pts.length, out = [];
    let area = 0; for (let i = 0; i < n; i++) { const a = pts[i], b = pts[(i + 1) % n]; area += a.x * b.y - b.x * a.y; }
    const sgn = area > 0 ? 1 : -1;
    for (let i = 0; i < n; i++) {
      const a = pts[(i - 1 + n) % n], b = pts[i], c = pts[(i + 1) % n];
      const n1 = new THREE.Vector2(b.y - a.y, a.x - b.x).normalize(), n2 = new THREE.Vector2(c.y - b.y, b.x - c.x).normalize();
      const nn = n1.add(n2).normalize().multiplyScalar(e * sgn); out.push(new THREE.Vector2(b.x + nn.x, b.y + nn.y));
    }
    return new THREE.Shape(out);
  }
  function piece(shape, z) {
    const g = new THREE.Group(), geo = new THREE.ShapeGeometry(shape, 10);
    const out = new THREE.Mesh(new THREE.ShapeGeometry(grow(shape, .013), 1), edge);   // a cut edge that still reads when it's drawn at text size out.position.z = -.001;
    const sh = new THREE.Mesh(out.geometry, shade); sh.position.set(.014, -.018, -.03);
    g.add(sh, out, new THREE.Mesh(geo, face)); g.position.z = z; flat.add(g); return g;
  }
  // A limb segment: a long rounded strip hanging down from its joint (0,0) to (0,-len).
  const strip = (len, w0, w1 = w0) => { const s = new THREE.Shape(); s.moveTo(-w0, 0); s.absarc(0, 0, w0, Math.PI, 0, true); s.lineTo(w1, -len); s.absarc(0, -len, w1, 0, Math.PI, true); s.lineTo(-w0, 0); return s; };
  const egg = (w, h) => { const s = new THREE.Shape(); s.moveTo(0, h); s.bezierCurveTo(w * 1.1, h, w, -h * .55, 0, -h); s.bezierCurveTo(-w, -h * .55, -w * 1.1, h, 0, h); return s; };
  const torsoShape = (() => { const s = new THREE.Shape(), t = .118, b = .092, h = D.chest + .02;
    s.moveTo(-t + .03, h); s.lineTo(t - .03, h); s.quadraticCurveTo(t, h, t - .004, h - .04); s.quadraticCurveTo(b + .012, h * .45, b, .02);
    s.quadraticCurveTo(b, -.03, b - .04, -.035); s.lineTo(-b + .04, -.035); s.quadraticCurveTo(-b, -.03, -b, .02);
    s.quadraticCurveTo(-b - .012, h * .45, -t + .004, h - .04); s.quadraticCurveTo(-t, h, -t + .03, h); return s; })();
  const footShape = (() => { const s = new THREE.Shape(); s.moveTo(-.03, .012); s.lineTo(.045, .012); s.absarc(.045, -.004, .016, Math.PI / 2, -Math.PI / 2, true); s.lineTo(-.03, -.02); s.absarc(-.03, -.004, .016, -Math.PI / 2, Math.PI / 2, true); return s; })();

  // Back to front: the far arm and leg, the body, the head, the near arm and leg.
  const P = {
    legB: [piece(strip(D.thigh, .036, .031), .01), piece(strip(D.shin, .031, .027), .012), piece(footShape, .014)],
    armB: [piece(strip(D.upper, .03, .026), .02), piece(strip(D.fore, .026, .028), .022)],
    torso: piece(torsoShape, .05),
    head: piece(egg(.118, .14), .07),
    legA: [piece(strip(D.thigh, .036, .031), .08), piece(strip(D.shin, .031, .027), .082), piece(footShape, .084)],
    armA: [piece(strip(D.upper, .03, .026), .09), piece(strip(D.fore, .026, .028), .092)],
  };
  const pins = Array.from({ length: 9 }, () => { const m = new THREE.Mesh(new THREE.CircleGeometry(.0105, 12), pinM); flat.add(m); return m; });
  const eyes = [0, 1].map(() => { const m = new THREE.Mesh(new THREE.CircleGeometry(.013, 14), hole); flat.add(m); return m; });

  const rel = relTo(THREE), top = flat.parent;
  const at = (o) => { const v = rel(o, top, flat); return { x: v.x, y: v.y }; };
  // Each piece points along its bone as the bone falls in the plane; when a bone points straight
  // at you the direction is meaningless, so the angle eases instead of jumping.
  const ang = new Map();
  function lay(g, a, b, z) {
    const dx = b.x - a.x, dy = b.y - a.y, len = Math.hypot(dx, dy);
    let target = Math.atan2(dx, -dy), cur = ang.get(g) ?? target;
    let d = target - cur; d = Math.atan2(Math.sin(d), Math.cos(d));
    cur += d * (len > .04 ? .55 : .12); ang.set(g, cur);
    g.position.set(a.x, a.y, g.position.z); g.rotation.z = cur + (crinkle.on ? crinkle.jit.get(g) * crinkle.x : 0);
    return { x: a.x + Math.sin(cur) * Math.hypot(dx, dy), y: a.y - Math.cos(cur) * Math.hypot(dx, dy) };
  }
  const crinkle = { x: 0, v: 0, on: false, jit: new Map() };
  for (const g of flat.children) crinkle.jit.set(g, (Math.random() - .5) * .9);
  let was = 'happy';

  return {
    mood(m) { if (m === 'ugh' && was !== 'ugh') crinkle.v += 7; if (m === 'surprised' && was !== 'surprised') crinkle.v += 2; was = m; },
    update(dt, c, open) {
      crinkle.v += (-55 * crinkle.x - 8 * crinkle.v) * dt; crinkle.x += crinkle.v * dt; crinkle.on = Math.abs(crinkle.x) > .002;
      const hp = at(R.hips), ch = at(R.chest), nk = at(R.neck), hd = at(R.head);
      // The body: from the hips, along the spine.
      const tAng = Math.atan2(-(ch.x - hp.x), ch.y - hp.y);
      P.torso.position.set(hp.x, hp.y, P.torso.position.z); P.torso.rotation.z = tAng + (crinkle.on ? crinkle.jit.get(P.torso) * crinkle.x * .4 : 0);
      P.head.position.set(hd.x, hd.y, P.head.position.z); P.head.rotation.z = Math.atan2(-(hd.x - nk.x), hd.y - nk.y) * 1.2 + (crinkle.on ? crinkle.jit.get(P.head) * crinkle.x : 0);
      let pin = 0;
      const pinAt = (p) => { const m = pins[pin++]; m.position.set(p.x, p.y, .12); };
      for (const [L, segs] of [[R.A, P.armA], [R.B, P.armB]]) {
        const s = at(L.sh), e1 = lay(segs[0], s, at(L.el)); lay(segs[1], e1, at(L.hand)); pinAt(s); pinAt(e1);
      }
      for (const [L, segs] of [[R.LA, P.legA], [R.LB, P.legB]]) {
        const h = at(L.hp), k1 = lay(segs[0], h, at(L.kn)), f = lay(segs[1], k1, at(L.ft));
        segs[2].position.set(f.x, f.y, segs[2].position.z); segs[2].scale.x = L.s; segs[2].rotation.z = 0; pinAt(h); pinAt(k1);
      }
      pinAt(nk);
      // Eyes: punched through the head, turning with it; they narrow, widen and look.
      const hr = P.head.rotation.z;
      eyes.forEach((e, i) => {
        const ox = (i ? -.042 : .042) + c.look.x * .016, oy = .015 - c.look.y * .012;
        e.position.set(hd.x + ox * Math.cos(hr) - oy * Math.sin(hr), hd.y + ox * Math.sin(hr) + oy * Math.cos(hr), .11);
        e.rotation.z = hr; e.scale.set(1.5, Math.max(.1, open) * .62, 1);   // slits cut in the paper, not dots
      });
    },
  };
}

/* ─────────────── line: drawn in ink, one weight, round ends ───────────────
   A drawing laid over the rig, redrawn every frame from where the joints are. The head is an egg
   drawn the way a hand draws one — an open loop whose ends overlap — the body a smooth bean, each
   limb one curved stroke through its joint, the feet a short tick. Claude's flat clay sits behind
   the body, offset down and right, never filling the line. The line drifts slowly and
   continuously, the way a held pen does; it never jitters. It always faces you, like a drawing. */
function makeLine(THREE, group, R) {
  const draw = new THREE.Group(); group.add(draw);
  const ink = new THREE.MeshBasicMaterial({ color: INK }), clay = new THREE.MeshBasicMaterial({ color: CLAY });
  const W = .016;   // half the stroke: ~2.8px at Peek's size — the illustrations' contour, not a marker
  const strokes = [], caps = [];
  const cap = () => { const m = new THREE.Mesh(new THREE.SphereGeometry(W, 10, 8), ink); draw.add(m); caps.push(m); return m; };
  const accent = new THREE.Mesh(new THREE.BufferGeometry(), clay); accent.position.z = -.2; draw.add(accent);
  const eyes = [0, 1].map(() => { const e = new THREE.Mesh(new THREE.CircleGeometry(.0135, 14), ink); e.position.z = .05; draw.add(e); return e; });

  const V3 = (x, y) => new THREE.Vector3(x, y, 0), rel = relTo(THREE);
  const P = (o, dx = 0, dy = 0) => { const v = rel(o, group, draw); return V3(v.x + dx, v.y + dy); };
  const wob = (p, i, t, a = .0042) => p.add(V3(Math.sin(t * 1.3 + i * 2.1) * a, Math.cos(t * 1.1 + i * 1.7) * a));
  function stroke(i, pts, closed = false, segs = 28) {
    const curve = new THREE.CatmullRomCurve3(pts, closed, 'centripetal');
    const geo = new THREE.TubeGeometry(curve, segs, W, 6, closed);
    if (!strokes[i]) { strokes[i] = new THREE.Mesh(geo, ink); draw.add(strokes[i]); } else { strokes[i].geometry.dispose(); strokes[i].geometry = geo; }
    return curve;
  }
  let ci = 0;
  const ends = (curve) => { const a = caps[ci++] || cap(), b = caps[ci++] || cap(); a.position.copy(curve.getPoint(0)); b.position.copy(curve.getPoint(1)); };
  // A limb through its joint, bowed a touch outward at the joint so it reads as an arm, not a rod.
  const bow = (a, b, e, s, k = .018) => { const m1 = a.clone().lerp(b, .5).add(V3(s * k, 0)), m2 = b.clone().lerp(e, .5).add(V3(s * k * .6, 0)); return [a, m1, b, m2, e]; };

  return {
    update(dt, c, open) {
      draw.rotation.y = -c.yaw;
      const t = c.t; ci = 0;
      // Head: an egg, narrower at the chin, drawn as an open loop that overlaps itself.
      const hc = P(R.head), nk = P(R.neck), up = hc.clone().sub(nk).normalize(), side = V3(up.y, -up.x);
      const head = [];
      for (let i = 0; i <= 13; i++) {
        const a = -Math.PI / 2 + .35 + i / 12 * Math.PI * 2, rr = D.head * (1 - .14 * Math.max(0, -Math.sin(a)));
        head.push(wob(hc.clone().addScaledVector(side, Math.cos(a) * rr * .9).addScaledVector(up, Math.sin(a) * rr * 1.04), i, t));
      }
      ends(stroke(0, head, false, 44));
      ends(stroke(8, [hc.clone().addScaledVector(up, -D.head * .95), P(R.chest, 0, D.chest * .02 + .01)], false, 4));
      // Body: a bean from the shoulders to the hips, following the spine's curve.
      const ch = P(R.chest), hp = P(R.hips), sp = ch.clone().sub(hp), spU = sp.clone().normalize(), spS = V3(spU.y, -spU.x);
      const along = (k, w) => hp.clone().addScaledVector(sp, k).addScaledVector(spS, w);
      // The body is the clay itself — one flat shape, no outline round it: a figure in ink and one
      // colour, the way an editorial illustration does it, not an outlined doll.
      const ring = [[1.04, 0], [1, .095], [.8, .112], [.5, .1], [.2, .108], [0, .095], [-.07, .04], [-.08, 0], [-.07, -.04], [0, -.095], [.2, -.108], [.5, -.1], [.8, -.112], [1, -.095]];
      const body = ring.map(([k, w], i) => wob(along(k, w), i + 20, t, .003));
      if (strokes[1]) strokes[1].visible = false;
      accent.geometry.dispose();
      accent.geometry = new THREE.ShapeGeometry(new THREE.Shape(new THREE.CatmullRomCurve3(body, true, 'centripetal').getPoints(48).map((p) => new THREE.Vector2(p.x, p.y))), 4);
      accent.position.z = .01;
      // Arms from the shoulders, legs from the hips — each one curved stroke.
      const limb = (i, pts) => ends(stroke(i, pts.map((p, k) => wob(p, i * 7 + k, t, .0018)), false, 32));
      for (const [i, L] of [[2, R.A], [3, R.B]]) limb(i, bow(P(L.sh, -L.s * .045, -.02), P(L.el), P(L.hand), L.s, .012));
      for (const [i, L] of [[4, R.LA], [5, R.LB]]) limb(i, bow(P(L.hp, 0, .04), P(L.kn), P(L.ft), L.s, .008));
      // Feet: a short tick out from each ankle.
      for (const [i, L] of [[6, R.LA], [7, R.LB]]) { const f = P(L.ft); ends(stroke(i, [f, f.clone().add(V3(L.s * .02, -.006)), f.clone().add(V3(L.s * .048, -.004))], false, 8)); }
      // Eyes: two dots of ink that narrow, widen and look.
      R.eyeAt.forEach((p, i) => { const e = eyes[i], q = P(p); e.position.set(q.x + c.look.x * .014, q.y - c.look.y * .011 - .01, .05); e.scale.set(1.35, .75 * Math.max(.08, open), 1); });
    },
  };
}
