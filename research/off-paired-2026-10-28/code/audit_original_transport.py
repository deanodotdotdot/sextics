"""Exact universal transport of arbitrary compact currents to original fields.
Checks differential formulas and deck parity; does not claim residual zero.
"""
import sympy as sy
from audit_core import *
st=time.time();checks={}
def check(k,expr):assert sy.cancel(expr)==0,k;checks[k]=True
# All velocities below are formal; checking them proves the chain formulas
# for our explicit rational coefficient current without huge substitution.
x,a,y,iv,jv,wv,vv,zv=sy.symbols('x a y i j w v z',nonzero=True)
ui,uj,uw,ux,dv=sy.symbols('ui uj uw ux dv')
TT=1+wv**3;JJ=vv*(2*a*a+jv*a*x)-2*y*y;BB=2*iv*x+jv*a+1
loga=(-vv*BB-6*y*x*x/a)*ux/JJ-vv*x*x*ui/JJ-vv*a*x*uj/JJ+y*y*dv/(vv*JJ)
da=a*loga;dy=y*(3*ux/x-loga)
# ay=x^3 is used only for this first tangent identity.
check('first curve relation tangent on ay=x^3',(da*y+a*dy-3*x*x*ux).subs(y,x**3/a))
curve=y*y+vv*(a*a+iv*x*x+jv*a*x+x+1)
dcurve=sy.diff(curve,a)*da+sy.diff(curve,y)*dy+sy.diff(curve,x)*ux+sy.diff(curve,iv)*ui+sy.diff(curve,jv)*uj+sy.diff(curve,vv)*dv
check('second curve relation logarithmic tangent',(dcurve-curve*dv/vv).subs(y,x**3/a))
logz=uw/(2*wv);logT=3*wv*wv*uw/TT
logk=ui/iv+uw/wv-logT
logq=ux/x-logz+logT
logX=(loga+uj/jv-logk)/3
logY=logq-logX
RR=sy.symbols('R',nonzero=True)
logR=2*(RR+1)/RR*(logk+logT/2-uj/jv)
logU=logX+logR/6
logP=logk+logq-logU
check('q=XY logarithmic derivative',logX+logY-logq)
check('k=UP/(XY) logarithmic derivative',logU+logP-logX-logY-logk)
check('R=(U/X)^6 logarithmic derivative',6*(logU-logX)-logR)
check('i=4kT/(3w) logarithmic derivative',logk+logT-uw/wv-ui/iv)
check('j^2=k^2*T/(1+R) logarithmic derivative',2*logk+logT-RR/(1+RR)*logR-2*uj/jv)
check('xdesc=z*XY/(2T) logarithmic derivative',logz+logq-logT-ux/x)
check('adesc=k*X^3/j logarithmic derivative',logk+3*logX-uj/jv-loga)
check('ydesc=z^3*Y^3*j/(8*k*T^3) logarithmic derivative',3*logz+3*logY+uj/jv-logk-3*logT-(3*ux/x-loga))
# Bind the physical v expression as a rational identity in base variables.
kk=3*iv*wv/(4*TT);Rphys=kk*kk*TT/(jv*jv)-1;Sphys=kk**6/Rphys
vold=wv**3/(64*TT**4*(1+Rphys)*(1+Sphys))
NN=9*iv*iv*wv*wv-16*jv*jv*TT;LL=256*TT**5*NN+729*iv**6*jv*jv*wv**6
vphysical=64*jv*jv*wv*TT*TT*NN/(9*iv*iv*LL)
check('physical v equals original quotient expression',vold-vphysical)
# Direct original hypersurface binding, valid before imposing F=0.
XX,UU,YY,ZZ,PP=sy.symbols('X U Y Z P',nonzero=True)
q0=XX*YY;k0=UU*PP/q0;R0=(UU/XX)**6;S0=(PP/YY)**6;T0=1+ZZ**6
J20=k0*k0*T0/(1+R0);v0=ZZ**6/(64*T0**4*(1+R0)*(1+S0));x0=ZZ*q0/(2*T0);i0=4*k0*T0/(3*ZZ**2)
curve_over_v=ZZ**6*YY**6*J20/(64*k0*k0*T0**6*v0)+k0*k0*XX**6/J20+i0*x0*x0+k0*XX**3*x0+x0+1
F0=1+XX**6+UU**6+YY**6+ZZ**6+PP**6+XX*YY*ZZ/2+XX**3*UU*ZZ*PP/2+XX*UU*YY*PP/3
check('curve divided by v equals original F divided by T',curve_over_v-F0/T0)
# Deck parity checks on the actual current and every literal primitive.
cur=read('simple-discriminant-current.json');eps=[0,0,0,0,1,1,1,1]
def parity(poly,expected):return all(int(e[1])%2==expected for e in poly.to_dict())
for name in ['Hi','HL','Delta']:assert parity(P(cur[name]),0);checks[name+' even in j']=True
for t in ['j','w']:
 for r,b in enumerate(cur['B'][t]):
  for key in ['n','d']:
   expected=(eps[r] if t=='j' else 1-eps[r]) if key=='n' else 0
   # A rational representation may have an odd j denominator. Test numerator
   # and denominator parities together rather than impose a representation.
  pn=P(b['n']);pd=P(b['d']);pnset={int(e[1])%2 for e in pn.to_dict()};pdset={int(e[1])%2 for e in pd.to_dict()}
  assert len(pnset)<=1 and len(pdset)==1
  assert not pnset or (next(iter(pnset))+next(iter(pdset)))%2==(eps[r] if t=='j' else 1-eps[r])
