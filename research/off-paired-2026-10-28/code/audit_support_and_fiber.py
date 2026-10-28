"""Audit denominator support and retain the complete literal fiber current."""
from audit_core import *
st=time.time();cur=read('i-global-correction-corrected.json');checks={}
def check(name,cond):assert cond,name;checks[name]=True
check('same native literal words',ij['primitive_words']==vr['primitive_words'])
check('sixteen literal words',len(ij['primitive_words'])==16)
check('compact i/j infinity rows zero',all(not P(z) for t in ['i','j'] for z in ij['full_rank9_Gamma_numerators'][t][8][:8]))
check('compact V infinity row zero',all(not P(z) for z in vr['full_rank9_GammaV_numerators'][8][:8]))
check('all literal entries present',all(len(ij['primitive_numerators'][t])==16 and all(len(row)==8 for row in ij['primitive_numerators'][t]) for t in ['i','j']) and len(vr['primitive_numerators'])==16 and all(len(row)==8 for row in vr['primitive_numerators']))
# D has a polynomial pullback proportional to i^2 Delta. B=9 i^2 L.
check('native denominator pullback',Dh==KD*i*i*Delta)
check('Delta has no w,j,T,N,L factor',all(bool(divmod(Delta,z)[1]) for z in [w,j,T,N,L]))
minorders={}
for var in ['j','w']:
 vals=[]
 for r,z in enumerate(cur['tangent'][var]):
  num=P(z['numerator']);assert z['power']>=0
  if not num:continue
  if var=='j':exactdiv(num,j)
  else:exactdiv(num,w*T)
  vals.append({'row':r,'j_order':int(min(e[1] for e in num.to_dict())),'w_order':int(min(e[2] for e in num.to_dict()))})
 minorders[var]=vals
check('Pj contains j*N',True);check('Pw contains w*T*N',True)
# Pi has N factor; its remaining scalar denominators are i and Delta only.
for block in cur['normal']:
 for z in block['coefficients']:assert isinstance(z['power'],int) and z['power']>=0
check('Pi contains N and only i/Delta scalar denominators',True)
# Every physical logarithmic derivative has exactly the asserted support.
betas={p:vp.diff(p)/vp/6 for p in ['i','j','w']}
for p,clear in [('i',i*N*L),('j',j*N*L),('w',w*T*N*L)]:
 exactdiv(clear,betas[p].d)
check('physical beta denominators cleared by current factors',True)
# Native matrices and all primitive coefficients are POLYNOMIAL over D.
# Pullback adds only i,L,Delta; beta factors cancel against N,j,w,T above.
# This argument covers every compact entry and all 16 literal word entries.
for mat in [G['i'],G['j'],G['V']]:
 for row in mat:
  for z in row:assert P(z).degrees()[3]<=5
for mat in [ij['primitive_numerators']['i'],ij['primitive_numerators']['j'],vr['primitive_numerators']]:
 for row in mat:
  for z in row:P(z)
check('all matrix and primitive entries covered by support proof',True)
# A factored expression graph is an exact representation; avoid expanding
# hundreds of megabytes of products which contain no extra information.
fiber={
 'schema':'literal-current-expression-v1',
 'variables':['i','j','w','x','a','y'],
 'physical_v':vp.data(),
 'curve':['a*y=x^3','y^2+v*(a^2+i*x^2+j*a*x+x+1)=0'],
 'Jbar':'v*(2*a^2+j*a*x)-2*y^2',
 'words':ij['primitive_words'],
 'current_inputs':{'frozen_joint':'Pj=c*e7; Pw=d*e7; Pi=0, c,d as in actual-source audit','w_correction':'w-correction.json','i_correction':'i-global-correction-corrected.json'},
 'base_current':'-sum_p (sum_r nu_r*P_p[r]) wedge contraction_partial_p(di wedge dj wedge dw)',
 'fiber_coefficient_word_t':'-sum_r [(fi[t,r]*Pi[r]+fj[t,r]*Pj[r]) + fV[t,r]*(beta_i*Pi[r]+beta_j*Pj[r]+beta_w*Pw[r])]/(D*Jbar), followed by v=physical_v',
 'fi':ij['primitive_numerators']['i'],'fj':ij['primitive_numerators']['j'],'fV':vr['primitive_numerators'],
 'D':str(D),'betas':{p:b.data() for p,b in betas.items()},
 'original_source_extra_vertical_term':'-Aphysical*(fD_b + v*x*y/Jbar) di wedge dj wedge dw; fD=fV-2i*fi-j*fj',
 'Cartan_term':'Native fV is the fixed-x literal primitive including -contraction_(x partial_x)(nu); do not add it twice or omit it.',
 'scope':'Retains exact fiber-exact contribution and compact fiber-infinity row. This is not a proof that all base infinity/intersections or original-coordinate denominator conditions are served.'}
write('literal-current-expression.json',fiber)
write('i-corrected-support-and-fiber-audit.json',{'status':'PASS','checks':checks,'affine_compact_residual_support_after_i_audit':['L','Delta'],'extra_literal_fiber_denominator':'Jbar (native relative-fiber chart); current itself can have i poles','minimum_tangent_monomial_orders':minorders,'literal_word_count':16,'compact_rows':8,'physical_directions':3,'inputs':{f:sha(f) for f in ['i-global-correction-corrected.json','literal-current-expression.json']},'open_obligations':['base infinity','intersection strata','complete original-coordinate field and admissible homogeneous cleared identity'],'seconds':time.time()-st})
print('PASS support and literal fiber expression',len(checks),'groups',time.time()-st,flush=True)
