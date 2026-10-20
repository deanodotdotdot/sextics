# An explicit denominator for the pole-two holdout

The accepted proof constructs two endpoint certificates and combines them over a product denominator. Its homogeneous coefficient clearing is existential: it does not name a unique six-variable polynomial. The following gives one explicit choice of that clearing, using the same rational fields and endpoint combination. It is deliberately nonminimal. This is a presentation export, not an additional kernel-checked witness or a change to the accepted proof and credit.

All matrices below are 27 by 27 except the stated 10 by 10 source matrix. Matrix products, adjugates, and determinants give finite polynomial formulas; expansion into monomials is unnecessary. Work over the exact coefficient ring `Q(k)[alpha,beta]`, with `k²+k+1=0`, and set

\[
a=1+\alpha^6,\quad b=1+\beta^6,\quad c=\alpha\cdot\beta,\quad d=\beta\cdot k^2.
\]

## Clear the line coordinates

Let `p` be the raw degree-27 polynomial of `NewEliminant.lean`, with leading coefficient \(t=729\cdot a^{11}\). Let \(R\) be the multiplication matrix of its root in the basis \(1,r,\ldots,r^{26}\), for the monic polynomial \(p/t\). Then \(R_0=t\cdot R\) is polynomial. Use exactly `kappa`, `uu`, `coordinateNum`, and `coordinateDen` from `NewLineChart.lean` to define

\[
K_0=t^3\cdot\kappa(R),\qquad U_0=t\cdot\mathrm{uu}(R),\qquad
A_0=t^{17}\cdot\mathrm{coordinateNum}(R),\qquad
B_0=t^{21}\cdot\mathrm{coordinateDen}(R).
\]

The respective root degrees are at most 3, 1, 17, and 21, so these are polynomial matrices. Define

\[
\delta=\det B_0,\quad \eta=\det(K_0\cdot A_0),\quad
E_0=t^4\cdot A_0\cdot\operatorname{adj}(B_0),
\]
\[
G_0=d\cdot U_0\cdot B_0\cdot\operatorname{adj}(K_0\cdot A_0),\qquad
H=6\cdot t^3\cdot\eta\cdot d\cdot\delta.
\]

The following are \(H\) times the multiplication matrices of the accepted proof's `lineE`, `lineF`, `lineG`, and `lineH`:

\[
\begin{aligned}
E_H&=6\cdot t^3\cdot\eta\cdot d\cdot E_0,\\
F_H&=6\cdot t^2\cdot\eta\cdot d\cdot R_0\cdot E_0,\\
G_H&=t\cdot d\cdot\delta\cdot G_0,\\
J_H&=\delta\cdot(d\cdot R_0\cdot G_0+6\cdot\eta\cdot K_0).
\end{aligned}
\]

These identities follow directly from the four rational formulas in `NewLineAlgebra.lean`; all the matrices commute because they are rational expressions in the same root matrix. The denominator factors are nonzero on the proof's good fiber \((a,b,c,d)=(2,2,1,1)\), by its unit calculations.

## Clear the source solver and pole-two correction

Let \(J\) be the accepted 10 by 10 `GenericQuadratic.minor`. Its first four columns are the gradient coefficients. The remaining six are the first six power-basis coefficients of the ten `LineContact.sourceCoefficients`, evaluated at the four line coordinates. Put

\[
\overline J=H^4\cdot J,\qquad B=\det\overline J.
\]

This is a polynomial matrix: every source coefficient has line-coordinate degree at most four. Its determinant is nonzero on the good fiber, where the proof supplies an exact inverse. Let

\[
L=27\cdot a^2\cdot b+4\cdot c^3,\qquad
Q=L\cdot(L^4-2916\cdot a^8\cdot d^6),
\]

which is the coefficient denominator of `QuinticReduction.lean`. For active coordinates \((U,V,S,T)\), define

\[
\Pi=H\cdot S\cdot I-U\cdot E_H-V\cdot F_H,\qquad
\widehat D=6\cdot B\cdot Q\cdot H\cdot\det\Pi.
\]

