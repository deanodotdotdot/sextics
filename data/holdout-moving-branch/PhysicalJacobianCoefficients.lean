import Proposal.PhysicalNormalTransport
import Proposal.JacobianModel

/-! Exact coefficient bindings for the physical holdout-moving-branch cubic.
The integral Jacobian API uses scales 4116 and 111132; these identities bind its
coefficients to the actual prescribed physical equation. The transitive construction
is due to fqlx, building on the accepted cycle-three construction; this coefficient
specialization was prepared for benediamond with OpenAI Codex assistance. -/
noncomputable section
namespace CyclePhysicalJacobianCoefficients
open CyclePhysical CyclePhysicalCoordinates

lemma a8_scaling : CycleJacobian.a8 cOne cTwo 1 radial (radial*t)=
    4116*radial^4*TransitiveCubic.s4 coeffA coeffB coeffC coeffD coeffE coeffF := by
  simp only [CycleJacobian.a8,TransitiveCubic.s4,TransitiveCubic.s4Numerator,
    coeffA,coeffB,coeffC,coeffD,coeffE,coeffF,t]
  ring
lemma b256_scaling : CycleJacobian.b256 cOne cTwo 1 radial (radial*t)=
    111132*radial^6*(-TransitiveCubic.s6 coeffA coeffB coeffC coeffD coeffE coeffF/4) := by
  simp only [CycleJacobian.b256,TransitiveCubic.s6,TransitiveCubic.s6Numerator,
    coeffA,coeffB,coeffC,coeffD,coeffE,coeffF,t]
  ring
end CyclePhysicalJacobianCoefficients
