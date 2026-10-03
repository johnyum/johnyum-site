// The monster kit — what a character is, shared by the two pages that use one:
// monsters/ (where you build it) and peek/ (where it lives in a UI). One copy, so
// the two can never disagree about what a Gumdrop is or where an ear goes.
//
// A character is [body, ...parts]. The body is one organic shape; a part is a few
// shapes in its own frame (+y out of the body), stored not as a position but as a
// direction from the body's centre — it sits where that direction meets the body.
// Everything is a signed distance field. The shader in monsters/index.html carries
// its own copy of prim() — change one, change both.
import * as THREE from 'three';

export const BODIES = ['Round', 'Gumdrop', 'Hunch', 'Bell', 'Peanut', 'Noodle', 'Slug', 'Mochi'];   // prim types 8–15
// A part: its sub-shapes in part units (+y points out of the body), and where it goes by default.
// c: 'self' takes the part's colour. k: how much it melts into what it touches (× the Melt slider).
export const PARTS = {
  // A bead eye, as plush toys have: glossy black (or any colour) with a white catch-light.
  // In a part's frame +y is out of the body and -z is up the face, so the light sits top-left.
  eye:      { name: 'Eye', s: .14, color: '#1a1a1a', dir: [.36, .36, 1], subs: [
              { t: 0, p: [0, .2, 0], s: [1, 1, 1.15], c: 'self', k: .08 },
              { t: 0, p: [-.32, .98, -.38], s: [.26, .26, .26], c: '#ffffff', k: .02 }] },
  smile:    { name: 'Smile', s: .19, color: '#3a2328', dir: [0, -.14, 1], carve: true, subs: [
              { t: 19, p: [0, 0, -.35], s: [1, 1, 1], c: 'self', k: .3 }] },
  blush:    { name: 'Blush', s: .13, color: '#f39bb0', dir: [.55, .02, .85], subs: [
              { t: 7, p: [0, 0, 0], s: [1, 1, 1], c: 'self', k: .04 }] },
  nose:     { name: 'Nose', s: .1, color: null, dir: [0, .16, 1], subs: [{ t: 0, p: [0, .35, 0], s: [1, .85, 1], c: 'self', k: .6 }] },
  horn:     { name: 'Horn', s: .22, color: '#f1ece4', dir: [.4, 1, .05], subs: [{ t: 16, p: [0, -.25, 0], s: [1, 1, 1], c: 'self', k: .5 }] },
  ear:      { name: 'Ear', s: .24, color: null, dir: [.62, .9, .05], subs: [{ t: 0, p: [0, .9, 0], s: [.75, 1.15, .28], c: 'self', k: .7 }] },
  antenna:  { name: 'Antenna', s: .2, color: null, dir: [.22, 1, 0], subs: [
              { t: 6, p: [0, .9, 0], s: [.6, .9, .6], c: 'self', k: .5 },
              { t: 0, p: [0, 1.9, 0], s: [.34, .34, .34], c: '#e8b04a', k: .3 }] },
  arm:      { name: 'Arm', s: .2, color: null, dir: [1, 0, .2], subs: [
              { t: 17, p: [0, -.2, 0], s: [1, 1, 1], c: 'self', k: .9 },
              { t: 0, p: [0, 1.3, .41], s: [.42, .42, .42], c: 'self', k: .6 }] },
  leg:      { name: 'Leg', s: .26, color: null, dir: [.38, -1, .12], subs: [
              { t: 2, p: [0, .45, 0], s: [.58, .72, .58], c: 'self', k: .8 },
              { t: 0, p: [0, 1.1, .28], s: [.52, .34, .68], c: 'self', k: .5 }] },
  tentacle: { name: 'Tentacle', s: .3, color: null, dir: [.55, -.7, .45], subs: [{ t: 18, p: [0, -.2, 0], s: [1, 1, 1], c: 'self', k: .8 }] },
  lump:     { name: 'Lump', s: .26, color: null, dir: [0, 1, 0], subs: [{ t: 0, p: [0, .15, 0], s: [1, 1, 1], c: 'self', k: 1 }] },
  spots:    { name: 'Spots', s: .14, color: '#8a5cd6', dir: [.62, .15, .7], subs: [
              { t: 7, p: [0, 0, 0], s: [1, 1, 1], c: 'self', k: .04 },
              { t: 7, p: [1.5, -.05, .9], s: [.6, 1, .6], c: 'self', k: .04 },
              { t: 7, p: [-.4, -.05, 1.7], s: [.45, 1, .45], c: 'self', k: .04 }] },
};

