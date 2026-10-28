"""Bind the two native denominator normalizations in the original field graph."""
from audit_core import *
st=time.time()
s=read('packet/coupled-fresh/ruling-source/full-base-connection/source-euler-current-results.json')
ds=P(s['remaining_common_denominator'])
ratio=exactdiv(ds,D)
assert ratio==P('67108864/2187')
assert s['fiber_primitive_words']==ij['primitive_words']
checks=[]
for t,z in enumerate(s['fiber_primitive_D_numerators']):
 raw=P(vr['primitive_numerators'][t][6])-2*i*P(ij['primitive_numerators']['i'][t][6])-j*P(ij['primitive_numerators']['j'][t][6])
 assert P(z)*D==raw*ds,t
 checks.append(t)
write('source-fiber-normalization-audit.json',{'status':'PASS','source_denominator_over_native_denominator':str(ratio),'all_16_literal_words':checks,'identity':'sum(source_D_num*word)/Dsource = sum((fV_num_col6-2i*fi_num_col6-j*fj_num_col6)*word)/Dnative = Jbar*fD_actual','field_numerator_convention':'Hfib and FDnum in the original field graph omit the common Jbar denominator, which cancels in ux=-(Hfib+Aphysical*FDnum+Aphysical*v*x*y)/(rho*v).','scope':'The point evaluator already used the correct source denominator. This audit corrects an ambiguous normalization in the descriptive expression graph; it does not change the verified current or point result.','seconds':time.time()-st})
print('PASS both native denominator normalizations, all16 source fiber words',flush=True)
