from pathlib import Path
import json,time
from flint import fmpq_mpoly_ctx,fmpq_mpoly
r=Path(__file__).resolve().parents[1];st=time.time();C=fmpq_mpoly_ctx.get(('i','j','x','v'));i,j,x,v=C.gens();D=fmpq_mpoly(json.loads((r/'packet/coupled-fresh/ruling-source/full-base-connection/rank8-ij-connections-results.json').read_text())['common_denominator'],C)
Q=8*(i*x*x+2*x+3)**2-j*j*x*x*(2*i*x*x+5*x+8)
B=(2*i*x*x+5*x+8)*(x+2);H=v*B-4*x**6
res=Q.resultant(H,'x');q,rem=divmod(res,D);assert not rem
print('Resultant identity factor',q.factor(),'elapsed',time.time()-st,flush=True)
disc=Q.discriminant('x');print('Critical quartic discriminant',disc.factor(),'elapsed',time.time()-st,flush=True)
dv=D.discriminant('v');fac=dv.factor();print('D discriminant factors',[(len(f.to_dict()),e,str(f)[:100]) for f,e in fac[1]],'elapsed',time.time()-st,flush=True)
(r/'critical-quartic-model.json').write_text(json.dumps({'status':'PASS exact resultant identity','critical_quartic':str(Q),'critical_value_relation':str(H),'resultant_Q_H_equals_native_D_times':str(q),'quartic_discriminant':str(disc),'quartic_discriminant_factors':[{'polynomial':str(f),'multiplicity':int(e)} for f,e in disc.factor()[1]],'native_D_v_discriminant_factors':[{'polynomial':str(f),'multiplicity':int(e)} for f,e in fac[1]],'critical_a':'-2*(i*x^2+2*x+3)/(j*x)','critical_a_squared':'i*x^2+5*x/2+4','critical_v':'4*x^6/((2*i*x^2+5*x+8)*(x+2))','scope':'Auxiliary critical-point cover; no current or certificate asserted','seconds':time.time()-st},indent=2)+'\n')
