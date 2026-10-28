"""Geometrically motivated non-diagonal gauge at j=infinity."""
from audit_core import *
import sympy as sy
st=time.time();rho=2*N*L+j*N.derivative('j')*L-j*N*L.derivative('j');den=6*N*L*BV*Dh
A=[]
for r in range(8):
 row=[]
 for k in range(8):row.append(F(hom(6*j*N*L*G['j'][r][k]+rho*G['V'][r][k],5),den))
 A.append(row)
print('physical j*Gamma_j ready',round(time.time()-st,3),flush=True)
g=vp*F((i-j*j/4)*(i-5*j*j/4),4*j)
# T=I+g E_(5,3), corresponding to nu3 -> nu3+g nu5.
AA=[[A[r][k]+(g*A[r][5] if k==3 else 0)-(g*A[3][k] if r==5 else 0)-(g*g*A[3][5] if r==5 and k==3 else 0)+(j*g.diff('j') if r==5 and k==3 else 0) for k in range(8)] for r in range(8)]
print('unipotent basis shear ready',round(time.time()-st,3),flush=True)
degrees=[[int(z.n.degrees()[1]-z.d.degrees()[1]) if z else -10000 for z in row] for row in AA]
hh=[0]*8;success=False
for iteration in range(12):
 changed=False
 for r in range(8):
  for k in range(8):
   if AA[r][k] and hh[r]<hh[k]+degrees[r][k]:hh[r]=hh[k]+degrees[r][k];changed=True
 if not changed:success=True;break
out={'status':'PASS Fuchsian gauge' if success else 'diagonal step after shear failed','shear_g':g.data(),'unipotent_basis':'T=I+g*E_(5,3), zero-based indices','diagonal_j_powers':hh,'degrees':degrees,'seconds':time.time()-st}
if success:
 mat=[]
 for r in range(8):
  row=[]
  for k in range(8):
   z=AA[r][k];value=F(0)
   if z and degrees[r][k]+hh[k]-hh[r]==0:
    nn=coeffs(z.n,'j');dd=coeffs(z.d,'j');value=-F(nn[max(nn)],dd[max(dd)])
   row.append(value-(hh[r] if r==k else 0))
  mat.append(row)
 sm=sy.Matrix([[sy.sympify(str(z.n).replace('^','**'))/sy.sympify(str(z.d).replace('^','**')) for z in row] for row in mat]);x=sy.symbols('x');ch=sy.factor(sm.charpoly(x).as_expr());out['residue']=[[z.data() for z in row] for row in mat];out['characteristic_polynomial']=str(ch)
 print('PASS j infinity gauge',hh,'charpoly',ch,'seconds',round(time.time()-st,3),flush=True)
else:print('shear not sufficient',hh,round(time.time()-st,3),flush=True)
write('j-infinity-shear.json',out)
