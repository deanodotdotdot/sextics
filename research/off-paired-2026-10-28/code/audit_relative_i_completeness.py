"""Independent local/infinity completeness bounds for fixed-tangent families.
Reconstructs every spectral input from native polynomial matrices. Does not
use the old bounds JSON or stored source/connection jets.
"""
from audit_core import *
import sympy as sy
st=time.time();checks={}
def ck(k,c):assert c,k;checks[k]=True
def smat(mat):return sy.Matrix([[sy.sympify(str(z.n).replace('^','**'))/sy.sympify(str(z.d).replace('^','**')) for z in row] for row in mat])
x=sy.symbols('x');N0=N.subs({'i':0});K0=(L*L*Delta).subs({'i':0})
co=(-2*N+18*i*i*w*w)*L-i*N*L.derivative('i')
M0=[]
for r in range(8):
 row=[]
 for k in range(8):
  raw=hom(6*L*i*N*G['i'][r][k]+co*G['V'][r][k],5,7)
  num=exactdiv(raw,54*KD*i**(4+h[r]-h[k]))
  row.append(F(num.subs({'i':0}),K0*N0)+(h[r] if r==k else 0))
 M0.append(row)
char0=sy.factor(smat(M0).charpoly(x).as_expr());expected0=x**4*(5*x-2)*(5*x+1)*(5*x+2)*(5*x+4)/625
ck('i0 residue characteristic polynomial',sy.cancel(char0-expected0)==0)
print('PASS independent i=0 residue',char0,'seconds',round(time.time()-st,3),flush=True)
# Discriminant residue: native normal identities plus nilpotent GammaV.
Di=D.derivative('i');Dj=D.derivative('j');Dv=D.derivative('v')
for r in range(8):
 for k in range(8):
  for p,Dp in [('i',Di),('j',Dj)]:exactdiv(6*v*Dv*G[p][r][k]-Dp*G['V'][r][k],D)
  exactdiv(sum((G['V'][r][l]*G['V'][l][k] for l in range(8)),zero),D)
ck('128 native normal identities and 64 nilpotence identities',True)
ck('D squarefree in v',D.gcd(Dv).total_degree()==0)
ck('Delta squarefree in i',Delta.gcd(Delta.derivative('i')).total_degree()==0)
ck('L squarefree in i',L.gcd(L.derivative('i')).total_degree()==0)
ck('i L Delta pairwise coprime',all(a.gcd(b).total_degree()==0 for a,b in [(i,L),(i,Delta),(L,Delta)]))
print('PASS generic discriminant nilpotence and finite divisor separation','seconds',round(time.time()-st,3),flush=True)
# N=0 is NOT an ordinary connection point: v has a simple zero there.
# Its positive fractional residue eigenvalues exclude integer-order poles.
D0=D.subs({'v':0});MN=[[F(z.subs({'v':0}),6*D0) for z in row] for row in G['V']]
charN=sy.factor(smat(MN).charpoly(x).as_expr());expectedN=(6*x-1)**2*(3*x-1)**2*(3*x-2)**2*(6*x-5)**2/(6**4*3**4)
ck('N residue characteristic polynomial',sy.cancel(charN-expectedN)==0)
ck('N squarefree and separated',N.gcd(N.derivative('i')).total_degree()==0 and all(N.gcd(z).total_degree()==0 for z in [i,L,Delta]))
print('PASS N=0 fractional residue; no rational primitive pole allowed',charN,'seconds',round(time.time()-st,3),flush=True)
# Native v=infinity residue, which is the generic L=0 residue after pullback.
s=[1,1,0,0,1,1,0,0];d4=coeffs(D,'v')[4];ML=[]
for r in range(8):
 row=[]
 for k in range(8):
  terms=coeffs(G['V'][r][k],'v');assert max(terms,default=-100)<=4+s[r]-s[k]
  row.append(-F(terms.get(4+s[r]-s[k],zero),6*d4)-(s[r] if r==k else 0))
 ML.append(row)
charL=sy.factor(smat(ML).charpoly(x).as_expr());expectedL=(x+1)**6*(2*x+1)*(2*x+3)/4
ck('L residue characteristic polynomial',sy.cancel(charL-expectedL)==0)
print('PASS independent L residue',charL,'seconds',round(time.time()-st,3),flush=True)
# Generic i=infinity, built from leading polynomial coefficients of i*Gamma_i.
hinf=[0,0,1,2,0,0,1,2];den=6*L*BV*Dh*N;dc=coeffs(den,'i');dd=max(dc);Minf=[]
for r in range(8):
 row=[]
 for k in range(8):
  raw=hom(6*L*i*N*G['i'][r][k]+co*G['V'][r][k],5);nc=coeffs(raw,'i');nd=max(nc,default=-1000)
  ck('infinity regularity '+str(r)+' '+str(k),nd-dd+hinf[k]-hinf[r]<=0)
  entry=-F(nc[nd],dc[dd]) if nd-dd+hinf[k]-hinf[r]==0 else F(0)
  row.append(entry-(hinf[r] if r==k else 0))
 Minf.append(row)
