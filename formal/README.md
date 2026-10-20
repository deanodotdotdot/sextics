# The formal acceptance contract

The live challenge's target is existence, not minimization of the degree of a denominator. A constructive and a nonconstructive Lean proof must prove the same statement for an immutable `(F,q,A)`.

Let `R = ℂ[X0,X1,X2,Y0,Y1,Y2]`. For the chosen sextic `F`, pole parameter `q`, and homogeneous odd target `A`, the statement asks for a nonzero homogeneous `D` and a six-tuple `N` such that:

- `D` is relatively prime to `F`.
- Each `Nᵢ` is homogeneous of degree `deg(D) + 6q − 5`; zero components are allowed by the homogeneous predicate.
- The rational field `vᵢ = Nᵢ / D` satisfies `F^(q+1) ∣ A − q·dF(v) + F·div(v)` in the localization away from `F`.

The standing instances have `q ∈ {1,2}`, `F(X,−Y)=F(X,Y)`, and `A(X,−Y)=−A(X,Y)`. Field parity may be enforced by averaging; it must not accidentally narrow the stated existential problem.

## A finite algebraic witness

Define the polynomial

```text
E = A D² − q D Σᵢ Nᵢ ∂ᵢF
    + F (D Σᵢ ∂ᵢNᵢ − Σᵢ Nᵢ ∂ᵢD).
```

Since `D` is invertible in the relevant localization, a witness for the equation is the exact polynomial identity `E = F^(q+1) Q`. A strict certificate has `E=0`. This cleared identity, together with homogeneity and denominator admissibility, is the constructive checker interface. The theorem `localization_identity` in `HodgeComputer/Verify.lean` establishes the bridge to the rational-vector-field statement.

## Protected verification

`formal/lean/HodgeComputer/Verify.lean` defines `Verify` and the existential `HasCertificate` over complex coefficients. Its localization identity justifies the cleared equation. The shared contract imposes no denominator-degree bound or extra parity condition on the witness.

The verifier generates a protected exact target from the base branch's record. Contributors prove its existential statement and, when exporting a JSON witness for display, an additional theorem about those exact witness polynomials. The protected pipeline compiles the source in isolation, replays its declarations with the kernel checker, and audits the statement and axioms. Allowed axioms are `propext`, `Classical.choice`, and `Quot.sound`.

A rational-coefficient identity transfers to complex coefficients, but denominator admissibility over the complex numbers must also be established. Do not infer complex coprimality merely from rational irreducibility. Nonconstructive proofs are allowed when they establish the same protected existential theorem.

The Lean project pins its toolchain and mathlib manifest. Instance-specific proofs belong to each instance's existing data folder and first enter through its solve PR. Reusable machinery from accepted proofs can be extracted into the shared library through a separate maintenance PR. A checked merge by the configured owner and a trusted acceptance receipt are required before the publisher derives solved status and leaderboard credit. See [the proposal specification](../CONTRIBUTING.md) and [verification workflow](../MAINTAINING.md#verification-sign-off-and-publication).

## Reusable constructions

[`HodgeComputer.Constructions.HoldoutCover`](lean/HodgeComputer/Constructions/HoldoutCover/README.md) contains the Fermat-cover and moving-conic machinery from `fqlx`'s accepted [holdout proof](https://github.com/hodge-computer/sextics/pull/128). The construction supplies a primitive for an arbitrary polynomial source on its weighted quotient; an application must prove the source and derivative identities that transport its own target back to the original sextic.

New holdout specializations can import `HodgeComputer.Constructions.HoldoutCover.GeneralizedCover` and apply `HoldoutGeneralization.certificate_of_source_pair`. The module also supplies the vanishing traces of the square and inverse square of the cover coordinate. These are ingredients for the fixed holdout sextic, not a theorem for arbitrary sextics or targets.

The original accepted files under `data/holdout/` remain unchanged as the source of the original verification record. New submissions use the maintained shared modules instead of copying those files. Imports retain the original declaration namespaces and mathematical attribution; do not import both copies into the same Lean module.

[`HodgeComputer.Constructions.PolynomialCurves`](lean/HodgeComputer/Constructions/PolynomialCurves/README.md) contains arithmetic lifting and polynomial-family integration extracted from the accepted constructions of `fqlx` and `hodgepodgeconjecture`. It lifts a nonsingular square incidence system from a special fiber to a finite extension of the generic coefficient field, and converts a dominant polynomial-curve family with a polynomial normal into normalized certificate data. The [module guide](lean/HodgeComputer/Constructions/PolynomialCurves/README.md) lists the precise application obligations and original sources. These results supply reusable steps; each application still establishes its own incidence, dominance, coordinate transport, and exact target.
