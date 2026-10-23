# Denominator construction and exact slice display

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

## Exact polynomial on the saved section

The saved section is the numerical realization of

\[
\alpha=\frac{2i}{5},\qquad\beta=\frac{13i}{20}.
\]

At these values,

\[
(p,q,s,k,u,v)=\left(-\frac{32}{5},-\frac{52}{5},-\frac{169}{10},
\frac{31i}{175},\frac{248976}{15625},\frac{59173191}{4000000}\right).
\]

Let $P$ be the specialized monic eliminant. In the exact finite algebra
$E=\mathbb Q[r]/(P)$, set $\xi=-m(r)/\ell(r)$ and $\eta=r\xi$.
Although $k$ is imaginary, these two elements have rational power-basis
coefficients: their formulas use only even powers of $k$. Write $M_f$ for
multiplication by $f$ in the basis $1,r,\ldots,r^{26}$ and define

\[
N(S,B,C)=\det(SI-BM_\xi-CM_\eta).
\]

This is a homogeneous degree-$27$ polynomial with $406$ rational coefficients.
The exporter obtains it by taking the characteristic polynomials of
$M_\xi+cM_\eta$ for the integers $c=0,\ldots,27$, interpolating exactly, and
homogenizing in $B$. It does not approximate the individual algebraic roots or
line factors.

The same exact computation establishes $P(0)\ne0$, invertibility of
$\ell(r)$, and a nonzero determinant for the original eight source rows and
first eight power-basis coordinates. Thus $H$ and $E_0$ are nonzero constants
on this section. The global clearing above restricts to

\[
D=E_0H^{28}\,a^{3000002}c^{3000002}
N\bigl(2(x^2+y^2),a^2,c^2\bigr).
\]

Consequently the displayed polynomial

\[
a\,c\,N\bigl(2(x^2+y^2),a^2,c^2\bigr)
\]

has exactly the same zero set, with multiplicities removed. Its degree is $56$.
`slices/divisors/quadric-contact-broken.json` stores a compact arithmetic program for a nonzero rational
multiple of this polynomial. It is presentation material extracted from the
accepted construction, not a replacement witness or acceptance receipt.

Regenerate it with `scripts/export-quadric-contact-divisor.py`, which requires
`python-flint`. The export records the saved plane and coordinate phases under
`sliceRestriction`; a different plane requires a new extraction. The stored
plane and the mesh have ordinary floating-point rounding, so they approximate
the ideal section above. The restriction metadata ties the formula to that
specific numerical realization; it does not claim the rounded rows satisfy
exact rational identities.

The renderer evaluates the quadratic inputs at a common projective scale before
forming their degree-$27$ norm. This preserves the zero set and the normalized
value/gradient calculation while preventing the norm from underflowing merely
because all three inputs are small. Difference-of-squares evaluation also avoids
unnecessary cancellation in the phase-rotated $2(x^2+y^2)$. The coefficients are
exact, but pixels still use floating-point arithmetic and the surface remains a
triangle approximation. Cancellation can produce small display artifacts near
closely spaced components; the numerical image is not mathematical evidence.
