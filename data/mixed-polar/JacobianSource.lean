import Proposal.JacobianResidue

/-! The exact mixed-polar polynomial source on the Jacobian hypersurface.
The generic residue primitive applies to this source before its physical transport.
The incidence and trace architecture follows the accepted cyclic and transitive
constructions of hodgepodgeconjecture and fqlx. This specialization was prepared
for benediamond with OpenAI Codex assistance. -/
noncomputable section
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 1000000
namespace CycleJacobianSource
open HoldoutConstruction CycleJacobianHypersurface CycleJacobianEmbedding CycleJacobianResidue
open Polynomial
local notation "v" => (MvPolynomial.X : Fin 6 → Ambient)
/-- The coefficient of the Weierstrass X-coordinate in the source. -/
def P4 : Ambient :=
  (v 4+v 3^6*v 1)*(MvPolynomial.C (9/2 : ℂ)*(v 4+v 1)*(v 4+v 2^6*v 1)-
    MvPolynomial.C (1/12 : ℂ)*v 2^4*v 4*v 1)
/-- The constant coefficient of the source. -/
def P6 : Ambient :=
  MvPolynomial.C (1/8 : ℂ)*v 2^3*v 3^2*v 4^2*v 1*(v 4+v 1)*(v 4+v 3^6*v 1)
def source : Ambient :=
  MvPolynomial.C (1/144 : ℂ)*v 2*v 3*(P4*v 5+P6)
/-- Every polynomial source, in particular this exact source, has a primitive. -/
theorem source_residue_solution :
    ∃ w : Fin 5 → TargetField,
      residueDivergence tangent (residueMap (MvPolynomial.pderiv 0 hypersurface)) w=
        -(residueMap (MvPolynomial.pderiv 0 source)/residueMap (MvPolynomial.pderiv 0 hypersurface)-
          residueMap source*residueMap (MvPolynomial.pderiv 0 (MvPolynomial.pderiv 0 hypersurface))/
            (residueMap (MvPolynomial.pderiv 0 hypersurface))^2) :=
  target_residue_solution source
#print axioms source_residue_solution
end CycleJacobianSource
