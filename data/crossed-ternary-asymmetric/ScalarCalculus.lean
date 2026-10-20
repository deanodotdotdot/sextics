import Proposal.CompanionPrimitives
import HodgeComputer.Constructions.HoldoutCover.PolynomialCalculus
import HodgeComputer.Constructions.HoldoutCover.ResidueClearing
import Mathlib.RingTheory.Derivation.Basic
import Mathlib.Tactic

/- Prepared with OpenAI Codex assistance for contributor 1337isnot1337.
See solution.md for the construction, provenance, and prior-work credit. -/

/- Source component: EvaluatedRationalJets. -/
section

noncomputable section
namespace CrossedEvaluatedJets
open HoldoutConstruction
open scoped BigOperators
variable {R L : Type*} [CommRing R] [Field L]

def values (ρ : R →+* L) (D : R) (N : Fin 4 → R) (i : Fin 4) : L := ρ (N i)/ρ D
def jet (ρ : R →+* L) (Δ : Fin 4 → Derivation ℤ R R) (D : R) (N : Fin 4 → R)
    (i j : Fin 4) : L := (ρ (Δ j (N i))*ρ D-ρ (N i)*ρ (Δ j D))/(ρ D)^2

lemma normal_values (ρ : R →+* L) (D A : R) (N g : Fin 4 → R)
    (hd : ρ D≠0) (hn : (∑ i,N i*g i)=A*D) :
    (∑ i,values ρ D N i*ρ (g i))=ρ A := by
  have he := congrArg ρ hn
  simp only [map_sum,map_mul,map_add,map_zero,Fin.sum_univ_succ,Fin.sum_univ_zero] at he
  simp only [values,Fin.sum_univ_succ,Fin.sum_univ_zero]
  field_simp
  linear_combination he

lemma normal_jets (ρ : R →+* L) (Δ : Fin 4 → Derivation ℤ R R) (D A : R)
    (N g : Fin 4 → R) (hd : ρ D≠0) (hn : (∑ i,N i*g i)=A*D) (j : Fin 4) :
    (∑ i,jet ρ Δ D N i j*ρ (g i))+
      (∑ i,values ρ D N i*ρ (Δ j (g i)))=ρ (Δ j A) := by
  have he := congrArg ρ hn
  have he' := congrArg (fun p => ρ (Δ j p)) hn
  simp only [map_sum,map_mul,map_add,map_zero,Derivation.leibniz,smul_eq_mul,
    Fin.sum_univ_succ,Fin.sum_univ_zero] at he he'
  simp only [jet,values,Fin.sum_univ_succ,Fin.sum_univ_zero]
  field_simp
  linear_combination ρ D*he'-ρ (Δ j D)*he

lemma divergence_jets (ρ : R →+* L) (Δ : Fin 4 → Derivation ℤ R R) (D : R) (N : Fin 4 → R)
    (hd : ρ D≠0)
    (hdiv : ρ (D*(∑ i,Δ i (N i))-(∑ i,N i*Δ i D))=0) :
    (∑ i,jet ρ Δ D N i i)=0 := by
  simp only [map_sub,map_mul,map_sum,map_add,map_zero,Fin.sum_univ_succ,Fin.sum_univ_zero] at hdiv
  simp only [jet,Fin.sum_univ_succ,Fin.sum_univ_zero]
  field_simp
  linear_combination hdiv

lemma derivative_values (ρ : R →+* L) (Δ : Fin 4 → Derivation ℤ R R)
    (E : Derivation ℤ L L) (z : Fin 4 → L)
    (hchain : ∀ p,E (ρ p)=∑ j,ρ (Δ j p)*z j)
    (D : R) (N : Fin 4 → R) (hd : ρ D≠0) (i : Fin 4) :
    E (values ρ D N i)=(∑ j,jet ρ Δ D N i j*z j) := by
  simp only [values,Derivation.leibniz_div,hchain,smul_eq_mul,jet,
    Fin.sum_univ_succ,Fin.sum_univ_zero]
  field_simp
  ring

end CrossedEvaluatedJets
end
end

/- Source component: EllipticJet. -/
section

/- Algebraic identities for a proposed split-sextic construction.
   These are intermediate identities, not a certificate existence theorem.
   Prepared with OpenAI Codex assistance for 1337isnot1337. -/
namespace CrossedEllipticJet

variable {R : Type*} [CommRing R]

theorem scaled_jet_identity
    (u a b px py B Bs Bt vx vy vs vt vxx vyy vss vtt
      vxs vys vts vxt vyt vst : R) :
    (3*u^2*(-a^2*vs-b^2*vt)
      +3*u^3*(b^3*vss-a^2*b*vst-a*b^2*vts+a^3*vtt)
      -3*u^3*(vxx+vyy)
      -u*(px*(a*vxs+b*vxt)+py*(a*vys+b*vyt))+px*vx+py*vy)
      -B+u*(a*Bs+b*Bt) =
    -3*u^3*(vxx+vyy+vss+vtt)
      -a*u*(px*vxs+py*vys+6*u*a*vs+3*u^2*a^2*vss+3*u^2*b^2*vts-Bs)
      -b*u*(px*vxt+py*vyt+6*u*b*vt+3*u^2*a^2*vst+3*u^2*b^2*vtt-Bt)
      +(px*vx+py*vy+3*u^2*a^2*vs+3*u^2*b^2*vt-B)
      +3*u^3*(a^3+b^3+1)*(vss+vtt) := by
  ring

variable {K : Type*} [Field K] [CharZero K]

theorem affine_first_equation
    (p q l src Pd Qd : K) (hp : p ≠ 0) (hq : q ≠ 0) (hl : l ≠ 0) :
    -(l/(3*p))*(Pd+l^6*Qd)
      +6*l^5*q*((3*p*src+Pd+l^6*Qd)/(18*p*l^4*q)) = src*l := by
  field_simp
  <;> ring

theorem affine_divergence_quotient
    (p q l src Pd Qd : K) (hp : p ≠ 0) (hq : q ≠ 0) (hl : l ≠ 0) :
    -l/(3*p)*(src+4*Pd/(3*p)+2*Qd/(3*q)) + l*Pd/(3*p^2)
      -(3*p*src+Pd)/(9*p*q*l^5)+2*l*Qd/(9*p*q)
      = -(p+l^6*q)*(3*p*src+Pd)/(9*p^2*q*l^5) := by
  field_simp
  <;> ring

