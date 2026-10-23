# Denominator construction and former numerical visualization

`HeadOfNaps`'s accepted proof constructs a cubic contact field over a finite algebra, then proves that a common homogeneous clearing of its coefficients exists. Here is one completely specified clearing. It gives the same rational field after the sextic lift. It is deliberately nonminimal: large powers clear fractions without expanding millions of coefficients. Neither the accepted Lean files nor their attribution are changed by this presentation export.

All arithmetic below is exact over $R=\mathbb Q[\alpha,\beta]$. Matrices have size $27$ unless stated otherwise. Products, adjugates, and determinants specify polynomials; an expanded monomial list is unnecessary.

## Polynomial matrices for the line

Take $p,q,s,k,u,v$, the degree-$27$ eliminant, and the polynomials $a(r),b(r),c(r),d(r),e(r),f(r),g(r)$ exactly as defined in `ParameterSpecialization.lean`, `GenericEliminant.lean`, and `GenericLineChart.lean`. Write

\[
\ell(r)=d(r)\cdot(b(r)^2-a(r)\cdot c(r))-e(r)\cdot a(r)\cdot b(r)+f(r)\cdot a(r)^2,
\]
\[
m(r)=d(r)\cdot b(r)\cdot c(r)-e(r)\cdot a(r)\cdot c(r)+g(r)\cdot a(r)^2.
\]

Let $t=u^{10}\cdot v$, let $R_c$ be the companion matrix of the monic eliminant, and set $R_0=t\cdot R_c$. Thus the subdiagonal of $R_0$ is $t$, and its last column is minus the $27$ lower coefficients of the raw eliminant. Its entries lie in $R$.

Define the following polynomial matrices and scalars:

\[
L_0=t^{26}\cdot\ell(R_c),\qquad M_0=t^{26}\cdot m(R_c),\qquad
\delta=\det L_0,\qquad e_0=\det R_0,
\]
\[
T_x=-\operatorname{adj}(L_0)\cdot M_0,\qquad
A_6=t^6\cdot\mathrm{aa}(R_c),\qquad B_3=t^3\cdot\mathrm{bb}(R_c),\qquad
h_3=t^3\cdot\mathrm{hNum}(R_c).
\]

Here `aa`, `bb`, and `hNum` are the polynomials in `GenericLineChart.lean`. Their degrees in $r$ are at most $6,3,3$; the degrees of $\ell,m$ are at most $26$. The displayed powers of $t$ therefore clear every companion-matrix denominator.

Put

\[
H=t^4\cdot\delta\cdot k^3\cdot e_0^3,
\]
\[
Z_0=(A_6\cdot T_x+k^2\cdot t^2\cdot\delta\cdot R_0\cdot B_3)\cdot\operatorname{adj}(R_0)^3,
\]
\[
\begin{aligned}
X_H&=t^4\cdot k^3\cdot e_0^3\cdot T_x, &
Y_H&=t^3\cdot k^3\cdot e_0^3\cdot R_0\cdot T_x,\\
Z_H&=t\cdot Z_0, &
W_H&=R_0\cdot Z_0+t^2\cdot\delta\cdot k^2\cdot e_0^2\cdot h_3\cdot\operatorname{adj}(R_0).
\end{aligned}
\]

Over $\mathbb Q(\alpha,\beta)$ these matrices equal $H$ times the multiplication matrices of the proof's line coordinates $\xi,\eta,\zeta,\omega$. This follows by substituting $\xi=-m(r)/\ell(r)$ and the formulas `lineZ`, `lineW` from `GenericLineUnscale.lean`.

## A common clearing for the field

Let $J_0$ be the $8\times8$ matrix whose row $i$ consists of the first eight entries in column zero of

\[
H^4\cdot\mathrm{sourceCoefficients}_i(p,q,s,k,X_H/H,Y_H/H,Z_H/H,W_H/H).
\]

Use exactly the eight source polynomials and their order in `ConcreteLine.lean`. Their degree in the four line coordinates is at most four, so $J_0$ is polynomial. Set $E_0=\det J_0$.

For the active variables $(S,T,B,C)$, set

\[
\Pi=H\cdot S\cdot I-B\cdot X_H-C\cdot Y_H,\qquad
\widehat D=H\cdot E_0\cdot\det\Pi.
\]

This is an explicit polynomial denominator. To check that it clears the numerators as well, let $U_j$ be the proof's four numerator multiplication matrices, and put $\widehat U_j=H^3\cdot U_j$. These matrices are polynomial because each numerator has coordinate degree at most three. Let $\widehat w$ be column three of $\operatorname{adj}(J_0)$, padded with nineteen zero entries. Then

\[
\widehat N_j=H^3\cdot\widehat w^{\mathsf T}\cdot\widehat U_j\cdot\operatorname{adj}(\Pi)\cdot e_{\mathrm{first}}.
\]

The proof's scalar cubic denominator and numerators are $D_0=\det\Pi/H^{27}$ and $N_{0,j}=\widehat w^{\mathsf T}\widehat U_j\operatorname{adj}(\Pi)e_{\mathrm{first}}/(E_0\cdot H^{25})$. Consequently both are multiplied by the **same** factor $E_0\cdot H^{28}$ above. The extra factor $H$ also makes all coordinate-clearing loci part of the displayed divisor.

