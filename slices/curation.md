# Saved real slices and cameras

Each `slices/<instance-id>.json` records the phase choices, orthonormal real four-plane, mesh, and camera used to visualize that instance. These settings must agree with `instance.rec` and the mesh manifest. The projected box is fixed at ±10, and x-ray reach is 2.0.

A camera has three fields: a unit quaternion `orientation` in `[x,y,z,w]` order, a `distance`, and a three-coordinate `center`. The quaternion maps the camera's right/up/back axes into world coordinates and is the sole saved orientation. Exploration and background parallax apply rotations directly to it; reset restores the saved pose.

Meshes sample the real section obtained by intersecting the chosen four-plane with the unit sphere and the sextic, then stereographically projecting into three dimensions. Their positions and normals are floating-point presentation data. They do not prove smoothness, topology, or certificate validity.

Validate finite values, normals, coordinate and index bounds, edge lengths, and polynomial residuals when replacing a mesh. `scripts/validate-records.py` checks consistency between the current records, saved slices, and mesh manifests. A finite grid can miss sufficiently thin features. Camera and slice choices are aesthetic decisions, independent of the mathematical target.

Denominators are evaluated directly at each pixel, independently of the geometric mesh. Compact formulas and slice-specific factorizations can be supplied through `data/<id>/display-divisor.json`; see MAINTAINING.md. A factorization restricted to a saved plane must be regenerated if that plane or its coordinate phases change. Open instances have no displayed denominator.

The homepage uses its separately saved Contact cone view in `home.json`. The Contact cone atlas entry uses `contact46006.json`.

Equal-sextic targets share the same geometric section and camera: the two Fermat targets, the two cross-block Two ties targets, the coupled Fano reflection and its complementary-character target, and the cyclic triple cover and its complementary-character target. Their accepted denominators, when available, are evaluated independently. Special sections used to expose repeated-factor divisors are checked by the exact `sliceIdentity` mechanism described in MAINTAINING.md.

Off-block tie and One tie intentionally use different sections. The special section that exposes the off-block quartic makes the other target's denominator vanish on surface components, producing broad highlights instead of divisor curves; One tie retains its general section.

The twelve central holdout targets share an unrestricted four-plane and camera. The pole-two target's divisor factorization requires a different, fixed-ratio section, retained in `data/holdout-q2/fixed-slice-divisor.json`; it is not applied to the atlas view. One reflection's residual sector uses a section with a fixed ratio between `Y1` and `Y0`, avoiding repeated-factor junctions in its divisor highlights. Its transverse sector has no exported denominator and uses a separate unrestricted four-plane. These choices do not change the exact instances or accepted certificates.
