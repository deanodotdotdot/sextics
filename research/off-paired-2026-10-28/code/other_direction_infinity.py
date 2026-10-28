from audit_core import *
import sympy as sy
st=time.time();out={};x=sy.symbols('x')
for t in ['j','w']:
 if t=='j':rho=2*N*L+j*N.derivative('j')*L-j*N*L.derivative('j');den=6*N*L*BV*Dh
 else:rho=T*N*L+2*w*T.derivative('w')*N*L+w*T*N.derivative('w')*L-w*T*N*L.derivative('w');den=6*T*N*L*BV*Dh
 idx={'j':1,'w':2}[t];den_co=coeffs(den,t);dd=int(max(den_co));nums=[];degrees=[]
 for r in range(8):
  row=[];deg=[]
  for k in range(8):
   z=hom(rho*G['V'][r][k]+(6*j*N*L*G['j'][r][k] if t=='j' else zero),5)
   row.append(z);deg.append(int(z.degrees()[idx])-dd if z else -10000)
  nums.append(row);degrees.append(deg)
 hs=[0]*8;success=False
 for iteration in range(10):
  changed=False
  for r in range(8):
   for k in range(8):
    if nums[r][k] and hs[r]<hs[k]+degrees[r][k]:hs[r]=hs[k]+degrees[r][k];changed=True
  if not changed:success=True;break
 if not success:out[t]={'status':'diagonal gauge failed','shifts':hs,'degrees':degrees};continue
 mat=[]
 for r in range(8):
  row=[]
  for k in range(8):
   z=F(0)
   if nums[r][k] and degrees[r][k]+hs[k]-hs[r]==0:
    nc=coeffs(nums[r][k],t);z=-F(nc[max(nc)],den_co[dd])
   if r==k:z-=hs[r]
   row.append(z)
  mat.append(row)
 sm=sy.Matrix([[sy.sympify(str(z.n).replace('^','**'))/sy.sympify(str(z.d).replace('^','**')) for z in row] for row in mat]);ch=sy.factor(sm.charpoly(x).as_expr())
 out[t]={'status':'PASS','gauge':hs,'charpoly':str(ch),'residue':[[z.data() for z in row] for row in mat],'degrees':degrees}
 print(t,'gauge',hs,'charpoly',ch,'seconds',round(time.time()-st,3),flush=True)
write('other-direction-infinity.json',out)
