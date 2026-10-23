#!/usr/bin/env python3
"""Exact algebraic checks for four structured sextics.

Checks bind the compact presentations to the atlas targets, prove smooth
Fermat reduction and primitive targets, and screen specified linear symmetries,
finite-cover densities, and plane configurations. They do not exclude arbitrary
nonlinear correspondences or replace the accepted-proof workflow.
Run with --write to regenerate data/<id>/checks.json after reviewing changes.
"""
from pathlib import Path
from itertools import permutations, combinations
import argparse
import yaml
import json
import sympy as s

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--write", action="store_true", help="Regenerate checked algebraic summaries")
args = parser.parse_args()
z = s.symbols('X0 X1 X2 Y0 Y1 Y2')
X, Y = z[:3], z[3:]
fermat = sum(v**6 for v in z)
target = X[0]**3 * Y[0]**3
L = X[0]+2*X[1]+3*X[2]
M = Y[0]+3*Y[1]+5*Y[2]
quadrics = [
    X[0]**2+s.Rational(5,7)*(X[1]*X[2]+Y[0]*Y[1]),
    X[1]**2+s.Rational(5,11)*(X[0]*X[2]+Y[1]*Y[2]),
    X[2]**2+s.Rational(5,13)*(X[0]*X[1]+Y[0]*Y[2]),
    Y[0]**2+s.Rational(5,17)*(X[0]*X[1]+Y[1]*Y[2]),
    Y[1]**2+s.Rational(5,19)*(X[1]*X[2]+Y[0]*Y[2]),
    Y[2]**2+s.Rational(5,23)*(X[0]*X[2]+Y[0]*Y[1]),
]
plane_quartics = []
for i in range(3):
    l = sum((j+i+1)*X[j] for j in range(3))/7
    m = sum((2*j+i+1)*Y[j] for j in range(3))/11
    n = sum((j+1)**(i+1)*X[j] for j in range(3))/13
    o = sum((j+2)**(i+1)*Y[j] for j in range(3))/17
    plane_quartics.append(l**3*n+m**3*o+l**2*o**2)
orbits = [0,0,0]
for i,j,k in permutations(range(3)):
    orbits[0] += X[i]**3*X[j]*Y[i]*Y[j]
    orbits[1] += X[i]**3*X[j]*Y[k]**2
    orbits[2] += Y[i]**3*Y[j]*X[k]**2
candidates = {
    'short-power-presentation': fermat+s.Rational(5,7**7)*((L+M)**6+(L-M)**6),
    'quadratic-cubic-pullback': sum(q**3 for q in quadrics),
    'eight-plane-configuration': fermat+sum(s.Rational(5,p)*(X[i]**2+Y[i]**2)*plane_quartics[i] for i,p in enumerate((7,11,13))),
    'diagonal-permutation': fermat+sum(s.Rational(5,p)*o for p,o in zip((7,11,13),orbits)),
}
def mod(q,p):
    a,b=s.Rational(q).as_numer_denom()
    return int(a)*pow(int(b),-1,p)%p
def rank(rows,p):
    piv={}
    for row in rows:
        a=[int(x)%p for x in row]
        for i in range(len(a)):
            if not a[i]:continue
            if i in piv:
                r=piv[i];c=a[i];a=[(u-c*v)%p for u,v in zip(a,r)]
            else:
                c=pow(a[i],-1,p);piv[i]=[(u*c)%p for u in a];break
    return len(piv)
def symmetrizer(F,p=101):
    H=[[{e:mod(q,p) for e,q in s.Poly(s.diff(F,z[i],z[j]),*z).terms()} for j in range(6)] for i in range(6)]
    rows=[]
    for i,j in combinations(range(6),2):
        coeff={}
        for k in range(6):
            for e,q in H[k][j].items():
                coeff.setdefault(e,[0]*36)[6*i+k]+=q
            for e,q in H[i][k].items():
                coeff.setdefault(e,[0]*36)[6*j+k]-=q
        rows.extend(coeff.values())
    return 36-rank(rows,p)
def pairings(items):
    if not items:yield ();return
    a=items[0]
    for b in items[1:]:
        for r in pairings([i for i in items if i not in (a,b)]):yield ((a,b),)+r

