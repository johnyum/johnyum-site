#!/usr/bin/env python3
"""Kept, step two: a model reads one area's record and names the directions in it.

    python3 kept/distill.py [area ...]      -> kept/data/areas/<area>.json

The engine is whatever CLI is in ENGINE: Claude Code headless by default, with
no tools, no session saved (a distill run must not make a new grave of its own)
and a JSON schema it has to answer in. Swap the command and the rest stands.

Everything the model says has to point at commits it was shown. The page drops
any sha it doesn't recognise, so an invented one never reaches the screen.
"""
import json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, 'data', 'raw.json')
OUT = os.path.join(HERE, 'data', 'areas')
NOTES = os.path.join(HERE, '..', 'CLAUDE.md')
ENGINE = os.environ.get('KEPT_ENGINE', 'claude')
MODEL = os.environ.get('KEPT_MODEL', 'opus')

SYSTEM = """You read the full working record of one designer, John, building one project with an AI coding agent over four months: every commit, and under each one the prompts he typed that led to it. You also get the project notes he kept by hand.

Your job is to give him back his own exploration, organised the way a designer thinks: by DIRECTION (an idea he was chasing), not by date and not as a tree.

Rules:
- A direction is one idea pursued across many commits ("the whale as a wood engraving", "the cast as a carousel"), not a single tweak. Aim for 6 to 16 per area. Merge small ones. Skip pure plumbing unless it cost him real effort.
- status: "settled" = it landed and he stopped changing it; "active" = still moving in the last week of the record; "set_aside" = he dropped or replaced it; "paused" = built, kept, switched off.
- why: one plain sentence. For set_aside, why he dropped it, in his words where the record has them. For settled, what he settled on.
- quotes: his own words, copied exactly from the prompts (typos and all), the ones that turned the direction. Never paraphrase inside a quote. None is fine.
- versions: the 2 to 8 commits that are the turning points, in order, each with a note under 12 words.
- confidence: how sure you are of the status, 0 to 1. Be honest: a direction with no clear ending is 0.5, not 0.9.
- lessons: things he learned that would save him time on the NEXT project, not this one. Specific and checkable ("a hidden browser pane pauses requestAnimationFrame, so drive frames by hand in tests"), never generic ("test early"). If a lesson is generic, leave it out. Silence beats filler.
- redone: things he asked for more than once because the first answer didn't hold, or that he built, removed and built again. Count the times.
- Every sha you cite must be one you were shown. Plain language. No em dashes. No hyperbole."""

SCHEMA = {
    'type': 'object', 'additionalProperties': False,
    'required': ['summary', 'directions', 'lessons', 'redone'],
    'properties': {
        'summary': {'type': 'string'},
        'directions': {'type': 'array', 'items': {
            'type': 'object', 'additionalProperties': False,
            'required': ['title', 'chasing', 'status', 'why', 'versions', 'quotes', 'confidence'],
            'properties': {
                'title': {'type': 'string'},
                'chasing': {'type': 'string'},
                'status': {'type': 'string', 'enum': ['active', 'settled', 'set_aside', 'paused']},
                'why': {'type': 'string'},
                'versions': {'type': 'array', 'items': {
                    'type': 'object', 'additionalProperties': False, 'required': ['sha', 'note'],
                    'properties': {'sha': {'type': 'string'}, 'note': {'type': 'string'}}}},
                'quotes': {'type': 'array', 'items': {'type': 'string'}},
                'confidence': {'type': 'number'},
            }}},
        'lessons': {'type': 'array', 'items': {
            'type': 'object', 'additionalProperties': False, 'required': ['lesson', 'kind', 'evidence'],
            'properties': {
                'lesson': {'type': 'string'},
                'kind': {'type': 'string', 'enum': ['craft', 'taste', 'tooling']},
                'evidence': {'type': 'array', 'items': {'type': 'string'}}}}},
        'redone': {'type': 'array', 'items': {
            'type': 'object', 'additionalProperties': False, 'required': ['what', 'times', 'evidence'],
            'properties': {
                'what': {'type': 'string'}, 'times': {'type': 'integer'},
                'evidence': {'type': 'array', 'items': {'type': 'string'}}}}},
    },
}


