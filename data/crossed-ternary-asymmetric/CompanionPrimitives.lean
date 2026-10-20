import Proposal.MovingConic
import HodgeComputer.Constructions.HoldoutCover.ResidueClearing
import HodgeComputer.Constructions.HoldoutCover.ResiduePiolaPullback
import Mathlib.RingTheory.Trace.Basic
import Mathlib.Tactic

/- Prepared with OpenAI Codex assistance for contributor 1337isnot1337.
See solution.md for the construction, provenance, and prior-work credit. -/

/- Source component: FanoRadialSources. -/
section

noncomputable section
set_option backward.isDefEq.respectTransparency false
namespace CrossedFanoRadial
open HoldoutConstruction CrossedRadialResidue CrossedConicIncidence
open scoped BigOperators
local instance : Algebra ℤ CrossedFano.FunctionField := Ring.toIntAlgebra _
local instance : Algebra ℤ AffineField := Ring.toIntAlgebra _
local instance : Algebra ℤ RadialField := Ring.toIntAlgebra _

@[simp] lemma radial_C_five : RatFunc.C (5 : AffineField)=(5 : RadialField) := map_natCast _ 5
@[simp] lemma radial_C_seven : RatFunc.C (7 : AffineField)=(7 : RadialField) := map_natCast _ 7
@[simp] lemma radial_C_ten : RatFunc.C (10 : AffineField)=(10 : RadialField) := map_natCast _ 10
@[simp] lemma radial_C_42 : RatFunc.C (42 : AffineField)=(42 : RadialField) := map_natCast _ 42
@[simp] lemma radial_C_200 : RatFunc.C (200 : AffineField)=(200 : RadialField) := map_natCast _ 200
@[simp] lemma radial_C_210 : RatFunc.C (210 : AffineField)=(210 : RadialField) := map_natCast _ 210

def clearNormal : AffineField := gradient
  ![CrossedFanoAffine.coordinate 0,CrossedFanoAffine.normal,1,
    CrossedFanoAffine.coordinate 1,CrossedFanoAffine.coordinate 2] 1

lemma coneEvaluation_normal :
    coneEvaluation (MvPolynomial.pderiv 0 CrossedFano.hypersurface)=
      RatFunc.X^5*RatFunc.C clearNormal := by
  have hp : MvPolynomial.pderiv 0 CrossedFano.hypersurface=
      42*MvPolynomial.X 0^5+5*(MvPolynomial.X 1^5+MvPolynomial.X 1^3*MvPolynomial.X 2^2+
        MvPolynomial.X 1*MvPolynomial.X 2^4+10*MvPolynomial.X 1*MvPolynomial.X 0^4) := by
    rw [← integerPartial_apply,CrossedFano.hypersurface_partial]
    rfl
  rw [hp]
  have h42 : coneEvaluation (42 : MvPolynomial (Fin 5) ℂ)=(42 : RadialField) := map_natCast _ 42
  have h5 : coneEvaluation (5 : MvPolynomial (Fin 5) ℂ)=(5 : RadialField) := map_natCast _ 5
  have h10 : coneEvaluation (10 : MvPolynomial (Fin 5) ℂ)=(10 : RadialField) := map_natCast _ 10
  simp only [map_add,map_mul,map_pow,h42,h5,h10,coneEvaluation_X]
  simp [gradient,coneCoordinate,clearNormal]
  ring

lemma clearNormal_ne_zero : clearNormal≠0 := by
  have h := (_root_.map_ne_zero coneFieldMap).mpr CrossedFano.normal_ne_zero
  change coneEvaluation (MvPolynomial.pderiv 0 CrossedFano.hypersurface)≠0 at h
  rw [coneEvaluation_normal] at h
  intro hz
  apply h
  rw [hz,map_zero,mul_zero]

def clearSecondNormal : AffineField :=
  210*CrossedFanoAffine.normal^4+200*CrossedFanoAffine.coordinate 0*CrossedFanoAffine.normal^3

lemma hessian_polynomial : MvPolynomial.pderiv (R:=ℂ) (0 : Fin 5)
    (MvPolynomial.pderiv 0 CrossedFano.hypersurface)=
    210*MvPolynomial.X 0^4+200*MvPolynomial.X 1*MvPolynomial.X 0^3 := by
  change integerPartial 0 (integerPartial 0 CrossedFano.hypersurface)=_
  rw [CrossedFano.hypersurface_partial]
  have h42 : integerPartial (R:=ℂ) (0 : Fin 5) (42 : MvPolynomial (Fin 5) ℂ)=0 :=
    (integerPartial 0).map_natCast 42
  have h5 : integerPartial (R:=ℂ) (0 : Fin 5) (5 : MvPolynomial (Fin 5) ℂ)=0 :=
    (integerPartial 0).map_natCast 5
  have h10 : integerPartial (R:=ℂ) (0 : Fin 5) (10 : MvPolynomial (Fin 5) ℂ)=0 :=
    (integerPartial 0).map_natCast 10
  simp only [integerPartial_apply] at h42 h5 h10
  simp [gradient,Derivation.leibniz,Derivation.leibniz_pow,smul_eq_mul,h42,h5,h10]
  ring

lemma coneEvaluation_hessian : coneEvaluation (MvPolynomial.pderiv 0
    (MvPolynomial.pderiv 0 CrossedFano.hypersurface))=RatFunc.X^4*RatFunc.C clearSecondNormal := by
  rw [hessian_polynomial]
  have h210 : coneEvaluation (210 : MvPolynomial (Fin 5) ℂ)=(210 : RadialField) := map_natCast _ 210
  have h200 : coneEvaluation (200 : MvPolynomial (Fin 5) ℂ)=(200 : RadialField) := map_natCast _ 200
  simp only [map_add,map_mul,map_pow,h210,h200,coneEvaluation_X]
  simp [coneCoordinate,clearSecondNormal]
  ring

def firstSource : MvPolynomial (Fin 5) ℂ := 7*MvPolynomial.X 1^4*MvPolynomial.X 0
def secondSource : MvPolynomial (Fin 5) ℂ := 7*MvPolynomial.X 1*MvPolynomial.X 3*MvPolynomial.X 4

def affineFirstSource : AffineField :=
  7*CrossedFanoAffine.coordinate 0^4*CrossedFanoAffine.normal
def affineSecondSource : AffineField :=
  7*CrossedFanoAffine.coordinate 0*CrossedFanoAffine.coordinate 1*CrossedFanoAffine.coordinate 2

lemma firstSource_partial : MvPolynomial.pderiv 0 firstSource=7*MvPolynomial.X 1^4 := by
  have h7 : MvPolynomial.pderiv (R:=ℂ) (0 : Fin 5) (7 : MvPolynomial (Fin 5) ℂ)=0 :=
    (MvPolynomial.pderiv 0).map_natCast 7
  simp [firstSource,MvPolynomial.pderiv_mul,MvPolynomial.pderiv_pow,h7]
lemma secondSource_partial : MvPolynomial.pderiv 0 secondSource=0 := by
  have h7 : MvPolynomial.pderiv (R:=ℂ) (0 : Fin 5) (7 : MvPolynomial (Fin 5) ℂ)=0 :=
    (MvPolynomial.pderiv 0).map_natCast 7
  simp [secondSource,MvPolynomial.pderiv_mul,MvPolynomial.pderiv_pow,h7]

lemma coneEvaluation_firstSource : coneEvaluation firstSource=RatFunc.X^5*RatFunc.C affineFirstSource := by
  have h7 : coneEvaluation (7 : MvPolynomial (Fin 5) ℂ)=(7 : RadialField) := map_natCast _ 7
  simp only [firstSource,map_mul,map_pow,h7,coneEvaluation_X]
  simp [coneCoordinate,affineFirstSource]
  ring

