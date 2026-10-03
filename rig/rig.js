// A rigged character you can reshape — shared by rig/ (where you sculpt it) and peek/
// (where it lives in a chat). One copy, so a character looks the same in both.
//
// Three kinds of change, all kept through every animation:
//   proportions  bone scales (a bigger head, longer ears), applied after the animation
//                each frame, each bone's own factor divided out of its children so a
//                bigger chest doesn't also mean bigger arms
//   sculpt       offsets on the mesh in its rest pose. Skinning carries them into every
//                pose. Offsets are kept per *position* (a weld group), not per vertex —
//                the meshes split vertices at seams, and a brush would tear them apart.
//   fluff        fur: shells of the skinned mesh, each pushed out along the skinned normal
//                and cut to strands by a 3D hash of the rest position — so the fur rides
//                the skeleton, and trails the motion when the page feeds it a drag.
//
//   expression   its *own* eyes, moved: blink, look (the pupil shifts within the white),
//                widen, squint, close — every mood is the character's own face, never a
//                face pasted on from somewhere else.
//
// A character is a small JSON state: { v, model, prop, colors, fur, sculpt }, the sculpt as
// [group, dx, dy, dz] per moved group. pack()/unpack() put it in a link.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { FBXLoader } from 'three/addons/loaders/FBXLoader.js';

// Quaternius, CC0 (rig/models/LICENSE.txt): critters from the Ultimate Monsters Bundle,
// mechs from the Animated Mech Pack.
export const MODELS = [
  { name: 'Bunny', file: 'Bunny.fbx', fur: .55 }, { name: 'Cat', file: 'Cat.fbx', fur: .5 },
  { name: 'Yeti', file: 'Yeti.fbx', fur: .7 }, { name: 'Pink Blob', file: 'PinkBlob.fbx', fur: .35 },
  { name: 'Mushnub', file: 'Mushnub.fbx', fur: 0 }, { name: 'Birb', file: 'Birb.fbx', fur: .45 },
  { name: 'Frog', file: 'Frog.fbx', fur: 0 }, { name: 'Cactoro', file: 'Cactoro.fbx', fur: 0 },
  { name: 'Green Blob', file: 'GreenBlob.fbx', fur: .3 },
  { name: 'Mike', file: 'Mike.gltf', fur: 0 }, { name: 'Stan', file: 'Stan.gltf', fur: 0 },
  { name: 'George', file: 'George.gltf', fur: 0 }, { name: 'Leela', file: 'Leela.gltf', fur: 0 },
];
const modelOf = (name) => MODELS.find((m) => m.name === name) || MODELS[0];
// Bone names as three.js gives them: it strips the dots, so a file's "UpperArm.L" is "UpperArmL".
export const PROPS = {
  head:  { label: 'Head',   bones: [/^Head$/], axes: 'xyz' },
  body:  { label: 'Chubby', bones: [/^Body$/], axes: 'xz' },
  chest: { label: 'Chest',  bones: [/^Chest$/], axes: 'xz' },
  ears:  { label: 'Ears',   bones: [/^Ear\d[._]?[LR]$/], axes: 'y' },
  arms:  { label: 'Arms',   bones: [/^UpperArm[._]?[LR]$/, /^LowerArm[._]?[LR]$/], axes: 'y' },
  hands: { label: 'Hands',  bones: [/^Palm[A-Z][._]?[LR]$/, /^(Index|Middle|Pinky|Ring|Thumb)1[._]?[LR]$/], axes: 'xyz' },
  legs:  { label: 'Legs',   bones: [/^UpperLeg[._]?[LR]$/, /^MidLeg[._]?[LR]$/, /^LowerLeg[._]?[LR]$/], axes: 'y' },
  feet:  { label: 'Feet',   bones: [/^Foot[._]?[LR]$/, /^FootBack[._]?[LR]$/], axes: 'xyz' },
};
export const blankState = (model = 'Bunny') => ({ v: 2, model, prop: {}, colors: {}, fur: modelOf(model).fur, sculpt: [] });
// Which paint a swatch row sets: the mechs say Main / Accent; the critters say X_Main / X_Secondary.
const PAINT = { Main: /(^|_)Main$/, Accent: /(^Accent$|_Secondary$)/ };
const isEye = (m) => /^Eye/i.test(m?.name || '');
const furs = (m) => /(^|_)(Main|Secondary)$|^Accent$|^Ears$/.test(m?.name || '');

