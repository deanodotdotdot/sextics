import Mathlib.RingTheory.Localization.Away.Basic
import Mathlib.Analysis.Complex.Basic
import Mathlib.FieldTheory.IsAlgClosed.AlgebraicClosure
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic

/-!
The arithmetic coefficient ring for the fixed coefficient 5/7. Both the
complex target and the characteristic-five seed receive the same ring
Z[1/7]. The complex map is injective, which is essential to the flat
generic-fiber argument.
-/

noncomputable section
namespace ReflectionCoupledFano.Arithmetic

abbrev Base := Localization.Away (7 : ℤ)

def coupling : Base := 5 * IsLocalization.Away.invSelf (S := Base) (7 : ℤ)

def complexMap : Base →+* ℂ :=
  IsLocalization.Away.lift (7 : ℤ) (g := Int.castRingHom ℂ) (by norm_num)

@[simp] theorem complexMap_int (z : ℤ) :
    complexMap (algebraMap ℤ Base z) = z := by
  exact IsLocalization.Away.lift_eq _ _ _

theorem complexMap_injective : Function.Injective complexMap := by
  apply (IsLocalization.injective_iff_map_algebraMap_eq
    (Submonoid.powers (7 : ℤ)) complexMap).mpr
  intro x y
  constructor
  · exact congrArg complexMap
  · intro h
    have hxy : x = y := Int.cast_injective (by simpa using h : (x : ℂ) = (y : ℂ))
    exact congrArg (algebraMap ℤ Base) hxy

@[simp] theorem complexMap_coupling : complexMap coupling = (5/7 : ℂ) := by
  have h := congrArg complexMap (IsLocalization.Away.mul_invSelf (S := Base) (7 : ℤ))
  simp only [map_mul, complexMap_int, map_one] at h
  unfold coupling
  rw [map_mul, map_ofNat]
  have hi : complexMap (IsLocalization.Away.invSelf (S := Base) (7 : ℤ)) = (7 : ℂ)⁻¹ := by
    apply (mul_left_cancel₀ (by norm_num : (7 : ℂ) ≠ 0))
    simpa using h
  rw [hi, div_eq_mul_inv]

section SpecialFiber
variable (T : Type*) [Field T] [CharP T 5]

theorem seven_ne_zero : (7 : T) ≠ 0 :=
  (CharP.cast_eq_zero_iff T 5 7).not.mpr (by decide)

def specialMap : Base →+* T :=
  IsLocalization.Away.lift (7 : ℤ) (g := Int.castRingHom T)
    (by simpa using (isUnit_iff_ne_zero.mpr (seven_ne_zero T)))

@[simp] theorem specialMap_int (z : ℤ) :
    specialMap T (algebraMap ℤ Base z) = z := by
  exact IsLocalization.Away.lift_eq _ _ _

@[simp] theorem specialMap_coupling : specialMap T coupling = 0 := by
  have h5 : (5 : T) = 0 := CharP.cast_eq_zero T 5
  simp only [coupling, map_mul, map_ofNat, h5, zero_mul]

end SpecialFiber
end ReflectionCoupledFano.Arithmetic

#print axioms ReflectionCoupledFano.Arithmetic.complexMap_injective
#print axioms ReflectionCoupledFano.Arithmetic.specialMap_coupling
