import os
os.environ['SYMPY_GROUND_TYPES']='python'
import sympy as s,json,pathlib,time,hashlib
from fractions import Fraction
r=pathlib.Path(__file__).resolve().parents[1];st=time.time();checks={}
def check(n,z):assert s.cancel(z)==0,n;checks[n]=True
x,i,j,w,a,v,u=s.symbols('x i j w a v u',nonzero=True)
T=1+w**3;N=9*i*i*w*w-16*j*j*T;L=256*T**5*N+729*i**6*j*j*w**6;AV=64*j*j*w*T*T*N;BV=9*i*i*L;vp=AV/BV
K=i*x*x+2*x+3;A2=i*x*x+s.Rational(5,2)*x+4;Q=8*K*K-j*j*x*x*(2*i*x*x+5*x+8);ac=-2*K/(j*x);tt=(x+2)/2
check('quartic gives a_squared',ac**2-A2-Q/(2*j*j*x*x))
check('curve at critical values',A2+i*x*x+j*ac*x+x+1+tt)
check('fiber a derivative times a',2*A2+j*ac*x-2*tt)
check('fiber x derivative times x',2*i*x*x+j*ac*x+x+6*tt)
inputs=json.loads((r/'critical-coupled-normal-inputs.json').read_text());dd={k:s.sympify(z.replace('^','**'),locals={'i':i,'u':j*j,'w':w,'x':x}) for k,z in inputs.items()}
check('i normal generator',dd['mi']/(2*N*L)-(i*x*x-i*s.diff(vp,i)/vp*tt))
check('j normal generator',dd['mj']/(2*N*L)-(j*ac*x-j*s.diff(vp,j)/vp*tt))
check('w normal generator',dd['mw']/(2*N*L*T)+w*s.diff(vp,w)/vp*tt)
rr,c=s.symbols('R c');krow=s.Matrix([[-1,1,-1,0,1]]);rrow=s.Matrix([[-6,6,0,0,0]]);wrow=s.Matrix([[0,0,0,2,0]]);Xrow=s.Matrix([[1,0,0,0,0]]);Yrow=s.Matrix([[0,0,1,0,0]])
mat=s.Matrix.vstack(krow+(c-1)*wrow,krow+c*wrow/2-rr*rrow/(2*(1+rr)),wrow,Xrow+Yrow+(s.Rational(1,2)-c)*wrow,3*Xrow-c*wrow/2+rr*rrow/(2*(1+rr)))
det=s.factor(mat.det());assert det!=0;print('Logarithmic Jacobian determinant',det,flush=True)
check('chart Jacobian',det+18*rr/(1+rr))
# Recheck the original hypersurface identity without imposing F=0.
X,U,Y,Z,P=s.symbols('X U Y Z P',nonzero=True);k0=U*P/(X*Y);R0=(U/X)**6;S0=(P/Y)**6;T0=1+Z**6;j20=k0*k0*T0/(1+R0);v0=Z**6/(64*T0**4*(1+R0)*(1+S0));x0=Z*X*Y/(2*T0);i0=4*k0*T0/(3*Z**2)
curve=Z**6*Y**6*j20/(64*k0*k0*T0**6*v0)+k0*k0*X**6/j20+i0*x0*x0+k0*X**3*x0+x0+1
f=1+X**6+U**6+Y**6+Z**6+P**6+X*Y*Z/2+X**3*U*Z*P/2+X*U*Y*P/3
check('original hypersurface before imposing F',curve-f/T0)
# Exact smoothness bound, independently reconstructed.
xs=s.symbols('X0 X1 X2 Y0 Y1 Y2');X0,X1,X2,Y0,Y1,Y2=xs;pert=X0**3*X1*Y0*Y1/2+X1**3*X2*Y1*Y2/2+X0**2*X1*X2*Y0*Y2/3
bounds=[]
for z in xs:
 bound=sum(abs(q) for q in s.Poly(s.diff(pert,z),*xs).coeffs());assert bound<6;bounds.append(str(bound))
(r/'coupled-unit-geometry-audit.json').write_text(json.dumps({'status':'PASS exact inputs to characteristic-zero geometric unit-ideal proof','checks':checks,'gradient_L1_bounds':bounds,'chart_log_jacobian':str(det),'localization':'B=i*u*w*T*N*L, u=j^2','ideal':'(Q,Vrel,mi,mj,mw) with Vrel=AV*(2i*x^2+5x+8)*(x+2)-4*BV*x^6','conclusion':'The ideal becomes the unit ideal after inverting B over Q; proof in COUPLED-NORMAL-IDEAL.txt. This is a geometric proof, not an exported rational Bezout multiplier certificate.','scope':'Critical-normal scalar algebra only; no resulting full eight-row current or closure claimed','seconds':time.time()-st},indent=2)+'\n');print('PASS',len(checks),'identities and six gradient bounds',time.time()-st,flush=True)
