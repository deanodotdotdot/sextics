import os
os.environ['SYMPY_GROUND_TYPES']='python'
import json,pathlib,time,hashlib,sys
from sympy.polys.rings import ring
from sympy.polys.domains import QQ
from qq_poly_parser import parse
sys.setrecursionlimit(50000);root=pathlib.Path(__file__).resolve().parents[1];st=time.time();checks={}
def read(n):return json.loads((root/n).read_text())
def ck(k,b):assert b,k;checks[k]=True
R,i,j,w=ring('i,j,w',QQ);T=1+w**3;N=9*i*i*w*w-16*j*j*T;L=256*T**5*N+729*i**6*j*j*w**6;AV=64*j*j*w*T*T*N;BV=9*i*i*L;s=4*i-1
cur=read('two-node-physical-current-patched.json');K=cur['K'];kn,kd=[parse(K[z],R) for z in ['n','d']]
ck('exact cubic patch',kn*(1728*BV)**3==kd*((1728*BV)**3+s**9*AV**3))
ck('patch difference boundary divisibility',not (s**9*AV**3).div(j**6*w**3*T**6*N**3)[1])
S,I,W=ring('i,w',QQ);tt=1+W**3;nn=9*I*I*W*W-16*tt;ll=256*tt**5*nn+729*I**6*W**6;aa=64*W*tt*tt*nn;bb=9*I*I*ll;ss=4*I-1
new=read(cur['Pnew_file']);hh=parse(new['h'],S);hh1=parse(new['remaining_H1'],S)
ck('cubic patch vanishes on double-node divisor',not ((1728*bb)**3+ss**9*aa**3).div(hh)[1])
for name,g in [('i',I),('L',ll),('H1',hh1)]:ck('h coprime '+name,hh.gcd(g).is_ground)
for block in cur['slices']:
 for rec in block['rows']:
  row=read(rec['file']);ck('bound file '+rec['file'],hashlib.sha256((root/rec['file']).read_bytes()).hexdigest()==rec['sha256']);den=parse(row['d'],S);expected=S.one
  for name,order in rec['denominator_support'].items():expected*=dict(i=I,L=ll,H1=hh1)[name]**order
  quotient,remainder=den.div(expected);ck('exact denominator '+rec['file'],not remainder and quotient.is_ground and bool(quotient))
  ck('nonzero '+rec['file'],row['n']!='0')
 print('PASS independently bound denominators',block['j'],time.time()-st,flush=True)
# Pure Python numerator parity on both deck branches.
a,b=cur['slices']
for rp,rm in zip(a['rows'],b['rows']):
 p=read(rp['file']);m=read(rm['file']);ck('denominator parity '+str(rp['row']),p['d']==m['d']);ck('numerator parity '+str(rp['row']),parse(m['n'],S)==(-1 if rp['row']<4 else 1)*parse(p['n'],S))
 print('PASS deck parity',rp['row'],time.time()-st,flush=True)
out={'status':'PASS independent exact patch identities and all saved denominator factorizations','check_count':len(checks),'checks':checks,'method':'Independent parser and pure Python QQ polynomial arithmetic; exact factorization support, hashes and deck parity. Full row equality is independently reconstructed from the native connection in patched-native-direct-replay-audit.json.','certificate':False,'seconds':time.time()-st};(root/'independent-patched-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(checks),'checks',time.time()-st,flush=True)
