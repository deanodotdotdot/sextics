import Mathlib.Tactic.Ring

/-!
The integral Jacobian model for the fixed cycle-three target.

Work in progress: these algebraic identities are not a HasCertificate proof.
Classical ternary-cubic invariant theory is credited to its original authors;
the normalization follows Tom Fisher, Testing Equivalence of Ternary Cubics.
Prepared with OpenAI Codex assistance for hodgepodgeconjecture.
-/

namespace CycleJacobian

section Ring
variable {K : Type*} [CommRing K]

/-- Eight times the homogeneous Weierstrass coefficient a. -/
def a8 (c₁ c₂ α r t : K) : K :=
  r^2 * t * (c₁^2*c₂^3*(α*r+t) +
    c₁*c₂^2*(r+c₁^6*t) + c₁^3*c₂*(r+c₂^6*t))

/-- 256 times the homogeneous Weierstrass coefficient b. -/
def b256 (c₁ c₂ α r t : K) : K :=
  -1728*(α*r+t)^2*(r+c₁^6*t)^2*(r+c₂^6*t)^2
  -32*r^2*t*(c₁^3*c₂^3*(α*r+t)^2*(r+c₂^6*t) +
    c₂^3*(α*r+t)*(r+c₁^6*t)^2 +
    c₁^3*(r+c₁^6*t)*(r+c₂^6*t)^2)
  -48*r^2*t*c₁^2*c₂^2*(α*r+t)*(r+c₁^6*t)*(r+c₂^6*t)
  +r^4*t^2*c₁^4*c₂^4

/-- 256 times y²-x³-a*x-b. The fixed target uses α=1. -/
def equation (c₁ c₂ α r t x y : K) : K :=
  256*y^2 - 256*x^3 - 32*a8 c₁ c₂ α r t*x - b256 c₁ c₂ α r t

theorem a8_weight (c₁ c₂ α r t s : K) :
    a8 c₁ c₂ α (s*r) (s*t) = s^4 * a8 c₁ c₂ α r t := by
  simp only [a8]
  ring

theorem b256_weight (c₁ c₂ α r t s : K) :
    b256 c₁ c₂ α (s*r) (s*t) = s^6 * b256 c₁ c₂ α r t := by
  simp only [b256]
  ring

theorem equation_weight (c₁ c₂ α r t x y s : K) :
    equation c₁ c₂ α (s*r) (s*t) (s^2*x) (s^3*y) =
      s^6 * equation c₁ c₂ α r t x y := by
  simp only [equation, a8_weight, b256_weight]
  ring

end Ring
end CycleJacobian