export async function loadRig(state, base = new URL('./models/', import.meta.url).href) {
  const M = modelOf(state.model), fbx = M.file.endsWith('.fbx');
  let scene, animations;
  if (fbx) {
    scene = await new FBXLoader().loadAsync(base + M.file); animations = scene.animations;
    for (const a of animations) a.name = a.name.replace(/^.*\|/, '');   // "CharacterArmature|Walk" → "Walk"
  } else { const g = await new GLTFLoader().loadAsync(base + M.file); scene = g.scene; animations = g.animations; }
  const meshes = [];
  scene.traverse((o) => { if (o.isSkinnedMesh) { meshes.push(o); o.frustumCulled = false; } });
  // FBX comes with Phong materials; standard ones take the room light the same way the mechs do.
  if (fbx) for (const m of meshes) {
    const swap = (mt) => new THREE.MeshStandardMaterial({ name: mt.name, color: mt.color, roughness: isEye(mt) ? .25 : .75, metalness: 0 });
    m.material = Array.isArray(m.material) ? m.material.map(swap) : swap(m.material);
  }
  const bones = meshes[0].skeleton.bones;
  const rest = bones.map((b) => ({ p: b.position.clone(), q: b.quaternion.clone(), s: b.scale.clone() }));
  const box = new THREE.Box3(); for (const m of meshes) { m.geometry.computeBoundingBox(); box.union(m.geometry.boundingBox); }
  const size = box.getSize(new THREE.Vector3()).y || 1;

  // Weld groups: every vertex at one position, across all the parts, moves as one.
  const key = (x, y, z) => `${Math.round(x / size * 1e5)},${Math.round(y / size * 1e5)},${Math.round(z / size * 1e5)}`;
  const at = new Map(), groups = [];
  const tri = (geo, t) => geo.index ? [geo.index.getX(t), geo.index.getX(t + 1), geo.index.getX(t + 2)] : [t, t + 1, t + 2];
  meshes.forEach((m, mi) => {
    const geo = m.geometry, pos = geo.attributes.position, nor = geo.attributes.normal, gOf = new Int32Array(pos.count);
    for (let i = 0; i < pos.count; i++) {
      const k = key(pos.getX(i), pos.getY(i), pos.getZ(i));
      let g = at.get(k);
      if (g == null) { g = groups.length; at.set(k, g); groups.push({ b: new THREE.Vector3(pos.getX(i), pos.getY(i), pos.getZ(i)), d: new THREE.Vector3(), n: new THREE.Vector3(), m: [], nb: new Set() }); }
      groups[g].m.push(mi, i); if (nor) groups[g].n.add(new THREE.Vector3(nor.getX(i), nor.getY(i), nor.getZ(i))); gOf[i] = g;
    }
    const n = geo.index ? geo.index.count : pos.count;
    for (let t = 0; t < n; t += 3) {
      const [a, b, c] = tri(geo, t).map((i) => gOf[i]);
      groups[a].nb.add(b).add(c); groups[b].nb.add(a).add(c); groups[c].nb.add(a).add(b);
    }
    m.userData.gOf = gOf;
    // Hard-edged (indexed, split at its edges) keeps its facets; smooth meshes stay smooth.
    m.userData.smooth = !geo.index;
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
  const hasProp = (k) => bones.some((b) => PROPS[k].bones.some((r) => r.test(b.name)));
  // Every bone back to rest — the animation then sets the ones it moves.
  function restore() { bones.forEach((b, i) => { b.position.copy(rest[i].p); b.quaternion.copy(rest[i].q); b.scale.copy(rest[i].s); }); }
  // After the animation: each bone's factor in, its parent's divided out.
  function shape() { for (const b of bones) { const f = factor.get(b), pf = factor.get(b.parent); if (f) b.scale.multiply(f); if (pf) b.scale.divide(pf); } }

  // Write moved groups back into the meshes.
  const dirty = new Set();
  function write(list) {
    for (const gi of list) { const g = groups[gi];
      for (let j = 0; j < g.m.length; j += 2) { const m = meshes[g.m[j]]; m.geometry.attributes.position.setXYZ(g.m[j + 1], g.b.x + g.d.x, g.b.y + g.d.y, g.b.z + g.d.z); dirty.add(m); } }
  }
  const fa = new THREE.Vector3(), fb = new THREE.Vector3(), fc = new THREE.Vector3();
  function flush() {
    for (const m of dirty) {
      const geo = m.geometry; geo.attributes.position.needsUpdate = true;
      if (!m.userData.smooth) geo.computeVertexNormals();
      else {
        // Smooth normals across the welds: every face's normal into its corners' groups.
        const pos = geo.attributes.position, nor = geo.attributes.normal, acc = new Map(), gOf = m.userData.gOf;
        for (let t = 0; t < pos.count; t += 3) {
          fa.fromBufferAttribute(pos, t); fb.fromBufferAttribute(pos, t + 1); fc.fromBufferAttribute(pos, t + 2);
          const fn = fc.sub(fb).cross(fa.sub(fb));
          for (let k = 0; k < 3; k++) { const g = gOf[t + k]; (acc.get(g) || acc.set(g, new THREE.Vector3()).get(g)).add(fn); }
        }
        for (let i = 0; i < pos.count; i++) { const v = acc.get(gOf[i]).normalize(); nor.setXYZ(i, v.x, v.y, v.z); }
        nor.needsUpdate = true;
      }
      geo.computeBoundingSphere();
    }
    dirty.clear();
  }
  function setSculpt(list) {
    const touched = [];
    groups.forEach((g, i) => { if (g.d.lengthSq()) { g.d.set(0, 0, 0); touched.push(i); } });
    for (const [gi, x, y, z] of list || []) if (groups[gi]) { groups[gi].d.set(x, y, z); touched.push(gi); }
    write(touched); flush();
  }
  const getSculpt = () => groups.flatMap((g, i) => g.d.lengthSq() > 1e-12 * size * size ? [[i, ...g.d.toArray().map((v) => +v.toPrecision(5))]] : []);

  // Paint: Main and Accent, whatever the file calls them.
  const mats = new Map(); for (const m of meshes) for (const mt of [].concat(m.material)) mats.set(mt.name, mt);
  const paintMat = (slot) => [...mats.values()].find((mt) => PAINT[slot].test(mt.name));
  const original = Object.fromEntries(['Main', 'Accent'].map((s) => [s, paintMat(s) ? '#' + paintMat(s).color.getHexString() : null]));
  function setColors(c) { for (const s of ['Main', 'Accent']) { const mt = paintMat(s); if (mt) mt.color.set(c?.[s] || original[s]); } }
  // ── its own eyes ──
  // Each eye: the vertices of its white and its pupil (critters: Eye_White / Eye_Black; the
  // mechs have one "Eye" part, which is all white), its rest centre and size. Left and right
  // by which side of the middle they're on.
  const eyes = (() => {
    const seen = new Set(), sides = { [-1]: { white: [], pupil: [] }, 1: { white: [], pupil: [] } };
    for (const m of meshes) {
      const list = [].concat(m.material), geo = m.geometry, n = geo.index ? geo.index.count : geo.attributes.position.count;
      const ranges = geo.groups.length ? geo.groups : [{ start: 0, count: n, materialIndex: 0 }];
      for (const r of ranges) {
        const mt = list[r.materialIndex ?? 0]; if (!isEye(mt)) continue;
        const pupil = /black|pupil/i.test(mt.name);
        for (let k = r.start; k < r.start + r.count; k++) {
          const i = geo.index ? geo.index.getX(k) : k, id = m.uuid + ':' + i; if (seen.has(id)) continue; seen.add(id);
          const x = geo.attributes.position.getX(i);
          sides[x < 0 ? -1 : 1][pupil ? 'pupil' : 'white'].push([m, i]);
        }
      }
    }
    return Object.entries(sides).filter(([, e]) => e.white.length + e.pupil.length).map(([side, e]) => {
      const pts = [...e.white, ...e.pupil].map(([m, i]) => new THREE.Vector3().fromBufferAttribute(m.geometry.attributes.position, i));
      const c = pts.reduce((a, p) => a.add(p), new THREE.Vector3()).divideScalar(pts.length);
      const r = Math.max(...pts.map((p) => Math.hypot(p.x - c.x, p.y - c.y))) || size * .02;
      return { side: +side, ...e, c, r };
    });
  })();
  // Where it looks and how open its eyes are, written straight into the eye vertices (on top
  // of any sculpt). open: 1 normal, < 1 squinting or closed, > 1 wide. look: -1…1 each way.
  const eyeMeshes = new Set(eyes.flatMap((e) => [...e.white, ...e.pupil].map(([m]) => m)));
  function setEyes({ open = 1, lookX = 0, lookY = 0, lift = 0 } = {}) {
    for (const e of eyes) for (const [list, pupil] of [[e.white, false], [e.pupil, true]]) for (const [m, i] of list) {
      const g = groups[m.userData.gOf[i]], bx = g.b.x + g.d.x, by = g.b.y + g.d.y, bz = g.b.z + g.d.z;
      const y = e.c.y + e.r * lift + (by - e.c.y) * open + (pupil ? lookY * e.r * .32 * Math.min(1, open) : 0);
      m.geometry.attributes.position.setXYZ(i, bx + (pupil ? lookX * e.r * .38 : 0), y, bz);
    }
    for (const m of eyeMeshes) m.geometry.attributes.position.needsUpdate = true;
  }

  // Fluff: shells of each skinned mesh, sharing its geometry and skeleton.
  const SHELLS = 12;
  const fur = { drag: { value: new THREE.Vector2() }, droop: { value: size * .004 }, len: { value: 0 }, density: { value: 110 / size },
               bald: { value: [0, 1].map((i) => eyes[i] ? new THREE.Vector4(eyes[i].c.x, eyes[i].c.y, eyes[i].c.z, eyes[i].r) : new THREE.Vector4(0, -1e6, 0, 0)) } };
  const shells = [];
  function furMaterial(mt, k) {
    if (!furs(mt)) return new THREE.MeshBasicMaterial({ visible: false });
    return new THREE.ShaderMaterial({
      uniforms: { uShell: { value: k }, uColor: { value: mt.color }, uDrag: fur.drag, uDroop: fur.droop, uFur: fur.len, uDensity: fur.density, uBald: fur.bald },
      vertexShader: `
        #include <common>
        #include <skinning_pars_vertex>
        uniform float uShell, uFur, uDroop; uniform vec2 uDrag; uniform vec4 uBald[2]; varying vec3 vN, vRest;
        void main() {
          #include <skinbase_vertex>
          #include <begin_vertex>
          #include <beginnormal_vertex>
          #include <skinnormal_vertex>
          #include <skinning_vertex>
          vRest = position; vN = normalize(normalMatrix * objectNormal);
          // Short fur round the eyes, or it grows over them and they read as half-shut.
          float bald = 0.;
          for (int i = 0; i < 2; i++) bald = max(bald, 1. - smoothstep(uBald[i].w * 1.05, uBald[i].w * 2.1, distance(position, uBald[i].xyz)));
          vec4 mv = modelViewMatrix * vec4(transformed + normalize(objectNormal) * uFur * uShell * (1. - .92 * bald), 1.);
          float bend = uShell * uShell;
          mv.xy += uDrag * bend; mv.y -= uDroop * bend;
          gl_Position = projectionMatrix * mv;
        }`,
      fragmentShader: `
        uniform float uShell, uDensity; uniform vec3 uColor; varying vec3 vN, vRest;
        float hash(vec3 c) { return fract(sin(dot(c, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
        void main() {
          if (hash(floor(vRest * uDensity)) < uShell * .92 + .06) discard;   // strands thin toward their tips
          vec3 n = normalize(vN), L = normalize(vec3(.45, .75, .55));
          float dif = clamp(dot(n, L) * .55 + .45, 0., 1.), rim = pow(1. - clamp(n.z, 0., 1.), 2.5);
          vec3 c = mix(uColor * .62, uColor, uShell) * dif + mix(uColor, vec3(1.), .5) * rim * .3 * uShell;
          gl_FragColor = vec4(c, 1.);
          #include <tonemapping_fragment>
          #include <colorspace_fragment>
        }`,
    });
  }
  function setFur(amount) {
    fur.len.value = amount * size * .05;
    if (amount > 0 && !shells.length) for (const m of meshes) for (let i = 1; i <= SHELLS; i++) {
      const k = i / SHELLS, mat = Array.isArray(m.material) ? m.material.map((mt) => furMaterial(mt, k)) : furMaterial(m.material, k);
      const s = new THREE.SkinnedMesh(m.geometry, mat); s.bind(m.skeleton, m.bindMatrix); s.frustumCulled = false; s.renderOrder = i;
      m.parent.add(s); s.position.copy(m.position); s.quaternion.copy(m.quaternion); s.scale.copy(m.scale); shells.push(s);
    }
    for (const s of shells) s.visible = amount > 0;
  }

  function apply(s) { setProps(s.prop || {}); setSculpt(s.sculpt); setColors(s.colors); setFur(s.fur ?? 0); restore(); shape(); }

  // Standing on the floor whatever the legs: how far the lowest foot bone sits from where it
  // sits with no proportions, measured in the rest pose — so jumps in a clip still leave the ground.
  const feet = bones.filter((b) => /^(Foot|FootBack|LowerLeg)/.test(b.name));
  function lowest(root) {
    root.updateMatrixWorld(true); const v = new THREE.Vector3(); let m = Infinity;
    for (const b of (feet.length ? feet : bones)) { b.getWorldPosition(v); m = Math.min(m, v.y); }
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

  apply(state);
  return { scene, meshes, bones, groups, animations, original, size, fur, restore, shape, setProps, hasProp, setSculpt, getSculpt,
           setColors, setFur, setEyes, eyes, write, flush, apply, groundLift };
}

// Moods as the eyes alone — Peek and Rig Studio both use these.
export const MOODS = {
  happy:     { open: 1 },
  curious:   { open: 1.12 },
  thinking:  { open: .85, lookX: -.7, lookY: .8 },
  surprised: { open: 1.3 },
  love:      { open: .22, lift: .35 },    // scrunched up into happy crescents
  sleepy:    { open: .3, lift: -.25 },
  ugh:       { open: .38, lookY: -.2 },
  sad:       { open: .62, lift: -.3, lookY: -.45 },  // droopy, eyes down
};

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
