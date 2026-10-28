from audit_core import *
st=time.time();bz=read('two-node-physical-normal-bezout-i4T.json');h=P(bz['h']);Abez,Bbez,Cbez=[P(z) for z in bz['multipliers']];assert Abez*h+Bbez*h.derivative('i')+Cbez*h.derivative('w')==i**4*T
s=4*i-1
sp=lambda f,sign=1:F(f.n.subs({'j':sign}),f.d.subs({'j':sign}))
AV1=AV.subs({'j':1});BV1=BV.subs({'j':1});T1=T;N1=N.subs({'j':1});L1=L.subs({'j':1})
ri=sp(vp.diff('i')/vp);rj=sp(vp.diff('j')/vp);rw=sp(vp.diff('w')/vp)
Kfac=F(AV1*s*s,64);Ztarget=Kfac*(3-s-s*rj/2)
Zoriginal=Ztarget;Lu=-4096*T**6+729*i**6*w**6
Ztarget=Zoriginal-F(h*Lu,L1)+F(h);assert Ztarget.d.total_degree()==0
ai=Ztarget*F(Bbez,i**4*T);aw=Ztarget*F(Cbez,i**4*T)
assert F(h.derivative('i'))*ai+F(h.derivative('w'))*aw==Ztarget*(1-F(Abez*h,i**4*T))
# Pull only the relevant native columns after j specialization.
powers={};
def pull(p,sign):
 p=p.subs({'j':sign});dc=coeffs(p,'v');degree=max(dc,default=0)
 if degree not in powers:powers[degree]=([AV1**k for k in range(degree+1)],[BV1**k for k in range(degree+1)])
 aa,bb=powers[degree];num=sum((a*aa[k]*bb[degree-k] for k,a in dc.items()),zero)
 return F(num,BV1**degree)
H1=32*i**6*v*v-16*i**5*v*v+1728*i**3*v-10800*i*i*v+11250*i*v-3125*v+23328
H1phys=pull(H1,1).n
outdir=ROOT/'two-node-improved-residual';outdir.mkdir(exist_ok=True);results=[]
for sign in [1,-1]:
 dd=pull(D,sign);ap=sp(AP,sign);aj=F(P(str(sign))/2);rjs=sp(vp.diff('j')/vp,sign)
 div=sp(AP.diff('i'),sign)*ai+ap*ai.diff('i')+sp(AP.diff('j'),sign)*aj+ap/2+sp(AP.diff('w'),sign)*aw+ap*aw.diff('w')
 rows=[]
 for rr in range(8):
  g={t:{c:pull(G[t][rr][c],sign)/dd for c in [6,7]} for t in ['i','j','V']}
  src=ap*((4 if rr==6 else 0)-g['V'][6]+2*i*g['i'][6]+sign*g['j'][6])
  conn=ai*g['i'][7]+aj*g['j'][7]+(ai*ri+aj*rjs+aw*rw)*g['V'][7]/6
  res=src+ap*conn+(div if rr==7 else F(0));assert res.d.gcd(h).total_degree()==0
  # Explicitly remove every admitted denominator factor.
  rest=res.d;support={}
  for name,f in [('i',i),('w',w),('T',T),('N',N1),('L',L1),('H1',H1phys)]:
   order=0
   while rest.total_degree()>0:
    qq,rem=divmod(rest,f)
    if rem:break
    rest=qq;order+=1
   if order:support[name]=order
  assert rest.total_degree()==0,('unserved denominator',rr,str(rest)[:200])
  path=f'two-node-improved-residual/j{sign}-row-{rr}.json';write(path,{'row':rr,'j':sign,'n':str(res.n),'d':str(res.d)})
  rows.append({'row':rr,'file':path,'sha256':sha(path),'numerator_terms':len(res.n.to_dict()),'denominator_support':support,'h_coprime':True,'nonzero':bool(res)})
  print('j',sign,'row',rr,rows[-1]['numerator_terms'],support,'seconds',round(time.time()-st,2),flush=True)
 results.append({'j':sign,'rows':rows})
write('two-node-physical-current-improved.json',{'status':'PASS actual weighted eight-row physical residual has no two-node h denominator on j=+/-1 slices','extension':'alpha_i(i,w), alpha_w(i,w) independent of j; alpha_j=j/2. Pp=-AP*alpha_p*e7. All divergence derivatives taken before j specialization.','alpha_i':ai.data(),'alpha_w':aw.data(),'alpha_j':'j/2','Ztarget':Ztarget.data(),'original_Ztarget':Zoriginal.data(),'normal_rate_improvement':'Zprime=Zoriginal-h*L_u/L+h; Zprime is divisible by w*T^2. Alpha denominators reduce to powers of i.','Bezout_input':'two-node-physical-normal-bezout-i4T.json','critical_normal_identity':'On h=0 and (4i-1)x^2+6x+12=0, alpha_i*(x^2-rho_i*t)+(j/2)*(a*x-rho_j*t)+alpha_w*(-rho_w*t)=1, t=(x+2)/2,a=-(x+2)/(2j).','h':str(h),'remaining_H1':str(H1phys),'slices':results,'scope':'Specialized physical coupled construction. Full generic residual, off-slice support, boundaries, infinity, and original field closure are not asserted. Baseline Delta-only actual current remains preferred.','certificate':False,'seconds':time.time()-st})
print('PASS actual two-node physical coupled correction',time.time()-st,flush=True)
