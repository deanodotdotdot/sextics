#!/usr/bin/env python3
"""Compile local .rec and Markdown sources. No network access or proof acceptance."""
from datetime import date, datetime
from fractions import Fraction
import json
import re
import sys
from pathlib import Path
import sympy as sp

from content import render
from divisors import validate_program, validate_slice_identity
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parent / "proposals"))
from acceptance import exact_polynomial, read_acceptance, solution_record

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / 'assets/atlas'
outputs = {}

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
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(text)
    temporary.replace(path)

def dump(path, value):
    emit(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def polynomial(expression):
    variables = sp.symbols('X0 X1 X2 Y0 Y1 Y2')
    value = sp.Poly(exact_polynomial(expression, variables), *variables)
    terms = [[str(c), list(m)] for m, c in value.terms() if c]
    return {'expression': expression, 'latex': sp.latex(value.as_expr()),
            'degree': value.total_degree(), 'termCount': len(terms), 'terms': terms}


catalogue = json.loads((ROOT / 'data/catalogue.json').read_text())
presentation = json.loads((ROOT / 'assets/atlas-presentation.json').read_text())
summaries = []
credits = []
require(catalogue['schemaVersion'] == 2, 'Unsupported catalogue schema')
require(len(catalogue['instanceIds']) == len(set(catalogue['instanceIds'])), 'Duplicate instance ID')
for rid in catalogue['instanceIds']:
    require(re.fullmatch(r'[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*', rid), 'Invalid instance ID')
    folder = ROOT / 'data' / rid
    record = yaml.load((folder / 'instance.rec').read_text(), Loader=yaml.CSafeLoader)
    require(record['id'] == rid, f'{rid}: mismatched instance ID')
    require(record['q'] in (1, 2), f'{rid}: unsupported pole order')
    display = presentation[rid]
    for name in ('F', 'A'):
        record[name] = {**polynomial(record[name]), 'latex': display[name]}
    record['category'] = display['category']
    record['displayDefinitions'] = display['definitions']
    record['render'] = json.loads((ROOT / 'slices' / f'{rid}.json').read_text())
    record['evidenceKind'] = 'none'
    record['formalStatus'] = 'unproved'
    record['content'] = {'why': f'assets/atlas/{rid}/why.html'}
    emit(ATLAS / rid / 'why.html', render(prose(local_path(record['rationale'], folder)), root=ROOT, source_path=local_path(record['rationale'], folder)))
    if (folder / 'acceptance.json').is_file():
        solution = solution_record(ROOT, read_acceptance(ROOT, rid))
        witness = solution['witness']
        login = solution['solver']['githubLogin']
        require(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', login), f'{rid}: invalid GitHub identity')
        pull_request = solution['pullRequest']
        require(isinstance(pull_request, dict), f'{rid}: invalid pull request record')
        require(isinstance(pull_request.get('url'), str) and re.fullmatch(
            r'https://github\.com/hodge-computer/sextics/pull/[1-9][0-9]*', pull_request['url']),
            f'{rid}: expected a pull request URL in hodge-computer/sextics')
        for key in ('headCommit', 'mergeCommit'):
            require(isinstance(pull_request.get(key), str) and re.fullmatch(r'[0-9a-f]{40}', pull_request[key]),
                    f'{rid}: pull request {key} must be a full commit SHA')
        record['pullRequest'] = dict(pull_request)
        record['formalStatus'] = 'proved'
        record['evidenceKind'] = 'explicit-certificate' if 'D' in witness else 'existence-proof'
        record['certificate'] = dict(solution['witness'])
        if 'D' in record['certificate']:
            record['D'] = polynomial(record['certificate'].pop('D')['expression'])
            record['render']['divisorTerms'] = [[float(Fraction(c)), m] for c,m in record['D']['terms']]
        record['witnessAvailability'] = solution['witnessAvailability']
        record['leanVerification'] = solution['proof']
        display_divisor = ROOT / 'slices/divisors' / f'{rid}.json'
        if display_divisor.is_file():
            display = validate_program(json.loads(display_divisor.read_text()), ROOT)
            if 'sliceRestriction' in display:
                require(display['sliceRestriction'] == {key: record['render'][key] for key in ('planeMatrix', 'phaseSigns')},
                        f'{rid}: display divisor belongs to a different saved section')
            if 'D' in witness:
                validate_slice_identity(display, record['D'], record['render'], folder)
            else:
                require('sliceIdentity' not in display, f'{rid}: slice identity needs an explicit denominator')
            record['render']['divisorProgram'] = display
        submitted = solution.get('submittedAt')
        if isinstance(submitted, (date, datetime)):
            submitted = submitted.isoformat()
        require(submitted is None or isinstance(submitted, str), f'{rid}: invalid submission date')
        solution['submittedAt'] = submitted
        record['credit'] = {'githubLogin': login, 'origin': solution['creditOrigin'], 'awardedAt': submitted}
        record['content']['solution'] = f'assets/atlas/{rid}/solution.html'
        emit(ATLAS / rid / 'solution.html', render(prose(local_path(solution['explanation'], folder)), root=ROOT, source_path=local_path(solution['explanation'], folder)))
        accepted = solution['acceptedAt']
        accepted = accepted.isoformat() if isinstance(accepted, (date, datetime)) else accepted
        credits.append({'instanceId': rid, **record['credit'], 'acceptedAt': accepted})
    if record['formalStatus'] == 'unproved':
        require(not (ROOT / 'slices/divisors' / f'{rid}.json').exists(), f'{rid}: display divisor requires an accepted proof')
        record['witnessAvailability'] = 'missing'
    dump(ATLAS / rid / 'record.json', record)
    summary = {k: record[k] for k in ['id', 'title', 'formalStatus', 'evidenceKind', 'category', 'q']}
    summary['path'] = f'assets/atlas/{rid}/record.json'
    if 'credit' in record:
        summary['credit'] = record['credit']
    summaries.append(summary)
home = json.loads((ROOT / 'slices/home.json').read_text())
dump(ROOT / 'assets/home-scene.json', {key: home[key] for key in ['pairId', 'seed', 'mesh', 'camera']})
dump(ATLAS / 'index.json', {'schemaVersion': 2, 'records': summaries})
dump(ROOT / 'leaderboard/credits.json', {'schemaVersion': 2, 'basis': 'accepted-proofs', 'credits': credits})

doc_index = json.loads((ROOT / 'docs/index.json').read_text())
for page in doc_index['pages']:
    source = prose(local_path(page['source']))
    # The page shell supplies the title; retain all other chapter content.
    source = re.sub(r'^# [^\n]+\n', '', source, count=1)
    emit(local_path(page['content']), render(source))

if doc_index.get('overview'):
    emit(local_path(doc_index['overview']['content']), render(prose(local_path(doc_index['overview']['source']))))

# Delete only known generated exports, after every source has passed the build.
# Removing a solution must also retire its old downloadable explanation.
generated = [*ATLAS.glob('*/record.json'), *ATLAS.glob('*/why.html'), *ATLAS.glob('*/solution.html'), *ROOT.glob('docs/*.html')]
for path in generated:
    if path not in outputs:
        path.unlink()
for path, text in outputs.items():
    write_output(path, text)
print(f'Built {len(summaries)} instances, {len(credits)} credited constructions, and {len(doc_index["pages"])} chapters.')