export const roundCone = (qx, qy, r1, r2, h) => {
  const b = (r1 - r2) / h, a = Math.sqrt(1 - b * b), k = -b * qx + a * qy;
  if (k < 0) return Math.hypot(qx, qy) - r1;
  if (k > a * h) return Math.hypot(qx, qy - h) - r2;
  return qx * a + qy * b - r1;
};
export const smin = (a, b, k) => { const h = Math.min(1, Math.max(0, .5 + .5 * (b - a) / k)); return b + (a - b) * h - k * h * (1 - h); };
// Unit shapes. Kept identical to prim() in monsters/index.html's shader — change one, change both.
export function prim(t, x, y, z) {
  switch (t) {
    case 0: return Math.hypot(x, y, z) - 1;
    case 2: return Math.hypot(x, y - Math.max(-.6, Math.min(.6, y)), z) - .5;
    case 5: return roundCone(Math.hypot(x, z), y + .7, .7, .08, 1.5);
    case 6: return Math.hypot(x, y - Math.max(-1, Math.min(1, y)), z) - .14;
    case 7: { const dx = Math.hypot(x, z) - .85, dy = Math.abs(y) - .06;
      return Math.min(Math.max(dx, dy), 0) + Math.hypot(Math.max(dx, 0), Math.max(dy, 0)) - .04; }
    // bodies
    case 8: return Math.hypot(x, y, z) - 1;                                                   // round
    case 9: return (Math.hypot(x, y * .85, z) - (1 - .32 * y)) * .62;                         // gumdrop
    case 10: return (Math.hypot(x * .92, y * .85, z * 1.12) - (1 + .3 * y)) * .62;            // hunch
    case 11: return roundCone(Math.hypot(x, z), y + .75, 1, .5, 1.45);                       // bell
    case 12: return smin(Math.hypot(x, y - .55, z) - .6, Math.hypot(x, y + .42, z) - .78, .3); // peanut
    case 13: { const qz = z - .3 * Math.sin(y * 1.4);                                         // noodle, wiggling front to back
      return (Math.hypot(x, y - Math.max(-1.15, Math.min(1.15, y)), qz) - .45) * .75; }
    case 14: return (Math.hypot(x * .58, y * 1.3, z * .95) - (1 + .2 * z)) * .5;              // slug
    case 15: return smin(Math.hypot(x * .82, y * 1.25, z * .9) - 1, -.55 - y, -.25);         // mochi: soft, wide, sat flat (a negative k is a smooth max)
    // part shapes
    case 16: { const qz = z + .28 * y * y; return roundCone(Math.hypot(x, qz), y, .45, .06, 1.8) * .8; }   // curved horn
    case 17: { const qz = z - .18 * y * y; return (Math.hypot(x, y - Math.max(0, Math.min(1.5, y)), qz) - .3) * .85; }   // bent arm
    case 18: { const qx = x - .25 * Math.sin(y * 2.2), r = .38 + (.08 - .38) * Math.min(1, Math.max(0, y / 2));   // tentacle
      return (Math.hypot(qx, y - Math.max(0, Math.min(2, y)), z) - r) * .7; }
    case 19: return Math.max(Math.hypot(Math.hypot(x, z) - .8, y) - .2, .25 - z);           // smile: the lower arc of a ring
    default: return Math.hypot(x, y, z) - 1;
  }
}

// ── the body, and where parts sit on it ──
const tmp = new THREE.Vector3();
const bottomCache = {};
export function bottomOf(type) {   // how far below its centre a unit body reaches, so it can stand on the floor
  if (bottomCache[type] == null) { let y = -2.5; while (prim(8 + type, 0, y, 0) > 0 && y < 0) y += .005; bottomCache[type] = y; }
  return bottomCache[type];
}
// The body's centre, scale and shape: standing on y = 0.
export function bodyFrameOf(b) {
  const sc = new THREE.Vector3(b.w, b.h, b.d).multiplyScalar(b.s);
  return { c: new THREE.Vector3(0, -bottomOf(b.type) * sc.y, 0), s: sc, type: 8 + b.type };
}
export const bodyField = (B, p) => { tmp.copy(p).sub(B.c); return prim(B.type, tmp.x / B.s.x, tmp.y / B.s.y, tmp.z / B.s.z) * Math.min(B.s.x, B.s.y, B.s.z); };
// Where a direction from the body's centre meets its surface, and the outward normal there.
export function anchor(B, dir) {
  const d = new THREE.Vector3(...dir).normalize(), p = new THREE.Vector3(), start = B.c.clone().addScaledVector(d, 6);
  let t = 0;
  for (let i = 0; i < 200 && t < 6; i++) {
    p.copy(start).addScaledVector(d, -t);
    const f = bodyField(B, p);
    if (f < .002) break;
    t += Math.max(f * .9, .002);
  }
  const e = .002, n = new THREE.Vector3(
    bodyField(B, p.clone().add(new THREE.Vector3(e, 0, 0))) - bodyField(B, p.clone().add(new THREE.Vector3(-e, 0, 0))),
    bodyField(B, p.clone().add(new THREE.Vector3(0, e, 0))) - bodyField(B, p.clone().add(new THREE.Vector3(0, -e, 0))),
    bodyField(B, p.clone().add(new THREE.Vector3(0, 0, e))) - bodyField(B, p.clone().add(new THREE.Vector3(0, 0, -e)))).normalize();
  return { p, n };
}
// A part placed on the body: its origin and orientation, for one side (m = 1, or -1 for its mirror twin).
const UP = new THREE.Vector3(0, 1, 0), ZED = new THREE.Vector3(0, 0, 1);
export function partPose(B, part, m = 1) {
  const at = anchor(B, [part.dir[0] * m, part.dir[1], part.dir[2]]);
  const q = new THREE.Quaternion().setFromUnitVectors(UP, at.n)
    .multiply(new THREE.Quaternion().setFromAxisAngle(UP, (part.turn || 0) * m))
    .multiply(new THREE.Quaternion().setFromAxisAngle(ZED, (part.tilt || 0) * m));
  return { origin: at.p.clone().addScaledVector(at.n, (part.lift || 0) * part.s), q, n: at.n, p: at.p };
}
export const twinned = (part, mirror = true) => mirror && Math.abs(part.dir[0]) > .06;

// A character travels between pages in the URL — short enough to share.
export const pack = (shapes) => btoa(unescape(encodeURIComponent(JSON.stringify(shapes)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
export function unpack(s) {
  try { return JSON.parse(decodeURIComponent(escape(atob(s.replace(/-/g, '+').replace(/_/g, '/'))))); } catch { return null; }
}
