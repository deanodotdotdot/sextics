from audit_core import *
st=time.time();h=((4*i-1)**3*AV+1728*BV).subs({'j':1});fac=h.factor();print('physical h0 factors',[(str(f) if len(f.to_dict())<70 else 'terms'+str(len(f.to_dict())),int(e)) for f,e in fac[1]],flush=True)
write('physical-two-node-curve.json',{'status':'exact factorization','h0_numerator':str(h),'factors':[{'polynomial':str(f),'multiplicity':int(e),'terms':len(f.to_dict())} for f,e in fac[1]],'seconds':time.time()-st})
