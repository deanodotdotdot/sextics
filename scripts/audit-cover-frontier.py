#!/usr/bin/env python3
"""Exact curation checks for the two cover-deformation targets.

Run with Python content dependencies. --write regenerates checks.json.
These calculations establish the stated curation facts, not Lean acceptance.
"""
import argparse,itertools,json
import yaml
from pathlib import Path
import sympy as s
from sympy.polys.matrices import DomainMatrix
Z=s.symbols('X0 X1 X2 Y0 Y1 Y2'); x0,x1,x2,y0,y1,y2=Z
F0=sum(z**6 for z in Z)
Holdout=F0+x0**3*x1*y0*y1+x1**3*x2*y1*y2
ROOT=Path(__file__).resolve().parents[1]
IDS=('holdout-moving-branch','holdout-ternary-deformation')

def rank(cols):
 mons=sorted(set().union(*(c.keys() for c in cols)))
 M=s.SparseMatrix(len(mons),len(cols),{(i,j):c[m] for i,m in enumerate(mons) for j,c in enumerate(cols) if m in c})
 return DomainMatrix.from_Matrix(M).convert_to(s.QQ).rank()
def center_dimension(F):
 # A linear split supplies a nonscalar projector T satisfying Hess(F)T=T^t Hess(F).
 Hess=[[s.Poly(s.diff(F,a,b),*Z).as_dict() for b in Z] for a in Z]
 rows={}
 for i in range(6):
  for j in range(i):
   for k in range(6):
    for m,c in Hess[i][k].items():
     row=rows.setdefault((i,j,m),{});row[6*k+j]=row.get(6*k+j,0)+c
    for m,c in Hess[j][k].items():
     row=rows.setdefault((i,j,m),{});row[6*k+i]=row.get(6*k+i,0)-c
 M=s.SparseMatrix(len(rows),36,{(n,j):c for n,row in enumerate(rows.values()) for j,c in row.items() if c})
 return 36-DomainMatrix.from_Matrix(M).convert_to(s.QQ).rank()
def diagonal(F,A):
 # Pure sixth powers force projective diagonal symmetries into mu_6.
 # The residue numerator includes the determinant character. A fixed coordinate
 # eigenspace meets F only when it has dimension at least two; the normal
 # character is -6*k=0, so tangent age equals the ambient sum below.
 fm=s.Poly(F,*Z).monoms();am=s.Poly(A,*Z).monoms();grp=[];fix=[];jun=[]
 for w0 in itertools.product(range(6),repeat=5):
  w=w0+(0,)
  if any(sum(a*b for a,b in zip(m,w))%6 for m in fm):continue
  grp.append(w)
  if any(sum((a+1)*b for a,b in zip(m,w))%6 for m in am):continue
  fix.append(w)
  ages=[]
  for k in set(w):
   if w.count(k)>=2:
    ages.append(sum((v-k)%6 for v in w))
  if any(0<v<6 for v in ages):jun.append(w)
 return {'groupOrder':len(grp),'targetFixingOrder':len(fix),'juniorElementsFixingTarget':jun}
def audit(name,F,A,q):
 F=s.expand(F);A=s.expand(A);pf=s.Poly(F,*Z);pa=s.Poly(A,*Z)
 assert all(sum(m)==6 and sum(m[3:])%2==0 for m in pf.monoms())
 assert all(sum(m)==6*q and sum(m[3:])%2==1 for m in pa.monoms())
 # A maximal-modulus coordinate has pure derivative modulus 6*M^5.
 # If its perturbation coefficient sum is <6, the gradient cannot vanish.
 loads=[sum(abs(c) for c in s.Poly(s.diff(F-F0,z),*Z).coeffs()) for z in Z]
 assert max(loads)<6
 out={'id':name,'F':str(F),'A':str(A),'q':q,'smoothness':{'method':'maximal-coordinate derivative estimate','bounds':list(map(str,loads)),'strictBound':6},'hessianSymmetrizerDimension':int(center_dimension(F)),'coordinateReflections':[str(z) for z in Z if s.expand(F.subs(z,-z)-F)==0],'diagonal':diagonal(F,A)}
 if q==1:
  cols=[s.Poly(z*s.diff(F,w),*Z).as_dict() for z in Z for w in Z]
  out['JacobianRanks']=[int(rank(cols)),int(rank(cols+[pa.as_dict()]))];assert out['JacobianRanks']==[36,37]
 # Keep precise obstruction to original coefficient curve, not universal claim.
 T,alpha,beta,y=s.symbols('T alpha beta y')
 cover=s.expand(F.subs({y0:alpha*T,y1:y,y2:beta*T}))
 reduced=s.Poly(cover,alpha).rem(s.Poly(alpha**6+beta**6-1,alpha)).as_expr()
 swap=s.expand(reduced.subs({T:y,y:T},simultaneous=True)-reduced)
 out['originalCoverSwapDifference']=str(swap)
 return out

def check(ident):
 record=yaml.safe_load((ROOT/'data'/ident/'instance.rec').read_text())
 assert record['id']==ident and record['q']==1
 F,A=(s.sympify(record[k]) for k in ('F','A'))
 result=audit(ident,F,A,record['q'])
 assert result['hessianSymmetrizerDimension']==1
 assert not result['coordinateReflections']
 assert not result['diagonal']['juniorElementsFixingTarget']
 if ident=='holdout-moving-branch':
  T,alpha,beta,y=s.symbols('T alpha beta y')
  assert s.expand(s.sympify(result['originalCoverSwapDifference'],locals={'alpha':alpha,'beta':beta,'T':T,'y':y})-x0**2*alpha**2*beta**2*(y**4-T**4)/7)==0
  assert s.expand(F.subs({x2:y2,y2:x2},simultaneous=True)-F)!=0
 else:
  assert result['originalCoverSwapDifference']=='0'
  T,y=s.symbols('T y');active=(x0,x1,x2,y,T)
  pure=sum(z**6 for z in active)
  f=s.expand(F.subs({y0:0,y1:0,y2:0}))
  G=f+y**6+T**6+y*T*x0**3*x1
  loads=[sum(abs(c) for c in s.Poly(s.diff(G-pure,z),*active).coeffs()) for z in active]
  assert max(loads)<6
  S,P=s.symbols('S P')
  H=f+P*x0**3*x1+S**3-3*S*P**2
  assert s.rem(s.diff(H,S),S**2-4*P**2,S)==9*P**2
  u,v,k=s.symbols('u v k')
  defect=s.expand((F-Holdout).subs({x0:u**2,x1:k*u*v,x2:v**2}))
  assert s.expand(defect-(k*u**11*v+2*k**5*u**5*v**7+u**2*v**10)/14)==0
  result['genericQuotientSmoothnessWitness']={'alpha':1,'beta':0,'coverGradientBounds':list(map(str,loads)),'branchDerivative':'9*P**2','weights':[1,1,1,2,2],'degree':6,'anticanonicalIndex':1,'ambientQuotientPoints':3,'quotientType':'1/2(1,1,1)'}
  result['originalConicDefect']=str(defect)
 return result

if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--write',action='store_true');args=parser.parse_args()
 for ident in IDS:
  result=check(ident);path=ROOT/'data'/ident/'checks.json'
  if args.write:path.write_text(json.dumps(result,indent=2)+'\n')
  else:assert json.loads(path.read_text())==result,f'{ident}: stale checks.json'
  print(f'{ident}: exact target, smoothness, and cover-method screens passed')
