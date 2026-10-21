import Proposal.PhysicalNormalTransport
import Proposal.JacobianModel

/-! Exact coefficient bindings for the physical mixed-polar cubic.
The integral Jacobian API uses scales 8 and 432; these identities bind its
coefficients to the prescribed physical equation. Adapted from the construction
of fqlx and collaborators for benediamond with OpenAI Codex assistance. -/
noncomputable section
namespace CyclePhysicalJacobianCoefficients
open CyclePhysical CyclePhysicalCoordinates

lemma a8_scaling : CycleJacobian.a8 cOne cTwo 1 radial (radial*t)=
    8*radial^4*PolarCubic.s4 coeffA coeffB coeffC coeffD coeffE coeffF := by
  simp only [CycleJacobian.a8,PolarCubic.s4,PolarCubic.s4Numerator,
    coeffA,coeffB,coeffC,coeffD,coeffE,coeffF,t]
  ring
lemma b256_scaling : CycleJacobian.b256 cOne cTwo 1 radial (radial*t)=
    432*radial^6*(-PolarCubic.s6 coeffA coeffB coeffC coeffD coeffE coeffF/4) := by
  simp only [CycleJacobian.b256,PolarCubic.s6,PolarCubic.s6Numerator,
    coeffA,coeffB,coeffC,coeffD,coeffE,coeffF,t]
  ring
end CyclePhysicalJacobianCoefficients
