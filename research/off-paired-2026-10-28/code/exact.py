from flint import fmpq_mpoly_ctx,fmpq_mpoly,fmpq
import json, pathlib
C=fmpq_mpoly_ctx.get(('i','j','w','v'));i,j,w,v=C.gens();ZERO=C.constant(0);ONE=C.constant(1)
def poly(x):
 if isinstance(x,fmpq_mpoly):return x
 if isinstance(x,str):return fmpq_mpoly(x.replace('**','^'),C)
 return C.constant(x)
class Rat:
 def __init__(self,n=0,d=1):
  if isinstance(n,Rat):self.n,self.d=n.n,n.d;return
  n,d=poly(n),poly(d)
  if not d:raise ZeroDivisionError
  if not n:self.n,self.d=ZERO,ONE;return
  g=n.gcd(d);n=n//g;d=d//g
  lead=d.leading_coefficient();self.n,self.d=n/lead,d/lead
 def __add__(a,b):
  b=Rat(b)
  if a.d==b.d:return Rat(a.n+b.n,a.d)
  g=a.d.gcd(b.d);x=a.d//g;y=b.d//g
  return Rat(a.n*y+b.n*x,a.d*y)
 __radd__=__add__
 def __neg__(a):return Rat(-a.n,a.d)
 def __sub__(a,b):return a+-Rat(b)
 def __rsub__(a,b):return Rat(b)+-a
 def __mul__(a,b):
  b=Rat(b)
  g=a.n.gcd(b.d);h=b.n.gcd(a.d)
  return Rat((a.n//g)*(b.n//h),(a.d//h)*(b.d//g))
 __rmul__=__mul__
 def __truediv__(a,b):
  b=Rat(b);return a*Rat(b.d,b.n)
 def __rtruediv__(a,b):return Rat(b)/a
 def __pow__(a,k):return Rat(a.n**k,a.d**k) if k>=0 else Rat(a.d**(-k),a.n**(-k))
 def diff(a,var):return Rat(a.n.derivative(var)*a.d-a.n*a.d.derivative(var),a.d*a.d)
 def __bool__(a):return bool(a.n)
 def __eq__(a,b):return not (a-Rat(b))
 def __str__(a):return str(a.n) if a.d==ONE else '('+str(a.n)+')/('+str(a.d)+')'
 def data(a):return {'n':str(a.n),'d':str(a.d)}
 def evaluate(a,mapping):return Rat(a.n.subs(mapping),a.d.subs(mapping))
R=Rat
HERE=pathlib.Path(__file__).resolve().parents[1]
PACKET=HERE/'packet'
def load(name):return json.loads((PACKET/name).read_text())
def matrices():
 ij=load('coupled-fresh/ruling-source/full-base-connection/rank8-ij-connections-results.json')
 vr=load('coupled-fresh/ruling-source/full-base-connection/rank8-v-literal-primitives-results.json')
 D=poly(ij['common_denominator']);DV=poly(vr['common_denominator']);assert D==DV
 G={k:[[poly(z) for z in row] for row in ij['Gamma_numerators'][k]] for k in ['i','j']};G['V']=[[poly(z) for z in row] for row in vr['GammaV_numerators']]
 return D,G,ij,vr
T=1+w**3;N=9*i*i*w*w-16*j*j*T;L=256*T**5*N+729*i**6*j*j*w**6
vp=R(64*j*j*w*T*T*N,9*i*i*L)
A=R(9*i**3*w*T,j*j*N)
Vj=R(j*(2-w**3),2*i*w**3);Vw=R(T,i*w*w)
c0=R(-i*T,4*w*j)+R(28*T*T*j,45*i*w**3)
c=c0-R(224*j*(2-w**3),405*i*w**3);d=R(-448*T,405*i*w*w)
def export(path,obj):pathlib.Path(path).write_text(json.dumps(obj,indent=2)+'\n')
