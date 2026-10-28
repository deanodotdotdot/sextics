#!/usr/bin/env python3
"""Independent generic horizontal, literal primitive and flatness audit.

Imports only the independent quotient-ring audit, never a primary builder.
"""
import hashlib,json
from pathlib import Path
import sympy as s
from flint import fmpq_mpoly_ctx,fmpq_mpoly
import verify_generic_compact_connection as Q

HERE=Path(__file__).resolve().parent
DATA=HERE.parents[1]/'coupled-fresh/ruling-source/full-base-connection'
TDATA=HERE.parents[1]/'coupled-fresh/theta-compact'
checks={}


def check(name,condition):
    assert condition,name
    checks[name]=True


def main():
    rawfile=DATA/'affine-cd-generic-results.json'
    descfile=DATA/'rank8-ij-connections-results.json'
    vfile=DATA/'rank8-v-literal-primitives-results.json'
    raw=json.loads(rawfile.read_text());desc=json.loads(descfile.read_text());vr=json.loads(vfile.read_text())
    normv=json.loads((TDATA/'affine-V-generic-results.json').read_text())
    rankv=json.loads((TDATA/'rank8-descended-connection-results.json').read_text())
    den=Q.parse(raw['common_denominator'])
    basis=[Q.monomial(x) for x in raw['basis']]
    pwords=[Q.monomial(x) for x in raw['primitive_words']]
    DJ=Q.delta(Q.J);JJ=Q.mul(Q.J,Q.J)
    Jvar=Q.add(Q.scale(Q.mul(Q.aa,Q.aa),4),Q.scale(Q.mul(Q.aa,Q.qq),Q.d),Q.scale(Q.mul(Q.bb,Q.bb),4))
    for name,Qp,explicit in [('c',Q.normal(0,0,2),{}),('d',Q.normal(1,0,1),Q.normal(1,0,1))]:
        F=[[Q.parse(x) for x in row] for row in raw['primitive_numerators'][name]]
        G=[[Q.parse(x) for x in row] for row in raw['gamma_numerators'][name]]
        for col,N in enumerate(basis):
            numerator=Q.add(
              Q.mul(Q.mul(Qp,Q.add(Q.scale(Q.mul(Q.aa,Q.diff_word(N,0)),-1),Q.mul(Q.bb,Q.diff_word(N,1)))),Q.J),
              Q.scale(Q.mul(Q.mul(N,explicit),Q.J),-1),Q.mul(Q.mul(N,Qp),Jvar))
            f=Q.add(*(Q.scale(word,F[row][col]) for row,word in enumerate(pwords)))
            expected=Q.add(Q.mul(Q.J,Q.delta(f)),Q.scale(Q.mul(f,DJ),-1),
              *(Q.scale(Q.mul(word,JJ),G[row][col]) for row,word in enumerate(basis)))
            check('full generic '+name+' curve identity '+str(col),not Q.add(expected,Q.scale(numerator,-den)))

    C=fmpq_mpoly_ctx.get(('i','j','v'));ii,jj,vv=C.gens();zero=C.constant(0)
    D=fmpq_mpoly(desc['common_denominator'],C)
    Dv=fmpq_mpoly(vr['common_denominator'],C)
    w=[1,2,3,4,5,1,2,4,5];ind=[0,1,3,4,5,6,7,8,2]
    cp=ii-jj*jj/4;r4=cp*(cp-jj*jj)/8
    T=[[zero for _ in range(9)] for _ in range(9)]
    for col,row in enumerate(ind):T[row][col]=C.constant(1)
    T[2][3]=-vv*r4;T[2][5]=jj/2
    def descend(poly,shift):
        out={}
        for (aa,bb,cc),z in poly.to_dict().items():
            n=2*aa+bb+cc+shift
            assert n%6==0 and n>=0,(n,shift)
            key=(aa,bb,n//6);out[key]=out.get(key,0)+z
        return C.from_dict(out)
    DD=descend(den,0)
    exps=[]
    for word in pwords:
        assert len(word)==1
        exps.append(next(iter(word)))
    for direction,key,shift in [('i','c',2),('j','d',1),('V',None,0)]:
        source=raw if key else normv
        Fsource=source['primitive_numerators'][key] if key else source['primitive_numerators']
        Gsource=source['gamma_numerators'][key] if key else source['gamma_numerators']
        GG=[[descend(Q.parse(Gsource[r][col]),w[col]+shift-w[r]) for col in range(9)] for r in range(9)]
        PP=[[descend(Q.parse(Fsource[r][col]),w[col]+shift+6-3*exps[r][1]-exps[r][2]) for col in range(9)] for r in range(16)]
        if direction=='V':
            # All sixteen primitive words include x times each raw numerator.
            for col,word in enumerate(basis):
                (a,b,q),coef=next(iter(word.items()))
                k=exps.index((a,b,q+1))
                PP[k][col]-=vv*DD
                GG[col][col]+=w[col]*DD
        for col in range(9):
            newcol=[sum((GG[row][k]*T[k][col] for k in range(9)),zero) for row in range(9)]
            var={'i':0,'j':1,'V':2}[direction]
            for row in range(9):
                deriv=T[row][col].derivative(var)
                newcol[row]+=DD*deriv*(6*vv if direction=='V' else 1)
            # Compact rows are all raw rows except q², followed by its residue.
            changed=[newcol[k] for k in ind[:8]]+[newcol[2]+vv*r4*newcol[4]-jj*newcol[6]/2]
            target=(desc['full_rank9_Gamma_numerators'][direction] if key else vr['full_rank9_GammaV_numerators'])
            Dtarget=D if key else Dv
            for row in range(9):
                value=fmpq_mpoly(target[row][col],C)
                check('literal descended '+direction+' connection '+str(row)+','+str(col),not(changed[row]*Dtarget-value*DD))
            Ptarget=(desc['primitive_numerators'][direction] if key else vr['primitive_numerators'])
            for row in range(16):
                value=sum((PP[row][k]*T[k][col] for k in range(9)),zero)
                out=(Ptarget[row][col] if col<8 else
                     (desc['omega_primitive_numerators'][direction][row] if key else vr['omega_primitive_numerators'][row]))
                check('literal descended '+direction+' primitive '+str(row)+','+str(col),not(value*Dtarget-fmpq_mpoly(out,C)*DD))

    # Generic cohomological flatness, including the 6v in the V direction.
    check('shared connection denominator',D==fmpq_mpoly(rankv['GammaV_denominator'],C))
    Ni=[[fmpq_mpoly(x,C) for x in row] for row in desc['Gamma_numerators']['i']]
    Nj=[[fmpq_mpoly(x,C) for x in row] for row in desc['Gamma_numerators']['j']]
    Nv=[[fmpq_mpoly(x,C) for x in row] for row in rankv['GammaV_numerator']]
    def comm(A,B,r,c):return sum((A[r][k]*B[k][c]-B[r][k]*A[k][c] for k in range(8)),zero)
    for r in range(8):
        for c in range(8):
            ij=D*(Nj[r][c].derivative(0)-Ni[r][c].derivative(1))-Nj[r][c]*D.derivative(0)+Ni[r][c]*D.derivative(1)+comm(Ni,Nj,r,c)
            check('generic flatness i,j '+str(r)+','+str(c),not ij)
            for name,A,var in [('i',Ni,0),('j',Nj,1)]:
                residual=D*Nv[r][c].derivative(var)-Nv[r][c]*D.derivative(var)-6*vv*D*A[r][c].derivative(2)+6*vv*A[r][c]*D.derivative(2)+comm(A,Nv,r,c)
                check('generic flatness '+name+',v '+str(r)+','+str(c),not residual)
    out={'status':'passed generic horizontal and literal primitive audit','checks':checks,'count':len(checks),
      'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [rawfile,descfile,vfile]},
      'scope':'18 full generic curve identities, all horizontal and fixed-x V connection and primitive entries, all192 generic curvature entries. Actual compact source integration remains open.'}
    p=HERE/'full-base-connection-audit-results.json';p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'pass':True,'checks':len(checks),'output':str(p)}))


if __name__=='__main__':main()
