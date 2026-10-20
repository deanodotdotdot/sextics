This sextic closes the two-link holdout into a cycle:
\[
F=F_0+\frac12\cdot\bigl(
X_0^3\cdot X_1\cdot Y_0\cdot Y_1+
X_1^3\cdot X_2\cdot Y_1\cdot Y_2+
X_2^3\cdot X_0\cdot Y_2\cdot Y_0\bigr).
\]
Simultaneously cycling the three coordinate pairs preserves the equation. The target \(A=X_0^3\cdot Y_0^3\) singles out one pair, so a certificate transports to its cyclic translates. A certificate for their invariant sum, however, does not automatically separate into certificates for each summand.

The closing edge gives a precise boundary for the [holdout cover construction](#technical-information/explicit-constructions). Adjoin \(T^6=Y_0^6+Y_2^6\), and write \(\alpha=Y_0/T\), \(\beta=Y_2/T\), \(y=Y_1\). The two chain terms become \(yT\) times a quartic in \(X\), which respects the exchange \(y\leftrightarrow T\). The closing term becomes
\[
\frac12\cdot\alpha\cdot\beta\cdot X_0\cdot X_2^3\cdot T^2.
\]
There is no matching \(y^2\) term. The exchange that creates the weighted quotient and its moving conic is therefore lost. This is more specific than a general lack of symmetry: the cycle retains paired signs and a cyclic permutation while breaking the particular symmetry used by the cover.

A useful next construction would replace that quotient, compensate for the unmatched term, or combine the three choices of distinguished coordinate in a way that recovers the individual target. None follows simply by transporting the chain proof. The discussion contains a reported exact exclusion of denominator degrees at most six by `rbajaj5`, with full numerator space and a nonzero quotient allowed; see the [calculation and reproduction packet](https://github.com/hodge-computer/sextics/discussions/55#discussioncomment-19002223). This bounds one search parameter, not unrestricted existence. [The degree-twelve companion](#case/cycle-q2) separately tests the pole-order boundary.
