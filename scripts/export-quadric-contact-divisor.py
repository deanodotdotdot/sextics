#!/usr/bin/env python3
"""Export the zero set of an explicit clearing of the accepted cubic-contact field.

See data/quadric-contact-broken/display-divisor.md for the exact polynomial.
Requires numpy and python-flint. All expensive work is offline. Interval arithmetic
must isolate every coefficient; an unresolved coefficient stops the export.
"""
import gzip
import json
from pathlib import Path
import re

import numpy as np
import yaml
from flint import acb, arb, acb_mat, acb_poly, ctx

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'data/quadric-contact-broken'
SOURCE = (FOLDER / 'GenericEliminant.lean').read_text()
EXPRESSIONS = []
for i in range(28):
    text = re.search(r'def eliminantCoeff'+str(i)+r' .*? := (.*)', SOURCE)[1]
    if not re.fullmatch(r'[0-9pqs kuv*+^()\-]+', text):
        raise ValueError('Unexpected eliminant expression')
    EXPRESSIONS.append(compile(text.replace('^', '**'), '<eliminant>', 'eval'))


def real_log(value, imaginary=False):
    component = value.imag if imaginary else value.real
    other = value.real if imaginary else value.imag
    if not other.contains(0) or component.contains(0) or component.rel_accuracy_bits() < 40:
        raise ValueError(f'Unresolved real divisor factor: {value}, component bits {component.rel_accuracy_bits()}, other contains zero {other.contains(0)}')
    return (1 if component > 0 else -1), float(abs(component).log().mid())


