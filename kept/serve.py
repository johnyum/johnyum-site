#!/usr/bin/env python3
"""Kept, the surface: build with Claude Code, try many things at once, and every turn is kept.

    python3 kept/serve.py                   -> http://localhost:5350/kept/

What this server does, all stdlib:

- Every direction you build on gets its OWN folder and branch: a git worktree at
  ~/.kept/worktrees/<repo>/<direction>, on kept/<project>/<name>. Three ideas at once
  are three folders that never touch until one is merged; the main folder is never
  edited by any of them. This is the fix for colliding.
- Each direction runs its own real Claude Code in a pseudo-terminal in its folder,
  bridged to the page (output over server-sent events, keys back over POST). They run
  side by side; switching panes stops none of them. Each is launched with two hooks,
  for that instance only, that report back with the direction's id:
  UserPromptSubmit (remember what was asked, and say if it was tried before) and Stop
  (keep what the turn made).
- A turn that changed something becomes a real commit on the direction's branch, so
  a direction is PR-ready: Open PR pushes the branch and opens a pull request.
- Serves each direction live from its folder at /kept/w/<direction>/<path>, and any
  version straight out of git at /kept/v/<sha>/<path> (the worktrees share one object
  store), and shoots each new version with headless Chrome for the filmstrip.
- A plain Claude Code in the main folder (the "_main" pane) is there too, for work
  that isn't a direction. Its turns are not kept.

State (directions, their folders, versions) is kept/data/build.json; the directions
read from history are kept/data/areas/, grouped into things by kept/data/things.json.
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
WT = os.path.expanduser(os.environ.get('KEPT_WORKTREES', f'~/.kept/worktrees/{os.path.basename(ROOT)}'))
PORT = int(os.environ.get('PORT', '5350'))
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CLAUDE = os.environ.get('KEPT_ENGINE', os.path.expanduser('~/.local/bin/claude'))
MAIN = '_main'

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


def git(*a, env=None, check=True, inp=None, cwd=None):
    e = dict(os.environ, **(env or {}))
    r = subprocess.run(['git', *a], cwd=cwd or ROOT, capture_output=True, env=e, input=inp)
    if check and r.returncode:
        raise RuntimeError(r.stderr.decode()[-400:])
    return r.stdout


def short(s, n):
    s = ' '.join(str(s).split())
    return s if len(s) <= n else s[:n].rsplit(' ', 1)[0] + '…'


# ---------------------------------------------------------------- state

def load():
    try:
        s = json.load(open(STATE))
    except (OSError, ValueError):
        s = {}
    s.setdefault('directions', {})   # id -> {project, thing, title, status, why, versions: [...]}
    s.setdefault('current', None)    # {project, thing, direction}
    s.setdefault('history', {})      # history direction id -> versions built on it here
    s.setdefault('things', {})       # project -> [{id, name, directions: []}] made here
    s.setdefault('wt', {})           # direction id -> {path, branch, base, pr}: its own folder
    return s


def save(s):
    os.makedirs(DATA, exist_ok=True)
    tmp = STATE + '.tmp'
    json.dump(s, open(tmp, 'w'), indent=1)
    os.replace(tmp, STATE)


S = load()
PEND = {}     # pane key -> {prompt, t, done}: what was last asked there, and whether it's still building
NUDGES = {}   # pane key -> the last recall shown for it


def thumbs():
    try:
        return json.load(open(os.path.join(THUMBS, 'thumbs.json')))
    except (OSError, ValueError):
        return {}


def history():
    """The directions read from four months of history, by project."""
    out, raw = {}, {}
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


def versions_of(did):
    return S['history'].setdefault(did, []) if did.startswith('h-') else S['directions'][did]['versions']


def directions(project):
    """History directions with any versions built on them here, then the ones started here."""
    ds = history().get(project, [])
    for d in ds:
        d['versions'] = d['versions'] + S['history'].get(d['id'], [])
    for id_, d in S['directions'].items():
        if d['project'] == project:
            ds.append(dict(d, id=id_, kind='new'))
    for d in ds:
        w = S['wt'].get(d['id'])
        d['folder'] = bool(w and os.path.isdir(w['path']))
        d['branch'] = w and w['branch']
        d['pr'] = w and w.get('pr')
        d['building'] = building(d['id']) or d['id'] in RUNS
        d['running'] = d['id'] in TERMS and TERMS[d['id']].alive()
        if d['folder'] and d['status'] == 'active':
            # How many changes Main has that this thread doesn't: someone pushed while you were working.
            d['behind'] = int(git('rev-list', '--count', f"{w['branch']}..main", check=False).decode().strip() or 0)
            d['head'] = git('rev-parse', '--short=7', w['branch'], check=False).decode().strip()
        src = S['directions'].get(d['id'], {})
        d['conflict'] = src.get('conflict')
        d['resolved'] = src.get('resolved')
    return ds


def things(project):
    """A project's things: what was made in it (Tide pool, Moby Dick), each holding its directions.
    The four months were grouped once (data/things.json, Claude's reading); things made here add to it.
    A direction that belongs to none sits in Loose, so nothing is ever hidden."""
    try:
        seed = json.load(open(os.path.join(DATA, 'things.json'))).get(project, [])
    except (OSError, ValueError):
        seed = []
    ts = [dict(t, directions=list(t['directions'])) for t in seed] + [dict(t, directions=list(t.get('directions', []))) for t in S['things'].get(project, [])]
    by = {t['id']: t for t in ts}
    ds = {d['id']: d for d in directions(project)}
    for did, d in S['directions'].items():
        if d['project'] == project and d.get('thing') in by and did not in by[d['thing']]['directions']:
            by[d['thing']]['directions'].append(did)
    placed = {x for t in ts for x in t['directions']}
    loose = [x for x in ds if x not in placed]
    if loose:
        ts.append({'id': f't-{project}-loose', 'name': 'Loose', 'directions': loose})
    order = {'active': 0, 'paused': 1, 'settled': 2, 'set_aside': 3}
    out = []
    for t in ts:
        dirs = [ds[x] for x in t['directions'] if x in ds]
        dirs.sort(key=lambda d: (order.get(d['status'], 9), -max([v['t'] for v in d['versions']] or [0])))
        last = max([v['t'] for d in dirs for v in d['versions']] or [0])
        out.append({'id': t['id'], 'name': t['name'], 'directions': dirs, 'last': last})
    return out


def working_on(limit=8, days=21):
    """What you're in the middle of: anything building now, then active directions touched lately, newest first."""
    rows = []
    for p in PROJECTS:
        for t in things(p['key']):
            for d in t['directions']:
                last = max([v['t'] for v in d['versions']] or [d.get('t', 0)])
                if d['building'] or d['running']:
                    last = time.time()
                if d['status'] == 'active' or d['running']:
                    rows.append({'project': p['key'], 'thing': t['id'], 'direction': d['id'], 'title': d['title'],
                                 'thingName': t['name'], 'last': last, 'building': d['building'], 'running': d['running']})
    rows.sort(key=lambda r: -r['last'])
    newest = rows[0]['last'] if rows else 0
    return [r for r in rows if r['last'] >= newest - days * 86400][:limit]


def main_versions(project, n=40):
    """Main's strip: the commits on main that touched this project, oldest first. What's live, and how it got there."""
    paths = [x.rstrip('/') for x in P[project]['paths']]
    out = git('log', 'main', f'-n{n}', '--format=%h%x09%at%x09%s', '--', *paths, check=False).decode().strip().split('\n')
    th = thumbs()
    vs = []
    for line in reversed([l for l in out if l]):
        sha, t, subj = line.split('\t', 2)
        sha = sha[:7]
        e = th.get(sha, {})
        pic = (e.get('pics') or [{}])[0].get('src')
        shot = pic or (e.get('shot') or {}).get('src') or (f'{sha}.jpg' if os.path.exists(os.path.join(THUMBS, f'{sha}.jpg')) else None)
        vs.append({'sha': sha, 't': int(t), 'note': short(subj, 90), 'prompt': subj, 'shot': shot,
                   'page': (e.get('shot') or {}).get('url', '').lstrip('/') or P[project]['page'], 'from': 'main'})
    return vs


OPEN = ('active',)                 # a branch you're working on
CLOSED = ('set_aside', 'paused', 'closed')


def project_view(project):
    """One project: Main (what's live), the branches open on it, and what was closed and why.
    The four months' settled and active work is Main's history now; set-aside and paused ideas are Closed."""
    ds = directions(project)
    branches = [d for d in ds if d['kind'] == 'new' and d['status'] in OPEN]
    branches.sort(key=lambda d: -max([v['t'] for v in d['versions']] or [d.get('t', 0)]))
    closed = [d for d in ds if d['status'] in CLOSED]
    closed.sort(key=lambda d: -max([v['t'] for v in d['versions']] or [d.get('t', 0)]))
    main = main_versions(project)
    last = max([v['t'] for v in main] + [v['t'] for d in branches for v in d['versions']] + [d.get('t', 0) for d in branches] + [0])
    return {'main': main, 'branches': branches, 'closed': closed, 'last': last}


def find(did):
    proj = did.split('-')[1] if did.startswith('h-') else S['directions'].get(did, {}).get('project', '')
    return next((d for d in directions(proj) if d['id'] == did), None)


# ---------------------------------------------------------------- a folder per direction

def slug(s):
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')[:36] or 'direction'


def folder(did, base=None):
    """The direction's own worktree and branch, made the first time you build on it."""
    with LOCK:
        w = S['wt'].get(did)
        if w and os.path.isdir(w['path']):
            return w
        d = find(did)
        if not d:
            raise KeyError(did)
        path = os.path.join(WT, did)
        branch = f"kept/{d['project']}/{slug(d['title'])}-{did[-4:]}"
        base = base or git('rev-parse', 'HEAD').decode().strip()
        os.makedirs(WT, exist_ok=True)
        if subprocess.run(['git', 'show-ref', '--verify', '--quiet', f'refs/heads/{branch}'], cwd=ROOT).returncode == 0:
            git('worktree', 'add', path, branch)          # the branch outlived its folder: pick it up again
        else:
            git('worktree', 'add', '-b', branch, path, base)
        S['wt'][did] = {'path': path, 'branch': branch, 'base': base, 'pr': (w or {}).get('pr')}
        save(S)
        return S['wt'][did]


def keep(did, prompt):
    """What a turn made, as a commit on the direction's own branch. A turn that changed nothing is no version."""
    with LOCK:
        w = S['wt'].get(did)
        if not w or not os.path.isdir(w['path']):
            return None
        cwd, vs = w['path'], versions_of(did)
        git('add', '-A', cwd=cwd)
        if subprocess.run(['git', 'diff', '--cached', '--quiet'], cwd=cwd).returncode:
            git('commit', '-q', '--no-verify', '-m', (prompt or 'A turn').strip()[:2000], cwd=cwd)
        sha = git('rev-parse', 'HEAD', cwd=cwd).decode().strip()   # Claude may have committed on its own, too
        prev = vs[-1].get('full') if vs and vs[-1].get('from') == 'here' else w['base']
        if sha == prev:
            return None
        changed = [f for f in git('diff', '--name-only', prev, sha, cwd=cwd).decode().split('\n') if f][:40]
        d = find(did)
        v = {'sha': sha[:7], 'full': sha, 't': int(time.time()), 'prompt': (prompt or '').strip()[:2000],
             'note': short(prompt or 'A turn', 80), 'files': changed, 'shot': None,
             'page': page_for(d['project'], changed), 'pushed': False, 'from': 'here'}
        vs.append(v)
        save(S)
        threading.Thread(target=shoot, args=(v['sha'], v['page']), daemon=True).start()
        return v


def snapshot(project, did, prompt):
    """A direction with no folder of its own: keep the main folder as a commit on refs/kept/<project>/<direction>,
    through a throwaway index, so HEAD, index and branch are untouched. (How Kept worked before worktrees.)"""
    with LOCK:
        vs = versions_of(did)
        prev = vs[-1]['sha'] if vs else None
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
            return None
        parent = prev or git('rev-parse', 'HEAD').decode().strip()
        sha = git('commit-tree', tree, '-p', parent, '-m', (prompt or 'A turn').strip()[:2000]).decode().strip()
        git('update-ref', f'refs/kept/{project}/{did}', sha)
        changed = [f for f in git('diff', '--name-only', parent, sha).decode().split('\n') if f][:40]
        v = {'sha': sha[:7], 'full': sha, 't': int(time.time()), 'prompt': prompt, 'note': short(prompt or 'A turn', 80),
             'files': changed, 'shot': None, 'page': page_for(project, changed), 'pushed': False, 'from': 'here'}
        vs.append(v)
        save(S)
        threading.Thread(target=shoot, args=(v['sha'], v['page']), daemon=True).start()
        return v


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


def shoot(sha, page):
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


def restore(did, sha):
    """Take a direction's folder back to one of its versions. What's there now is kept as a version first."""
    with LOCK:
        w = S['wt'].get(did)
        if not w:
            raise KeyError(did)
        keep(did, f'Kept before going back to {sha}')
        git('checkout', sha, '--', '.', cwd=w['path'])
        return keep(did, f'Back to {sha}')


def open_pr(did):
    """Push the direction's branch and open a pull request for it, with what each version asked for."""
    w, d = S['wt'][did], find(did)
    git('push', '-u', 'origin', w['branch'], cwd=w['path'])
    mine = [v for v in versions_of(did) if v.get('from') == 'here']
    body = '\n'.join([f"Made in Kept: {d['title']}.", ''] +
                     [f"- v{i + 1}: {short(v.get('prompt') or v.get('note') or '', 160)}" for i, v in enumerate(mine)])
    r = subprocess.run(['gh', 'pr', 'create', '--head', w['branch'], '--base', 'main', '--title', d['title'], '--body', body],
                       cwd=w['path'], capture_output=True, text=True)
    url = (r.stdout.strip().splitlines() or [''])[-1]
    if r.returncode and 'already exists' in r.stderr:
        url = subprocess.run(['gh', 'pr', 'view', w['branch'], '--json', 'url', '-q', '.url'], cwd=w['path'],
                             capture_output=True, text=True).stdout.strip()
    elif r.returncode:
        raise RuntimeError(r.stderr[-400:])
    with LOCK:
        w['pr'] = url
        save(S)
    return url


def name_from(prompt):
    """A branch named from what was asked: its first few words, the way you'd say it."""
    w = re.sub(r'\s+', ' ', re.sub(r'[^\w\s\'-]', ' ', prompt)).strip().split(' ')
    n = ' '.join(w[:6])
    return (n[:1].upper() + n[1:]) if n else 'Untitled'


def start(project, prompt, cols=100, rows=30):
    """Just start typing: a new branch with its own folder and Claude, and the prompt handed to it once it's up."""
    with LOCK:
        did = 'd' + str(int(time.time() * 1000))[-9:]
        S['directions'][did] = {'project': project, 'title': name_from(prompt), 'status': 'active', 'why': '',
                                'quotes': [], 't': int(time.time()), 'versions': []}
        S['current'] = {'project': project, 'direction': did}
        save(S)
    t = term(did, make=True)
    t.start(cols, rows)

    def hand_over():
        end = time.time() + 25
        while time.time() < end and b'\xe2\x9d\xaf' not in bytes(t.buf):   # the prompt mark: Claude is ready
            time.sleep(0.3)
        time.sleep(0.6)
        t.write(prompt.encode())
        time.sleep(0.4)
        t.write(b'\r')
    threading.Thread(target=hand_over, daemon=True).start()
    return did


def push(did):
    """Push: put a branch into main and send it live. It merges in the main folder, so if your own unsaved
    edits there touch the same files, git refuses and nothing changes; you're told why."""
    with LOCK:
        w, d = S['wt'][did], find(did)
        keep(did, 'Kept before pushing')
        if int(git('rev-list', '--count', f"{w['branch']}..main").decode().strip() or 0):
            if bring_in(did):
                raise RuntimeError('CONFLICT: Main changed the same part you did. Say how to combine them, then Push again.')
        if git('rev-parse', '--abbrev-ref', 'HEAD').decode().strip() != 'main':
            raise RuntimeError('The main folder is not on main. Switch it back to main, then push.')
        r = subprocess.run(['git', 'merge', '--no-ff', '--no-edit', '-m', f"{d['title']} (from Kept)", w['branch']],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            subprocess.run(['git', 'merge', '--abort'], cwd=ROOT, capture_output=True)
            out = r.stderr + r.stdout
            mine = re.findall(r'^\t(\S+)$', out, re.M)
            if 'local changes' in out and mine:
                raise RuntimeError(f"Not pushed. You have unsaved edits in the main folder to {', '.join(mine[:4])}, which this branch "
                                   f"also changes. Save or undo them there, then Push again. Nothing changed.")
            if 'CONFLICT' in out:
                raise RuntimeError('Not pushed. Main has changed the same lines since this branch started; ask its Claude to '
                                   '"bring in the latest main and resolve it", then Push again. Nothing changed.')
            raise RuntimeError('Not pushed: ' + out.strip()[-300:])
        merged = git('rev-parse', '--short=7', 'HEAD').decode().strip()
        r = subprocess.run(['git', 'push', 'origin', 'main'], cwd=ROOT, capture_output=True, text=True)
        live = r.returncode == 0
        S['directions'][did].update(status='pushed', pushed=int(time.time()), merged=merged, live=live)
        save(S)
        t = TERMS.pop(did, None)
        t and t.stop()
        # Its folder has done its job; the branch stays, so its history is still there.
        subprocess.run(['git', 'worktree', 'remove', '--force', w['path']], cwd=ROOT, capture_output=True)
        if not live:
            raise RuntimeError('Merged into main, but the push to GitHub failed: ' + r.stderr.strip()[-200:])
        return merged


def bring_in(did):
    """Bring the latest Main into a thread. Clean: a new version. A clash: the merge is left open in the thread's
    folder and recorded, so the page can show the three pictures and ask how to combine them."""
    with LOCK:
        w, d = S['wt'][did], S['directions'][did]
        if d.get('conflict'):
            return d['conflict']
        keep(did, 'Kept before bringing in Main')
        pre = git('rev-parse', 'HEAD', cwd=w['path']).decode().strip()
        theirs = git('rev-parse', 'main').decode().strip()
        base = git('merge-base', pre, theirs).decode().strip()
        r = subprocess.run(['git', 'merge', '--no-edit', '-m', 'Brought in the latest Main', 'main'], cwd=w['path'],
                           capture_output=True, text=True)
        if r.returncode == 0:
            keep(did, 'Brought in the latest Main')
            return None
        files = [f for f in git('diff', '--name-only', '--diff-filter=U', cwd=w['path']).decode().split('\n') if f]
        if not files:
            subprocess.run(['git', 'merge', '--abort'], cwd=w['path'], capture_output=True)
            raise RuntimeError('Could not bring in Main: ' + (r.stderr or r.stdout).strip()[-300:])
        page = page_for(d['project'], files)
        d['conflict'] = {'files': files, 'pre': pre, 'mine': pre[:7], 'theirs': theirs[:7], 'base': base[:7], 'page': page,
                         't': int(time.time())}
        save(S)
        return d['conflict']


def resolve(did, text):
    """Combine the clash the way you say: the thread's Claude does the merge in its folder."""
    c = S['directions'][did]['conflict']
    send = (f"Main has been merged into this thread and these files clash: {', '.join(c['files'])}. Combine the two sides "
            f"the way he says: \"{text}\". Remove every conflict marker (<<<<<<<, =======, >>>>>>>), keep the page working, "
            f"and don't commit. Then say in one sentence what you kept from each side.")
    turn(did, text, send=send)


def abort_merge(did):
    with LOCK:
        w, d = S['wt'][did], S['directions'][did]
        subprocess.run(['git', 'merge', '--abort'], cwd=w['path'], capture_output=True)
        d.pop('conflict', None)
        save(S)


def undo_merge(did):
    """Didn't like how it combined: go back to the thread as it was before Main was brought in."""
    with LOCK:
        w, d = S['wt'][did], S['directions'][did]
        r = d.pop('resolved', None)
        if r:
            git('reset', '--hard', r['pre'], cwd=w['path'])
            keep(did, 'Undid bringing in Main')
        save(S)


def close(did, why):
    with LOCK:
        S['directions'][did].update(status='closed', why=why or '', closed=int(time.time()))
        save(S)
        t = TERMS.pop(did, None)
        t and t.stop()


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
    a word with its name AND a rare word with its record (in at most three of the project's directions).
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
    return {'direction': d['id'], 'title': d['title'], 'words': sorted(hit), 't': time.time(),
            'text': f'You tried "{d["title"]}" (last {when}) and {"set it aside" if d["status"] == "set_aside" else "paused it"}: {short(d["why"], 180)}',
            'context': (f'[Kept] John tried something close to this before: "{d["title"]}", '
                        f'{"set aside" if d["status"] == "set_aside" else "paused"} as of {when}. Why: {d["why"]}{q} '
                        f'If this ask repeats that attempt, say so in one line and ask what is different this time; otherwise ignore this.')}


def building(key):
    p = PEND.get(key)
    return bool(p and p['t'] > p['done'] and time.time() - p['t'] < 3600)


# ---------------------------------------------------------------- the chat: Claude Code, headless, one session per thread

GUIDE = """You are working inside Kept, for a designer who builds in code and doesn't read terminals. You're in this
thread's own copy of the project (a git worktree on its own branch); edit files here freely, nothing else is touched until
he pushes. Reply in one or two short plain sentences: what you changed and where, or the one question you need answered.
No code blocks, no file listings, no headings unless he asks. Don't commit; Kept saves every turn as a version itself."""

RUNS = {}   # thread id -> the running claude process


def step_of(tool, inp, cwd):
    """A tool call as a few words a designer can follow."""
    f = os.path.relpath(inp.get('file_path') or inp.get('path') or '', cwd) if (inp.get('file_path') or inp.get('path')) else ''
    if tool in ('Edit', 'MultiEdit', 'Write', 'NotebookEdit'):
        return f'Editing {f}'
    if tool == 'Read':
        return f'Reading {f}'
    if tool in ('Grep', 'Glob'):
        return 'Looking through the files'
    if tool == 'Bash':
        return 'Running ' + short(inp.get('command', ''), 60)
    if tool in ('WebSearch', 'WebFetch'):
        return 'Looking it up'
    return tool


def chat_of(did):
    d = S['directions'][did]
    return d.setdefault('chat', [])


def turn(did, text, allow=None, send=None):
    """One message to the thread's Claude. Runs in the background; the page watches the chat fill in."""
    with LOCK:
        w = folder(did)
        d = S['directions'][did]
        chat = chat_of(did)
        if not allow:
            chat.append({'role': 'you', 'text': text, 't': int(time.time())})
        reply = {'role': 'claude', 'text': '', 'steps': [], 't': int(time.time()), 'busy': True}
        chat.append(reply)
        save(S)
        hit = recall(d['project'], text) if not allow else None
        NUDGES[did] = hit

    def run():
        args = [CLAUDE, '-p', '--output-format', 'stream-json', '--verbose', '--permission-mode', 'acceptEdits',
                '--append-system-prompt', GUIDE + ('\n\n' + hit['context'] if hit else '')]
        if d.get('session'):
            args += ['--resume', d['session']]
        if allow:
            args += ['--allowedTools', allow]
        env = {k: v for k, v in os.environ.items() if not (k.startswith('CLAUDE_CODE') or k in ('CLAUDECODE', 'CLAUDE_AGENT_SDK_VERSION'))}
        env['PATH'] = os.path.expanduser('~/.local/bin') + ':' + env.get('PATH', '')
        proc = subprocess.Popen(args, cwd=w['path'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, env=env)
        RUNS[did] = proc
        proc.stdin.write(('Go ahead, that step is allowed now.' if allow else send or text))
        proc.stdin.close()
        last = None
        for line in proc.stdout:
            try:
                o = json.loads(line)
            except ValueError:
                continue
            with LOCK:
                if o.get('session_id'):
                    d['session'] = o['session_id']
                if o.get('type') == 'assistant':
                    for c in o.get('message', {}).get('content', []):
                        if c.get('type') == 'tool_use':
                            reply['steps'].append(step_of(c.get('name', ''), c.get('input') or {}, w['path']))
                        elif c.get('type') == 'text' and c.get('text', '').strip():
                            reply['text'] = c['text'].strip()
                    save(S)
                if o.get('type') == 'result':
                    last = o
        proc.wait()
        RUNS.pop(did, None)
        with LOCK:
            if last:
                reply['text'] = (last.get('result') or reply['text'] or '').strip()
                denied = [x for x in last.get('permission_denials') or [] if x.get('tool_name')]
                if denied:
                    x = denied[0]
                    inp = x.get('tool_input') or {}
                    reply['blocked'] = {'tool': x['tool_name'], 'what': step_of(x['tool_name'], inp, w['path']),
                                        'allow': f"Bash({inp['command']})" if x['tool_name'] == 'Bash' and inp.get('command') else x['tool_name']}
                if last.get('is_error'):
                    reply['error'] = True
            elif proc.returncode:
                reply['text'] = reply['text'] or 'Stopped.'
            reply['busy'] = False
            save(S)
        c = d.get('conflict')
        if c:
            left = [f for f in c['files'] if os.path.exists(os.path.join(w['path'], f)) and
                    re.search(r'^(<{7}|>{7}) ', open(os.path.join(w['path'], f), errors='ignore').read(), re.M)]
            if left:
                with LOCK:
                    reply['text'] = (reply['text'] + ' ' if reply['text'] else '') + f"Still clashing in {', '.join(left)}."
                    reply['error'] = True
                    save(S)
                return
            v = keep(did, f'Brought in the latest Main: {text}')
            with LOCK:
                reply.pop('blocked', None)   # the merge is done; a check it wanted to run after doesn't need you
                d['resolved'] = dict(c, sha=v['sha'] if v else None, said=text)
                d.pop('conflict', None)
                if v:
                    reply['version'] = v['sha']
                save(S)
            return
        v = keep(did, text if not allow else f'{text} (allowed)')
        with LOCK:
            if v:
                reply['version'] = v['sha']
                save(S)

    threading.Thread(target=run, daemon=True).start()


def begin(project, text):
    """A sentence on a project's home starts a thread: its own branch and folder, named from the words."""
    with LOCK:
        did = 'd' + str(int(time.time() * 1000))[-9:]
        S['directions'][did] = {'project': project, 'title': name_from(text), 'status': 'active', 'why': '',
                                'quotes': [], 't': int(time.time()), 'versions': [], 'chat': []}
        S['current'] = {'project': project, 'direction': did}
        save(S)
    turn(did, text)
    return did


def stop_turn(did):
    p = RUNS.get(did)
    if p and p.poll() is None:
        p.terminate()


# ---------------------------------------------------------------- the terminals: one Claude Code per direction (kept, unused by the page)

class Term:
    def __init__(self, key, cwd):
        self.key, self.cwd = key, cwd
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
                f'curl -s -m 8 -X POST --data-binary @- "http://127.0.0.1:{PORT}/kept/api/hook/{ev}?d={self.key}" || true'}]}]
        settings = json.dumps({'hooks': {'UserPromptSubmit': hook('prompt'), 'Stop': hook('stop')}})
        pid, fd = pty.fork()
        if pid == 0:
            os.chdir(self.cwd)
            # Started from inside another Claude Code session, this would inherit its CLAUDE_CODE_* / CLAUDECODE
            # variables, take itself for a child and stop saving transcripts. Each pane is its own session.
            env = {k: v for k, v in os.environ.items() if not (k.startswith('CLAUDE_CODE') or k in ('CLAUDECODE', 'CLAUDE_AGENT_SDK_VERSION'))}
            env.update(TERM='xterm-256color', COLORTERM='truecolor', KEPT='1', KEPT_DIRECTION=self.key)
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


