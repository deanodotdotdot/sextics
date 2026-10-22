import Proposal.JacobianModel
import Mathlib.Algebra.Polynomial.Basic
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Matrix.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Tactic.NormNum
/-! Exact integral-incidence seed for mixed-polar. The coefficient method follows
hodgepodgeconjecture and fqlx's accepted constructions. This specialization was
prepared for benediamond with OpenAI Codex assistance. -/
noncomputable section
namespace CycleJacobianSeed
open Polynomial
abbrev K := ZMod 5
def r : Polynomial K := 2*X^2 + 3*X + 1
def x : Polynomial K := 2*X^4 + 2*X^3 + X^2 + X + 3
def y : Polynomial K := 4*X^6 + 4*X^5 + 3*X^4 + X^2 + 4*X + 2
def reducedEquation {R : Type*} [CommRing R] (r t x y : R) : R :=
  r^6 + 2*r^5*t + 3*r^4*t^2 + 4*r^3*t*x + 3*r*t^5 + r*t^3*x + t^6 + 3*x^3 + 2*y^2

lemma five_zero : (5 : Polynomial K)=0 := by
  simpa only [map_ofNat,map_zero] using congrArg (Polynomial.C : K →+* Polynomial K)
    (by decide : (5 : K)=0)
theorem seed_incidence : reducedEquation r X x y=0 := by
  have he : reducedEquation r X x y=5*(24*X^12 + 168*X^11 + 684*X^10 + 1736*X^9 + 2954*X^8 + 3506*X^7 + 3000*X^6 + 1904*X^5 + 919*X^4 + 326*X^3 + 88*X^2 + 29*X + 18) := by
    dsimp [reducedEquation,r,x,y]; ring
  rw [he,five_zero,zero_mul]
theorem specialized_equation (r t x y : Polynomial K) :
    CycleJacobian.equation 2 1 1 r t x y=reducedEquation r t x y := by
  have he : CycleJacobian.equation 2 1 1 r t x y-reducedEquation r t x y=
      5*(583*r^6 + 76118*r^5*t + 2628865*r^4*t^2 + 9819216*r^3*t^3 + 604*r^3*t*x + 14442180*r^2*t^4 + 1296*r^2*t^2*x + 9565081*r*t^5 + 691*r*t^3*x + 2388787*t^6 - 87*x^3 + 86*y^2) := by
    dsimp [CycleJacobian.equation,CycleJacobian.a8,CycleJacobian.b256,reducedEquation]; ring
  rw [five_zero,zero_mul] at he
  exact sub_eq_zero.mp he
theorem full_seed_incidence : CycleJacobian.equation 2 1 1 r X x y=0 := by
  rw [specialized_equation]; exact seed_incidence
def coefficientJacobian : Matrix (Fin 13) (Fin 13) K := ![
![0,0,0,0,0,0,3,0,0,0,0,0,0],
![1,0,1,0,0,0,1,3,0,0,0,0,0],
![1,1,3,1,0,0,4,1,3,0,0,0,0],
![0,1,4,3,1,0,0,4,1,3,0,0,0],
![3,0,4,4,3,1,2,0,4,1,3,0,0],
![1,3,3,4,4,3,1,2,0,4,1,3,0],
![0,1,3,3,4,4,1,1,2,0,4,1,3],
![2,0,1,3,3,4,0,1,1,2,0,4,1],
![2,2,4,1,3,3,0,0,1,1,2,0,4],
![0,2,1,4,1,3,0,0,0,1,1,2,0],
![1,0,0,1,4,1,0,0,0,0,1,1,2],
![2,1,0,0,1,4,0,0,0,0,0,1,1],
![0,2,0,0,0,1,0,0,0,0,0,0,1]
]
def inverseJacobian : Matrix (Fin 13) (Fin 13) K := ![
![0,4,3,1,0,1,3,1,3,3,3,1,1],
![2,4,2,3,4,2,2,3,3,0,2,3,2],
![0,0,0,1,2,4,2,1,1,1,4,1,0],
![4,0,0,1,3,1,1,3,2,2,0,0,1],
![0,4,0,0,1,3,1,1,3,2,2,0,0],
![0,0,4,3,1,3,4,4,4,1,4,0,0],
![2,0,0,0,0,0,0,0,0,0,0,0,0],
![1,4,4,1,1,0,0,1,2,2,1,1,3],
![0,1,4,2,2,3,1,3,4,0,4,4,1],
![4,0,1,0,4,1,0,2,4,0,4,0,4],
![2,4,0,1,0,4,1,0,2,4,0,4,0],
![2,2,4,2,0,3,3,3,2,4,2,2,4],
![1,2,2,1,1,3,2,0,0,4,2,4,2]
]
set_option maxRecDepth 100000 in
set_option maxHeartbeats 8000000 in
theorem inverse_product : coefficientJacobian*inverseJacobian=1 := by decide
end CycleJacobianSeed
