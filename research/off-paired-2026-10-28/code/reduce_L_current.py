"""Move the old explicit L current pole to Delta without new served divisors."""
from audit_core import *
st=time.time();d4=coeffs(D,'v')[4]
E=exactdiv(d4*AV**4,KD*i*i)
H=exactdiv(Delta-E,L)
assert Delta==E+L*H
# The only explicit L pole in the old w coefficient Z is in row7:
# Z7 = (L-regular terms) - 4096*i^2*w^2/(9L).
# Replace it with -4096*i^2*w^2*H/(9Delta).
old=read('w-correction.json');z7=jf(old['Z'][7]);singular=F(-4096*i*i*w*w,9*L)
regular=z7-singular
leftden=regular.d
while not divmod(leftden,i)[1]:leftden=exactdiv(leftden,i)
assert leftden.total_degree()==0
newz7=regular+F(-4096*i*i*w*w*H,9*Delta)
new=old.copy();new['Z']=[z.copy() for z in old['Z']];new['Z'][7]=newz7.data();new['status']='L pole removed from w coefficient current using Delta=E+L*H'
write('w-correction-L-removed.json',new)
# Added current equals minus E/Delta times old singular contribution.
Vj=F(j*(2-w**3),2*i*w**3);Vw=F(T,i*w*w)
change=newz7-z7
assert change==F(4096*i*i*w*w*E,9*L*Delta)
Pj=Vj*change;Pw=Vw*change
# Their numerators have sufficient factors for N,j,w,T preservation and
# i-regularity after the h gauge; only row7, h7=2, is nonzero.
for name,z,required in [('j',Pj,i**4*j*w**3*N),('w',Pw,i**4*w**4*T*N)]:
 exactdiv(z.n,required)
 # Denominator support is L and Delta only; no i,j,w,T,N factor.
 exactdiv(L*Delta,z.d)
write('L-current-reduction.json',{'status':'PASS','Delta_identity':'Delta=E+L*H','E':str(E),'H':str(H),'native_v4_factorization':str(d4.factor()),'new_Z7':newz7.data(),'added_Pj_row7':Pj.data(),'added_Pw_row7':Pw.data(),'all_other_added_components':'0','preservation':'Added currents have i^4 N factors, Pj has j*w^3 and Pw has w^4*T; physical tangential matrices are regular in i gauge. Hence i principal parts unchanged. Direct w audit remains required.','inputs':{f:sha(f) for f in ['w-correction.json','w-correction-L-removed.json']},'seconds':time.time()-st})
print('PASS exact L-current replacement; E/H terms',len(E.to_dict()),len(H.to_dict()),'seconds',time.time()-st,flush=True)
