#!/usr/bin/env python3
"""Kept, the surface: build with Claude Code, and every turn is kept.

    python3 kept/serve.py                   -> http://localhost:5350/kept/

What this server does, all stdlib:

- Runs the real Claude Code in a pseudo-terminal and bridges it to the page
  (output over server-sent events, keys back over POST). Nothing about Claude
  Code changes; it is launched with two hooks, for this instance only:
  UserPromptSubmit (remember what was asked, and say if it was tried before)
  and Stop (keep what the turn made).
- Keeps each turn as a version without touching your branch, index or HEAD: the
  working tree is written to a throwaway index, committed with commit-tree, and
  pinned under refs/kept/<project>/<direction>. Plain git underneath, never in
  the way; `git log refs/kept/...` reads it.
- Serves any version straight out of git at /kept/v/<sha>/<path>, so the
  preview can show the page as it was, with no checkout.
- Shoots each new version's page with headless Chrome for the filmstrip.

State (directions made here, their versions, held or pushed) is in
kept/data/build.json; the directions read from history are kept/data/areas/.
"""
import base64, fcntl, functools, glob, json, mimetypes, os, pty, queue, re, select, signal
import struct, subprocess, sys, tempfile, termios, threading, time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, 'data')
STATE = os.path.join(DATA, 'build.json')
THUMBS = os.path.join(DATA, 'thumbs')
PORT = int(os.environ.get('PORT', '5350'))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CLAUDE = os.environ.get('KEPT_ENGINE', os.path.expanduser('~/.local/bin/claude'))

# A project is a set of folders in the repo and the page that shows it.
PROJECTS = [
    {'key': 'preso',   'name': 'The deck',            'paths': ['preso/'],                                  'page': 'preso/'},
    {'key': 'multi',   'name': 'Multi-host calendar', 'paths': ['multi/', 'multi2/', 'multical/', 'recurrence/'], 'page': 'multi/'},
    {'key': 'peek',    'name': 'Peek',                'paths': ['peek/', 'plush/', 'rig/', 'monsters/', 'api/'], 'page': 'peek/'},
    {'key': 'explore', 'name': 'Explore map',         'paths': ['explore/'],                                'page': 'explore/'},
    {'key': 'icons',   'name': 'Icon systems',        'paths': ['claude-icons/', 'playful/', 'icons/'],     'page': 'claude-icons/index.html'},
    {'key': 'site',    'name': 'johnyum.com',         'paths': ['index.html', 'img/', 'Website_Images/'],   'page': ''},
]
P = {p['key']: p for p in PROJECTS}
LOCK = threading.RLock()


def git(*a, env=None, check=True, inp=None):
    e = dict(os.environ, **(env or {}))
    r = subprocess.run(['git', *a], cwd=ROOT, capture_output=True, env=e, input=inp)
    if check and r.returncode:
        raise RuntimeError(r.stderr.decode()[-400:])
    return r.stdout


# ---------------------------------------------------------------- state

def load():
    try:
        s = json.load(open(STATE))
    except (OSError, ValueError):
        s = {}
    s.setdefault('directions', {})   # id -> {project, title, status, why, base, versions: [...]}
    s.setdefault('current', None)    # {project, direction}
    s.setdefault('history', {})      # history direction id -> extra versions built on it here
    return s


def save(s):
    os.makedirs(DATA, exist_ok=True)
    tmp = STATE + '.tmp'
    json.dump(s, open(tmp, 'w'), indent=1)
    os.replace(tmp, STATE)


S = load()
PENDING = {'prompt': None, 't': 0, 'done': 0}
NUDGE = {'text': None, 'direction': None, 't': 0}


def thumbs():
    try:
        return json.load(open(os.path.join(THUMBS, 'thumbs.json')))
    except (OSError, ValueError):
        return {}


