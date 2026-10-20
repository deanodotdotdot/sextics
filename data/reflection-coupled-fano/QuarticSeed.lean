import Mathlib.Algebra.Polynomial.Basic
import Mathlib.Algebra.CharP.Lemmas
import Mathlib.FieldTheory.IsAlgClosed.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Tactic

noncomputable section

namespace CoupledFanoQuarticSeed

open Polynomial

variable {K : Type*} [Field K] [CharP K 5]

lemma five_eq_zero : (5 : K) = 0 := by exact CharP.cast_eq_zero K 5

lemma two_ne_zero : (2 : K) ≠ 0 :=
  (CharP.cast_eq_zero_iff K 5 2).not.mpr (by decide)

lemma j_ne_zero {j : K} (hj : j^2 = 2) : j ≠ 0 := by
  intro h
  apply two_ne_zero (K := K)
  simpa [h] using hj.symm

lemma j_fifth {j : K} (hj : j^2 = 2) : j^5 = -j := by
  have h5 := five_eq_zero (K := K)
  calc
    j^5 = (j^2)^2*j := by ring
    _ = 4*j := by rw [hj]; ring
    _ = -j := by linear_combination j*h5

def seedX (j : K) : Fin 5 → K[X] :=
  ![C j*(1+X^4), C (2+j)*(X+X^3), C j*X^2,
    C j*(X-X^3), 1-X^4]

def seedU : K[X] := 1+X^4+X^8

lemma seed_equation {j : K} (hj : j^2 = 2) :
    (seedU (K := K))^3 + ∑ i : Fin 5, (seedX j i)^6 = 0 := by
  have h5 : (5 : K[X]) = 0 := by exact CharP.cast_eq_zero _ 5
  have hjp : (C j : K[X])^2 = 2 := by simpa only [← map_pow, hj, map_ofNat]
  simp only [seedU, seedX, Fin.sum_univ_succ, Matrix.cons_val_zero,
    Matrix.cons_val_succ, Fin.sum_univ_zero, add_zero, map_add, map_ofNat]
  linear_combination
    ((C j^4+2*C j^2+4)*((1+X^4)^6+X^12+(X-X^3)^6) +
      (C j^4+12*C j^3+62*C j^2+184*C j+364)*(X+X^3)^6)*hjp +
    (((1+X^4)^6+X^12+(X-X^3)^6) + (158+112*C j)*(X+X^3)^6 +
      (X^24+3*X^20+X^18+12*X^16+15*X^14+6*X^12+
        15*X^10+12*X^8+X^6+3*X^4+1))*h5

end CoupledFanoQuarticSeed
