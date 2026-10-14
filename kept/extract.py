#!/usr/bin/env python3
"""Kept, step one: lift the raw record out of a repo and its Claude Code sessions.

    python3 kept/extract.py [repo]          -> kept/data/raw.json

No model here. Every commit, the files it touched and the area they belong to;
every prompt typed into a session in that repo; and each prompt tied to the
commit that landed after it. A prompt with no commit after it is an ask that
never landed: a question, an abandoned try, or a turn that was talked out of.

Stdlib only. The output holds your own words from every session, so kept/data/
is gitignored and never ships.
"""
import json, os, re, subprocess, sys, glob
from datetime import datetime

REPO = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'raw.json')
SESSIONS = os.path.expanduser('~/.claude/projects/' + REPO.replace('/', '-'))

# Areas are the projects inside the repo. Order matters: first match wins.
AREAS = [
    ('preso',    'The deck',            r'^preso/'),
    ('multi',    'Multi-host calendar', r'^(multi|multi2|multical|recurrence)/'),
    ('peek',     'Peek',                r'^(peek|plush|rig|monsters|api)/'),
    ('explore',  'Explore map',         r'^explore/'),
    ('icons',    'Icon systems',        r'^(claude-icons|playful|icons|bento-widgets)/'),
    ('site',     'johnyum.com',         r'^(index\.html|img/|"img|Website_Images/|js/|vercel\.json)'),
]
SKIP = r'^(CLAUDE\.md|\.claude/|\.gitignore|test/|homes/|research/)'

# What pushing back sounds like. Matched on John's prompts, never the model's.
PUSHBACK = re.compile(r"\b(no+|nope|don'?t|dont|not|never|stop|undo|revert|go back|back to|instead|remove|get rid|"
                      r"too|weird|wrong|broke|broken|sucks?|janky|ugly|bad|hate|off|again|still|why)\b", re.I)
KEEP = re.compile(r'\b(love|perfect|great|nice|yes|good|better|keep|ship|push it|looks good)\b', re.I)


def area_of(path):
    if re.match(SKIP, path):
        return None
    for key, _, rx in AREAS:
        if re.match(rx, path):
            return key
    return None


def commits():
    log = subprocess.run(['git', '-C', REPO, 'log', '--reverse', '--format=%x00%H|%aI|%s', '--name-only'],
                         capture_output=True, text=True, check=True).stdout
    out = []
    for rec in log.split('\x00')[1:]:
        lines = [l for l in rec.split('\n') if l.strip()]
        sha, when, subj = lines[0].split('|', 2)
        files = lines[1:]
        areas = sorted({a for a in map(area_of, files) if a})
        slides = sorted({m.group(1) for f in files for m in [re.match(r'preso/slides/([0-9a-z]+)\.html', f)] if m})
        out.append({
            'sha': sha[:7], 't': int(datetime.fromisoformat(when.replace('Z', '+00:00')).timestamp()), 'msg': subj,
            'files': files[:12], 'nfiles': len(files), 'areas': areas, 'slides': slides,
            'revert': bool(re.match(r'(revert|back to|undo)', subj, re.I)),
        })
    return out


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        if any(isinstance(x, dict) and x.get('type') == 'tool_result' for x in content):
            return ''
        return ' '.join(x.get('text', '') for x in content if isinstance(x, dict) and x.get('type') == 'text')
    return ''


def prompts():
    out = []
    for f in glob.glob(SESSIONS + '/*.jsonl'):
        sid = os.path.basename(f)[:8]
        for line in open(f, errors='ignore'):
            if '"user"' not in line:
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if o.get('type') != 'user' or o.get('isMeta') or o.get('isSidechain'):
                continue
            t = text_of(o.get('message', {}).get('content')).strip()
            if (not t or t.startswith('<') or t.startswith('[Request interrupted')
                    or t.startswith('This session is being continued')):
                continue
            # Pasted files and @-mentions carry whole documents; keep what was typed.
            t = re.sub(r'@"[^"]+"', '@file', t)
            ts = o.get('timestamp')
            if not ts:
                continue
            out.append({
                't': int(datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()),
                'session': sid, 'text': t[:1200],
                'push': len(PUSHBACK.findall(t[:400])) > 0 and not KEEP.search(t[:60]),
            })
    out.sort(key=lambda p: p['t'])
    return out


def main():
    cs, ps = commits(), prompts()
    # Tie each prompt to the first commit within 3 hours after it.
    j = 0
    for p in ps:
        while j < len(cs) and cs[j]['t'] < p['t']:
            j += 1
        p['commit'] = cs[j]['sha'] if j < len(cs) and cs[j]['t'] - p['t'] < 3 * 3600 else None
    by = {c['sha']: c for c in cs}
    for c in cs:
        c['asks'] = 0
        c['push'] = 0
    for p in ps:
        if p['commit']:
            by[p['commit']]['asks'] += 1
            by[p['commit']]['push'] += p['push']
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump({
        'repo': os.path.basename(REPO),
        'made': int(datetime.now().timestamp()),
        'areas': [{'key': k, 'name': n} for k, n, _ in AREAS],
        'commits': cs, 'prompts': ps,
    }, open(OUT, 'w'))
    landed = sum(1 for p in ps if p['commit'])
    print(f'{len(cs)} commits, {len(ps)} prompts ({landed} landed, {len(ps) - landed} never did) -> {OUT}')


if __name__ == '__main__':
    main()
