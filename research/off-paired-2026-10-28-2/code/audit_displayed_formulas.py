from audit_core import *
st=time.time();cur=read('two-node-physical-current-improved.json');bz=read('two-node-physical-normal-bezout-i4T.json');s=4*i-1;N1=N.subs({'j':1});L1=L.subs({'j':1})
closed=w*T*T*(s*s*N1*(3-s)+16*s**3*T)+559872*i**4*w*w*T**5
assert jf(cur['Ztarget'])==F(closed)
assert P(bz['h'])==w*T*T*s**3*N1+243*i*i*L1
assert [len(P(z).to_dict()) for z in bz['multipliers']]==[146,157,144]
patch=read('two-node-physical-current-patched.json');expected=[{'i':13,'L':5,'H1':1},{'i':13,'L':5,'H1':1},{'i':11,'L':4,'H1':1},{'i':11,'L':4,'H1':1},{'i':13,'L':5,'H1':1},{'i':13,'L':5,'H1':1},{'i':12,'L':5,'H1':1},{'i':11,'L':5,'H1':1}]
for block in patch['slices']:assert [z['denominator_support'] for z in block['rows']]==expected
write('displayed-formulas-audit.json',{'status':'PASS','checks':['displayed Zprime polynomial','displayed physical h','three multiplier term counts','all sixteen displayed reduced denominator orders'],'certificate':False,'seconds':time.time()-st})
print('PASS displayed formulas and denominator table',flush=True)
