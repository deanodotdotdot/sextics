import os
os.environ['SYMPY_GROUND_TYPES']='python'
import ast,json,time,sys,hashlib
from pathlib import Path
from sympy.polys.rings import ring
from sympy.polys.domains import QQ
sys.setrecursionlimit(50000)
R,i,j,w,v=ring('i,j,w,v',QQ);one=R.one;zero=R.zero
root=Path(__file__).resolve().parents[1];st=time.time();checks={}
def load(n):return json.loads((root/n).read_text())
def check(k,c):assert c,k;checks[k]=True
def parse(s):
 if isinstance(s,int):return R(s)
 tree=ast.parse(s.replace('^','**'),mode='eval').body;stack=[(tree,False)];vals={}
 while stack:
  z,seen=stack.pop()
  if not seen:
   stack.append((z,True))
   if isinstance(z,ast.BinOp):stack.extend([(z.right,False),(z.left,False)])
   elif isinstance(z,ast.UnaryOp):stack.append((z.operand,False))
  else:
   if isinstance(z,ast.Name):a={'i':i,'j':j,'w':w,'v':v}[z.id]
   elif isinstance(z,ast.Constant):assert isinstance(z.value,int);a=R(z.value)
   elif isinstance(z,ast.UnaryOp):assert isinstance(z.op,ast.USub);a=-vals.pop(id(z.operand))
   elif isinstance(z,ast.BinOp):
    a=vals.pop(id(z.left));b=vals.pop(id(z.right))
    if isinstance(z.op,ast.Add):a=a+b
    elif isinstance(z.op,ast.Sub):a=a-b
    elif isinstance(z.op,ast.Mult):a=a*b
    elif isinstance(z.op,ast.Div):assert b.is_ground;a=a.quo_ground(b[(0,0,0,0)])
    elif isinstance(z.op,ast.Pow):assert b.is_ground;a=a**int(b[(0,0,0,0)])
    else:raise ValueError(type(z.op))
   else:raise ValueError(type(z))
   vals[id(z)]=a
 return vals[id(tree)]
bp='packet/coupled-fresh/ruling-source/full-base-connection/';ij=load(bp+'rank8-ij-connections-results.json');vr=load(bp+'rank8-v-literal-primitives-results.json');D=parse(ij['common_denominator']);G={t:[[parse(x) for x in row] for row in ij['Gamma_numerators'][t]] for t in ['i','j']};G['V']=[[parse(x) for x in row] for row in vr['GammaV_numerators']]
Q=[zero]*8;Q[2]=j/6;Q[6]=R(QQ(2,3));Q[7]=i/3
for r in range(8):check(f'native source row {r}',(4*D if r==6 else zero)-G['V'][r][6]+2*i*G['i'][r][6]+j*G['j'][r][6]==sum((G['i'][r][k]*Q[k] for k in range(8)),zero)-(D/6 if r==7 else zero))
print('PASS eight source identities',round(time.time()-st,3),flush=True)
frame=load('native-logarithmic-frame.json')
for k,field in enumerate(frame['fields']):
 a=parse(field['Ei']);b=parse(field['Ej'].split(')/(2*j)')[0][1:]);c=parse(field['Ev_over_v']);h=parse(field['E_D_over_D'])
 check(f'log tangency {k}',2*j*a*D.diff(i)+b*D.diff(j)+2*j*c*v*D.diff(v)==2*j*h*D)
 for r in range(8):
  for s in range(8):check(f'log connection {k} {r} {s}',6*j*a*G['i'][r][s]+3*b*G['j'][r][s]+j*c*G['V'][r][s]==D*parse(field['six_j_connection_polynomial'][r][s]))
print('PASS logarithmic frame',round(time.time()-st,3),flush=True)
# Rename w to the auxiliary critical x for the resultant calculation.
model=load('critical-quartic-model.json');q=parse(model['critical_quartic'].replace('x','w'));h=parse(model['critical_value_relation'].replace('x','w'))
Rc=ring('w,i,j,v',QQ)[0]; qc=q.set_ring(Rc); hc=h.set_ring(Rc)
check('critical quartic defining resultant',R.from_expr(qc.resultant(hc).as_expr())==2187*D)
check('critical quartic discriminant',R.from_expr(qc.discriminant().as_expr())==parse(model['quartic_discriminant']))
print('PASS independent exact resultant and discriminant',round(time.time()-st,3),flush=True)
(root/'independent-new-identities-audit.json').write_text(json.dumps({'status':'PASS','method':'Independent AST parser and pure Python QQ polynomial arithmetic; no producer or FLINT imports','checks':checks,'check_count':len(checks),'seconds':time.time()-st},indent=2)+'\n')
