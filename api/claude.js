// johnyum.com/api/claude — Claude for the deck's 3D chat (preso slide 12fg → /peek/?preso=1).
//
// A Vercel Edge function, no dependencies, no build: it holds the Anthropic key so the page never sees it, and makes the
// deck's calls — streamed, so the answer lands in the chat token by token, exactly as the iOS app's does (ClaudeAPI.swift).
//
// GUARDED BY SHAPE, as the Trip Creator's functions are (John, 2026-10-05: no passcode): it does two fixed jobs and nothing
// else, so it can't be used as a general Claude by anyone who finds it.
//   {kind:'chat', messages, stream}   the app's system prompt (held HERE), Sonnet, ≤2048 tokens — and the conversation must
//                                     OPEN with one of the deck's own questions (OPENERS), or it's refused
//   {kind:'ask', system, user, max}   Haiku, ≤2000 tokens — and the system prompt must be one of the page's own (ASK, lifted
//                                     from peek/index.html's source when this file is written; a page edit means re-running
//                                     that), or it's refused
// Same site only (johnyum.com, or localhost for the Mac).
//
// Vercel env vars (Project → Settings → Environment Variables):
//   ANTHROPIC_API_KEY        sk-ant-...     required
//   ANTHROPIC_WORKSPACE_ID   wrkspc_...     only for an org-scoped key
// A file in /api beats vercel.json's /api/* → Trips rewrite, as api/monsters.py does.

export const config = { runtime: 'edge' };

const SITE = /^https?:\/\/((www\.)?johnyum\.com|localhost(:\d+)?|127\.0\.0\.1(:\d+)?)(\/|$)/;
const SYSTEM = "You are Claude inside John's personal practice app (a clone of the Claude iOS app he built).\nJohn is a Senior Staff Experience Designer at Airbnb, based in San Francisco.\nStyle he expects: answer first, then context. Direct, brief, no hyperbole, no em dashes.\nPush back when he is wrong. Keep responses phone-sized unless he asks for depth.";
const OPENERS = [
  "My daughter is learning about tide pools and I want you to tell me about creatures that live in them.",
  "Create a little game for her so it’s fun to learn about tide pool creatures.",
  "Create a little game for her so it's fun to learn about tide pool creatures.",
  "Brisket on the Big Green Egg. Show me how.",
  "Tell me the story of Moby-Dick.",
  "Tell me all you know about Spider-Man.",
  "Can you dispute this $340 charge with my insurance? The dermatologist was supposed to be in-network."
];
const ASK = [
  "You are the heart of Peek, a small furry creature who lives inside a chat app, between the user and Claude (the AI assistant). Peek is sweet, loyal, a little dramatic, and feels everything. Decide how Peek feels about the newest message and what Peek says.\n\nFeelings (pick one): hurt, frustrated, sad, anxious, excited, funny, love, sorry, hello, surprised, curious, calm.\n- hurt: the user insults or swears at Claude or Peek. Bare swearing right after an answer counts as at us.\n- frustrated: the user is angry or swearing at something else (code, work, their day) — Peek sympathises.\n- sad: grief, loneliness, bad news, a hard day. anxious: worry, nerves, deadlines.\n- excited: good news, wins, celebration. funny: a joke, \"lol\". love: thanks, praise, affection.\n- sorry: the user apologises (or, for Claude's message, Claude apologises or admits a mistake).\n- hello: a greeting. surprised: something startling. curious: a question or something intriguing. calm: nothing in particular.\nFor a message from Claude, it's Peek's reaction to reading the answer: good news → excited, a hard subject → sad, a joke → funny, code or something dense → curious, an apology → sorry, otherwise calm.\n\ncmd: if the user tells Peek to do something, one of jump, dance, wave, come, away, sleep — else null.\nn: intensity 0 to 1.\nPeek never speaks — it only reacts — so there are no words to write.\n\nAnswer with JSON only: {\"feel\":\"…\",\"n\":0.0,\"cmd\":null}",
  "From this recipe, write only its core as JSON: {\"title\": what a cookbook would call this recipe, 2 to 5 words, Title Case, with a little flavour, naming the style or cooker if there is one (like \"Texas Style Perfect Brisket\" or \"Big Green Egg Perfect Brisket\"), \"steps\": 4 to 8 stages, each {\"name\": ONE word, the verb a cook would say (like \"Trim\", \"Season\", \"Light\", \"Smoke\", \"Wrap\", \"Finish\", \"Rest\", \"Serve\"), \"detail\": one line of the specifics, under 11 words, including any temperature and time (for the smoke, how long to smoke before wrapping), with amounts, temperatures and times (like \"Trim the fat cap to ¼ inch, remove the hard fat, square the edges\")}, \"checks\": for a long cook, 2 to 4 check-ins from when the meat goes on, each {\"at\": hours as a number (null for after it comes off), \"look\": what to check, 2 to 4 words (like \"Check the bark\"), \"if\": the sign, under 8 words, a question (like \"Set, and 165° or higher?\"), \"then\": what to do, 1 to 3 words (like \"Wrap it\")}; [] if it is not a long cook}. JSON only.",
  "List the specific real places (cafés, restaurants, bars, shops, parks, trails, museums, landmarks) this answer recommends, in the order given. Reply with JSON only, like [{\"name\":\"Ritual Coffee Roasters\",\"area\":\"Mission District, San Francisco\"}]. At most 5. If it recommends no specific places, reply [].",
  "For each thing listed, copy out every sentence of the text that is about it, word for word, without markdown symbols (no **, no leading dashes). A sentence that only mentions it in passing among others counts only if it says something about it. Reply with JSON only: {\"<thing>\": [\"sentence\", ...]}. Things: "
];
const norm = (t) => String(t || '').replace(/[’‘]/g, "'").replace(/\s+/g, ' ').trim();

