"""Full generic exact residual from actual native source and physical derivatives.
Produces polynomial numerators over Delta^3 by exact denominator division.
"""
from audit_core import *
st=time.time();dc=coeffs(D,'v');D0,D1,D2=dc[0],dc[1],dc[2]
Taylor=D0*D0+2*D0*D1*v+(D1*D1+2*D0*D2)*v*v
Zj=Taylor.derivative('j')*D-2*Taylor*D.derivative('j')
Zv=6*v*(Taylor.derivative('v')*D-2*Taylor*D.derivative('v'))
Z=[jf(z) for z in read('w-correction.json')['Z']]
c=F(-i*T,4*w*j)+F(28*T*T*j,45*i*w**3)-F(224*j*(2-w**3),405*i*w**3);d=F(-448*T,405*i*w*w)
Vj=F(j*(2-w**3),2*i*w**3);Vw=F(T,i*w*w)
Pj=[Vj*z+(c if r==7 else 0) for r,z in enumerate(Z)];Pw=[Vw*z+(d if r==7 else 0) for r,z in enumerate(Z)]
bj=vp.diff('j')/vp/6;bw=vp.diff('w')/vp/6
B=[bj*Pj[r]+bw*Pw[r] for r in range(8)];div=[Pj[r].diff('j')+Pw[r].diff('w') for r in range(8)]
common=one
for z in [AP]+Pj+B+div:common=exactdiv(common*z.d,common.gcd(z.d))
def cc(z):return exactdiv(common,z.d)*z.n
ca=cc(AP);cj=[cc(z) for z in Pj];cb=[cc(z) for z in B];cd=[cc(z) for z in div]
remove=common*KD**3*i**6
outdir=ROOT/'taylor-residual';outdir.mkdir(exist_ok=True);rows=[]
for r in range(8):
 Q=(4*D if r==6 else zero)-G['V'][r][6]+2*i*G['i'][r][6]+j*G['j'][r][6]
 native=ca*Q*D*D-Taylor*D*cd[r]-Zj*cj[r]-Zv*cb[r]
 for k in range(8):native-=Taylor*(G['j'][r][k]*cj[k]+G['V'][r][k]*cb[k])
 print('row',r,'native numerator terms',len(native.to_dict()),'seconds',round(time.time()-st,3),flush=True)
 raw=hom(native,12)
 print('row',r,'physical cleared terms',len(raw.to_dict()),'seconds',round(time.time()-st,3),flush=True)
 numerator=exactdiv(raw,remove)
 power=3
 while power and not divmod(numerator,Delta)[1]:numerator=exactdiv(numerator,Delta);power-=1
 name=f'taylor-residual/row-{r}.json';write(name,{'row':r,'numerator':str(numerator),'Delta_power':power})
 rows.append({'row':r,'file':name,'Delta_power':power,'terms':len(numerator.to_dict()),'degrees':[int(z) for z in numerator.degrees()],'sha256':sha(name)})
 print('PASS exact generic residual row',r,'Delta power',power,'terms',len(numerator.to_dict()),'seconds',round(time.time()-st,3),flush=True)
 write('taylor-full-residual.json',{'status':'PASS' if len(rows)==8 else 'in progress','method':'Actual native source and all physical derivative terms; exact division of every non-Delta denominator; no prior residual is used in this calculation','current':'taylor-discriminant-current.json','Delta':str(Delta),'rows':rows,'seconds':time.time()-st})
