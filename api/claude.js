// johnyum.com/api/claude — Claude for the deck's 3D chat (preso slide 12fg → /peek/?preso=1).
//
// A Vercel Edge function, no dependencies, no build: it holds the Anthropic key so the page never sees it, and
// passes a Messages call straight through — streamed, so the answer lands in the chat token by token, exactly as
// the iOS app's does (ClaudeAPI.swift). One route, POST /api/claude, the body a Messages request (model, system,
// messages, max_tokens, stream); the response is Anthropic's own (SSE when streamed).
//
// Vercel env vars (Project → Settings → Environment Variables):
//   ANTHROPIC_API_KEY        sk-ant-...                      required
//   ANTHROPIC_WORKSPACE_ID   wrkspc_... (an org-scoped key)   optional
//   CLAUDE_PASSCODE          whatever the page sends          optional — set, every call needs it (X-Claude-Pass)
//
// Guards: same site only (johnyum.com, or localhost for the Mac), a short list of models, max_tokens capped.
// A file in /api beats vercel.json's /api/* → Trips rewrite, as api/monsters.py does.

export const config = { runtime: 'edge' };

const MODELS = new Set(['claude-sonnet-5', 'claude-sonnet-5-5', 'claude-opus-5-5', 'claude-haiku-4-5', 'claude-haiku-4-5-20251001']);
const SITE = /^https?:\/\/((www\.)?johnyum\.com|localhost(:\d+)?|127\.0\.0\.1(:\d+)?)(\/|$)/;

const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });

export default async function handler(req) {
  if (req.method === 'GET') return json(200, { ready: !!process.env.ANTHROPIC_API_KEY, gated: !!process.env.CLAUDE_PASSCODE });
  if (req.method !== 'POST') return json(405, { error: 'POST' });
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return json(503, { error: 'no ANTHROPIC_API_KEY on the server' });
  const from = req.headers.get('origin') || req.headers.get('referer') || '';
  if (!SITE.test(from)) return json(403, { error: 'not from the site' });
  const pass = process.env.CLAUDE_PASSCODE;
  if (pass && req.headers.get('x-claude-pass') !== pass) return json(401, { error: 'passcode' });
  let body;
  try { body = await req.json(); } catch (_) { return json(400, { error: 'bad json' }); }
  const payload = {
    model: MODELS.has(body.model) ? body.model : 'claude-sonnet-5',
    max_tokens: Math.max(1, Math.min(body.max_tokens | 0 || 1024, 4096)),
    messages: Array.isArray(body.messages) ? body.messages : [],
    stream: !!body.stream,
  };
  if (typeof body.system === 'string' && body.system) payload.system = body.system;
  if (body.temperature != null) payload.temperature = body.temperature;
  const headers = { 'content-type': 'application/json', 'x-api-key': key, 'anthropic-version': '2023-06-01' };
  if (process.env.ANTHROPIC_WORKSPACE_ID) headers['anthropic-workspace-id'] = process.env.ANTHROPIC_WORKSPACE_ID;
  const r = await fetch('https://api.anthropic.com/v1/messages', { method: 'POST', headers, body: JSON.stringify(payload) });
  return new Response(r.body, { status: r.status, headers: { 'content-type': r.headers.get('content-type') || 'application/json', 'cache-control': 'no-store' } });
}
