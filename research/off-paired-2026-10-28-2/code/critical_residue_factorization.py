from pathlib import Path
from flint import fmpq_mpoly_ctx,fmpq_mpoly
import json,time
r=Path(__file__).resolve().parents[1];st=time.time();C=fmpq_mpoly_ctx.get(('x','a'));x,a=C.gens();Z=C.constant(0);O=C.constant(1)
Nctx=fmpq_mpoly_ctx.get(('i','j','v'))
def np(z):return fmpq_mpoly(z,Nctx)
bp=r/'packet/coupled-fresh/ruling-source/full-base-connection';ij=json.loads((bp/'rank8-ij-connections-results.json').read_text());vr=json.loads((bp/'rank8-v-literal-primitives-results.json').read_text());D=np(ij['common_denominator']);G={t:[[np(z) for z in row] for row in ij['Gamma_numerators'][t]] for t in ['i','j']};G['V']=[[np(z) for z in row] for row in vr['GammaV_numerators']]
nums=[2*a*a-5*x-8,x+2-2*a*a,2*x**6];dens=[2*x*x,a*x,a*a*(x+2)];allp=[D]+[z for t in G for row in G[t] for z in row];caps=[max(z.degrees()[k] for z in allp) for k in range(3)];powers=[([n**k for k in range(d+1)],[b**k for k in range(d+1)]) for n,b,d in zip(nums,dens,caps)];B=O
for b,d in zip(dens,caps):B*=b**d
def pull(p):
 out=Z
 for ee,c in p.to_dict().items():
  term=C.constant(c)
  for k,e in enumerate(ee):term*=powers[k][0][e]*powers[k][1][caps[k]-e]
  out+=term
 return out
assert not pull(D);GP={t:[[pull(z) for z in row] for row in G[t]] for t in G};print('Pulled all192 native matrix entries',time.time()-st,flush=True)
# Row of critical values for the compact basis; common denominator for row3.
I,J,V=nums;di,dj,dv=dens
# Rebuild row3 with exact rational arithmetic rather than an oversized common denominator.
class F:
 def __init__(self,n,d=1):
  n=n if isinstance(n,fmpq_mpoly) else C.constant(n);d=d if isinstance(d,fmpq_mpoly) else C.constant(d);g=n.gcd(d);self.n=n//g;self.d=d//g
 def __add__(self,b):
  b=b if isinstance(b,F) else F(b);return F(self.n*b.d+b.n*self.d,self.d*b.d)
 __radd__=__add__
 def __neg__(self):return F(-self.n,self.d)
 def __sub__(self,b):return self+-b if isinstance(b,F) else self+F(-b)
 def __mul__(self,b):
  b=b if isinstance(b,F) else F(b);return F(self.n*b.n,self.d*b.d)
 __rmul__=__mul__
 def __truediv__(self,b):
  b=b if isinstance(b,F) else F(b);return F(self.n*b.d,self.d*b.n)
 def data(self):return {'n':str(self.n),'d':str(self.d)}
ii,jj,vv=[F(n,d) for n,d in zip(nums,dens)]
ell=[F(1),F(x),F(x**3),F(x**4)-vv*(ii-jj*jj/4)*(ii-5*jj*jj/4)*x*x/8,F(a),F(a*x)+jj*x*x/2,F(x**3,a),F(x**4,a)]
checks=[]
for row in range(8):
 for col in range(8):
  assert GP['i'][row][col]*ell[col].d==GP['i'][row][0]*ell[col].n
  assert x*GP['j'][row][col]==a*GP['i'][row][col]
  assert x*x*GP['V'][row][col]==-3*(x+2)*GP['i'][row][col]
  checks.append([row,col])
# Use first column of i-connection numerator as a common residue direction.
u=[F(GP['i'][row][0],B) for row in range(8)];nil=F(0)
for z,l in zip(u,ell):nil+=z*l
assert not nil.n
out={'status':'PASS exact factorization on the normalized critical cover','parametrization':{'i':ii.data(),'j':jj.data(),'v':vv.data(),'y':F(x**3,a).data()},'basis_evaluation_row':[z.data() for z in ell],'i_numerator_column0':[z.data() for z in u],'identities':['D=0','Gi_num = U*ell','Gj_num = (a/x)*U*ell','GV_num = -3*(x+2)/x^2*U*ell','ell*U=0'],'checks':len(checks)*3+2,'physical_normals':'Gi_phys numerator = (x^2-rho_i*(x+2)/2)/x^2 *U*ell; similarly j with a*x, w with0. rho_p=v_p/v. Common native D denominator understood.','scope':'Exact identities on the auxiliary critical cover, not a global compact-basis current or a descent certificate at intersecting discriminant branches.','seconds':time.time()-st}
(r/'critical-residue-factorization.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',out['checks'],'identities; U term counts',[(len(z.n.to_dict()),len(z.d.to_dict())) for z in u],time.time()-st,flush=True)
