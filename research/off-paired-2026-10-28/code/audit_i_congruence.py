"""Independent generic audit via cleared polynomial congruences, not Laurent division.

Prove i^7 times the gauged residual is zero modulo i^7. All denominators
other than the displayed i powers are units in Q(j,w)[[i]].
"""
from audit_core import *
import sys
current_name=sys.argv[1] if len(sys.argv)>1 else 'i-global-correction-corrected.json'
st=time.time();cur=read(current_name);assert cur['h']==h;assert P(cur['Delta'])==Delta
N0=N.subs({'i':0});L0=L.subs({'i':0});Delta0=Delta.subs({'i':0});Kden=L*L*Delta;K0=Kden.subs({'i':0})
# Build generic normal connection numerator directly from native matrices.
co=(-2*N+18*i*i*w*w)*L-i*N*L.derivative('i')
KN=[]
for r in range(8):
 rr=[]
 for k in range(8):
  native=6*L*i*N*G['i'][r][k]+co*G['V'][r][k]
  raw=hom(native,5,13)
  rr.append(trunc(exactdiv(raw,54*KD*i**(4+h[r]-h[k]))))
 KN.append(rr);print('normal polynomial matrix row',r,'seconds',round(time.time()-st,3),flush=True)
# Independently reconstruct both tangential boundary connections and verify
# their regularity in the same gauge by exact monomial divisibility.
tan={};oldtan=read('tangent-boundary.json');comparisons=0
for var in ['j','w']:
 mat=[]
 for r in range(8):
  rr=[]
  for k in range(8):
   if var=='j':
    rho=2*N*L+j*N.derivative('j')*L-j*N*L.derivative('j')
    native=6*j*N*L*G['j'][r][k]+rho*G['V'][r][k]
    den0=54*KD*j*N0*L0*L0*Delta0
   else:
    rho=T*N*L+2*w*T.derivative('w')*N*L+w*T*N.derivative('w')*L-w*T*N*L.derivative('w')
    native=rho*G['V'][r][k]
    den0=54*KD*w*T*N0*L0*L0*Delta0
   raw=exactdiv(hom(native,5,7),i**(4+h[r]-h[k]))
   value=F(raw.subs({'i':0}),den0)
   assert value==jf(oldtan[var][r][k]),('boundary mismatch',var,r,k)
   comparisons+=1;rr.append(value)
  mat.append(rr)
 tan[var]=mat;print('PASS tangential regularity and boundary',var,'seconds',round(time.time()-st,3),flush=True)
# Reconstruct boundary current from the ACTUAL global lift. No producer
# source-coefficient jets or saved served vector is used in the equation.
U={}
for var in ['j','w']:
 U[var]=[]
 for r,z in enumerate(cur['tangent'][var]):
  num=P(z['numerator']);assert not num or num.degrees()[0]==0
  value=F(N0*num,Delta0**z['power'])
  assert value==jf(read('boundary-current.json')['U'][var][r])
  U[var].append(value)
served=[]
for r in range(8):
 z=U['j'][r].diff('j')+U['w'][r].diff('w')
 for k in range(8):z+=tan['j'][r][k]*U['j'][k]+tan['w'][r][k]*U['w'][k]
 assert z==jf(read('boundary-current.json')['served_boundary_vector'][r])
 served.append(z)
print('PASS all eight literal boundary divergences',round(time.time()-st,3),flush=True)
# Assemble one polynomial numerator for the entire normal current, through
# the jet order needed for a principal-part proof.
dp=tpows(trunc(Delta),8);FF=[zero for _ in range(8)]
for block in cur['normal']:
 m=block['m'];assert -7<=m<=-1
 for r,z in enumerate(block['coefficients']):
  num=P(z['numerator']);assert not num or num.degrees()[0]==0
  FF[r]+=trunc(i**(m+7)*mul(num,dp[7-z['power']]))
print('assembled all seven normal blocks','seconds',round(time.time()-st,3),flush=True)
old=read('after-w-physical.json')['rows'];checks=[];residual_terms=[]
kd=trunc(Kden);dd=trunc(Delta);di=dd.derivative('i')
for r,row in enumerate(old):
 remaining_den=exactdiv(P(row['d']),i**(7-h[r]))
 snum=trunc(P(row['n'])*exactdiv(Kden,remaining_den))
 f=FF[r]
 derivative=mul(i*N*f.derivative('i')+(h[r]-6)*N*f+i*N.derivative('i')*f,dd)-7*mul(i*N*f,di)
 matrix=sum((mul(KN[r][k],FF[k]) for k in range(8)),zero)
 tangent=i**6*served[r].n*exactdiv(K0*Delta0**8,served[r].d)
 residual=mul(snum,dp[8])-tangent-mul(kd,derivative)-mul(dd,matrix)
 residual=trunc(residual)
 checks.append(not bool(residual));residual_terms.append(len(residual.to_dict()))
 if residual:write('i-audit-failure.json',{'row':r,'residual':str(residual)});raise AssertionError(('nonzero principal part',r,len(residual.to_dict())))
 print('PASS cleared generic i congruence row',r,'seconds',round(time.time()-st,3),flush=True)
write('i-corrected-independent-audit.json' if 'corrected' in current_name else 'i-original-principal-part-audit.json',{'status':'PASS','method':'Native matrices, exact monomial divisibility, boundary differentiation, and cleared polynomial congruences modulo i^7; no saved normal/source jets and no producer Laurent division','all_eight_rows':checks,'residual_term_counts':residual_terms,'tangent_connection_entries_checked':comparisons,'h':h,'common_i_gauge_source_pole_bound':7,'normal_current_common_Delta_power':7,'affine_residual_support':'See separate support audit; principal-part test alone does not establish it','scope':'Generic along i=0; divisor support statement on affine base. Intersection strata, base infinity, original six-variable clearing remain separate obligations. Literal fiber expressions are retained by separate audit.','inputs':{f:sha(f) for f in [current_name,'after-w-physical.json','boundary-current.json']},'seconds':time.time()-st})
