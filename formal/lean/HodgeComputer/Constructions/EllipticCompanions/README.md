# Elliptic companion algebra

Target-independent residue and elliptic contraction machinery extracted from the accepted crossed-ternary construction of `1337isnot1337`. The original declaration namespaces and acceptance-backed instance files are preserved. See `data/crossed-ternary-asymmetric/solution.md` for mathematical attribution, collaborators, and disclosed AI assistance.

The entry point `Contraction` proves `CrossedElliptic.product_divergence` for arbitrary characteristic-zero fields, two groups of derivations, and supplied scalar primitives with the required independence. It does not construct those primitives or identify any application target.

`CompanionAlgebra` contains generic incidence opens, normals, monic hypersurface derivations, and affine residue-data clearing. `Residues`, `Coordinates`, `Calculus`, `Kernels`, `Translation`, and `Infinity` implement the field, rational residues, coefficient derivations, translated pole separation, and infinity correction used by `Contraction`. Target-specific companion equations, seeds, domain proofs, scalar sources, and physical certificate closure are not extracted.

`ScalarEmbedding` parameterizes the monic companion cubic and its injective elliptic substitution by an arbitrary two-variable polynomial. `AffineCompanion` supplies the required irreducibility when that polynomial has constant term one. These modules justify denominator preservation under the substitution; they do not construct a scalar primitive or extend a source's pole order.

Build with `lake build HodgeComputer.Constructions.EllipticCompanions.Contraction`. New applications must independently establish their companion primitives, exact target transport, nonzero/legal denominators, homogeneity, and the protected certificate theorem.
