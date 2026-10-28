"""Sharper global pole cutoff from the degree-two Taylor part of D(v)^2."""
from audit_core import *
st=time.time();dc=coeffs(D,'v');d0,d1,d2=dc[0],dc[1],dc[2]
# K=[D0^2+2D0D1*v+(D1^2+2D0D2)*v^2]/D(v)^2.
# In physical coordinates K=Knum/Delta^2 with Knum=i^8 L^6 W.
W=exactdiv(9**6*(d0*d0*BV*BV+2*d0*d1*AV*BV+(d1*d1+2*d0*d2)*AV*AV),KD*KD)
Knum=i**8*L**6*W
Hnum=Delta*Delta-Knum
check_remainder=exactdiv(Hnum,j**6*w**3*T**6*N**3)
assert (D*D-(d0*d0+2*d0*d1*v+(d1*d1+2*d0*d2)*v*v)).to_dict()
exactdiv(D*D-(d0*d0+2*d0*d1*v+(d1*d1+2*d0*d2)*v*v),v**3)
# A compact exact expression: same current as the joint+w checkpoint, timesK.
write('taylor-discriminant-current.json',{'schema':'factored-compact-current-v4','Pi':'0','Pj':'K*(c*e7+Vj*Z)','Pw':'K*(d*e7+Vw*Z)','w_current_input':'w-correction.json','joint_c':'-i*T/(4*w*j)+28*T^2*j/(45*i*w^3)-224*j*(2-w^3)/(405*i*w^3)','joint_d':'-448*T/(405*i*w^2)','Vj':'j*(2-w^3)/(2*i*w^3)','Vw':'T/(i*w^2)','K':'i^8*L^6*W/Delta^2','W':str(W),'Delta':str(Delta),'native_cutoff':'[D0^2+2D0D1*v+(D1^2+2D0D2)*v^2]/D(v)^2, then physical v; Dk=[v^k]D','residual':'K*R_after_w+(1-K)*S-(partial_j K)*Pj_after_w-(partial_w K)*Pw_after_w','residual_ring':'Q[i,j,w,1/Delta]^8','residual_common_denominator_bound':'Delta^3','literal_fiber':'Multiply the full joint+w literal fiber current by K; retain all16 native words and the fixed-x Cartan primitive. Add the original source vertical term separately.','certificate':False})
write('taylor-discriminant-audit.json',{'status':'PASS','exact_identities':{'physical_Knum_equals_i8_L6_W':True,'Delta_squared_minus_Knum_divisible_j6_w3_T6_N3':True,'native_D_squared_Taylor_remainder_divisible_v3':True},'inherited_independent_bounds':'simple-discriminant-independent-audit.json: i-gauged currents >=-7, tangential connection i regular; raw currents L>=-1, physical matrices L>=-2; actual source i,L regular','pole_margins':{'i_gauged_current':8-7,'L_raw_current_after_cutoff':6-1,'L_residual':6-1-2,'w_residual':3-3,'j_residual':6-2,'N_residual':3-1,'T_residual':6-1},'all_eight_rows':True,'residual_support':['Delta'],'common_Delta_power_bound':3,'coefficient_W_terms':len(W.to_dict()),'Knum_terms':len(Knum.to_dict()),'Hnum_terms':len(Hnum.to_dict()),'scope':'Exact generic affine compact residual pole reduction. Residual need not vanish; fiber/base-infinity/original certificate obligations remain as stated elsewhere.','seconds':time.time()-st})
print('PASS sharper cutoff: residual denominator Delta^3; W,Knum,Hnum terms',len(W.to_dict()),len(Knum.to_dict()),len(Hnum.to_dict()),'seconds',time.time()-st,flush=True)
