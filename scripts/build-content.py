#!/usr/bin/env python3
"""Compile local .rec and Markdown sources. No network access or proof acceptance."""
import argparse
from datetime import date, datetime
from fractions import Fraction
import hashlib
import json
import re
import sys
from pathlib import Path

from content import render
from divisors import validate_display, validate_slice_identity
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent / "proposals"))
from acceptance import validate_solution

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--root', type=Path, default=ROOT, help=argparse.SUPPRESS)
parser.add_argument('--check', action='store_true', help='Fail if generated files are stale')
args = parser.parse_args()
ROOT = args.root.resolve()
stale = []
outputs = {}
checked_replay_receipts = {}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def local_path(relative, base=None):
    base = (base or ROOT).resolve()
    path = (base / relative).resolve()
    require(path.is_relative_to(base), f'Path leaves its content folder: {relative}')
    return path

def prose(path):
    text = path.read_text()
    require(text.strip() and not text.strip().startswith('<!--'), f'Missing prose: {path}')
    return text


def emit(path, text):
    outputs[path] = text

def write_output(path, text):
    if path.exists() and path.read_text() == text:
        return
    if args.check:
        stale.append(str(path.relative_to(ROOT)))
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(path.suffix + '.tmp')
        temporary.write_text(text)
        temporary.replace(path)

