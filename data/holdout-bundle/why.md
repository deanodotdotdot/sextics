This target combines two residue characters on the central chain sextic:

\[
A=X_0^3\cdot Y_0^3+X_0^3\cdot Y_0\cdot Y_1^2.
\]

The first summand is served by the Fermat cover and its moving-conic construction. The second has deck exponent zero: the antisymmetrized source used by that cover vanishes. The bundle therefore tests assembly across two supporting geometries, rather than another specialization of one source formula.

**Geometric existence for both summands follows from [Chapter 4, §4.6](#technical-information/known-locus/46-all-target-support-on-the-chain-example).** The construction of `fqlx` makes the complementary quotient effective in Lean. With \(p=Y_0\cdot Y_1\), \(v=Y_1\cdot Y_2\), and \(\lambda=Y_1^3/(Y_0^3+i\cdot Y_2^3)\), its fiber equation has polynomial source \(-X_0^3\cdot p/(6\cdot\lambda)\). An exact nonsingular curve incidence, a polynomial normal, coefficientwise integration and finite trace supply its primitive; full coordinate transport returns the required physical target. [Chapter 2, §2.8](#technical-information/explicit-constructions/28-a-complementary-quotient-and-its-polynomial-densities) explains the mechanism and its source boundary.

The two certificates combine over the product of their denominators. Both quotient remainders are retained, so this assembly does not require strict certificates. It also does not produce a compact expanded divisor: the proof constructs finite algebraic coefficient fields and traces before homogeneous clearing.

The broader lesson concerns the image of a construction. The complementary curve family handles every polynomial source on its fixed quotient, including fifty odd sextic monomials on the physical variety. Other invariant sources acquire fiber denominators and are not covered directly by that polynomial-integration theorem. Their geometric existence is still known; extracting useful fields or formalizing another primitive remains a separate problem. Combining two mechanisms can enlarge target coverage without implying that either survives a change in the sextic equation.
