import Mathlib.Tactic.Ring

/-! Integral Weierstrass model of the mixed-polar cubic.
The historical API names are retained: a8 means 8*a₄ and b256 means 432*b₆.
The incidence architecture follows the accepted cyclic and transitive constructions
of hodgepodgeconjecture and fqlx. This coefficient specialization was prepared for
benediamond with OpenAI Codex assistance. -/
namespace CycleJacobian
section Ring
variable {K : Type*} [CommRing K]

def a8 (c₁ c₂ α r t : K) : K :=
  c₁^3*c₂*r^2*t*(r+c₂^6*t) -
  4*c₁^4*c₂*r*t*(α*r+t)*(r+c₂^6*t)

def b256 (c₁ c₂ α r t : K) : K :=
  -2916*(α*r+t)^2*(r+c₁^6*t)^2*(r+c₂^6*t)^2
  -54*c₁^3*c₂^3*r^2*t*(α*r+t)^2*(r+c₂^6*t)
  +324*c₁^4*r*t*(α*r+t)*(r+c₁^6*t)*(r+c₂^6*t)^2
  -16*c₁^9*r*t^2*(α*r+t)*(r+c₂^6*t)^2
  -54*c₁^3*r^2*t*(r+c₁^6*t)*(r+c₂^6*t)^2
  +3*c₁^8*r^2*t^2*(r+c₂^6*t)^2

def equation (c₁ c₂ α r t x y : K) : K :=
  432*y^2-432*x^3-54*a8 c₁ c₂ α r t*x-b256 c₁ c₂ α r t

theorem a8_weight (c₁ c₂ α r t s : K) :
    a8 c₁ c₂ α (s*r) (s*t)=s^4*a8 c₁ c₂ α r t := by
  simp only [a8]; ring

theorem b256_weight (c₁ c₂ α r t s : K) :
    b256 c₁ c₂ α (s*r) (s*t)=s^6*b256 c₁ c₂ α r t := by
  simp only [b256]; ring

theorem equation_weight (c₁ c₂ α r t x y s : K) :
    equation c₁ c₂ α (s*r) (s*t) (s^2*x) (s^3*y)=s^6*equation c₁ c₂ α r t x y := by
  simp only [equation,a8_weight,b256_weight]; ring
end Ring
end CycleJacobian
