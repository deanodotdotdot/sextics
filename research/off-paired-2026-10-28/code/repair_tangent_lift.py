"""Repair the j boundary lift's failure to vanish along j=0."""
from audit_core import *
cur=read('i-global-correction.json');Delta0=Delta.subs({'i':0})
oldq=[P(z['numerator']) for z in cur['tangent']['j']]
# Original all nonzero j-current coefficients have common Delta power one.
assert all(z['power']==1 for z in cur['tangent']['j'] if P(z['numerator']))
# Residue of Gamma_j,physical Pj at j=0: (GammaV(v=0)/3) Pj(j=0).
# Save a concrete nonzero first-row residue of the RESIDUAL (outer minus).
num=-N.subs({'j':0})*sum((G['V'][0][k].subs({'v':0,'j':0})*oldq[k].subs({'j':0}) for k in range(8)),zero)
den=3*i*D.subs({'v':0,'j':0})*Delta.subs({'j':0})
residue=F(num,den);assert residue
for z in cur['tangent']['j']:
 if P(z['numerator']):z['numerator']=str(P(z['numerator'])*Delta0);z['power']+=1
cur['status']='Corrected candidate: j tangent current multiplied by Delta(i=0)/Delta; independent complete audit pending'
cur.pop('checks',None);cur['repair']='Only Pj changes: Pj_new=Pj_old*Delta(0,j,w)/Delta(i,j,w). This preserves its i boundary value and forces a j^22 factor. Pi and Pw are unchanged.'
write('i-global-correction-corrected.json',cur)
write('i-original-lift-defect.json',{'status':'EXACT DEFECT','scope':'Original i-global-correction.json only; i principal-part cancellation may still hold','defect':'New j=0 pole from physical beta_j=1/(3j)+regular multiplying GammaV Pj','residual_first_row_j_residue':residue.data(),'residue_nonzero':True,'repair':'Multiply the whole added Pj by Delta(0,j,w)/Delta(i,j,w)','original_sha256':sha('i-global-correction.json'),'corrected_sha256':sha('i-global-correction-corrected.json')})
print('EXACT nonzero original j residue:',str(residue.n),'/',str(residue.d),flush=True)
print('Repaired Pj lift saved; other directions unchanged',flush=True)
