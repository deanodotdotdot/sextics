"""Exact unrestricted physical Euler-current probe; no pole-preservation claim."""
from audit_core import *
st=time.time();wi=F(2*i);wj=F(j);ww=(-6*vp-wi*vp.diff('i')-wj*vp.diff('j'))/vp.diff('w')
Pp={'i':AP*wi,'j':AP*wj,'w':AP*ww}
error=4*AP-sum((z.diff(p) for p,z in Pp.items()),F(0))
write('euler-scalar-probe.json',{'status':'PASS exact reduction to scalar' if error else 'ZERO scalar residual','Pi_row6':Pp['i'].data(),'Pj_row6':Pp['j'].data(),'Pw_row6':Pp['w'].data(),'residual_only_row6':error.data(),'new_denominator_factors':str(ww.d.factor()),'not_certificate':bool(error),'seconds':time.time()-st})
print('Exact scalar residual zero?',not bool(error),'num/den terms',len(error.n.to_dict()),len(error.d.to_dict()),'seconds',time.time()-st,flush=True)
