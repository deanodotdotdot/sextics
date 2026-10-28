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
F=D.derivative('i')+rho*v*D.derivative('v');E=2*i*D.derivative('i')+j*D.derivative('j')-6*v*D.derivative('v')
num=inv*E
while num.degrees()[3]>=4:
 deg=int(num.degrees()[3]);lead=coeff(num,deg);num=d4*num-lead*v**(deg-4)*D;den*=d4
 common=num.gcd(den);num=div(num,common);den=div(den,common)
 print('reduced v degree',num.degrees()[3],'num/den terms',len(num.to_dict()),len(den.to_dict()),'seconds',round(time.time()-st,3),flush=True)
div(F*num-E*den,D)
_,factors=den.factor();checks=[]
for r in range(8):
 gi=p(ij['Gamma_numerators']['i'][r][6]);gj=p(ij['Gamma_numerators']['j'][r][6]);gv=p(vr['GammaV_numerators'][r][6]);Q=(4*D if r==6 else zero)-gv+2*i*gi+j*gj
 div(6*den*Q-num*(6*gi+rho*gv),6*D);checks.append(r)
result={'status':'PASS source-directed normal current, reduced modulo D','scalar_numerator':str(num),'scalar_denominator':str(den),'denominator_factors':[{'polynomial':str(f),'multiplicity':int(e)} for f,e in factors],'Pi_row6':'Aphysical*scalar_numerator/scalar_denominator after rho=v_i/v, v=vp','other_current_components':'0','residue_identity':'(D_i+rho*v*D_v)*scalar_numerator-E*scalar_denominator is divisible by D; E=2i D_i+j D_j-6v D_v','all_eight_actual_source_rows_checked':checks,'physical_derivatives':'Retain d_i via i,rho,v and Aphysical; rho_i and v_i are required','literal_fiber':'-(fi_col6+rho*fV_col6/6)*Pi_row6 di dj dw, all16 words','scope':'Generic Delta residue served, other introduced divisors remain to be served; not a certificate','seconds':time.time()-st}
(root/'reduced-actual-normal-current.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS reduced actual current factors',[(e,len(f.to_dict())) for f,e in factors],time.time()-st,flush=True)
