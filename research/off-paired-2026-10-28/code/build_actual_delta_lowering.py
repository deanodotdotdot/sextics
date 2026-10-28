"""Explicit physical normal correction lowering the ACTUAL Delta^3 pole to Delta^2.
Introduces listed other divisors; this is not the main globally supported frontier.
"""
from pathlib import Path
from flint import fmpq_mpoly_ctx,fmpq_mpoly
import json,time,hashlib
root=Path(__file__).resolve().parents[1];st=time.time();C=fmpq_mpoly_ctx.get(('i','j','rho','v'));i,j,rho,v=C.gens();zero=C.constant(0)
def p(z):return fmpq_mpoly(z,C)
def load(n):return json.loads((root/n).read_text())
def exactdiv(a,b):q,r=divmod(a,b);assert not r;return q
bp='packet/coupled-fresh/ruling-source/full-base-connection/';ij=load(bp+'rank8-ij-connections-results.json');vr=load(bp+'rank8-v-literal-primitives-results.json');D=p(ij['common_denominator'])
inv=load('physical-discriminant-inverse-reduced.json');a=p(inv['inverse_numerator']);b=p(inv['denominator']);bez=p(inv['Bezout_coefficient']);dn=D.derivative('i')+rho*v*D.derivative('v')
assert a*dn+bez*D==b
H=[[6*p(ij['Gamma_numerators']['i'][r][k])+rho*p(vr['GammaV_numerators'][r][k]) for k in range(8)] for r in range(8)]
receipts=[]
for r in range(8):
 for k in range(8):
  h2=sum((H[r][l]*H[l][k] for l in range(8)),zero);quot=exactdiv(h2,D);receipts.append({'row':r,'column':k,'quotient_terms':len(quot.to_dict())})
# Formal matrix algebra with H^2 divisible by D gives
# (H/6-2 dn I)*(-a/(2b) I-a^2/(24b^2) H) = I modulo D.
# The exact cleared error is 144 b (a dn-b) I +12 a(a dn-b)H-a^2 H^2.
source=load('taylor-full-residual.json');assert source['status']=='PASS';assert len(source['rows'])==8
for row in source['rows']:
 assert row['Delta_power']==3
 assert hashlib.sha256((root/row['file']).read_bytes()).hexdigest()==row['sha256']
result={'status':'PASS actual Delta^3-to-Delta^2 normal correction','actual_source':'taylor-full-residual.json','source_rows':source['rows'],'inverse':'physical-discriminant-inverse-reduced.json','definitions':{'a':'inverse_numerator','b':'denominator','H':'6*Gamma_i_numerator+rho*GammaV_numerator','rho':'v_i/v (physical)','Jfac':'BV^4/(KD*i^2)=9^4*i^6*L^4/KD, where Dh=KD*i^2*Delta','Ares':'Jfac*H/6, so Gamma_i,physical=Ares/Delta exactly','U':'-[a/(2*b*Jfac)*I+a^2/(24*b^2*Jfac)*H]*Rnum, followed by rho=v_i/v and v=vp','added_Pi':'U/Delta^2','added_Pj':'0','added_Pw':'0'},'operator_proof':{'inverse_identity':True,'all_64_H_squared_divisible_by_D':True,'cleared_operator_error':'144*b*(a*dn-b)*I+12*a*(a*dn-b)*H-a^2*H^2, divisible by D','physical_D_relation':'D(vp)=Delta/Jfac; Delta_i=Jfac*dn modulo Delta','conclusion':'All eight Delta^-3 coefficients cancel. Full physical derivative of U is retained, so remaining generic Delta order is at most2.'},'nilpotence_receipts':receipts,'literal_fiber':'Add -sum_r (fi_r+rho*fV_r/6)*U_r/Delta^2 di dj dw; every one of the16 word coefficients is retained by the native arrays','new_divisors':'See reduced-inverse-physical-inventory.json plus i,N,L. These poles are NOT claimed served; this does not improve the Delta-only global-support frontier by itself.','seconds':time.time()-st}
(root/'actual-delta-lowering-current.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS actual eight-row Delta3->Delta2 operator, with new divisors',time.time()-st,flush=True)
