"""Exact original-affine divergence versus compact residual at a sextic point.
Arithmetic: Q[alpha]/(6 alpha^6+5 alpha+33), with five forward derivatives.
This is a specialization check of the generic transport, not a replacement
for its polynomial proof or a certificate claim.
"""
from audit_core import *
from flint import fmpq_poly
import os
deck=int(os.environ.get('DECK_SIGN','1'));assert deck in [-1,1]
st=time.time();MOD=fmpq_poly([fmpq(11,2),fmpq(5,6),0,0,0,0,1])
factors=MOD.factor()[1]
assert len(factors)==1 and factors[0][1]==1 and factors[0][0].degree()==6
class K:
 inverse_count=0
 def __init__(self,z=0):
  if isinstance(z,K):self.p=z.p;return
  self.p=(z if isinstance(z,fmpq_poly) else fmpq_poly([fmpq(z)]))%MOD
 def __add__(a,b):return K(a.p+K(b).p)
 __radd__=__add__
 def __neg__(a):return K(-a.p)
 def __sub__(a,b):return a+-K(b)
 def __rsub__(a,b):return K(b)+-a
 def __mul__(a,b):return K(a.p*K(b).p)
 __rmul__=__mul__
 def inv(a):
  K.inverse_count+=1
  g,s,t=a.p.xgcd(MOD);assert g==fmpq_poly([1]);return K(s)
 def __truediv__(a,b):return a*K(b).inv()
 def __rtruediv__(a,b):return K(b)*a.inv()
 def __pow__(a,n):
  if n<0:return a.inv()**(-n)
  out=K(1);base=a
  while n:
   if n&1:out=out*base
   n//=2
   if n:base=base*base
  return out
 def __eq__(a,b):return a.p==K(b).p
 def __bool__(a):return bool(a.p)
 def data(a):return [str(z) for z in a.p.coeffs()]
class Jet:
 def __init__(self,z=0,ds=None):
  if isinstance(z,Jet):self.val,self.ds=z.val,z.ds;return
  self.val=K(z);self.ds=[K(0) for _ in range(5)] if ds is None else [K(x) for x in ds]
 def __add__(a,b):
  b=Jet(b);return Jet(a.val+b.val,[a.ds[n]+b.ds[n] for n in range(5)])
 __radd__=__add__
 def __neg__(a):return Jet(-a.val,[-d for d in a.ds])
 def __sub__(a,b):return a+-Jet(b)
 def __rsub__(a,b):return Jet(b)+-a
 def __mul__(a,b):
  b=Jet(b);return Jet(a.val*b.val,[a.ds[n]*b.val+a.val*b.ds[n] for n in range(5)])
 __rmul__=__mul__
 def inv(a):
  vv=a.val.inv();return Jet(vv,[-d*vv*vv for d in a.ds])
 def __truediv__(a,b):return a*Jet(b).inv()
 def __rtruediv__(a,b):return Jet(b)*a.inv()
 def __pow__(a,n):
  if n==0:return Jet(1)
  val=a.val**n;der=n*(a.val**(n-1));return Jet(val,[d*der for d in a.ds])
 def __eq__(a,b):b=Jet(b);return a.val==b.val and a.ds==b.ds
alpha=K(fmpq_poly([0,1]))
def variable(value,idx):
 ds=[0]*5;ds[idx]=1;return Jet(value,ds)
def evaluate(poly,values):
 pp=P(poly);deg=pp.degrees();powers=[]
 for n,value in enumerate(values):
  powers.append([Jet(1)])
  for k in range(max(0,int(deg[n]))):powers[-1].append(powers[-1][-1]*value)
 out=Jet(0)
 for exp,c in pp.to_dict().items():
  term=Jet(c)
  for n,e in enumerate(exp):
   if e:term=term*powers[n][int(e)]
  out=out+term
 return out