The accepted generic denominator is \(6\cdot\det\Pi/H^{27}\). Thus \(\widehat D\) multiplies it by the explicit common factor \(B\cdot Q\cdot H^{28}\).

This factor also clears every numerator. Indeed, \(J^{-1}=H^4\cdot\operatorname{adj}(\overline J)/B\); the quintic primitive and its active divergence have denominator \(Q\); the elementary line numerators have coordinate degree at most three; and the pole adjugate has denominator \(H^{26}\). Substitution in `QuadraticSolver.combinedNumerators` and then `GenericQ2.N` gives polynomial numerators after multiplication by the same common factor. Multiplication by the passive scalar \(\alpha^3\cdot\beta^2/2\) introduces no additional coefficient denominator.

## The six-variable polynomial

Write \((x,a_1,c_1,y,b_1,d_1)=(X_0,X_1,X_2,Y_0,Y_1,Y_2)\) and choose \(n=6{,}000{,}000\). For each of the two roots \(k\), set

\[
D_k=x^2\cdot a_1^2\cdot(x\cdot a_1)^n\cdot
\widehat D\left(\frac yx,\frac{b_1}{a_1};
x^2,a_1^2,c_1^2+k^2\cdot d_1^2,k\cdot c_1\cdot d_1\right).
\]

The displayed expression is a polynomial. Sufficient bounds on the degree in each of \(\alpha,\beta\) are:

| Expression | Bound |
| --- | ---: |
| \(R_0,t\) | 66 |
| \(K_0,U_0,A_0,B_0\) | 204, 72, 1,182, 1,446 |
| \(\delta,\eta,E_0,G_0\) | 39,042, 37,422, 39,042, 37,555 |
| \(H\) and the four cleared line matrices | 76,668 |
| \(\overline J\) | 306,678 |
| \(B\) | 3,066,780 |
| \(Q\), quintic primitive coefficient numerators | 90, 100 |
| \(\widehat D\) and all cleared active numerators, including the passive scalar | less than 5,214,000 |

The bounds follow from root degrees, coefficient degrees in the submitted formulas, and the degree bounds for determinants and adjugates. They leave room below \(n\) for every coefficient. The active denominator has degree 27, so \(D_k\) is homogeneous of degree 12,000,058. The final polynomial is

\[
D=D_k\cdot D_{k^2},\qquad \deg D=24{,}000{,}116.
\]

The large degree is solely a conservative choice of clearing, not a lower bound or a claim of optimality. The simultaneous clearing and endpoint lift give corresponding homogeneous numerators with degree \(\deg D+7\). On the good fiber the extra factors are nonzero constants, so the proof's monic specialization argument for relative primality applies. The final combination is exactly the operation of `ReflectionCombination.lean`.

## Display on a fixed-ratio slice

The section retained in `fixed-slice-divisor.json` keeps \(Y_0/X_0\) and \(Y_1/X_1\) constant. The atlas uses a different, unrestricted section and does not display this divisor overlay. The exporter checks that the line-coordinate denominators, both source minors, and both quintic denominators are nonzero on the fixed-ratio section. Away from \(X_0X_1=0\), all coefficient-clearing factors are consequently nonzero constants. The remaining zero set is the union of the 27 factors

\[
X_2^2+k^2\cdot Y_2^2-e_j\cdot X_0^2-f_j\cdot X_1^2,
\]

for each endpoint, together with \(X_0=0\) and \(X_1=0\). Conjugate factors have the same zeros on the real amplitudes and are drawn once; multiplicities are suppressed. This preserves the support of the polynomial specified above.

`scripts/export-holdout-q2-divisor.py` isolates the roots with complex ball arithmetic, verifies all four cubic-line equations for every root, and checks invertibility of the exact source construction after specialization. It regenerates `fixed-slice-divisor.json`, preserving that section independently of the atlas view; `--slice` and `--output` select another fixed-ratio section and destination. The export contains floating-point coefficients for per-pixel evaluation. It is not a new proof of the certificate, nor does it certify topology. Changing the fixed ratios, phases, or saved plane requires regenerating the export.
