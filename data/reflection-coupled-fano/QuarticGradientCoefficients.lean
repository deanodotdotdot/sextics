import Proposal.QuarticGradient

noncomputable section
namespace CoupledFanoQuarticSeed
open Polynomial
variable {K : Type*} [Field K] [CharP K 5]

def seedCoeff (j : K) (n : ℕ) : Fin 6 → K :=
  ![-j*((if n=0 then 1 else 0)+(if n=20 then 1 else 0)),
    (2-j)*((if n=5 then 1 else 0)+(if n=15 then 1 else 0)),
    -j*(if n=10 then 1 else 0),
    -j*((if n=5 then 1 else 0)-(if n=15 then 1 else 0)),
    (if n=0 then 1 else 0)-(if n=20 then 1 else 0),
    (if n=0 then 3 else 0)+(if n=4 then 1 else 0)+4*(if n=8 then 1 else 0)+
      (if n=12 then 1 else 0)+3*(if n=16 then 1 else 0)]

lemma seedGradient_coeff (j : K) (k : Fin 6) (n : ℕ) :
    (seedGradient j k).coeff n = seedCoeff j n k := by
  have h3 : (3 : K[X]) = C 3 := by simpa only [map_ofNat]
  fin_cases k <;>
    simp [seedGradient, seedCoeff, Matrix.cons_val, coeff_C_mul, coeff_one,
      coeff_X_pow, sub_mul, h3, coeff_C] <;> split_ifs <;> ring

end CoupledFanoQuarticSeed