end CrossedEllipticJet
end

/- Source component: ScalarCompanionJet. -/
section

noncomputable section
namespace CrossedScalarCompanionJet
variable {L : Type*} [Field L] [CharZero L]

def scalarB (u a b : L) (v : Fin 4 → L) : L := 3*(b*v 2-a*v 3)/u^2
def scalarX (u : L) (v : Fin 4 → L) : L := -3*v 0/u
def scalarY (u : L) (v : Fin 4 → L) : L := -3*v 1/u

def jetNumerator (u a b px py : L) (v : Fin 4 → L) (J : Matrix (Fin 4) (Fin 4) L) : L :=
  3*u^2*(-a^2*v 2-b^2*v 3)+
  3*u^3*(b^3*J 2 2-a^2*b*J 2 3-a*b^2*J 3 2+a^3*J 3 3)-
  3*u^3*(J 0 0+J 1 1)-
  u*(px*(a*J 0 2+b*J 0 3)+py*(a*J 1 2+b*J 1 3))+px*v 0+py*v 1

theorem scalar_equation (δ Dx Dy : Derivation ℤ L L)
    (u a b px py B Bs Bt : L) (v : Fin 4 → L) (J : Matrix (Fin 4) (Fin 4) L)
    (hu : u≠0) (hδu : δ u=0) (ha : δ a=b^2) (hb : δ b= -a^2)
    (hDxu : Dx u=px/(3*u^2)) (hDyu : Dy u=py/(3*u^2))
    (hδs : δ (v 2)=u*b^2*J 2 2-u*a^2*J 2 3)
    (hδt : δ (v 3)=u*b^2*J 3 2-u*a^2*J 3 3)
    (hDx : Dx (v 0)=J 0 0+px/(3*u^2)*(a*J 0 2+b*J 0 3))
    (hDy : Dy (v 1)=J 1 1+py/(3*u^2)*(a*J 1 2+b*J 1 3))
    (hfermat : a^3+b^3+1=0)
    (hdiv : J 0 0+J 1 1+J 2 2+J 3 3=0)
    (hnormal : px*v 0+py*v 1+3*u^2*a^2*v 2+3*u^2*b^2*v 3=B)
    (hs : px*J 0 2+py*J 1 2+6*u*a*v 2+3*u^2*a^2*J 2 2+3*u^2*b^2*J 3 2=Bs)
    (ht : px*J 0 3+py*J 1 3+6*u*b*v 3+3*u^2*a^2*J 2 3+3*u^2*b^2*J 3 3=Bt) :
    δ (scalarB u a b v)+Dx (scalarX u v)+Dy (scalarY u v)=B/u^4-(a*Bs+b*Bt)/u^3 := by
  have hraw := CrossedEllipticJet.scaled_jet_identity u a b px py B Bs Bt
    (v 0) (v 1) (v 2) (v 3) (J 0 0) (J 1 1) (J 2 2) (J 3 3)
    (J 0 2) (J 1 2) (J 3 2) (J 0 3) (J 1 3) (J 2 3)
  simp only [hdiv,hnormal,hs,ht,hfermat,sub_self,mul_zero,zero_mul,add_zero] at hraw
  change jetNumerator u a b px py v J-B+u*(a*Bs+b*Bt)=0 at hraw
  have hδ3 : δ (3 : L)=0 := δ.map_natCast 3
  have hx3 : Dx (3 : L)=0 := Dx.map_natCast 3
  have hy3 : Dy (3 : L)=0 := Dy.map_natCast 3
  have he : δ (scalarB u a b v)+Dx (scalarX u v)+Dy (scalarY u v)-
      (B/u^4-(a*Bs+b*Bt)/u^3)=(jetNumerator u a b px py v J-B+u*(a*Bs+b*Bt))/u^4 := by
    simp only [scalarB,scalarX,scalarY,jetNumerator,Derivation.leibniz_div,Derivation.leibniz,
      Derivation.leibniz_pow,map_sub,map_add,map_neg,hδ3,hx3,hy3,hδu,ha,hb,hDxu,hDyu,
      hδs,hδt,hDx,hDy,smul_eq_mul,nsmul_eq_mul,smul_zero,mul_zero,zero_mul,add_zero,zero_add]
    norm_num only
    field_simp [hu]
    ring
  rw [hraw,zero_div] at he
  exact sub_eq_zero.mp he

end CrossedScalarCompanionJet
end
end

/- Source component: FanoEllipticCalculus. -/
section

noncomputable section
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 400000
namespace CrossedFanoElliptic
open HoldoutConstruction CrossedElliptic CrossedConicIncidence
open scoped BigOperators
variable {K : Type*} [Field K] [CharZero K]
local instance : Algebra ℤ (E K) := Ring.toIntAlgebra _

abbrev P2 := MvPolynomial (Fin 2) ℂ
abbrev P4 := MvPolynomial (Fin 4) ℂ

def swap : Fin 4 → Fin 4 := ![1,0,2,3]
def ambientD (i : Fin 4) : Derivation ℤ P4 P4 := integerPartial (swap i)
def baseGradient (φ : P2 →+* K) (i : Fin 2) : K := φ (integerPartial i basePolynomial)