def history():
    """The directions read from four months of history, by project."""
    out = {}
    raw = {}
    try:
        for c in json.load(open(os.path.join(DATA, 'raw.json')))['commits']:
            raw[c['sha']] = c
    except (OSError, ValueError):
        pass
    th = thumbs()
    for f in glob.glob(os.path.join(DATA, 'areas', '*.json')):
        a = json.load(open(f))
        for i, d in enumerate(a['directions']):
            vs = []
            for v in d['versions']:
                sha = v['sha'][:7]
                e, c = th.get(sha, {}), raw.get(sha, {})
                pic = (e.get('pics') or [{}])[0].get('src')
                vs.append({'sha': sha, 't': c.get('t', 0), 'note': v['note'], 'prompt': None,
                           'shot': pic or (e.get('shot') or {}).get('src'), 'page': (e.get('shot') or {}).get('url', '').lstrip('/'),
                           'from': 'history'})
            out.setdefault(a['area'], []).append({
                'id': f"h-{a['area']}-{i}", 'project': a['area'], 'title': d['title'], 'status': d['status'],
                'why': d['why'], 'quotes': d.get('quotes', []), 'confirmed': d.get('confirmed', False),
                'versions': vs, 'kind': 'history'})
    return out


def directions(project):
    """History directions with any versions built on them here, then the ones started here."""
    ds = history().get(project, [])
    for d in ds:
        d['versions'] = d['versions'] + S['history'].get(d['id'], [])
    for id_, d in S['directions'].items():
        if d['project'] == project:
            ds.append(dict(d, id=id_, kind='new'))
    return ds


def find(did):
    for d in directions(did.split('-')[1] if did.startswith('h-') else S['directions'].get(did, {}).get('project', '')):
        if d['id'] == did:
            return d
    return None


# ---------------------------------------------------------------- versions

def snapshot(project, did, prompt):
    """Write the working tree as a commit on refs/kept/<project>/<direction>. HEAD, index and branch untouched."""
    with LOCK:
        d = find(did)
        if not d:
            return None
        prev = d['versions'][-1]['sha'] if d['versions'] else None
        fd, idx = tempfile.mkstemp(prefix='kept-index-')
        os.close(fd)
        try:
            env = {'GIT_INDEX_FILE': idx}
            git('read-tree', 'HEAD', env=env)
            git('add', '-A', env=env)
            tree = git('write-tree', env=env).decode().strip()
        finally:
            os.remove(idx)
        if prev and git('rev-parse', f'{prev}^{{tree}}', check=False).decode().strip() == tree:
            return None  # the turn changed nothing: no new version
        parent = prev or git('rev-parse', 'HEAD').decode().strip()
        msg = (prompt or 'A turn').strip()[:2000]
        sha = git('commit-tree', tree, '-p', parent, '-m', msg).decode().strip()
        git('update-ref', f'refs/kept/{project}/{did}', sha)
        changed = [f for f in git('diff', '--name-only', parent, sha).decode().split('\n') if f][:40]
        v = {'sha': sha[:7], 'full': sha, 't': int(time.time()), 'prompt': msg, 'note': short(msg, 80),
             'files': changed, 'shot': None, 'page': page_for(project, changed), 'pushed': False, 'from': 'here'}
        if did.startswith('h-'):
            S['history'].setdefault(did, []).append(v)
        else:
            S['directions'][did]['versions'].append(v)
        save(S)
        threading.Thread(target=shoot, args=(did, v['sha'], v['page']), daemon=True).start()
        return v


def short(s, n):
    s = ' '.join(str(s).split())
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0] + '…'


def page_for(project, files):
    for f in files:
        m = re.match(r'preso/slides/([0-9a-z]+)\.html$', f)
        if m:
            return f'preso/slides/{m.group(1)}.html'
    for f in files:
        if f.endswith('index.html') and any(f.startswith(p) for p in P[project]['paths']):
            return f[:-len('index.html')]
    # Otherwise the page the turn touched, wherever it lives (Kept's own files aside).
    for f in files:
        if f.endswith('.html') and not f.startswith('kept/'):
            return f[:-len('index.html')] if f.endswith('/index.html') else f
    return P[project]['page']


