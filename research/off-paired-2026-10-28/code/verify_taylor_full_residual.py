"""Independent generic product-rule check of all expanded Taylor residual rows."""
from audit_core import *
st=time.time();cur=read('taylor-discriminant-current.json');kn=i**8*L**6*P(cur['W']);hh=Delta**2-kn
kj=kn.derivative('j')*Delta-2*kn*Delta.derivative('j');kw=kn.derivative('w')*Delta-2*kn*Delta.derivative('w')
Z=[jf(z) for z in read('w-correction.json')['Z']]
c=F(-i*T,4*w*j)+F(28*T*T*j,45*i*w**3)-F(224*j*(2-w**3),405*i*w**3);d=F(-448*T,405*i*w*w);Vj=F(j*(2-w**3),2*i*w**3);Vw=F(T,i*w*w)
Pj=[Vj*z+(c if r==7 else 0) for r,z in enumerate(Z)];Pw=[Vw*z+(d if r==7 else 0) for r,z in enumerate(Z)]
old=read('after-w-physical.json')['rows'];src=read('actual-source-polynomial.json')['numerators'];hs=exactdiv(hh,j*j*N)
cache={}
def quotient(poly,den,label):
 key=(label,str(den))
 if key not in cache:cache[key]=exactdiv(poly,den)
 return cache[key]
passed=[]
for r in range(8):
 path=ROOT/f'taylor-residual/row-{r}.json'
 while not path.exists():time.sleep(1)
 saved=json.loads(path.read_text());target=P(saved['numerator'])*Delta**(3-saved['Delta_power'])
 oldden=exactdiv(P(old[r]['d']),Delta)
 rhs=P(old[r]['n'])*quotient(kn,oldden,'K')+hs*P(src[r])-Pj[r].n*quotient(kj,Pj[r].d,'Kj')-Pw[r].n*quotient(kw,Pw[r].d,'Kw')
 assert target==rhs,('expanded residual mismatch',r)
 passed.append(r);print('PASS independent generic expanded residual row',r,'seconds',round(time.time()-st,3),flush=True)
 write('taylor-full-residual-independent-audit.json',{'status':'PASS' if len(passed)==8 else 'in progress','rows':passed,'method':'Independent product-rule identity K*R_after_w+(1-K)*S-K_j*Pj_old-K_w*Pw_old, using previously independently reconstructed full residual; exact polynomial divisions and equality against the newly expanded direct native calculation','seconds':time.time()-st})
