"""Independent pure-Python QQ polynomial audit of the small cutoff construction.
No imports from any producing/audit support module; no FLINT arithmetic.
"""
import os
os.environ['SYMPY_GROUND_TYPES']='python'
import ast,json,time,sys
sys.setrecursionlimit(50000)
from pathlib import Path
from sympy.polys.rings import ring
from sympy.polys.domains import QQ
R,i,j,w,v=ring('i,j,w,v',QQ);one=R.one;zero=R.zero
root=Path(__file__).resolve().parents[1];st=time.time();checks={}
def load(n):return json.loads((root/n).read_text())
def out(s):print(s,'seconds',round(time.time()-st,3),flush=True)
def check(k,c):assert c,k;checks[k]=True
def parse(s):
 if isinstance(s,int):return R(s)
 if len(s)>10000 and '(' not in s:
  terms=s.replace(' - ',' + -').split(' + ');data={}
  for term in terms:
   zz=parse(term)
   assert len(zz)<=1
   for e,c in zz.items():data[e]=data.get(e,QQ.zero)+c
  return R.from_dict(data)
 tree=ast.parse(s.replace('^','**'),mode='eval').body;stack=[(tree,False)];values={}
 while stack:
  node,seen=stack.pop()
  if not seen:
   stack.append((node,True))
   if isinstance(node,ast.BinOp):stack.extend([(node.right,False),(node.left,False)])
   elif isinstance(node,ast.UnaryOp):stack.append((node.operand,False))
  else:
   if isinstance(node,ast.Name):z={'i':i,'j':j,'w':w,'v':v}[node.id]
   elif isinstance(node,ast.Constant):assert isinstance(node.value,int);z=R(node.value)
   elif isinstance(node,ast.UnaryOp):assert isinstance(node.op,ast.USub);z=-values.pop(id(node.operand))
   elif isinstance(node,ast.BinOp):
    a=values.pop(id(node.left));b=values.pop(id(node.right))
    if isinstance(node.op,ast.Add):z=a+b
    elif isinstance(node.op,ast.Sub):z=a-b
    elif isinstance(node.op,ast.Mult):z=a*b
    elif isinstance(node.op,ast.Pow):assert b.is_ground;z=a**int(b[(0,0,0,0)])
    elif isinstance(node.op,ast.Div):assert b.is_ground;z=a.quo_ground(b[(0,0,0,0)])
    else:raise ValueError('bad operation')
   else:raise ValueError('bad node')
   values[id(node)]=z
 return values[id(tree)]
def div(a,b):q,r=a.div(b);assert not r;return q
def trunc(a,n=7):return R.from_dict({e:c for e,c in a.items() if e[0]<n})
def mul(a,b):return trunc(a*b)
def subs0(a,idx):return R.from_dict({e:c for e,c in a.items() if not e[idx]})
def val(a,idx):return min((e[idx] for e in a),default=100000)
T=one+w**3;N=9*i*i*w*w-16*j*j*T;L=256*T**5*N+729*i**6*j*j*w**6
AV=64*j*j*w*T*T*N;BV=9*i*i*L
cur=load('simple-discriminant-current.json');Delta=parse(cur['Delta']);Ei=parse(cur['Ei']);EL=parse(cur['EL']);Hi=parse(cur['Hi']);HL=parse(cur['HL'])
check('i cutoff polynomial identity',Delta==Ei+i*Hi)
check('L cutoff polynomial identity',Delta==EL+L*HL)
for name,z in [('Ei',Ei),('EL',EL)]:div(z,j**8*w**3*T**8*N)
check('cutoff differences preserve j,w,T,N',True)
out('PASS two cutoff identities and common factors')
basepath='packet/coupled-fresh/ruling-source/full-base-connection/'
ij=load(basepath+'rank8-ij-connections-results.json');vr=load(basepath+'rank8-v-literal-primitives-results.json')
D=parse(ij['common_denominator']);G={t:[[parse(z) for z in row] for row in ij['Gamma_numerators'][t]] for t in ['i','j']};G['V']=[[parse(z) for z in row] for row in vr['GammaV_numerators']]
s=[1,1,0,0,1,1,0,0];h=[0,0,2,2,0,0,1,2]
for t,mat in G.items():
 for r in range(8):
  for k in range(8):check(f'native L degree {t} {r} {k}',max((e[3] for e in mat[r][k]),default=-100)<=4+s[r]-s[k])
