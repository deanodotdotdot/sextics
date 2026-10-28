"""Independent direct original-chart density versus compact source check."""
import json,time
from pathlib import Path
from flint import fmpq_mpoly_ctx,fmpq_mpoly
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'packet/coupled-fresh/ruling-source/full-base-connection';st=time.time()
C=fmpq_mpoly_ctx.get(('a','x','y','i','j','v'));a,x,y,i,j,v=C.gens();zero=C.constant(0);parse=lambda z:fmpq_mpoly(z.replace('**','^'),C)
src=json.loads((P/'source-euler-current-results.json').read_text());D=parse(src['remaining_common_denominator']);Q=[parse(z) for z in src['remaining_vector_numerators']]
basis=[C.constant(1),x,x**3,x**4-v*(i-j*j/4)*(i-5*j*j/4)*x*x/8,a,a*x+j*x*x/2,y,y*x]
J=v*(2*a*a+j*a*x)-2*y*y;B=2*i*x+j*a+1;da=-v*a*B-6*y*x*x;dy=v*y*B+3*v*x*x*(2*a+j*x)
def delta(p):return p.derivative('a')*da+p.derivative('x')*J+p.derivative('y')*dy
words=[parse(z) for z in src['fiber_primitive_words']]
FD=sum((parse(z)*word for z,word in zip(src['fiber_primitive_D_numerators'],words)),zero)
# D is shared between the source vector and its source fiber primitive.
Knum=FD+D*v*x*y
compact=sum((z*b for z,b in zip(Q,basis)),zero)*v*J*J-delta(Knum)*J+Knum*delta(J)
canonical=-D*v*v*x*y*(6*v*a*a+2*y*y+2*v*j*a*x)
difference=compact-canonical
print('uncleared term count',len(difference.to_dict()),flush=True)
# Substitute y=x^3/a, clear the largest negative a exponent, and reduce the quartic.
ymax=max((ex[2]-ex[0] for ex in difference.to_dict()),default=0);ymax=max(0,ymax)
terms={}
for (ae,xe,ye,ie,je,ve),coef in difference.to_dict().items():
 exp=(ae-ye+ymax,xe+3*ye,0,ie,je,ve);terms[exp]=terms.get(exp,0)+coef
rem=C.from_dict(terms);quartic=v*a**4+v*j*x*a**3+v*(i*x*x+x+1)*a*a+x**6
steps=0
while rem and rem.degrees()[0]>=4:
 deg=rem.degrees()[0];lead=C.from_dict({(0,xe,ye,ie,je,ve):coef for (ae,xe,ye,ie,je,ve),coef in rem.to_dict().items() if ae==deg})
 rem=v*rem-lead*a**(deg-4)*quartic;steps+=1
assert not rem,str(rem)
result={'status':'PASS','checks':{'original_Graw_F_equals_3J':'symbolically recorded in transport notes; direct curve equality verified here','compact_source_plus_literal_vertical_correction_equals_original_density':True,'quartic_pseudoremainder_zero':True},'target_density_in_nu0_units':'-Aphysical*x*y*v^2*(6*a^2+2*y^2/v+2*j*a*x)/Jbar^2','source_vertical_primitive':'-Aphysical*(fD_b+v*x*y/Jbar) di dj dw','clear_a_power':int(ymax),'pseudo_remainder_steps':steps,'seconds':time.time()-st}
(ROOT/'original-density-binding.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
