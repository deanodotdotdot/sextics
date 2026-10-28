#!/usr/bin/env python3
"""Exact degree-24 ORIGINAL-target partial current; nonzero residual retained.

This is not a sextic certificate. It verifies E=F*R48, not E=F²*Q.
"""
import hashlib,json
from pathlib import Path
import sympy as s
from flint import fmpq_mpoly_ctx

HERE=Path(__file__).resolve().parent
C=fmpq_mpoly_ctx.get(('X0','X1','X2','Y0','Y1','Y2'))
X0,X1,X2,Y0,Y1,Y2=C.gens()
F=X0**6+X1**6+X2**6+Y0**6+Y1**6+Y2**6+X0**3*X1*Y0*Y1/2+X1**3*X2*Y1*Y2/2+X0**2*X1*X2*Y0*Y2/3
A=X0**3*Y0**3
m=X1**3*X2*Y1*Y2
K=3*X2**6*Y2**6*Y1**6-3*X2**6*Y2**6*X0**6-8*X2**6*Y0**6*Y1**6+X2**6*Y0**6*X0**6-X1**6*Y2**6*Y1**6+2*X1**6*Y2**6*X0**6
LR=3*(X1**6+X2**6)*((Y2**6-Y0**6)*X0**6+Y1**6*(3*Y0**6-Y2**6))
LK=2*(X1**6*Y2**6-X2**6*Y0**6)*(X0**6-2*Y1**6)
LZ=(X0**6+Y1**6)*(X1**6*Y2**6-X2**6*Y0**6)
D=3*m*K
N=[C.constant(0),2*A*X1*(K-LK),2*A*X2*(K+LR-LK),
   2*A*Y0*(3*LZ-2*LK-K),6*A*Y1*LZ,2*A*Y2*(LK+3*LZ-LR-K)]
R,S,W=s.symbols('R S W')
delta=3*R*S*W-3*R*S-8*R*W+R-S*W+2*S
nr=3*(1+R)*(S-1+W*(3-S));nk=2*(S-R)*(1-2*W);nz=(1+W)*(S-R)
pr=s.Poly(s.expand(2*(nz+nk-delta)*delta-(2*R*nr*s.diff(delta,R)+S*(6*nk-2*nr)*s.diff(delta,S)+6*W*nz*s.diff(delta,W))),R,S,W)
P36=C.constant(0)
for (r,ss,w),coef in pr.terms():
    assert max(r,ss,w)<=2
    P36+=int(coef)*X2**(6*r)*Y2**(6*ss)*Y1**(6*w)*X1**(12-6*r)*Y0**(12-6*ss)*X0**(12-6*w)
R48=18*A*m*P36
gradient=sum((N[k]*F.derivative(k) for k in range(6)),C.constant(0))
divN=sum((N[k].derivative(k) for k in range(6)),C.constant(0))
ND=sum((N[k]*D.derivative(k) for k in range(6)),C.constant(0))
E=A*D*D-D*gradient+F*(D*divN-ND)
assert E==F*R48
assert D and R48
assert all(sum(ex)==24 for ex in D.to_dict())
assert all(not p or all(sum(ex)==25 for ex in p.to_dict()) for p in N)
assert all(sum(ex)==48 for ex in R48.to_dict())
weights=[0,1,1,-1,0,-1]
assert sum((weights[k]*C.gens()[k]*D.derivative(k) for k in range(6)),C.constant(0))==3*D
_,rem=divmod(R48,F)
assert rem
def expr(p):return str(p).replace('^','**')
out={'status':'UNSOLVED: exact original-target PARTIAL current; not a certificate',
 'variable_order':['X0','X1','X2','Y0','Y1','Y2'],'q':1,'d':24,
 'F':expr(F),'A':expr(A),'D':expr(D),'N':[expr(p) for p in N],
 'remaining_R48':expr(R48),'factor_K18':expr(K),
 'remaining_P36':expr(P36),
 'verified_identity':'A*D^2-D*sum(N_i*F_i)+F*(D*divN-N.gradD)=F*R48',
 'checks':{'exact_cleared_original_identity':True,'D_nonzero':True,'D_homogeneous_degree24':True,
   'all_N_homogeneous_degree25':True,'R48_homogeneous_degree48':True,
   'Graw_D_equals_3D':True,'R48_nonzero':True,'F_does_not_divide_R48':True},
 'coprimality':'Mathematical argument supplied in DEGREE24-PARTIAL-HANDOFF.md; no Lean proof. D is Graw weight3, so every irreducible common factor would be weight-homogeneous and divide both disjoint F weight components X1^6+X2^6 and Y0^6+Y2^6, impossible.',
 'verification':'Native exact rational multivariate polynomial arithmetic; no numerical sampling.',
 'not_verified':'No full certificate, Lean theorem, kernel verification, CI, acceptance or publication.'}
path=HERE/'degree24-partial-current.json';path.write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'verified_identity':'E=F*R48','certificate':False,'D_degree':24,'N_degree':25,
 'R48_terms':len(R48.to_dict()),'R48_not_divisible_by_F':True,'path':str(path),
 'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))
