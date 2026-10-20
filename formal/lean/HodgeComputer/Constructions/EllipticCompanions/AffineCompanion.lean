import HodgeComputer.Constructions.EllipticCompanions.ScalarEmbedding
import HodgeComputer.Constructions.HoldoutCover.HypersurfaceDomain

/-!
The affine companion `T^3+S^3+p(x,a)` is irreducible when `p(0,0)=1`.
The proof specializes to the same simple Eisenstein fibre used by the
accepted crossed-ternary construction, without fixing its ternary polynomial.
Prepared with OpenAI Codex assistance for fqlx.
-/

noncomputable section
namespace EllipticCompanion
open Polynomial HoldoutConstruction

def zeroEvaluation : P2 →+* ℂ := MvPolynomial.eval (fun _ => 0)

def affineSpecialization : Coeff →+* ℂ[X] :=
  (Polynomial.eval₂RingHom C (X-1)).comp
    ((Polynomial.mapRingHom zeroEvaluation).comp (MvPolynomial.finSuccEquiv ℂ 2).toRingHom)

lemma affineSpecialization_base (p : P2) :
    affineSpecialization (base p)=C (zeroEvaluation p) := by
  change Polynomial.eval₂ C (X-1) ((MvPolynomial.finSuccEquiv ℂ 2 (base p)).map zeroEvaluation)=_
  rw [base_univariate,Polynomial.map_C,Polynomial.eval₂_C]

lemma affineSpecialization_S : affineSpecialization (MvPolynomial.X 0)=X-1 := by
  change Polynomial.eval₂ C (X-1)
    ((MvPolynomial.finSuccEquiv ℂ 2 (MvPolynomial.X 0)).map zeroEvaluation)=_
  rw [MvPolynomial.finSuccEquiv_X_zero,Polynomial.map_X,Polynomial.eval₂_X]

theorem equation_irreducible (p : P2) (hp : zeroEvaluation p=1) :
    Irreducible (equation p) := by
  apply (equation_monic p).irreducible_of_irreducible_map affineSpecialization
  have hmap : (equation p).map affineSpecialization=
      (X : (ℂ[X])[X])^3+C ((X-1)^3+1) := by
    simp only [equation,Polynomial.map_add,Polynomial.map_pow,Polynomial.map_X,
      Polynomial.map_C,map_add,map_pow,affineSpecialization_base,
      affineSpecialization_S,hp,Polynomial.C_1]
  rw [hmap]
  have he : (X-1)^3+1=(X^3-3*X^2+3*X : ℂ[X]) := by ring
  rw [he]
  exact irreducible_power_add_constant (X^3-3*X^2+3*X : ℂ[X])
    (by simp) (by norm_num) 3 (by decide)

#print axioms equation_irreducible
end EllipticCompanion
