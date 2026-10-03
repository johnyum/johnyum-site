// Capture a live page for a slide, at 2x, with any cookie dialog taken off first (John, 2026-10-03 — 09d03's article).
//   export PATH="$HOME/.local/node/bin:$PATH"; node preso/tools/capture-page.mjs <url> <out.png> <css-width> <css-height>
import { spawn } from 'node:child_process';
import { writeFileSync } from 'node:fs';
const [,, url, out, W, H] = process.argv;
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new','--hide-scrollbars','--remote-debugging-port=9333','--user-data-dir=' + process.env.TMPDIR + '/capchrome', '--window-size=' + W + ',' + H, 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
let ws;
for (let i = 0; i < 40; i++) { try { const l = await (await fetch('http://127.0.0.1:9333/json')).json(); const pg = l.find(t => t.type === 'page'); if (pg) { ws = new WebSocket(pg.webSocketDebuggerUrl); break; } } catch {} await sleep(250); }
await new Promise(r => ws.onopen = r);
let id = 0; const pend = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Emulation.setDeviceMetricsOverride', { width: +W, height: +H, deviceScaleFactor: 2, mobile: false });
await send('Network.setUserAgentOverride', { userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36' });
await send('Page.enable');
await send('Page.navigate', { url });
await sleep(9000);
const r = await send('Runtime.evaluate', { returnByValue: true, expression: `(() => {
  const hits = [...document.querySelectorAll('div,section,aside')].filter(e => /Help us improve your experience/.test(e.textContent) && e.querySelector('button'));
  const root = hits.sort((a,b) => b.textContent.length - a.textContent.length)[0];
  let n = 0;
  // remove the smallest container that is fixed-position and holds the banner text
  let el = hits.sort((a,b)=>a.textContent.length-b.textContent.length)[0];
  while (el && getComputedStyle(el).position !== 'fixed') el = el.parentElement;
  if (el) { el.remove(); n++; }
  document.documentElement.style.overflow = ''; document.body.style.overflow = '';
  window.scrollTo(0, 0);
  return n;
})()` });
console.log('removed', JSON.stringify(r.result && r.result.result));
await sleep(1500);
const shot = await send('Page.captureScreenshot', { format: 'png' });
writeFileSync(out, Buffer.from(shot.result.data, 'base64'));
chrome.kill();
process.exit(0);
