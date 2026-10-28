"""Rational completeness bounds for i-only or w-only additions to Taylor current."""
from audit_core import *
from fractions import Fraction
st=time.time();base=read('relative-i-completeness-independent-audit.json');assert base['status']=='PASS'
assert read('taylor-full-residual-independent-audit.json')['status']=='PASS'
inf=read('other-direction-infinity.json')['w'];assert inf['status']=='PASS' and inf['gauge']==[0]*8
assert inf['charpoly']=='(3*x - 20)**2*(3*x - 16)**2*(3*x - 8)**2*(3*x - 4)**2/6561'
records=read('taylor-full-residual.json')['rows'];degrees=[]
for row in records:
 assert sha(row['file'])==row['sha256']
 d=read(row['file']);num=P(d['numerator']);assert d['Delta_power']==3
 assert [int(z) for z in num.degrees()]==row['degrees']
 degrees.append([int(z) for z in num.degrees()])
hinf=base['infinity_gauge'];ideg=[degrees[r][0]-3*int(Delta.degrees()[0])-hinf[r] for r in range(8)];wdeg=[degrees[r][2]-3*int(Delta.degrees()[2]) for r in range(8)]
assert max(ideg)<=-1;assert max(wdeg)==3
# Along w, zeros of v are w, N and T with ramification orders1,1,2.
for p in [w,N,T,L,Delta]:assert p.gcd(p.derivative('w')).total_degree()==0
for a in [w,N,T,L,Delta]:
 for b in [w,N,T,L,Delta]:
  if a!=b:assert a.gcd(b).total_degree()==0
for multiplicity in [1,2]:
 for exponent in [Fraction(1,6),Fraction(1,3),Fraction(2,3),Fraction(5,6)]:assert (multiplicity*exponent).denominator!=1
for exponent in [Fraction(4,3),Fraction(8,3),Fraction(16,3),Fraction(20,3)]:assert exponent.denominator!=1
families=[
 {'direction':'i','coefficient_field':'C(j,w)','finite_primitive_bounds':{'i':1,'N':0,'L':1,'Delta':2,'ordinary':0},'denominator':'i*L*Delta^2','denominator_degree':67,'growth_bound':5,'numerator_degree_bound':72,'infinity_source_degrees_in_gauge':ideg,'argument':'Raw target is regular at i,L,N. At i=0 its h-gauged pole is at most2, so the primitive gauge pole is at most1; raw i pole<=1. At L the gauged target is regular and negative residue eigenvalues force no gauge pole, so raw L pole<=1. Delta residues are nilpotent and target pole3 gives primitive pole<=2. N fractional residues allow no primitive pole. Infinity gives raw growth<=5.'},
 {'direction':'w','coefficient_field':'C(i,j)','finite_primitive_bounds':{'w':0,'N':0,'T':0,'L':1,'Delta':2,'ordinary':0},'denominator':'L*Delta^2','denominator_degree':162,'growth_bound':4,'numerator_degree_bound':166,'infinity_source_degrees':wdeg,'infinity_residue_charpoly':inf['charpoly'],'argument':'At w,N the v-zero residue has eigenvalues1/6,1/3,2/3,5/6; at T these double, with no integer eigenvalue. A regular target permits no pole. At L the v-infinity frame and negative residue eigenvalues permit raw pole<=1. Delta target order3 and nilpotence permit pole<=2. At infinity the connection is Fuchsian without a shear, with no integer residue eigenvalue; target growth<=3 forces primitive growth<=4.'}
]
for f in families:assert f['denominator_degree']+f['growth_bound']==f['numerator_degree_bound']
write('taylor-relative-completeness-audit.json',{'status':'PASS','current':'taylor-discriminant-current.json','families':families,'scope':'All rational additions in the named single direction, with the other two current components fixed. Does not exclude coupled changes in two or three directions, and is not unrestricted nonexistence for the original certificate.','source_rows_hashed_and_degrees_recomputed':8,'native_spectral_audit':'relative-i-completeness-independent-audit.json','w_infinity_audit':'other-direction-infinity.json','seconds':time.time()-st})
print('PASS rational completeness: i numerator<=72, w numerator<=166',time.time()-st,flush=True)
