// johnyum.com/api/unsplash — real photographs for the Explore prototype's listings, from Unsplash.
//
// A Vercel Edge function, no dependencies. It holds the Unsplash access key (John put it in Vercel, 2026-10-07 — there is no
// copy on the Mac, so the photos are pulled THROUGH this, at build time, into explore/assets/img). Guarded by shape like
// api/claude.js: one fixed job — a search, ten results at most — and nothing else.
//   GET /api/unsplash?q=faroe+islands+turf+house&n=9
//   → [{ url, w, h, name, link, download }]   (`download` is the download_location Unsplash asks to be pinged when a photo is used)
//   GET /api/unsplash  → readiness and the key's shape, never its contents
//
// Vercel env var (Project → Settings → Environment Variables): UNSPLASH_ACCESS_KEY (or UNSPLASH_KEY).
// A file in /api beats vercel.json's /api/* → Trips rewrite, as api/claude.js does.

export const config = { runtime: 'edge' };

export default async function handler(req) {
  const key = process.env.UNSPLASH_ACCESS_KEY || process.env.UNSPLASH_KEY || '';
  const url = new URL(req.url);
  const q = (url.searchParams.get('q') || '').trim().slice(0, 80);
  const json = (o, status) => new Response(JSON.stringify(o), { status: status || 200, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
  if (!q) return json({ ready: !!key, key: key ? key.slice(0, 4) + '…' + key.length : null });
  if (!key) return json({ error: 'no key' }, 503);
  const n = Math.max(1, Math.min(10, +url.searchParams.get('n') || 9));
  const page = Math.max(1, Math.min(5, +url.searchParams.get('page') || 1));
  const r = await fetch('https://api.unsplash.com/search/photos?' + new URLSearchParams({ query: q, per_page: String(n), page: String(page), orientation: 'landscape', content_filter: 'high' }),
    { headers: { Authorization: 'Client-ID ' + key, 'Accept-Version': 'v1' } });
  if (!r.ok) return json({ error: 'unsplash ' + r.status }, 502);
  const d = await r.json();
  return json((d.results || []).map(p => ({ url: p.urls.regular, w: p.width, h: p.height, name: p.user && p.user.name, link: p.links && p.links.html, download: p.links && p.links.download_location, alt: p.alt_description })));
}