At $(\alpha,\beta)=(1,2)$, all the inverses used in the accepted proof are units. Hence $t,k,e_0,\delta,E_0,H$ are nonzero there. This clearing has the nonzero specialization required by `ClearedDenominatorLegal.lean`.

## Homogeneous sextic denominator

Write $(x,a,c,y,b,d)=(X_0,X_1,X_2,Y_0,Y_1,Y_2)$ and take $n=3{,}000{,}000$. Define

\[
Q=(a\cdot c)^n\cdot\widehat D\left(\frac b a,\frac d c;
2(x^2+y^2),4x\cdot y,a^2,c^2\right),\qquad D=a^2\cdot c^2\cdot Q.
\]

This is a polynomial, not a rational-function prescription with unresolved denominators. Here are sufficient bounds on the degree in **each** of $\alpha,\beta$ of the coefficients:

| Expression | Bound |
| --- | ---: |
| $R_0,t$ | 60 |
| $L_0,M_0$ | 1,660 |
| $\delta,T_x$ | 44,820 |
| $H$ | 49,926 |
| $X_H,Y_H,Z_H,W_H$ | 49,932 |
| $J_0$ | 199,730 |
| $E_0$ | 1,597,840 |
| $\widehat D$ | 2,995,930 |
| $\widehat N_j$ | 2,995,918 |

These follow by adding degrees in products, taking maxima in sums, and multiplying by $m$ or $m-1$ for an $m\times m$ determinant or adjugate. The raw eliminant coefficients have degree at most $60$ in either parameter, and the coefficients of $\ell,m$ at most $100$. Thus the same $n$ clears both active numerator and denominator coefficients. All are homogeneous of active degree $27$. The final $D$ is homogeneous of degree $6{,}000{,}058$. This large degree is a consequence of the conservative clearing, **not** a lower bound or a claim of minimality.

Substitute the similarly cleared $\widehat N_j$ into the six numerator formulas in the accepted explanation. The strict equations follow from the same common-factor and sextic-lift identities. On the good fiber the new clearing is a nonzero scalar times $(a\cdot c)^n$, so the accepted denominator-legality argument applies unchanged.

## Numerical rendering

The denominator overlay is disabled. The former numerical export is retained in `fixed-slice-divisor.json` for offline investigation; restoring the overlay requires an exact display formula. The following describes the former presentation on the parameter-constant slice. `scripts/export-quadric-contact-divisor.py` uses complex ball arithmetic to isolate all $27$ eliminant roots at $4{,}096$-bit precision, checks the four cubic-line identities, and reconstructs the power-basis source minor by interpolation. It checks the resulting factorization against independent full-norm evaluations at $16$ points. An unresolved coefficient stops the export.

Away from $a\cdot c=0$, the support of this denominator is the union of the zeros of

\[
u,\quad v,\quad k,\quad\operatorname{Norm}(\ell(r)),\quad
\det(\mathrm{sourceMinor}),\quad\operatorname{Norm}(S-\xi\cdot B-\eta\cdot C).
\]

Indeed $e_0=u^{261}\cdot v^{36}$ and $H=u^{823}\cdot v^{112}\cdot k^3\cdot\delta$, while $\delta=t^{702}\cdot\operatorname{Norm}(\ell(r))$. On $H\ne0$, $E_0=H^{32}\cdot\det(\mathrm{sourceMinor})$ and $\det\Pi=H^{27}\cdot D_0$. On $H=0$, the explicit extra factor $H$ makes $\widehat D$ vanish. The additional components $a=0$ and $c=0$ come from the final sextic factor.

For visibility the sampled factors undergo continuous, sign-preserving normalization, then their signed minimum is used to display the union of their zero sets without multiplying many small magnitudes together. This suppresses multiplicities; it is not an exact distance function. As with every atlas surface, triangle interpolation only approximates the curves. The bounding box remains $\pm10$. These samples and the explicit clearing are presentation material, not a replacement acceptance receipt or a separately kernel-checked witness export.

## Saved real slice

The saved visualization holds the two parameters fixed: `Y1 = (2i/5) X1` and `Y2 = (13i/20) X2`, up to floating-point rounding of the orthonormal plane. At this parameter pair the eliminant has three real lines and twelve complex-conjugate pairs; the line relations and the nonvanishing coefficient factors are checked with 4096-bit ball arithmetic. Away from `X1 X2 = 0`, the coefficient-clearing factors are nonzero constants. The remaining support is evaluated from the individual line factors, with the two coordinate factors retained. This is a restriction of the same polynomial specified above, not a replacement certificate. Factoring the display calculation this way avoids underflow and loss of precision from multiplying many tiny values.

The export contains the two coordinate factors and the line factors grouped into three real factors and twelve conjugate pairs. Their coefficients refer to the real amplitudes before the saved coordinate phases are applied. The former shader evaluated these factors and their gradients directly at each pixel; no divisor values are stored at mesh vertices. The numerical coefficients are display approximations, not additions to the accepted Lean proof.
