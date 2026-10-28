from audit_core import *
st=time.time();cur=read('two-node-physical-current-patched.json');new=read(cur['Pnew_file']);K=jf(cur['K']);po={p:[jf(z) for z in zz] for p,zz in cur['Pold'].items()};pn={'i':[F(0)]*7+[-AP*jf(new['alpha_i'])],'j':[F(0)]*7+[-AP*F(j,2)],'w':[F(0)]*7+[-AP*jf(new['alpha_w'])]}
# Build derivatives from the actual extended current, before specialization.
pp={p:[K*po[p][r]+(1-K)*pn[p][r] for r in range(8)] for p in po}
div=[sum((pp[p][r].diff(p) for p in pp),F(0)) for r in range(8)]
checks=[]
def sp(f,sign):return F(f.n.subs({'j':sign}),f.d.subs({'j':sign}))
for block in cur['slices']:
 sign=block['j'];av=AV.subs({'j':sign});bv=BV.subs({'j':sign});powers={}
 def pull(p):
  cc=coeffs(p.subs({'j':sign}),'v');deg=max(cc,default=0)
  if deg not in powers:powers[deg]=([av**k for k in range(deg+1)],[bv**k for k in range(deg+1)])
  aa,bb=powers[deg];return F(sum((q*aa[k]*bb[deg-k] for k,q in cc.items()),zero),bv**deg)
 dd=pull(D);ps={p:[sp(z,sign) for z in zz] for p,zz in pp.items()};rho={p:sp(vp.diff(p)/vp,sign) for p in pp};ap=sp(AP,sign)
 for r in range(8):
  gi=[pull(z)/dd for z in G['i'][r]];gj=[pull(z)/dd for z in G['j'][r]];gv=[pull(z)/dd for z in G['V'][r]]
  source=ap*((4 if r==6 else 0)-gv[6]+2*i*gi[6]+sign*gj[6])
  conn=sum((gi[c]*ps['i'][c]+gj[c]*ps['j'][c]+gv[c]/6*sum((rho[p]*ps[p][c] for p in pp),F(0)) for c in range(8)),F(0))
  result=source-sp(div[r],sign)-conn;saved=jf(read(block['rows'][r]['file']));assert result==saved
  checks.append({'j':sign,'row':r,'exact_equality':True});print('PASS',sign,r,'seconds',time.time()-st,flush=True)
write('patched-native-direct-replay-audit.json',{'status':'PASS exact direct native reconstruction of all sixteen saved rows','checks':checks,'method':'Differentiate the fully extended rational current; pull all native matrix columns; compute source minus divergence and connection directly. Compare exact reduced fractions to product-rule producer output.','certificate':False,'seconds':time.time()-st})
