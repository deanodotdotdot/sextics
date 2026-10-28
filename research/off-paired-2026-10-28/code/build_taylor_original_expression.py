"""Bind the verified generic transport to the preferred Taylor current."""
from audit_core import *
d=read('original-partial-field-expression.json')
d['current']='taylor-discriminant-current.json'
d['scope']='Explicit factorized partial rational field and generic transport identity. Denominator admissibility and homogeneous degree compatibility are proved in partial-field-admissibility-audit.json. No expanded homogeneous polynomial numerators/common denominator are exported. The nonzero original divergence proves that this field is not a certificate.'
d['normalization_audit']='source-fiber-normalization-audit.json'
d['base_polynomials']={'T':'1+w^3','N':'9*i^2*w^2-16*j^2*T','L':'256*T^5*N+729*i^6*j^2*w^6','Aphysical':'9*i^3*w*T/(j^2*N)','beta_j':'partial_j(v)/(6*v), with v=vp(i,j,w)','beta_w':'partial_w(v)/(6*v), with v=vp(i,j,w)'}
d['native_files']={'fj_num':'packet/coupled-fresh/ruling-source/full-base-connection/rank8-ij-connections-results.json:primitive_numerators.j','fV_num':'packet/coupled-fresh/ruling-source/full-base-connection/rank8-v-literal-primitives-results.json:primitive_numerators, including fixed-x Cartan term','source_D_num':'packet/coupled-fresh/ruling-source/full-base-connection/source-euler-current-results.json:fiber_primitive_D_numerators'}
assert 'Dsource=' in d['fiber_numerator'] and 'FDnum' in d['ux']
cur=read(d['current'])
for key in ['W','Delta']:
 assert all(int(e[1])%2==0 for e in P(cur[key]).to_dict())
write('original-taylor-partial-field-expression.json',d)
print('PASS original expression bound to Taylor current and correct source denominator',flush=True)
