import os
os.environ['SYMPY_GROUND_TYPES']='python'
import sympy as s,json,pathlib,time
r=pathlib.Path(__file__).resolve().parents[1];st=time.time();x,a,I,J,V=s.symbols('x a i j v');ip=(2*a*a-5*x-8)/(2*x*x);jp=(x+2-2*a*a)/(a*x);vp=2*x**6/(a*a*(x+2));C=5*x*x+6*x*a*a+26*x+16*a*a+32
Q=8*(I*x*x+2*x+3)**2-J*J*x*x*(2*I*x*x+5*x+8);qx=s.factor(s.diff(Q,x).subs({I:ip,J:jp}));det=s.factor(s.diff(ip,x)*s.diff(jp,a)-s.diff(ip,a)*s.diff(jp,x));minors=[]
for p,q in [(ip,jp),(ip,vp),(jp,vp)]:minors.append(s.factor(s.diff(p,x)*s.diff(q,a)-s.diff(p,a)*s.diff(q,x)))
print('Q_x on cover',qx,'Jacobian i,j',det,flush=True);print('All map minors',minors,flush=True)
expected=[-C/(2*a*a*x**4),-2*x**3*C/(a**3*(x+2)**2),2*x**4*C/(a**4*(x+2)**2)]
for z,e in zip(minors,expected):assert s.cancel(z-e)==0
# The first minor is a unit times C on x*a !=0; record exact quotient.
quot=s.factor(det/C);assert s.Poly(s.fraction(quot)[0],x,a).is_ground
norm=json.loads((r/'critical-normalized-residue.json').read_text());facs=[]
for row in norm['denominator_factors']:
 for z in row:
  f=s.sympify(z['polynomial'].replace('^','**'));assert s.cancel(f-x)==0 or s.cancel(f-a)==0 or s.cancel(f-C)==0
out={'status':'PASS exact critical-cover ramification and normalized residue support','cusp_polynomial':str(C),'Q_x_on_cover':str(qx),'parametrization_jacobian_i_j':str(det),'all_three_parametrization_minors':[str(z) for z in minors],'normalized_residue_denominator_support':['x','a','cusp_polynomial'],'geometric_scope':'On x*a*(x+2)!=0, the parametrization differential loses rank exactly on C=0. No global singularity classification or cusp normal-form assertion at exceptional intersections is made.','seconds':time.time()-st};(r/'critical-cover-ramification-audit.json').write_text(json.dumps(out,indent=2)+'\n')
