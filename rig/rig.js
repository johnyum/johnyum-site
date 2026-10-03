// A rigged character you can reshape — shared by rig/ (where you sculpt it) and peek/
// (where it lives in a chat). One copy, so a character looks the same in both.
//
// Two kinds of change, both kept through every animation:
//   proportions  bone scales (a bigger head, longer legs), applied after the animation
//                each frame, each bone's own factor divided out of its children so a
//                bigger chest doesn't also mean bigger arms
//   sculpt       offsets on the mesh in its rest pose. Skinning carries them into every
//                pose, so the sculpt moves with the character. The low-poly meshes split
//                vertices at hard edges, so the offsets are kept per *position* (a weld
//                group), not per vertex — or a brush would tear the surface along its seams.
//
// A character is a small JSON state: { v, model, prop, colors, face, sculpt }, with the
// sculpt as [group, dx, dy, dz] for each moved group. pack()/unpack() put it in a link.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// Quaternius' Animated Mech Pack (CC0) — rig/models/LICENSE.txt.
export const MODELS = ['Mike', 'Stan', 'George', 'Leela'];
// Bone names as three.js gives them: it strips the dots, so the file's "UpperArm.L" is "UpperArmL".
export const PROPS = {
  head:  { label: 'Head',  bones: [/^Head$/], axes: 'xyz' },
  chest: { label: 'Chest', bones: [/^Chest$/], axes: 'xz' },
  arms:  { label: 'Arms',  bones: [/^UpperArm[._]?[LR]$/, /^LowerArm[._]?[LR]$/], axes: 'y' },
  hands: { label: 'Hands', bones: [/^Palm[A-Z][._]?[LR]$/], axes: 'xyz' },
  legs:  { label: 'Legs',  bones: [/^UpperLeg[._]?[LR]$/, /^MidLeg[._]?[LR]$/, /^LowerLeg[._]?[LR]$/], axes: 'y' },
  feet:  { label: 'Feet',  bones: [/^Foot[._]?[LR]$/, /^FootBack[._]?[LR]$/], axes: 'xyz' },
};
export const blankState = (model = 'Mike') => ({ v: 1, model, prop: {}, colors: {}, face: true, sculpt: [] });

