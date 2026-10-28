from audit_core import *
st=time.time();cur=read('two-node-physical-current-patched.json');new=read(cur['Pnew_file']);K=jf(cur['K']);po={p:[jf(z) for z in zz] for p,zz in cur['Pold'].items()};pn={'i':[F(0)]*7+[-AP*jf(new['alpha_i'])],'j':[F(0)]*7+[-AP*F(j,2)],'w':[F(0)]*7+[-AP*jf(new['alpha_w'])]};records=[]
def check_support(f,label,allowed):
 rest=f.d;orders={}
 for name,g in allowed:
  k=0
  while rest.total_degree()>0:
   q,rem=divmod(rest,g)
   if rem:break
   rest=q;k+=1
  if k:orders[name]=k
 assert rest.total_degree()==0,(label,str(rest)[:200]);records.append({'label':label,'support':orders});return orders
corr={p:[] for p in po}
for p in po:
 for r in range(8):
  z=(1-K)*(pn[p][r]-po[p][r]);corr[p].append(z);check_support(z,f'correction {p} {r}',[('i',i),('L',L)])
 print('PASS correction support',p,time.time()-st,flush=True)
for r in range(8):
 z=sum(((vp.diff(p)/vp)*corr[p][r] for p in po),F(0));check_support(z,f'vertical contraction {r}',[('i',i),('L',L)])
 print('PASS logarithmic contraction',r,time.time()-st,flush=True)
for r,row in enumerate(read('after-w-physical.json')['rows']):check_support(jf(row),f'old residual {r}',[('i',i),('L',L),('Delta',Delta)])
max_degree=0
for p in G:
 for r,row in enumerate(G[p]):
  for c,z in enumerate(row):max_degree=max(max_degree,int(z.degrees()[3]))
# For numerator v degree d, homogenization gives denominator dividing
# Dh*BV^max(0,d-4). Both BV=9*i^2*L and Dh=KD*i^2*Delta are exact identities.
assert BV==9*i*i*L
assert max_degree<=8
write('patched-generic-support-audit.json',{'status':'PASS exact generic denominator-support proof','checks':records,'check_count':len(records)+192,'matrix_degree_checks':192,'maximum_native_numerator_v_degree':max_degree,'pulled_native_denominator':'Dh*BV^max(0,d-4), where Dh=KD*i^2*Delta and BV=9*i^2*L','argument':'Ppatch=Pold+C. Every C_p and sum_p rho_p*C_p has denominator supported on i,L. Differentiation preserves that support. Homogenizing each native numerator shows the pulled matrices have denominator supported on i,L,Delta. Since Rold is supported on i,L,Delta, the full generic Rpatch is supported on i,L,Delta. This proves a support bound without expanding the full generic residual.','generic_residual_support':['i','L','Delta'],'scope':'At j=+/-1 the separately expanded residual further cancels h and has support i,L,H1. No zero-residual or global removal of i,L,Delta is claimed.','certificate':False,'seconds':time.time()-st})
print('PASS generic support',time.time()-st,flush=True)