lemma coneEvaluation_secondSource : coneEvaluation secondSource=RatFunc.X^5*RatFunc.C affineSecondSource := by
  have h7 : coneEvaluation (7 : MvPolynomial (Fin 5) ℂ)=(7 : RadialField) := map_natCast _ 7
  simp only [secondSource,map_mul,map_pow,h7,coneEvaluation_X]
  simp [coneCoordinate,affineSecondSource]
  ring

lemma coneEvaluation_firstPartial : coneEvaluation (MvPolynomial.pderiv 0 firstSource)=
    RatFunc.X^4*RatFunc.C (7*CrossedFanoAffine.coordinate 0^4) := by
  rw [firstSource_partial]
  have h7 : coneEvaluation (7 : MvPolynomial (Fin 5) ℂ)=(7 : RadialField) := map_natCast _ 7
  simp only [map_mul,map_pow,h7,coneEvaluation_X]
  simp [coneCoordinate]
  ring

lemma radial_source_fraction (ρ g k A B : RadialField) (hρ : ρ≠0) (hg : g≠0) :
    -(ρ^4*B/(ρ^5*g)-(ρ^5*A)*(ρ^4*k)/(ρ^5*g)^2)=
      (-(B/g-A*k/g^2))/ρ := by
  field_simp <;> ring

lemma cone_residue_solution_radial (A : MvPolynomial (Fin 5) ℂ) :
    ∃ w : Fin 4 → RadialField,
      residueDivergence radialDerivation (RatFunc.X^5*RatFunc.C clearNormal) w=
        -(coneEvaluation (MvPolynomial.pderiv 0 A)/(RatFunc.X^5*RatFunc.C clearNormal)-
          coneEvaluation A*(RatFunc.X^4*RatFunc.C clearSecondNormal)/
            (RatFunc.X^5*RatFunc.C clearNormal)^2) := by
  obtain ⟨w,hw⟩ := CrossedFixedConic.companion_residue_solution A
  refine ⟨fun i => coneFieldMap (w i),?_⟩
  have hm := residueDivergence_map coneFieldMap CrossedFano.tangent radialDerivation
    radialDerivation_compatible (CrossedFano.residueMap (MvPolynomial.pderiv 0 CrossedFano.hypersurface)) w
  rw [hw] at hm
  simp only [map_neg,map_sub,map_div₀,map_mul,map_pow] at hm
  change residueDivergence radialDerivation
    (coneEvaluation (MvPolynomial.pderiv 0 CrossedFano.hypersurface)) (fun i => coneFieldMap (w i))=
      -(coneEvaluation (MvPolynomial.pderiv 0 A)/coneEvaluation (MvPolynomial.pderiv 0 CrossedFano.hypersurface)-
        coneEvaluation A*coneEvaluation (MvPolynomial.pderiv 0 (MvPolynomial.pderiv 0 CrossedFano.hypersurface))/
          (coneEvaluation (MvPolynomial.pderiv 0 CrossedFano.hypersurface))^2) at hm
  rw [coneEvaluation_normal,coneEvaluation_hessian] at hm
  exact hm

theorem affine_first_residue_solution :
    ∃ v : Fin 3 → AffineField,
      residueDivergence CrossedFanoAffine.tangent clearNormal v=
        -((7*CrossedFanoAffine.coordinate 0^4)/clearNormal-
          affineFirstSource*clearSecondNormal/clearNormal^2) := by
  obtain ⟨w,hw⟩ := cone_residue_solution_radial firstSource
  rw [coneEvaluation_firstSource,coneEvaluation_firstPartial] at hw
  have hρ : (RatFunc.X : RadialField)≠0 := CrossedRationalResidue.X_ne_zero
  have hg : (RatFunc.C clearNormal : RadialField)≠0 := by
    simpa only [map_zero] using RatFunc.C_injective.ne clearNormal_ne_zero
  rw [radial_source_fraction _ _ _ _ _ hρ hg] at hw
  have hr : -(RatFunc.C (7*CrossedFanoAffine.coordinate 0^4)/RatFunc.C clearNormal-
      RatFunc.C affineFirstSource*RatFunc.C clearSecondNormal/(RatFunc.C clearNormal)^2)=
      RatFunc.C (-((7*CrossedFanoAffine.coordinate 0^4)/clearNormal-
        affineFirstSource*clearSecondNormal/clearNormal^2)) := by
    simp
  rw [hr] at hw
  exact residue_solution_descends_radial CrossedFanoAffine.tangent CrossedFanoAffine.coordinate
    (fun i => by simpa using CrossedFanoAffine.tangent_coordinate i i)
    clearNormal clearNormal_ne_zero _ w hw

theorem affine_second_residue_solution :
    ∃ v : Fin 3 → AffineField,
      residueDivergence CrossedFanoAffine.tangent clearNormal v=
        affineSecondSource*clearSecondNormal/clearNormal^2 := by
  obtain ⟨w,hw⟩ := cone_residue_solution_radial secondSource
  rw [coneEvaluation_secondSource,secondSource_partial,map_zero] at hw
  have hρ : (RatFunc.X : RadialField)≠0 := CrossedRationalResidue.X_ne_zero
  have hg : (RatFunc.C clearNormal : RadialField)≠0 := by
    simpa only [map_zero] using RatFunc.C_injective.ne clearNormal_ne_zero
  have hs : -(0/(RatFunc.X^5*RatFunc.C clearNormal)-
      (RatFunc.X^5*RatFunc.C affineSecondSource)*(RatFunc.X^4*RatFunc.C clearSecondNormal)/
        (RatFunc.X^5*RatFunc.C clearNormal)^2)=
      RatFunc.C (affineSecondSource*clearSecondNormal/clearNormal^2)/RatFunc.X := by
    simp only [map_div₀,map_mul,map_pow]
    field_simp
    ring
  rw [hs] at hw
  exact residue_solution_descends_radial CrossedFanoAffine.tangent CrossedFanoAffine.coordinate
    (fun i => by simpa using CrossedFanoAffine.tangent_coordinate i i)
    clearNormal clearNormal_ne_zero _ w hw

end CrossedFanoRadial
end
end

/- Source component: AffinePrimitiveData. -/
section

/- The representative construction here is the first, pre-legality part of
   fqlx's maintained residue_solution_clearing, retaining exactly the normal
   identity and zero reduced divergence needed by the elliptic jet calculation. -/
noncomputable section
namespace CrossedAffinePrimitiveData
open HoldoutConstruction
open scoped BigOperators
variable {R K : Type*} [CommRing R] [Field K]

