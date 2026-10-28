"""Full generic source binding by denominator clearing, independent of B,H,J reductions."""
from audit_core import *
st=time.time()
Z=[jf(z) for z in read('w-correction.json')['Z']]
c=F(-i*T,4*w*j)+F(28*T*T*j,45*i*w**3)-F(224*j*(2-w**3),405*i*w**3)
d=F(-448*T,405*i*w*w)
Vj=F(j*(2-w**3),2*i*w**3);Vw=F(T,i*w*w)
Pj=[Vj*z+(c if k==7 else 0) for k,z in enumerate(Z)]
Pw=[Vw*z+(d if k==7 else 0) for k,z in enumerate(Z)]
bj=vp.diff('j')/vp/6;bw=vp.diff('w')/vp/6
B=[bj*Pj[k]+bw*Pw[k] for k in range(8)]
div=[Pj[k].diff('j')+Pw[k].diff('w') for k in range(8)]
common=one
for z in [AP]+Pj+B+div:common=exactdiv(common*z.d,common.gcd(z.d))
coef=lambda z:exactdiv(common,z.d)*z.n
ca=coef(AP);cj=[coef(z) for z in Pj];cv=[coef(z) for z in B];cd=[coef(z) for z in div]
den=common*BV*Dh
saved=read('after-w-physical.json')['rows'];checks=[]
for r,row in enumerate(saved):
 native=ca*((4*D if r==6 else zero)-G['V'][r][6]+2*i*G['i'][r][6]+j*G['j'][r][6])-cd[r]*D
 for k in range(8):native-=cj[k]*G['j'][r][k]+cv[k]*G['V'][r][k]
 actual=hom(native,5);rn,rd=P(row['n']),P(row['d'])
 scale=exactdiv(den,rd)
 assert actual==rn*scale,('actual source residual mismatch',r)
 checks.append(True);print('PASS full generic actual-source row',r,'seconds',round(time.time()-st,3),flush=True)
write('actual-source-independent-audit.json',{'status':'PASS','method':'Direct native source and physical connection, common denominator clearing and exact polynomial equality; no B/H/J intermediate or saved residual jets','all_eight_rows':checks,'physical_beta_j':bj.data(),'physical_beta_w':bw.data(),'inputs':{f:sha(f) for f in ['w-correction.json','after-w-physical.json']},'seconds':time.time()-st})
