"""Use the saved physical normal inverse on the ACTUAL source residue.
This serves the native discriminant generically but introduces listed new
divisors. It is an alternative partial current, not a closed certificate.
"""
from pathlib import Path
from flint import fmpq_mpoly_ctx,fmpq_mpoly
import json,time,hashlib
root=Path(__file__).resolve().parents[1];st=time.time()
C=fmpq_mpoly_ctx.get(('i','j','rho','v'));i,j,rho,v=C.gens();zero=C.constant(0)
def p(s):return fmpq_mpoly(s.replace('**','^'),C)
def load(n):return json.loads((root/n).read_text())
def exactdiv(a,b):q,r=divmod(a,b);assert not r;return q
base='packet/coupled-fresh/ruling-source/full-base-connection/'
ij=load(base+'rank8-ij-connections-results.json');vr=load(base+'rank8-v-literal-primitives-results.json');saved=load('physical-discriminant-inverse.json')
D=p(ij['common_denominator']);Di=D.derivative('i');Dj=D.derivative('j');Dv=D.derivative('v')
Gi=[[p(z) for z in row] for row in ij['Gamma_numerators']['i']];Gj=[[p(z) for z in row] for row in ij['Gamma_numerators']['j']];GV=[[p(z) for z in row] for row in vr['GammaV_numerators']]
inv=p(saved['inverse_numerator']);den=p(saved['denominator']);bez=p(saved['Bezout_coefficient'])
assert inv*(Di+rho*v*Dv)+bez*D==den
print('PASS independent replay of exact normal inverse identity',time.time()-st,flush=True)
E=-6*v*Dv+2*i*Di+j*Dj
quotients=[]
for r in range(8):
 Q=(4*D if r==6 else zero)-GV[r][6]+2*i*Gi[r][6]+j*Gj[r][6]
 num=6*den*Q-inv*E*(6*Gi[r][6]+rho*GV[r][6])
 quotient=exactdiv(num,6*D)
 raw=str(quotient).encode();quotients.append({'row':r,'terms':len(quotient.to_dict()),'degrees':[int(z) for z in quotient.degrees()],'sha256':hashlib.sha256(raw).hexdigest()})
 print('PASS actual source discriminant cancellation row',r,'quotient terms',len(quotient.to_dict()),'seconds',round(time.time()-st,3),flush=True)
# The primitive is P_i=Aphysical*inv*E/den * e6, Pj=Pw=0.
# The remaining connection part is Aphysical*quotient/den, and the full
# physical derivative of the primitive only contributes in row6.
result={'status':'PASS actual source discriminant residue served','current':{'Pi_row6':'Aphysical*inverse_numerator*E/denominator, then rho=v_i/v and v=vp','Pj':'0','Pw':'0','E':str(E),'inverse_input':'physical-discriminant-inverse.json'},'physical_derivative':'d_i[A*f]=A_i*f+A*(partial_i(f)+rho_i*partial_rho(f)+v_i*partial_v(f)); rho=v_i/v','residual':'Aphysical*quotient_r/denominator - delta_(r,6)*d_i(Pi_row6)','quotient_definition':'quotient_r=(6*den*Q_r-inverse_numerator*E*(6*Gamma_i_numerator[r,6]+rho*GammaV_numerator[r,6]))/(6*D), exact polynomial quotient','quotient_receipts':quotients,'all_eight_rows':True,'literal_fiber':'-(fi_col6+(rho/6)*fV_col6)*Pi_row6 di dj dw; retain all sixteen literal words and fixed-x Cartan term','scope':'Native D denominator cancels exactly in all eight residual rows before physical substitution. Physical denominator inventory checked separately. This alternative can reintroduce other affine divisors and is not closure.','seconds':time.time()-st}
(root/'actual-source-discriminant-current.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS actual source-serving discriminant current (new divisors pending inventory)',time.time()-st,flush=True)
