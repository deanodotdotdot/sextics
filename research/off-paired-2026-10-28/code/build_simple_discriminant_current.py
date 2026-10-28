"""A smaller Delta-only current using two scalar cutoffs, Pi=0.

This construction does not need the 43 MB normal-i correction. It is a
partial source reduction, not a primitive of the residual or a certificate.
"""
from audit_core import *
st=time.time();checks={}
def check(k,condition):assert condition,k;checks[k]=True
# Actual source regular at i and L follows directly from native v-degree.
Q=[(4*D if r==6 else zero)-G['V'][r][6]+2*i*G['i'][r][6]+j*G['j'][r][6] for r in range(8)]
check('native source degree at most four in v',all(not z or z.degrees()[3]<=4 for z in Q))
snum=[exactdiv(9*i*w*T*hom(z,4),KD) for z in Q]
write('actual-source-polynomial.json',{'numerators':[str(z) for z in snum],'denominator':str(j*j*N*Delta),'meaning':'Exact actual compact source, before all currents; all eight rows','i_and_L_regular':True})
# Ei agrees with Delta at i=0 and vanishes along N,j,w,T.
Delta0=Delta.subs({'i':0});N0=N.subs({'i':0})
Ei=N*exactdiv(Delta0,N0);Hi=exactdiv(Delta-Ei,i)
EL=exactdiv(coeffs(D,'v')[4]*AV**4,KD*i*i);HL=exactdiv(Delta-EL,L)
exactdiv(Ei,N*j**20*w**3*T**14)
exactdiv(EL,i**3*j**8*w**4*T**8*N**4)
check('Delta=Ei+i*Hi',Delta==Ei+i*Hi)
check('Delta=EL+L*HL',Delta==EL+L*HL)
Z=[jf(z) for z in read('w-correction.json')['Z']]
c=F(-i*T,4*w*j)+F(28*T*T*j,45*i*w**3)-F(224*j*(2-w**3),405*i*w**3);d=F(-448*T,405*i*w*w)
Vj=F(j*(2-w**3),2*i*w**3);Vw=F(T,i*w*w)
base={'j':[Vj*z+(c if r==7 else 0) for r,z in enumerate(Z)],'w':[Vw*z+(d if r==7 else 0) for r,z in enumerate(Z)]}
def order(z,p):
 if not z:return 10000
 def valuation(a):
  k=0
  while True:
   q,rem=divmod(a,p)
   if rem:return k
   a=q;k+=1
 return valuation(z.n)-valuation(z.d)
orders={}
for p,label in [(i,'i'),(j,'j'),(w,'w'),(T,'T'),(N,'N'),(L,'L')]:
 orders[label]={t:[order(z,p)-(h[r] if label=='i' else 0) for r,z in enumerate(vec)] for t,vec in base.items()}
check('i-gauged current lower bound minus seven',min(orders['i'][t][r] for t in base for r in range(8))>=-7)
check('raw current L lower bound minus one',min(orders['L'][t][r] for t in base for r in range(8))>=-1)
check('j-current w lower bound minus three',min(orders['w']['j'])>=-3)
check('w-current w lower bound minus two',min(orders['w']['w'])>=-2)
check('both currents j lower bound minus one',min(orders['j'][t][r] for t in base for r in range(8))>=-1)
check('both currents N and T regular',all(orders[p][t][r]>=0 for p in ['N','T'] for t in base for r in range(8)))
# K=(1-Ei/Delta)^7*(1-EL/Delta)^3.
# i order >=7, L order >=3. K-1 is in ideal (Ei,EL), hence divisible
# by j^8*w^3*T^8*N (the common factors of Ei and EL).
common=j**8*w**3*T**8*N
exactdiv(Ei,common);exactdiv(EL,common)
check('K_minus_one_has_common_served_divisor_factors',True)
# Check the independent connection bounds used in this algebraic proof.
ia=read('i-corrected-independent-audit.json');la=read('L-gauge-audit.json')
check('128 physical tangential i gauge entries audited',ia['tangent_connection_entries_checked']==128)
check('all native L gauge matrices bounded',la['bounded_native_matrices']=={'i':64,'j':64,'V':64})
# In raw frame physical matrices have at most L^-2; K*P has L^2.
# In i gauge physical tangent matrices are regular; K*P has i^0.
# Along w only Gamma_w is at most w^-1. Along j only Gamma_j has
# at most j^-1. Along N each has at most N^-1; T only w at most T^-1.
# Delta is a unit at generic points of each of these divisors.
check('Delta coprime to every served factor',all(divmod(Delta,p)[1] for p in [i,j,w,T,N,L]))
# Store small polynomial prefactors B=i^7 L^3 P0. Final P=Hi^7 HL^3 B/Delta^10.
B={t:[] for t in base}
for t,vec in base.items():
 for z in vec:
  zz=F(i**7*L**3)*z
  rem=zz.d
  for p in [j,w]:
   while not divmod(rem,p)[1]:rem=exactdiv(rem,p)
  assert rem.total_degree()==0
  B[t].append(zz.data())
check('B coefficients only j/w denominators',True)
write('simple-discriminant-current.json',{
 'schema':'factored-compact-current-v3','Pi':'0','Pj_and_Pw':'P_p=Hi^7*HL^3/Delta^10 * B[p], p=j,w',
 'Hi':str(Hi),'HL':str(HL),'Ei':str(Ei),'EL':str(EL),'Delta':str(Delta),'B':B,
 'equivalent_multiplier':'K=(1-Ei/Delta)^7*(1-EL/Delta)^3; multiply the original frozen joint plus w current by K',
 'source':'actual-source-polynomial.json','native_matrices':'packet/coupled-fresh/ruling-source/full-base-connection',
 'residual':'R=S-(partial_j+Gamma_j,physical)Pj-(partial_w+Gamma_w,physical)Pw',
 'residual_ring':'Q[i,j,w,1/Delta]^8','residual_common_denominator_bound':'Delta^11',
 'literal_fiber':'Jfiber=-sum_word word*(fj_word dot Pj+fV_word dot (beta_j Pj+beta_w Pw))/(D*Jbar) di dj dw, physical v pullback; use all16 native words',
 'certificate':False})
write('simple-discriminant-audit.json',{'status':'PASS','checks':checks,'exact_current_valuations':orders,'all_eight_rows':True,'physical_directions_used':['j','w'],'residual_support':['Delta'],'residual_common_Delta_power_bound':11,'proof':'Exact source denominator clearing; exact cutoff identities; independently computed native connection bounds; divisor valuation proof. No full expanded residual numerator is claimed.','scope':'Affine compact residual only. Fiber-exact terms retained. Base infinity, relative fiber chart and original cleared identity remain obligations.','inputs':{f:sha(f) for f in ['simple-discriminant-current.json','w-correction.json','actual-source-polynomial.json']},'seconds':time.time()-st})
print('PASS smaller current: Pi=0, affine residual support Delta only, power<=11',round(time.time()-st,3),flush=True)
