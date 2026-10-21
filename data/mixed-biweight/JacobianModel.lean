import Mathlib.Tactic.Ring

/-! Integral Weierstrass model of the mixed-biweight transitive cubic.
The historical API names are retained: a8 now means 216*a₄ and b256 means
5832*b₆. Classical cubic invariant theory and the accepted cyclic construction
are credited to their authors; this instance adaptation is by fqlx with Codex assistance. -/
namespace CycleJacobian
section Ring
variable {K : Type*} [CommRing K]

def a8 (c₁ c₂ α r t : K) : K :=
  27*c₁^3*c₂*r^2*t*(r+c₂^6*t) -
  108*c₁*c₂*r*t*(r+c₁^6*t)*(r+c₂^6*t) -
  2*c₁^2*c₂^4*r^2*t^2

def b256 (c₁ c₂ α r t : K) : K :=
  -39366*(α*r+t)^2*(r+c₁^6*t)^2*(r+c₂^6*t)^2
  -729*c₁^3*c₂^3*r^2*t*(α*r+t)^2*(r+c₂^6*t)
  -216*c₂^3*r*t^2*(r+c₁^6*t)^2*(r+c₂^6*t)
  -729*c₁^3*r^2*t*(r+c₁^6*t)*(r+c₂^6*t)^2
  +162*c₁^2*c₂^3*r^2*t^2*(r+c₁^6*t)*(r+c₂^6*t)
  -81*c₁^4*c₂^3*r^3*t^2*(r+c₂^6*t)
  -2*c₁^3*c₂^6*r^3*t^3

def equation (c₁ c₂ α r t x y : K) : K :=
  5832*y^2-5832*x^3-27*a8 c₁ c₂ α r t*x-b256 c₁ c₂ α r t

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
