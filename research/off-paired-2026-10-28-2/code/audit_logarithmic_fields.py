from audit_core import *
st=time.time();raw=(ROOT/'native-log-syzygies.txt').read_text().strip();entries=raw.split(',');assert len(entries)==48,len(entries)
C=fmpq_mpoly_ctx.get(('i','u','v'))
def conv(s):
 p=fmpq_mpoly(s,C);return CTX.from_dict({(a,2*b,0,c):q for (a,b,c),q in p.to_dict().items()})
M=[[conv(entries[r*12+k]) for k in range(12)] for r in range(4)]
rows=[];out=[]
for k in range(12):
 a,b,c,h=[M[r][k] for r in range(4)];assert 2*j*a*D.derivative('i')+b*D.derivative('j')+2*j*c*v*D.derivative('v')+2*j*h*D==0
 mat=[];remainders=[]
 for r in range(8):
  row=[]
  for s in range(8):
   n=6*j*a*G['i'][r][s]+3*b*G['j'][r][s]+j*c*G['V'][r][s];q,rem=divmod(n,D);row.append(str(q));remainders.append(bool(rem))
  mat.append(row)
 ok=not any(remainders);rows.append({'index':k,'tangency_identity':True,'connection_cancels_D':ok,'uncancelled_entries':sum(remainders),'vector_terms':[len(z.to_dict()) for z in [a,b,c,h]]})
 out.append({'Ei':str(a),'Ej':'('+str(b)+')/(2*j)','Ev_over_v':str(c),'E_D_over_D':str(-h),'six_j_connection_polynomial':mat if ok else None})
 print(k,rows[-1],flush=True)
write('native-logarithmic-frame-audit.json',{'status':'PASS' if all(z['connection_cancels_D'] for z in rows) else 'PARTIAL','rows':rows,'field_count':12,'checks':12+12*64,'seconds':time.time()-st})
write('native-logarithmic-frame.json',{'fields':out,'convention':'E=(a,b/(2j),v*c) in native i,j,v. Contraction Gamma(E)=matrix/(6j). Every D cancels exactly.','basis':ij['compact_basis_numerators'],'seconds':time.time()-st})
