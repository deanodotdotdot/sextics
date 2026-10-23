#!/usr/bin/env python3
"""Export the exact fixed-section norm described in display-divisor.md.

Requires python-flint. No algebraic roots are approximated. The source plane is
numerical geometry; sliceRestriction prevents reuse on a different saved plane.
"""
import json
from pathlib import Path
import re

from flint import fmpq as Q, fmpq_mat as Matrix, fmpq_poly as Poly

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'data/quadric-contact-broken'


def norm_coefficients():
    mu, nu = Q(2, 5), Q(13, 20)
    p, q, s = -40*mu**2, -40*mu*nu, -40*nu**2
    ki = Q(20, 7)*mu*(1-2*nu**2)
    K, u, v = -ki**2, 16*(1-mu**6), 16*(1-nu**6)
    source = (FOLDER / 'GenericEliminant.lean').read_text()
    env = dict(p=p, q=q, s=s, K=K, u=u, v=v)
    coefficients = []
    for i in range(28):
        expression = re.search(r'def eliminantCoeff'+str(i)+r' .*? := (.*)', source)[1]
        if not re.fullmatch(r'[0-9pqs kuv*+^()\-]+', expression):
            raise ValueError('Unexpected eliminant expression')
        def even_power(match):
            exponent = int(match[1])
            if exponent % 2:
                raise ValueError('Expected even powers of k in the eliminant')
            return 'K^'+str(exponent//2)
        expression = re.sub(r'k\^(\d+)', even_power, expression)
        coefficients.append(eval(expression.replace('^', '**'), {'__builtins__': {}}, env))
    P = Poly(coefficients)/coefficients[-1]
    r = Poly([0, 1])
    h = v-u*r**3
    aa = h*h+K*r*r*(p*r*r-q*r+s)
    bb = v+2*u*r**3
    qa = 2*h*aa
    qb = K*r*(2*h*bb+h*h+K*r*r*(s-p*r*r))
    qc = K**2*r*r*h
    cd = aa*aa+2*K**3*r**6
    ce = 2*K*r*aa*bb
    cf = K**2*r*r*(bb*bb+p*K*r**4)
    cg = u*K**3*r**6
    L = cd*(qb*qb-qa*qc)-ce*qa*qb+cf*qa*qa
    M = cd*qb*qc-ce*qa*qc+cg*qa*qa
    g, inverse, _ = L.xgcd(P)
    if g != 1 or not P[0]:
        raise ValueError('The line chart is singular on this section')
    xi = (-M*inverse)%P
    eta = r*xi%P
    inverse_r = r.xgcd(P)[1]
    z = ((aa*xi+K*r*bb)*inverse_r**3/ki**3)%P
    w = (r*z-h*inverse_r/ki)%P
    # zeta=i*z, omega=i*w. Strip i from the six imaginary source rows.
    sources = [
        12*xi*xi*w-12*xi*eta*z+6*ki*xi,
        12*xi*eta*w-12*eta*eta*z-6*ki*eta,
        2*eta*z-2*xi*w,
        2*xi*z*w-2*eta*z*z-2*ki*z+2*p*eta-q*xi,
        -2*eta*z*w+2*xi*w*w+2*ki*w+q*eta-2*s*xi,
        (6*xi*xi+2*p)*(2*xi*w+eta*z+ki)-(6*xi*eta+q)*(3*xi*z),
        (6*xi*xi+2*p)*(3*eta*w)+(6*xi*eta+q)*(2*xi*w+eta*z+ki)
        -(6*xi*eta+q)*(xi*w+2*eta*z+ki)-(6*eta*eta+2*s)*(3*xi*z),
        (6*xi*eta+q)*(3*eta*w)-(6*eta*eta+2*s)*(xi*w+2*eta*z+ki),
    ]
    reduced = [f%P for f in sources]
    if not Matrix([[f[j] for j in range(8)] for f in reduced]).det():
        raise ValueError('The source minor is singular on this section')
    matrices = []
    for f in [xi, eta]:
        columns = [r**j*f%P for j in range(27)]
        matrices.append(Matrix([[f[i] for f in columns] for i in range(27)]))
    values = [(matrices[0]+c*matrices[1]).charpoly() for c in range(28)]
    result = {}
    for i in range(28):
        differences, row = [], [f[i] for f in values]
        while row:
            differences.append(row[0])
            row = [row[j+1]-row[j] for j in range(len(row)-1)]
        polynomial, term = Poly([0]), Poly([1])
        for j in range(28-i):
            polynomial += term*differences[j]
            term = term*Poly([-j, 1])/(j+1)
        for j, value in enumerate(polynomial):
            if value:
                result[i, 27-i-j, j] = value
    return result


def program(coefficients):
    nodes, cache = [], {}

    def node(*instruction):
        if instruction not in cache:
            cache[instruction] = len(nodes)
            nodes.append(list(instruction))
        return cache[instruction]

    def rational(value):
        return node('rational', str(value))

    zero, one = rational(0), rational(1)

    def multiply(a, b):
        if a == zero or b == zero:
            return zero
        return b if a == one else a if b == one else node('mul', a, b)

    def add(a, b):
        return b if a == zero else a if b == zero else node('add', a, b)

    def power(a, n):
        return one if n == 0 else a if n == 1 else node('pow', a, n)

    x, a, c, y = [node('variable', j) for j in [0, 1, 2, 3]]
    S = multiply(rational(2), add(power(x, 2), power(y, 2)))
    B, C = power(a, 2), power(c, 2)
    scale = max(abs(value) for value in coefficients.values())
    result = zero
    for i in range(27, -1, -1):
        row, n = zero, 27-i
        for j in range(n, -1, -1):
            k = n-j
            row = add(multiply(row, B), multiply(rational(coefficients.get((i, j, k), 0)/scale), power(C, k)))
        result = add(multiply(result, S), row)
    return nodes, multiply(multiply(a, c), result)


def main():
    saved = json.loads((ROOT / 'slices/quadric-contact-broken.json').read_text())
    plane, signs = saved['planeMatrix'], saved['phaseSigns']
    if signs != [1, 1, 1, -1, -1, -1] or any(
        abs(a-ratio*b) > 2e-15
        for top, bottom, ratio in [(4, 1, 2/5), (5, 2, 13/20)]
        for a, b in zip(plane[top], plane[bottom])
    ):
        raise ValueError('This norm is for alpha=2i/5, beta=13i/20')
    coefficients = norm_coefficients()
    nodes, output = program(coefficients)
    display = {
        'schemaVersion': 1, 'kind': 'polynomial-program', 'degree': 56,
        'source': {'path': 'display-divisor.md', 'definition': 'Exact fixed-section norm of the cubic contact denominator'},
        'description': 'Same zero set as the explicit clearing on alpha=2i/5, beta=13i/20; all polynomial coefficients are exact rationals.',
        'sliceRestriction': {'planeMatrix': plane, 'phaseSigns': signs},
        'nodes': nodes, 'output': output, 'normalization': {'gradient': True},
    }
    (FOLDER / 'display-divisor.json').write_text(json.dumps(display, indent=2)+'\n')
    print(f'Wrote exact norm: {len(coefficients)} coefficients, {len(nodes)} program nodes.')


if __name__ == '__main__':
    main()
