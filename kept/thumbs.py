#!/usr/bin/env python3
"""Kept, step three: what each turn looked like.

    python3 kept/thumbs.py                  -> kept/data/thumbs/<sha>.jpg, <sha>-<n>.jpg, thumbs.json

For every turn the distill named, two kinds of picture:
- the images that commit itself added or changed (a generated plush, a Figma export), taken
  from git AT that commit, so a set-aside picture still shows even if it was later deleted;
- a screenshot of the page the commit touched, as it was that day: the commit is checked out
  in a worktree, served, and shot with headless Chrome.

Worktrees live in a temp dir and are removed after. Turns already shot are skipped, so a
rerun after a new distill only shoots what's new.
"""
import glob, http.server, functools, json, os, re, shutil, subprocess, sys, tempfile, threading
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
OUT = os.path.join(HERE, 'data', 'thumbs')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
IMG = re.compile(r'\.(png|jpe?g|webp|gif)$', re.I)
LANES = 4

# Where to look when a commit touched an area but no page in particular.
HOME = {'preso': '/preso/', 'multi': '/multi/', 'peek': '/peek/', 'explore': '/explore/',
        'icons': '/claude-icons/index.html', 'site': '/'}


def git(*a, cwd=REPO):
    return subprocess.run(['git', *a], cwd=cwd, capture_output=True, check=True).stdout


def page_for(area, files):
    for f in files:
        m = re.match(r'preso/slides/([0-9a-z]+)\.html$', f)
        if m:
            return f'/preso/slides/{m.group(1)}.html'
    for f in files:
        m = re.match(r'([a-z0-9-]+)/index\.html$', f)
        if m and m.group(1) not in ('preso', 'kept'):
            return f'/{m.group(1)}/' + ('?preso=1' if m.group(1) == 'recurrence' else '')
    if 'index.html' in files:
        return '/'
    return HOME[area]


def pictures(sha, files):
    """The images the commit itself changed, read from git at that commit, shrunk."""
    out = []
    for f in [f for f in files if IMG.search(f)][:4]:
        try:
            blob = git('show', f'{sha}:{f}')
        except subprocess.CalledProcessError:
            continue  # deleted in this commit
        src = os.path.join(tempfile.gettempdir(), f'kept-{sha}-{len(out)}{os.path.splitext(f)[1]}')
        open(src, 'wb').write(blob)
        dst = os.path.join(OUT, f'{sha}-{len(out)}.jpg')
        r = subprocess.run(['sips', '-Z', '480', '-s', 'format', 'jpeg', src, '--out', dst], capture_output=True)
        os.remove(src)
        if r.returncode == 0:
            out.append({'src': os.path.basename(dst), 'file': f})
    return out


def serve(root):
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(
        type('Q', (http.server.SimpleHTTPRequestHandler,), {'log_message': lambda *a: None}), directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def lane(n, jobs, tmp, done):
    wt = os.path.join(tmp, f'wt{n}')
    git('worktree', 'add', '--detach', '-f', wt, jobs[0][0])
    srv, prof = serve(wt), os.path.join(tmp, f'chrome{n}')
    try:
        for sha, url in jobs:
            git('checkout', '-q', '--detach', '-f', sha, cwd=wt)
            png = os.path.join(tmp, f'{sha}.png')
            subprocess.run([CHROME, '--headless=new', '--hide-scrollbars', '--mute-audio', f'--user-data-dir={prof}',
                            '--window-size=1440,900', '--virtual-time-budget=6000', f'--screenshot={png}',
                            f'http://127.0.0.1:{srv.server_address[1]}{url}'], capture_output=True, timeout=90)
            if os.path.exists(png):
                subprocess.run(['sips', '-Z', '720', '-s', 'format', 'jpeg', png, '--out',
                                os.path.join(OUT, f'{sha}.jpg')], capture_output=True)
                done[sha] = url
            print(f'lane {n}: {sha} {url}', flush=True)
    finally:
        srv.shutdown()
        git('worktree', 'remove', '--force', wt)


def main():
    os.makedirs(OUT, exist_ok=True)
    raw = json.load(open(os.path.join(HERE, 'data', 'raw.json')))
    by = {c['sha']: c for c in raw['commits']}
    index_path = os.path.join(OUT, 'thumbs.json')
    index = json.load(open(index_path)) if os.path.exists(index_path) else {}
    turns = {}
    for f in glob.glob(os.path.join(HERE, 'data', 'areas', '*.json')):
        a = json.load(open(f))
        for d in a['directions']:
            for v in d['versions']:
                turns[v['sha'][:7]] = a['area']
    todo = []
    for sha, area in sorted(turns.items(), key=lambda x: by[x[0]]['t']):
        files = git('show', '--name-only', '--format=', sha).decode().split('\n')
        e = index.setdefault(sha, {})
        if 'pics' not in e:
            e['pics'] = pictures(sha, files)
        if 'shot' not in e and '--no-shots' not in sys.argv:
            todo.append((sha, page_for(area, files)))
    json.dump(index, open(index_path, 'w'))
    print(f'{len(turns)} turns, {sum(len(e["pics"]) for e in index.values())} pictures, {len(todo)} pages to shoot', flush=True)
    if todo:
        done = {}
        with tempfile.TemporaryDirectory() as tmp:
            # Each lane walks its turns in time order, so every checkout is a small step from the last.
            with ThreadPoolExecutor(LANES) as pool:
                list(pool.map(lambda n: lane(n, todo[n::LANES], tmp, done), range(min(LANES, len(todo)))))
        for sha, url in done.items():
            index[sha]['shot'] = {'src': f'{sha}.jpg', 'url': url}
        git('worktree', 'prune')
        json.dump(index, open(index_path, 'w'))
        print(f'shot {len(done)} of {len(todo)}')


if __name__ == '__main__':
    main()
