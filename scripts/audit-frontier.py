#!/usr/bin/env python3
"""Exact curation checks for the structured frontier targets.

Run with SageMath 10.1 or later: sage -python scripts/audit-frontier.py
Use --write to regenerate data/<id>/checks.json after reviewing target changes.
These checks establish the stated algebraic facts, not proof acceptance.
"""
import argparse
import itertools
import json
from pathlib import Path

import yaml
from sage.all import GF, QQ, IntegerVectors, PolynomialRing, matrix, prod, vector

ROOT = Path(__file__).resolve().parents[1]
IDS = (
    'reflection-coupled-fano', 'cyclic-triple-fano', 'split-ternary-q2',
    'crossed-ternary-asymmetric', 'polarized-k3-remainder',
    'klein-coupled-character', 'symmetric-sextic-residual',
    'rank-one-biquartic', 'quadric-contact-broken', 'four-plus-two-residual',
    'reflection-coupled-residual', 'cyclic-triple-residual',
)
R = PolynomialRing(QQ, names=('X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2'))
Z = R.gens()
R5 = PolynomialRing(GF(5), names=R.variable_names())


def exact_polynomial(record, name):
    return R(record[name])


def center_dimension(F):
    # A linear direct-sum decomposition gives a nonscalar projector T with
    # Hess(F) T = T^t Hess(F). Dimension one rules out every linear split,
    # including splits over C: this is a rational linear system.
    H = [[F.derivative(x).derivative(y).dict() for y in Z] for x in Z]
    rows = {}
    for i in range(6):
        for j in range(i):
            for k in range(6):
                for mon, coefficient in H[i][k].items():
                    row = rows.setdefault((i, j, mon), {})
                    row[6*k+j] = row.get(6*k+j, 0) + coefficient
                for mon, coefficient in H[j][k].items():
                    row = rows.setdefault((i, j, mon), {})
                    row[6*k+i] = row.get(6*k+i, 0) - coefficient
    M = matrix(QQ, len(rows), 36,
               {(n, j): c for n, row in enumerate(rows.values())
                for j, c in row.items()}, sparse=True)
    return int(36 - M.rank())


def euler_atoms(F, A):
    result = []
    for mask in range(1, 63):
        block = [i for i in range(6) if mask >> i & 1]
        split = all(sum(m[i] for i in block) in (0, 6) for m in F.exponents())
        balanced = all(sum(m[i] for i in block) + len(block) == 6
                       for m in A.exponents())
        if split and balanced:
            result.append(block)
    return result


def diagonal_screen(F, A):
    # Normalize the last diagonal entry to one. Pure sixth powers force all
    # entries into mu_6. For the Klein block, the equations instead give
    # weights (a,-5a,25a,21b,21c,0) modulo 126.
    if all(F.monomial_coefficient(z**6) for z in Z):
        order = 6
        space = (w + (0,) for w in itertools.product(range(6), repeat=5))
    else:
        assert all(F.monomial_coefficient(Z[i]**5 * Z[(i+1) % 3])
                   for i in range(3))
        order = 126
        space = ((a, (-5*a) % 126, (25*a) % 126, 21*b, 21*c, 0)
                 for a in range(126) for b in range(6) for c in range(6))
    group = []
    serving = []
    for weights in space:
        if any(sum(a*b for a, b in zip(m, weights)) % order
               for m in F.exponents()):
            continue
        group.append(weights)
        # A contributes its polynomial character; the residue volume adds
        # the determinant character. F itself is invariant in this lift.
        if any(sum((a+1)*b for a, b in zip(m, weights)) % order
               for m in A.exponents()):
            continue
        ages = []
        for weight in set(weights):
            block = [i for i in range(6) if weights[i] == weight]
            meets_X = len(block) >= 2 or not F.monomial_coefficient(Z[block[0]]**6)
            if meets_X:
                # At a fixed point of projective weight e, the normal line
                # of the invariant degree-six equation has weight -6e.
                ambient_age = sum((w-weight) % order for w in weights)
                ages.append(ambient_age - (-6*weight) % order)
        if any(0 < age < order for age in ages):
            serving.append(list(weights))
    return {'projectiveDiagonalGroupOrder': len(group),
            'juniorElementsFixingTarget': serving}


