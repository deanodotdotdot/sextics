import os
os.environ['SYMPY_GROUND_TYPES']='python'
import json,pathlib,time,hashlib,sys
from sympy.polys.rings import ring
from sympy.polys.domains import QQ
from qq_poly_parser import parse
sys.setrecursionlimit(50000);root=pathlib.Path(__file__).resolve().parents[1];st=time.time();checks={}
def read(n):return json.loads((root/n).read_text())
def ck(n,b):assert b,n;checks[n]=True
R,i,w=ring('i,w',QQ);bz=read('two-node-physical-normal-bezout-i4T.json');h=parse(bz['h'],R);A,B,C=[parse(z,R) for z in bz['multipliers']]
ck('exact rational Bezout certificate',A*h+B*h.diff(i)+C*h.diff(w)==i**4*(1+w**3))
T=1+w**3;N=9*i*i*w*w-16*T;L=256*T**5*N+729*i**6*w**6;AV=64*w*T*T*N;BV=9*i*i*L;s=4*i-1
ck('physical double-node numerator factor',64*h==s**3*AV+1728*BV)
ck('i derivative of physical normal coordinate',64*BV*h.diff(i)-64*h*BV.diff(i)==s*s*(12*AV*BV+s*(AV.diff(i)*BV-AV*BV.diff(i))))
ck('w derivative of physical normal coordinate',64*BV*h.diff(w)-64*h*BV.diff(w)==s**3*(AV.diff(w)*BV-AV*BV.diff(w)))
Jnum=2*N*L-32*T*L-2*(-4096*T**6+729*i**6*w**6)*N
zn=AV*s*s*(2*(3-s)*N*L-s*Jnum);zd=128*N*L
zn=zn*L+h*(L-(-4096*T**6+729*i**6*w**6))*zd;zd=zd*L
cur=read('two-node-physical-current-improved.json');z=cur['Ztarget'];ck('physical normal scale',parse(z['n'],R)*zd==parse(z['d'],R)*zn)
for name,m in [('alpha_i',B),('alpha_w',C)]:
 f=cur[name];fn=parse(f['n'],R);fd=parse(f['d'],R);ck(name+' exact construction',fn*zd*i**4*T==fd*zn*m)
 # No forbidden current pole: denominator divides a power of i and L.
 rest=fd
 for g in [i]:
  while rest and not rest.is_ground:
   q,rem=rest.div(g)
   if rem:break
   rest=q
 ck(name+' denominator support i',rest.is_ground)
print('PASS exact Bezout and physical normal construction',time.time()-st,flush=True)
S,I,J,V=ring('i,j,v',QQ);bp='packet/coupled-fresh/ruling-source/full-base-connection/';ij=read(bp+'rank8-ij-connections-results.json');vr=read(bp+'rank8-v-literal-primitives-results.json');D=parse(ij['common_denominator'],S);G={p:[[parse(z,S) for z in row] for row in ij['Gamma_numerators'][p]] for p in ['i','j']};G['V']=[[parse(z,S) for z in row] for row in vr['GammaV_numerators']]
H0=(4*I-1)**3*V+1728;H1=32*I**6*V*V-16*I**5*V*V+1728*I**3*V-10800*I*I*V+11250*I*V-3125*V+23328
# Preserve the same polynomial ring when substituting j, so exact division is unambiguous.
def sp(p,sign):return S.from_dict({(a,0,c):sum(q*sign**b for (aa,b,cc),q in p.items() if aa==a and cc==c) for a,_,c in p})
for sign in [1,-1]:
 ck(f'D factor j={sign}',sp(D,sign)==QQ(512,2187)*H1*H0**2)
 for row in range(8):
  src=(4*D if row==6 else S.zero)-G['V'][row][6]+2*I*G['i'][row][6]+J*G['j'][row][6]
  sq,srem=sp(src,sign).div(H0);gq,grem=sp(G['i'][row][7],sign).div(H0);jq,jrem=sp(G['j'][row][7],sign).div(H0);vq,vrem=sp(G['V'][row][7],sign).div(H0)
  ck(f'first double factor {sign} {row}',not(srem or grem or jrem or vrem))
  ck(f'normal linear coefficient {sign} {row}',not((4*I-1)*gq-2*vq).div(H0)[1])
  ck(f'normal constant coefficient {sign} {row}',not(6*(4*I-1)*(sq+QQ(sign,2)*jq)+(3-(4*I-1))*vq).div(H0)[1])
print('PASS all eight native pole functionals on both slices',time.time()-st,flush=True)
# The direct producer also saved the full residuals after density differentiation.
# Check exact deck symmetry and independently bind the files; numerator regeneration
# is a separate direct-native replay, not claimed by this structural proof.
a,b=cur['slices'];assert a['j']==1 and b['j']==-1
for rp,rm in zip(a['rows'],b['rows']):
 dp=read(rp['file']);dm=read(rm['file']);row=rp['row'];ck(f'row {row} denominator deck equality',dp['d']==dm['d']);ck(f'row {row} numerator deck parity',parse(dm['n'],R)==((-1 if row<4 else 1)*parse(dp['n'],R)))
 for rec in [rp,rm]:ck('hash '+rec['file'],hashlib.sha256((root/rec['file']).read_bytes()).hexdigest()==rec['sha256'])
 for name,g in [('i',i),('N',N),('L',L)]:ck(f'h coprime {name}',h.gcd(g).is_ground)
out={'status':'PASS independent rational Bezout and full eight-row pole-cancellation proof','method':'Pure Python QQ arithmetic, independent parser, direct native residue-functional identities; all derivative terms accounted for structurally','checks':checks,'check_count':len(checks),'full_saved_numerator_verification':'Direct native regeneration is separate; this audit proves h cancellation and deck parity, binds saved rows, and verifies the exact scalar certificate','conclusion':'The weighted physical current has no h denominator on either j=+/-1 slice; derivatives and remaining density corrections are retained. This does not prove global off-slice support or zero residual.','seconds':time.time()-st};(root/'independent-two-node-improved-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'checks',time.time()-st,flush=True)
