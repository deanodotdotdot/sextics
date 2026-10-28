import os
os.environ['SYMPY_GROUND_TYPES']='python'
import ast,json,pathlib,time,sys,hashlib
from sympy.polys.rings import ring
from sympy.polys.domains import QQ
sys.setrecursionlimit(50000);r=pathlib.Path(__file__).resolve().parents[1];st=time.time();checks={}
def load(n):return json.loads((r/n).read_text())
def check(n,b):assert b,n;checks[n]=True
def parse(s,R):
 if isinstance(s,int):return R(s)
 names=dict(zip(R.symbols,R.gens));names={str(k):v for k,v in names.items()};tree=ast.parse(s.replace('^','**'),mode='eval').body
 def rec(z):
  if isinstance(z,ast.Name):return names[z.id]
  if isinstance(z,ast.Constant):assert isinstance(z.value,int);return R(z.value)
  if isinstance(z,ast.UnaryOp):assert isinstance(z.op,ast.USub);return -rec(z.operand)
  assert isinstance(z,ast.BinOp);a=rec(z.left);b=rec(z.right)
  if isinstance(z.op,ast.Add):return a+b
  if isinstance(z.op,ast.Sub):return a-b
  if isinstance(z.op,ast.Mult):return a*b
  if isinstance(z.op,ast.Div):assert b.is_ground;return a.quo_ground(b.get((0,)*R.ngens,QQ.zero))
  if isinstance(z.op,ast.Pow):assert b.is_ground;return a**int(b.get((0,)*R.ngens,QQ.zero))
  raise ValueError(type(z.op))
 return rec(tree)
R,i,j,v=ring('i,j,v',QQ);S,x,a=ring('x,a',QQ)
bp='packet/coupled-fresh/ruling-source/full-base-connection/';ij=load(bp+'rank8-ij-connections-results.json');vr=load(bp+'rank8-v-literal-primitives-results.json');D=parse(ij['common_denominator'],R);G={t:[[parse(z,R) for z in row] for row in ij['Gamma_numerators'][t]] for t in ['i','j']};G['V']=[[parse(z,R) for z in row] for row in vr['GammaV_numerators']]
nums=[2*a*a-5*x-8,x+2-2*a*a,2*x**6];dens=[2*x*x,a*x,a*a*(x+2)];allp=[D]+[z for t in G for row in G[t] for z in row];caps=[max(z.degrees()[k] for z in allp) for k in range(3)];pp=[([n**k for k in range(d+1)],[b**k for k in range(d+1)]) for n,b,d in zip(nums,dens,caps)]
def pull(poly):
 out=S.zero
 for ee,c in poly.items():
  z=S(c)
  for k,e in enumerate(ee):z*=pp[k][0][e]*pp[k][1][caps[k]-e]
  out+=z
 return out
check('native D vanishes on critical cover',not pull(D));dip=pull(D.diff(i));djp=pull(D.diff(j));dvp=pull(D.diff(v));check('i normal nonzero',bool(dip));check('gradient j normal identity',x*djp==a*dip);check('gradient v normal identity',6*nums[2]*x*x*dvp==-3*(x+2)*dens[2]*dip)
model=load('critical-normalized-residue.json');den=parse(model['common_column_denominator'],S);column=[parse(z,S) for z in model['common_column_numerators']];ell=[(parse(z['n'],S),parse(z['d'],S)) for z in model['basis_evaluation_row']]
GP={t:[[pull(z) for z in row] for row in G[t]] for t in G};print('Independent pulled matrices',time.time()-st,flush=True)
for rr in range(8):
 check(f'normalized column {rr}',GP['i'][rr][0]*den==dip*column[rr])
 for cc in range(8):
  en,ed=ell[cc];check(f'i rank one {rr} {cc}',GP['i'][rr][cc]*ed==GP['i'][rr][0]*en);check(f'j rank one {rr} {cc}',x*GP['j'][rr][cc]==a*GP['i'][rr][cc]);check(f'V rank one {rr} {cc}',x*x*GP['V'][rr][cc]==-3*(x+2)*GP['i'][rr][cc])
# A polynomial common denominator proves nilpotency without rational-function gcds.
common=S.one
for en,ed in ell:common*=ed
z=S.zero
for u,(en,ed) in zip(column,ell):q,rem=common.div(ed);assert not rem;z+=u*en*q
check('normalized residue square zero',not z)
C=5*x*x+6*x*a*a+26*x+16*a*a+32;check('compact denominator formula',den==24*a**3*x**4*C)
# The same displayed row is the evaluation of the compact basis.
K=S.to_field();xx,aa=K.gens;ii=(2*aa*aa-5*xx-8)/(2*xx*xx);jj=(xx+2-2*aa*aa)/(aa*xx);vv=2*xx**6/(aa*aa*(xx+2));actual=[K.one,xx,xx**3,xx**4-vv*(ii-jj*jj/4)*(ii-5*jj*jj/4)*xx*xx/8,aa,aa*xx+jj*xx*xx/2,xx**3/aa,xx**4/aa]
for k,(en,ed) in enumerate(ell):check(f'basis evaluation {k}',K(en)/K(ed)==actual[k])
out={'status':'PASS','method':'Independent AST parser, pure Python rational sparse polynomials, full native substitution and cleared identities; no producing/FLINT imports','check_count':len(checks),'checks':checks,'seconds':time.time()-st};(r/'independent-critical-residue-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'identities',time.time()-st,flush=True)
