import Mathlib.RingTheory.Derivation.Basic
import Mathlib.Tactic

/- Exact scalar identities for the fixed split-ternary-q2 construction.
Prepared with OpenAI Codex assistance for fqlx. These conversion
lemmas require a supplied residue primitive and do not assert its existence. -/

noncomputable section
namespace SplitEllipticSource

variable {K : Type*} [Field K] [CharZero K]

def residueOne (D : Derivation ℤ K K) (g A : K) : K :=
  D A/g - A*D g/g^2

def residueTwo (D : Derivation ℤ K K) (g A : K) : K :=
  (D (D A)/g^2 - (3*D A*D g + A*D (D g))/g^3 +
    3*A*(D g)^2/g^4)/2

/-- A pole-three source is the pole-two residue source of a rational
normal derivative. Its new denominator must be checked on the companion. -/
theorem residueTwo_eq_one (D : Derivation ℤ K K) (g A : K) (hg : g≠0) :
    residueOne D g (residueOne D g A/2) = residueTwo D g A := by
  have h2 : D (2 : K)=0 := D.map_natCast 2
  simp only [residueOne, residueTwo, Derivation.leibniz_div,
    Derivation.leibniz, Derivation.leibniz_pow, map_sub, h2,
    smul_eq_mul, nsmul_eq_mul]
  norm_num only
  field_simp [hg]
  ring

/-- For the cleared companion equation `7*(p+S^3+T^3)`, use the
pole-three numerator `49*h*S*T`. The resulting rational pole-two
numerator has weighted degree five, so it retains the radial weight. -/
theorem cleared_rational_source (D : Derivation ℤ K K) (h S T : K)
    (hT : T≠0) (hh : D h=0) (hS : D S=0) (hDT : D T=1) :
    residueOne D (21*T^2) (49*h*S*T)/2 = -7*h*S/(6*T^2) := by
  have h21 : D (21 : K)=0 := D.map_natCast 21
  have h49 : D (49 : K)=0 := D.map_natCast 49
  simp only [residueOne, Derivation.leibniz, Derivation.leibniz_pow,
    hh,hS,hDT,h21,h49,smul_eq_mul,nsmul_eq_mul]
  norm_num only
  field_simp [hT]
  ring

/-- Bind the rational companion numerator and its two cubic-coordinate
derivatives to the scalar source used by elliptic contraction. -/
theorem scalar_source_binding (h u a b : K) (hu : u≠0) (hb : b≠0) :
    (-7*h*a/(6*u*b^2))/(7*u^4) -
      (a*(-7*h/(6*u^2*b^2)) + b*(7*h*a/(3*u^2*b^3)))/(7*u^3) =
      -h*a/(3*u^5*b^2) := by
  field_simp [hu,hb]
  ring

/-- The elliptic correction interchanges two representatives of the same
nontrivial Fermat character. -/
theorem elliptic_correction (δ : Derivation ℤ K K) (a b : K)
    (ha : a≠0) (hb : b≠0) (hδa : δ a=b^2) (hδb : δ b= -a^2)
    (hfermat : a^3+b^3+1=0) :
    δ (a^2/b + b^2/a) = b/a^2 - a/b^2 := by
  simp only [map_add, Derivation.leibniz_div, Derivation.leibniz_pow,
    hδa, hδb, smul_eq_mul, nsmul_eq_mul]
  norm_num only
  field_simp [ha,hb]
  linear_combination (a^3-b^3)*hfermat

/-- Convert the rational companion source into the theta source required
by elliptic contraction. The other derivatives are ordinary base divergence. -/
theorem corrected_primitive (δ : Derivation ℤ K K)
    (a b α f c : K) (ha : a≠0) (hb : b≠0)
    (hδa : δ a=b^2) (hδb : δ b= -a^2) (hδα : δ α=0)
    (hfermat : a^3+b^3+1=0)
    (hf : δ f+c= -α*a/(3*b^2)) :
    δ (-3*f + α*(a^2/b+b^2/a)) - 3*c = α*(b/a^2) := by
  have h3 : δ (3 : K)=0 := δ.map_natCast 3
  have hn3 : δ (-3 : K)=0 := by rw [map_neg,h3,neg_zero]
  rw [map_add, Derivation.leibniz, Derivation.leibniz, hn3, hδα,
    elliptic_correction δ a b ha hb hδa hδb hfermat]
  simp only [smul_eq_mul, zero_mul, zero_add]
  rw [show δ f = -α*a/(3*b^2)-c by linear_combination hf]
  field_simp [ha,hb]
  ring

#print axioms residueTwo_eq_one
#print axioms cleared_rational_source
#print axioms scalar_source_binding
#print axioms elliptic_correction
#print axioms corrected_primitive
end SplitEllipticSource
