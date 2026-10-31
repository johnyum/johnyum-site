// The door to johnyum.com — every build behind one knock (user's call, 2026-10-29,
// after the Airbnb handoff: the live demos go private; the password is given in person).
// Server-side gate: Vercel Edge Middleware runs before every static asset and every
// /api call on this project — including the /trips and /api rewrites to the Trips
// project — so view-source can't skip it and the AI keys can't be hit anonymously.
// The old client-side KnockKnock curtain on the work pile stays; this stands in front.
// The Trips repo carries this same file so its direct .vercel.app URL is locked too —
// same cookie, so one knock on johnyum.com opens the proxied /trips as well.
var PASSWORD = 'KnockKnock';            // exact case — same word as the pile curtain
var COOKIE = 'knock';
var TOKEN = 'kk-2026-10';               // bump this to re-lock every browser at once

export var config = { matcher: '/:path*' };

export default async function middleware(req) {
  var url = new URL(req.url);
  var jar = (req.headers.get('cookie') || '').split(/;\s*/);
  if (jar.indexOf(COOKIE + '=' + TOKEN) >= 0) return;          // unlocked — pass through
  // Open to everyone (John, 2026-10-30): /monsters (Fuzzball) and its Meshy route. Building
  // still takes the Monsters passcode in api/monsters.py, so credits can't be spent anonymously.
  if (/^\/monsters(\/|$)/.test(url.pathname) || url.pathname === '/api/monsters') return;
  if (url.pathname === '/__knock' && req.method === 'POST') {
    var form = new URLSearchParams(await req.text());
    var next = form.get('next') || '/';
    if (!/^\/(?!\/)/.test(next)) next = '/';                   // same-site paths only
    if (form.get('p') === PASSWORD) {
      return new Response(null, { status: 303, headers: {
        'set-cookie': COOKIE + '=' + TOKEN + '; Path=/; Max-Age=2592000; HttpOnly; Secure; SameSite=Lax',
        'location': next
      } });
    }
    return door(next, true);
  }
  return door(url.pathname + url.search, false);
}

function door(next, wrong) {
  var esc = next.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');
  var html = '<!doctype html><html><head><meta charset="utf-8">'
    + '<meta name="viewport" content="width=device-width, initial-scale=1">'
    + '<meta name="robots" content="noindex">'
    + '<title>John Yum</title><style>'
    + 'html,body{height:100%;margin:0}'
    + 'body{display:flex;align-items:center;justify-content:center;background:#FFFFFF;'
    + 'font:16px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#222222}'
    + 'form{text-align:center}'
    + 'input{width:240px;padding:8px 2px;border:0;border-bottom:2px solid #222222;'
    + 'border-radius:0;outline:none;background:transparent;font:inherit;text-align:center;color:inherit}'
    + 'input::placeholder{color:#BBBBBB}'
    + (wrong ? 'form{animation:knockshake .4s ease}'
             + '@keyframes knockshake{0%,100%{transform:translateX(0)}'
             + '20%,60%{transform:translateX(-8px)}40%,80%{transform:translateX(8px)}}' : '')
    + '</style></head><body>'
    + '<form method="POST" action="/__knock">'
    + '<input type="password" name="p" placeholder="Knock knock" autofocus autocomplete="off">'
    + '<input type="hidden" name="next" value="' + esc + '">'
    + '</form></body></html>';
  return new Response(html, { status: 401, headers: {
    'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store'
  } });
}
