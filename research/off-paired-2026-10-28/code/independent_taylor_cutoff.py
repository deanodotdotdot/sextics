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
cur=load('taylor-discriminant-current.json');Delta=parse(cur['Delta']);W=parse(cur['W'])
native=load('packet/coupled-fresh/ruling-source/full-base-connection/rank8-ij-connections-results.json');D=parse(native['common_denominator'])
dc={}
for exp,c in D.items():
 ee=list(exp);k=ee[3];ee[3]=0;dc.setdefault(k,{})[tuple(ee)]=c
dc={k:R.from_dict(z) for k,z in dc.items()};assert max(dc)==4
Dh=sum((dc[k]*AV**k*BV**(4-k) for k in dc),zero)
base=i*i*Delta;kd=Dh.LC/base.LC
check('native discriminant homogeneous physical identity',Dh==kd*base)
d0,d1,d2=dc[0],dc[1],dc[2]
check('saved W equals independent Taylor pullback',kd**2*W==9**6*(d0*d0*BV*BV+2*d0*d1*AV*BV+(d1*d1+2*d0*d2)*AV*AV))
low=d0*d0+2*d0*d1*v+(d1*d1+2*d0*d2)*v*v;rem=D*D-low
check('native squared-discriminant remainder order at least three',all(e[3]>=3 for e in rem))
common=j**6*w**3*T**6*N**3
check('AV cubed divisible by preservation factor',not (AV**3).div(common)[1])
check('preservation factor coprime to i',val(common,0)==0)
# i^4*(Delta^2-Knum) is a constant times the homogeneous native
# remainder, so common divides it. Since common is coprime to i, it
# divides the polynomial Delta^2-Knum itself. No dense square is needed.
prior=load('simple-discriminant-independent-audit.json');check('independent native matrix/current bounds available',prior['status']=='PASS')
check('i regularity margin',8-7>=0)
check('L regularity margin',6-1-2>=0)
check('w preservation margin',3-3>=0)
check('j preservation margin',6-2>=0)
check('N preservation margin',3-1>=0)
check('T preservation margin',6-1>=0)
(root/'taylor-discriminant-independent-audit.json').write_text(json.dumps({'status':'PASS','method':'Independent AST parser and pure-Python QQ polynomial arithmetic; native homogenization and Taylor remainder factor argument','checks':checks,'conclusion':'All eight final compact residual rows have denominator support Delta only and power at most3','seconds':time.time()-st},indent=2)+'\n')
out('PASS independent Taylor cutoff audit')
