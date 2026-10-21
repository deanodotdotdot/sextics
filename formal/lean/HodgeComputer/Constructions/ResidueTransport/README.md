# Residue transport and moving cubic maps

These modules express two reusable transport identities and a coordinate-independence criterion from `hodgepodgeconjecture`'s [cyclic cubic construction](https://github.com/hodge-computer/sextics/pull/165). The Piola and residue framework builds on `fqlx` and the Hodge Computer collaborators. The original construction acknowledges OpenAI Codex assistance.

Import `HodgeComputer.Constructions.ResidueTransport`, or an individual module separately.

| Module | Main statements | Application obligations |
| --- | --- | --- |
| `Density` | `CycleResidueTransport.change_density`, `piola_pullback` | Nonzero normal derivatives; inverse coordinate matrices; the chain rule and equality of mixed partials. The multiplier is the ratio of normal derivatives times the coordinate determinant. |
| `MovingMap` | `CycleMovingMap.moving_weierstrass_jet`, `residue_source_from_jet`, `moving_weierstrass_source` | The cubic equation, invariant differential identity, and compatible first variations. The jet form applies at a fixed parameter value without assuming a parameter derivation on the specialized field. |
| `CoordinateIndependence` | `ResidueCoordinateIndependence.injective_of_coordinate_derivations` | Characteristic zero, derivations fixing the coefficient field, and the identity matrix of coordinate derivatives. These imply injectivity of polynomial evaluation by degree descent. |

These identities transport a primitive; they do not construct one on an arbitrary elliptic family. The cyclic application supplies its own covariants, polynomial-curve incidence, normal, source, field embedding, and legal homogeneous clearing. Neither an arbitrary rational source nor a higher-pole target is automatically covered.

[Chapter 2, §2.9](../../../../../docs/02-explicit-constructions.md#29-moving-cubic-maps-and-jacobian-residue-transport) develops the mathematical identities. The accepted application is assembled in [PhysicalPrimitive.lean](../../../../../data/cycle-three/PhysicalPrimitive.lean). Its original modules remain unchanged as verification evidence. The two transport identities retain their original declaration namespaces; the coordinate criterion uses `ResidueCoordinateIndependence`. Import the maintained transport modules instead of the original `MovingMap` and `ResidueTransport` copies, not alongside them.
