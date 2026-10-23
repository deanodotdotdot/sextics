#!/usr/bin/env python3
"""Export the exact fixed-section norm explained in display-divisor.md.

Requires python-flint. All coefficient arithmetic is rational; no line roots are
approximated. The saved plane realizes alpha=23i/20, beta=3i/4 numerically.
"""
import json
from pathlib import Path
import re

from flint import fmpq as Q, fmpq_mat as Matrix, fmpq_poly as Poly

from norm_divisor import NormProgram, matrix_norm_coefficients

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'data/holdout-q2'


def norm_coefficients():
    mu, nu = Q(23, 20), Q(3, 4)
    a, b, c, D6 = 1-mu**6, 1-nu**6, -mu*nu, -nu**6
    source = (FOLDER / 'NewEliminant.lean').read_text()
    coefficients = []
    for j in range(28):
        expression = re.search(r'def coefficient'+str(j)+r' .*? := (.*)', source)[1]
        if not re.fullmatch(r'[0-9abcd*+^() \-]+', expression):
            raise ValueError('Unexpected eliminant expression')
        expression = expression.replace('((d)^12)', '(D6^2)').replace('((d)^6)', 'D6')
        if 'd' in expression:
            raise ValueError('Expected only sixth powers of d in the eliminant')
        coefficients.append(eval(expression.replace('^', '**'), {'__builtins__': {}},
                                 dict(a=a, b=b, c=c, D6=D6)))
    P = Poly(coefficients)/coefficients[-1]
    r = Poly([0, 1])
    K, t, u = a*r**3-c*r**2-b, 3*a*r-2*c, c-3*a*r
    num = -27*nu**2*u*u*K**5-nu**8*u*(2*r*r*t*t+K*u)
    den = 12*K*(27*a*K**6-nu**6*r**3*t**3-K*nu**6*r*t*u)

    def inverse(f):
        gcd, value, _ = f.xgcd(P)
        if gcd != 1:
            raise ValueError('The line chart is singular on this section')
        return value

    # For k²+k+1=0, the accepted line coordinates are
    # e=kE, f=kV, g=ikG, h=ikH. These four polynomials are rational.
    E = num*inverse(den)%P
    V = r*E%P
    G = nu*u*inverse(K*E)/6%P
    H = (r*G-K/nu)%P
    relations = [
        E**3+3*E*G**2+a,
        3*E*E*V+6*E*G*H+3*V*G*G+c,
        3*E*V*V+3*E*H*H+6*V*G*H-nu*G,
        V**3+3*V*H*H+b-nu*H,
    ]
    if any(f%P != 0 for f in relations) or P.gcd(P.derivative()) != 1:
        raise ValueError('Invalid cubic line algebra')
    L = 27*a*a*b+4*c**3
    if not L*(L**4+2916*a**8*nu**6):
        raise ValueError('The quintic correction is singular on this section')
    # Remove nonzero powers of i and k from the rows and gradient columns of
    # GenericQuadratic.minor; invertibility is unchanged (see the derivation).
    sources = [
        -18*E**3*H+18*E*E*V*G,
        6*nu*E*E-36*E*E*V*H+36*E*V*V*G,
        -18*E*E*H+18*E*V*G,
        18*E*G*H-18*V*G*G,
        6*nu*E*V-18*E*V*V*H+18*V**3*G,
        6*nu*E-18*E*V*H+18*V*V*G,
        12*nu*G+18*E*H*H-18*V*G*H,
        Poly(), Poly(), -18*E*H+18*V*G,
    ]
    sources = [f%P for f in sources]
    gradients = [
        [3*a, c, 0, 0], [2*c, 0, 0, 0], [0]*4, [0]*4,
        [0, 3*b, 0, nu], [0]*4, [0, -2*nu, 0, 0],
        [0, 0, 3, 0], [0, 0, 0, -6], [0, 0, -3, 0],
    ]
    if not Matrix([gradients[j]+[sources[j][i] for i in range(6)]
                   for j in range(10)]).det():
        raise ValueError('The source minor is singular on this section')
    matrices = []
    for f in [E, V]:
        columns = [r**j*f%P for j in range(27)]
        matrices.append(Matrix([[f[i] for f in columns] for i in range(27)]))
    return matrix_norm_coefficients(matrices)


def program(coefficients):
    p = NormProgram()
    x, a, c, d = [p.node('variable', j) for j in [0, 1, 2, 5]]
    C, D = p.power(c, 2), p.power(d, 2)
    negative = lambda value: p.multiply(p.rational(-1), value)
    S = p.multiply(p.rational(Q(1, 2)), p.add(
        negative(p.add(C, D)),
        p.multiply(p.node('sqrt', -3), p.add(D, negative(C)))))
    norm = p.evaluate(coefficients, S, p.power(x, 2), p.power(a, 2))
    output = p.multiply(p.multiply(x, a), norm)
    return p.nodes, output


def main():
    saved = json.loads((ROOT / 'slices/holdout-q2.json').read_text())
    plane, signs = saved['planeMatrix'], saved['phaseSigns']
    if signs != [1, 1, 1, -1, -1, -1] or any(
        abs(a-ratio*b) > 2e-15
        for top, bottom, ratio in [(3, 0, 23/20), (4, 1, 3/4)]
        for a, b in zip(plane[top], plane[bottom])
    ):
        raise ValueError('This norm is for alpha=23i/20, beta=3i/4')
    coefficients = norm_coefficients()
    nodes, output = program(coefficients)
    display = {
        'schemaVersion': 1, 'kind': 'polynomial-program', 'degree': 56,
        'source': {'path': 'display-divisor.md', 'definition': 'Exact fixed-section norm of the pole-two endpoint denominator'},
        'description': 'Same zero set as the explicit common clearing on alpha=23i/20, beta=3i/4; coefficients are exact rationals and sqrt(-3).',
        'sliceRestriction': {'planeMatrix': plane, 'phaseSigns': signs},
        'nodes': nodes, 'output': output, 'normalization': {'gradient': True},
    }
    (FOLDER / 'display-divisor.json').write_text(json.dumps(display, indent=2)+'\n')
    print(f'Wrote exact norm: {len(coefficients)} coefficients, {len(nodes)} program nodes.')


if __name__ == '__main__':
    main()
