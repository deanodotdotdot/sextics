import Mathlib.Tactic.Ring

/-! Integral Weierstrass model of the holdout-moving-branch transitive cubic.
The historical API names are retained: a8 now means 4116*a₄ and b256 means
111132*b₆. Classical cubic invariant theory and the accepted cyclic construction
are credited to their authors. The transitive adaptation is due to fqlx; this
coefficient specialization was prepared for benediamond with OpenAI Codex assistance. -/
namespace CycleJacobian
section Ring
variable {K : Type*} [CommRing K]

def a8 (c₁ c₂ α r t : K) : K :=
  4116*c₁^3*c₂*r^2*t*(r+c₂^6*t) -
  1764*c₁*c₂^2*r*t*(r+c₁^6*t)*(r+c₂^6*t) -
  28*c₁^2*c₂^6*r^2*t^2

def b256 (c₁ c₂ α r t : K) : K :=
  -750141*(α*r+t)^2*(r+c₁^6*t)^2*(r+c₂^6*t)^2
  -111132*c₁^3*c₂^3*r^2*t*(α*r+t)^2*(r+c₂^6*t)
  -324*c₂^6*r*t^2*(r+c₁^6*t)^2*(r+c₂^6*t)
  -111132*c₁^3*r^2*t*(r+c₁^6*t)*(r+c₂^6*t)^2
  +2268*c₁^2*c₂^5*r^2*t^2*(r+c₁^6*t)*(r+c₂^6*t)
  -10584*c₁^4*c₂^4*r^3*t^2*(r+c₂^6*t)
  -24*c₁^3*c₂^9*r^3*t^3

def equation (c₁ c₂ α r t x y : K) : K :=
  111132*y^2-111132*x^3-27*a8 c₁ c₂ α r t*x-b256 c₁ c₂ α r t

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
