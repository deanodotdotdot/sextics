import Mathlib.Algebra.TrivSqZeroExt.Basic
import Mathlib.Tactic

/-! Polynomial identities to first order can be evaluated at any square-zero
parameter. This elementary ring homomorphism keeps all subsequent jet
arguments inside ordinary commutative algebra. -/
noncomputable section
namespace PolarCubicJetAlgebra
open TrivSqZeroExt
variable {R : Type*} [CommRing R]

def squareZeroEval (k : R) (hk : k^2=0) : TrivSqZeroExt R R →+* R where
  toFun a := a.fst+k*a.snd
  map_zero' := by simp
  map_one' := by simp
  map_add' := by intro a b; simp only [fst_add,snd_add]; ring
  map_mul' := by
    intro a b
    simp only [fst_mul,snd_mul,smul_eq_mul,op_smul_eq_smul]
    linear_combination -a.snd*b.snd*hk

@[simp] theorem squareZeroEval_mk (k : R) (hk : k^2=0) (a b : R) :
    squareZeroEval k hk (a,b)=a+k*b := rfl

end PolarCubicJetAlgebra