checks['all 16 actual current coefficients have descent parity']=True
words=ij['primitive_words'];wordeps=[int('a' in s)+int('y' in s and 'y^2' not in s and 'y**2' not in s) for s in words]
# Parse word powers independently in a simple symbolic polynomial.
aa,xx,yy=sy.symbols('a x y');wordeps=[]
for word in words:
 pp=sy.Poly(sy.sympify(word.replace('^','**')),aa,xx,yy);exps=pp.monoms();assert len(exps)==1;wordeps.append((exps[0][0]+exps[0][2])%2)
count=0
for direction,mat in [('i',ij['primitive_numerators']['i']),('j',ij['primitive_numerators']['j']),('V',vr['primitive_numerators'])]:
 for t,row in enumerate(mat):
  for r,z in enumerate(row):
   expected=(eps[r]+wordeps[t]+int(direction=='j'))%2
   assert parity(P(z),expected),(direction,t,r)
   count+=1
checks['384 native literal coefficients have correct deck parity']=True
src=read('packet/coupled-fresh/ruling-source/full-base-connection/source-euler-current-results.json')
assert src['fiber_primitive_words']==words
for t,z in enumerate(src['fiber_primitive_D_numerators']):assert parity(P(z),(1+wordeps[t])%2)
checks['source vertical primitive has odd deck parity']=True
write('original-transport-audit.json',{'status':'PASS','checks':checks,'native_primitive_entries':count,'meaning':'Universal exact chain formulas for the explicit current, including original physical v and rational descent under j -> -j. Combined with prior density/source binding, gives a concrete partial original-coordinate field. Residual is not asserted zero.','seconds':time.time()-st})
write('original-partial-field-expression.json',{
 'schema':'rational-original-field-v1','original_affine_variables':['X','U','Y','Z','P'],'F':'1+X^6+U^6+Y^6+Z^6+P^6+X*Y*Z/2+X^3*U*Z*P/2+X*U*Y*P/3','b':'Y^3',
 'chart':{'q':'X*Y','R':'(U/X)^6','k':'U*P/(X*Y)','w':'Z^2','T':'1+w^3','i':'4*k*T/(3*w)','j_squared':'k^2*T/(1+R)','x':'Z*q/(2*T)','a':'k*X^3/j','y':'Z^3*Y^3*j/(8*k*T^3)','v':'64*j^2*w*T^2*N/(9*i^2*L)'},
 'current':'simple-discriminant-current.json',
 'basis':['1','x','x^3','x^4-v*(i-j^2/4)*(i-5*j^2/4)*x^2/8','a','a*x+j*x^2/2','y','y*x'],
 'rho':'3*i^2*w^2*x/(2*N*Z*j)',
 'base_velocities':{'ui':'0','uj':'sum_r basis[r]*Pj[r]/rho','uw':'sum_r basis[r]*Pw[r]/rho'},
 'fiber_numerator':'Hfib=sum_word word*(fj_num_word dot Pj+fV_num_word dot (beta_j*Pj+beta_w*Pw))/Dnative; FDnum=sum_word source_D_num_word*word/Dsource. Dnative=rank8-ij-connections-results.json common_denominator; Dsource=source-euler-current-results.json remaining_common_denominator=(67108864/2187)*Dnative. Both Hfib and FDnum omit Jbar; FDnum=Jbar*fD_actual.',
 'ux':'-(Hfib+Aphysical*FDnum+Aphysical*v*x*y)/(rho*v)',
 'dv':'v_i*ui+v_j*uj+v_w*uw (physical derivatives)',
 'Jbar':'v*(2*a^2+j*a*x)-2*y^2',
 'loga':'(-v*(2*i*x+j*a+1)-6*y*x^2/a)*ux/Jbar-v*x^2*ui/Jbar-v*a*x*uj/Jbar+y^2*dv/(v*Jbar)',
 'logs':{'logZ':'uw/(2*w)','logT':'3*w^2*uw/T','logk':'ui/i+uw/w-logT','logq':'ux/x-logZ+logT','logX':'(loga+uj/j-logk)/3','logY':'logq-logX','logR':'2*(R+1)/R*(logk+logT/2-uj/j)','logU':'logX+logR/6','logP':'logk+logq-logU'},
 'W':'(X*logX,U*logU,Y*logY,Z*logZ,P*logP)',
 'normal':'n=(X,U,-Y,0,-P)/(3*J), J=2*(X^6+U^6-Y^6-P^6)+X^3*U*Z*P/2; n(F)=1',
 'sigma':'3*w^2*uw/T; the chain identities give W(F)=sigma*F',
 'tangent_field':'Wtilde=W-F*sigma*n',
 'partial_field':'V=(b+F*sigma)*n-W; therefore dF(V)=b exactly',
 'on_F_divergence':'div(V)|F = (sum_r basis[r]*R_compact[r])/rho, using the literal source and fiber binding',
 'homogeneous_six_field':'V0=0; V_l=X0*V_affine,l(X1/X0,X2/X0,Y0/X0,Y1/X0,Y2/X0), l=1..5',
 'deck_descent':'Every original field component is invariant under j -> -j. The formula is rational in original variables; j may be eliminated using j^2=k^2*T/(1+R).',
 'scope':'Explicit factorized partial rational field and transport identity. Not expanded into homogeneous polynomial N,D,Q; full cleared divisibility and denominator-admissibility obligations remain open.'})
print('PASS original transport',len(checks),'groups,',count,'literal parity entries, seconds',round(time.time()-st,3),flush=True)
