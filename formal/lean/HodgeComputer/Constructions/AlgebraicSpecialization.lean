import Mathlib.RingTheory.Polynomial.Resultant.Basic

/-!
# Nonvanishing at algebraic roots by specialization

A polynomial that is nonzero at a coalesced specialized root is nonzero
at every generic root. The coefficient maps must have compatible kernels,
and a fixed-size resultant retains its specialization identity when degrees
drop. No irreducibility assumption or specialization of a chosen root is
needed. Applications specialize polynomials on a suitable coefficient ring;
the statement does not evaluate rational functions at their poles.

Generalized from `fqlx`'s quadratic-shear construction in PR #184,
`data/mixed-polar/ResultantSpecialization.lean`, and its explanation in
discussion #58 (comment 19111681). That construction was prepared with
OpenAI Codex assistance for `fqlx`; the resultant identities are due to
the Lean/mathlib contributors. This generalization was prepared for
`benediamond` with OpenAI ChatGPT and Codex assistance.
-/

noncomputable section

namespace AlgebraicSpecialization

open Polynomial

variable {R K C : Type*} [CommRing R] [Field K] [Field C]

/-- Suppose `q` specializes to `u * (X - r)^m`, with `m > 0` and `u ≠ 0`.
If `P` is nonzero at `r` after specialization, then it is nonzero at every
root of `q` in the generic field. The kernel hypothesis permits transferring
vanishing of the fixed-size resultant from the generic field to the point.
It does not require either coefficient map to be injective. -/
theorem eval_ne_zero_of_coalescing_root_specialization
    (toField : R →+* K) (toPoint : R →+* C)
    (kernel : ∀ a, toField a = 0 → toPoint a = 0)
    (q P : Polynomial R) (k : K) (u r : C) (m : ℕ)
    (hm : 0 < m) (hq : q.natDegree ≤ m)
    (hroot : q.eval₂ toField k = 0)
    (hspecial : q.map toPoint = Polynomial.C u * (Polynomial.X - Polynomial.C r)^m)
    (hu : u ≠ 0) (hP : P.eval₂ toPoint r ≠ 0) :
    P.eval₂ toField k ≠ 0 := by
  intro hz
  let n := P.natDegree
  have hqField : (q.map toField).natDegree ≤ m := natDegree_map_le.trans hq
  have hPField : (P.map toField).natDegree ≤ n := natDegree_map_le
  obtain ⟨s, t, hs, ht, hbezout⟩ := exists_mul_add_mul_eq_C_resultant
    (q.map toField) (P.map toField) hqField hPField (Or.inl (Nat.ne_of_gt hm))
  have hzero : toField (q.resultant P m n) = 0 := by
    have h := congrArg (Polynomial.eval k) hbezout
    simp only [eval_add, eval_mul, eval_C, eval_map, hroot, hz, zero_mul, zero_add] at h
    rw [resultant_map_map] at h
    exact h.symm
  have hpointZero := kernel (q.resultant P m n) hzero
  have hPPoint : (P.map toPoint).natDegree ≤ n := natDegree_map_le
  have hpoint : toPoint (q.resultant P m n) = u^n * (P.eval₂ toPoint r)^m := by
    rw [← resultant_map_map, hspecial, resultant_C_mul_left]
    rw [resultant_X_sub_C_pow_left r _ m n hPPoint, eval_map]
  rw [hpoint] at hpointZero
  exact (mul_ne_zero (pow_ne_zero _ hu) (pow_ne_zero _ hP)) hpointZero

/-- Quadratic specialization with both roots coalescing at zero. -/
theorem eval_ne_zero_of_double_root_specialization
    (toField : R →+* K) (toPoint : R →+* C)
    (kernel : ∀ a, toField a = 0 → toPoint a = 0)
    (q P : Polynomial R) (k : K) (u : C)
    (hq : q.natDegree ≤ 2)
    (hroot : q.eval₂ toField k = 0)
    (hspecial : q.map toPoint = Polynomial.C u * Polynomial.X^2)
    (hu : u ≠ 0) (hP : P.eval₂ toPoint 0 ≠ 0) :
    P.eval₂ toField k ≠ 0 :=
  eval_ne_zero_of_coalescing_root_specialization toField toPoint kernel q P k u 0 2
    (by decide) hq hroot (by simpa using hspecial) hu hP

end AlgebraicSpecialization

#print axioms AlgebraicSpecialization.eval_ne_zero_of_coalescing_root_specialization
#print axioms AlgebraicSpecialization.eval_ne_zero_of_double_root_specialization