def fixed_quadratic(F, A, D):
    # AD in the Jacobian ideal is necessary for any legal certificate with
    # this D. Use ALL six cubic numerator components, without parity cuts.
    K = GF(101)
    S = PolynomialRing(K, names=R.variable_names())
    F, A, D = S(F), S(A), S(D)
    zz = S.gens()
    monomials = [prod(z**e for z, e in zip(zz, m)) for m in IntegerVectors(3, 6)]
    columns = [(F.derivative(z)*m).dict() for z in zz for m in monomials]
    rhs = (A*D).dict()
    exponents = set(rhs)
    for column in columns:
        exponents.update(column)
    rows = {m: i for i, m in enumerate(sorted(exponents))}
    M = matrix(K, len(rows), len(columns),
               {(rows[m], j): c for j, col in enumerate(columns)
                for m, c in col.items()}, sparse=True)
    b = vector(K, [rhs.get(m, 0) for m in sorted(exponents)])
    rank = M.rank()
    augmented = M.augment(matrix(K, len(rows), 1, list(b))).rank()
    # Full column rank is essential: a modular inconsistency by itself
    # need not imply inconsistency in characteristic zero.
    assert rank == len(columns) == 336 and augmented == 337
    return {'prime': 101, 'columns': len(columns), 'rank': int(rank),
            'augmentedRank': int(augmented)}


def audit(record):
    F, A = (exact_polynomial(record, name) for name in ('F', 'A'))
    q = record['q']
    assert all(sum(m) == 6 and sum(m[3:]) % 2 == 0 for m in F.exponents())
    assert all(sum(m) == 6*q and sum(m[3:]) % 2 == 1 for m in A.exponents())
    partials = [R5(F).derivative(z) for z in R5.gens()]
    assert set(partials) == {z**5 for z in R5.gens()}
    assert R5(A) != 0 and all(max(m) < 5 for m in R5(A).exponents())
    reflections = [i for i in range(6) if all(m[i] % 2 == 0 for m in F.exponents())]
    result = {
        'id': record['id'], 'smoothReductionPrime': 5,
        'reducedPartials': [str(p) for p in partials],
        'targetNonzeroInReducedJacobianRing': True,
        'coordinateReflections': reflections,
        'reflectionsServingTarget': [i for i in reflections
                                     if all(m[i] % 2 == 1 for m in A.exponents())],
        'subsetEulerAtoms': euler_atoms(F, A),
        'hessianSymmetrizerDimension': center_dimension(F),
        'diagonalSymmetryScreen': diagonal_screen(F, A),
    }
    if record['id'] == 'quadric-contact-broken':
        result['oldDenominatorE1'] = fixed_quadratic(F, A, Z[0]**2 + Z[3]**2)
    if record['id'] == 'polarized-k3-remainder':
        B = A.subs({Z[3]: Z[0], Z[4]: Z[1], Z[5]: Z[2]})
        result['diagonalTarget'] = str(B)
        assert B == Z[0]**2 * Z[1]**2 * Z[2]**2
        # Recover the exact ternary f from F(X,0); this reduction also proves
        # B/64 is nonzero in the K3 projection's ternary Jacobian component.
        f = F.subs({Z[3]: 0, Z[4]: 0, Z[5]: 0})
        assert [R5(f.derivative(z)) for z in Z[:3]] == [z**5 for z in R5.gens()[:3]]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    for rid in IDS:
        folder = ROOT / 'data' / rid
        record = yaml.safe_load((folder / 'instance.rec').read_text())
        assert record['id'] == rid
        result = audit(record)
        output = folder / 'checks.json'
        if args.write:
            output.write_text(json.dumps(result, indent=2) + '\n')
        else:
            assert json.loads(output.read_text()) == result, f'{rid}: stale checks.json'
        print(f'{rid}: exact curation checks passed', flush=True)


if __name__ == '__main__':
    main()
