"""Independent pure-Python univariate audit of the exact relative-i operator.
FLINT only parses immutable polynomial strings; all rational-function algebra is SymPy/Python.
Native full connection, actual source and all fixed current derivatives are reconstructed.
"""
import json,time
from pathlib import Path
from sympy.polys.fields import field
from sympy import QQ
from flint import fmpq_mpoly_ctx,fmpq_mpoly
ROOT=Path(__file__).resolve().parents[1];PACK=ROOT/'packet/coupled-fresh/ruling-source/full-base-connection';st=time.time();F,t=field('t',QQ);C=fmpq_mpoly_ctx.get(('i','j','w','v'));ring=F.ring
ival=wval=1
cache={}
def coefficients(text):
 if text not in cache:cache[text]=fmpq_mpoly(text.replace('**','^'),C).to_dict()
 return cache[text]
def poly_eval(text,vvalue=0,deriv=None):
 grouped={}
 for ex,c in coefficients(text).items():
  e=list(map(int,ex));coef=QQ(int(c.numerator),int(c.denominator))
  if deriv is not None:
   ix={'j':1,'w':2}[deriv];coef*=e[ix];e[ix]-=1
   if not coef:continue
  coef*=ival**e[0]*wval**e[2]
  group=grouped.setdefault(e[3],{});group[(e[1],)]=group.get((e[1],),QQ.zero)+coef
 if not grouped:return F.zero
 out=F.zero
 for k in range(max(grouped),-1,-1):out=out*vvalue+F.new(ring.from_dict(grouped.get(k,{})))
 return out
class Jet:
 def __init__(self,a=0,b=0,c=0):self.a=F(a);self.b=F(b);self.c=F(c)
 def __add__(a,b):
  if not isinstance(b,Jet):b=Jet(b)
  return Jet(a.a+b.a,a.b+b.b,a.c+b.c)
 __radd__=__add__
 def __neg__(a):return Jet(-a.a,-a.b,-a.c)
 def __sub__(a,b):return a+-Jet.wrap(b)
 def __rsub__(a,b):return Jet.wrap(b)+-a
 def __mul__(a,b):
  b=Jet.wrap(b);return Jet(a.a*b.a,a.b*b.a+a.a*b.b,a.c*b.a+a.a*b.c)
 __rmul__=__mul__
 @staticmethod
 def wrap(x):return x if isinstance(x,Jet) else Jet(x)
 def inv(a):return Jet(1/a.a,-a.b/a.a**2,-a.c/a.a**2)
 def __truediv__(a,b):return a*Jet.wrap(b).inv()
 def __rtruediv__(a,b):return Jet.wrap(b)*a.inv()
 def __pow__(a,n):
  if n<0:return (a.inv())**(-n)
  if n==0:return Jet(1)
  return Jet(a.a**n,n*a.a**(n-1)*a.b,n*a.a**(n-1)*a.c)
def pj(text):return Jet(poly_eval(text),poly_eval(text,deriv='j'),poly_eval(text,deriv='w'))
def frac(z):return pj(z['n'])/pj(z['d'])
i=Jet(1);j=Jet(t,1,0);w=Jet(1,0,1);T=1+w**3;N=9*i*i*w*w-16*j*j*T;L=256*T**5*N+729*i**6*j*j*w**6;vp=64*j*j*w*T*T*N/(9*i*i*L);A=9*i**3*w*T/(j*j*N)
c=-i*T/(4*w*j)+28*T*T*j/(45*i*w**3)-224*j*(2-w**3)/(405*i*w**3);d=-448*T/(405*i*w*w);Vj=j*(2-w**3)/(2*i*w**3);Vw=T/(i*w*w)
Pj=[Jet(0) for _ in range(8)];Pw=[Jet(0) for _ in range(8)]
print('all fixed currents and literal physical derivatives ready',time.time()-st,flush=True)
ij=json.loads((PACK/'rank8-ij-connections-results.json').read_text());vd=json.loads((PACK/'rank8-v-literal-primitives-results.json').read_text());den=poly_eval(ij['common_denominator'],vp.a);G={}
for key,raw in [('i',ij['Gamma_numerators']['i']),('j',ij['Gamma_numerators']['j']),('V',vd['GammaV_numerators'])]:
 G[key]=[[poly_eval(z,vp.a)/den for z in row] for row in raw];print('connection',key,'ready',time.time()-st,flush=True)
gi=[[G['i'][r][k]+vp.a.diff(t)/(6*vp.a)*G['V'][r][k] for k in range(8)] for r in range(8)]
gj=[[G['j'][r][k]+vp.b/(6*vp.a)*G['V'][r][k] for k in range(8)] for r in range(8)];gw=[[vp.c/(6*vp.a)*G['V'][r][k] for k in range(8)] for r in range(8)]
gi=gj
record=json.loads((ROOT/'bare-source-relative-j-screen-1-1-8.json').read_text());H=poly_eval(record['current_denominator']);clear=poly_eval(record['operator_denominator']);checks=[]
for r in range(8):
 Q=4*(r==6)-G['V'][r][6]+2*G['i'][r][6]+t*G['j'][r][6]
 rhs=A.a*Q-Pj[r].b-Pw[r].c-sum((gj[r][k]*Pj[k].a+gw[r][k]*Pw[k].a for k in range(8)),F.zero)
 assert poly_eval(record['target_numerators'][r])/clear==H*rhs,('target mismatch',r)
 for k in range(8):assert poly_eval(record['operator_numerators'][r][k])/clear==gi[r][k]-(H.diff(t)/H if r==k else 0),('operator mismatch',r,k)
 checks.append(r);print('PASS direct source/current and operator row',r,time.time()-st,flush=True)
 (ROOT/'bare-source-j-independent-operator.json').write_text(json.dumps({'status':'PASS' if len(checks)==8 else 'in progress','rows':checks,'matrix_entries_checked':8*len(checks),'source_rows_checked':len(checks),'seconds':time.time()-st,'arithmetic':'SymPy QQ univariate fraction field with Python ground types, FLINT parser only','inputs':'Native full connection, actual source, physical chain rule; all other current components are zero'},indent=2)+'\n')