lemma tangent_formula_from_coordinates {n : ℕ}
    (θ : MvPolynomial (Fin (n+1)) R →+* K) (f : MvPolynomial (Fin (n+1)) R)
    (hf : θ f=0) (hg : θ (MvPolynomial.pderiv 0 f)≠0)
    (D : Derivation ℤ K K) (i : Fin n)
    (hC : ∀ r,D (θ (MvPolynomial.C r))=0)
    (hX : ∀ j : Fin n,D (θ (MvPolynomial.X j.succ))=if j=i then 1 else 0)
    (p : MvPolynomial (Fin (n+1)) R) :
    D (θ p)=θ (MvPolynomial.pderiv i.succ p)-
      θ (MvPolynomial.pderiv i.succ f)/θ (MvPolynomial.pderiv 0 f)*θ (MvPolynomial.pderiv 0 p) := by
  have he := derivation_polynomial_ringHom_chain D θ hC f
  rw [hf,map_zero] at he
  simp only [Fin.sum_univ_succ,hX,mul_ite,mul_one,mul_zero,Finset.sum_ite_eq',Finset.mem_univ,ite_true] at he
  have hn : D (θ (MvPolynomial.X 0))= -θ (MvPolynomial.pderiv i.succ f)/θ (MvPolynomial.pderiv 0 f) := by
    field_simp
    linear_combination -he
  rw [derivation_polynomial_ringHom_chain D θ hC p]
  simp only [Fin.sum_univ_succ,hX,mul_ite,mul_one,mul_zero,Finset.sum_ite_eq',Finset.mem_univ,ite_true,hn]
  ring

theorem ambient_data {ι : Type*} [Fintype ι]
    (ρ : R →+* K) (Δ₀ : Derivation ℤ R R) (Δ : ι → Derivation ℤ R R)
    (E : ι → Derivation ℤ K K) (f A : R) (w : ι → K)
    (hg : ρ (Δ₀ f)≠0)
    (mixed : ∀ i,Δ i (Δ₀ f)=Δ₀ (Δ i f))
    (compatible : ∀ i p,E i (ρ p)=ρ (Δ i p)-ρ (Δ i f)/ρ (Δ₀ f)*ρ (Δ₀ p))
    (representatives : ∃ d : R,∃ n : ι → R,ρ d≠0 ∧ ∀ i,ρ (n i)=ρ d*w i)
    (equation : residueDivergence E (ρ (Δ₀ f)) w=
      -(ρ (Δ₀ A)/ρ (Δ₀ f)-ρ A*ρ (Δ₀ (Δ₀ f))/(ρ (Δ₀ f))^2)) :
    ∃ D N₀ : R,∃ N : ι → R,
      ρ D≠0 ∧ (N₀*Δ₀ f+∑ i,N i*Δ i f=A*D) ∧ ρ (residueDivNum Δ₀ Δ D N₀ N)=0 := by
  obtain ⟨d,n,hd,hn⟩ := representatives
  let D := Δ₀ f*d
  let N₀ := A*d-∑ i,Δ i f*n i
  let N : ι → R := fun i => Δ₀ f*n i
  have hD : ρ D≠0 := by
    change ρ (Δ₀ f*d)≠0
    rw [map_mul]
    exact mul_ne_zero hg hd
  have hN (i : ι) : ρ (N i)=ρ D*w i := by
    simp only [N,D,map_mul,hn]
    ring
  have hnormal : N₀*Δ₀ f+∑ i,N i*Δ i f=A*D :=
    cleared_normal_source A d (Δ₀ f) (fun i => Δ i f) n
  have heq : (ρ (Δ₀ A)*ρ (Δ₀ f)-ρ A*ρ (Δ₀ (Δ₀ f)))/(ρ (Δ₀ f))^2+
      ∑ i,(E i (w i)-w i*E i (ρ (Δ₀ f))/ρ (Δ₀ f))=0 := by
    have he : residueDivergence E (ρ (Δ₀ f)) w=
        ∑ i,(E i (w i)-w i*E i (ρ (Δ₀ f))/ρ (Δ₀ f)) := by
      simp only [residueDivergence,fieldDivergence,Finset.sum_sub_distrib,Finset.sum_div]
    rw [← he,equation]
    field_simp
    ring
  have hdiv := residue_divergence_identity ρ Δ₀ Δ E A D N₀ (Δ₀ f) N
    (fun i => Δ i f) w hg mixed compatible hN hnormal
  rw [heq,mul_zero] at hdiv
  exact ⟨D,N₀,N,hD,hnormal,hdiv⟩

end CrossedAffinePrimitiveData
end
end

/- Source component: FanoAffinePrimitiveData. -/
section

noncomputable section
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 200000
namespace CrossedFanoAffineData
open Polynomial HoldoutConstruction CrossedConicIncidence
open scoped BigOperators
abbrev Poly := MvPolynomial (Fin 4) ℂ
abbrev K := CrossedFanoAffine.FunctionField
local instance : Algebra ℤ K := Ring.toIntAlgebra _

def equation : Poly := H ![MvPolynomial.X 1,MvPolynomial.X 0,1,MvPolynomial.X 2,MvPolynomial.X 3]
def evaluation : Poly →+* K := MvPolynomial.eval₂Hom (algebraMap ℂ K)
  ![CrossedFanoAffine.normal,CrossedFanoAffine.coordinate 0,CrossedFanoAffine.coordinate 1,
    CrossedFanoAffine.coordinate 2]

@[simp] lemma evaluation_C (c : ℂ) : evaluation (MvPolynomial.C c)=algebraMap ℂ K c :=
  MvPolynomial.eval₂Hom_C _ _ c
@[simp] lemma evaluation_X_zero : evaluation (MvPolynomial.X 0)=CrossedFanoAffine.normal := by
  rw [evaluation,MvPolynomial.eval₂Hom_X']
  rfl
lemma evaluation_X_succ (j : Fin 3) : evaluation (MvPolynomial.X j.succ)=CrossedFanoAffine.coordinate j := by
  rw [evaluation,MvPolynomial.eval₂Hom_X']
  fin_cases j <;> rfl

@[simp] lemma evaluation_X_one : evaluation (MvPolynomial.X 1)=CrossedFanoAffine.coordinate 0 :=
  evaluation_X_succ 0
@[simp] lemma evaluation_X_two : evaluation (MvPolynomial.X 2)=CrossedFanoAffine.coordinate 1 :=
  evaluation_X_succ 1
@[simp] lemma evaluation_X_three : evaluation (MvPolynomial.X 3)=CrossedFanoAffine.coordinate 2 :=
  evaluation_X_succ 2

lemma evaluation_residue : evaluation=CrossedFanoAffine.residueMap := by
  apply MvPolynomial.ringHom_ext
  · intro c
    rw [evaluation_C]
    exact (CrossedMonicHypersurface.residueMap_C CrossedFanoAffine.equation c).symm
  · intro i
    refine Fin.cases ?_ (fun j => ?_) i
    · rw [evaluation_X_zero]
      exact (CrossedMonicHypersurface.residueMap_X_zero CrossedFanoAffine.equation).symm
    · rw [evaluation_X_succ,CrossedFanoAffine.residueMap_coordinate]

lemma equation_zero : evaluation equation=0 := by
  rw [equation,H_map]
  have hv : (fun i => evaluation
      (![MvPolynomial.X 1,MvPolynomial.X 0,1,MvPolynomial.X 2,MvPolynomial.X 3] i))=
      ![CrossedFanoAffine.coordinate 0,CrossedFanoAffine.normal,1,
        CrossedFanoAffine.coordinate 1,CrossedFanoAffine.coordinate 2] := by
    funext i
    fin_cases i <;> simp [evaluation_X_succ,evaluation]
  rw [hv]
  exact CrossedFanoAffine.cleared_equation

lemma equation_partial : integerPartial 0 equation=
    42*MvPolynomial.X 0^5+5*(MvPolynomial.X 1^5+MvPolynomial.X 1^3+
      MvPolynomial.X 1+10*MvPolynomial.X 1*MvPolynomial.X 0^4) := by
  rw [equation,H_derivation]
  simp [gradient,Fin.sum_univ_succ]

lemma normal_evaluation : evaluation (integerPartial 0 equation)=CrossedFanoRadial.clearNormal := by
  rw [equation_partial]
  have h42 : evaluation (42 : Poly)=(42 : K) := map_natCast _ 42
  have h5 : evaluation (5 : Poly)=(5 : K) := map_natCast _ 5
  have h10 : evaluation (10 : Poly)=(10 : K) := map_natCast _ 10
  simp only [map_add,map_mul,map_pow,h42,h5,h10,evaluation_X_zero,evaluation_X_one]
  simp [CrossedFanoRadial.clearNormal,gradient]

lemma equation_hessian : integerPartial 0 (integerPartial 0 equation)=
    210*MvPolynomial.X 0^4+200*MvPolynomial.X 1*MvPolynomial.X 0^3 := by
  rw [equation_partial]
  have h42 : MvPolynomial.pderiv (R:=ℂ) (0 : Fin 4) (42 : Poly)=0 := (MvPolynomial.pderiv 0).map_natCast 42
  have h5 : MvPolynomial.pderiv (R:=ℂ) (0 : Fin 4) (5 : Poly)=0 := (MvPolynomial.pderiv 0).map_natCast 5
  have h10 : MvPolynomial.pderiv (R:=ℂ) (0 : Fin 4) (10 : Poly)=0 := (MvPolynomial.pderiv 0).map_natCast 10
  simp [integerPartial_apply,Derivation.leibniz,Derivation.leibniz_pow,smul_eq_mul,h42,h5,h10]
  ring

lemma hessian_evaluation : evaluation (integerPartial 0 (integerPartial 0 equation))=
    CrossedFanoRadial.clearSecondNormal := by
  rw [equation_hessian]
  have h210 : evaluation (210 : Poly)=(210 : K) := map_natCast _ 210
  have h200 : evaluation (200 : Poly)=(200 : K) := map_natCast _ 200
  simp only [map_add,map_mul,map_pow,h210,h200,evaluation_X_zero,evaluation_X_one]
  rfl

lemma tangent_formula (i : Fin 3) (p : Poly) :
    CrossedFanoAffine.tangent i (evaluation p)=evaluation (integerPartial i.succ p)-
      evaluation (integerPartial i.succ equation)/evaluation (integerPartial 0 equation)*
        evaluation (integerPartial 0 p) := by
  apply CrossedAffinePrimitiveData.tangent_formula_from_coordinates evaluation equation equation_zero
    (by change evaluation (integerPartial 0 equation)≠0
        rw [normal_evaluation]; exact CrossedFanoRadial.clearNormal_ne_zero)
    (CrossedFanoAffine.tangent i) i
  · intro c; rw [evaluation_C,CrossedFanoAffine.tangent_base]
  · intro j; rw [evaluation_X_succ]; exact CrossedFanoAffine.tangent_coordinate i j

theorem data_of_residue_solution (A : Poly) (w : Fin 3 → K)
    (hw : residueDivergence CrossedFanoAffine.tangent CrossedFanoRadial.clearNormal w=
      -(evaluation (integerPartial 0 A)/CrossedFanoRadial.clearNormal-
        evaluation A*CrossedFanoRadial.clearSecondNormal/CrossedFanoRadial.clearNormal^2)) :
    ∃ D N₀ : Poly,∃ N : Fin 3 → Poly,evaluation D≠0 ∧
      (N₀*integerPartial 0 equation+∑ i,N i*integerPartial i.succ equation=A*D) ∧
      evaluation (residueDivNum (integerPartial 0) (fun i : Fin 3 => integerPartial i.succ) D N₀ N)=0 := by
  apply CrossedAffinePrimitiveData.ambient_data evaluation (integerPartial 0)
    (fun i : Fin 3 => integerPartial i.succ) CrossedFanoAffine.tangent equation A w
  · rw [normal_evaluation]; exact CrossedFanoRadial.clearNormal_ne_zero
  · intro i; exact integerPartial_commute i.succ 0 equation
  · exact tangent_formula
  · rw [evaluation_residue]
    exact residue_common_representatives
      (CrossedMonicHypersurface.projection CrossedFanoAffine.equation)
      (CrossedMonicHypersurface.projection_surjective CrossedFanoAffine.equation) w
  · rw [normal_evaluation,hessian_evaluation]
    exact hw

def firstSource : Poly := 7*MvPolynomial.X 1^4*MvPolynomial.X 0
def secondSource : Poly := 7*MvPolynomial.X 1*MvPolynomial.X 2*MvPolynomial.X 3

lemma firstSource_value : evaluation firstSource=CrossedFanoRadial.affineFirstSource := by
  have h7 : evaluation (7 : Poly)=(7 : K) := map_natCast _ 7
  simp only [firstSource,map_mul,map_pow,h7,evaluation_X_zero,evaluation_X_one]
  rfl
lemma secondSource_value : evaluation secondSource=CrossedFanoRadial.affineSecondSource := by
  have h7 : evaluation (7 : Poly)=(7 : K) := map_natCast _ 7
  simp only [secondSource,map_mul,h7,evaluation_X_one,evaluation_X_two,evaluation_X_three]
  rfl

lemma firstSource_partial_value : evaluation (integerPartial 0 firstSource)=
    7*CrossedFanoAffine.coordinate 0^4 := by
  have h7 : MvPolynomial.pderiv (R:=ℂ) (0 : Fin 4) (7 : Poly)=0 := (MvPolynomial.pderiv 0).map_natCast 7
  have hp : integerPartial 0 firstSource=7*MvPolynomial.X 1^4 := by
    simp [firstSource,integerPartial_apply,h7]
  have he7 : evaluation (7 : Poly)=(7 : K) := map_natCast _ 7
  rw [hp,map_mul,map_pow,he7,evaluation_X_one]
lemma secondSource_partial_value : evaluation (integerPartial 0 secondSource)=0 := by
  have h7 : MvPolynomial.pderiv (R:=ℂ) (0 : Fin 4) (7 : Poly)=0 := (MvPolynomial.pderiv 0).map_natCast 7
  have hp : integerPartial 0 secondSource=0 := by simp [secondSource,integerPartial_apply,h7]
  rw [hp,map_zero]

theorem firstSource_data : ∃ D N₀ : Poly,∃ N : Fin 3 → Poly,evaluation D≠0 ∧
    (N₀*integerPartial 0 equation+∑ i,N i*integerPartial i.succ equation=firstSource*D) ∧
    evaluation (residueDivNum (integerPartial 0) (fun i : Fin 3 => integerPartial i.succ) D N₀ N)=0 := by
  obtain ⟨w,hw⟩ := CrossedFanoRadial.affine_first_residue_solution
  apply data_of_residue_solution firstSource w
  rw [firstSource_partial_value,firstSource_value]
  exact hw

theorem secondSource_data : ∃ D N₀ : Poly,∃ N : Fin 3 → Poly,evaluation D≠0 ∧
    (N₀*integerPartial 0 equation+∑ i,N i*integerPartial i.succ equation=secondSource*D) ∧
    evaluation (residueDivNum (integerPartial 0) (fun i : Fin 3 => integerPartial i.succ) D N₀ N)=0 := by
  obtain ⟨w,hw⟩ := CrossedFanoRadial.affine_second_residue_solution
  apply data_of_residue_solution secondSource w
  rw [secondSource_partial_value,secondSource_value,zero_div,zero_sub,neg_neg]
  exact hw

end CrossedFanoAffineData
end
end

/- Source component: FanoCubicProjection. -/
section

noncomputable section
namespace CrossedFanoCubic
open HoldoutConstruction
abbrev Poly := MvPolynomial (Fin 4) ℂ

def projection : Poly →+* CoordinateRing := (AdjoinRoot.mk equation).comp
  ((MvPolynomial.finSuccEquiv ℂ 3).toRingHom.comp (MvPolynomial.rename reverse).toRingHom)

lemma old_projection_kernel (p : Poly) :
    CrossedMonicHypersurface.projection CrossedFanoAffine.equation p=0 ↔ affineEquation ∣ p := by
  change AdjoinRoot.mk CrossedFanoAffine.equation (MvPolynomial.finSuccEquiv ℂ 3 p)=0 ↔ _
  rw [AdjoinRoot.mk_eq_zero,← old_univariate]
  exact map_dvd_iff (MvPolynomial.finSuccEquiv ℂ 3)

lemma projection_kernel (p : Poly) : projection p=0 ↔ affineEquation ∣ p := by
  change AdjoinRoot.mk equation (MvPolynomial.finSuccEquiv ℂ 3
    (MvPolynomial.rename reverse p))=0 ↔ _
  rw [AdjoinRoot.mk_eq_zero,← new_univariate]
  rw [map_dvd_iff (MvPolynomial.finSuccEquiv ℂ 3)]
  exact map_dvd_iff (MvPolynomial.renameEquiv (R:=ℂ) reverse)

lemma nonzero_of_old_evaluation (D : Poly) (hD : CrossedFanoAffineData.evaluation D≠0) :
    projection D≠0 := by
  intro h
  apply hD
  rw [CrossedFanoAffineData.evaluation_residue]
  change algebraMap CrossedFanoAffine.CoordinateRing CrossedFanoAffine.FunctionField
    (CrossedMonicHypersurface.projection CrossedFanoAffine.equation D)=0
  rw [(old_projection_kernel D).mpr ((projection_kernel D).mp h),map_zero]

lemma zero_of_old_evaluation (p : Poly) (hp : CrossedFanoAffineData.evaluation p=0) :
    projection p=0 := by
  rw [CrossedFanoAffineData.evaluation_residue] at hp
  change algebraMap CrossedFanoAffine.CoordinateRing CrossedFanoAffine.FunctionField
    (CrossedMonicHypersurface.projection CrossedFanoAffine.equation p)=0 at hp
  have hπ : CrossedMonicHypersurface.projection CrossedFanoAffine.equation p=0 := by
    apply IsFractionRing.injective CrossedFanoAffine.CoordinateRing CrossedFanoAffine.FunctionField
    simpa only [map_zero] using hp
  exact (projection_kernel p).mpr ((old_projection_kernel p).mp hπ)

end CrossedFanoCubic
end
end

/- Source component: EllipticFermatCoordinates. -/
section

noncomputable section
namespace CrossedElliptic
variable {K : Type*} [Field K] [CharZero K]
local instance : Algebra ℤ (RatFunc K) := Ring.toIntAlgebra _
local instance : Algebra ℤ (E K) := Ring.toIntAlgebra _

def a : E K := -(y K+36)/(6*x K)
def b : E K := (y K-36)/(6*x K)

lemma fermat_relation : (a (K := K))^3+(b (K := K))^3+1=0 := by
  dsimp [a,b]
  field_simp [x_ne_zero K]
  linear_combination -216*(relation K)

lemma delta_x : delta (K := K) (x K) = -y K/3 := by
  simp [delta,time_x]
lemma delta_y : delta (K := K) (y K) = -(x K)^2/2 := by
  simp only [delta,Derivation.smul_apply,smul_eq_mul,time_y]
  field_simp [y_ne_zero (K := K)]

lemma delta_a : delta (K := K) (a (K := K)) = (b (K := K))^2 := by
  have hc6 : delta (K := K) (6 : E K) = 0 := (delta (K := K)).map_natCast 6
  have hc36 : delta (K := K) (36 : E K) = 0 := (delta (K := K)).map_natCast 36
  dsimp [a,b]
  rw [Derivation.leibniz_div,map_neg,map_add,hc36,add_zero,
    Derivation.leibniz,hc6,smul_zero,add_zero,delta_x,delta_y]
  simp only [smul_eq_mul]
  field_simp [x_ne_zero K]
  linear_combination -18*(relation K)

lemma delta_b : delta (K := K) (b (K := K)) = -(a (K := K))^2 := by
  have hc6 : delta (K := K) (6 : E K) = 0 := (delta (K := K)).map_natCast 6
  have hc36 : delta (K := K) (36 : E K) = 0 := (delta (K := K)).map_natCast 36
  dsimp [a,b]
  rw [Derivation.leibniz_div,map_sub,hc36,sub_zero,
    Derivation.leibniz,hc6,smul_zero,add_zero,delta_x,delta_y]
  simp only [smul_eq_mul]
  field_simp [x_ne_zero K]
  linear_combination 18*(relation K)

lemma coefficient_a (D : Derivation ℤ K K) : coefficient D (a (K := K)) = 0 := by
  have hc6 : coefficient D (6 : E K) = 0 := (coefficient D).map_natCast 6
  have hc36 : coefficient D (36 : E K) = 0 := (coefficient D).map_natCast 36
  dsimp [a]
  rw [Derivation.leibniz_div,map_neg,map_add,coefficient_y,hc36,
    Derivation.leibniz,hc6,coefficient_x]
  simp
lemma coefficient_b (D : Derivation ℤ K K) : coefficient D (b (K := K)) = 0 := by
  have hc6 : coefficient D (6 : E K) = 0 := (coefficient D).map_natCast 6
  have hc36 : coefficient D (36 : E K) = 0 := (coefficient D).map_natCast 36
  dsimp [b]
  rw [Derivation.leibniz_div,map_sub,coefficient_y,hc36,
    Derivation.leibniz,hc6,coefficient_x]
  simp

end CrossedElliptic
end
end

/- Source component: EllipticBasis. -/
section

noncomputable section
namespace CrossedElliptic
open Polynomial
variable (K : Type*) [Field K]

lemma equation_natDegree : (equation K).natDegree = 2 := by
  rw [equation_eq]
  compute_degree <;> simp

def basis : Module.Basis (Fin 2) (RatFunc K) (E K) :=
  (AdjoinRoot.powerBasis' (equation_monic K)).basis.reindex (finCongr (equation_natDegree K))

lemma basis_apply (i : Fin 2) : basis K i = (y K)^i.val := by
  rw [basis,Module.Basis.reindex_apply]
  rw [(AdjoinRoot.powerBasis' (equation_monic K)).basis_eq_pow]
  rfl

lemma basis_zero : basis K 0 = 1 := by rw [basis_apply]; rfl
lemma basis_one : basis K 1 = y K := by rw [basis_apply]; simp

lemma finrank_eq_two : Module.finrank (RatFunc K) (E K) = 2 := by
  rw [Module.finrank_eq_card_basis (basis K),Fintype.card_fin]

def first : E K →ₗ[RatFunc K] RatFunc K :=
  (Finsupp.lapply (0 : Fin 2) : (Fin 2 →₀ RatFunc K) →ₗ[RatFunc K] RatFunc K).comp (basis K).repr.toLinearMap
def second : E K →ₗ[RatFunc K] RatFunc K :=
  (Finsupp.lapply (1 : Fin 2) : (Fin 2 →₀ RatFunc K) →ₗ[RatFunc K] RatFunc K).comp (basis K).repr.toLinearMap

lemma first_second_expansion (f : E K) :
    f = algebraMap (RatFunc K) (E K) (first K f) +
      algebraMap (RatFunc K) (E K) (second K f)*y K := by
  have h := (basis K).sum_repr f
  rw [Fin.sum_univ_two,basis_zero,basis_one] at h
  simpa only [first,second,LinearMap.comp_apply,Finsupp.lapply_apply,
    LinearEquiv.coe_coe,Algebra.smul_def,mul_one] using h.symm

lemma trace_y : Algebra.trace (RatFunc K) (E K) (y K) = 0 := by
  have h := (AdjoinRoot.powerBasis' (equation_monic K)).trace_gen_eq_nextCoeff_minpoly
  rw [show (AdjoinRoot.powerBasis' (equation_monic K)).gen = y K from rfl] at h
  have hm : minpoly (RatFunc K) (y K) = equation K := by
    simpa only [y,(equation_monic K).leadingCoeff,inv_one,C_1,mul_one] using
      AdjoinRoot.minpoly_root (equation_irreducible K).ne_zero
  rw [hm] at h
  rw [h]
  rw [Polynomial.nextCoeff,equation_natDegree]
  norm_num [equation_eq]
  rw [← map_pow,Polynomial.coeff_C,if_neg (by decide)]

lemma trace_expansion (f : E K) : Algebra.trace (RatFunc K) (E K) f = 2*first K f := by
  conv_lhs => rw [first_second_expansion K f]
  rw [map_add,Algebra.trace_algebraMap,finrank_eq_two]
  have hm : algebraMap (RatFunc K) (E K) (second K f)*y K = (second K f) • y K :=
    (Algebra.smul_def _ _).symm
  rw [hm,map_smul,trace_y,smul_zero,add_zero]
  simp [smul_eq_mul]

end CrossedElliptic
end
end

/- Source component: EllipticTranslationIdentities. -/
section

namespace CrossedEllipticTranslation
variable {R : Type*} [CommRing R]

def xNumerator (x y u v : R) : R := (y-v)^2-(x+u)*(x-u)^2
def yNumerator (x y u v : R) : R :=
  -y*(x-u)^3+(y-v)*(x*(x-u)^2-xNumerator x y u v)

lemma cleared_curve_identity (x y u v : R) :
    (yNumerator x y u v)^2-(xNumerator x y u v)^3+432*(x-u)^6=
      -(x-u)^3*(u^3-3*u^2*x+2*v*y+x^3-y^2+432)*(y^2-x^3+432)+
      (x-u)^3*(u^3-3*u*x^2-v^2+2*v*y+x^3+432)*(v^2-u^3+432) := by
  unfold yNumerator xNumerator
  ring

variable {L : Type*} [Field L]

def slope (x y u v : L) : L := (y-v)/(x-u)
def translatedX (x y u v : L) : L := (slope x y u v)^2-x-u
def translatedY (x y u v : L) : L := -y+slope x y u v*(x-translatedX x y u v)

lemma translatedX_fraction (x y u v : L) (h : x-u≠0) :
    translatedX x y u v=xNumerator x y u v/(x-u)^2 := by
  unfold translatedX slope xNumerator
  field_simp <;> ring

lemma translatedY_fraction (x y u v : L) (h : x-u≠0) :
    translatedY x y u v=yNumerator x y u v/(x-u)^3 := by
  rw [translatedY,translatedX_fraction x y u v h]
  unfold slope yNumerator
  field_simp <;> ring

lemma translated_curve (x y u v : L) (h : x-u≠0)
    (hp : y^2=x^3-432) (hq : v^2=u^3-432) :
    (translatedY x y u v)^2=(translatedX x y u v)^3-432 := by
  have hc := cleared_curve_identity x y u v
  rw [hp,hq] at hc
  have hc' : (yNumerator x y u v)^2-(xNumerator x y u v)^3+432*(x-u)^6=0 := by
    linear_combination hc
  rw [translatedX_fraction x y u v h,translatedY_fraction x y u v h]
  apply (mul_right_injective₀ (pow_ne_zero 6 h))
  field_simp
  linear_combination hc'

lemma inverse_slope (x y u v : L) (h : x-u≠0)
    (h' : translatedX x y u v-u≠0) :
    slope (translatedX x y u v) (translatedY x y u v) u (-v)= -slope x y u v := by
  unfold translatedY slope
  field_simp <;> ring

lemma inverse_x (x y u v : L) (h : x-u≠0)
    (h' : translatedX x y u v-u≠0) :
    translatedX (translatedX x y u v) (translatedY x y u v) u (-v)=x := by
  rw [translatedX,inverse_slope x y u v h h']
  unfold translatedX
  ring

lemma inverse_y (x y u v : L) (h : x-u≠0)
    (h' : translatedX x y u v-u≠0) :
    translatedY (translatedX x y u v) (translatedY x y u v) u (-v)=y := by
  rw [translatedY,inverse_x x y u v h h',inverse_slope x y u v h h']
  unfold translatedY
  ring

end CrossedEllipticTranslation
end

/- Source component: EllipticBasisCoordinates. -/
section

noncomputable section
set_option backward.isDefEq.respectTransparency false
namespace CrossedElliptic
open Polynomial CrossedRationalResidue
variable (K : Type*) [Field K]

lemma first_one : first K (1 : E K)=1 := by
  change (basis K).repr 1 0=1
  rw [← basis_zero,(basis K).repr_self]
  simp
lemma second_one : second K (1 : E K)=0 := by
  change (basis K).repr 1 1=0
  rw [← basis_zero,(basis K).repr_self]
  simp
lemma second_y : second K (y K)=1 := by
  change (basis K).repr (y K) 1=1
  rw [← basis_one,(basis K).repr_self]
  simp

lemma first_algebraMap (f : RatFunc K) : first K (algebraMap (RatFunc K) (E K) f)=f := by
  have hs : algebraMap (RatFunc K) (E K) f=f • (1 : E K) := by
    rw [Algebra.smul_def,mul_one]
  rw [hs,map_smul,first_one,smul_eq_mul,mul_one]
lemma second_algebraMap (f : RatFunc K) : second K (algebraMap (RatFunc K) (E K) f)=0 := by
  have hs : algebraMap (RatFunc K) (E K) f=f • (1 : E K) := by
    rw [Algebra.smul_def,mul_one]
  rw [hs,map_smul,second_one,smul_zero]
lemma second_coeff_y (f : RatFunc K) :
    second K (algebraMap (RatFunc K) (E K) f*y K)=f := by
  rw [← Algebra.smul_def,map_smul,second_y,smul_eq_mul,mul_one]

lemma x_transcendental : Transcendental K (x K) :=
  (transcendental_algebraMap_iff (algebraMap (RatFunc K) (E K)).injective).mpr RatFunc.transcendental_X

lemma map_constant (u : K) : algebraMap (RatFunc K) (E K) (RatFunc.C u)=algebraMap K (E K) u := by
  rw [← RatFunc.algebraMap_eq_C]
  exact (IsScalarTower.algebraMap_apply K (RatFunc K) (E K) u).symm

lemma x_sub_constant_ne_zero (u : K) : x K-algebraMap K (E K) u≠0 := by
  have h := (algebraMap (RatFunc K) (E K)).injective.ne (uniformizer_ne_zero u)
  simpa only [uniformizer,map_sub,map_zero,RatFunc.algebraMap_X,RatFunc.algebraMap_C,x,map_constant] using h

variable [CharZero K]
open CrossedEllipticTranslation

lemma translatedX_expansion (u v : K) :
    translatedX (x K) (y K) (algebraMap K (E K) u) (algebraMap K (E K) v)-algebraMap K (E K) u=
      algebraMap (RatFunc K) (E K)
        (((RatFunc.X : RatFunc K)^3-432+(RatFunc.C v)^2)/(RatFunc.X-RatFunc.C u)^2-
          RatFunc.X-2*RatFunc.C u)+
      algebraMap (RatFunc K) (E K)
        (-2*RatFunc.C v/(RatFunc.X-RatFunc.C u)^2)*y K := by
  have hd := x_sub_constant_ne_zero K u
  have hr := relation K
  simp only [translatedX,slope,map_sub,map_add,map_div₀,map_pow,map_mul,map_neg,map_ofNat,map_constant]
  change ((y K-algebraMap K (E K) v)/(x K-algebraMap K (E K) u))^2-x K-
    algebraMap K (E K) u-algebraMap K (E K) u=
    ((x K)^3-432+(algebraMap K (E K) v)^2)/(x K-algebraMap K (E K) u)^2-
      x K-2*algebraMap K (E K) u+
    (-2*algebraMap K (E K) v/(x K-algebraMap K (E K) u)^2)*y K
  field_simp
  linear_combination hr

lemma translatedX_sub_constant_ne_zero (u v : K) (hv : v≠0) :
    translatedX (x K) (y K) (algebraMap K (E K) u) (algebraMap K (E K) v)-
      algebraMap K (E K) u≠0 := by
  intro h
  rw [translatedX_expansion] at h
  have hs := congrArg (second K) h
  rw [map_add,second_algebraMap,second_coeff_y,map_zero,zero_add] at hs
  have hu : (RatFunc.X : RatFunc K)-RatFunc.C u≠0 := by
    simpa [uniformizer] using uniformizer_ne_zero u
  have hv' : (RatFunc.C v : RatFunc K)≠0 := by
    simpa only [map_zero] using RatFunc.C_injective.ne hv
  exact (div_ne_zero (mul_ne_zero (by norm_num) hv') (pow_ne_zero 2 hu)) hs

lemma translatedX_sub_constant_ne_zero_of_point (u v : K) (hp : v^2=u^3-432) :
    translatedX (x K) (y K) (algebraMap K (E K) u) (algebraMap K (E K) v)-
      algebraMap K (E K) u≠0 := by
  by_cases hv : v=0
  · subst v
    have hu : u≠0 := by intro h; rw [h] at hp; norm_num at hp
    have hu' : algebraMap K (E K) u≠0 := (_root_.map_ne_zero _).mpr hu
    have hd := x_sub_constant_ne_zero K u
    have hp' := congrArg (algebraMap K (E K)) hp
    simp only [map_pow,map_sub,map_zero] at hp'
    have h432 : algebraMap K (E K) (432 : K)=(432 : E K) := map_natCast _ 432
    rw [h432] at hp'
    have hr := relation K
    have he : (x K-algebraMap K (E K) u)^2*
        (translatedX (x K) (y K) (algebraMap K (E K) u) 0-algebraMap K (E K) u)=
        3*(algebraMap K (E K) u)^2*(x K-algebraMap K (E K) u) := by
      unfold translatedX slope
      field_simp
      linear_combination hr-hp'
    rw [map_zero]
    intro hz
    rw [hz,mul_zero] at he
    exact (mul_ne_zero (mul_ne_zero (by norm_num) (pow_ne_zero 2 hu')) hd) he.symm
  · exact translatedX_sub_constant_ne_zero K u v hv

end CrossedElliptic
end
end

/- Source component: EllipticFermatTranscendence. -/
section

noncomputable section
namespace CrossedElliptic
variable {K : Type*} [Field K] [CharZero K]

lemma fermat_sum_relation : (a (K:=K)+b (K:=K))*x K= -12 := by
  unfold a b
  field_simp [x_ne_zero K]
  ring

lemma fermat_sum_ne_zero : a (K:=K)+b (K:=K)≠0 := by
  intro h
  have he := fermat_sum_relation (K:=K)
  rw [h,zero_mul] at he
  norm_num at he

lemma x_from_fermat : x K= -12/(a (K:=K)+b (K:=K)) := by
  apply (eq_div_iff (fermat_sum_ne_zero (K:=K))).mpr
  linear_combination fermat_sum_relation (K:=K)

lemma fermat_a_transcendental : Transcendental K (a (K:=K)) := by
  intro ha
  have hone : IsAlgebraic K (1 : E K) := by simpa using (isAlgebraic_algebraMap (1 : K) (A:=E K))
  have hb : IsAlgebraic K (b (K:=K)) := by
    apply IsAlgebraic.of_pow (by decide : 0<3)
    have he : b (K:=K)^3= -(a (K:=K))^3-1 := by linear_combination fermat_relation (K:=K)
    rw [he]
    exact (ha.pow 3).neg.sub hone
  apply x_transcendental K
  rw [x_from_fermat (K:=K),div_eq_mul_inv]
  have h12 : IsAlgebraic K (-12 : E K) := by
    have hh : IsAlgebraic K (algebraMap K (E K) (-12 : K)) := isAlgebraic_algebraMap (-12 : K)
    have hc : algebraMap K (E K) (-12 : K)=(-12 : E K) := by
      rw [map_neg]
      congr 1
      exact map_natCast _ 12
    simpa only [hc] using hh
  have hi : IsAlgebraic K ((a (K:=K)+b (K:=K))⁻¹) := IsAlgebraic.inv_iff.mpr (ha.add hb)
  exact h12.mul hi

lemma fermat_scaled_a_transcendental (u : K) (hu : u≠0) :
    Transcendental K (algebraMap K (E K) u*a (K:=K)) := by
  intro hs
  have hu' : algebraMap K (E K) u≠0 := (_root_.map_ne_zero _).mpr hu
  have ha : a (K:=K)=(algebraMap K (E K) u*a (K:=K))/algebraMap K (E K) u := by
    field_simp
  apply fermat_a_transcendental (K:=K)
  rw [ha,div_eq_mul_inv]
  exact hs.mul (IsAlgebraic.inv_iff.mpr (isAlgebraic_algebraMap u))

end CrossedElliptic
end
end

/- Source component: FanoEllipticEmbedding. -/
section

noncomputable section
set_option backward.isDefEq.respectTransparency false
namespace CrossedFanoElliptic
open Polynomial HoldoutConstruction CrossedElliptic
variable {K : Type*} [Field K] [CharZero K]

def basePolynomial : MvPolynomial (Fin 2) ℂ :=
  MvPolynomial.X 0^6+MvPolynomial.X 1^6+1+
  MvPolynomial.C (5/7 : ℂ)*(MvPolynomial.X 0^5*MvPolynomial.X 1+
    MvPolynomial.X 0^3*MvPolynomial.X 1+MvPolynomial.X 0*MvPolynomial.X 1+
    2*MvPolynomial.X 0*MvPolynomial.X 1^5)

def coefficientMap (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) : CrossedFanoCubic.Coeff →+* E K :=
  (Polynomial.eval₂RingHom (algebraMap K (E K)) (algebraMap K (E K) u*a (K:=K))).comp
    ((Polynomial.mapRingHom φ).comp (MvPolynomial.finSuccEquiv ℂ 2).toRingHom)

lemma coefficientMap_injective (φ : MvPolynomial (Fin 2) ℂ →+* K) (hφ : Function.Injective φ)
    (u : K) (hu : u≠0) : Function.Injective (coefficientMap φ u) :=
  (transcendental_iff_injective.mp (fermat_scaled_a_transcendental u hu)).comp
    ((Polynomial.map_injective φ hφ).comp (MvPolynomial.finSuccEquiv ℂ 2).injective)

lemma base_univariate : MvPolynomial.finSuccEquiv ℂ 2 CrossedFanoCubic.base=C basePolynomial := by
  have hv : (Fin.cases (Polynomial.X : Polynomial (MvPolynomial (Fin 2) ℂ))
      (fun j => C (MvPolynomial.X j)))=![X,C (MvPolynomial.X 0),C (MvPolynomial.X 1)] := by
    funext j; fin_cases j <;> rfl
  have hc2 : Polynomial.C (2 : MvPolynomial (Fin 2) ℂ)=(2 : Polynomial (MvPolynomial (Fin 2) ℂ)) := map_natCast _ 2
  simp [CrossedFanoCubic.base,basePolynomial,MvPolynomial.finSuccEquiv_apply,hv,hc2]

lemma coefficientMap_base (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) :
    coefficientMap φ u CrossedFanoCubic.base=algebraMap K (E K) (φ basePolynomial) := by
  change Polynomial.eval₂ (algebraMap K (E K)) (algebraMap K (E K) u*a (K:=K))
    ((MvPolynomial.finSuccEquiv ℂ 2 CrossedFanoCubic.base).map φ)=_
  rw [base_univariate,Polynomial.map_C,Polynomial.eval₂_C]

lemma coefficientMap_S (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) :
    coefficientMap φ u (MvPolynomial.X 0)=algebraMap K (E K) u*a (K:=K) := by
  change Polynomial.eval₂ (algebraMap K (E K)) (algebraMap K (E K) u*a (K:=K))
    ((MvPolynomial.finSuccEquiv ℂ 2 (MvPolynomial.X 0)).map φ)=_
  rw [MvPolynomial.finSuccEquiv_X_zero,Polynomial.map_X,Polynomial.eval₂_X]

lemma coefficientMap_X_succ (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (i : Fin 2) :
    coefficientMap φ u (MvPolynomial.X i.succ)=algebraMap K (E K) (φ (MvPolynomial.X i)) := by
  change Polynomial.eval₂ (algebraMap K (E K)) (algebraMap K (E K) u*a (K:=K))
    ((MvPolynomial.finSuccEquiv ℂ 2 (MvPolynomial.X i.succ)).map φ)=_
  rw [MvPolynomial.finSuccEquiv_X_succ,Polynomial.map_C,Polynomial.eval₂_C]

lemma coefficientMap_C (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (c : ℂ) :
    coefficientMap φ u (MvPolynomial.C c)=algebraMap K (E K) (φ (MvPolynomial.C c)) := by
  change Polynomial.eval₂ (algebraMap K (E K)) (algebraMap K (E K) u*a (K:=K))
    ((MvPolynomial.finSuccEquiv ℂ 2 (MvPolynomial.C c)).map φ)=_
  rw [show MvPolynomial.finSuccEquiv ℂ 2 (MvPolynomial.C c)=C (MvPolynomial.C c)
    from (MvPolynomial.finSuccEquiv ℂ 2).commutes c,Polynomial.map_C,Polynomial.eval₂_C]

lemma equation_root (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (hu : u^3=φ basePolynomial) :
    CrossedFanoCubic.equation.eval₂ (coefficientMap φ u) (algebraMap K (E K) u*b (K:=K))=0 := by
  simp only [CrossedFanoCubic.equation,Polynomial.eval₂_add,Polynomial.eval₂_pow,
    Polynomial.eval₂_X,Polynomial.eval₂_C,map_add,map_pow,coefficientMap_base,coefficientMap_S]
  rw [← hu,map_pow]
  linear_combination (algebraMap K (E K) u)^3*fermat_relation (K:=K)

def ringMap (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (hu : u^3=φ basePolynomial) :
    CrossedFanoCubic.CoordinateRing →+* E K :=
  AdjoinRoot.lift (f:=CrossedFanoCubic.equation) (coefficientMap φ u)
    (algebraMap K (E K) u*b (K:=K)) (equation_root φ u hu)

lemma ringMap_injective (φ : MvPolynomial (Fin 2) ℂ →+* K) (hφ : Function.Injective φ)
    (u : K) (hu0 : u≠0) (hu : u^3=φ basePolynomial) : Function.Injective (ringMap φ u hu) :=
  monic_root_embedding_injective CrossedFanoCubic.equation CrossedFanoCubic.equation_monic
    CrossedFanoCubic.equation_irreducible (coefficientMap φ u) (coefficientMap_injective φ hφ u hu0)
    (algebraMap K (E K) u*b (K:=K)) (equation_root φ u hu)

def evaluation (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (hu : u^3=φ basePolynomial) :
    MvPolynomial (Fin 4) ℂ →+* E K := (ringMap φ u hu).comp CrossedFanoCubic.projection

lemma evaluation_univariate (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (hu : u^3=φ basePolynomial)
    (p : MvPolynomial (Fin 4) ℂ) : evaluation φ u hu p=
      (MvPolynomial.finSuccEquiv ℂ 3 (MvPolynomial.rename CrossedFanoCubic.reverse p)).eval₂
        (coefficientMap φ u) (algebraMap K (E K) u*b (K:=K)) := by
  rfl

lemma evaluation_C (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (hu : u^3=φ basePolynomial) (c : ℂ) :
    evaluation φ u hu (MvPolynomial.C c)=algebraMap K (E K) (φ (MvPolynomial.C c)) := by
  rw [evaluation_univariate,MvPolynomial.rename_C]
  rw [show MvPolynomial.finSuccEquiv ℂ 3 (MvPolynomial.C c)=C (MvPolynomial.C c)
    from (MvPolynomial.finSuccEquiv ℂ 3).commutes c,Polynomial.eval₂_C,coefficientMap_C]

lemma evaluation_X (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (hu : u^3=φ basePolynomial) (i : Fin 4) :
    evaluation φ u hu (MvPolynomial.X i)=
      ![algebraMap K (E K) (φ (MvPolynomial.X 1)),algebraMap K (E K) (φ (MvPolynomial.X 0)),
        algebraMap K (E K) u*a (K:=K),algebraMap K (E K) u*b (K:=K)] i := by
  have hv : (Fin.cases (Polynomial.X : Polynomial CrossedFanoCubic.Coeff)
      (fun j => C (MvPolynomial.X j)))=![X,C (MvPolynomial.X 0),C (MvPolynomial.X 1),C (MvPolynomial.X 2)] := by
    funext j; fin_cases j <;> rfl
  have hx1 := coefficientMap_X_succ φ u 0
  have hx2 := coefficientMap_X_succ φ u 1
  change coefficientMap φ u (MvPolynomial.X 1)=_ at hx1
  change coefficientMap φ u (MvPolynomial.X 2)=_ at hx2
  rw [evaluation_univariate,MvPolynomial.rename_X]
  fin_cases i <;>
    simp [CrossedFanoCubic.reverse,MvPolynomial.finSuccEquiv_apply,hv,coefficientMap_S,hx1,hx2]

lemma evaluation_denominator_nonzero (φ : MvPolynomial (Fin 2) ℂ →+* K) (hφ : Function.Injective φ)
    (u : K) (hu0 : u≠0) (hu : u^3=φ basePolynomial) (D : MvPolynomial (Fin 4) ℂ)
    (hD : CrossedFanoAffineData.evaluation D≠0) : evaluation φ u hu D≠0 := by
  have h := (ringMap_injective φ hφ u hu0 hu).ne (CrossedFanoCubic.nonzero_of_old_evaluation D hD)
  change ringMap φ u hu (CrossedFanoCubic.projection D)≠0
  simpa only [map_zero] using h

lemma evaluation_zero_of_old (φ : MvPolynomial (Fin 2) ℂ →+* K) (u : K) (hu : u^3=φ basePolynomial)
    (p : MvPolynomial (Fin 4) ℂ) (hp : CrossedFanoAffineData.evaluation p=0) : evaluation φ u hu p=0 := by
  change ringMap φ u hu (CrossedFanoCubic.projection p)=0
  rw [CrossedFanoCubic.zero_of_old_evaluation p hp,map_zero]

end CrossedFanoElliptic
end
end
