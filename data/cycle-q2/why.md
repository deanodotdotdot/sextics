Use the cyclic three-link sextic from [the degree-six cyclic instance](#case/cycle-three), but request
\[
q=2,\qquad
A=X_0^2\cdot X_1^2\cdot X_2^3\cdot Y_0^2\cdot Y_1^2\cdot Y_2.
\]
Every coordinate occurs, and the final pair has unequal exponents. The target singles out one position in the cycle even though the equation is invariant under cyclic permutation of all three pairs.

That symmetry offers a concrete organizing tool. Rotating the target produces two companion directions on the same hypersurface, and any valid field can be transported accordingly. Their invariant sum is only one combination, however. A method that solves the sum must still separate the non-invariant components before it solves the individual target displayed here.

The higher pole order introduces an independent difficulty. The field components have degree seven, and the condition is divisibility of \(A-2\cdot dF(v)+F\cdot\operatorname{div}(v)\) by \(F^3\). Multiplying a degree-six certificate by a polynomial does not generally produce this identity, because the multiplier contributes its own derivative. The [cyclic \(q=1\) construction](#case/cycle-three) supplies a primitive through a paired-sign cubic and its Jacobian, but it does not establish this third-order-pole identity.

The complementary diagonal quotient in [Chapter 2, §2.8](#technical-information/explicit-constructions) also fails on this equation: the closing edge has nonzero character under its action. This issue precedes the higher-pole integration problem, so extending the polynomial-density theorem to higher poles alone would not settle this target.

There is also an exact character distinction within the new route. The cyclic sextic is invariant under a sixth-root action with weights \((2,1,0,3,2,1)\) in the standard coordinate order. The projective volume contributes weight nine. The solved numerator has weight fifteen, giving invariant residue character, whereas the present numerator has weight seventeen, giving character \(\zeta_6^2\). Thus projecting to the same invariant quotient erases this target. This is a specific obstruction to transferring that construction, not a claim of nonexistence. [Chapter 2, §2.9](#technical-information/explicit-constructions) records the calculation.

The purpose is to test the higher pole order while retaining a sparse equation and a small symmetry group. This is more controlled than immediately attempting a dense general sextic at the same pole order.

Compare [the holdout \(q=2\) target](#case/holdout-q2): both use degree-twelve monomials, but one lives on an oriented chain and the other on a closed cycle. The all-target support theorem for the chain in [Chapter 4, §4.6](#technical-information/known-locus/46-all-target-support-on-the-chain-example) applies at every pole order. Its auxiliary reflection is lost when the cycle closes, because the additional coupling becomes an unmatched \(T^2\) term on the cover. Thus this target tests extension of the supporting geometry, as well as extension of a particular field formula. The all-pole-order diagonal constructions in [Chapter 2a](#technical-information/binary-blocks) provide a second baseline.
