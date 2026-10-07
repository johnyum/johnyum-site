// Meshy's files on johnyum.com, shared by Monsters and Peek.
//
// Meshy's files send no CORS header, so the page can't fetch them itself: they come
// through /api/monsters?p=asset in slices (a Vercel response stops at 4.5MB). Each
// slice is 2MB, retried on its own, a few at a time — one dropped slice used to fail
// the whole model, and with it the build.
//
// Every file is then kept in this browser (IndexedDB, keyed by the file's path, as
// serve.py's cache is keyed on the Mac). Monsters puts each one there as it loads it,
// so Peek opens a fresh monster from here instantly instead of pulling ~190MB back
// through the function, and it still opens after Meshy deletes the files (3 days).

const DB = 'monsters-files', STORE = 'files';
const SLICE = 2 * 1024 * 1024, TRIES = 4, AT_ONCE = 4;

const keyOf = (url) => { try { return new URL(url).pathname; } catch { return url; } };
let opening = null;
function db() {
  opening ??= new Promise((res, rej) => {
    const r = indexedDB.open(DB, 1);
    r.onupgradeneeded = () => r.result.createObjectStore(STORE);
    r.onsuccess = () => res(r.result);
    r.onerror = () => rej(r.error);
  });
  return opening;
}
export async function getFile(url) {
  try {
    const d = await db();
    return await new Promise((res) => {
      const q = d.transaction(STORE).objectStore(STORE).get(keyOf(url));
      q.onsuccess = () => res(q.result || null); q.onerror = () => res(null);
    });
  } catch { return null; }
}
export async function putFile(url, buf) {
  try {
    const d = await db();
    await new Promise((res) => {
      const t = d.transaction(STORE, 'readwrite'); t.objectStore(STORE).put(buf, keyOf(url));
      t.oncomplete = t.onerror = t.onabort = res;
    });
  } catch {}
}

const nap = (ms) => new Promise((r) => setTimeout(r, ms));

// A Meshy file through the hosted function: from this browser's copy when there is one.
export async function hostedBytes(url, pass) {
  const kept = await getFile(url);
  if (kept) return kept;
  const slice = async (start) => {
    let last = null;
    for (let i = 0; i < TRIES; i++) {
      if (i) await nap(600 * 2 ** i);
      let r;
      try {
        r = await fetch(`/api/monsters?p=asset&url=${encodeURIComponent(url)}&start=${start}&end=${start + SLICE - 1}`,
                        { headers: { 'X-Monsters-Pass': pass } });
      } catch (e) { last = e; continue; }
      if (r.status === 401) throw new Error('unlock Monsters with the passcode first');
      if (r.ok) return { buf: new Uint8Array(await r.arrayBuffer()), total: +r.headers.get('X-Total-Size') };
      last = new Error(`the model's download stopped (${r.status})`);
    }
    throw new Error(`${last?.message || 'the model wouldn\'t download'} — or Meshy's link has expired`);
  };
  const first = await slice(0);
  const out = new Uint8Array(first.total || first.buf.length); out.set(first.buf);
  const starts = []; for (let at = first.buf.length; at < out.length; at += SLICE) starts.push(at);
  await Promise.all(Array.from({ length: AT_ONCE }, async () => {
    for (let at; (at = starts.shift()) !== undefined;) out.set((await slice(at)).buf, at);
  }));
  putFile(url, out.buffer);
  return out.buffer;
}
