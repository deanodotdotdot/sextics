"""Physical denominator inventory for the actual discriminant current."""
from audit_core import *
from flint import fmpq_mpoly_ctx,fmpq_mpoly
st=time.time();saved=read('physical-discriminant-inverse-reduced.json');C3=fmpq_mpoly_ctx.get(('i','j','rho'));rhoF=vp.diff('i')/vp
out=[]
for index,item in enumerate(saved['denominator_factors']):
 native=fmpq_mpoly(item['polynomial'],C3);degree=max((e[2] for e in native.to_dict()),default=0);num=zero
 for (a,b,c),coef in native.to_dict().items():num+=coef*i**a*j**b*rhoF.n**c*rhoF.d**(degree-c)
 rational=F(num,rhoF.d**degree);num=rational.n
 g=num.gcd(Delta);assert g.total_degree()==0,('new denominator contains Delta',index)
 content,factors=num.factor()
 ff=[{'polynomial':str(p),'multiplicity':int(e),'degrees':[int(z) for z in p.degrees()],'terms':len(p.to_dict())} for p,e in factors]
 out.append({'native_factor':item,'rho_degree':int(degree),'physical_numerator_factors':ff,'physical_denominator':str(rational.d),'coprime_to_Delta':True})
 print('factor',index,'rho degree',degree,'physical numerator factors',[(z['multiplicity'],z['terms']) for z in ff],'seconds',round(time.time()-st,3),flush=True)
write('reduced-inverse-physical-inventory.json',{'status':'PASS','rho':rhoF.data(),'all_physical_inverse_factors_coprime_to_Delta':True,'factor_inventory':out,'conclusion':'The actual source-serving normal current removes the generic Delta pole, but introduces the listed other divisors; this is an alternative current, not a completion of the Delta-only current.','other_possible_denominators':['i','j','N','L'],'no_inverse_v_w':True,'physical_derivatives_retained':['v_i','rho_i'],'seconds':time.time()-st})
print('PASS actual inverse denominator inventory',time.time()-st,flush=True)
