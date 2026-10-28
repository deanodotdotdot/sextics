"""Check that the displayed Delta^3 denominator is not merely a loose bound."""
from audit_core import *
from flint import fmpq_poly

st=time.time();receipt=read('taylor-full-residual.json');rows=[]
def specialized(p):
 out=[fmpq(0)]*(int(p.degrees()[0])+1)
 for e,c in p.to_dict().items():out[int(e[0])]+=c
 return fmpq_poly(out)
delta_specialized=specialized(Delta)
for entry in receipt['rows']:
 assert sha(entry['file'])==entry['sha256']
 data=read(entry['file'])
 key='numerator' if 'numerator' in data else 'Rnum'
 p=P(data[key]);q,r=divmod(specialized(p),delta_specialized)
 assert r,('Unexpected removable Delta factor',entry['row'])
 valuations=[min(int(e[k]) for e in p.to_dict()) for k in range(3)]
 rows.append({'row':entry['row'],'nonzero_remainder_mod_Delta':True,'specialization':{'j':1,'w':1},'remainder_coefficients':[str(c) for c in r.coeffs()],'numerator_coordinate_valuations':dict(zip(['i','j','w'],valuations))})
 print('row',entry['row'],'Delta does not divide numerator; coordinate valuations',valuations,'seconds',round(time.time()-st,3),flush=True)
write('taylor-residual-denominator-audit.json',{'status':'PASS','rows':rows,'proof':'Polynomial divisibility by Delta would remain true after j=w=1. All eight exact Q[i] remainders are nonzero.','conclusion':'No row numerator is divisible by the entire polynomial Delta. The common displayed Delta^3 denominator cannot be reduced to Delta^2 by canceling a global Delta factor. This does not assert every irreducible factor has order3 or rule out another current with a smaller residual denominator.','seconds':time.time()-st})
