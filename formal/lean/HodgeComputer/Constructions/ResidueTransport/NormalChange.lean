import Mathlib.RingTheory.Derivation.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring

/-!
# Changing a coordinate normal to a paired normal

The source with numerator `B * p * q` can be expressed using the paired
normal `p * f + q * g`, with an explicit residue-divergence correction.
The statement is a field identity with specified tangent derivatives; it
requires neither a hypersurface presentation nor characteristic zero.

The residue-normal transport architecture follows `hodgepodgeconjecture`'s
accepted cyclic cubic construction (PR #165), building on `fqlx` and the
Hodge Computer collaborators' residue framework. This balanced-source
identity was prepared for `benediamond` with OpenAI ChatGPT and Codex
assistance for the mixed-polar construction. Applications supply their
normal and Hessian values, tangent identities and nonvanishing proofs.
-/

set_option maxHeartbeats 2000000

namespace ResidueNormalChange

variable {K : Type*} [Field K]

/-- Change the coordinate normal `f` to the paired normal `p * f + q * g`.
The final summand is `D C - C * D f / f` for
`C = -B * p * q ^ 2 / (p * f + q * g)`. In a hypersurface application,
`f` and `g` are the two coordinate partials, the three `fpp`, `fpq`, `fqq`
are the Hessian entries, and `D` is the tangent derivative in `q`.
The passive factor `B` need only satisfy `D B = 0`. -/
lemma paired_normal_change (D : Derivation ℤ K K)
    (p q B f g fpp fpq fqq : K)
    (hf : f ≠ 0) (hh : p * f + q * g ≠ 0)
    (DB : D B = 0)
    (Dp : D p = -g / f) (Dq : D q = 1)
    (Df : D f = fpq - g / f * fpp) (Dg : D g = fqq - g / f * fpq) :
    B * q / f - B * p * q * fpp / f ^ 2 =
      B * p * q * (3 * (p * f + q * g) -
        (p ^ 2 * fpp + 2 * p * q * fpq + q ^ 2 * fqq)) / (p * f + q * g) ^ 2 +
      (D (-B * p * q ^ 2 / (p * f + q * g)) -
        (-B * p * q ^ 2 / (p * f + q * g)) * D f / f) := by
  simp only [Derivation.leibniz_div, Derivation.leibniz, Derivation.leibniz_pow,
    map_neg, map_add, smul_eq_mul, nsmul_eq_mul, Dp, Dq, Df, Dg, DB]
  generalize hG : p * f + q * g = G at *
  field_simp [hf, hh]
  rw [← hG]
  ring

end ResidueNormalChange
