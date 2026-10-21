#!/usr/bin/env python3
"""Exact coefficient, source, and elliptic-model screens for paired cubics.

These are curation calculations for the book, not Lean certificate checks.
Run with the content dependencies: python3 scripts/audit-jacobian-scope.py.
"""
import itertools
from pathlib import Path

import sympy as s
import yaml

ROOT = Path(__file__).resolve().parents[1]
Z = s.symbols('X0 X1 X2 Y0 Y1 Y2')
X, Y, W, T = s.symbols('x y z t')


def compositions(n, k):
    if k == 1:
        yield (n,)
    else:
        for i in range(n + 1):
            for rest in compositions(n - i, k - 1):
                yield (i,) + rest


def symmetry_scope():
    weights = (2, 1, 0, 3, 2, 1)
    equations, sources = [], []
    for e in compositions(6, 6):
        if any((e[i] + e[i + 3]) % 2 for i in range(3)):
            continue
        j = sum(e[3:])
        weight = sum(a * b for a, b in zip(e, weights)) % 6
        if j % 2 == 0 and weight == 0:
            equations.append(e)
        if j % 2 == 1 and weight == 3:
            sources.append(e)
    assert len(equations) == 26 and len(sources) == 22
    assert [sum(sum(e[3:]) == j for e in sources) for j in (1, 3, 5)] == [6, 10, 6]
    for e in sources:
        m = tuple((e[i] + e[i + 3]) // 2 for i in range(3))
        shift = sum(e[3:]) - 3
        weight = (4 * m[0] + 2 * m[1]) % 6
        for degree in (4, 6):
            # An invariant derivative has degree d-1 in cubic coefficients.
            exponents = [n + shift for n in range(0, 6 * (degree - 1) + 1, 2)
                         if n % 6 == weight]
            assert exponents and all(n % 6 == 0 for n in exponents)
            assert min(exponents) >= 0 and max(exponents) <= 6 * (degree - 1)
    print('26 equation monomials; 22 invariant sources, all passing polynomiality.')


def determinant(matrix):
    positive = ((0, 1, 2), (1, 2, 0), (2, 0, 1))
    return s.expand(sum((1 if p in positive else -1)
                        * matrix[0, p[0]] * matrix[1, p[1]] * matrix[2, p[2]]
                        for p in itertools.permutations(range(3))))


def invariants(cubic):
    """Recover the degree-four and degree-six invariants from the Hessian pencil.

    H = 3/8 det Hess(U), matching the integral-covariant normalization of §2.9.
    Every cubic coefficient of both pencil identities is checked afterward.
    """
    variables = (X, Y, W)
    matrix = s.hessian(cubic, variables)
    h = s.expand(s.Rational(3, 8) * determinant(matrix))
    hmatrix = s.hessian(h, variables)
    pencil = {}
    for degree in (1, 2):
        pencil[degree] = s.expand(s.Rational(3, 8) * sum(
            determinant(s.Matrix.hstack(*[
                hmatrix[:, i] if i in chosen else matrix[:, i] for i in range(3)]))
            for chosen in itertools.combinations(range(3), degree)))
    coefficient = lambda f: s.Poly(s.expand(f), *variables).coeff_monomial(X**3)
    a = coefficient(cubic)
    s4 = s.cancel(-coefficient(pencil[1]) / (81 * a))
    s6 = s.cancel(coefficient(pencil[2] - 81 * s4 * h) / (-s.Rational(2187, 4) * a))
    assert s.expand(pencil[1] + 81 * s4 * cubic) == 0
    assert s.expand(pencil[2] + s.Rational(2187, 4) * s6 * cubic - 81 * s4 * h) == 0
    return s.Poly(s4, T), s.Poly(-s6 / 4, T)


def quadric_residual_model():
    record = yaml.safe_load((ROOT / 'data/quadric-contact-residual/instance.rec').read_text())
    f = s.Poly(s.sympify(record['F']), *Z)
    cubic = 0
    for e, q in f.terms():
        assert all((e[i] + e[i + 3]) % 2 == 0 for i in range(3))
        assert sum(e[3:]) % 2 == 0
        # Set c1=2,c2=3 and t=v² in the paired quotient.
        cubic += (q * 2**e[4] * 3**e[5] * T**(sum(e[3:]) // 2)
                  * X**((e[0] + e[3]) // 2) * Y**((e[1] + e[4]) // 2)
                  * W**((e[2] + e[5]) // 2))
    a4, b6 = invariants(s.expand(cubic))
    assert (a4.degree(), b6.degree()) == (11, 18)
    assert s.gcd(a4, b6).degree() == 0
    assert (4 * a4**3 + 27 * b6**2).degree() == 36
    # Coprimality gives finite minimality; degree18 gives minimality at infinity.
    print('Quadric contact residual: coprime Jacobian coefficients of degrees 11,18;')
    print('minimal elliptic surface has chi(O)=3 at c1=2,c2=3 (hence generically).')


if __name__ == '__main__':
    symmetry_scope()
    quadric_residual_model()