charinf=sy.factor(smat(Minf).charpoly(x).as_expr());expectedinf=(x-1)**2*(x-2)**2*(x-3)**4
ck('infinity residue characteristic polynomial',sy.cancel(charinf-expectedinf)==0)
print('PASS independent i=infinity residue',charinf,'seconds',round(time.time()-st,3),flush=True)
# Actual after-w source bounds, directly from serialized polynomial degrees.
after=read('after-w-physical.json')['rows'];source_degrees=[]
for r,z in enumerate(after):
 nn,ddp=P(z['n']),P(z['d']);source_degrees.append(int(nn.degrees()[0]-ddp.degrees()[0])-hinf[r])
 ck('i0 target source pole '+str(r),min(e[0] for e in ddp.to_dict())-min(e[0] for e in nn.to_dict())+h[r]<=7)
 for factor,label,maxorder in [(L,'L',2+s[r]),(Delta,'Delta',1)]:
  temp=ddp;order=0
  while True:
   quotient,remainder=divmod(temp,factor)
   if remainder:break
   temp=quotient;order+=1
  ck('target '+label+' pole bound '+str(r),order<=maxorder)
 ck('target N regular '+str(r),bool(divmod(ddp,N)[1]))
ck('after-w target growth bound',max(source_degrees)<=-1)
# Compute all physical tangential infinity degrees, closing the old gap.
degrees={}
for t in ['j','w']:
 mat=[]
 if t=='j':rho=2*N*L+j*N.derivative('j')*L-j*N*L.derivative('j');td=6*j*N*L*BV*Dh
 else:rho=T*N*L+2*w*T.derivative('w')*N*L+w*T*N.derivative('w')*L-w*T*N*L.derivative('w');td=6*w*T*N*L*BV*Dh
 for r in range(8):
  row=[]
  for k in range(8):
   raw=hom(rho*G['V'][r][k]+(6*j*N*L*G['j'][r][k] if t=='j' else zero),5)
   row.append(int(raw.degrees()[0]-td.degrees()[0]) if raw else -10000)
  mat.append(row)
 degrees[t]=mat
# Both old and corrected fixed tangent currents have only rows 0,1; all
# their numerator polynomials are independent of i. Degree =1-30*power.
families=[]
for name,dpower in [('i-global-correction.json',1),('i-global-correction-corrected.json',2)]:
 data=read(name);growth=[]
 for t in ['j','w']:
  cdeg=[]
  for r,z in enumerate(data['tangent'][t]):
   pn=P(z['numerator']);assert not pn or pn.degrees()[0]==0
   cdeg.append(1-30*z['power'] if pn else -10000)
  for r in range(8):
   bound=max([cdeg[r]]+[degrees[t][r][k]+cdeg[k] for k in range(8)])-hinf[r]
   growth.append(bound);assert bound<=-1
 # Source at Delta has order at most largest tangent denominator+1.
 # Nilpotent residues then bound a rational primitive by that power.
 maxpower=max(z['power'] for t in ['j','w'] for z in data['tangent'][t]);assert maxpower==dpower
 denominator_degree=6+2*6+30*dpower
 families.append({'fixed_tangent_input':name,'primitive_i_pole_bound':6,'primitive_L_pole_bound':2,'primitive_Delta_pole_bound':dpower,'no_other_finite_i_poles':True,'maximum_i_growth':5,'common_denominator_i_degree':denominator_degree,'numerator_degree_bound':denominator_degree+5,'tangent_source_growth_bounds':growth})
ck('full fixed tangent infinity contribution controlled',True)
write('relative-i-completeness-independent-audit.json',{'status':'PASS','checks':checks,'i0_gauge':h,'i0_characteristic_polynomial':str(char0),'N_characteristic_polynomial':str(charN),'N_primitive_pole_bound':0,'L_gauge_s':s,'L_characteristic_polynomial':str(charL),'infinity_gauge':hinf,'infinity_characteristic_polynomial':str(charinf),'after_w_source_degrees_in_infinity_gauge':source_degrees,'physical_tangent_matrix_infinity_degrees':degrees,'families':families,'local_argument':'At a pole of order k of a primitive in a regular-singular frame, the coefficient is (Residue-k I) times the leading vector. At i=0,L=0,Delta=0 there is no positive integer residue eigenvalue; a source pole of order m allows primitive pole at most m-1. At N=0 the positive fractional residues have no positive integer eigenvalues and the target is regular, so a rational primitive has no pole. At other ordinary points differentiation forces no pole. At infinity source has at most a simple t=1/i pole and residue eigenvalues1,2,3, so gauged primitive growth<=3; raw growth<=5.','scope':'Any rational i-only completion with coefficients in C(j,w) after the precisely fixed j,w tangent currents. This imposes no restriction on the original full problem.','seconds':time.time()-st})
print('PASS complete rational i-only bounds: degree53 old, degree83 corrected','seconds',round(time.time()-st,3),flush=True)
