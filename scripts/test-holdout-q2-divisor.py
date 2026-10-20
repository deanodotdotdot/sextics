#!/usr/bin/env python3
"""Check the explicit pole-two clearing and its numerical display export."""
import importlib.util
from pathlib import Path
import json
import numpy as np
import sympy as sp
from flint import acb, acb_mat, acb_poly, arb, ctx

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('holdout_export',ROOT/'scripts/export-holdout-q2-divisor.py')
export=importlib.util.module_from_spec(spec);spec.loader.exec_module(export)

# Bound every eliminant coefficient in each passive parameter exactly.
x,y=sp.symbols('x y')
env=dict(a=1+x**6,b=1+y**6,c=x*y,d=y)
assert all(max(sp.degree(sp.expand(eval(e,{'__builtins__':{}},env)),z) for z in [x,y])<=66 for e in export.exprs)
# Uniform conservative bounds used in display-divisor.md.
t=66;K=3*t+6;U=t+6;A=17*t+60;B0=21*t+60
delta=27*B0;eta=27*(K+A);E=4*t+A+26*B0;G=1+U+B0+26*(K+A)
H=3*t+eta+1+delta
line=max(3*t+eta+1+E,2*t+eta+1+t+E,t+1+delta+G,delta+max(1+t+G,eta+K))
J=4*line+6;B=10*J
D=B+90+H+27*line
N=max(B+H+27*line+100,3*H+9*J+100+3*line+6+26*line,5*H+9*J+100+27*line)+3
assert max(D,N)<5_214_000<6_000_000
assert 2*(2*6_000_000+58)==24_000_116
print('Eliminant degree bounds and common-clearing bounds passed:',D,N)

# Independent exact matrix arithmetic in finite fields. These are diagnostics
# for the extracted rational formulas, not a replacement for the accepted proof.
for prime in [1009,10039]:
 p=prime;dim=27;I=np.eye(dim,dtype=np.int64)
 def scalar(v):return int(v)%p
 def mul(a,b):return a@b%p
 def power(a,n):
  r=I.copy()
  while n:
   if n&1:r=mul(r,a)
   a=mul(a,a);n//=2
  return r
 def det(a):
  a=a.copy()%p;v=1
  for i in range(len(a)):
   j=next((j for j in range(i,len(a)) if a[j,i]),None)
   if j is None:return 0
   if i!=j:a[[i,j]]=a[[j,i]];v=-v
   q=int(a[i,i]);v=v*q%p;a[i]=a[i]*pow(q,-1,p)%p
   for j in range(i+1,len(a)):a[j]=(a[j]-a[j,i]*a[i])%p
  return v%p
 def inverse(a):
  a=np.c_[a.copy()%p,I.copy()]
  for i in range(dim):
   j=next(j for j in range(i,dim) if a[j,i]);a[[i,j]]=a[[j,i]]
   a[i]=a[i]*pow(int(a[i,i]),-1,p)%p
   for j in range(dim):
    if j!=i:a[j]=(a[j]-a[j,i]*a[i])%p
  return a[:,dim:]
 def adj(a):return det(a)*inverse(a)%p
 def check(a,b):assert np.array_equal(a%p,b%p)
 for a,b,c,d in [(2,2,1,1),(3,4,2,5)]:
  env=dict(a=a,b=b,c=c,d=d);co=[int(eval(e,{'__builtins__':{}},env))%p for e in export.exprs];t=co[-1]
  R=np.zeros((dim,dim),dtype=np.int64);R[1:,:-1]=np.eye(26,dtype=np.int64);R[:,-1]=np.array(co[:-1])*pow(t,-1,p)*(-1)%p
  R2=power(R,2);R3=power(R,3);K=(a*R3-c*R2-b*I)%p;u=(c*I-3*a*R)%p;tt=(3*a*R-2*c*I)%p
  num=(27*d*d*mul(power(u,2),power(K,5))-d**8*mul(u,(2*mul(R2,power(tt,2))+mul(K,u))%p))%p
  den=12*mul(K,(27*a*power(K,6)+d**6*mul(R3,power(tt,3))+d**6*mul(mul(mul(K,R),tt),u))%p)%p
  e=mul(num,inverse(den));f=mul(R,e);g=d*mul(u,inverse(6*mul(K,e)%p))%p;h=(mul(R,g)+pow(d,-1,p)*K)%p
  R0=t*R%p;K0=pow(t,3,p)*K%p;U0=t*u%p;A0=pow(t,17,p)*num%p;B0=pow(t,21,p)*den%p
  de=det(B0);et=det(mul(K0,A0));E0=pow(t,4,p)*mul(A0,adj(B0))%p;G0=d*mul(mul(U0,B0),adj(mul(K0,A0)))%p
  H=6*pow(t,3,p)*et*d*de%p
  EH=scalar(6*pow(t,3,p)*et*d)*E0%p
  FH=scalar(6*pow(t,2,p)*et*d)*mul(R0,E0)%p
  GH=scalar(t*d*de)*G0%p
  JH=de*(d*mul(R0,G0)+6*et*K0)%p
  for v,w in zip([EH,FH,GH,JH],[e,f,g,h]):check(v,H*w)
  # Check all four line equations as matrix identities.
  check(power(e,3)-3*mul(e,power(g,2))+a*I,0*I)
  check(3*mul(power(e,2),f)-6*mul(mul(e,g),h)-3*mul(f,power(g,2))+c*I,0*I)
  check(3*mul(e,power(f,2))-3*mul(e,power(h,2))-6*mul(mul(f,g),h)+d*g,0*I)
  check(power(f,3)-3*mul(f,power(h,2))+b*I+d*h,0*I)
print('Exact finite-field checks: cleared line matrices and all line equations passed.')

display=json.loads((ROOT/'data/holdout-q2/fixed-slice-divisor.json').read_text())
rebuilt=export.factors_for(display,2048)
assert rebuilt['factors']==display['factors']
# Compare exported floating-point factors to independently isolated roots.
ctx.prec=2048
alpha,beta=[acb(*pair) for pair in display['checks']['ratios']]
lines,k,checks=export.chart(alpha,beta,2048)
rng=np.random.default_rng(20261019)
for point in rng.normal(size=(24,6)):
 signs=display['phaseSigns'];z=[acb(float(v))*(acb(0,1) if sign<0 else 1) for v,sign in zip(point,signs)]
 exact=acb(1)
 for e,f in lines:exact*=z[2]**2+k**2*z[5]**2-e*z[0]**2-f*z[1]**2
 numerical=complex(1)
 for factor in display['factors'][2:]:
  numerical*=sum(complex(*co)*np.prod(point**np.array(ex)) for co,ex in factor)
 assert abs(numerical-complex(exact))<=1e-11*max(abs(complex(exact)),1e-200)
print('Export regeneration and 24 independent high-precision norm comparisons passed.')
