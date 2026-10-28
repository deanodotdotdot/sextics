"""A sharp lower bound within the boundary-preserving scalar cutoff strategy.

This is not a lower bound on arbitrary currents or original certificates.
"""
from audit_core import *
from fractions import Fraction

st=time.time()
dw0=coeffs(Delta,'w').get(0,zero)
assert dw0==P('281474976710656/282429536481')*i**6*j**8
assert coeffs(Delta,'i').get(0,zero)
cur=read('taylor-discriminant-current.json')
assert cur['K']=='i^8*L^6*W/Delta^2'
kn=i**8*L**6*P(cur['W'])
assert coeffs(kn,'w').get(0,zero)==dw0**2
assert min(int(e[0]) for e in kn.to_dict())==8
write('scalar-cutoff-minimum-audit.json',{
 'status':'PASS exact restricted minimum',
 'Delta_at_w_zero':str(dw0),
 'Delta_not_divisible_by_i':True,
 'class':'K=P/Delta^m, P in C[i,j,w], m a nonnegative integer, ord_i(K)>=7, and K(i,j,0)=1 as a rational identity in C(i,j)',
 'proof':'Since i does not divide Delta, i^7 divides P. Specialization w=0 gives P(i,j,0)=Delta(i,j,0)^m=c^m*i^(6m)*j^(8m). This nonzero polynomial has exact i order6m, hence6m>=7 and m>=2. The saved Taylor cutoff has m=2, exact i order8, and K(w=0)=1, so the bound is attained.',
 'minimum_denominator_power_in_class':2,
 'attained_by':'taylor-discriminant-current.json',
 'scope':'Explains the minimum cutoff denominator in this specific vanishing-based strategy. Does not exclude other scalar cutoffs that cancel principal parts without order7 vanishing, vector-valued coupled corrections, residual denominators below Delta^3, or the original certificate.',
 'seconds':time.time()-st})
print('PASS restricted scalar cutoff minimum m=2',time.time()-st,flush=True)
