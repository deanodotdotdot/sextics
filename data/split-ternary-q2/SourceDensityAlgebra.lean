import Mathlib.Tactic

/- Scalar assembly of the normal source jets. Prepared with OpenAI Codex
assistance for fqlx. -/
namespace SplitSourceDensityAlgebra
variable {K : Type*} [Field K]

theorem source_jets (g A A₁ A₂ l m r₀ r₁ r₂ a d₀ d₁ h : K)
    (hg : g≠0) (h₀ : A=g*r₀)
    (h₁ : A₁/g-A*l/g^2=r₁+d₀)
    (h₂ : A₂/g-(A₁*l+A*m)/g^2+A*l^2/g^3=r₂+a*r₁+d₁+h/2) :
    A₁=l*r₀+g*(r₁+d₀) ∧
    A₂=m*r₀+l*(r₁+d₀)+g*(r₂+a*r₁+d₁+h/2) := by
  have hfirst : A₁=l*r₀+g*(r₁+d₀) := by
    calc
      A₁=g*(A₁/g-A*l/g^2)+A*l/g := by field_simp [hg]; ring
      _=g*(r₁+d₀)+A*l/g := by rw [h₁]
      _=l*r₀+g*(r₁+d₀) := by rw [h₀]; field_simp [hg]; ring
  refine ⟨hfirst,?_⟩
  calc
    A₂=g*(A₂/g-(A₁*l+A*m)/g^2+A*l^2/g^3)+
        (A₁*l+A*m)/g-A*l^2/g^2 := by field_simp [hg]; ring
    _=g*(r₂+a*r₁+d₁+h/2)+(A₁*l+A*m)/g-A*l^2/g^2 := by rw [h₂]
    _=m*r₀+l*(r₁+d₀)+g*(r₂+a*r₁+d₁+h/2) := by
      rw [h₀,hfirst]
      field_simp [hg]
      ring

#print axioms source_jets
end SplitSourceDensityAlgebra
