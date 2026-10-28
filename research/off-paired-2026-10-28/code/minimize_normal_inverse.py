from pathlib import Path
from flint import fmpq_mpoly_ctx,fmpq_mpoly
import json,time
root=Path(__file__).resolve().parents[1];st=time.time();C=fmpq_mpoly_ctx.get(('i','j','rho','v'));i,j,rho,v=C.gens()
def P(s):return fmpq_mpoly(s,C)
d=json.loads((root/'physical-discriminant-inverse.json').read_text());inv,den,bez=[P(d[k]) for k in ['inverse_numerator','denominator','Bezout_coefficient']]
g=inv.gcd(den);g=g.gcd(bez);inv=inv//g;den=den//g;bez=bez//g
D=P(json.loads((root/'packet/coupled-fresh/ruling-source/full-base-connection/rank8-ij-connections-results.json').read_text())['common_denominator'])
assert inv*(D.derivative('i')+rho*v*D.derivative('v'))+bez*D==den
_,factors=den.factor();d.update({'inverse_numerator':str(inv),'denominator':str(den),'Bezout_coefficient':str(bez),'denominator_factors':[{'polynomial':str(f),'multiplicity':int(e)} for f,e in factors],'removed_common_factor':str(g),'status':'PASS reduced exact physical normal inverse','seconds':time.time()-st})
(root/'physical-discriminant-inverse-reduced.json').write_text(json.dumps(d,indent=2)+'\n')
print('Removed',g.factor(),'reduced den factors',[(e,len(f.to_dict())) for f,e in factors],'terms inv/den/bez',len(inv.to_dict()),len(den.to_dict()),len(bez.to_dict()),'seconds',time.time()-st,flush=True)