def dump(path, value):
    emit(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


catalogue = json.loads((ROOT / 'data/catalogue.json').read_text())
summaries = []
credits = []
require(catalogue['schemaVersion'] == 2, 'Unsupported catalogue schema')
require(len(catalogue['instanceIds']) == len(set(catalogue['instanceIds'])), 'Duplicate instance ID')
for rid in catalogue['instanceIds']:
    require(re.fullmatch(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', rid), 'Invalid instance ID')
    folder = ROOT / 'data' / rid
    record = yaml.load((folder / 'instance.rec').read_text(), Loader=yaml.CSafeLoader)
    require(record['id'] == rid, f'{rid}: mismatched instance ID')
    require(record.get('formalStatus', 'unproved') == 'unproved', f'{rid}: no formal acceptance without a checked theorem')
    require(record['q'] in (1, 2), f'{rid}: unsupported pole order')
    record = dict(record)
    for name, meta in record.pop('polynomialData').items():
        record[name] = {**meta, 'expression': record[name]}
    record['status'] = 'open'
    record['evidenceKind'] = 'none'
    record['certificateAvailable'] = False
    record['formalStatus'] = 'unproved'
    record['content'] = {'why': f'data/{rid}/why.html'}
    emit(folder / 'why.html', render(prose(local_path(record['rationale'], folder)), root=ROOT, source_path=local_path(record['rationale'], folder)))
    if (folder / 'solution.rec').is_file():
        solution = yaml.load((folder / 'solution.rec').read_text(), Loader=yaml.CSafeLoader)
        validate_solution(ROOT, rid, solution)
        witness = solution['witness']
        login = solution['solver']['githubLogin']
        require(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', login), f'{rid}: invalid GitHub identity')
        pull_request = solution.get('pullRequest')
        if pull_request is not None:
            require(isinstance(pull_request, dict), f'{rid}: invalid pull request record')
            require(isinstance(pull_request.get('url'), str) and re.fullmatch(
                r'https://github\.com/hodge-computer/sextics/pull/[1-9][0-9]*', pull_request['url']),
                f'{rid}: expected a pull request URL in hodge-computer/sextics')
            for key in ('headCommit', 'mergeCommit'):
                require(isinstance(pull_request.get(key), str) and re.fullmatch(r'[0-9a-f]{40}', pull_request[key]),
                        f'{rid}: pull request {key} must be a full commit SHA')
            record['pullRequest'] = dict(pull_request)
        record['status'] = 'solved'
        record['formalStatus'] = 'proved'
        record['evidenceKind'] = 'explicit-certificate' if 'D' in witness else 'existence-proof'
        record['certificateAvailable'] = True
        record['certificate'] = dict(solution['witness'])
        if 'D' in record['certificate']:
            record['D'] = record['certificate'].pop('D')
            record['render']['divisorTerms'] = [[float(Fraction(c)), m] for c,m in record['D']['terms']]
        record['witnessAvailability'] = solution['witnessAvailability']
        record['leanVerification'] = solution['proof']
        display_divisor = folder / 'display-divisor.json'
        if display_divisor.is_file():
            display = validate_display(json.loads(display_divisor.read_text()), folder, record['render'])
            if 'D' in witness:
                validate_slice_identity(display, witness['D'], record['render'], folder)
            else:
                require('sliceIdentity' not in display, f'{rid}: slice identity needs an explicit denominator')
            record['render']['divisorProgram'] = display
        submitted = solution.get('submittedAt')
        if isinstance(submitted, (date, datetime)):
            submitted = submitted.isoformat()
        require(submitted is None or isinstance(submitted, str), f'{rid}: invalid submission date')
        solution['submittedAt'] = submitted
        record['credit'] = {'githubLogin': login, 'origin': solution['creditOrigin'], 'awardedAt': submitted}
        record['content']['solution'] = f'data/{rid}/solution.html'
        emit(folder / 'solution.html', render(prose(local_path(solution['explanation'], folder)), root=ROOT, source_path=local_path(solution['explanation'], folder)))
        dump(folder / 'solution.json', solution)
        accepted = solution['acceptedAt']
        accepted = accepted.isoformat() if isinstance(accepted, (date, datetime)) else accepted
        credits.append({'instanceId': rid, **record['credit'], 'acceptedAt': accepted})
    if not record['certificateAvailable']:
        record['render'].pop('divisorTerms', None)
        record['render'].pop('divisorProgram', None)
        require(not (folder / 'display-divisor.json').exists(), f'{rid}: display divisor requires an accepted proof')
        record['witnessAvailability'] = 'missing'
    record['draftDisplayStatus'] = record['status']
    dump(folder / 'record.json', record)
    summary = {k: record[k] for k in ['id', 'title', 'status', 'formalStatus', 'evidenceKind', 'certificateAvailable', 'visibility', 'draftDisplayStatus', 'category', 'q']}
    summary['path'] = f'data/{rid}/record.json'
    if 'credit' in record:
        summary['credit'] = record['credit']
    summaries.append(summary)
dump(ROOT / 'data/index.json', {'schemaVersion': 2, 'records': summaries})
dump(ROOT / 'leaderboard/credits.json', {'schemaVersion': 2, 'basis': 'accepted-proofs', 'credits': credits})

doc_index = json.loads((ROOT / 'docs/index.json').read_text())
for page in doc_index['pages']:
    source = prose(local_path(page['source']))
    # The page shell supplies the title; retain all other chapter content.
    source = re.sub(r'^# [^\n]+\n', '', source, count=1)
    emit(local_path(page['content']), render(source))

if doc_index.get('overview'):
    emit(local_path(doc_index['overview']['content']), render(prose(local_path(doc_index['overview']['source']))))

# The revision changes for data, prose, navigation, or UI changes. It is written last.
digest = hashlib.sha256()
for path in sorted(outputs):
    digest.update(str(path.relative_to(ROOT)).encode())
    digest.update(outputs[path].encode())
for path in sorted({ROOT / 'index.html', ROOT / 'docs/index.json', *ROOT.glob('assets/*.js'), *ROOT.glob('assets/*.css'), *ROOT.glob('data/*/witness.json'), *ROOT.glob('data/*/provenance.json')}):
    digest.update(path.read_bytes())
# Delete only known generated exports, after every source has passed the build.
# Removing a solution must also retire its old downloadable explanation.
generated = [*ROOT.glob('data/*/record.json'), *ROOT.glob('data/*/solution.json'), *ROOT.glob('data/*/why.html'), *ROOT.glob('data/*/solution.html'), *ROOT.glob('docs/*.html')]
for path in generated:
    if path not in outputs:
        if args.check:
            stale.append(str(path.relative_to(ROOT)))
        else:
            path.unlink()
for path, text in outputs.items():
    write_output(path, text)
write_output(ROOT / 'data/revision.json', json.dumps({'revision': digest.hexdigest()}) + '\n')

if stale:
    sys.exit('Stale generated content:\n' + '\n'.join(stale))
print(f'{"Checked" if args.check else "Built"} {len(summaries)} instances, {len(credits)} credited constructions, and {len(doc_index["pages"])} chapters.')
