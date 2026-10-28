from pathlib import Path
from flint import fmpq_mpoly_ctx,fmpq_mpoly,nmod_mat,fmpz_mat
import json,time,sys
r=Path(__file__).resolve().parents[1];st=time.time();p=1009;C=fmpq_mpoly_ctx.get(('i','w'),ordering='degrevlex');i,w=C.gens();d=json.loads((r/'physical-two-node-curve.json').read_text());h=fmpq_mpoly(d['factors'][0]['polynomial'],C);gg=[h,h.derivative('i'),h.derivative('w')];target=i**4*(1+w**3)
for bound in range(28,49,2):
 columns=[];labels=[];support=set(target.to_dict())
 for k,g in enumerate(gg):
  for a in range(bound-g.total_degree()+1):
   for b in range(bound-g.total_degree()-a+1):
    e=(a,b);co={ee:int(c) for ee,c in (g*C.from_dict({e:1})).to_dict().items()};columns.append(co);labels.append((k,e));support.update(co)
 support=sorted(support);idx={e:k for k,e in enumerate(support)};rows=len(support);cols=len(columns);mat=nmod_mat(rows,cols+1,p)
 for col,co in enumerate(columns):
  for e,c in co.items():mat[idx[e],col]=c%p

 for e,c in target.to_dict().items():mat[idx[e],cols]=int(c)%p
 rr,rank=mat.rref();piv=[];bad=False
 for row in range(rank):
  c=next(k for k in range(cols+1) if rr[row,k]);piv.append(c)
  if c==cols:bad=True;break
 print('BOUND',bound,'shape',rows,cols,'rank',rank,'solvable',not bad,'seconds',time.time()-st,flush=True)
 if bad:continue
 # Pick a square nonsingular submatrix; solve exactly, then verify all equations.
 A=nmod_mat([[columns[c].get(e,0)%p for e in support] for c in piv],p);rr2,rk2=A.rref();assert rk2==rank
 rowids=[next(k for k in range(rows) if rr2[row,k]) for row in range(rank)]
 M=fmpz_mat([[columns[c].get(support[row],0) for c in piv] for row in rowids]);rhs=fmpz_mat([[int(target.to_dict().get(support[row],0))] for row in rowids]);print('EXACT_SOLVE',rank,time.time()-st,flush=True);sol=M.solve(rhs);print('EXACT_SOLVE_DONE',time.time()-st,flush=True)
 mult=[C.constant(0) for _ in gg]
 for n,c in enumerate(piv):
  if sol[n,0]:k,e=labels[c];mult[k]+=C.from_dict({e:sol[n,0]})
 assert sum((g*z for g,z in zip(gg,mult)),C.constant(0))==target,'Selected modular solution did not lift to all rational equations'
 out={'status':'PASS exact rational Bezout certificate','identity':'A*h+B*h_i+C*h_w=i^4*(1+w^3)','h':str(h),'multipliers':[str(z) for z in mult],'degree_bound':bound,'matrix_shape':[rows,cols+1],'selected_minor_size':rank,'selected_rows':rowids,'selected_columns':piv,'prime_for_pivot_selection_only':p,'verified_over':'Q[i,w]','term_counts':[len(z.to_dict()) for z in mult],'normal_field_on_h_zero':'(B/(i^4*T))*partial_i+(C/(i^4*T))*partial_w has derivative h=1','scope':'Actual physical double-node curve at j=+/-1; not a global eight-row source solution','seconds':time.time()-st};(r/'two-node-physical-normal-bezout-i4T.json').write_text(json.dumps(out,indent=2)+'\n');print('SAVED EXACT CERTIFICATE',out['term_counts'],flush=True);break
else:print('No certificate in tested degree range; no nonexistence conclusion.',flush=True)