def evalfrac(z,values):return evaluate(z['n'],values)/evaluate(z['d'],values)
cur=read('taylor-discriminant-current.json');wc=read('w-correction.json')
def current(values,method):
 ii,jj,ww,vvalue=values;tt=1+ww**3;nn=9*ii*ii*ww*ww-16*jj*jj*tt;ll=256*tt**5*nn+729*ii**6*jj*jj*ww**6
 if method=='B':
  kk=ii**8*ll**6*evaluate(cur['W'],values)/evaluate(cur['Delta'],values)**2
 else:
  dc=coeffs(D,'v');d0=evaluate(dc[0],values);d1=evaluate(dc[1],values);d2=evaluate(dc[2],values)
  kk=(d0*d0+2*d0*d1*vvalue+(d1*d1+2*d0*d2)*vvalue*vvalue)/evaluate(D,values)**2
 co=-ii*tt/(4*ww*jj)+28*tt**2*jj/(45*ii*ww**3)-224*jj*(2-ww**3)/(405*ii*ww**3);do=-448*tt/(405*ii*ww**2)
 vzj=jj*(2-ww**3)/(2*ii*ww**3);vzw=tt/(ii*ww**2);zz=[evalfrac(z,values) for z in wc['Z']]
 return {'j':[kk*(vzj*z+(co if r==7 else 0)) for r,z in enumerate(zz)],'w':[kk*(vzw*z+(do if r==7 else 0)) for r,z in enumerate(zz)]}
def progress(s):print(s,'seconds',round(time.time()-st,3),flush=True)
X,U,Y,Z,PP=[variable(z,k) for k,z in enumerate([1,1,1,1,alpha])]
F0=1+X**6+U**6+Y**6+Z**6+PP**6+X*Y*Z/2+X**3*U*Z*PP/2+X*U*Y*PP/3
assert not F0.val
q=X*Y;RR=(U/X)**6;k=U*PP/q;ww=Z**2;tt=1+ww**3;ii=4*k*tt/(3*ww);j2=k*k*tt/(1+RR)
jj=Jet(deck*alpha,[d/(2*deck*alpha) for d in j2.ds]);assert jj*jj==j2
xx=Z*q/(2*tt);aa=k*X**3/jj;yy=Z**3*Y**3*jj/(8*k*tt**3)
NN=9*ii*ii*ww*ww-16*jj*jj*tt;LL=256*tt**5*NN+729*ii**6*jj*jj*ww**6
vv=64*jj*jj*ww*tt**2*NN/(9*ii*ii*LL)
assert vv==Z**6/(64*tt**4*(1+RR)*(1+(PP/Y)**6))
values=[ii,jj,ww,vv];pc=current(values,'B');progress('Original coordinate current evaluated')
rho=3*ii*ii*ww*ww*xx/(2*NN*Z*jj)
basis=[Jet(1),xx,xx**3,xx**4-vv*(ii-jj*jj/4)*(ii-5*jj*jj/4)*xx*xx/8,aa,aa*xx+jj*xx*xx/2,yy,yy*xx]
uj=sum((basis[r]*pc['j'][r] for r in range(8)),Jet(0))/rho;uw=sum((basis[r]*pc['w'][r] for r in range(8)),Jet(0))/rho
vj=evaluate(vp.diff('j').n,values)/evaluate(vp.diff('j').d,values);vw=evaluate(vp.diff('w').n,values)/evaluate(vp.diff('w').d,values)
bj=vj/(6*vv);bw=vw/(6*vv);DD=evaluate(D,values)
words=[Jet(1),xx,xx**2,xx**3,xx**4,xx**5,aa,aa*xx,aa*xx**2,aa*xx**3,yy,yy*xx,yy*xx**2,yy*xx**3,yy**2*xx,yy**2*xx**2]
Hfib=Jet(0)
for t,word in enumerate(words):
 entry=Jet(0)
 for r in range(8):entry+=evaluate(ij['primitive_numerators']['j'][t][r],values)*pc['j'][r]+evaluate(vr['primitive_numerators'][t][r],values)*(bj*pc['j'][r]+bw*pc['w'][r])
 Hfib+=word*entry/DD