out={}
for name,expected in candidates.items():
    record = yaml.safe_load((ROOT/"data"/name/"instance.rec").read_text())
    F = s.sympify(record["F"])
    assert s.expand(F-expected)==0
    A=target-X[1]**3*Y[1]**3 if name=='diagonal-permutation' else target
    assert s.expand(A-s.sympify(record['A']))==0
    F=s.expand(F);P=s.Poly(F,*z);terms=P.terms()
    assert all(sum(e)==6 and sum(e[3:])%2==0 for e,q in terms)
    red={e:mod(q,5) for e,q in terms if mod(q,5)}
    assert red=={tuple(6 if i==j else 0 for i in range(6)):1 for j in range(6)}
    # In characteristic five, the Jacobian ideal is (X0^5,...,Y2^5).
    assert all(max(e)<5 for e in s.Poly(A,*z).monoms())
    rec={'F':str(F),'A':str(A),'q':1,'term_count':len(terms),
         'smoothness':'Good reduction to Fermat modulo 5; six partials are the fifth powers.',
         'primitive_target':'Target survives the Jacobian ring modulo 5; smooth complete-intersection base change applies.',
         'hessian_symmetrizer_dimension_mod101':symmetrizer(F),
         'coordinate_reflections':[i for i in range(6) if all(e[i]%2==0 for e,q in terms)],
         'coordinate_paired_signs':[pairs for pairs in pairings(list(range(6))) if all(all((e[i]+e[j])%2==0 for i,j in pairs) for e,q in terms)],
         'scope':'Exact algebraic screening; not a certificate or a universal obstruction to other constructions.'}
    if name=='diagonal-permutation':
        for perm in permutations(range(3)):
            assert s.expand(F.xreplace({X[i]:X[perm[i]] for i in range(3)}|{Y[i]:Y[perm[i]] for i in range(3)})-F)==0
        rec['symmetry']='Simultaneous S3 on X and Y; transpositions have fixed codimension two, not reflections.'
    if name=='eight-plane-configuration':
        from itertools import product
        for signs in product((-1,1),repeat=3):
            assert s.expand(F.xreplace({Y[i]:signs[i]*s.I*X[i] for i in range(3)}))==0
        rec['planes']='Eight explicit planes Yi=+/- i Xi, exchanged by the involution.'
    if name=='quadratic-cubic-pullback':
        rec['quadrics']=[str(q) for q in quadrics]
        rec['known_density']='det(dQi/dzj), reducing to 64*X0*X1*X2*Y0*Y1*Y2 modulo 5; independent of A in the Jacobian ring.'
    if name=='short-power-presentation':
        rec['presentation']='Six coordinate sixth powers plus (5/7^7)*((L+M)^6+(L-M)^6); Waring rank eight over C.'
        rec['L']=str(L);rec['M']=str(M)
        def comps(n,k):
            if k==1:yield (n,);return
            for i in range(n+1):
                for rest in comps(n-i,k-1):yield (i,)+rest
        from math import factorial
        mon=list(comps(3,6));co=P.as_dict()
        cat=[[mod(co.get(tuple(x+y for x,y in zip(a,b)),0)*s.prod(s.Rational(factorial(x+y),factorial(y)) for x,y in zip(a,b)),101) for b in mon] for a in mon]
        rec['middle_catalecticant_rank_mod101']=rank(cat,101)
        assert rec['middle_catalecticant_rank_mod101']==8
    out[name]=rec
    print(name,{k:rec[k] for k in ('term_count','hessian_symmetrizer_dimension_mod101','coordinate_reflections','coordinate_paired_signs')},flush=True)

