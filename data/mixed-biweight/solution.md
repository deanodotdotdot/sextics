# Mixed-biweight through a transitive cubic and its Jacobian

## Status and exact target

This is a draft mathematical construction for the fixed `mixed-biweight` instance. It does not yet supply `Solution.lean`, a `proof.json` manifest, an expanded polynomial witness, or a protected proof of `HodgeComputer.HasCertificate`. The instance remains open until the repository verification and acceptance process succeeds. The arithmetic checks below are separate from that formal obligation.

Variables are ordered \(X_0,X_1,X_2,Y_0,Y_1,Y_2\). Keep \(q=1\), \(A=X_0^3Y_0^3\), and

\[
F=\sum_{i=0}^2(X_i^6+Y_i^6)
+\frac12X_0^3X_1Y_0Y_1
+\frac12X_1^3X_2Y_1Y_2
+\frac13X_0X_2Y_0^3Y_2.
\]

The argument replaces the broken holdout reflection with a paired-sign plane cubic, a newly computed Jacobian model, and a polynomial-curve incidence system. It follows the integration, finite-trace, and moving-map architecture of the [accepted cyclic construction](https://github.com/hodge-computer/sextics/blob/fc84eb5862d83c3491cdd45cc35bddd151c45892/data/cycle-three/solution.md), while retaining the transitive monomial and the exact fixed source.

The requested final identity is

\[
AD^2-D\sum_iN_iF_i
+F\left(D\sum_i\partial_iN_i-\sum_iN_i\partial_iD\right)=F^2Q,
\]

with \(D\ne0\), complex coprimality \(\gcd(D,F)=1\), and every \(N_i\) homogeneous of degree \(\deg D+1\). A nonzero \(Q\) is allowed. The construction asserts existence, with no denominator-degree bound.

The [discussion's degree-six exclusion](https://github.com/hodge-computer/sextics/discussions/56#discussioncomment-19002359) is a reported bounded result and is not a premise of this construction.

## 1. The actual cubic and its function field

Write \(p=(p_0,\ldots,p_5)\) in the required order and let


\[
K_F=\operatorname{Frac}\bigl(\mathbb C[p_0,\ldots,p_5]/(F)\bigr).
\]
First, the fixed \(F\) is irreducible over \(\mathbb C\). Regard it as a monic polynomial in \(p_0\), and specialize


\[
p_1=p_2=p_4=0,\qquad p_3=s+1,\qquad p_5=i.
\]
The result is


\[
p_0^6+(s+1)^6-1.
\]
This is Eisenstein at \(s\) in \(\mathbb C[s][p_0]\): its constant coefficient begins \(6s\), and all other nonleading coefficients vanish. A factorization of the original monic polynomial would specialize to a factorization with the same \(p_0\)-degrees. Hence the original polynomial is irreducible over \(\mathbb C\).

The paired-sign coordinates are therefore legitimate function-field elements:


\[
R=p_2^2,\qquad v=\frac{p_3}{p_0},\qquad
c_1=\frac{p_0p_4}{p_1p_3},\qquad
c_2=\frac{p_0p_5}{p_2p_3},
\qquad x=\frac{p_0^2}{R},\qquad y=\frac{p_1^2}{R}.
\]
Every coordinate occurring in these denominators is nonzero in \(K_F\), since \(F\) cannot divide a nonzero polynomial of degree less than six.

Direct substitution gives


\[
F=R^3U(x,y,1),\qquad A=v^3R^3x^3,
\]
where


\[
U=ax^3+By^3+Cz^3+dx^2y+ey^2z+fx^2z
\]
and


\[
\begin{aligned}
a&=\alpha+v^6,& B&=1+c_1^6v^6,& C&=1+c_2^6v^6,\\
d&=\frac{c_1v^2}{2},&
e&=\frac{c_1c_2v^2}{2},&
f&=\frac{c_2v^4}{3}.
\end{aligned}
\]
The physical target always has \(\alpha=1\). The variable \(\alpha\) is used only to form the required first variation before specialization.


---

## 2. New invariants and a fully normalized map

For this transitive cubic, the exact invariants are


\[
\boxed{s_4=Cd^2e-3BCdf-\frac13e^2f^2}
\]
and


\[
\boxed{
\begin{aligned}
s_6={}&27a^2B^2C^2+4a^2Ce^3+4B^2Cf^3+4BC^2d^3\\
&-4BCdef^2+\frac83Cd^2e^2f+\frac8{27}e^3f^3.
\end{aligned}}
\]
In particular, **\(s_4\) is independent of \(a\)**. This makes the first-variation source simpler than in the cyclic case.

Here is the normalization used throughout. For symmetric \(3\times3\) matrices, define


\[
\operatorname{MAdj}(A,B)
=\operatorname{adj}(A+B)-\operatorname{adj}(A)-\operatorname{adj}(B)
\]
and, for \(\mathbf r=(x,y,z)^t\),


\[
\mathcal C(A,B)=\mathbf r^t\operatorname{MAdj}(A,B)\mathbf r.
\]
Set


\[
H=\frac18\det\operatorname{Hess}(U),
\]

\[
\Theta=\frac19\mathcal C\left(
\operatorname{adj}\!\left(\frac{\operatorname{Hess}(U)}2\right),
\operatorname{adj}\!\left(\frac{\operatorname{Hess}(H)}2\right)
\right),
\]

\[
J=\frac19\det(\nabla U,\nabla H,\nabla\Theta).
\]
The placement of the factors \(1/2\) **inside** the adjugates matters.

The proposed construction uses the following covariants over


\[
\mathbb Q[x,y,z,a,B,C,d,e,f],
\]
and the associated covariant identities. On \(U=0\), the required relation is


\[
J^2=4\Theta^3+4s_4\Theta H^4-s_6H^6.
\]
Consequently,


\[
\boxed{\xi=\frac{\Theta}{H^2},\qquad
\eta=-\frac{J}{2H^3}}
\]
satisfy


\[
\boxed{\eta^2=\xi^3+s_4\xi-\frac{s_6}{4}}.
\]
The required full projective tangent identity is:


\[
\begin{aligned}
3zJ={}&U(H_x\Theta_y-H_y\Theta_x)\\
&-H(U_x\Theta_y-U_y\Theta_x)
+2\Theta(U_xH_y-U_yH_x).
\end{aligned}
\]
Thus, with \(z=1\),


\[
g=U_x,\qquad D_y=\partial_y-\frac{U_y}{g}\partial_x,
\]
we obtain


\[
\boxed{\frac{D_y\xi}{2\eta}=\frac3g.}
\]
This fixes the differential normalization needed for transport. The proof uses this explicit map and its identities directly.


### Actual nonvanishing

The complex point


\[
p=(2,2i,1-i,1+i,0,0)
\]
lies on the fixed sextic and has nonzero chart denominators. Exact evaluation gives


\[
g=-12+\frac32i,\qquad H=108-\frac{27}{2}i,
\]

\[
J=-\frac{725416965}{64}
-\frac{4668512355}{256}i,\qquad F_0=192.
\]
Therefore \(g,H,J,\eta,F_0\) are nonzero in the physical function field.

This is a localization argument: if one of these rational functions vanished in \(K_F\), its numerator after clearing the chart denominators would lie in \((F)\), and would vanish at this point.

The Weierstrass discriminant in this normalization is


\[
\Delta=-64s_4^3-27s_6^2.
\]
At the same point, \(s_4=0\) and \(s_6=27(1-i/8)^2\), so it is nonzero.


---

## 3. Symmetry and the homogeneous Jacobian coefficients

Put \(b=v^2\). The requested symmetry holds:


\[
U_{\zeta^2b}(x,y,z)=U_b(x,\zeta^2y,\zeta z),
\qquad \zeta^3=1.
\]
The coordinate substitution has determinant \(\zeta^3=1\).

In the displayed invariant formulas, the only \(b\)-exponents in \(s_4\) are \(3,6,9\), while those in \(s_6\) are \(0,3,\ldots,18\).

Set


\[
T=Rv^6,\qquad X=R^2\xi,\qquad Y=R^3\eta,
\]
and abbreviate


\[
\mathsf A=\alpha R+T,\qquad
\mathsf B=R+c_1^6T,\qquad
\mathsf C=R+c_2^6T.
\]
The degree-four coefficient is


\[
\boxed{
a_4=
\frac{c_1^3c_2}{8}R^2T\mathsf C
-\frac{c_1c_2}{2}RT\mathsf B\mathsf C
-\frac{c_1^2c_2^4}{108}R^2T^2.
}
\]
The degree-six coefficient is


\[
\boxed{
\begin{aligned}
b_6=-\frac14\Big(&27\mathsf A^2\mathsf B^2\mathsf C^2
+\frac{c_1^3c_2^3}{2}R^2T\mathsf A^2\mathsf C\\
&+\frac{4c_2^3}{27}RT^2\mathsf B^2\mathsf C
+\frac{c_1^3}{2}R^2T\mathsf B\mathsf C^2\\
&-\frac{c_1^2c_2^3}{9}R^2T^2\mathsf B\mathsf C
+\frac{c_1^4c_2^3}{18}R^3T^2\mathsf C
+\frac{c_1^3c_2^6}{729}R^3T^3\Big).
\end{aligned}}
\]
They satisfy


\[
a_4=R^4s_4,\qquad b_6=-R^6s_6/4
\]
after \(T=Rv^6\). Hence the actual auxiliary equation is


\[
V=Y^2-X^3-a_4(R,T)X-b_6(R,T)=0.
\]
All incidence calculations below use **\(\alpha=1\)**.


---

## 4. A new nonsingular thirteen-equation seed

Use


\[
R(T)=r_0+r_1T+r_2T^2,
\]

\[
X(T)=x_0+x_1T+x_2T^2+x_3T^3+x_4T^4,
\]

\[
Y(T)=y_0+y_1T+\cdots+y_6T^6.
\]
There are thirteen unknowns, in the order


\[
u=(r_1,r_2,x_1,x_2,x_3,x_4,y_0,y_1,\ldots,y_6).
\]
The equations are the coefficients of \(T^0,\ldots,T^{12}\) in


\[
\mathcal H=5832V.
\]
The factor \(5832=2^3 3^6\) clears all denominators. Homogeneity of \(a_4,b_6\) proves that no coefficients above degree twelve occur.


### Seed

Over \(\mathbf F_5\), take


\[
(c_1,c_2,r_0,x_0)=(1,1,1,3)
\]
and


\[
\boxed{
R=1+T^2,\qquad
X=3+4T^2+3T^4,\qquad
Y=2+3T^6.
}
\]
At these parameters,


\[
\bar a_4=4R^3T+4R^2T^2+2RT^3,
\]

\[
\bar b_6=
2R^6+3R^5T+3R^4T^2+2R^3T^3
+3R^2T^4+4RT^5+2T^6.
\]
Substitution gives the zero polynomial.

For coefficient rows \(0,\ldots,12\) and the unknown order above,


\[
\boxed{\det J_V=4\pmod5.}
\]
For the integral equations,


\[
J_{\mathcal H}=2J_V,\qquad
\boxed{\det J_{\mathcal H}=3\pmod5.}
\]
The inverse of \(J_V\), with entries in \(\mathbf F_5\), is:

```text
0 1 4 2 1 0 0 1 4 2 1 0 0
1 0 0 1 2 4 1 0 0 1 2 4 1
2 1 2 1 1 1 2 1 2 1 1 1 2
2 2 0 4 1 4 2 2 0 4 1 4 2
2 2 4 1 4 0 2 2 4 1 4 0 2
1 2 1 1 1 2 1 2 1 1 1 2 1
4 0 0 0 0 0 0 0 0 0 0 0 0
1 0 3 4 1 3 1 1 3 4 1 3 1
1 1 2 4 4 0 1 1 3 4 4 0 1
0 1 1 2 4 4 0 1 1 3 4 4 0
4 0 1 1 2 4 4 0 1 1 3 4 4
4 4 0 1 1 2 4 4 0 1 1 3 4
4 4 2 4 1 2 4 4 2 4 1 2 0
```

Thus \(J_{\mathcal H}^{-1}=3J_V^{-1}\) modulo five.

The displayed inverse and determinant must be bound to the actual thirteen coefficient equations, with all 169 derivative entries retained. Independent checks performed for this draft are recorded below.


---

## 5. Why the seed gives a characteristic-zero dominant family

This step has all the hypotheses required to change characteristic.

Let


\[
B_0=\mathbb Z[c_1,c_2,r_0,x_0].
\]
Form the integral square incidence scheme and localize at


\[
\det J_{\mathcal H}\,r_2x_4y_6y_0.
\]
At the seed, these factors have values


\[
(3,1,3,3,2),
\]
so the localized scheme is nonempty.

The square Jacobian criterion makes it étale over \(B_0\). Its image is therefore a nonempty open subset of the integral scheme \(\operatorname{Spec}B_0\), and contains the generic point. The generic fiber is nonzero.

The map


\[
B_0\longrightarrow \mathbb C(c_1,c_2,r_0,x_0)
\]
is injective. After extending scalars, a field factor of the resulting nonzero finite-type étale algebra supplies a finite separable extension


\[
\boxed{E/\mathbb C(c_1,c_2,r_0,x_0)}
\]
containing a solution of the same equations. The localized leading coefficients remain units, so the degrees are exactly \((2,4,6)\).


### Dominance from the endpoints

The substitution


\[
\mathbb C[T,c_1,c_2,R,X]\longrightarrow E[T]
\]
is injective. To see this, write a proposed nonzero relation as


\[
Q=\sum_j T^jQ_j(c_1,c_2,R,X)
\]
and choose its first nonzero coefficient. After substitution, the first surviving coefficient is


\[
Q_j(c_1,c_2,r_0,x_0)\ne0
\]
because these four parameters are algebraically independent.

The auxiliary equation is irreducible: over \(\mathbb C(c_1,c_2,R,T)\), the polynomial


\[
X^3+a_4X+b_6
\]
has odd valuation \(-3\) at \(X=\infty\), so it cannot be a rational square. Therefore


\[
K_J=\operatorname{Frac}\bigl(\mathbb C[Y,T,c_1,c_2,R,X]/(V)\bigr)
\]
embeds in \(L=E(T)\).

Both fields have transcendence degree five, and \(L/K_J\) is finitely generated. Thus


\[
\boxed{L/K_J\text{ is finite separable}.}
\]

### Polynomial normal and actual parameter derivatives

Write \(E_j=[T^j]\mathcal H\) for the thirteen incidence polynomials and
\(J_{\mathcal H}=(\partial E_i/\partial u_j)\). Group the entries of
\(5832J_{\mathcal H}^{-1}e_0=J_V^{-1}e_0\) by their corresponding slot
monomials. The factor \(5832\) accounts for \(\mathcal H=5832V\).
This gives polynomials \(n_R,n_X,n_Y\) such that


\[
V_Rn_R+V_Xn_X+V_Yn_Y=1,
\qquad n_R(0)=n_X(0)=0.
\]
In ambient order \((Y,T,c_1,c_2,R,X)\), put


\[
\psi=(n_Y,0,0,0,n_R,n_X).
\]
Order the derivations as

\[
(D_0,D_1,D_2,D_3,D_4)
=(\partial_T,\partial_{c_1},\partial_{c_2},\partial_{r_0},\partial_{x_0}).
\]

Here \(\partial_T\) fixes \(E\). The four base derivations extend uniquely
to \(E\), fix \(T\), commute, and preserve \(E[T]\). Their action on the
actual incidence coefficients is


\[
\partial_su=-J_{\mathcal H}^{-1}\partial_s(E_0,\ldots,E_{12})^t.
\]
On the right-hand side, \(\partial_sE_j\) differentiates the polynomial
with the unknown slots \(u\) held fixed, before evaluation at the incidence
solution. Consequently coefficient motion is retained throughout.

For


\[
\Phi=(Y(T),T,c_1,c_2,R(T),X(T))
\]
and the five derivations \(D_i\), including \(\partial_T\), let


\[
\mathcal M=[\psi,D_0\Phi,\ldots,D_4\Phi].
\]
The endpoint identities give


\[
\boxed{\det\mathcal M(0)=\frac1{2Y(0)}\ne0.}
\]
This proves the required full normal/tangent determinant and polynomiality properties.


---

## 6. The auxiliary construction gives an actual rational primitive

For any polynomial source \(P\), write \(\mathcal J=\det\mathcal M\), with polynomial evaluations understood at \(\Phi\). Define


\[
\mathcal B_P=
\mathcal J\,\nabla P\cdot\psi+
P\left(
\sum_{i=0}^{4}
\det\bigl(\mathcal M[i+1\leftarrow D_i\psi]\bigr)
-\mathcal J\,\psi^t\operatorname{Hess}(V)\psi
\right).
\]
Every term lies in \(E[T]\). This includes **all derivatives of the moving normal** and the Hessian term. Hence


\[
h(T)=\int_0^T\mathcal B_P(t)\,dt
\]
exists coefficientwise in \(E[T]\), because the characteristic is zero and \(\partial_T\) fixes \(E\).

The rational current


\[
w^L=P\psi_{\rm tail}
-\frac h{\mathcal J}D_0\Phi_{\rm tail}
\]
satisfies the full residue equation


\[
\boxed{
\operatorname{div}_{2Y}w^L
=-\frac{P_Y}{2Y}+\frac{P}{2Y^2}.
}
\]
Here “tail” omits the first, \(Y\), coordinate.

The proof is the normal-density identity followed by Piola transport. Its polynomial density is displayed above, so there is no unresolved algebraic integration in \(T\).

Finally, normalized finite trace


\[
\frac1{[L:K_J]}\operatorname{Tr}_{L/K_J}
\]
commutes with derivations and is \(K_J\)-linear. Applying it componentwise gives


\[
w^J\in K_J^5
\]
satisfying the same equation. The specified source is already in \(K_J\), so trace fixes it exactly.


---

## 7. Exact alpha source and physical moving-map correction

Because \(\partial_\alpha a_4=0\), the polynomial source is


\[
\boxed{
P_J=-\frac{V_\alpha}{144R}\bigg|_{\alpha=1}
=
-\frac{(R+T)\mathsf C
\left(54\mathsf B^2\mathsf C+c_1^3c_2^3R^2T\right)}{576}.
}
\]
The cancellation by \(R\) is exact. In particular, \(P_J\) is polynomial and independent of \(X,Y\).

Under the physical map,


\[
\boxed{P_J=\frac{R^5}{144}\dot b_W,\qquad b_W=-s_6/4.}
\]
The auxiliary construction therefore supplies


\[
\operatorname{div}_{2Y}w^J=\frac{P_J}{2Y^2}.
\]

### First variation

Use the dual-number deformation


\[
\alpha_\epsilon=1+\epsilon,\qquad
x_\epsilon=x-\epsilon x^3/g.
\]
It preserves the cubic equation exactly modulo \(\epsilon^2\). Thus


\[
\dot{\ }=\partial_a-\frac{x^3}{g}\partial_x,
\qquad
\dot g=3x^2-\frac{x^3U_{xx}}g.
\]
The exact moving-map identity is


\[
\boxed{
\frac{\dot g}{g}
=
\frac{\dot b_W}{2\eta^2}
-\frac g3D_y\left(\frac{\dot\xi}{2\eta}\right).
}
\]
It includes the induced motion of \(x\). This identity can be checked after clearing denominators and reducing by \(U\).

A compact explicit expression is


\[
Z=H(g\Theta_a-x^3\Theta_x)
-2\Theta(gH_a-x^3H_x),
\qquad
\frac{\dot\xi}{2\eta}=-\frac{Z}{gJ}.
\]

### Physical density and source

Let


\[
\delta_j=\partial_j-\frac{F_j}{F_0}\partial_0,
\qquad j=1,\ldots,5,
\]
and


\[
M_{ij}=\delta_j(T,c_1,c_2,R,X)_i.
\]
The exact volume multiplier, with the stipulated physical variable order, is


\[
\boxed{\kappa=\frac{F_0\det M}{2Y}=-144Rv^3.}
\]
The sign follows directly from the ambient chart volume


\[
\Omega=\frac{R^2v^2}{8}\,
dR\wedge dx\wedge dy\wedge dv\wedge dc_1\wedge dc_2.
\]
Taking the residue in the second coordinate \(x\) gives


\[
\omega_F=-\frac{v^2}{8Rg}\,
dv\wedge dc_1\wedge dc_2\wedge dR\wedge dy,
\]
whereas the auxiliary residue pulls back to


\[
\omega_J=\frac{18v^5}{g}\,
dv\wedge dc_1\wedge dc_2\wedge dR\wedge dy.
\]
Since the multiplier is nonzero, \(M\) is invertible. Its inverse supplies coordinate derivations, which prove algebraic independence of the five passive functions. Thus the actual covariant relation induces an embedding \(K_J\hookrightarrow K_F\). Equal transcendence degree and finite generation make this extension finite separable, supplying the required compatibility of derivations.

Now set


\[
h_0=p_0F_0+p_3F_3,\qquad h_1=p_1F_1+p_4F_4,
\qquad
\lambda=\frac{p_3^3}{4p_0^5p_1^2p_2^2},
\]
and, in tail order \((X_1,X_2,Y_0,Y_1,Y_2)\),


\[
W=(\lambda h_0p_1,0,-\lambda h_1p_3,\lambda h_0p_4,0),
\]

\[
C^{\rm vec}=(0,0,-p_0^3p_3^4/h_0,0,0).
\]
Direct computation for the fixed sextic proves


\[
h_0=2R^3xg,\qquad
\operatorname{div}_{F_0}W=0,\qquad W=v^3gD_y,
\]
and


\[
\frac{A_0}{F_0}-\frac{AF_{00}}{F_0^2}
=
v^3\frac{\dot g}{g}
+\operatorname{div}_{F_0}C^{\rm vec}.
\]
Therefore the complete physical current is


\[
\boxed{
w^F=\kappa M^{-1}w^J
+\frac{\dot\xi}{6\eta}W-C^{\rm vec}.
}
\]
It satisfies


\[
\boxed{
\operatorname{div}_{F_0}w^F
=-\frac{A_0}{F_0}+\frac{AF_{00}}{F_0^2}.
}
\]
This is the actual prescribed source equation in \(K_F\).


---

## 8. Legal homogeneous clearing proves the requested statement

The physical residue source has homogeneous weight zero. Under scaling,


\[
\operatorname{div}_{F_0}\bigl(w(\tau p)\bigr)
=
\tau\,(\operatorname{div}_{F_0}w)(\tau p).
\]
Taking the coefficient of \(\tau^1\) in the Laurent expansion of \(w^F(\tau p)\) therefore preserves the residue equation and produces a current of homogeneous weight one.

These coefficients have legal homogeneous representatives. In the graded domain \(\mathbb C[p]/(F)\), take the lowest nonzero homogeneous component of a denominator. Laurent inversion expresses each needed coefficient over a power of that component. Its homogeneous lift is not divisible by \(F\).

Lift the resulting current components to homogeneous rational ambient functions \(\widetilde w_j\), and define


\[
v_j=\widetilde w_j\quad(1\le j\le5),
\qquad
v_0=\frac{A-\sum_{j=1}^{5}F_j\widetilde w_j}{F_0}.
\]
Then


\[
\sum_iF_iv_i=A
\]
holds **exactly in the ambient rational field**, and


\[
\operatorname{div}v=0\pmod F
\]
follows from the physical residue equation.

Every \(v_i\) has homogeneous weight one. Choose a common homogeneous denominator \(D\) from the legal denominators and \(F_0\), and put


\[
N_i=Dv_i.
\]
Then:


- \(D\ne0\).
- \(\gcd(D,F)=1\) over \(\mathbb C\).
- Every \(N_i\) is homogeneous of degree \(\deg D+1\).
- \(\sum_iN_iF_i=AD\).

Moreover,


\[
B=D\sum_i\partial_iN_i-\sum_iN_i\partial_iD
=D^2\operatorname{div}v
\]
is a polynomial vanishing modulo \(F\). Hence \(B=FQ\) for a polynomial \(Q\), and


\[
\boxed{
AD^2-D\sum_iN_iF_i+
F\left(D\sum_i\partial_iN_i-\sum_iN_i\partial_iD\right)
=F^2Q.
}
\]
This establishes all the mathematical side conditions of the fixed certificate statement. No denominator-degree bound or assumption \(Q=0\) enters the argument.


---

## Independent checks for this draft

The modular incidence calculation was independently rebuilt from the displayed rational coefficients, rather than by accepting an exported Jacobian. The thirteen seed residuals vanish, the actual coefficient Jacobian has determinant four modulo five, both products with the displayed inverse are the identity, and the reconstructed polynomial normal pairs to one. For the integral equations, the determinant is three modulo five. The endpoint normal has value four, equal to the inverse of twice the seed value of \(Y(0)\).

The following self-contained check ran successfully with Python 3.11 and SymPy 1.14.0. Save it as a Python file and run it with SymPy installed. It verifies this arithmetic component; it does not formalize characteristic-zero lifting, the full covariant identities, physical transport, or the final certificate theorem.

```python
#!/usr/bin/env python3
"""Independent reconstruction of mixed-biweight displayed F5 incidence.
Uses displayed a4,b6, differentiates V directly, derives each coefficient from the displayed model.
"""
import json
import sympy as s
R,T,X,Y,c1,c2,alpha=s.symbols('R T X Y c1 c2 alpha')
A=alpha*R+T; B=R+c1**6*T; C=R+c2**6*T
q=s.Rational
a4=c1**3*c2*R**2*T*C/8-c1*c2*R*T*B*C/2-c1**2*c2**4*R**2*T**2/108
b6=-q(1,4)*(27*A**2*B**2*C**2+c1**3*c2**3*R**2*T*A**2*C/2+q(4,27)*c2**3*R*T**2*B**2*C+c1**3*R**2*T*B*C**2/2-c1**2*c2**3*R**2*T**2*B*C/9+c1**4*c2**3*R**3*T**2*C/18+c1**3*c2**6*R**3*T**3/729)
V=Y**2-X**3-a4*X-b6
H=s.Poly(s.expand(5832*V),R,T,X,Y,c1,c2,alpha)
assert all(z.q==1 for z in H.coeffs())
def mod(z):
 z=s.Rational(z);return int(z.p)*pow(int(z.q),-1,5)%5
def coeffs(expr):return [mod(s.expand(expr).coeff(T,i)) for i in range(13)]
seed={R:1+T**2,X:3+4*T**2+3*T**4,Y:2+3*T**6,c1:1,c2:1,alpha:1}
seedres=coeffs(V.subs(seed,simultaneous=True)); assert seedres==[0]*13
assert s.Poly(s.expand(V.subs(seed,simultaneous=True)),T).degree()<=12
coords=[R,R,X,X,X,X,Y,Y,Y,Y,Y,Y,Y]
degs=[1,2,1,2,3,4,0,1,2,3,4,5,6]
cols=[coeffs(s.diff(V,z).subs(seed,simultaneous=True)*T**d) for z,d in zip(coords,degs)]
J=s.Matrix(13,13,lambda i,j:cols[j][i]); det=int(J.det())%5; assert det==4
Inv=s.Matrix([
[0,1,4,2,1,0,0,1,4,2,1,0,0],
[1,0,0,1,2,4,1,0,0,1,2,4,1],
[2,1,2,1,1,1,2,1,2,1,1,1,2],
[2,2,0,4,1,4,2,2,0,4,1,4,2],
[2,2,4,1,4,0,2,2,4,1,4,0,2],
[1,2,1,1,1,2,1,2,1,1,1,2,1],
[4,0,0,0,0,0,0,0,0,0,0,0,0],
[1,0,3,4,1,3,1,1,3,4,1,3,1],
[1,1,2,4,4,0,1,1,3,4,4,0,1],
[0,1,1,2,4,4,0,1,1,3,4,4,0],
[4,0,1,1,2,4,4,0,1,1,3,4,4],
[4,4,0,1,1,2,4,4,0,1,1,3,4],
[4,4,2,4,1,2,4,4,2,4,1,2,0]])
assert (J*Inv).applyfunc(lambda z:z%5)==s.eye(13)
assert (Inv*J).applyfunc(lambda z:z%5)==s.eye(13)
# First inverse column solves J u = constant polynomial 1; group by ambient coord.
n={z:s.Integer(0) for z in [R,X,Y]}
for j,(z,d) in enumerate(zip(coords,degs)):n[z]+=Inv[j,0]*T**d
pair=sum(s.diff(V,z).subs(seed,simultaneous=True)*n[z] for z in [R,X,Y])
assert coeffs(pair)==[1]+[0]*12
assert n[R].subs(T,0)==n[X].subs(T,0)==0
assert mod(n[Y].subs(T,0))==pow(2*2,-1,5)==4
receipt={"seed_residual_mod_5":seedres,"det_JV_mod_5":det,"det_JH_mod_5":int((2*J).det())%5,"integral_equation_denominators_cleared":True,"both_inverse_products_identity":True,"normal_pairing_mod_5":[1]+[0]*12,"normal_R":str(n[R]),"normal_X":str(n[X]),"normal_Y":str(n[Y]),"normal_endpoint_Y_mod_5":4,"Jacobian_V_mod_5":[[int(z) for z in row] for row in J.tolist()]}
print(json.dumps({k:v for k,v in receipt.items() if k!='Jacobian_V_mod_5'},indent=2))

```

### Independent covariant and physical-source audit

A second exact reconstruction, also with SymPy 1.14.0, verifies the universal transitive-cubic syzygy modulo \(U\), the projective differential identity, the full moving-map identity modulo \(U\), the homogeneous \(a_4,b_6\) formulas, the derivative defining \(P_J\), the physical coordinate and source reduction, the ambient chart determinant, the normal-source correction, and the tangent field identities. Every Boolean check passed. The syzygy and moving-map calculations use the full generic polynomial rings, rather than checking finitely many parameter samples.

The following reproducer reconstructs the covariants from their displayed definitions. It checks these identities and reports the exact complex-point values. It does not establish the entire formal theorem or independently replace the shared normal-density, Piola, and finite-descent arguments.

```python
#!/usr/bin/env python3
"""Independent exact audit of the visible transitive-cubic formulas.
Requires SymPy 1.14.0.
Definitions are reconstructed directly from the displayed formulas.
"""
import json,time
import sympy as sp
from sympy.polys.rings import ring
from sympy import QQ
start=time.time()
R,x,y,z,a,b,c,d,e,f=ring('x,y,z,a,b,c,d,e,f',QQ)
coords=[x,y,z]
def mat_scale(A,c):return [[c*q for q in row] for row in A]
def transpose(A):return list(map(list,zip(*A)))
def adj(A):
 out=[]
 for i in range(3):
  row=[]
  for j in range(3):
   I=[q for q in range(3) if q!=j];J=[q for q in range(3) if q!=i]
   row.append((-1)**(i+j)*(A[I[0]][J[0]]*A[I[1]][J[1]]-A[I[0]][J[1]]*A[I[1]][J[0]]))
  out.append(row)
 return out
def det(A):return sum(A[0][j]*adj(A)[j][0] for j in range(3))
def hess(P):return [[P.diff(q).diff(t) for t in coords] for q in coords]
def report(k,v):
 if isinstance(v,bool):
  assert v, k
 print(json.dumps({k:v,'seconds':round(time.time()-start,3)}),flush=True)
 if isinstance(v,bool) and not v: raise AssertionError(k)
U=a*x**3+b*y**3+c*z**3+d*x*x*y+e*y*y*z+f*x*x*z
HU=hess(U);H=det(HU)/8
Au=adj(mat_scale(HU,QQ(1,2)));Ah=adj(mat_scale(hess(H),QQ(1,2)))
MA=adj([[Au[i][j]+Ah[i][j] for j in range(3)] for i in range(3)])
AdU=adj(Au);AdH=adj(Ah)
Theta=sum(coords[i]*coords[j]*(MA[i][j]-AdU[i][j]-AdH[i][j]) for i in range(3) for j in range(3))/9
J=det([[P.diff(q) for q in coords] for P in [U,H,Theta]])/9
S4=c*d*d*e-3*b*c*d*f-e*e*f*f/3
S6=27*a*a*b*b*c*c+4*a*a*c*e**3+4*b*b*c*f**3+4*b*c*c*d**3-4*b*c*d*e*f*f+QQ(8,3)*c*d*d*e*e*f+QQ(8,27)*e**3*f**3
report('covariant_term_counts',{'U':len(U),'H':len(H),'Theta':len(Theta),'J':len(J)})
report('s4_independent_a',S4.diff(a)==0)
report('s6_first_variation',S6.diff(a)==2*a*c*(27*b*b*c+4*e**3))
differential=3*z*J-U*(H.diff(x)*Theta.diff(y)-H.diff(y)*Theta.diff(x))+H*(U.diff(x)*Theta.diff(y)-U.diff(y)*Theta.diff(x))-2*Theta*(U.diff(x)*H.diff(y)-U.diff(y)*H.diff(x))
report('full_differential_identity',differential==0)
syzygy=J*J-4*Theta**3-4*S4*Theta*H**4+S6*H**6
report('syzygy_defect_term_count',len(syzygy))
quo,rem=syzygy.div(U)
report('syzygy_divisible_U',rem==0)
report('syzygy_quotient_term_count',len(quo))
# Verify the actual complex chart point, without simplifying generic fractions.
p=[2,2*sp.I,1-sp.I,1+sp.I,0,0]
rad=p[2]**2;v=p[3]/p[0];c1=p[0]*p[4]/(p[1]*p[3]);c2=p[0]*p[5]/(p[2]*p[3]);xx=p[0]**2/rad;yy=p[1]**2/rad
values=[xx,yy,1,1+v**6,1+c1**6*v**6,1+c2**6*v**6,c1*v*v/2,c1*c2*v*v/2,c2*v**4/3]
def at_point(P):
 return sp.simplify(P.as_expr().subs(dict(zip(sp.symbols('x y z a b c d e f'),values))))
report('physical_point_values',{k:str(at_point(P)) for k,P in [('U',U),('g',U.diff(x)),('H',H),('J',J),('s4',S4),('s6',S6)]})
# Source claimed by independently derived same normalization.
rr,tt,cc1,cc2,alpha,vv=sp.symbols('R T c1 c2 alpha v')
AA=alpha*rr+tt;BB=rr+cc1**6*tt;CC=rr+cc2**6*tt
Pj=-sp.Rational(3,32)*AA*BB**2*CC**2-sp.Rational(1,576)*rr**2*tt*cc1**3*cc2**3*AA*CC
bdot=-((alpha+vv**6)*(1+cc2**6*vv**6)*(27*(1+cc1**6*vv**6)**2*(1+cc2**6*vv**6)+4*(cc1*cc2*vv**2/2)**3))/2
report('homogeneous_source_identity',sp.expand(Pj.subs(tt,rr*vv**6)-rr**5*bdot/144)==0)
report('sympy_version',sp.__version__)
# Full fixed-parameter moving-map identity, with every induced x derivative.
U1=U.compose(z,R.one); H1=H.compose(z,R.one); Th1=Theta.compose(z,R.one); J1=J.compose(z,R.one)
g=U1.diff(x); uy=U1.diff(y)
Z=H1*(g*Th1.diff(a)-x**3*Th1.diff(x))-2*Th1*(g*H1.diff(a)-x**3*H1.diff(x))
Nden=g*J1
Nder=g*(Z*Nden.diff(y)-Nden*Z.diff(y))-uy*(Z*Nden.diff(x)-Nden*Z.diff(x))
move=6*J1**2*(3*x*x*g-x**3*U1.diff(x).diff(x))+3*S6.diff(a)*H1**6*g*g+2*Nder
report('moving_map_defect_term_count',len(move))
moveq,mover=move.div(U1)
report('moving_map_full_remainder_zero',mover==0)
# New homogeneous Weierstrass coefficients as transcribed from the draft.
a4=cc1**3*cc2*rr**2*tt*CC/8-cc1*cc2*rr*tt*BB*CC/2-cc1**2*cc2**4*rr**2*tt**2/108
b6=-sp.Rational(1,4)*(27*AA**2*BB**2*CC**2+cc1**3*cc2**3*rr**2*tt*AA**2*CC/2+sp.Rational(4,27)*cc2**3*rr*tt**2*BB**2*CC+cc1**3*rr**2*tt*BB*CC**2/2-cc1**2*cc2**3*rr**2*tt**2*BB*CC/9+cc1**4*cc2**3*rr**3*tt**2*CC/18+cc1**3*cc2**6*rr**3*tt**3/729)
pars=sp.symbols('a b c d e f')
physpars=[alpha+vv**6,1+cc1**6*vv**6,1+cc2**6*vv**6,cc1*vv**2/2,cc1*cc2*vv**2/2,cc2*vv**4/3]
S4phys=S4.as_expr().subs(dict(zip(pars,physpars))); S6phys=S6.as_expr().subs(dict(zip(pars,physpars)))
report('homogeneous_a4_identity',sp.expand(a4.subs(tt,rr*vv**6)-rr**4*S4phys)==0)
report('homogeneous_b6_identity',sp.expand(b6.subs(tt,rr*vv**6)+rr**6*S6phys/4)==0)
report('source_from_b6_alpha',sp.expand(sp.diff(b6,alpha)-144*rr*Pj)==0)
# Ambient physical reduction and normal-change data.
p=sp.symbols('p0:6');p0,p1,p2,p3,p4,p5=p
F=sum(q**6 for q in p)+p0**3*p1*p3*p4/2+p1**3*p2*p4*p5/2+p0*p2*p3**3*p5/3
A=p0**3*p3**3; Fr=[sp.diff(F,q) for q in p]
rad=p2*p2;rat=p3/p0;cone=p0*p4/(p1*p3);ctwo=p0*p5/(p2*p3);cx=p0*p0/rad;cy=p1*p1/rad
up=U1.as_expr().subs(dict(zip(sp.symbols('x y a b c d e f'),[cx,cy,1+rat**6,1+cone**6*rat**6,1+ctwo**6*rat**6,cone*rat**2/2,cone*ctwo*rat**2/2,ctwo*rat**4/3])))
gp=g.as_expr().subs(dict(zip(sp.symbols('x y a b c d e f'),[cx,cy,1+rat**6,1+cone**6*rat**6,1+ctwo**6*rat**6,cone*rat**2/2,cone*ctwo*rat**2/2,ctwo*rat**4/3])))
gxp=g.diff(x).as_expr().subs(dict(zip(sp.symbols('x y a b c d e f'),[cx,cy,1+rat**6,1+cone**6*rat**6,1+ctwo**6*rat**6,cone*rat**2/2,cone*ctwo*rat**2/2,ctwo*rat**4/3])))
h0=p0*Fr[0]+p3*Fr[3];hh=p0*p0*sp.diff(F,p0,2)+2*p0*p3*sp.diff(F,p0,p3)+p3*p3*sp.diff(F,p3,2)
report('physical_cubic_reduction',sp.cancel(F-rad**3*up)==0)
report('physical_source_reduction',sp.cancel(A-rat**3*rad**3*cx**3)==0)
report('physical_paired_gradient',sp.cancel(h0-2*rad**3*cx*gp)==0)
report('physical_paired_hessian',sp.cancel(hh-h0-4*rad**3*cx**2*gxp)==0)
# Raw coordinate volume, independent of covariants and of the hypersurface.
chart=[rad,cx,cy,rat,cone,ctwo]
chartdet=sp.factor(sp.Matrix([[sp.diff(q,t) for t in p] for q in chart]).det())
report('ambient_chart_volume',sp.cancel(chartdet-8/(rad**2*rat**2))==0)
report('ambient_chart_det',str(chartdet))
cor=-p0**3*p3**4/h0
F0,F3=Fr[0],Fr[3]
def delta3(q):return sp.diff(q,p3)-F3/F0*sp.diff(q,p0)
divcor=delta3(cor)-cor*delta3(F0)/F0
physical_source=3*p0*p0*p3**3/F0-A*sp.diff(F,p0,2)/F0**2
normal_jet=3*cx*cx-cx**3*gxp/gp
report('full_physical_normal_source_identity',sp.cancel(physical_source-rat**3*normal_jet/gp-divcor)==0)
h1=p1*Fr[1]+p4*Fr[4]
lam=p3**3/(4*p0**5*p1**2*p2**2)
Wfull=[-lam*h1*p0,lam*h0*p1,0,-lam*h1*p3,lam*h0*p4,0]
report('ambient_tangent_W',sp.cancel(sum(w*fi for w,fi in zip(Wfull,Fr)))==0)
report('ambient_divergence_W',sp.cancel(sum(sp.diff(w,q) for w,q in zip(Wfull,p)))==0)
def Wapply(q):return sum(w*sp.diff(q,t) for w,t in zip(Wfull,p))
report('W_passive_coordinates_constant',all(sp.cancel(Wapply(q))==0 for q in [rad,rat,cone,ctwo]))
report('W_cubic_y_direction',sp.cancel(Wapply(cy)-rat**3*gp)==0)
uyphys=uy.as_expr().subs(dict(zip(sp.symbols('x y a b c d e f'),[cx,cy,1+rat**6,1+cone**6*rat**6,1+ctwo**6*rat**6,cone*rat**2/2,cone*ctwo*rat**2/2,ctwo*rat**4/3])))
report('W_cubic_x_direction',sp.cancel(Wapply(cx)+rat**3*uyphys)==0)
report('audit_finished',True)

```

## Attribution and remaining formal work

The draft was developed for `fqlx` with OpenAI ChatGPT Pro and Codex assistance. The originating research chat is [Constructive Existence Derivation](https://chatgpt.com/c/6ad83d5f-5dc8-83ea-9612-b66d2d541d2c). This write-up contains the mathematical data needed to inspect the proposal without access to that chat.

The cubic invariant theory is classical; see Tom Fisher, [Testing Equivalence of Ternary Cubics](https://www.dpmms.cam.ac.uk/~taf1000/papers/testeqtc.pdf). The accepted cyclic construction, credited there to `hodgepodgeconjecture`, `fqlx`, the Hodge Computer collaborators, and prior mathematical sources, supplies the proof architecture. The shared PolynomialCurves and ResidueTransport libraries provide reusable lifting, integration, trace, and moving-map identities with application-specific hypotheses.

The following remain necessary before this draft can be presented as a complete solve submission: implement the target-specific invariant identities and incidence bindings in Lean, establish the function-field and transport obligations using the maintained shared library, prove the exact protected `Submission.certificate`, and run sandboxed compilation, kernel replay, and the axiom audit. No such formal verification or project acceptance is claimed here.