export async function loadRig(state, base = new URL('./models/', import.meta.url).href) {
  const gltf = await new GLTFLoader().loadAsync(`${base}${state.model}.gltf`);
  const scene = gltf.scene, meshes = [];
  scene.traverse((o) => { if (o.isSkinnedMesh) { meshes.push(o); o.frustumCulled = false; } });
  const bones = meshes[0].skeleton.bones;
  const rest = bones.map((b) => ({ p: b.position.clone(), q: b.quaternion.clone(), s: b.scale.clone() }));

  // Weld groups: every vertex at one position, across all six coloured parts, moves as one.
  const key = (x, y, z) => `${Math.round(x * 1e4)},${Math.round(y * 1e4)},${Math.round(z * 1e4)}`;
  const at = new Map(), groups = [];
  meshes.forEach((m, mi) => {
    const pos = m.geometry.attributes.position, nor = m.geometry.attributes.normal, gOf = new Int32Array(pos.count);
    for (let i = 0; i < pos.count; i++) {
      const k = key(pos.getX(i), pos.getY(i), pos.getZ(i));
      let g = at.get(k);
      if (g == null) { g = groups.length; at.set(k, g); groups.push({ b: new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i)), d: new THREE.Vector3(), n: new THREE.Vector3(), m: [], nb: new Set() }); }
      groups[g].m.push(mi, i); groups[g].n.x += nor.getX(i); groups[g].n.y += nor.getY(i); groups[g].n.z += nor.getZ(i); gOf[i] = g;
    }
    const idx = m.geometry.index;
    if (idx) for (let t = 0; t < idx.count; t += 3) {
      const a = gOf[idx.getX(t)], b = gOf[idx.getX(t + 1)], c = gOf[idx.getX(t + 2)];
      groups[a].nb.add(b).add(c); groups[b].nb.add(a).add(c); groups[c].nb.add(a).add(b);
    }
    m.userData.gOf = gOf;
  });
  for (const g of groups) g.n.normalize();

  // Bone scale factors, by name.
  const factor = new Map();
  function setProps(prop) {
    factor.clear();
    for (const [k, P] of Object.entries(PROPS)) {
      const f = prop[k] ?? 1; if (f === 1) continue;
      const v = new THREE.Vector3(P.axes.includes('x') ? f : 1, P.axes.includes('y') ? f : 1, P.axes.includes('z') ? f : 1);
      for (const b of bones) if (P.bones.some((r) => r.test(b.name))) factor.set(b, v);
    }
  }
  // Every bone back to rest — the animation then sets the ones it moves.
  function restore() { bones.forEach((b, i) => { b.position.copy(rest[i].p); b.quaternion.copy(rest[i].q); b.scale.copy(rest[i].s); }); }
  // After the animation: each bone's factor in, its parent's divided out.
  const one = new THREE.Vector3(1, 1, 1);
  function shape() { for (const b of bones) { const f = factor.get(b), pf = factor.get(b.parent); if (f) b.scale.multiply(f); if (pf) b.scale.divide(pf); } }

  // Write moved groups back into the meshes.
  const dirty = new Set();
  function write(list) {
    for (const gi of list) { const g = groups[gi];
      for (let j = 0; j < g.m.length; j += 2) { const m = meshes[g.m[j]]; m.geometry.attributes.position.setXYZ(g.m[j + 1], g.b.x + g.d.x, g.b.y + g.d.y, g.b.z + g.d.z); dirty.add(m); } }
  }
  function flush() {
    for (const m of dirty) { m.geometry.attributes.position.needsUpdate = true; m.geometry.computeVertexNormals(); m.geometry.computeBoundingSphere(); }
    dirty.clear();
  }
  function setSculpt(list) {
    const touched = [];
    groups.forEach((g, i) => { if (g.d.lengthSq()) { g.d.set(0, 0, 0); touched.push(i); } });
    for (const [gi, x, y, z] of list || []) if (groups[gi]) { groups[gi].d.set(x, y, z); touched.push(gi); }
    write(touched); flush();
  }
  const getSculpt = () => groups.flatMap((g, i) => g.d.lengthSq() > 1e-10 ? [[i, +g.d.x.toFixed(4), +g.d.y.toFixed(4), +g.d.z.toFixed(4)]] : []);

  // Colours by material name — Main and Accent are the mech's paint.
  const mats = {}; for (const m of meshes) for (const mt of [].concat(m.material)) mats[mt.name] = mt;
  const original = Object.fromEntries(Object.entries(mats).map(([k, m]) => [k, '#' + m.color.getHexString()]));
  function setColors(c) { for (const [k, m] of Object.entries(mats)) m.color.set(c?.[k] || original[k]); }
  // The face: with face on, its own eyes are hidden — Peek puts a live, expressive face there.
  function setFace(on) { for (const m of meshes) if ([].concat(m.material).some((mt) => mt.name === 'Eye')) m.visible = !on; }

  // Standing on the floor whatever the legs: how far the lowest foot bone sits from where it
  // sits with no proportions, measured in the rest pose — so jumps in a clip still leave the ground.
  const feet = bones.filter((b) => /^(Foot|FootBack|LowerLeg)/.test(b.name));
  function lowest(root) {
    root.updateMatrixWorld(true); const v = new THREE.Vector3(); let m = Infinity;
    for (const b of feet) { b.getWorldPosition(v); m = Math.min(m, v.y); }
    return m;
  }
  // Pass the object that places the character (its parent): returns the lift that grounds it.
  function groundLift(placer) {
    const keep = new Map(factor), y0 = placer.position.y; placer.position.y = 0;
    factor.clear(); restore(); shape(); const neutral = lowest(placer);
    keep.forEach((v, k) => factor.set(k, v)); restore(); shape(); const now = lowest(placer);
    placer.position.y = y0; restore(); shape();
    return neutral - now;
  }
  function apply(s) { setProps(s.prop || {}); setSculpt(s.sculpt); setColors(s.colors); setFace(s.face !== false); restore(); shape(); }
  apply(state);
  return { gltf, scene, meshes, bones, groups, animations: gltf.animations, original, restore, shape, setProps, setSculpt, getSculpt, setColors, setFace, write, flush, apply, groundLift };
}

// A state into a link and back: JSON, gzipped, base64url.
export async function pack(state) {
  const gz = new Blob([JSON.stringify(state)]).stream().pipeThrough(new CompressionStream('gzip'));
  const bytes = new Uint8Array(await new Response(gz).arrayBuffer());
  let s = ''; for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}
export async function unpack(s) {
  try {
    const bin = atob(s.replace(/-/g, '+').replace(/_/g, '/')), bytes = Uint8Array.from(bin, (c) => c.charCodeAt(0));
    const text = await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
    return JSON.parse(text);
  } catch { return null; }
}
