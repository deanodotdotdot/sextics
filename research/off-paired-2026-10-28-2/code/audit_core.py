"""Independent exact polynomial audit support; no producing code imports."""
from pathlib import Path
import json,time,hashlib
from flint import fmpq_mpoly_ctx,fmpq_mpoly,fmpq
ROOT=Path(__file__).resolve().parents[1]
CTX=fmpq_mpoly_ctx.get(('i','j','w','v'))
i,j,w,v=CTX.gens();zero=CTX.constant(0);one=CTX.constant(1)
def P(x):
 if isinstance(x,fmpq_mpoly):return x
 return fmpq_mpoly(x.replace('**','^'),CTX) if isinstance(x,str) else CTX.constant(x)
def read(name):return json.loads((ROOT/name).read_text())
def write(name,data):(ROOT/name).write_text(json.dumps(data,indent=2)+'\n')
def sha(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def exactdiv(a,b):
 q,r=divmod(a,b)
 assert not r,'Nonexact polynomial division'
 return q
class F:
 """Scalar field arithmetic only; global checks use polynomial exact division."""
 def __init__(self,n=0,d=1):
  if isinstance(n,F):self.n,self.d=n.n,n.d;return
  n,d=P(n),P(d);assert d
  g=n.gcd(d);n,d=exactdiv(n,g),exactdiv(d,g);c=d.leading_coefficient();self.n,self.d=n/c,d/c
 def __add__(a,b):
  b=F(b);return F(a.n*b.d+b.n*a.d,a.d*b.d)
 __radd__=__add__
 def __neg__(a):return F(-a.n,a.d)
 def __sub__(a,b):return a+-F(b)
 def __rsub__(a,b):return F(b)+-a
 def __mul__(a,b):
  b=F(b);return F(a.n*b.n,a.d*b.d)
 __rmul__=__mul__
 def __truediv__(a,b):
  b=F(b);return F(a.n*b.d,a.d*b.n)
 def diff(a,t):return F(a.n.derivative(t)*a.d-a.n*a.d.derivative(t),a.d*a.d)
 def __bool__(a):return bool(a.n)
 def data(a):return {'n':str(a.n),'d':str(a.d)}
 def __eq__(a,b):b=F(b);return a.n*b.d==b.n*a.d
def jf(z):return F(z['n'],z['d'])
def coeffs(z,var):
 idx=('i','j','w','v').index(var);d={}
 for exp,c in z.to_dict().items():
  e=list(exp);k=e[idx];e[idx]=0;d.setdefault(k,{})[tuple(e)]=c
 return {k:CTX.from_dict(a) for k,a in d.items()}
def trunc(z,n=7):return CTX.from_dict({e:c for e,c in z.to_dict().items() if e[0]<n})
def mul(a,b,n=7):return trunc(a*b,n)
def tpows(z,upto,n=7):
 a=[one]
 for k in range(upto):a.append(mul(a[-1],z,n))
 return a
T=1+w**3;N=9*i*i*w*w-16*j*j*T;L=256*T**5*N+729*i**6*j*j*w**6
AV=64*j*j*w*T*T*N;BV=9*i*i*L
vp=F(AV,BV);AP=F(9*i**3*w*T,j*j*N)
ij=read('packet/coupled-fresh/ruling-source/full-base-connection/rank8-ij-connections-results.json')
vr=read('packet/coupled-fresh/ruling-source/full-base-connection/rank8-v-literal-primitives-results.json')
D=P(ij['common_denominator']);assert D==P(vr['common_denominator'])
G={t:[[P(z) for z in row] for row in ij['Gamma_numerators'][t]] for t in ['i','j']};G['V']=[[P(z) for z in row] for row in vr['GammaV_numerators']]
_cache={}
def hom(z,degree,n=None):
 if n not in _cache:
  _cache[n]=(tpows(AV,degree,n),tpows(BV,degree,n)) if n is not None else ([AV**k for k in range(degree+1)],[BV**k for k in range(degree+1)])
 ap,bp=_cache[n]
 if len(ap)<=degree:
  _cache.pop(n);return hom(z,degree,n)
 out=zero
 for k,a in coeffs(z,'v').items():
  assert k<=degree
  term=a*ap[k]*bp[degree-k]
  out+=trunc(term,n) if n is not None else term
 return out
Delta=P(read('pole-inventory.json')['Delta']);Dh=hom(D,4);KD=exactdiv(Dh,i*i*Delta);assert KD.total_degree()==0
h=[0,0,2,2,0,0,1,2]
