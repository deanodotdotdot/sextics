"""Standard-library-only independent exact proof of the stored augmented minor."""
import ast,json,time,hashlib
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];st=time.time();path=ROOT/'corrected-relative-i-screen-1-1-90.json';data=json.loads(path.read_text());cert=json.loads((ROOT/'corrected-relative-i-rank-witness.json').read_text());assert hashlib.sha256(path.read_bytes()).hexdigest()==cert['operator_input_sha256'];p=cert['prime']
def add(a,b,sign=1):
 d=dict(a)
 for k,v in b.items():d[k]=d.get(k,Fraction(0))+sign*v
 return {k:v for k,v in d.items() if v}
def mul(a,b):
 d={}
 for k,v in a.items():
  for l,w in b.items():d[k+l]=d.get(k+l,Fraction(0))+v*w
 return {k:v for k,v in d.items() if v}
def parse(text):
 def go(node):
  if isinstance(node,ast.Constant):assert isinstance(node.value,int);return {0:Fraction(node.value)}
  if isinstance(node,ast.Name):assert node.id=='i';return {1:Fraction(1)}
  if isinstance(node,ast.UnaryOp):
   out=go(node.operand)
   if isinstance(node.op,ast.USub):return {k:-v for k,v in out.items()}
   assert isinstance(node.op,ast.UAdd);return out
  assert isinstance(node,ast.BinOp)
  if isinstance(node.op,ast.Pow):
   a=go(node.left);b=go(node.right);assert set(b)<=set([0]);n=b.get(0,Fraction(0));assert n.denominator==1 and n>=0
   out={0:Fraction(1)}
   for k in range(n.numerator):out=mul(out,a)
   return out
  a,b=go(node.left),go(node.right)
  if isinstance(node.op,ast.Add):return add(a,b)
  if isinstance(node.op,ast.Sub):return add(a,b,-1)
  if isinstance(node.op,ast.Mult):return mul(a,b)
  assert isinstance(node.op,ast.Div) and set(b)==set([0]);return {k:v/b[0] for k,v in a.items()}
 out=go(ast.parse(text.replace('^','**'),mode='eval').body)
 return {k:v.numerator%p*pow(v.denominator%p,-1,p)%p for k,v in out.items()}
A=[[parse(z) for z in row] for row in data['operator_numerators']];B=[parse(z) for z in data['target_numerators']];D=parse(data['operator_denominator']);height=data['matrix_shape'][0]//8;bound=data['numerator_degree_bound'];M=[]
for idx in cert['selected_rows']:
 r,e=divmod(idx,height);row=[]
 for k in range(8):
  for n in range(bound+1):row.append((A[r][k].get(e-n,0)+(n*D.get(e-n+1,0) if r==k else 0))%p)
 row.append(B[r].get(e,0));M.append(row)
size=len(M);assert size==cert['unknown_count']+1;det=1
for k in range(size):
 pivot=next((r for r in range(k,size) if M[r][k]),None);assert pivot is not None
 if pivot!=k:M[k],M[pivot]=M[pivot],M[k];det=-det
 value=M[k][k];det=det*value%p;inv=pow(value,-1,p);top=M[k]
 for r in range(k+1,size):
  if not M[r][k]:continue
  factor=M[r][k]*inv%p;row=M[r]
  row[k+1:]=[(a-factor*b)%p for a,b in zip(row[k+1:],top[k+1:])];row[k]=0
 if k%100==0:print('verified pivot',k,'seconds',time.time()-st,flush=True)
assert det%p==cert['determinant_mod_prime']!=0
out={'status':'PASS','minor_size':size,'determinant_mod_prime':det%p,'prime':p,'arithmetic':'Python standard library fractions, integers and AST polynomial parser; no FLINT/SymPy','seconds':time.time()-st}
(ROOT/'corrected-rank-witness-independent-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