progress('All sixteen literal fiber coefficients evaluated')
src=read('packet/coupled-fresh/ruling-source/full-base-connection/source-euler-current-results.json')
FD=sum((word*evaluate(z,values) for word,z in zip(words,src['fiber_primitive_D_numerators'])),Jet(0))/evaluate(src['remaining_common_denominator'],values)
APh=9*ii**3*ww*tt/(jj*jj*NN);ux=-(Hfib+APh*FD+APh*vv*xx*yy)/(rho*vv)
Jb=vv*(2*aa*aa+jj*aa*xx)-2*yy*yy;dvv=vj*uj+vw*uw
loga=(-vv*(2*ii*xx+jj*aa+1)-6*yy*xx*xx/aa)*ux/Jb-vv*aa*xx*uj/Jb+yy*yy*dvv/(vv*Jb)
logZ=uw/(2*ww);logT=3*ww*ww*uw/tt;logk=uw/ww-logT;logq=ux/xx-logZ+logT
logX=(loga+uj/jj-logk)/3;logY=logq-logX;logR=2*(RR+1)/RR*(logk+logT/2-uj/jj);logU=logX+logR/6;logP=logk+logq-logU
W=[X*logX,U*logU,Y*logY,Z*logZ,PP*logP]
J=2*(X**6+U**6-Y**6-PP**6)+X**3*U*Z*PP/2
normal=[X/(3*J),U/(3*J),-Y/(3*J),Jet(0),-PP/(3*J)]
V=[(Y**3+F0*logT)*normal[r]-W[r] for r in range(5)]
normal_check=sum((F0.ds[r]*V[r].val for r in range(5)),K(0));assert normal_check==Y.val**3
original_div=sum((V[r].ds[r] for r in range(5)),K(0))
progress('Actual five-component field and its original-coordinate divergence evaluated')
# Separately differentiate the alternate cutoff expression in physical base
# coordinates; compare it to the original-coordinate divergence above.
bi=variable(K(fmpq(8,3))*alpha,0);bjv=variable(deck*alpha,1);bwvar=variable(1,2);bT=1+bwvar**3;bN=9*bi*bi*bwvar*bwvar-16*bjv*bjv*bT;bL=256*bT**5*bN+729*bi**6*bjv*bjv*bwvar**6
bv=64*bjv*bjv*bwvar*bT*bT*bN/(9*bi*bi*bL);bvals=[bi,bjv,bwvar,bv];pbase=current(bvals,'cutoff')
Dval=evaluate(D,bvals).val;beta_j=bv.ds[1]/(6*bv.val);beta_w=bv.ds[2]/(6*bv.val);Aval=(9*bi**3*bwvar*bT/(bjv*bjv*bN)).val
res=[]
for r in range(8):
 sv=Aval*((4 if r==6 else 0)-(evaluate(G['V'][r][6],bvals).val-2*bi.val*evaluate(G['i'][r][6],bvals).val-bjv.val*evaluate(G['j'][r][6],bvals).val)/Dval)
 rr=sv-pbase['j'][r].ds[1]-pbase['w'][r].ds[2]
 for c in range(8):
  gv=evaluate(G['V'][r][c],bvals).val/Dval;gj=evaluate(G['j'][r][c],bvals).val/Dval
  rr-=(gj+beta_j*gv)*pbase['j'][c].val+beta_w*gv*pbase['w'][c].val
 res.append(rr)
compact_div=sum((basis[r].val*res[r] for r in range(8)),K(0))/rho.val
assert original_div==compact_div,'Original divergence does not match literal compact transport'
assert original_div,'This check unexpectedly found zero residual; investigate separately'
write('taylor-algebraic-original-field-audit.json' if deck==1 else 'taylor-negative-deck-field-audit.json',{'status':'PASS','field':'Q[alpha]/(6*alpha^6+5*alpha+33), irreducible over Q by exact factorization','original_point':['1','1','1','1','alpha'],'physical_point':['8*alpha/3','alpha' if deck==1 else '-alpha','1'],'checks':{'original_F_zero':True,'j_square_dual_binding':True,'physical_v_full_dual_binding':True,'normal_derivative_dF_V_equals_Y3':True,'all_16_literal_fiber_coefficients_used':True,'actual_original_divergence_equals_compact_residual_over_density':True,'remaining_original_divergence_nonzero':True},'deck_sign':deck,'nonzero_inverse_inputs_checked':K.inverse_count,'field_component_values':[z.val.data() for z in V],'original_divergence_coefficients_mod_minpoly':original_div.data(),'compact_residual_rows_mod_minpoly':[z.data() for z in res],'seconds':time.time()-st})
progress('PASS exact algebraic-point original field/divergence audit; residual nonzero')
