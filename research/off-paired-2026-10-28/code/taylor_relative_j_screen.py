from exact import *
from jets import pcoeff
from flint import fmpq_poly,nmod_mat
import time,sys
st=time.time();IVAL=int(sys.argv[1]) if len(sys.argv)>1 else 1;WVAL=int(sys.argv[2]) if len(sys.argv)>2 else 1;BOUND=int(sys.argv[3]) if len(sys.argv)>3 else 61;prime=1009
sp={'i':IVAL,'w':WVAL};D,G,ij,vr=matrices();vps=vp.evaluate(sp);A1,B1=vps.n,vps.d
ap=[A1**k for k in range(6)];bp=[B1**k for k in range(6)]
def pull(p):
 p=p.subs(sp);co=pcoeff(p,'v');deg=max(co,default=0)
 return R(sum((z*ap[k]*bp[deg-k] for k,z in co.items()),ZERO),bp[deg])
Dp=pull(D);Gam={var:[[pull(z)/Dp for z in row] for row in G[var]] for var in G}
ci=(vp.diff('i')/vp/6).evaluate(sp);cj=(vp.diff('j')/vp/6).evaluate(sp);cw=(vp.diff('w')/vp/6).evaluate(sp)
Gi=[[Gam['i'][r][k]+ci*Gam['V'][r][k] for k in range(8)] for r in range(8)];Gj=[[Gam['j'][r][k]+cj*Gam['V'][r][k] for k in range(8)] for r in range(8)];Gw=[[cw*Gam['V'][r][k] for k in range(8)] for r in range(8)]
dat=json.loads((HERE/'after-w-physical.json').read_text());oldtarget=[R(poly(row['n']).subs(sp),poly(row['d']).subs(sp)) for row in dat['rows']]
cur=json.loads((HERE/'taylor-discriminant-current.json').read_text());Delta=poly(cur['Delta']);Knum=i**8*L**6*poly(cur['W']);ds=Delta.subs(sp);kns=Knum.subs(sp);cut=R(kns,ds**2)
cutj=R(Knum.derivative('j').subs(sp)*ds-2*kns*Delta.derivative('j').subs(sp),ds**3);cutw=R(Knum.derivative('w').subs(sp)*ds-2*kns*Delta.derivative('w').subs(sp),ds**3)
wc=json.loads((HERE/'w-correction.json').read_text());zs=[R(poly(z['n']).subs(sp),poly(z['d']).subs(sp)) for z in wc['Z']]
oldj=[Vj.evaluate(sp)*z+(c.evaluate(sp) if r==7 else 0) for r,z in enumerate(zs)];oldw=[Vw.evaluate(sp)*z+(d.evaluate(sp) if r==7 else 0) for r,z in enumerate(zs)]
actual=[A.evaluate(sp)*((4 if r==6 else 0)-Gam['V'][r][6]+2*IVAL*Gam['i'][r][6]+j*Gam['j'][r][6]) for r in range(8)]
target=[cut*oldtarget[r]+(1-cut)*actual[r]-cutj*oldj[r]-cutw*oldw[r] for r in range(8)]
print('univariate target ready',time.time()-st,flush=True)
H=poly((L*Delta**2).subs(sp));HP=R(H.derivative('j'),H)
A=[[Gj[r][k]-(HP if r==k else 0) for k in range(8)] for r in range(8)];B=[R(H)*z for z in target]
den=ONE
for z in [z for row in A for z in row]+B:den=den*z.d//den.gcd(z.d)
print('clearing denominator degree',den.degrees()[1], 'H degree',H.degrees()[1],flush=True)
AA=[[z.n*(den//z.d) for z in row] for row in A];BB=[z.n*(den//z.d) for z in B]
maxdeg=max(max(z.degrees()[1] for row in AA for z in row)+BOUND,max(z.degrees()[1] for z in BB),den.degrees()[1]+BOUND-1);height=int(maxdeg+1);width=8*(BOUND+1)
def coeffmod(p):
 out={}
 for exp,z in p.to_dict().items():
  assert not exp[0] and not exp[2] and not exp[3];out[int(exp[1])]=(int(z.numerator)%prime)*pow(int(z.denominator)%prime,-1,prime)%prime
 return out
mat=[[0]*(width+1) for _ in range(8*height)];dc=coeffmod(den)
for r in range(8):
 for degree,z in coeffmod(BB[r]).items():mat[r*height+degree][-1]=z
 for k in range(8):
  co=coeffmod(AA[r][k])
  for n in range(BOUND+1):
   col=k*(BOUND+1)+n
   for degree,z in co.items():mat[r*height+degree+n][col]=(mat[r*height+degree+n][col]+z)%prime
   if r==k and n:
    for degree,z in dc.items():mat[r*height+degree+n-1][col]=(mat[r*height+degree+n-1][col]+n*z)%prime
print('matrix',len(mat),width+1,'seconds',time.time()-st,flush=True)
mr=nmod_mat(mat,prime);rref,rank=mr.rref();mrank=nmod_mat([row[:-1] for row in mat],prime).rank()
print('ranks',mrank,rank,'unknowns',width,'seconds',time.time()-st,flush=True)
res={'i':IVAL,'w':WVAL,'variable':'j','prime':prime,'numerator_degree_bound':BOUND,'denominator':'L Delta^2','matrix_shape':[len(mat),width+1],'column_rank':mrank,'augmented_rank':rank,'full_column_rank':mrank==width,'scope':'Specified relative-j correction ansatz after fixed Taylor-cutoff j,w currents; no unrestricted certificate exclusion','seconds':time.time()-st,'operator_denominator':str(den),'operator_numerators':[[str(z) for z in row] for row in AA],'target_numerators':[str(z) for z in BB],'current_denominator':str(H)}
export(HERE/f'taylor-relative-j-screen-{IVAL}-{WVAL}-{BOUND}.json',res)