def record(raw, area):
    asks = {}
    for p in raw['prompts']:
        if p['commit']:
            asks.setdefault(p['commit'], []).append(p['text'])
    lines = []
    for c in raw['commits']:
        if area not in c['areas']:
            continue
        day = datetime.fromtimestamp(c['t']).strftime('%Y-%m-%d')
        lines.append(f"[{day} {c['sha']}] {c['msg']}")
        for t in asks.get(c['sha'], []):
            lines.append('    > ' + ' '.join(t.split())[:300])
    return '\n'.join(lines)


def distill(raw, area):
    with tempfile.TemporaryDirectory() as cwd:  # no project instructions picked up from here
        r = subprocess.run([ENGINE, '-p', '--model', MODEL, '--tools', '', '--no-session-persistence',
                            '--output-format', 'json', '--system-prompt', SYSTEM,
                            '--json-schema', json.dumps(SCHEMA)],
                           input=brief(raw, area), capture_output=True, text=True, cwd=cwd, timeout=1800)
    env = json.loads(r.stdout or '{}')
    if r.returncode or env.get('is_error'):
        raise RuntimeError(f"{area}: {env.get('result') or r.stderr[-800:]}")
    out = env.get('structured_output') or json.loads(env['result'])
    return finish(raw, area, out, MODEL, env.get('total_cost_usd'))


def brief(raw, area):
    name = next(a['name'] for a in raw['areas'] if a['key'] == area)
    fixes = ''
    log = os.path.join(HERE, 'data', 'corrections.jsonl')
    if os.path.exists(log):
        mine = [json.loads(l) for l in open(log) if l.strip()]
        mine = [c for c in mine if c.get('area') == area]
        if mine:
            fixes = ('# His corrections to your last reading. They are right; keep them.\n\n' +
                     '\n'.join(f"- {c.get('direction')}: {c.get('field')} -> {c.get('value')}"
                               + (f" (\"{c['note']}\")" if c.get('note') else '') for c in mine) + '\n\n')
    return (f'# Project notes (kept by hand)\n\n{open(NOTES).read()}\n\n{fixes}'
            f'# The record for area "{name}" ({area}), oldest first\n\n{record(raw, area)}')


def finish(raw, area, out, model, cost=None):
    """Keep only shas the area really has, stamp it, and write it where the page reads."""
    name = next(a['name'] for a in raw['areas'] if a['key'] == area)
    known = {c['sha'] for c in raw['commits'] if area in c['areas']}
    for d in out['directions']:
        d['versions'] = [v for v in d['versions'] if v['sha'][:7] in known]
    for x in out['lessons'] + out['redone']:
        x['evidence'] = [s for s in x['evidence'] if s[:7] in known]
    out.update(area=area, name=name, model=model, made=int(datetime.now().timestamp()), cost=cost)
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, area + '.json'), 'w'), indent=1)
    return f"{area}: {len(out['directions'])} directions, {len(out['lessons'])} lessons, {len(out['redone'])} redone"


def main():
    raw = json.load(open(RAW))
    args = sys.argv[1:]
    # --dump: write each area's brief to disk for an engine that isn't this CLI (an agent, another tool).
    # --ingest <area> <answer.json>: take that engine's answer through the same checks.
    if args[:1] == ['--dump']:
        d = os.path.join(HERE, 'data', 'briefs'); os.makedirs(d, exist_ok=True)
        json.dump({'system': SYSTEM, 'schema': SCHEMA}, open(os.path.join(d, 'instructions.json'), 'w'), indent=1)
        for a in args[1:] or [a['key'] for a in raw['areas']]:
            open(os.path.join(d, a + '.md'), 'w').write(brief(raw, a))
            print('wrote', os.path.join(d, a + '.md'))
        return
    if args[:1] == ['--ingest']:
        print(finish(raw, args[1], json.load(open(args[2])), os.environ.get('KEPT_MODEL', 'agent')))
        return
    areas = args or [a['key'] for a in raw['areas']]
    with ThreadPoolExecutor(len(areas)) as pool:
        for f in [pool.submit(distill, raw, a) for a in areas]:
            try:
                print(f.result(), flush=True)
            except Exception as e:
                print('FAILED', e, flush=True)


if __name__ == '__main__':
    main()
