import HodgeComputer.Verify
import Mathlib.RingTheory.Derivation.Basic

/-!
Strict pole-two transport from a split weighted-divergence primitive.

This proves the chart calculus without asserting existence of the required
weighted-divergence primitive, an embedding of the physical function field,
or legal denominator clearing. Those are separate application obligations.

Prepared with OpenAI Codex assistance for contributor fqlx.
-/

noncomputable section
namespace SplitTernaryHigherPole
open scoped BigOperators

section Field
variable {K : Type*} [Field K] [CharZero K]

def chartEquation (p q l : K) : K := p + l ^ 6 * q

def baseCoefficient (p q l : K) : K := chartEquation p q l * l ^ 5 / (9 * p ^ 2)

def vertical (p q l s P Q : K) : K :=
  -l ^ 6 * s / (12 * p) - l ^ 6 * s * chartEquation p q l / (18 * p ^ 2) +
    chartEquation p q l * l ^ 6 * (P / p - Q / q) / (54 * p ^ 2)

def horizontalDivergence (p q l s P Q : K) : K :=
  chartEquation p q l * l ^ 5 / (9 * p ^ 2) * s +
    (-chartEquation p q l * l ^ 5 / (27 * p ^ 3) + l ^ 5 / (9 * p ^ 2)) * P +
    (4 * chartEquation p q l * l ^ 5 / (27 * p ^ 2 * q) + l ^ 11 / (9 * p ^ 2)) * Q

/-- Convert the supplied weighted-divergence equation into the actual
horizontal divergence of the chart field. -/
theorem horizontal_divergence
    {ι : Type*} [Fintype ι] (D : ι → Derivation ℤ K K) (W : ι → K)
    (p q l s P Q : K) (hp : p ≠ 0) (hq : q ≠ 0)
    (hDl : ∀ i, D i l = 0)
    (hP : (∑ i, W i * D i p) = P) (hQ : (∑ i, W i * D i q) = Q)
    (hw : (∑ i, D i (W i)) - 5 * P / (3 * p) - 4 * Q / (3 * q) = s) :
    (∑ i, D i (baseCoefficient p q l * W i)) = horizontalDivergence p q l s P Q := by
  have hterm (i : ι) : D i (baseCoefficient p q l * W i) =
      baseCoefficient p q l * D i (W i) +
        (l ^ 5 / (9 * p ^ 2) - 2 * chartEquation p q l * l ^ 5 / (9 * p ^ 3)) *
          (W i * D i p) + l ^ 11 / (9 * p ^ 2) * (W i * D i q) := by
    have h9 : D i (9 : K) = 0 := (D i).map_natCast 9
    simp only [baseCoefficient, chartEquation, Derivation.leibniz,
      Derivation.leibniz_div, Derivation.leibniz_pow, map_add, smul_eq_mul,
      hDl, h9, zero_mul, mul_zero, add_zero, zero_add]
    field_simp [hp]
    <;> ring
  simp_rw [hterm]
  simp only [Finset.sum_add_distrib, ← Finset.mul_sum]
  rw [hP, hQ]
  have hdiv : (∑ i, D i (W i)) = s + 5 * P / (3 * p) + 4 * Q / (3 * q) := by
    linear_combination hw
  rw [hdiv]
  unfold horizontalDivergence baseCoefficient
  field_simp [hp, hq]
  <;> ring

/-- The complete strict chart identity. The term `2 v_l / l` is the physical
coordinate Jacobian correction and is retained in full. -/
theorem strict_chart_identity
    (L : Derivation ℤ K K) (p q l s P Q : K)
    (hp : p ≠ 0) (hq : q ≠ 0) (hl : l ≠ 0)
    (hLp : L p = 0) (hLq : L q = 0) (hLl : L l = 1)
    (hLs : L s = 0) (hLP : L P = 0) (hLQ : L Q = 0) :
    l ^ 5 * s -
        2 * (baseCoefficient p q l * (P + l ^ 6 * Q) +
          6 * l ^ 5 * q * vertical p q l s P Q) +
        chartEquation p q l *
          (horizontalDivergence p q l s P Q + L (vertical p q l s P Q) +
            2 * vertical p q l s P Q / l) = 0 := by
  have h12 : L (12 : K) = 0 := L.map_natCast 12
  have h18 : L (18 : K) = 0 := L.map_natCast 18
  have h54 : L (54 : K) = 0 := L.map_natCast 54
  simp only [vertical, horizontalDivergence, baseCoefficient, chartEquation,
    map_add, map_sub, map_neg, Derivation.leibniz, Derivation.leibniz_div,
    Derivation.leibniz_pow, smul_eq_mul, hLp, hLq, hLl, hLs, hLP, hLQ,
    h12, h18, h54, zero_mul, mul_zero, zero_add, add_zero, one_mul,
    mul_one, zero_sub, sub_zero]
  field_simp [hp, hq, hl]
  <;> ring

/-- An actual weighted-divergence primitive produces the complete strict
pole-two chart field, including its normal component and Jacobian correction. -/
theorem strict_chart_from_weighted_divergence
    {ι : Type*} [Fintype ι] (D : ι → Derivation ℤ K K) (L : Derivation ℤ K K)
    (W : ι → K) (p q l s P Q : K)
    (hp : p ≠ 0) (hq : q ≠ 0) (hl : l ≠ 0)
    (hDl : ∀ i, D i l = 0)
    (hP : (∑ i, W i * D i p) = P) (hQ : (∑ i, W i * D i q) = Q)
    (hw : (∑ i, D i (W i)) - 5 * P / (3 * p) - 4 * Q / (3 * q) = s)
    (hLp : L p = 0) (hLq : L q = 0) (hLl : L l = 1)
    (hLs : L s = 0) (hLP : L P = 0) (hLQ : L Q = 0) :
    l ^ 5 * s -
        2 * ((∑ i, (baseCoefficient p q l * W i) * D i (chartEquation p q l)) +
          vertical p q l s P Q * L (chartEquation p q l)) +
        chartEquation p q l *
          ((∑ i, D i (baseCoefficient p q l * W i)) + L (vertical p q l s P Q) +
            2 * vertical p q l s P Q / l) = 0 := by
  have hdir :
      (∑ i, (baseCoefficient p q l * W i) * D i (chartEquation p q l)) =
        baseCoefficient p q l * (P + l ^ 6 * Q) := by
    have heq (i : ι) : D i (chartEquation p q l) = D i p + l ^ 6 * D i q := by
      simp [chartEquation, Derivation.leibniz, Derivation.leibniz_pow, hDl]
    simp_rw [heq]
    calc
      _ = baseCoefficient p q l * ((∑ i, W i * D i p) + l ^ 6 * (∑ i, W i * D i q)) := by
        simp only [mul_add, Finset.sum_add_distrib, Finset.mul_sum]
        congr 1 <;> apply Finset.sum_congr rfl <;> intro i _ <;> ring
      _ = _ := by rw [hP, hQ]
  have hnormal : L (chartEquation p q l) = 6 * l ^ 5 * q := by
    simp [chartEquation, Derivation.leibniz, Derivation.leibniz_pow, hLp, hLq, hLl]
    <;> ring
  rw [hdir, hnormal, horizontal_divergence D W p q l s P Q hp hq hDl hP hQ hw]
  convert strict_chart_identity L p q l s P Q hp hq hl hLp hLq hLl hLs hLP hLQ using 1 <;> ring

end Field
end SplitTernaryHigherPole

#print axioms SplitTernaryHigherPole.strict_chart_identity
#print axioms SplitTernaryHigherPole.strict_chart_from_weighted_divergence
