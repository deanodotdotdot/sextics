"""Reduce the source-directed normal scalar modulo D and cancel content."""
from pathlib import Path
from flint import fmpq_mpoly_ctx,fmpq_mpoly
import json,time
root=Path(__file__).resolve().parents[1];st=time.time();C=fmpq_mpoly_ctx.get(('i','j','rho','v'));i,j,rho,v=C.gens();zero=C.constant(0)
def p(z):return fmpq_mpoly(z,C)
def coeff(z,k):return C.from_dict({(a,b,c,0):t for (a,b,c,d),t in z.to_dict().items() if d==k})
def div(a,b):q,r=divmod(a,b);assert not r;return q
saved=json.loads((root/'physical-discriminant-inverse-reduced.json').read_text());inv=p(saved['inverse_numerator']);den=p(saved['denominator'])
bp=root/'packet/coupled-fresh/ruling-source/full-base-connection';ij=json.loads((bp/'rank8-ij-connections-results.json').read_text());vr=json.loads((bp/'rank8-v-literal-primitives-results.json').read_text());D=p(ij['common_denominator']);d4=coeff(D,4)
F=D.derivative('i')+rho*v*D.derivative('v');E=v*D.derivative('v')
num=inv*E
while num.degrees()[3]>=4:
 deg=int(num.degrees()[3]);lead=coeff(num,deg);num=d4*num-lead*v**(deg-4)*D;den*=d4
 common=num.gcd(den);num=div(num,common);den=div(den,common)
 print('reduced v degree',num.degrees()[3],'num/den terms',len(num.to_dict()),len(den.to_dict()),'seconds',round(time.time()-st,3),flush=True)
div(F*num-E*den,D)
_,factors=den.factor();checks=[]
result={'status':'PASS reduced inverse applied to v*D_v','scalar_numerator':str(num),'scalar_denominator':str(den),'denominator_factors':[{'polynomial':str(f),'multiplicity':int(e)} for f,e in factors],'identity':'(D_i+rho*v*D_v)*scalar_numerator-v*D_v*scalar_denominator is divisible by D','seconds':time.time()-st}
(root/'reduced-v-normal-scalar.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS reduced actual current factors',[(e,len(f.to_dict())) for f,e in factors],time.time()-st,flush=True)
