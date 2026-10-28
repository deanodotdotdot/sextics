from audit_core import *
st=time.time();cur=read('two-node-physical-current-improved.json');wc=read('w-correction.json');old=read('after-w-physical.json')['rows'];hh=P(cur['h']);s=4*i-1
K=1+F(s**9*AV**3,1728**3*BV**3)
Z=[jf(z) for z in wc['Z']];Vj=F(j*(2-w**3),2*i*w**3);Vw=F(T,i*w*w)
c=-F(i*T,4*w*j)+F(28*T*T*j,45*i*w**3)-F(224*j*(2-w**3),405*i*w**3);d=-F(448*T,405*i*w*w)
Pold={'i':[F(0) for _ in range(8)],'j':[Vj*z+(c if r==7 else 0) for r,z in enumerate(Z)],'w':[Vw*z+(d if r==7 else 0) for r,z in enumerate(Z)]}
Pnew={'i':[F(0)]*7+[-AP*jf(cur['alpha_i'])],'j':[F(0)]*7+[-AP*F(j,2)],'w':[F(0)]*7+[-AP*jf(cur['alpha_w'])]}
def sp(f,sign):return F(f.n.subs({'j':sign}),f.d.subs({'j':sign}))
kd={p:K.diff(p) for p in ['i','j','w']};results=[];outdir=ROOT/'two-node-patched-residual';outdir.mkdir(exist_ok=True)
for block in cur['slices']:
 sign=block['j'];ks=sp(K,sign);N1=N.subs({'j':sign});L1=L.subs({'j':sign});H1=P(cur['remaining_H1']);records=[]
 for r in range(8):
  ro=sp(jf(old[r]),sign);rn=jf(read(block['rows'][r]['file']))
  correction=sum((sp(kd[p],sign)*(sp(Pold[p][r],sign)-sp(Pnew[p][r],sign)) for p in ['i','j','w']),F(0))
  rr=ks*ro+(1-ks)*rn-correction
  assert rr.d.gcd(hh).total_degree()==0 and rr.d.gcd(N1).total_degree()==0
  rest=rr.d;support={}
  for name,f in [('i',i),('w',w),('T',T),('N',N1),('L',L1),('H1',H1)]:
   order=0
   while rest.total_degree()>0:
    qq,rem=divmod(rest,f)
    if rem:break
    rest=qq;order+=1
   if order:support[name]=order
  assert rest.total_degree()==0
  path=f'two-node-patched-residual/j{sign}-row-{r}.json';write(path,{'row':r,'j':sign,**rr.data()});rec={'row':r,'file':path,'sha256':sha(path),'denominator_support':support,'numerator_terms':len(rr.n.to_dict()),'nonzero':bool(rr)};records.append(rec);print(sign,r,support,'seconds',round(time.time()-st,2),flush=True)
 results.append({'j':sign,'rows':records})
write('two-node-physical-current-patched.json',{'status':'PASS all sixteen exact residual rows have no h,N,w,T poles','construction':'Ppatch=K*Pold+(1-K)*Pnew; K=1+((4*i-1)^3*vp/1728)^3. Pold is the baseline joint+w current, Pnew the improved two-node current. All derivatives precede j specialization.','K':K.data(),'Pold':{p:[z.data() for z in vv] for p,vv in Pold.items()},'Pnew_file':'two-node-physical-current-improved.json','residual_formula':'Rpatch=K*Rold+(1-K)*Rnew-sum_p K_p*(Pold_p-Pnew_p)','slices':results,'scope':'Exact specialized residuals on j=+/-1; nonzero. The separate patched-generic-support-audit.json proves generic support i,L,Delta. Zero-residual closure is not claimed.','certificate':False,'seconds':time.time()-st})
print('PASS patched physical current',time.time()-st,flush=True)
