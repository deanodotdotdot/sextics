#!/usr/bin/env python3
"""Independent exact quotient-ring and deck audit of the full compact GM packet.

Does not import the primary connection builder or solver. Native rational
polynomials accelerate the arithmetic; the implicit variations and compact
change are reconstructed here from the two defining curve equations.
"""
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from flint import fmpq_mpoly_ctx, fmpq_mpoly
import sympy as s

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
DATA=ROOT/'coupled-fresh/theta-compact'
C=fmpq_mpoly_ctx.get(('c','d','e'))
c,d,e=C.gens();zero=C.constant(0);one=C.constant(1)
checks={}


def check(name,condition):
    assert condition,name
    checks[name]=True


def add(*xs):
    out={}
    for x in xs:
        for word,value in x.items():
            out[word]=out.get(word,zero)+value
            if not out[word]:del out[word]
    return out


def scale(x,value):return {w:value*a for w,a in x.items() if value*a}


@lru_cache(None)
def normal(A,B,Q):
    if A and B:
        t=min(A,B)
        return normal(A-t,B-t,Q+3*t)
    if A>=2:
        return scale(add(normal(A-2,B+2,Q),
                         scale(normal(A-1,B,Q+1),d),
                         scale(normal(A-2,B,Q+2),c),
                         scale(normal(A-2,B,Q+1),e),
                         normal(A-2,B,Q)),-1)
    if B>=3:
        return scale(add(normal(A+1,B-3,Q+3),
                         scale(normal(A,B-2,Q+2),c),
                         scale(normal(A,B-3,Q+4),d),
                         scale(normal(A,B-2,Q+1),e),
                         normal(A,B-2,Q)),-1)
    return {(A,B,Q):one}


def mul(x,y):
    out={}
    for wa,ca in x.items():
        for wb,cb in y.items():
            out=add(out,scale(normal(*(a+b for a,b in zip(wa,wb))),ca*cb))
    return out


def diff_word(x,k):
    out={}
    for w,z in x.items():
        if w[k]:
            ww=list(w);ww[k]-=1
            out=add(out,scale(normal(*ww),z*w[k]))
    return out


def pv(x):
    return {w:2*c*z.derivative(0)+d*z.derivative(1)+e*z.derivative(2)
            for w,z in x.items() if 2*c*z.derivative(0)+d*z.derivative(1)+e*z.derivative(2)}


aa=normal(1,0,0);bb=normal(0,1,0);qq=normal(0,0,1)
J=add(scale(mul(aa,aa),2),scale(mul(aa,qq),d),scale(mul(bb,bb),-2))
common=add(scale(qq,2*c),scale(aa,d),{(0,0,0):e})
da=add(scale(mul(aa,common),-1),scale(normal(0,1,2),-6))
db=add(mul(bb,common),scale(normal(1,0,2),6),scale(normal(0,0,3),3*d))


def delta(x):return add(mul(diff_word(x,0),da),mul(diff_word(x,1),db),mul(diff_word(x,2),J))


def monomial(text):
    a0,b0,q0=s.symbols('a b q')
    poly=s.Poly(s.sympify(text),a0,b0,q0)
    terms=poly.terms()
    assert len(terms)==1 and terms[0][1]==1
    return normal(*terms[0][0])


def parse(text):return fmpq_mpoly(text.replace('**','^'),C)


def main():
    rawpath=DATA/'affine-V-generic-results.json'
    resultpath=DATA/'rank8-descended-connection-results.json'
    raw=json.loads(rawpath.read_text());result=json.loads(resultpath.read_text())
    den=parse(raw['common_denominator'])
    basis=[monomial(x) for x in raw['basis']]
    primitives=[monomial(x) for x in raw['f_words']]
    F=[[parse(x) for x in row] for row in raw['primitive_numerators']]
    G=[[parse(x) for x in row] for row in raw['gamma_numerators']]
    DJ=delta(J);JJ=mul(J,J)
    QV=add(scale(normal(0,0,2),2*c),scale(normal(1,0,1),d),scale(qq,e))
    JVexplicit=scale(normal(1,0,1),d)
    Jvar=add(scale(mul(aa,aa),4),scale(mul(aa,qq),d),scale(mul(bb,bb),4))
    for col,N in enumerate(basis):
        numerator=add(mul(pv(N),JJ),
          mul(mul(QV,add(scale(mul(aa,diff_word(N,0)),-1),mul(bb,diff_word(N,1)))),J),
          scale(mul(mul(N,JVexplicit),J),-1),mul(mul(N,QV),Jvar))
        f=add(*(scale(word,F[row][col]) for row,word in enumerate(primitives)))
        expected=add(mul(J,delta(f)),scale(mul(f,DJ),-1),
          *(scale(mul(word,JJ),G[row][col]) for row,word in enumerate(basis)))
        check('generic full cleared curve identity column '+str(col),
              not add(expected,scale(numerator,-den)))

    # An independent residue-row implementation gives compact coordinates by
    # selecting all raw rows except q²; no primary basis-change code is used.
    Tctx=fmpq_mpoly_ctx.get(('i','j','v'))
    ii,jj,vv=Tctx.gens();zz=Tctx.constant(0)
    weights=[1,2,3,4,5,1,2,4,5]
    def descend(poly,shift=0):
        out={}
        for (C0,D0,E0),z in poly.to_dict().items():
            power=2*C0+D0+E0+shift
            assert power%6==0,(power,shift)
            assert power>=0,(power,shift)
            key=(C0,D0,power//6)
            out[key]=out.get(key,0)+z
        return Tctx.from_dict(out)
    DD=descend(den)
    GG=[[descend(G[r][col],weights[col]-weights[r]) for col in range(9)] for r in range(9)]
    for r in range(9):GG[r][r]+=weights[r]*DD
    cp=ii-jj*jj/4;r4=cp*(cp-jj*jj)/8
    indices=[0,1,3,4,5,6,7,8]
    def changed_column(col):
        index=indices[col]
        values=[GG[row][index] for row in range(9)]
        if col==3:values=[a-vv*r4*b for a,b in zip(values,[GG[row][2] for row in range(9)])]
        if col==5:values=[a+jj*b/2 for a,b in zip(values,[GG[row][2] for row in range(9)])]
        # derivative of -v*r4 in the fourth compact vector.
        if col==3:values[2]-=6*vv*DD*r4
        return values
    Dnew=fmpq_mpoly(result['GammaV_denominator'],Tctx)
    Nnew=[[fmpq_mpoly(x,Tctx) for x in row] for row in result['GammaV_numerator']]
    for col in range(8):
        values=changed_column(col)
        residue=values[2]+vv*r4*values[4]-jj*values[6]/2
        check('generic compact residue preservation column '+str(col),not residue)
        for row,index in enumerate(indices):
            check('generic descended compact entry '+str(row)+','+str(col),
                  not (values[index]*Dnew-Nnew[row][col]*DD))
    omega=[GG[row][2] for row in range(9)]
    check('generic third kind residue diagonal',
          not (omega[2]+vv*r4*omega[4]-jj*omega[6]/2-3*DD))
    out={'status':'passed exact generic identities', 'checks':checks,'count':len(checks),
      'generic_source_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),
      'descended_source_sha256':hashlib.sha256(resultpath.read_bytes()).hexdigest(),
      'scope':'All nine full generic cleared implicit-curve identities reconstructed independently, 64 full generic compact entries, zero residue leakage and third-kind diagonal. Actual source primitive not supplied.'}
    path=HERE/'generic-compact-connection-audit-results.json'
    path.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'pass':True,'checks':len(checks),'output':str(path)}))


if __name__=='__main__':main()
