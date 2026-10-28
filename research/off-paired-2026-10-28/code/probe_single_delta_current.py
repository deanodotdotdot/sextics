"""Probe a one-Delta current by preserving required j,w principal parts."""
from exact import *
from jets import rs,pcoeff,add,mul
import time
st=time.time();cur=json.loads((HERE/'taylor-discriminant-current.json').read_text());Delta=poly(cur['Delta']);dc={k:R(z) for k,z in pcoeff(Delta,'w').items() if k<=3}
Z=[R(z['n'],z['d']) for z in json.loads((HERE/'w-correction.json').read_text())['Z']]
p0={'j':[Vj*z+(c if r==7 else 0) for r,z in enumerate(Z)],'w':[Vw*z+(d if r==7 else 0) for r,z in enumerate(Z)]};B={}
for t in ['j','w']:
 B[t]=[]
 for r,z in enumerate(p0[t]):
  high=-1 if t=='j' else 0;series=mul(dc,rs(z,'w',high),high)
  for val in series.values():assert val.d.total_degree()==0,(t,r,'coefficient not polynomial')
  b=sum((val*R(w)**k for k,val in series.items()),R(0))
  if t=='w':b*=R(T)
  if t=='j' and r==7:b-=R(i*T*Delta.subs({'j':0}),4*w*j)
  B[t].append(b)
checks=[]
for r in range(8):
 delta_trace=B['j'][r]*N.derivative('j')+B['w'][r]*N.derivative('w')-R(Delta)*(p0['j'][r]*N.derivative('j')+p0['w'][r]*N.derivative('w'))
 quo,rem=divmod(delta_trace.n,N)
 checks.append({'row':r,'preserves_N':not bool(rem),'N_remainder_terms':len(rem.to_dict())})
export(HERE/'single-delta-current-probe.json',{'status':'candidate probe only','B':{t:[z.data() for z in vec] for t,vec in B.items()},'current':'Pj=Bj/Delta, Pw=Bw/Delta, Pi=0','N_checks':checks,'scope':'Preserves j/w/T boundary jets by construction; i,L and N behavior requires checks. Not a closure or validated improvement.','seconds':time.time()-st})
print('one-Delta probe N preservation',checks,'seconds',time.time()-st,flush=True)
