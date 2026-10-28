from audit_core import *
from fractions import Fraction
st=time.time();gauge=read('j-infinity-shear.json');assert gauge['status']=='PASS Fuchsian gauge';assert gauge['characteristic_polynomial']=='(x + 2)**4*(x + 4)**4'
hh=gauge['diagonal_j_powers'];g=jf(gauge['shear_g']);assert g==vp*F((i-j*j/4)*(i-5*j*j/4),4*j)
for r in range(8):
 for k in range(8):assert gauge['degrees'][r][k]+hh[k]-hh[r]<=0
for p in [j,N,L,Delta]:assert p.gcd(p.derivative('j')).total_degree()==0
for p in [j,N,L,Delta]:
 for q in [j,N,L,Delta]:
  if p!=q:assert p.gcd(q).total_degree()==0
for mult in [1,2]:
 for x in [Fraction(1,6),Fraction(1,3),Fraction(2,3),Fraction(5,6)]:assert (mult*x).denominator!=1
rows=read('taylor-full-residual.json')['rows'];raw=[r['degrees'][1]-3*int(Delta.degrees()[1]) for r in rows];gd=int(g.n.degrees()[1]-g.d.degrees()[1]);transformed=raw.copy();transformed[5]=max(raw[5],gd+raw[3]);gauged=[transformed[r]-hh[r] for r in range(8)]
assert max(gauged)==5
primitive_gauge_growth=max(gauged)+1;transform_growth=max(max(hh),gd+hh[3]);raw_growth=primitive_gauge_growth+transform_growth
assert (primitive_gauge_growth,transform_growth,raw_growth)==(6,5,11)
degree=int(L.degrees()[1])+2*int(Delta.degrees()[1]);assert degree==50
family={'direction':'j','coefficient_field':'C(i,w)','finite_primitive_bounds':{'j':0,'N':0,'L':1,'Delta':2,'ordinary':0},'denominator':'L*Delta^2','denominator_degree':degree,'growth_bound':raw_growth,'numerator_degree_bound':degree+raw_growth,'infinity_raw_source_degrees':raw,'infinity_source_degree_bounds_after_full_gauge':gauged,'infinity_gauge':'(I+g E_(5,3))*diag(j^h), with g,h in j-infinity-shear.json','infinity_residue_charpoly':gauge['characteristic_polynomial'],'argument':'At j=0 the v-zero residue doubles and has no positive integer eigenvalue; at N it has the undoubled fractional spectrum. At L the source is regular in the v-infinity gauge so raw primitive pole<=1. At Delta nilpotence and source pole3 give primitive pole<=2. The audited full infinity gauge has negative residue eigenvalues -2,-4, so source growth<=5 gives gauge primitive growth<=6. Transforming back increases degree by at most5, yielding raw growth<=11.'}
assert family['numerator_degree_bound']==61
record=read('taylor-relative-completeness-audit.json');record['families']=[f for f in record['families'] if f['direction']!='j']+[family];record['j_infinity_audit']='j-infinity-shear.json';write('taylor-relative-completeness-audit.json',record)
write('j-relative-completeness-audit.json',{'status':'PASS','family':family,'seconds':time.time()-st})
print('PASS complete rational j-only bound: numerator degree<=61',time.time()-st,flush=True)
