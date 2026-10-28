"""Exact source normalization and density transport from the five-variable affine sextic."""
import sympy as s,json,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];st=time.time();x,u,y,z,p=s.symbols('x u y z p',nonzero=True);variables=(x,u,y,z,p)
F=1+x**6+u**6+y**6+z**6+p**6+x*y*z/2+x**3*u*z*p/2+x*u*y*p/3
b=y**3;q=x*y;r=u**3/x**3;k=u*p/(x*y);T=1+z**6;R=r*r;S=p**6/y**6
J=2*(x**6+u**6-y**6-p**6)+x**3*u*z*p/2
G=[x,u,-y,0,-p];normal=[g/(3*J) for g in G];checks={}
def check(name,val):
 assert s.cancel(val)==0,name
 checks[name]=True
check('normal derivative of F equals 1',sum(normal[n]*s.diff(F,var) for n,var in enumerate(variables))-1)
quotient=(1+R)*x**6+(1+S)*y**6+k*q*q/3+z*k*x**3*q/2+z*q/2+T
check('exact target equals quotient curve',F-quotient)
jac=s.Matrix([[s.diff(f,var) for var in variables] for f in [F,q,r,k,z]]).det(method='domain-ge')
check('original Poincare residue density',jac*q/(9*r*J)-1)
div=sum(s.diff(b*normal[n],var) for n,var in enumerate(variables))
claimed=-b*(6*(x**6+u**6)+2*(y**6+p**6)+x**3*u*z*p)/J**2
check('original source divergence',div-claimed)
# The second coordinate Jacobian uses only rational log derivatives and dz=dw/(2z).
ii,jj,ww,xx=s.symbols('i j w X',nonzero=True);tt=1+ww**3;kk=3*ii*ww/(4*tt);rr=kk*kk*tt/(jj*jj)-1
basejac=s.det(s.Matrix([[s.diff(rr,ii),s.diff(rr,jj),s.diff(rr,ww)],[s.diff(kk,ii),s.diff(kk,jj),s.diff(kk,ww)],[0,0,1/(2*z)]]))
check('base coordinate Jacobian',basejac-3*kk*kk*ww/(4*z*jj**3))
# muF/nu0 = x*T/(18*R*E²)*basejac; E²=w/4, then use z²=w.
NN=9*ii**2*ww**2-16*jj**2*tt
rho=s.cancel(xx*tt/(18*rr*(ww/4))*basejac)
check('physical density ratio',rho-3*ii**2*ww**2*xx/(2*NN*z*jj))
result={'status':'PASS','checks':checks,'rho':'3*i^2*w^2*xdesc/(2*N*z*j), z^2=w','muF':'rho*nu_0 wedge di wedge dj wedge dw','original_normal':'(x*d_x+u*d_u-y*d_y-p*d_p)/(3*J), J=2(x^6+u^6-y^6-p^6)+x^3*u*z*p/2','source':'div(y^3*normal)*muF','seconds':time.time()-st}
(ROOT/'original-chart-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
