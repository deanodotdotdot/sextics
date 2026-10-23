#!/usr/bin/env python3
"""Exact checks for the three cubic-transfer frontier targets.

Run with the content dependencies: python3 scripts/audit-cubic-frontier.py.
Use --write to regenerate checks.json after reviewing target changes.
These rational calculations establish curation facts, not Lean acceptance.
"""
import argparse
import json
from pathlib import Path

import sympy as s
import yaml
from sympy.polys.matrices import DomainMatrix

ROOT = Path(__file__).resolve().parents[1]
Z = s.symbols('X0 X1 X2 Y0 Y1 Y2')
x, a, c, y, b, d = Z
IDS = ('quadric-contact-residual', 'one-reflection-y2-sector', 'one-reflection-skew')


def polynomial(record, name):
    return s.Poly(s.sympify(record[name]), *Z, domain=s.QQ)


def rank(columns):
    monomials = sorted(set().union(*(col.keys() for col in columns)))
    matrix = s.SparseMatrix(len(monomials), len(columns),
                           {(i, j): columns[j][m] for i, m in enumerate(monomials)
                            for j in range(len(columns)) if m in columns[j]})
    return DomainMatrix.from_Matrix(matrix).convert_to(s.QQ).rank()


def transform(poly, mapping):
    return s.Poly(poly.as_expr().subs(mapping, simultaneous=True), *Z, domain=s.QQ)


def check(ident):
    record = yaml.safe_load((ROOT / 'data' / ident / 'instance.rec').read_text())
    F, A = (polynomial(record, name) for name in ('F', 'A'))
    assert record['q'] == 1
    assert all(sum(e) == 6 for e in F.monoms() + A.monoms())
    involution = {y: -y, b: -b, d: -d}
    assert transform(F, involution) == F and transform(A, involution) == -A
    columns = [s.Poly(v * s.diff(F.as_expr(), w), *Z).as_dict() for v in Z for w in Z]
    ranks = [rank(columns), rank(columns + [A.as_dict()])]
    assert ranks == [36, 37]
    euler = []
    for mask in range(1, 63):
        block = [i for i in range(6) if mask >> i & 1]
        if (all(sum(e[i] for i in block) in (0, 6) for e in F.monoms())
                and all(sum(e[i] for i in block) + len(block) == 6 for e in A.monoms())):
            euler.append(block)
    assert not euler
    reflection_indices = [i for i, v in enumerate(Z) if transform(F, {v: -v}) == F]
    serving = [i for i in reflection_indices if transform(A, {Z[i]: -Z[i]}) == -A]
    result = {'id': ident, 'homogeneousDegrees': [6, 6], 'q': 1,
              'involutionParities': [1, -1], 'degreeSixJacobianRanks': ranks,
              'subsetEulerAtoms': euler,
              'coordinateReflections': [str(Z[i]) for i in reflection_indices],
              'coordinateReflectionsServingTarget': [str(Z[i]) for i in serving]}
    F0 = sum(v**6 for v in Z)
    if ident == 'quadric-contact-residual':
        # Reduction is Fermat mod 5, so its partials have no projective common zero.
        assert all(int(coef.p) % 5 == 0 and int(coef.q) % 5
                   for coef in s.Poly(F.as_expr() - F0, *Z).coeffs())
        result['smoothness'] = {'method': 'Fermat reduction', 'prime': 5}
        for exchange in ({x: y, y: x}, {a: b, b: a}):
            assert transform(F, exchange) == F and transform(A, exchange) == A
        result['densityObstruction'] = 'Target invariant under both X0/Y0 and X1/Y1 exchanges.'
    else:
        loads = [sum(abs(coef) for coef in s.Poly(s.diff(F.as_expr() - F0, v), *Z).coeffs())
                 for v in Z]
        assert max(loads) < 6
        result['smoothness'] = {'method': 'Maximal-coordinate derivative estimate',
                                'mixedDerivativeBounds': [str(t) for t in loads],
                                'pureDerivativeCoefficient': 6}
        if ident == 'one-reflection-y2-sector':
            # Each map and its determinant are fixed by its deck transformation,
            # while this target is odd under both commuting transformations.
            for eps in (1, -1):
                deck = {y: eps*b, b: eps*y, d: -d}
                coords = (x*x, y*b, d*d, (y**3-eps*b**3)/d, a/x, c/x)
                for f in coords:
                    assert s.cancel(f.subs(deck, simultaneous=True)-f) == 0
                determinant = 12*(y**3+eps*b**3)/x
                # The minus-map determinant has an irrelevant constant sign.
                assert s.cancel(determinant.subs(deck, simultaneous=True)-determinant) == 0
                assert transform(F, deck) == F and transform(A, deck) == -A
            assert serving == [5]
            result['densityObstruction'] = 'Odd under both deck transformations of the two binary-cubic maps.'
        else:
            assert transform(F, {y: b, b: y}) != F
            assert transform(F, {y: -b, b: -y}) != F
            assert reflection_indices == [5] and not serving
            result['brokenSymmetries'] = ['Y0/Y1 exchange', 'negative Y0/Y1 exchange']
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for instance_id in IDS:
        result = check(instance_id)
        path = ROOT / 'data' / instance_id / 'checks.json'
        if args.write:
            path.write_text(json.dumps(result, indent=2) + '\n')
        else:
            assert json.loads(path.read_text()) == result, f'{instance_id}: stale checks.json'
        print(f'{instance_id}: exact target, smoothness, and stated method screens passed')