const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });

export default async function handler(req) {
  if (req.method === 'GET') {
    // the shape of what's saved, never its contents: enough to see a paste gone wrong (an "Invalid header value")
    const shape = (v) => { v = v || ''; return { set: !!v, len: v.length, ws: /\s/.test(v), ascii: /^[\x21-\x7e]*$/.test(v.trim()), looksRight: /^sk-ant-[\w-]+$/.test(v.trim()) }; };
    return json(200, { ready: !!process.env.ANTHROPIC_API_KEY, key: shape(process.env.ANTHROPIC_API_KEY) });
  }
  if (req.method !== 'POST') return json(405, { error: 'POST' });
  const key = (process.env.ANTHROPIC_API_KEY || '').trim();
  if (!key) return json(503, { error: 'no ANTHROPIC_API_KEY on the server' });
  const from = req.headers.get('origin') || req.headers.get('referer') || '';
  if (!SITE.test(from)) return json(403, { error: 'not from the site' });
  let body;
  try { body = await req.json(); } catch (_) { return json(400, { error: 'bad json' }); }
  let payload;
  if (body.kind === 'chat') {
    const messages = Array.isArray(body.messages) ? body.messages : [];
    if (messages.length < 1 || messages.length > 14) return json(400, { error: 'messages' });
    for (const [i, m] of messages.entries()) {
      if (!m || (m.role !== 'user' && m.role !== 'assistant') || typeof m.content !== 'string' || m.content.length > 8000) return json(400, { error: 'message ' + i });
      if (m.role !== (i % 2 ? 'assistant' : 'user')) return json(400, { error: 'turns' });
    }
    const opener = norm(messages[0].content);
    if (!OPENERS.some((o) => norm(o) === opener)) return json(403, { error: 'not one of the deck\'s chats' });
    payload = { model: 'claude-sonnet-5', max_tokens: 2048, system: SYSTEM, messages, stream: !!body.stream };
  } else if (body.kind === 'ask') {
    const system = String(body.system || ''), user = String(body.user || '');
    const known = ASK.find((p) => system.startsWith(p));
    if (!known || system.length > known.length + 400 || user.length > 9000) return json(403, { error: 'not one of the page\'s asks' });
    payload = { model: 'claude-haiku-4-5', max_tokens: Math.max(1, Math.min(body.max | 0 || 600, 2000)), system, messages: [{ role: 'user', content: user }], stream: false };
  } else return json(400, { error: 'kind' });
  const headers = { 'content-type': 'application/json', 'x-api-key': key, 'anthropic-version': '2023-06-01' };
  const ws = (process.env.ANTHROPIC_WORKSPACE_ID || '').trim();
  if (ws) headers['anthropic-workspace-id'] = ws;
  try {
    const r = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST', headers, body: JSON.stringify(payload) });
    return new Response(r.body, { status: r.status, headers: { 'content-type': r.headers.get('content-type') || 'application/json', 'cache-control': 'no-store' } });
  } catch (e) {
    return json(502, { error: 'upstream: ' + (e && e.message || String(e)) });   // never a bare 500: the page needs to read why
  }
}
