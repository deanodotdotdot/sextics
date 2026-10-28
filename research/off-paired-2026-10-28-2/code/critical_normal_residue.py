from critical_residue_factorization import *
dip=pull(D.derivative('i'));assert dip
normalized=[F(GP['i'][row][0],dip) for row in range(8)]
for idx,z in enumerate(normalized):
 print('normalized column row',idx,'factors',[(str(f),int(e)) for f,e in z.d.factor()[1]],flush=True)
out={'status':'PASS exact normalized critical-cover residue','definition':'N=Gamma_i_numerator/D_i after critical parametrization, N=normalized_column*ell','normalized_column':[z.data() for z in normalized],'basis_evaluation_row':[z.data() for z in ell],'denominator_factors':[[{'polynomial':str(f),'multiplicity':int(e)} for f,e in z.d.factor()[1]] for z in normalized],'scope':'On the normalized native discriminant cover; not a physical correction or a proof of descent across singular discriminant branches','seconds':time.time()-st}
(r/'critical-normalized-residue.json').write_text(json.dumps(out,indent=2)+'\n')
from fractions import Fraction
from math import lcm
Djp=pull(D.derivative('j'));Dvp=pull(D.derivative('v'))
assert x*Djp==a*dip
assert 6*nums[2]*x*x*Dvp==-3*(x+2)*dens[2]*dip
cusp=5*x*x+6*x*a*a+26*x+16*a*a+32;base=a**3*x**4*cusp
vec=[];scale=1
for z in normalized:
 q,rem=divmod(base*z.n,z.d);assert not rem;vec.append(q)
 for c in q.to_dict().values():scale=lcm(scale,Fraction(str(c)).denominator)
vec=[z*scale for z in vec]
out['gradient_normal_identities']=['x*D_j=a*D_i','6*v*x^2*D_v=-3*(x+2)*D_i'];out['common_column_denominator']=str(scale*base);out['common_column_numerators']=[str(z) for z in vec];out['common_column_factorization']=str(scale)+'*a^3*x^4*C, C=5*x^2+6*x*a^2+26*x+16*a^2+32';out['full_matrix_denominator_support']=['x','a','x+2','C'];(r/'critical-normalized-residue.json').write_text(json.dumps(out,indent=2)+'\n')
print('Common column denominator multiplier',scale,'numerator term counts',[len(z.to_dict()) for z in vec],flush=True)
