This is a cyclic-cover version of the Fano construction, with a different symmetry from the reflection examples. Writing \(Z=X_2^3\), the sextic becomes \(G=Z^2+t\cdot Z\cdot C+H\), where \(C\) and \(H\) are the displayed cubic and sextic in the other five variables. The order-three automorphism \(X_2\mapsto\zeta_3\cdot X_2\) survives the couplings.

**Nonconstructive existence is known**, by the weighted-Fano density theorem in [Chapter 3, §3.4](#technical-information/geometric-support). The finite map

\[
\Phi=(X_0,X_1,X_2^3,Y_0,Y_1,Y_2),\qquad \det(d\Phi)=3\cdot X_2^2
\]

has weights \((1,1,3,1,1,1)\), whose sum is eight. Its degree-six quotient is Fano of index two. Our target has exactly the required density form:

\[
A=\det(d\Phi)\cdot \Phi^*\!\left(\frac{1}{3}\cdot X_0\cdot Y_0^3\right).
\]

The polynomial in parentheses has weighted degree four, as required for \(q=1\). Equivalently, the character \(\zeta_3^2\) of the numerator cancels the character \(\zeta_3\) of the residue volume.

The quotient theorem supplies support through rational curves. An explicit starting point is the free weighted line \([X_0:X_1:Z:Y_0:Y_1:Y_2]=[0:s:0:is:t:it]\), identified by `rbajaj5` in [the discussion](https://github.com/hodge-computer/sextics/discussions/112#discussioncomment-19002605). Its nonsingular incidence connects the geometry to the shared polynomial-family integration machinery. The key tasks are dominance, a polynomial normal, finite trace, and legal transport through the cubic map. This separates the construction of a quotient primitive from extraction of a practical denominator.

This is not merely the old reflection formula with a different label. None of the six coordinate reflections preserves the equation, and the Hessian symmetrizer calculation rules out a nontrivial linear block decomposition. The finite-map theorem is relevant because of the specific density factor in \(A\); it does not say that every target on the same sextic has been handled.
