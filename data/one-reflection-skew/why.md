The sextic of [One reflection · residual sector](#case/one-reflection) has hidden exchanges of \(Y_0\) and \(Y_1\), which allow its target to split between two cubic-surface constructions. The additional term
\[
\frac17\cdot X_0\cdot X_1\cdot Y_0\cdot Y_1\cdot(Y_0^2-Y_1^2)
\]
breaks those exchanges while preserving the prescribed involution and the separate \(Y_2\) reflection. The target \(X_0^3\cdot Y_0^3\) is even in \(Y_2\), so that surviving reflection does not serve it. Smoothness follows from a direct derivative estimate: the mixed terms cannot cancel the pure sixth-power derivative at a coordinate of maximal modulus.

The [equal-coefficient cover](#technical-information/explicit-constructions) gives a checked construction for the transverse target on the unperturbed equation. Its useful reflection does not survive this skew deformation. The same choice \(T^6=Y_0^6+Y_2^6\), \(Y_0=\alpha T\), \(Y_1=y\) transforms the skew term into
\[
\frac17\cdot\alpha\cdot X_0\cdot X_1\cdot y\cdot T
\cdot(\alpha^2T^2-y^2).
\]
It is not invariant under \(y\leftrightarrow T\) over the Fermat coefficient field. Thus neither the original exchange nor this particular cover supplies the desired quotient. The successful cover argument suggests a direction, but its hypotheses still need to be re-established for this fixed sextic.

The complementary diagonal quotient is broken too: under weights \((5,1,5)\) on \(Y\), the two monomials of the skew term have weights four and two. Neither is invariant. Its polynomial-source theorem therefore does not bypass the missing exchange on this deformation.

A nonsingular replacement conic solves the analogous curve problem for [the ternary deformation](#case/holdout-ternary-deformation), where the quotient survives. That example supplies reusable lifting and integration machinery, but does not cure the missing exchange here: the equation must first be placed on a serving auxiliary geometry.

An alternative retains the skew term and uses twisted elliptic companions. In the [construction of `fqlx`](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19080252), a quartic coefficient algebra supplies degree-three correspondences whose summed pullback–pushforward action is \(6I\) on the relevant two-dimensional differential space. Thus this route reaches the source character missed by the reflection. It reduces the problem to an explicit rational primitive equation with the physical parameter derivatives and connection terms retained. That primitive remains unsolved: a serving correspondence alone is not a certificate, and a proposed tangent lift leaves a nonzero divergence correction.

The instance therefore tests extension through a skew coupling at two distinct levels: finding a correspondence with the right source image, and constructing the primitive on that correspondence. The latter remains a useful focused target even after the former is understood. Neither the original failed quotients nor a failed correction ansatz excludes other supporting divisors.
