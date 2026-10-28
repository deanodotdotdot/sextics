from exact import *
from flint import nmod_mat
import time,hashlib
st=time.time();path=HERE/'corrected-relative-i-screen-1-1-90.json';rec=json.loads(path.read_text());p=rec['prime'];bound=rec['numerator_degree_bound'];rows,cols=rec['matrix_shape'];height=rows//8;dc=poly(rec['operator_denominator'])
def co(txt):
 out={}
 for e,c in poly(txt).to_dict().items():out[int(e[0])]=int(c.numerator)%p*pow(int(c.denominator)%p,-1,p)%p
 return out
d=co(str(dc));a=[[co(z) for z in row] for row in rec['operator_numerators']];b=[co(z) for z in rec['target_numerators']];mat=[]
for r in range(8):
 for e in range(height):
  row=[]
  for k in range(8):
   for n in range(bound+1):row.append((a[r][k].get(e-n,0)+(n*d.get(e-n+1,0) if r==k else 0))%p)
  row.append(b[r].get(e,0));mat.append(row)
M=nmod_mat(mat,p);rt,rank=M.transpose().rref();assert rank==cols
selected=[next(c for c in range(rows) if int(rt[r,c])) for r in range(cols)]
minor=nmod_mat([mat[r] for r in selected],p);det=int(minor.det());assert det
out={'status':'nonzero augmented full-column minor','prime':p,'unknown_count':cols-1,'augmented_minor_size':cols,'selected_rows':selected,'determinant_mod_prime':det,'operator_input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'proof':'The augmented matrix has a nonzero (unknown_count+1)-minor. Its characteristic-zero rank exceeds the possible rank of the coefficient matrix. No member of the specified finite ansatz can solve.','seconds':time.time()-st}
export(HERE/'corrected-relative-i-rank-witness.json',out);print('minor',cols,'determinant',det,'seconds',time.time()-st,flush=True)
