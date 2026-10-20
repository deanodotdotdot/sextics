#!/usr/bin/env python3
"""Export the explicit Holdout pole-two divisor on a fixed-ratio real slice.

See data/holdout-q2/display-divisor.md. Requires numpy and python-flint.
All root isolation and checks run offline; no algebraic solver runs in the browser.
"""
from pathlib import Path
import re,json,sys
from flint import acb,arb,acb_poly,acb_mat,ctx
ROOT=Path(__file__).resolve().parents[1]
exprs=[]
source=(ROOT/'data/holdout-q2/NewEliminant.lean').read_text()
for i in range(28):
 s=re.search(r'def coefficient'+str(i)+r' .*? := (.*)',source)[1]
 assert re.fullmatch(r'[0-9abcd*+^() \-]+',s)
 exprs.append(compile(s.replace('^','**'),'<eliminant>','eval'))
def chart(alpha,beta,bits=1024,endpoint=1):
 ctx.prec=bits
 k=(acb(-1,arb(3).sqrt())/2)**endpoint
 a,b,c,d=1+alpha**6,1+beta**6,alpha*beta,beta*k**2
 a,b,c,d=map(acb,[a,b,c,d])
 co=[eval(e,{'__builtins__':{}},dict(a=a,b=b,c=c,d=d)) for e in exprs]
 roots=acb_poly(co).roots(tol=arb(2)**(-bits//2),maxprec=4096)
 lines=[];sources=[]
 for r in roots:
  K=a*r**3-c*r**2-b;t=3*a*r-2*c;u=c-3*a*r
  num=27*d**2*u**2*K**5-d**8*u*(2*r**2*t**2+K*u)
  den=12*K*(27*a*K**6+d**6*r**3*t**3+K*d**6*r*t*u)
  assert not any(z.contains(0) for z in [K,num,den,d])
  e=num/den;f=r*e;g=d*u/(6*K*e);h=r*g+K/d
  rels=[e**3-3*e*g**2+a,3*e**2*f-6*e*g*h-3*f*g**2+c,3*e*f**2-3*e*h**2-6*f*g*h+d*g,f**3-3*f*h**2+b+d*h]
  assert all(z.contains(0) for z in rels)
  lines.append([e,f])
  sources.append([-18*e**3*h+18*e**2*f*g,6*d*e**2-36*e**2*f*h+36*e*f**2*g,-18*e**2*h+18*e*f*g,-18*e*g*h+18*f*g**2,6*d*e*f-18*e*f**2*h+18*f**3*g,6*d*e-18*e*f*h+18*f**2*g,-12*d*g-18*e*h**2+18*f*g*h,acb(0),acb(0),-18*e*h+18*f*g])
 polys=[acb_poly.interpolate(roots,[row[j] for row in sources]) for j in range(10)]
 gradients=[[3*a,c,0,0],[2*c,0,0,0],[0]*4,[0]*4,[0,3*b,0,d],[0]*4,[0,2*d,0,0],[0,0,3,0],[0,0,0,-6],[0,0,-3,0]]
 minor=acb_mat([gradients[j]+[polys[j][i] for i in range(6)] for j in range(10)])
 det=minor.det(); assert not det.contains(0)
 R=27*a*a*b+4*c**3;H=R*(R**4-2916*a**8*d**6);assert not H.contains(0)
 return lines,k,{'lineCount':len(lines),'minorRelativeAccuracyBits':det.rel_accuracy_bits(),'quinticRelativeAccuracyBits':H.rel_accuracy_bits()}

def factors_for(render,bits=2048):
 import numpy as np
 ctx.prec=bits
 plane=np.array(render['planeMatrix']); phases=render['phaseSigns']
 ratios=[]
 for i,j in [(3,0),(4,1)]:
  ratio=float(plane[i]@plane[j]/(plane[j]@plane[j]))
  if np.max(abs(plane[i]-ratio*plane[j]))>1e-14: raise ValueError('Slice parameters must be constant')
  phase=(acb(0,1) if phases[i]<0 else acb(1))/(acb(0,1) if phases[j]<0 else acb(1))
  ratios.append(phase*ratio)
 lines,k,checks=chart(*ratios,bits)
 other,k2,otherchecks=chart(*ratios,bits,endpoint=2)
 exponent=lambda j,n:[n if i==j else 0 for i in range(6)]
 factors=[[[[1,0],exponent(j,1)]] for j in [0,1]]
 # Both endpoint divisors are retained. Conjugate factors have identical zeros
 # on real amplitudes, and can be represented by one complex factor.
 coefficient_rows=[]
 for endpoint,unit in [(lines,k),(other,k2)]:
  for e,f in endpoint:
   row=[-e*phases[0],-f*phases[1],acb(phases[2]),unit**2*phases[5]]
   if any(all((a-b.conjugate()).contains(0) for a,b in zip(row,old)) for old in coefficient_rows): continue
   coefficient_rows.append(row)
 for row in coefficient_rows:
  if any(not z.is_finite() or z.rel_accuracy_bits()<40 for z in row):raise ValueError('Unresolved factor coefficient')
  factors.append([[[float(z.real),float(z.imag)],exponent(j,2)] for z,j in zip(row,[0,1,2,5])])
 checks.update(coefficientPrecisionBits=bits,endpointLineCounts=[len(lines),len(other)],renderedLineFactors=len(coefficient_rows),ratios=[[float(z.real),float(z.imag)] for z in ratios])
 return dict(schemaVersion=1,kind='factored-slice',degree=24000116,
  source={'path':'display-divisor.md','definition':'Explicit common clearing of the two endpoint certificates'},
  description='Support of an explicit, nonminimal common clearing of the accepted pole-two construction on this fixed-parameter slice. Algebraic coefficients are isolated numerically; this presentation export is not an additional Lean witness.',
  planeMatrix=render['planeMatrix'],phaseSigns=render['phaseSigns'],coordinateConvention='real-amplitudes',factors=factors,checks=checks)


if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--precision',type=int,default=2048)
 parser.add_argument('--slice',type=Path,default=ROOT/'data/holdout-q2/fixed-slice-divisor.json',help='JSON containing the fixed-ratio planeMatrix and phaseSigns')
 parser.add_argument('--output',type=Path,default=ROOT/'data/holdout-q2/fixed-slice-divisor.json')
 args=parser.parse_args()
 saved_slice=json.loads(args.slice.read_text())
 result=factors_for(saved_slice,args.precision)
 args.output.write_text(json.dumps(result,indent=2)+'\n')
 print('Exported',len(result['factors']),'factors; both sets of 27 line equations, coefficient units, and source minors checked.')