TERMS = {}


def term(key, make=False):
    """The pane for a direction (in its own folder) or for the main folder."""
    t = TERMS.get(key)
    if t is None and make:
        cwd = ROOT if key == MAIN else folder(key)['path']
        t = TERMS[key] = Term(key, cwd)
    return t


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
        q = parse_qs(u.query)
        if u.path.startswith('/kept/v/'):
            return self.version(u.path[len('/kept/v/'):])
        if u.path.startswith('/kept/w/'):
            return self.live(u.path[len('/kept/w/'):])
        if u.path == '/kept/api/state':
            return self.send_json(state())
        if u.path == '/kept/api/term/stream':
            return self.stream(q.get('k', [MAIN])[0])
        return super().do_GET()

    def send_bytes(self, data, path):
        self.send_response(200)
        self.send_header('Content-Type', mimetypes.guess_type(path)[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

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
        self.send_bytes(r.stdout, path)

    def live(self, rest):
        """A file as it is right now in a direction's own folder."""
        did, _, path = rest.partition('/')
        w = S['wt'].get(did)
        if not w:
            return self.send_error(404)
        root = os.path.realpath(w['path'])
        full = os.path.realpath(os.path.join(root, unquote(path)))
        if not (full == root or full.startswith(root + os.sep)):
            return self.send_error(403)
        if os.path.isdir(full):
            if path and not path.endswith('/'):
                self.send_response(301)
                self.send_header('Location', f'/kept/w/{did}/{path}/')
                return self.end_headers()
            full = os.path.join(full, 'index.html')
        if not os.path.isfile(full):
            return self.send_error(404)
        self.send_bytes(open(full, 'rb').read(), full)

    def stream(self, key):
        t = term(key)
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.end_headers()
        if not t:
            self.wfile.write(b': none\n\n')
            return
        q = queue.Queue()
        with t.lock:
            first = bytes(t.buf)
            t.subs.append(q)
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
            with t.lock:
                if q in t.subs:
                    t.subs.remove(q)

    def do_POST(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        b = self.body()
        p = u.path
        try:
            j = json.loads(b) if b and p != '/kept/api/term/input' else {}
        except ValueError:
            j = {}
        key = j.get('k') or q.get('k', q.get('d', [MAIN]))[0]

        try:
            if p == '/kept/api/term/start':
                term(key, make=True).start(int(j.get('cols', 100)), int(j.get('rows', 30)))
                return self.send_json(state())
            if p == '/kept/api/term/stop':
                t = term(key)
                t and t.stop()
                return self.send_json({'ok': True})
            if p == '/kept/api/term/input':
                t = term(key)
                t and t.write(b)
                self.send_response(204)
                return self.end_headers()
            if p == '/kept/api/term/resize':
                t = term(key)
                t and t.resize(int(j['cols']), int(j['rows']))
                return self.send_json({'ok': True})

            if p == '/kept/api/hook/prompt':
                PEND[key] = {'prompt': j.get('prompt'), 't': time.time(), 'done': 0}
                proj = (find(key) or {}).get('project') if key != MAIN else (S.get('current') or {}).get('project')
                hit = recall(proj, j.get('prompt', '')) if proj else None
                NUDGES[key] = hit
                if hit:
                    return self.send_json({'hookSpecificOutput': {'hookEventName': 'UserPromptSubmit', 'additionalContext': hit['context']}})
                return self.send_json({})
            if p == '/kept/api/hook/stop':
                pend = PEND.setdefault(key, {'prompt': None, 't': 0, 'done': 0})
                pend['done'] = time.time()
                if key != MAIN:
                    keep(key, pend.get('prompt'))
                return self.send_json({})

            with LOCK:
                if p == '/kept/api/current':
                    S['current'] = {'project': j['project'], 'thing': j.get('thing'), 'direction': j.get('direction')}
                    save(S)
                    return self.send_json(state())
                if p == '/kept/api/thing':
                    tid = 't' + str(int(time.time() * 1000))[-9:]
                    S['things'].setdefault(j['project'], []).append({'id': tid, 'name': j.get('name') or 'Untitled', 'directions': []})
                    S['current'] = {'project': j['project'], 'thing': tid, 'direction': None}
                    save(S)
                    return self.send_json(state())
                if p == '/kept/api/direction':
                    # A new direction, branched from main or from a version you were looking at: its own folder from the start.
                    did = 'd' + str(int(time.time() * 1000))[-9:]
                    S['directions'][did] = {'project': j['project'], 'thing': j.get('thing'), 'title': j.get('title') or 'Untitled direction',
                                            'status': 'active', 'why': '', 'quotes': [], 'base': j.get('from'),
                                            't': int(time.time()), 'versions': []}
                    S['current'] = {'project': j['project'], 'thing': j.get('thing'), 'direction': did}
                    save(S)
                    folder(did, j.get('from'))
                    return self.send_json(state())
                if p == '/kept/api/say':
                    # One box for everything: on a thread it continues it; on a project's home it starts one.
                    text = (j.get('text') or '').strip()
                    if j.get('direction') and j['direction'] in S['directions']:
                        if j['direction'] in RUNS:
                            raise RuntimeError('Claude is still working on the last message. Wait, or stop it.')
                        turn(j['direction'], text)
                    else:
                        if len(re.findall(r'\w+', text)) < 3:
                            raise RuntimeError('Say a little more: a few words about what you want to try.')
                        begin(j['project'], text)
                    return self.send_json(state())
                if p == '/kept/api/bringin':
                    bring_in(j['direction'])
                    return self.send_json(state())
                if p == '/kept/api/resolve':
                    if j['direction'] in RUNS:
                        raise RuntimeError('Claude is still working. Wait, or stop it.')
                    resolve(j['direction'], (j.get('text') or '').strip() or 'combine both sensibly')
                    return self.send_json(state())
                if p == '/kept/api/abortmerge':
                    abort_merge(j['direction'])
                    return self.send_json(state())
                if p == '/kept/api/undomerge':
                    undo_merge(j['direction'])
                    return self.send_json(state())
                if p == '/kept/api/keepmerge':
                    S['directions'][j['direction']].pop('resolved', None)
                    save(S)
                    return self.send_json(state())
                if p == '/kept/api/allow':
                    did = j['direction']
                    chat = chat_of(did)
                    asked = next((m['text'] for m in reversed(chat) if m['role'] == 'you'), '')
                    turn(did, asked, allow=j['allow'])
                    return self.send_json(state())
                if p == '/kept/api/stop':
                    stop_turn(j['direction'])
                    return self.send_json(state())
                if p == '/kept/api/start':
                    start(j['project'], j['prompt'], int(j.get('cols', 100)), int(j.get('rows', 30)))
                    return self.send_json(state())
                if p == '/kept/api/close':
                    close(j['direction'], j.get('why'))
                    return self.send_json(state())
                if p == '/kept/api/build':
                    folder(j['direction'])
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
                if p == '/kept/api/restore':
                    return self.send_json({'version': restore(j['direction'], j['sha']), **state()})
                if p == '/kept/api/snapshot':
                    did = j['direction']
                    v = keep(did, j.get('note') or 'Saved by hand') if did in S['wt'] else \
                        snapshot(find(did)['project'], did, j.get('note') or 'Saved by hand')
                    return self.send_json({'version': v, **state()})
            if p == '/kept/api/push':
                return self.send_json({'merged': push(j['direction']), **state()})
            if p == '/kept/api/pr':
                return self.send_json({'url': open_pr(j['direction']), **state()})
        except Exception as e:  # the page shows it; the server keeps going
            return self.send_json({'error': str(e)[-400:]}, 500)
        self.send_error(404)


def state():
    return {
        'projects': sorted([dict(project_view(p['key']), key=p['key'], name=p['name'], page=p['page']) for p in PROJECTS],
                           key=lambda x: -x['last']),
        'current': S.get('current'),
        'nudges': {k: v for k, v in NUDGES.items() if v and time.time() - v['t'] < 600},
        'main': {'running': bool(term(MAIN) and term(MAIN).alive()), 'building': building(MAIN)},
        'main_sha': git('rev-parse', '--short=7', 'main', check=False).decode().strip(),
    }


def shoot_main(per=12):
    """Main's strip should be pictures: shoot the newest commits in each project that have none yet, once, quietly."""
    time.sleep(3)
    for p in PROJECTS:
        for v in main_versions(p['key'])[-per:]:
            if v['shot']:
                continue
            files = git('show', '--name-only', '--format=', v['sha']).decode().split('\n')
            shoot(v['sha'], page_for(p['key'], [f for f in files if f]))


if __name__ == '__main__':
    print(f'Kept on http://localhost:{PORT}/kept/  (worktrees in {WT})')
    threading.Thread(target=shoot_main, daemon=True).start()
    srv = ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Handler, directory=ROOT))
    srv.daemon_threads = True
    srv.serve_forever()
