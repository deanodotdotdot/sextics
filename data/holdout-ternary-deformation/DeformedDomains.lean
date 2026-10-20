import HodgeComputer.Constructions.HoldoutCover.HypersurfaceDomain

/-!
The ternary deformation preserves the Eisenstein specializations of the
quotient and endpoint rings. This adapts the target-specific domain argument
of fqlx's accepted holdout construction, reusing its generic lemmas.
Prepared with OpenAI Codex assistance for hodgepodgeconjecture.
-/
noncomputable section
namespace DeformedGeometry
open Polynomial HoldoutConstruction
variable {R : Type*} [CommRing R]

/-- The four coefficient variables are x1,x2,S,P. The physical specialization
is d=1/14. Keeping d as a ring parameter avoids dividing in an integral model. -/
def quotientPolynomial (d a b : R) : (MvPolynomial (Fin 4) R)[X] :=
  X^6 + (C (MvPolynomial.C d * MvPolynomial.X 0)*X^5 +
    C (MvPolynomial.C a * MvPolynomial.X 0 * MvPolynomial.X 3)*X^3 +
    C (MvPolynomial.C d * MvPolynomial.X 1^5)*X +
    C (MvPolynomial.X 0^6 + MvPolynomial.X 1^6 +
      2*MvPolynomial.C d*MvPolynomial.X 0^5*MvPolynomial.X 1 +
      MvPolynomial.C b*MvPolynomial.X 0^3*MvPolynomial.X 1*MvPolynomial.X 3 +
      MvPolynomial.X 2^3-3*MvPolynomial.X 2*MvPolynomial.X 3^2))

lemma quotientPolynomial_monic (d a b : R) : (quotientPolynomial d a b).Monic := by
  apply monic_X_pow_add
  compute_degree <;> norm_num

lemma quotientPolynomial_specialization (d a b : R) :
    (quotientPolynomial d a b).map HoldoutConstruction.quotientSpecialization =
      (X : (R[X])[X])^6+C (X^3-3*X) := by
  simp [quotientPolynomial,HoldoutConstruction.quotientSpecialization]

lemma quotientPolynomial_irreducible [IsDomain R] [CharZero R] (d a b : R) :
    Irreducible (quotientPolynomial d a b) := by
  apply (quotientPolynomial_monic d a b).irreducible_of_irreducible_map
    HoldoutConstruction.quotientSpecialization
  rw [quotientPolynomial_specialization]
  exact irreducible_power_add_constant (X^3-3*X : R[X])
    (by simp) (by norm_num) 6 (by decide)

lemma quotientPolynomial_map {T : Type*} [CommRing T] (f : R →+* T) (d a b : R) :
    (quotientPolynomial d a b).map (MvPolynomial.map f)=
      quotientPolynomial (f d) (f a) (f b) := by
  simp [quotientPolynomial,map_ofNat]

lemma quotient_domain [IsDomain R] [CharZero R] (d a b : R) :
    IsDomain (AdjoinRoot (quotientPolynomial d a b)) := by
  let f : R →+* FractionRing R := algebraMap R (FractionRing R)
  have hf : Function.Injective f := IsFractionRing.injective R (FractionRing R)
  have hm : IsDomain (AdjoinRoot ((quotientPolynomial d a b).map (MvPolynomial.map f))) := by
    rw [quotientPolynomial_map]
    exact AdjoinRoot.isDomain_of_prime (quotientPolynomial_irreducible (f d) (f a) (f b)).prime
  letI := hm
  exact adjoinRoot_isDomain_of_monic_map (MvPolynomial.map f)
    (MvPolynomial.map_injective f hf) _ (quotientPolynomial_monic d a b)

/-- Endpoint parameters are x2,S,P, with x1=0. -/
def endpointPolynomial (d : R) : (MvPolynomial (Fin 3) R)[X] :=
  X^6 + (C (MvPolynomial.C d*MvPolynomial.X 0^5)*X +
    C (MvPolynomial.X 0^6+MvPolynomial.X 1^3-3*MvPolynomial.X 1*MvPolynomial.X 2^2))

lemma endpointPolynomial_monic (d : R) : (endpointPolynomial d).Monic := by
  apply monic_X_pow_add
  compute_degree <;> norm_num

lemma endpointPolynomial_irreducible [IsDomain R] [CharZero R] (d : R) :
    Irreducible (endpointPolynomial d) := by
  apply (endpointPolynomial_monic d).irreducible_of_irreducible_map
    (MvPolynomial.eval₂Hom C ![0,X,1])
  have he : (endpointPolynomial d).map (MvPolynomial.eval₂Hom C ![0,X,1]) =
      (X : (R[X])[X])^6+C (X^3-3*X) := by
    simp [endpointPolynomial]
  rw [he]
  exact irreducible_power_add_constant (X^3-3*X : R[X])
    (by simp) (by norm_num) 6 (by decide)

#print axioms quotientPolynomial_irreducible
#print axioms quotient_domain
#print axioms endpointPolynomial_irreducible
end DeformedGeometry
