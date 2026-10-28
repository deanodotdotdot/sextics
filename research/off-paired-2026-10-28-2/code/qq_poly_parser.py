import ast
from sympy.polys.domains import QQ
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