def shoot(did, sha, page):
    os.makedirs(THUMBS, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        png = os.path.join(tmp, 's.png')
        subprocess.run([CHROME, '--headless=new', '--hide-scrollbars', '--mute-audio', f'--user-data-dir={tmp}/p',
                        '--window-size=1440,900', '--virtual-time-budget=6000', f'--screenshot={png}',
                        f'http://127.0.0.1:{PORT}/kept/v/{sha}/{page}'], capture_output=True, timeout=90)
        if not os.path.exists(png):
            return
        subprocess.run(['sips', '-Z', '720', '-s', 'format', 'jpeg', png, '--out', os.path.join(THUMBS, f'{sha}.jpg')],
                       capture_output=True)
    with LOCK:
        for vs in [d['versions'] for d in S['directions'].values()] + list(S['history'].values()):
            for v in vs:
                if v['sha'] == sha:
                    v['shot'] = f'{sha}.jpg'
        save(S)


def restore(sha, project):
    """Put a version's files for one project back in the working tree. What's there now is kept first."""
    with LOCK:
        cur = S.get('current') or {}
        if cur.get('direction'):
            snapshot(cur['project'], cur['direction'], 'Kept before going back to ' + sha)
        paths = [p.rstrip('/') for p in P[project]['paths']]
        existing = [p for p in paths if subprocess.run(['git', 'cat-file', '-e', f'{sha}:{p}'], cwd=ROOT).returncode == 0]
        if existing:
            git('restore', f'--source={sha}', '--worktree', '--', *existing)
        return existing


# ---------------------------------------------------------------- memory

STOP = set('''the a an and or but to of in on at for with from into onto that this these those it its is are was were be been
make makes made let lets want need just like more less some any all each every when then than so very really can could
should would will do does did done have has had get got put take give keep use using also only still even back over
under about after before there here what which who how why where you your me my we our them they he she his her i im
dont doesnt cant wont didnt isnt lets thing things stuff look looks looking way new one two three bit little big please now'''.split())


def words(s):
    return {w for w in re.findall(r"[a-z][a-z-]{3,}", str(s).lower().replace("'", '')) if w not in STOP}


def recall(project, prompt):
    """Specific or silent. A set-aside or paused direction in this project comes back only when the ask shares
    two rare words with it (each in at most three of the project's directions), one of them from its name.
    "white", "page", "kept" match half the history; a name word like "thermometer" or "pile" does not."""
    ask = words(prompt)
    if len(ask) < 2:
        return None
    ds = directions(project)
    text = {d['id']: words(' '.join([d['title'], d['why'], *d.get('quotes', []), *[v.get('note') or '' for v in d['versions']]])) for d in ds}
    df = {}
    for ws in text.values():
        for w in ws:
            df[w] = df.get(w, 0) + 1
    best = None
    for d in ds:
        if d['status'] not in ('set_aside', 'paused') or not d['versions']:
            continue
        rare = {w for w in ask & text[d['id']] if df.get(w, 0) <= 3}
        named = ask & words(d['title'])
        hit = rare | named
        if rare and named and len(hit) >= 2 and (not best or len(hit) > len(best[1])):
            best = (d, hit)
    if not best:
        return None
    d, hit = best
    when = time.strftime('%b %-d', time.localtime(max(v['t'] for v in d['versions']) or time.time()))
    q = f' He said: "{short(d["quotes"][0], 140)}"' if d.get('quotes') else ''
    return {'direction': d['id'], 'title': d['title'], 'words': sorted(hit),
            'text': f'You tried "{d["title"]}" (last {when}) and {"set it aside" if d["status"] == "set_aside" else "paused it"}: {short(d["why"], 180)}',
            'context': (f'[Kept] John tried something close to this before: "{d["title"]}", '
                        f'{"set aside" if d["status"] == "set_aside" else "paused"} as of {when}. Why: {d["why"]}{q} '
                        f'If this ask repeats that attempt, say so in one line and ask what is different this time; otherwise ignore this.')}


# ---------------------------------------------------------------- the terminal

class Term:
    def __init__(self):
        self.pid = self.fd = None
        self.buf = bytearray()
        self.subs = []
        self.lock = threading.Lock()

    def alive(self):
        if not self.pid:
            return False
        try:
            return os.waitpid(self.pid, os.WNOHANG) == (0, 0)
        except ChildProcessError:
            return False

    def start(self, cols=100, rows=30):
        if self.alive():
            return
        hook = lambda ev: [{'hooks': [{'type': 'command', 'command':
                f'curl -s -m 8 -X POST --data-binary @- http://127.0.0.1:{PORT}/kept/api/hook/{ev} || true'}]}]
        settings = json.dumps({'hooks': {'UserPromptSubmit': hook('prompt'), 'Stop': hook('stop')}})
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(ROOT)
            # Started from inside another Claude Code session, this would inherit its CLAUDE_CODE_* / CLAUDECODE
            # variables, take itself for a child and stop saving transcripts. The pane is its own session.
            env = {k: v for k, v in os.environ.items() if not (k.startswith('CLAUDE_CODE') or k in ('CLAUDECODE', 'CLAUDE_AGENT_SDK_VERSION'))}
            env.update(TERM='xterm-256color', COLORTERM='truecolor', KEPT='1')
            env['PATH'] = os.path.expanduser('~/.local/bin') + ':' + env.get('PATH', '')
            os.execvpe(CLAUDE, [CLAUDE, '--settings', settings], env)
        self.pid, self.fd = pid, fd
        self.buf = bytearray()
        self.resize(cols, rows)
        threading.Thread(target=self.pump, daemon=True).start()

    def pump(self):
        while True:
            try:
                r, _, _ = select.select([self.fd], [], [], 1)
                if not r:
                    if not self.alive():
                        break
                    continue
                data = os.read(self.fd, 65536)
            except OSError:
                break
            if not data:
                break
            with self.lock:
                self.buf += data
                del self.buf[:-400000]
                for q in self.subs:
                    q.put(data)
        with self.lock:
            for q in self.subs:
                q.put(b'\r\n\x1b[2m[Claude Code ended. Start it again from the pane.]\x1b[0m\r\n')

    def write(self, data):
        if self.alive():
            os.write(self.fd, data)

    def resize(self, cols, rows):
        if self.fd is not None:
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))

    def stop(self):
        if self.alive():
            os.kill(self.pid, signal.SIGTERM)