for r in range(8):
 q=(4*D if r==6 else zero)-G['V'][r][6]+2*i*G['i'][r][6]+j*G['j'][r][6]
 check('source v degree '+str(r),max((e[3] for e in q),default=-100)<=4)
out('PASS 192 L matrix degree bounds and 8 actual-source degrees')
# Independent physical tangential i regularity via truncated polynomial
# homogenization; tests the actual cancellations, not saved matrix jets.
ap=[one];bp=[one]
for z,pp in [(AV,ap),(BV,bp)]:
 for k in range(5):pp.append(mul(pp[-1],z))
def hom(z):
 ans=zero;groups={}
 for exp,c in z.items():
  ee=list(exp);k=ee[3];ee[3]=0;groups.setdefault(k,{})[tuple(ee)]=c
 for k,a in groups.items():ans+=mul(mul(R.from_dict(a),ap[k]),bp[5-k])
 return trunc(ans)
gvh=[[hom(z) for z in row] for row in G['V']]
gjh=[[hom(z) for z in row] for row in G['j']]
rhoj=2*N*L+j*N.diff(j)*L-j*N*L.diff(j)
rhow=T*N*L+2*w*T.diff(w)*N*L+w*T*N.diff(w)*L-w*T*N*L.diff(w)
for t in ['j','w']:
 for r in range(8):
  for k in range(8):
   num=mul(rhoj,gvh[r][k])+mul(6*j*N*L,gjh[r][k]) if t=='j' else mul(rhow,gvh[r][k])
   check(f'i gauge regular {t} {r} {k}',val(num,0)>=4+h[r]-h[k])
 out('PASS 64 physical i-gauge cancellations '+t)
# Bind every saved small B coefficient to the original current using
# polynomial cross multiplication, with no field gcd algorithm.
wc=load('w-correction.json')
# Frozen c,d represented with one common small denominator.
cden=1620*i*w**3*j
cnum=-405*i*i*T*w*w+1008*T*T*j*j-896*j*j*(2-w**3)
dden=405*i*w*w;dnum=-448*T
for r,zz in enumerate(wc['Z']):
 zn,zd=parse(zz['n']),parse(zz['d'])
 pjn=j*(2-w**3)*zn; pjd=2*i*w**3*zd
 pwn=T*zn;pwd=i*w*w*zd
 if r==7:pjn,pjd=pjn*cden+cnum*pjd,pjd*cden;pwn,pwd=pwn*dden+dnum*pwd,pwd*dden
 for t,pn,pd in [('j',pjn,pjd),('w',pwn,pwd)]:
  b=cur['B'][t][r];bn,bd=parse(b['n']),parse(b['d'])
  check(f'B binding {t} {r}',bn*pd==i**7*L**3*pn*bd)
  check(f'i current bound {t} {r}',val(pn,0)-val(pd,0)-h[r]>=-7)
  # Raw j/w/N/T bounds follow by explicit small denominator support.
  rest=pd
  for p in [i,j,w,L]:
   while True:
    q,rem=rest.div(p)
    if rem:break
    rest=q
  check(f'base denominator support {t} {r}',rest.is_ground)
out('PASS all 16 current bindings and i bounds')
# The established after-w residual has only i,L,Delta denominators.
for r,row in enumerate(load('after-w-physical.json')['rows']):
 den=parse(row['d'])
 for p in [i,L,Delta]:
  while True:
   q,rem=den.div(p)
   if rem:break
   den=q
 check('prior residual denominator support '+str(r),den.is_ground)
check('no Pi direction',cur['Pi']=='0')
(root/'simple-discriminant-independent-audit.json').write_text(json.dumps({'status':'PASS','method':'Independent AST parser and pure-Python QQ polynomial arithmetic; no FLINT or producing imports','checks':checks,'groups':len(checks),'conclusion':'With K=(1-Ei/Delta)^7*(1-EL/Delta)^3, all eight exact compact residual coefficients lie in Q[i,j,w,1/Delta], power at most11','seconds':time.time()-st},indent=2)+'\n')
out('PASS complete independent cutoff audit')