def sample_at(z, bits, return_chart=False):
    ctx.prec = bits
    x0, a0, c0, y0, b0, d0 = map(float, z)
    # The saved phase convention is (real X, imaginary Y).
    if a0 == 0 or c0 == 0:
        return [0] * 16
    alpha, beta = acb(0, b0) / a0, acb(0, d0) / c0
    p, q, s = 40*alpha**2, 40*alpha*beta, 40*beta**2
    k = acb(20)/7*alpha*(1+2*beta**2)
    u, v = 16*(1+alpha**6), 16*(1+beta**6)
    env = dict(p=p, q=q, s=s, k=k, u=u, v=v)
    co = [eval(e, {'__builtins__': {}}, env) for e in EXPRESSIONS]
    P = acb_poly(co)
    roots = P.roots(tol=arb(2)**(-3*bits//4), maxprec=4096)
    if len(roots) != 27:
        raise ValueError('Eliminant did not isolate 27 roots')
    normL, normPole, sources, lines = acb(1), acb(1), [], []
    activeS, activeB, activeC = 2*(acb(x0)**2-acb(y0)**2), acb(a0)**2, acb(c0)**2
    for r in roots:
        h = v-u*r**3
        aa = h*h+k*k*r*r*(p*r*r-q*r+s)
        bb = v+2*u*r**3
        qa = 2*h*aa
        qb = k*k*r*(2*h*bb+h*h+k*k*r*r*(s-p*r*r))
        qc = k**4*r*r*h
        cd = aa*aa+2*k**6*r**6
        ce = 2*k*k*r*aa*bb
        cf = k**4*r*r*(bb*bb+p*k*k*r**4)
        cg = u*k**6*r**6
        L = cd*(qb*qb-qa*qc)-ce*qa*qb+cf*qa*qa
        M = cd*qb*qc-ce*qa*qc+cg*qa*qa
        xi = -M/L
        eta = r*xi
        zeta = (aa*xi+k*k*r*bb)/(k**3*r**3)
        omega = r*zeta+h/(k*r)
        if any(not value.is_finite() or value.rel_accuracy_bits() < 40 for value in [xi, eta, zeta, omega]):
            raise ValueError('Unresolved line coordinates')
        # Check all four coefficients of the cubic restricted to this line.
        relations = [2*xi**3+xi*zeta*zeta+p*xi+u,
                     6*xi*xi*eta+2*xi*zeta*omega+eta*zeta*zeta+q*xi+p*eta+k*zeta,
                     6*xi*eta*eta+xi*omega*omega+2*eta*zeta*omega+s*xi+q*eta+k*omega,
                     2*eta**3+eta*omega*omega+s*eta+v]
        if any(not rel.contains(0) for rel in relations):
            raise ValueError('Line failed a cubic coefficient identity')
        normL *= L
        normPole *= activeS-xi*activeB-eta*activeC
        lines.append((xi, eta))
        sources.append([12*xi*xi*omega-12*xi*eta*zeta+6*k*xi,
                        12*xi*eta*omega-12*eta*eta*zeta-6*k*eta,
                        2*eta*zeta-2*xi*omega,
                        -2*xi*zeta*omega+2*eta*zeta*zeta+2*k*zeta+2*p*eta-q*xi,
                        2*eta*zeta*omega-2*xi*omega*omega-2*k*omega+q*eta-2*s*xi,
                        (6*xi*xi+2*p)*(2*xi*omega+eta*zeta+k)-(6*xi*eta+q)*(3*xi*zeta),
                        (6*xi*xi+2*p)*(3*eta*omega)+(6*xi*eta+q)*(2*xi*omega+eta*zeta+k)
                        -(6*xi*eta+q)*(xi*omega+2*eta*zeta+k)-(6*eta*eta+2*s)*(3*xi*zeta),
                        (6*xi*eta+q)*(3*eta*omega)-(6*eta*eta+2*s)*(xi*omega+2*eta*zeta+k)])
    # Recover the power-basis coefficient minor used by sourceWeights, not a
    # trace functional or a different choice of eight lines.
    polys = [acb_poly.interpolate(roots, [row[j] for row in sources]) for j in range(8)]
    minor = acb_mat([[polys[i][j] for j in range(8)] for i in range(8)])
    factors = [real_log(acb(a0)), real_log(acb(c0)), real_log(u), real_log(v),
               real_log(k, imaginary=True), real_log(normL), real_log(minor.det()), real_log(normPole)]
    if return_chart:
        return lines
    return [item for factor in factors for item in factor]


def fixed_chart_factors(points, plane):
    """A parameter-constant slice avoids unnecessary high-degree interpolation.

    All coefficient-clearing factors are nonzero constants off a*c=0. Evaluate
    each real line factor and each complex-conjugate pair separately, preserving
    the support of the same global D. Coefficients are isolated at 4096 bits.
    """
    ratios = []
    for top, bottom in [(4, 1), (5, 2)]:
        row, base = np.array(plane[top]), np.array(plane[bottom])
        ratio = float(row @ base / (base @ base))
        if np.max(np.abs(row-ratio*base)) > 1e-14:
            return None
        ratios.append(ratio)
    mu, nu = ratios
    lines = sample_at([1, 1, 1, 1, mu, nu], 4096, return_chart=True)
    real_lines, paired_lines, remaining = [], [], list(lines)
    while remaining:
        xi, eta = remaining.pop()
        if xi.imag.contains(0) and eta.imag.contains(0):
            real_lines.append((float(xi.real), float(eta.real)))
        else:
            match = next((j for j,(a,b) in enumerate(remaining)
                          if (a-xi.conjugate()).contains(0) and (b-eta.conjugate()).contains(0)), None)
            if match is None:
                raise ValueError('Could not match conjugate line coordinates')
            remaining.pop(match)
            paired_lines.append((complex(xi), complex(eta)))
    x,a,c,y,_,_ = points.T
    exponents = lambda j,n: [n if k == j else 0 for k in range(6)]
    factors = [[[[1,0],exponents(j,1)]] for j in [1,2]]
    log_pole = np.zeros(len(points))
    sign_pole = np.ones(len(points))
    for xi,eta in real_lines+paired_lines:
        value = 2*(x*x-y*y)-xi*a*a-eta*c*c
        if isinstance(xi,complex):
            log_pole += 2*np.log(np.abs(value))
        else:
            log_pole += np.log(np.abs(value))
            sign_pole *= np.sign(value)
        factors.append([[[2,0],exponents(0,2)], [[-2,0],exponents(3,2)],
                        [[-complex(xi).real,-complex(xi).imag],exponents(1,2)],
                        [[-complex(eta).real,-complex(eta).imag],exponents(2,2)]])
    for j in np.linspace(0,len(points)-1,16,dtype=int):
        independent = sample_at(points[j],1024)
        if sign_pole[j] != independent[14] or abs(log_pole[j]-independent[15]) > 1e-7:
            raise ValueError('Fixed-chart factorization disagrees with the full norm evaluation')
    return factors, {'method':'constant-chart-factor-distance','ratios':ratios,
                   'realLines':len(real_lines),'conjugatePairs':len(paired_lines), 'coefficientPrecisionBits':4096,
                   'independentNormChecks':16}


def points_for_mesh(manifest):
    vertices = ROOT / 'assets/meshes' / manifest['vertices']
    data = np.frombuffer(gzip.decompress(vertices.read_bytes()), dtype='<f4').reshape(-1, 9)
    meta = manifest['meta']
    p = data[:, :3].astype('float64') * meta['displayScale'] + meta['centerOriginal']
    r2 = (p*p).sum(axis=1)
    sphere = np.c_[2*p/(1+r2)[:, None], (r2-1)/(r2+1)]
    return sphere @ np.array(meta['planeMatrix']).T


def main():
    record = yaml.safe_load((FOLDER / 'instance.rec').read_text())
    manifest = json.loads((ROOT / 'assets' / record['render']['mesh']).read_text())
    meta = manifest['meta']
    if meta['phaseSigns'] != [1, 1, 1, -1, -1, -1]:
        raise ValueError('This exporter expects the recorded real-X, imaginary-Y slice')
    points = points_for_mesh(manifest)
    fixed = fixed_chart_factors(points, meta['planeMatrix'])
    if fixed is None:
        raise ValueError('Choose a slice with both parameters fixed before exporting the factors')
    factors, checks = fixed
    display = {'schemaVersion': 1, 'kind': 'factored-slice', 'degree': 6000058,
               'source': {'path': 'display-divisor.md', 'definition': 'Explicit homogeneous clearing of GenericCubicCertificate'},
               'description': 'Support of the explicit nonminimal denominator on this fixed-parameter slice. Coefficients are numerical approximations to isolated algebraic roots; this is presentation data, not a new accepted proof package.',
               'planeMatrix': meta['planeMatrix'], 'phaseSigns': meta['phaseSigns'],
               'coordinateConvention': 'real-amplitudes', 'factors': factors, 'checks':checks}
    (FOLDER / 'fixed-slice-divisor.json').write_text(json.dumps(display, indent=2)+'\n')
    print('Wrote', len(factors), 'per-pixel factors; all 27 lines and 16 independent norm checks passed.', flush=True)


if __name__ == '__main__':
    main()
