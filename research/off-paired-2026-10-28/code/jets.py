from exact import *

def pcoeff(p,var):
 idx=C.names().index(var);out={}
 for exp,c in p.to_dict().items():
  e=list(exp);k=e[idx];e[idx]=0
  out.setdefault(k,{})[tuple(e)]=c
 return {k:C.from_dict(val) for k,val in out.items()}
def rs(z,var,high):
 z=R(z)
 if not z:return {}
 a=pcoeff(z.n,var);b=pcoeff(z.d,var);lo=min(a)-min(b);bd=min(b);b0=R(b[bd]);out={}
 for k in range(lo,high+1):
  val=R(a.get(k+bd,0))
  for q,c in b.items():
   if q>bd and k+bd-q in out:val-=R(c)*out[k+bd-q]
  out[k]=val/b0
 return {k:z for k,z in out.items() if z}
def add(*args):
 out={}
 for a in args:
  for k,z in a.items():out[k]=out.get(k,R(0))+z
 return {k:z for k,z in out.items() if z}
def mul(a,b,hi):
 out={}
 for k,z in a.items():
  for l,t in b.items():
   if k+l<=hi:out[k+l]=out.get(k+l,R(0))+z*t
 return {k:z for k,z in out.items() if z}
def scale(a,z):return {k:c*z for k,c in a.items() if c*z}
def diff(a,var):
 if var=='w':return {k-1:k*z for k,z in a.items() if k}
 return {k:z.diff(var) for k,z in a.items() if z.diff(var)}
def shift(a,m):return {k+m:z for k,z in a.items()}
def compose_v(z,vseries,high):
 q=rs(z,'v',high);out={};vpows={0:{0:R(1)}}
 for k in range(1,high+1):vpows[k]=mul(vpows[k-1],vseries,high)
 assert not q or min(q)>=0
 for k,c in q.items():out=add(out,scale(vpows[k],c))
 return out
if __name__=='__main__':
 import time
 st=time.time();D,G,ij,vr=matrices();data=load('coupled-fresh/theta-compact/actual-N-j-removed-source-results.json');Db=poly(data['common_curve_denominator'])
 saved=json.loads((HERE/'joint-audit.json').read_text());coefs={k:R(z['n'],z['d']) for k,z in saved['physical_scalar_coefficients'].items()}
 scalar={k:rs(z,'w',3) for k,z in coefs.items()};vser=rs(vp,'w',4)
 res=[{} for k in range(8)]
 for name,key in [('B','Bvector_numerators'),('J','Jvector_numerators'),('H','Hvector_numerators')]:
  for k in range(8):res[k]=add(res[k],mul(scalar[name],compose_v(R(data[key][k],Db),vser,3),-1))
 res[7]=add(res[7],{k:z for k,z in scalar['e7'].items() if k<0})
 print('remaining principal parts',flush=True)
 for k,row in enumerate(res):print(k,{m:str(z) for m,z in row.items()},flush=True)
 export(HERE/'w-jets.json',{'principal_parts':[{str(k):z.data() for k,z in row.items()} for row in res],'seconds':time.time()-st})
 # Native connection jets to physical w for forthcoming correction construction.
 out={key:[[{str(k):z.data() for k,z in compose_v(R(val,D),vser,3).items()} for val in row] for row in mat] for key,mat in G.items()}
 export(HERE/'connection-w-jets.json',out)
 print('saved connection jets',time.time()-st,flush=True)
