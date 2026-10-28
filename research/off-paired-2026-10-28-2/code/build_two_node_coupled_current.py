from audit_core import *
st=time.time();e_i=(1-i)/3;e_j=j/2;s=4*i-1;h0=s**3*v+1728
h1=32*i**6*v*v-16*i**5*v*v+1728*i**3*v-10800*i*i*v+11250*i*v-3125*v+23328
result={'scope':'Native coupled source current near the double critical value at j=+/-1, away from exceptional intersections; no global physical closure','native_current':{'Pi':'-(1-i)*e7/3','Pj':'-j*e7/2','Pv':'0'},'source':'(4I-GammaV+2i Gamma_i+j Gamma_j)e6','divergence_of_scalar_coefficients':'-e7/6','h0':str(h0),'h1':str(h1),'slices':[]}
for sign in [1,-1]:
 d=D.subs({'j':sign});assert d==P('512/2187')*h1*h0*h0
 rows=[]
 for rr in range(8):
  z=(4*D if rr==6 else zero)-G['V'][rr][6]+2*i*G['i'][rr][6]+j*G['j'][rr][6]+e_i*G['i'][rr][7]+e_j*G['j'][rr][7]+(D/6 if rr==7 else zero)
  qq,rem=divmod(z.subs({'j':sign}),h0*h0);assert not rem,(sign,rr)
  rows.append(str(qq));print('slice',sign,'row',rr,'quotient terms',len(qq.to_dict()),flush=True)
 result['slices'].append({'j':sign,'all_eight_double_factor_cancellations':True,'residual_numerators':rows,'residual_denominator':str(P('512/2187')*h1)})
# Two roots of Bnode represent the two colliding critical points.
result['critical_explanation']={'Bnode':'(4i-1)x^2+6x+12','a':'-(x+2)/(2j), j^2=1','v':'-1728/(4i-1)^3','discriminant_Bnode':'12*(7-16i)','coupled_normal_identity':'((1-i)/3)*x^2+(j/2)*a*x = 1 modulo Bnode','source_residue_identity':'2i*x^2+j*a*x+3*(x+2)=-x; multiply by y','exceptional_factors':['i-1/4','i-7/16','remaining h1 at v=-1728/(4i-1)^3'],'physical_Piola':'Pi=-AP*(1-i)*e7/3, Pj=-AP*j*e7/2, Pw=AP*((1-i)*v_i/3+j*v_j/2)*e7/v_w. Density derivative terms remain and introduce the v_w critical divisor; all sixteen fiber terms are required.'}
result['status']='PASS exact native coupled cancellation of both colliding branches';result['seconds']=time.time()-st;write('two-node-coupled-current.json',result)
print('PASS native coupled double-value cancellation',time.time()-st,flush=True)