primary=out
ns={"candidates":candidates,"quadrics":quadrics}
from fractions import Fraction
from collections import Counter
out={}
# The apolar quadratic base locus of the rank-eight form is its eight power points.
points=[s.eye(6)[:,i] for i in range(6)]+[s.Matrix([1,2,3,1,3,5]),s.Matrix([1,2,3,-1,-3,-5])]
# Fourth powers are independent: odd and even mixed terms isolate the last two.
forms=[sum(points[j][i]*z[i] for i in range(6)) for j in range(8)]
monoms=sorted(set().union(*(s.Poly(f**4,*z).as_dict() for f in forms)))
quartic_matrix=s.Matrix([[s.Poly(f**4,*z).as_dict().get(e,0) for f in forms] for e in monoms])
assert quartic_matrix.rank()==8
assert all(s.Matrix.hstack(*(points[i] for i in ids)).rank()==4 for ids in combinations(range(8),4))
circuits=[list(ids) for ids in combinations(range(8),5) if s.Matrix.hstack(*(points[i] for i in ids)).rank()<5]
assert circuits==[[0,1,2,6,7],[3,4,5,6,7]]
scales=[1,2,3,1,3,5];u=[z[i]/scales[i] for i in range(6)]
within=[u[i]*u[j] for block in [(0,1,2),(3,4,5)] for i,j in combinations(block,2)]
cross=[u[i]*u[j] for i in range(3) for j in range(3,6)]
quadrics=[a-within[0] for a in within[1:]]+[a-cross[0] for a in cross[1:]]
F=s.expand(ns['candidates']['short-power-presentation'])
for q in quadrics:
 value=0
 for exp,coef in s.Poly(q,*z).terms():
  value+=coef*s.diff(F,*[v for v,e in zip(z,exp) for _ in range(e)])
 assert s.expand(value)==0
out['short-power-presentation']={'apolar_quadrics_verified':len(quadrics),'quartic_power_rank':8,'minimal_five_point_circuits':circuits,'linear_automorphisms':'Only global Y sign, projectively; see screening-note.md for the base-locus and coefficient argument.'}
# Smooth reduction implies flat graded Jacobian quotients. The two target
# reductions are distinct degree-six basis monomials in F5[z]/(z_i^5).
Q=ns['quadrics'];J=s.Matrix([[s.diff(q,v) for v in z] for q in Q])
# Reduce coefficients before taking the determinant to avoid expansion costs.
def reduce5(f):
 return s.Poly.from_dict({e:int(c.p)*pow(int(c.q),-1,5)%5 for e,c in s.Poly(f,*z).terms()},z).as_expr()
J5=J.applyfunc(reduce5);delta=s.Poly(J5.det(),*z).trunc(5).as_expr()
assert s.Poly(delta-s.prod(z)*4,*z).trunc(5).is_zero
A=X[0]**3*Y[0]**3
assert s.Poly(A,*z).monoms()!=s.Poly(delta,*z).monoms()
out['quadratic-cubic-pullback']={'density_mod5':str(delta),'target_mod5':str(A),'independent_in_jacobian':True,'q1_source_space_on_same_map':'weight zero, hence constants; linear reparametrization of quadrics changes density only by a scalar.'}
# Every nontrivial obvious finite quotient must be screened, not just reflections.
ages=[]
for name,base in [('identity',[0,0,0]),('transposition',[0,0,3]),('three-cycle',[0,2,4])]:
 for parity in [0,1]:
  if name=='identity' and not parity:continue
  weights=base+[(w+3*parity)%6 for w in base]
  strata=[{'weight':a,'eigenspace_dimension':n,'age':str(sum(Fraction((w-a)%6,6) for w in weights))} for a,n in Counter(weights).items() if n>=2]
  assert all(Fraction(t['age'])>=1 for t in strata)
  ages.append({'permutation':name,'global_involution':bool(parity),'fixed_strata':strata})
A=X[0]**3*Y[0]**3-X[1]**3*Y[1]**3
assert s.expand(sum(A.xreplace({X[i]:X[p[i]] for i in range(3)}|{Y[i]:Y[p[i]] for i in range(3)}) for p in permutations(range(3))))==0
out['diagonal-permutation']={'quotient_age_screen':ages,'target_S3_average':0,'residue_representation':'standard, dimension two; simultaneous permutation determinant is one.'}

for rid,check in primary.items():
    for key in ('F','A','status'): check.pop(key,None)
    check['extensions']=out.get(rid,{})
    path=ROOT/'data'/rid/'checks.json'
    encoded=json.dumps(check,indent=2)+'\n'
    if args.write:path.write_text(encoded)
    else:assert path.read_text()==encoded, f'{rid}: stale algebraic checks; run with --write'
print('Verified four exact targets, Fermat reductions, primitive classes, symmetrizers, and structural checks.')
