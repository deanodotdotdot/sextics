import Proposal.JacobianModel

/-! Exact polynomial identities for the physical paired-sign cubic reduction.
The six physical coordinates are X0,X1,X2,Y0,Y1,Y2. The doubled equation avoids
all division, and the auxiliary coefficient is specialized to one for the
fixed target. This file does not identify differential residues or claim the
protected certificate. Classical invariant normalizations follow Tom Fisher
and SageMath, as credited in the accompanying research discussion.
Prepared with OpenAI Codex assistance for hodgepodgeconjecture. -/
namespace CycleCubic
variable {K : Type*} [CommRing K]
def cubic (a b c d e f x y z : K) : K :=
  a*x^3+b*y^3+c*z^3+d*x^2*y+e*y^2*z+f*z^2*x
/-- Twice the immutable physical sextic. -/
def doubledPhysical (x₀ x₁ x₂ y₀ y₁ y₂ : K) : K :=
  2*(x₀^6+x₁^6+x₂^6+y₀^6+y₁^6+y₂^6)+
    x₀^3*x₁*y₀*y₁+x₁^3*x₂*y₁*y₂+x₂^3*x₀*y₂*y₀
lemma paired_sign_reduction (x₀ x₁ x₂ a₀ a₁ a₂ : K) :
    doubledPhysical x₀ x₁ x₂ (a₀*x₀) (a₁*x₁) (a₂*x₂)=
      cubic (2*(1+a₀^6)) (2*(1+a₁^6)) (2*(1+a₂^6))
        (a₀*a₁) (a₁*a₂) (a₂*a₀) (x₀^2) (x₁^2) (x₂^2) := by
  simp only [doubledPhysical,cubic]
  ring
lemma paired_sign_source (x₀ a₀ : K) : x₀^3*(a₀*x₀)^3=a₀^3*(x₀^2)^3 := by ring
/-- The coefficient invariants with c4=-48*s4 and c6=216*s6. -/
def s4 (a b c d e f : K) : K := a*e^2*f+b*d*f^2+c*d^2*e
def s6 (a b c d e f : K) : K :=
  27*a^2*b^2*c^2+4*a^2*c*e^3+4*a*b^2*f^3+6*a*b*c*d*e*f+4*b*c^2*d^3-d^2*e^2*f^2
lemma model_a8 (c₁ c₂ α b : K) :
    s4 (2*(α+b^3)) (2*(1+c₁^6*b^3)) (2*(1+c₂^6*b^3))
      (b*c₁) (b*c₁*c₂) (b*c₂)=2*CycleJacobian.a8 c₁ c₂ α 1 (b^3) := by
  simp only [s4,CycleJacobian.a8]
  ring
lemma model_b256 (c₁ c₂ α b : K) :
    -s6 (2*(α+b^3)) (2*(1+c₁^6*b^3)) (2*(1+c₂^6*b^3))
      (b*c₁) (b*c₁*c₂) (b*c₂)=CycleJacobian.b256 c₁ c₂ α 1 (b^3) := by
  simp only [s6,CycleJacobian.b256]
  ring
lemma ratio_specialization (c₁ c₂ v x y r : K) :
    cubic (2*(1+v^6)) (2*(1+(c₁*v)^6)) (2*(1+(c₂*v)^6))
      (v*(c₁*v)) ((c₁*v)*(c₂*v)) ((c₂*v)*v) (r*x) (r*y) r=
    r^3*cubic (2*(1+(v^2)^3)) (2*(1+c₁^6*(v^2)^3)) (2*(1+c₂^6*(v^2)^3))
      (v^2*c₁) (v^2*c₁*c₂) (v^2*c₂) x y 1 := by
  simp only [cubic]
  ring
#print axioms model_b256
end CycleCubic