lemma evaluation_eq_eval₂ (φ : P2 →+* K) (u : K) (hu : u^3=φ basePolynomial) :
    evaluation φ u hu=MvPolynomial.eval₂Hom ((algebraMap K (E K)).comp (φ.comp MvPolynomial.C))
      ![algebraMap K (E K) (φ (MvPolynomial.X 1)),algebraMap K (E K) (φ (MvPolynomial.X 0)),
        algebraMap K (E K) u*a (K:=K),algebraMap K (E K) u*b (K:=K)] := by
  apply MvPolynomial.ringHom_ext
  · intro c; rw [MvPolynomial.eval₂Hom_C]; exact evaluation_C φ u hu c
  · intro i; rw [evaluation_X,MvPolynomial.eval₂Hom_X']

lemma evaluation_chain (φ : P2 →+* K) (u : K) (hu : u^3=φ basePolynomial)
    (D : Derivation ℤ (E K) (E K))
    (hc : ∀ c,D (algebraMap K (E K) (φ (MvPolynomial.C c)))=0) (p : P4) :
    D (evaluation φ u hu p)=∑ i,evaluation φ u hu (ambientD i p)*
      D (![algebraMap K (E K) (φ (MvPolynomial.X 0)),algebraMap K (E K) (φ (MvPolynomial.X 1)),
        algebraMap K (E K) u*a (K:=K),algebraMap K (E K) u*b (K:=K)] i) := by
  rw [evaluation_eq_eval₂]
  have hh := derivation_eval₂_chain D ((algebraMap K (E K)).comp (φ.comp MvPolynomial.C))
    ![algebraMap K (E K) (φ (MvPolynomial.X 1)),algebraMap K (E K) (φ (MvPolynomial.X 0)),
      algebraMap K (E K) u*a (K:=K),algebraMap K (E K) u*b (K:=K)] hc p
  rw [hh]
  simp [Fin.sum_univ_four,ambientD,swap,integerPartial_apply]
  ring

lemma evaluated_gradient (φ : P2 →+* K) (u : K) (hu : u^3=φ basePolynomial) (i : Fin 4) :
    evaluation φ u hu (ambientD i CrossedFanoAffineData.equation)=7*
      ![algebraMap K (E K) (baseGradient φ 0),algebraMap K (E K) (baseGradient φ 1),
        3*(algebraMap K (E K) u)^2*a (K:=K)^2,
        3*(algebraMap K (E K) u)^2*b (K:=K)^2] i := by
  have hc (n : ℕ) : evaluation φ u hu (n : P4)=(n : E K) := map_natCast _ n
  have hcφ (n : ℕ) : φ (n : P2)=(n : K) := map_natCast _ n
  have hcK (n : ℕ) : algebraMap K (E K) (n : K)=(n : E K) := map_natCast _ n
  have hq : algebraMap K (E K) (φ (MvPolynomial.C (5/7 : ℂ)))=(5/7 : E K) := by
    have h := map_ratCast ((algebraMap K (E K)).comp (φ.comp MvPolynomial.C)) (5/7 : ℚ)
    norm_num only [Rat.cast_div,Rat.cast_ofNat] at h
    exact h
  have hz2 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (2 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 2
  have hb2 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (2 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 2
  have hz3 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (3 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 3
  have hb3 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (3 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 3
  have hz5 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (5 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 5
  have hb5 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (5 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 5
  have hz6 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (6 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 6
  have hb6 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (6 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 6
  have hz7 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (7 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 7
  have hb7 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (7 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 7
  fin_cases i <;>
    simp [ambientD,swap,CrossedFanoAffineData.equation,H,baseGradient,basePolynomial,
      integerPartial_apply,MvPolynomial.pderiv_mul,Derivation.leibniz_pow,smul_eq_mul,
      evaluation_X,evaluation_C,hc,hcφ,hcK,hq,map_ofNat,hz2,hz3,hz5,hz6,hz7,hb2,hb3,hb5,hb6,hb7] <;> ring

lemma evaluated_hessian_S (φ : P2 →+* K) (u : K) (hu : u^3=φ basePolynomial) (i : Fin 4) :
    evaluation φ u hu (ambientD 2 (ambientD i CrossedFanoAffineData.equation))=
      ![0,0,42*algebraMap K (E K) u*a (K:=K),0] i := by
  have hc (n : ℕ) : evaluation φ u hu (n : P4)=(n : E K) := map_natCast _ n
  have hz2 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (2 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 2
  have hb2 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (2 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 2
  have hz3 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (3 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 3
  have hb3 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (3 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 3
  have hz5 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (5 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 5
  have hb5 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (5 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 5
  have hz6 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (6 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 6
  have hb6 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (6 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 6
  have hz7 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (7 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 7
  have hb7 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (7 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 7
  fin_cases i <;>
    simp [ambientD,swap,CrossedFanoAffineData.equation,H,integerPartial_apply,
      MvPolynomial.pderiv_mul,Derivation.leibniz_pow,smul_eq_mul,evaluation_X,hc,map_ofNat,hz2,hz3,hz5,hz6,hz7,hb2,hb3,hb5,hb6,hb7] <;> ring

lemma evaluated_hessian_T (φ : P2 →+* K) (u : K) (hu : u^3=φ basePolynomial) (i : Fin 4) :
    evaluation φ u hu (ambientD 3 (ambientD i CrossedFanoAffineData.equation))=
      ![0,0,0,42*algebraMap K (E K) u*b (K:=K)] i := by
  have hc (n : ℕ) : evaluation φ u hu (n : P4)=(n : E K) := map_natCast _ n
  have hz2 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (2 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 2
  have hb2 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (2 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 2
  have hz3 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (3 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 3
  have hb3 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (3 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 3
  have hz5 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (5 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 5
  have hb5 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (5 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 5
  have hz6 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (6 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 6
  have hb6 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (6 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 6
  have hz7 (j : Fin 4) : MvPolynomial.pderiv (R:=ℂ) j (7 : P4)=0 := (MvPolynomial.pderiv j).map_natCast 7
  have hb7 (j : Fin 2) : MvPolynomial.pderiv (R:=ℂ) j (7 : P2)=0 := (MvPolynomial.pderiv j).map_natCast 7
  fin_cases i <;>
    simp [ambientD,swap,CrossedFanoAffineData.equation,H,integerPartial_apply,
      MvPolynomial.pderiv_mul,Derivation.leibniz_pow,smul_eq_mul,evaluation_X,hc,map_ofNat,hz2,hz3,hz5,hz6,hz7,hb2,hb3,hb5,hb6,hb7] <;> ring

lemma base_chain (φ : P2 →+* K) (D : Derivation ℤ K K)
    (hc : ∀ c,D (φ (MvPolynomial.C c))=0)
    (hx : ∀ i : Fin 2,D (φ (MvPolynomial.X i))=if i=0 then 1 else 0) :
    D (φ basePolynomial)=baseGradient φ 0 := by
  have he : φ=MvPolynomial.eval₂Hom (φ.comp MvPolynomial.C) (fun i => φ (MvPolynomial.X i)) := by
    apply MvPolynomial.ringHom_ext
    · intro c; rw [MvPolynomial.eval₂Hom_C]; rfl
    · intro i; rw [MvPolynomial.eval₂Hom_X']
  have h := derivation_eval₂_chain D (φ.comp MvPolynomial.C) (fun i => φ (MvPolynomial.X i)) hc basePolynomial
  rw [← he] at h
  simpa [Fin.sum_univ_succ,hx,baseGradient,integerPartial_apply] using h

lemma base_chain_at (φ : P2 →+* K) (D : Derivation ℤ K K) (j : Fin 2)
    (hc : ∀ c,D (φ (MvPolynomial.C c))=0)
    (hx : ∀ i : Fin 2,D (φ (MvPolynomial.X i))=if i=j then 1 else 0) :
    D (φ basePolynomial)=baseGradient φ j := by
  have he : φ=MvPolynomial.eval₂Hom (φ.comp MvPolynomial.C) (fun i => φ (MvPolynomial.X i)) := by
    apply MvPolynomial.ringHom_ext
    · intro c; rw [MvPolynomial.eval₂Hom_C]; rfl
    · intro i; rw [MvPolynomial.eval₂Hom_X']
  have h := derivation_eval₂_chain D (φ.comp MvPolynomial.C) (fun i => φ (MvPolynomial.X i)) hc basePolynomial
  rw [← he] at h
  simpa [hx,baseGradient,integerPartial_apply] using h

lemma cubic_derivative (D : Derivation ℤ K K) (φ : P2 →+* K) (u : K)
    (hu : u^3=φ basePolynomial) (hu0 : u≠0) :
    D u=D (φ basePolynomial)/(3*u^2) := by
  have h := congrArg D hu
  simp only [Derivation.leibniz_pow,smul_eq_mul,nsmul_eq_mul] at h
  norm_num only at h
  apply (eq_div_iff (mul_ne_zero (by norm_num) (pow_ne_zero _ hu0))).mpr
  linear_combination h

end CrossedFanoElliptic
end
end

/- Source component: EllipticTranslationMap. -/
section

noncomputable section
set_option backward.isDefEq.respectTransparency false
namespace CrossedElliptic
open Polynomial CrossedEllipticTranslation
variable (K : Type*) [Field K] [CharZero K]

def translateX (u v : K) : E K :=
  translatedX (x K) (y K) (algebraMap K (E K) u) (algebraMap K (E K) v)
def translateY (u v : K) : E K :=
  translatedY (x K) (y K) (algebraMap K (E K) u) (algebraMap K (E K) v)

lemma translate_relation (u v : K) (hp : v^2=u^3-432) :
    (translateY K u v)^2=(translateX K u v)^3-432 := by
  have hp' := congrArg (algebraMap K (E K)) hp
  have h432 : algebraMap K (E K) (432 : K)=(432 : E K) := map_natCast _ 432
  simp only [map_pow,map_sub,h432] at hp'
  exact translated_curve _ _ _ _ (x_sub_constant_ne_zero K u) (relation K) hp'

lemma translateX_transcendental (u v : K) (hp : v^2=u^3-432) :
    Transcendental K (translateX K u v) := by
  intro hx
  have hy : IsAlgebraic K (translateY K u v) := by
    apply IsAlgebraic.of_pow (by decide : 0<2)
    rw [translate_relation K u v hp]
    exact (hx.pow 3).sub (isAlgebraic_natCast 432)
  have hu : IsAlgebraic K (algebraMap K (E K) u) := isAlgebraic_algebraMap u
  have hv : IsAlgebraic K (algebraMap K (E K) v) := isAlgebraic_algebraMap v
  have hm : IsAlgebraic K ((translateY K u v+algebraMap K (E K) v)/
      (translateX K u v-algebraMap K (E K) u)) := by
    rw [div_eq_mul_inv]
    exact (hy.add hv).mul (IsAlgebraic.inv_iff.mpr (hx.sub hu))
  have hi := inverse_x (x K) (y K) (algebraMap K (E K) u) (algebraMap K (E K) v)
    (x_sub_constant_ne_zero K u) (translatedX_sub_constant_ne_zero_of_point K u v hp)
  have halg : IsAlgebraic K (translateX K u v |> fun z =>
      ((translateY K u v+algebraMap K (E K) v)/(z-algebraMap K (E K) u))^2-z-
        algebraMap K (E K) u) := ((hm.pow 2).sub hx).sub hu
  have he : ((translateY K u v+algebraMap K (E K) v)/
      (translateX K u v-algebraMap K (E K) u))^2-translateX K u v-algebraMap K (E K) u=x K := by
    simpa only [translatedX,slope,sub_neg_eq_add,translateX,translateY] using hi
  exact x_transcendental K (he ▸ halg)

def translateRational (u v : K) (hp : v^2=u^3-432) : RatFunc K →+* E K :=
  IsFractionRing.lift (transcendental_iff_injective.mp (translateX_transcendental K u v hp))

lemma translateRational_C (u v : K) (hp : v^2=u^3-432) (c : K) :
    translateRational K u v hp (RatFunc.C c)=algebraMap K (E K) c := by
  change translateRational K u v hp (algebraMap K[X] (RatFunc K) (C c))=_
  rw [translateRational,IsFractionRing.lift_algebraMap]
  exact Polynomial.aeval_C _ _

lemma translateRational_X (u v : K) (hp : v^2=u^3-432) :
    translateRational K u v hp (RatFunc.X)=translateX K u v := by
  change translateRational K u v hp (algebraMap K[X] (RatFunc K) X)=_
  rw [translateRational,IsFractionRing.lift_algebraMap]
  exact Polynomial.aeval_X _

lemma translate_root (u v : K) (hp : v^2=u^3-432) :
    (equation K).eval₂ (translateRational K u v hp) (translateY K u v)=0 := by
  conv_lhs => arg 3; rw [equation_eq]
  simp only [eval₂_sub,eval₂_pow,eval₂_X,eval₂_C,map_sub,map_pow,translateRational_X]
  have hc : translateRational K u v hp (432 : RatFunc K)=(432 : E K) := map_natCast _ 432
  rw [hc,translate_relation K u v hp,sub_self]

def translateMap (u v : K) (hp : v^2=u^3-432) : E K →+* E K :=
  AdjoinRoot.lift (f:=equation K) (translateRational K u v hp) (translateY K u v) (translate_root K u v hp)

lemma translateMap_x (u v : K) (hp : v^2=u^3-432) :
    translateMap K u v hp (x K)=translateX K u v := by
  rw [x,translateMap]
  change AdjoinRoot.lift _ _ _ (AdjoinRoot.of _ RatFunc.X)=_
  rw [AdjoinRoot.lift_of,translateRational_X]

lemma translateMap_y (u v : K) (hp : v^2=u^3-432) :
    translateMap K u v hp (y K)=translateY K u v := AdjoinRoot.lift_root _

lemma translateMap_base (u v : K) (hp : v^2=u^3-432) (c : K) :
    translateMap K u v hp (algebraMap K (E K) c)=algebraMap K (E K) c := by
  rw [← map_constant]
  change AdjoinRoot.lift _ _ _ (AdjoinRoot.of _ (RatFunc.C c))=_
  rw [AdjoinRoot.lift_of,translateRational_C]
  exact (map_constant K c).symm

end CrossedElliptic
end
end

/- Source component: EllipticTranslationDifferentials. -/
section

noncomputable section
set_option maxHeartbeats 200000
namespace CrossedEllipticTranslation
variable {L : Type*} [Field L] [CharZero L]

lemma translatedX_derivation (D : Derivation ℤ L L) (x y u v : L)
    (h : x-u≠0) (hx : D x= -y/3) (hy : D y= -x^2/2) (hu : D u=0) (hv : D v=0)
    (hp : y^2=x^3-432) (hq : v^2=u^3-432) :
    D (translatedX x y u v)= -translatedY x y u v/3 := by
  have hi : D (translatedX x y u v)+translatedY x y u v/3=
      ((y-v)*(y^2-x^3+432)+(v-y)*(v^2-u^3+432))/(3*(x-u)^3) := by
    simp only [translatedY,translatedX,slope,div_eq_mul_inv]
    simp only [map_sub,map_add,map_neg,Derivation.leibniz_pow,Derivation.leibniz,
      Derivation.leibniz_inv,hx,hy,hu,hv,smul_eq_mul,nsmul_eq_mul,Nat.cast_ofNat,
      sub_zero,zero_sub,mul_zero,zero_mul,add_zero,zero_add]
    norm_num only
    generalize hd : x-u=d at *
    field_simp [h]
    rw [← hd]
    ring
  rw [hp,hq] at hi
  linear_combination hi

lemma translatedY_derivation (D : Derivation ℤ L L) (x y u v : L)
    (h : x-u≠0) (hx : D x= -y/3) (hy : D y= -x^2/2) (hu : D u=0) (hv : D v=0)
    (hp : y^2=x^3-432) (hq : v^2=u^3-432) :
    D (translatedY x y u v)= -(translatedX x y u v)^2/2 := by
  have hi : D (translatedY x y u v)+(translatedX x y u v)^2/2=
      ((-2*u^2*x+u*x^2+2*v*y-y^2+432)*(y^2-x^3+432)+
        (-u^3+2*u^2*x-u*x^2+v^2-2*v*y+x^3-432)*(v^2-u^3+432))/(2*(x-u)^4) := by
    simp only [translatedY,translatedX,slope,div_eq_mul_inv]
    simp only [map_sub,map_add,map_neg,Derivation.leibniz_pow,
      Derivation.leibniz_inv,Derivation.leibniz,hx,hy,hu,hv,smul_eq_mul,nsmul_eq_mul,Nat.cast_ofNat,sub_zero,zero_sub,
      mul_zero,zero_mul,add_zero,zero_add]
    norm_num only
    generalize hd : x-u=d at *
    field_simp [h]
    rw [← hd]
    ring
  rw [hp,hq] at hi
  linear_combination hi

end CrossedEllipticTranslation
end
end

/- Source component: EllipticTranslationCommutation. -/
section

noncomputable section
set_option backward.isDefEq.respectTransparency false
namespace CrossedElliptic
open Polynomial HoldoutConstruction CrossedEllipticTranslation

section Polynomial
variable {R F L : Type*} [CommRing R] [Field F] [Field L]
lemma polynomial_intertwines (θ : R →+* F) (φ : F →+* L)
    (D : Derivation ℤ F F) (E : Derivation ℤ L L) (z : F)
    (hC : ∀ c,E (φ (θ c))=φ (D (θ c))) (hX : E (φ z)=φ (D z))
    (p : R[X]) : E (φ (p.eval₂ θ z))=φ (D (p.eval₂ θ z)) := by
  induction p using Polynomial.induction_on' with
  | add p q hp hq => simp only [eval₂_add,map_add,hp,hq]
  | monomial n c =>
    simp only [eval₂_monomial,map_mul,Derivation.leibniz,Derivation.leibniz_pow,
      map_add,map_pow,smul_eq_mul,nsmul_eq_mul,map_natCast,hC,hX]
end Polynomial

variable {K : Type*} [Field K] [CharZero K]
local instance : Algebra ℤ (RatFunc K) := Ring.toIntAlgebra _
local instance : Algebra ℤ (E K) := Ring.toIntAlgebra _

lemma polynomial_field_image (p : K[X]) :
    algebraMap (RatFunc K) (E K) (algebraMap K[X] (RatFunc K) p)=
      p.eval₂ (algebraMap K (E K)) (x K) := by
  induction p using Polynomial.induction_on' with
  | add p q hp hq => simp only [map_add,eval₂_add,hp,hq]
  | monomial n c =>
    simp only [← Polynomial.C_mul_X_pow_eq_monomial,map_mul,map_pow,RatFunc.algebraMap_C,
      map_constant,eval₂_mul,eval₂_C,eval₂_pow,eval₂_X]
    rfl

lemma field_intertwines {L : Type*} [Field L] (φ : E K →+* L)
    (D : Derivation ℤ (E K) (E K)) (E' : Derivation ℤ L L)
    (hC : ∀ c,E' (φ (algebraMap K (E K) c))=φ (D (algebraMap K (E K) c)))
    (hX : E' (φ (x K))=φ (D (x K))) (hY : E' (φ (y K))=φ (D (y K)))
    (f : E K) : E' (φ f)=φ (D f) := by
  have hpoly (p : K[X]) :
      E' (φ (algebraMap (RatFunc K) (E K) (algebraMap K[X] (RatFunc K) p)))=
      φ (D (algebraMap (RatFunc K) (E K) (algebraMap K[X] (RatFunc K) p))) := by
    rw [polynomial_field_image]
    exact polynomial_intertwines (algebraMap K (E K)) φ D E' (x K) hC hX p
  have hcoeff (r : RatFunc K) : E' (φ (algebraMap (RatFunc K) (E K) r))=
      φ (D (algebraMap (RatFunc K) (E K) r)) := by
    induction r using RatFunc.induction_on with
    | f P Q hQ =>
      simp only [map_div₀,Derivation.leibniz_div,smul_eq_mul,map_mul,map_sub,map_pow,map_inv₀,hpoly]
  induction f using AdjoinRoot.induction_on with
  | ih p =>
    rw [← AdjoinRoot.aeval_eq,Polynomial.aeval_def]
    exact polynomial_intertwines (algebraMap (RatFunc K) (E K)) φ D E' (y K) hcoeff hY p

lemma delta_base (c : K) : delta (K:=K) (algebraMap K (E K) c)=0 := by
  rw [delta,Derivation.smul_apply,IsScalarTower.algebraMap_apply K (RatFunc K) (E K),time_base]
  change (-y K/3) • algebraMap (RatFunc K) (E K) (baseTime (RatFunc.C c))=0
  rw [baseTime_C,map_zero,smul_zero]

theorem translateMap_delta (u v : K) (hp : v^2=u^3-432) (f : E K) :
    delta (translateMap K u v hp f)=translateMap K u v hp (delta f) := by
  apply field_intertwines (translateMap K u v hp) delta delta
  · intro c
    rw [translateMap_base,delta_base,map_zero]
  · rw [translateMap_x,delta_x,map_div₀,map_neg,translateMap_y]
    have hc : translateMap K u v hp (3 : E K)=(3 : E K) := map_natCast _ 3
    rw [hc]
    exact translatedX_derivation delta _ _ _ _ (x_sub_constant_ne_zero K u) delta_x delta_y
      (delta_base u) (delta_base v) (relation K) (by
        have h := congrArg (algebraMap K (E K)) hp
        have h432 : algebraMap K (E K) (432 : K)=(432 : E K) := map_natCast _ 432
        simpa only [map_pow,map_sub,h432] using h)
  · rw [translateMap_y,delta_y,map_div₀,map_neg,map_pow,translateMap_x]
    have hc : translateMap K u v hp (2 : E K)=(2 : E K) := map_natCast _ 2
    rw [hc]
    exact translatedY_derivation delta _ _ _ _ (x_sub_constant_ne_zero K u) delta_x delta_y
      (delta_base u) (delta_base v) (relation K) (by
        have h := congrArg (algebraMap K (E K)) hp
        have h432 : algebraMap K (E K) (432 : K)=(432 : E K) := map_natCast _ 432
        simpa only [map_pow,map_sub,h432] using h)

lemma coefficient_scalar (D : Derivation ℤ K K) (c : K) :
    coefficient D (algebraMap K (E K) c)=algebraMap K (E K) (D c) := by
  rw [IsScalarTower.algebraMap_apply K (RatFunc K) (E K),coefficient_base]
  rw [RatFunc.algebraMap_eq_C,baseCoefficient_C,map_constant]

lemma coefficient_translateX (D : Derivation ℤ K K) (u v : K) (hu : D u=0) (hv : D v=0) :
    coefficient D (translateX K u v)=0 := by
  simp [translateX,translatedX,slope,map_sub,Derivation.leibniz_pow,Derivation.leibniz_div,
    coefficient_x,coefficient_y,coefficient_scalar,hu,hv]

lemma coefficient_translateY (D : Derivation ℤ K K) (u v : K) (hu : D u=0) (hv : D v=0) :
    coefficient D (translateY K u v)=0 := by
  simp [translateY,translatedY,translatedX,slope,map_sub,map_add,map_neg,Derivation.leibniz_pow,
    Derivation.leibniz,Derivation.leibniz_div,coefficient_x,coefficient_y,coefficient_scalar,hu,hv]

theorem translateMap_coefficient (D : Derivation ℤ K K) (u v : K) (hp : v^2=u^3-432)
    (hu : D u=0) (hv : D v=0) (f : E K) :
    coefficient D (translateMap K u v hp f)=translateMap K u v hp (coefficient D f) := by
  apply field_intertwines (translateMap K u v hp) (coefficient D) (coefficient D)
  · intro c
    rw [translateMap_base,coefficient_scalar,translateMap_base]
  · rw [translateMap_x,coefficient_translateX D u v hu hv,coefficient_x,map_zero]
  · rw [translateMap_y,coefficient_translateY D u v hu hv,coefficient_y,map_zero]

end CrossedElliptic
end
end

/- Source component: FanoScalarPrimitive. -/
section

noncomputable section
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 600000
namespace CrossedFanoElliptic
open HoldoutConstruction CrossedElliptic CrossedEvaluatedJets CrossedScalarCompanionJet
open scoped BigOperators
variable {K : Type*} [Field K] [CharZero K]
local instance : Algebra ℤ (E K) := Ring.toIntAlgebra _

lemma data_reindex (A D N₀ : P4) (N : Fin 3 → P4)
    (hn : N₀*integerPartial 0 CrossedFanoAffineData.equation+
      ∑ i,N i*integerPartial i.succ CrossedFanoAffineData.equation=A*D) :
    (∑ i,![N 0,N₀,N 1,N 2] i*ambientD i CrossedFanoAffineData.equation)=A*D := by
  simp [Fin.sum_univ_four,Fin.sum_univ_succ,ambientD,swap] at hn ⊢
  linear_combination hn

lemma divergence_reindex (D N₀ : P4) (N : Fin 3 → P4) :
    D*(∑ i,ambientD i (![N 0,N₀,N 1,N 2] i))-
      (∑ i,![N 0,N₀,N 1,N 2] i*ambientD i D)=
    residueDivNum (integerPartial 0) (fun i : Fin 3 => integerPartial i.succ) D N₀ N := by
  simp [Fin.sum_univ_four,Fin.sum_univ_succ,ambientD,swap,residueDivNum]
  ring

lemma delta_evaluation_chain (φ : P2 →+* K) (u : K) (hu : u^3=φ basePolynomial) (p : P4) :
    delta (evaluation φ u hu p)=∑ j,evaluation φ u hu (ambientD j p)*
      ![0,0,algebraMap K (E K) u*b (K:=K)^2,-(algebraMap K (E K) u)*a (K:=K)^2] j := by
  rw [evaluation_chain φ u hu delta (fun _ => delta_base _) p]
  apply Finset.sum_congr rfl
  intro i hi
  congr 1
  fin_cases i <;> simp [delta_base,Derivation.leibniz,delta_a,delta_b,smul_eq_mul]

lemma coefficient_evaluation_chain (φ : P2 →+* K) (u : K) (hu : u^3=φ basePolynomial)
    (hu0 : u≠0) (D : Derivation ℤ K K) (j : Fin 2)
    (hc : ∀ c,D (φ (MvPolynomial.C c))=0)
    (hx : ∀ i : Fin 2,D (φ (MvPolynomial.X i))=if i=j then 1 else 0) (p : P4) :
    coefficient D (evaluation φ u hu p)=∑ i,evaluation φ u hu (ambientD i p)*
      ![if j=0 then 1 else 0,if j=1 then 1 else 0,
        algebraMap K (E K) (baseGradient φ j)/(3*(algebraMap K (E K) u)^2)*a (K:=K),
        algebraMap K (E K) (baseGradient φ j)/(3*(algebraMap K (E K) u)^2)*b (K:=K)] i := by
  have du := cubic_derivative D φ u hu hu0
  rw [base_chain_at φ D j hc hx] at du
  rw [evaluation_chain φ u hu (coefficient D) (by intro c; rw [coefficient_scalar,hc,map_zero]) p]
  apply Finset.sum_congr rfl
  intro i hi
  congr 1
  fin_cases i <;>
    simp [coefficient_scalar,hx,Derivation.leibniz,coefficient_a,coefficient_b,smul_eq_mul,
      du,map_div₀,map_mul,map_pow,map_ofNat,eq_comm] <;> ring

lemma evaluation_killed (φ : P2 →+* K) (u : K) (hu : u^3=φ basePolynomial)
    (D : Derivation ℤ K K) (hφ : ∀ p,D (φ p)=0) (huD : D u=0) (p : P4) :
    coefficient D (evaluation φ u hu p)=0 := by
  rw [evaluation_chain φ u hu (coefficient D) (by intro c; rw [coefficient_scalar,hφ,map_zero]) p]
  apply Finset.sum_eq_zero
  intro i hi
  have hz : coefficient D
      (![algebraMap K (E K) (φ (MvPolynomial.X 0)),algebraMap K (E K) (φ (MvPolynomial.X 1)),
        algebraMap K (E K) u*a (K:=K),algebraMap K (E K) u*b (K:=K)] i)=0 := by
    fin_cases i <;> simp [coefficient_scalar,hφ,huD,Derivation.leibniz,coefficient_a,coefficient_b,smul_eq_mul]
  rw [hz,mul_zero]

/-- The actual affine polynomial data yield a scalar primitive on the cubic cover. -/
theorem scalar_primitive_of_data (φ : P2 →+* K) (hφ : Function.Injective φ)
    (u : K) (hu0 : u≠0) (hu : u^3=φ basePolynomial)
    (Dx Dy : Derivation ℤ K K)
    (hcx : ∀ c,Dx (φ (MvPolynomial.C c))=0)
    (hcy : ∀ c,Dy (φ (MvPolynomial.C c))=0)
    (hxx : ∀ i : Fin 2,Dx (φ (MvPolynomial.X i))=if i=0 then 1 else 0)
    (hyy : ∀ i : Fin 2,Dy (φ (MvPolynomial.X i))=if i=1 then 1 else 0)
    (A D N₀ : P4) (N : Fin 3 → P4) (hd : CrossedFanoAffineData.evaluation D≠0)
    (hn : N₀*integerPartial 0 CrossedFanoAffineData.equation+
      ∑ i,N i*integerPartial i.succ CrossedFanoAffineData.equation=A*D)
    (hdiv : CrossedFanoAffineData.evaluation
      (residueDivNum (integerPartial 0) (fun i : Fin 3 => integerPartial i.succ) D N₀ N)=0) :
    ∃ bf cx cy : E K,(delta bf+coefficient Dx cx+coefficient Dy cy=
      evaluation φ u hu A/(7*(algebraMap K (E K) u)^4)-
      (a (K:=K)*evaluation φ u hu (ambientD 2 A)+b (K:=K)*evaluation φ u hu (ambientD 3 A))/
        (7*(algebraMap K (E K) u)^3)) ∧
      ∀ D : Derivation ℤ K K,(∀ p,D (φ p)=0) → D u=0 →
        coefficient D bf=0 ∧ coefficient D cx=0 ∧ coefficient D cy=0 := by
  let ρ := evaluation φ u hu
  let nn : Fin 4 → P4 := ![N 0,N₀,N 1,N 2]
  let vv := values ρ D nn
  let jj := jet ρ ambientD D nn
  let uu := algebraMap K (E K) u
  let px := algebraMap K (E K) (baseGradient φ 0)
  let py := algebraMap K (E K) (baseGradient φ 1)
  have hd' : ρ D≠0 := evaluation_denominator_nonzero φ hφ u hu0 hu D hd
  have hu' : uu≠0 := by simpa only [map_zero] using (algebraMap K (E K)).injective.ne hu0
  have hn' := data_reindex A D N₀ N hn
  have hv := normal_values ρ D A nn (fun i => ambientD i CrossedFanoAffineData.equation) hd' hn'
  have hs := normal_jets ρ ambientD D A nn (fun i => ambientD i CrossedFanoAffineData.equation) hd' hn' 2
  have ht := normal_jets ρ ambientD D A nn (fun i => ambientD i CrossedFanoAffineData.equation) hd' hn' 3
  have hdv := divergence_jets ρ ambientD D nn hd' (by
    rw [show D*(∑ i,ambientD i (nn i))-(∑ i,nn i*ambientD i D)=
      residueDivNum (integerPartial 0) (fun i : Fin 3 => integerPartial i.succ) D N₀ N
      from divergence_reindex D N₀ N]
    exact evaluation_zero_of_old φ u hu _ hdiv)
  change (∑ i,jj i i)=0 at hdv
  have hg (i : Fin 4) : ρ (ambientD i CrossedFanoAffineData.equation)=
      7*![px,py,3*uu^2*a (K:=K)^2,3*uu^2*b (K:=K)^2] i := evaluated_gradient φ u hu i
  have hgs (i : Fin 4) : ρ (ambientD 2 (ambientD i CrossedFanoAffineData.equation))=
      ![0,0,42*uu*a (K:=K),0] i := evaluated_hessian_S φ u hu i
  have hgt (i : Fin 4) : ρ (ambientD 3 (ambientD i CrossedFanoAffineData.equation))=
      ![0,0,0,42*uu*b (K:=K)] i := evaluated_hessian_T φ u hu i
  change (∑ i,vv i*ρ (ambientD i CrossedFanoAffineData.equation))=ρ A at hv
  change (∑ i,jj i 2*ρ (ambientD i CrossedFanoAffineData.equation))+
    (∑ i,vv i*ρ (ambientD 2 (ambientD i CrossedFanoAffineData.equation)))=ρ (ambientD 2 A) at hs
  change (∑ i,jj i 3*ρ (ambientD i CrossedFanoAffineData.equation))+
    (∑ i,vv i*ρ (ambientD 3 (ambientD i CrossedFanoAffineData.equation)))=ρ (ambientD 3 A) at ht
  simp only [hg,hgs,hgt,Fin.sum_univ_four] at hv hs ht
  simp at hv hs ht
  have hδ (i : Fin 4) := derivative_values ρ ambientD delta
    ![0,0,uu*b (K:=K)^2,-uu*a (K:=K)^2] (delta_evaluation_chain φ u hu) D nn hd' i
  have hx (i : Fin 4) := derivative_values ρ ambientD (coefficient Dx)
    ![1,0,px/(3*uu^2)*a (K:=K),px/(3*uu^2)*b (K:=K)]
    (by simpa using coefficient_evaluation_chain φ u hu hu0 Dx 0 hcx hxx) D nn hd' i
  have hy (i : Fin 4) := derivative_values ρ ambientD (coefficient Dy)
    ![0,1,py/(3*uu^2)*a (K:=K),py/(3*uu^2)*b (K:=K)]
    (by simpa using coefficient_evaluation_chain φ u hu hu0 Dy 1 hcy hyy) D nn hd' i
  change ∀ i,delta (vv i)=∑ j,jj i j*![0,0,uu*b (K:=K)^2,-uu*a (K:=K)^2] j at hδ
  change ∀ i,coefficient Dx (vv i)=∑ j,jj i j*![1,0,px/(3*uu^2)*a (K:=K),px/(3*uu^2)*b (K:=K)] j at hx
  change ∀ i,coefficient Dy (vv i)=∑ j,jj i j*![0,1,py/(3*uu^2)*a (K:=K),py/(3*uu^2)*b (K:=K)] j at hy
  refine ⟨scalarB uu a b vv,scalarX uu vv,scalarY uu vv,?_,?_⟩
  ·
    have dux : coefficient Dx uu=px/(3*uu^2) := by
      dsimp [uu,px]
      rw [coefficient_scalar,cubic_derivative Dx φ u hu hu0,base_chain_at φ Dx 0 hcx hxx]
      simp [map_div₀,map_mul,map_pow,map_ofNat]
    have duy : coefficient Dy uu=py/(3*uu^2) := by
      dsimp [uu,py]
      rw [coefficient_scalar,cubic_derivative Dy φ u hu hu0,base_chain_at φ Dy 1 hcy hyy]
      simp [map_div₀,map_mul,map_pow,map_ofNat]
    have result := scalar_equation delta (coefficient Dx) (coefficient Dy)
      uu a b px py (ρ A/7) (ρ (ambientD 2 A)/7) (ρ (ambientD 3 A)/7) vv jj hu'
      (delta_base u) delta_a delta_b dux duy
      (by rw [hδ]; simp [Fin.sum_univ_four]; ring)
      (by rw [hδ]; simp [Fin.sum_univ_four]; ring)
      (by rw [hx]; simp [Fin.sum_univ_four]; ring)
      (by rw [hy]; simp [Fin.sum_univ_four]; ring)
      fermat_relation
      (by simpa [Fin.sum_univ_four,add_assoc] using hdv)
      (by linear_combination (1/7 : E K)*hv)
      (by linear_combination (1/7 : E K)*hs)
      (by linear_combination (1/7 : E K)*ht)
    convert result using 1 <;> dsimp [uu,ρ] <;> field_simp <;> ring
  · intro Dz hzφ hzu
    have hzρ (p : P4) : coefficient Dz (ρ p)=0 := evaluation_killed φ u hu Dz hzφ hzu p
    have hzuu : coefficient Dz uu=0 := by
      change coefficient Dz (algebraMap K (E K) u)=0
      rw [coefficient_scalar,hzu,map_zero]
    have hzv (i : Fin 4) : coefficient Dz (vv i)=0 := by
      change coefficient Dz (ρ (nn i)/ρ D)=0
      simp only [Derivation.leibniz_div,hzρ,
        smul_eq_mul,zero_mul,mul_zero,sub_self,zero_div]
    have hz3 : coefficient Dz (3 : E K)=0 := (coefficient Dz).map_natCast 3
    simp only [scalarB,scalarX,scalarY,Derivation.leibniz_div,Derivation.leibniz,
      Derivation.leibniz_pow,map_sub,map_neg,hzv,coefficient_scalar,coefficient_a,coefficient_b,
      hzuu,hz3,smul_eq_mul,smul_zero,mul_zero,zero_mul,sub_self,add_zero,zero_add,zero_div,
      nsmul_eq_mul,and_self,neg_zero,true_and]


end CrossedFanoElliptic
end
end