TERM = Term()


# ---------------------------------------------------------------- http

class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def body(self):
        n = int(self.headers.get('Content-Length') or 0)
        return self.rfile.read(n) if n else b''

    def send_json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path.startswith('/kept/v/'):
            return self.version(u.path[len('/kept/v/'):])
        if u.path == '/kept/api/state':
            return self.send_json(state())
        if u.path == '/kept/api/term/stream':
            return self.stream()
        return super().do_GET()

    def version(self, rest):
        """A file as it was at a version, straight out of git."""
        sha, _, path = rest.partition('/')
        path = unquote(path)
        if not re.fullmatch(r'[0-9a-f]{7,40}', sha):
            return self.send_error(404)
        if path == '' or path.endswith('/'):
            path += 'index.html'
        r = subprocess.run(['git', 'cat-file', 'blob', f'{sha}:{path}'], cwd=ROOT, capture_output=True)
        if r.returncode:
            # A folder asked for without its slash: send the browser to it, so relative links resolve.
            if subprocess.run(['git', 'cat-file', '-e', f'{sha}:{path}/index.html'], cwd=ROOT).returncode == 0:
                self.send_response(301)
                self.send_header('Location', f'/kept/v/{sha}/{path}/')
                return self.end_headers()
            return self.send_error(404)
        self.send_response(200)
        self.send_header('Content-Type', mimetypes.guess_type(path)[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(len(r.stdout)))
        self.end_headers()
        self.wfile.write(r.stdout)

    def stream(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.end_headers()
        q = queue.Queue()
        with TERM.lock:
            first = bytes(TERM.buf)
            TERM.subs.append(q)
        try:
            if first:
                self.wfile.write(b'data: ' + base64.b64encode(first) + b'\n\n')
            self.wfile.flush()
            while True:
                try:
                    data = q.get(timeout=15)
                    while not q.empty() and len(data) < 200000:
                        data += q.get_nowait()
                    self.wfile.write(b'data: ' + base64.b64encode(data) + b'\n\n')
                except queue.Empty:
                    self.wfile.write(b': ping\n\n')
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with TERM.lock:
                if q in TERM.subs:
                    TERM.subs.remove(q)

    def do_POST(self):
        u = urlparse(self.path)
        b = self.body()
        try:
            j = json.loads(b) if b and u.path not in ('/kept/api/term/input',) else {}
        except ValueError:
            j = {}
        p = u.path

        if p == '/kept/api/term/start':
            TERM.start(int(j.get('cols', 100)), int(j.get('rows', 30)))
            return self.send_json({'ok': True})
        if p == '/kept/api/term/stop':
            TERM.stop()
            return self.send_json({'ok': True})
        if p == '/kept/api/term/input':
            TERM.write(b)
            self.send_response(204)
            return self.end_headers()
        if p == '/kept/api/term/resize':
            TERM.resize(int(j['cols']), int(j['rows']))
            return self.send_json({'ok': True})

        if p == '/kept/api/hook/prompt':
            PENDING.update(prompt=j.get('prompt'), t=time.time())
            cur = S.get('current') or {}
            hit = recall(cur['project'], j.get('prompt', '')) if cur.get('project') else None
            NUDGE.update(text=hit and hit['text'], direction=hit and hit['direction'], t=time.time())
            if hit:
                return self.send_json({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': hit['context']}})
            return self.send_json({})
        if p == '/kept/api/hook/stop':
            PENDING['done'] = time.time()
            cur = S.get('current') or {}
            if cur.get('direction'):
                snapshot(cur['project'], cur['direction'], PENDING.get('prompt'))
            return self.send_json({})

        with LOCK:
            if p == '/kept/api/current':
                S['current'] = {'project': j['project'], 'direction': j.get('direction')}
                save(S)
                return self.send_json(state())
            if p == '/kept/api/direction':
                did = 'd' + str(int(time.time() * 1000))[-9:]
                S['directions'][did] = {'project': j['project'], 'title': j.get('title') or 'Untitled direction',
                                        'status': 'active', 'why': '', 'quotes': [], 'base': j.get('from'),
                                        't': int(time.time()), 'versions': []}
                S['current'] = {'project': j['project'], 'direction': did}
                save(S)
                return self.send_json(state())
            if p == '/kept/api/status':
                did = j['direction']
                if did in S['directions']:
                    S['directions'][did]['status'] = j['status']
                    if j.get('why') is not None:
                        S['directions'][did]['why'] = j['why']
                save(S)
                with open(os.path.join(DATA, 'corrections.jsonl'), 'a') as f:
                    f.write(json.dumps({'area': did.split('-')[1] if did.startswith('h-') else S['directions'][did]['project'],
                                        'direction': (find(did) or {}).get('title'), 'field': 'status',
                                        'value': j['status'], 'note': j.get('why'), 'at': int(time.time())}) + '\n')
                return self.send_json(state())
            if p == '/kept/api/push':
                for vs in [d['versions'] for d in S['directions'].values()] + list(S['history'].values()):
                    for v in vs:
                        if v['sha'] == j['sha']:
                            v['pushed'] = not v.get('pushed')
                save(S)
                return self.send_json(state())
            if p == '/kept/api/restore':
                return self.send_json({'restored': restore(j['sha'], j['project']), **state()})
            if p == '/kept/api/snapshot':
                cur = S.get('current') or {}
                v = snapshot(cur['project'], cur['direction'], j.get('note') or 'Saved by hand') if cur.get('direction') else None
                return self.send_json({'version': v, **state()})
        self.send_error(404)


def state():
    return {
        'projects': [{'key': p['key'], 'name': p['name'], 'page': p['page'], 'directions': directions(p['key'])} for p in PROJECTS],
        'current': S.get('current'),
        'nudge': NUDGE if NUDGE['text'] and time.time() - NUDGE['t'] < 600 else None,
        'working': PENDING['t'] > PENDING['done'] and time.time() - PENDING['t'] < 3600,
        'term': TERM.alive(),
    }


if __name__ == '__main__':
    print(f'Kept on http://localhost:{PORT}/kept/')
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Handler, directory=ROOT))
    srv.daemon_threads = True
    srv.serve_forever()
