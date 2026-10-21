# Maintaining the repository

Contributor instructions are in [CONTRIBUTING.md](CONTRIBUTING.md); this document covers the repository, acceptance pipeline, and website maintenance.

## Repository architecture

The project uses direct GitHub PRs with protected Lean verification, owner sign-off, and a trusted publication step. GitHub provides contributor identities, PRs, and discussions; the website backend handles GitHub sign-in and discussion access. Contribution format and checks are documented in [CONTRIBUTING.md](CONTRIBUTING.md); the review and publication procedure is described below.

Each instance lives permanently in `data/<id>/`. Its protected target and prospective context exist before a solve. A solve PR adds proof sources, an explanation, and optional witness data to that same folder. After a checked merge, the publisher adds an acceptance receipt and derives the canonical solution record. The atlas, explanations, PR links, and leaderboard are generated from these records.

`formal/lean/` pins the shared contract, Lean toolchain, and mathlib manifest. `scripts/proposals/` implements source restrictions, sandboxed compilation, kernel replay, theorem/axiom auditing, owner review, and publication. `.github/workflows/` invokes trusted base-branch code; candidate workflow and setup files are never executed as part of solve verification.

Treat the shared formal library as the Lean counterpart of the book: retain organized, generally useful machinery with explicit scope and concrete applications; keep failed experiments and instance-specific calculations out of it. Reusable constructions belong under `formal/lean/HodgeComputer/Constructions/` when they support concrete applications. Extract accepted machinery through a maintenance PR, preserving its attribution and the original acceptance-backed instance files. New solve PRs import the maintained library and supply their target-specific proof. Build changed shared modules, replay them with `leanchecker`, and check an application against the protected target before merging library changes. The protected dependency-cache key includes the shared Lean sources as well as the pinned toolchain and manifest.

`docs/index.json` and its Markdown sources define the expandable technical chapters. The content builder renders bundled KaTeX and local HTML. `assets/` contains local runtime scripts, styles, fonts, avatars, and meshes. `slices/` saves per-instance planes and cameras. The atlas and mathematical content are static; sign-in and discussions use the backend API.

The loopback preview watches content and UI files, rebuilds valid edits, and refreshes the browser while preserving its route. It defers refresh during free-camera exploration. Changes on `main` trigger `.github/workflows/deploy-website.yml`, which publishes the static website. Backend deployments are documented in `infra/aws/README.md`.

## Catalogue curation

The catalogue lists fixed instances of the existence problem in `formal/README.md`. `data/catalogue.json` determines displayed instance numbers; append new instances to preserve existing numbers. Solving or hiding an instance does not renumber other entries. The sidebar shows both open and solved targets by descending number. Previous/next navigation follows that same order. These numbers are presentation labels; proofs, discussion mappings, and acceptance records use stable instance IDs. Each instance has an exact statement, motivation, mathematical context, and saved visualization.

A target is open until a checked and merged PR has a validated acceptance receipt. The publisher derives solved status, contributor attribution, and leaderboard credit from that receipt. Solution files are first introduced by their solve PR and remain beside the target after acceptance.

Prospective context in `why.md` explains why the target is interesting without relying on its solution. The accepted `solution.md` explains the argument and its human mathematical sources. `provenance.json` links to the exact statement, mathematical context, discussion, and other atlas targets on the same sextic. Do not treat a restricted negative search as proof of nonexistence.

Adding or changing targets requires a separate owner-reviewed maintenance PR. Keep the variable order `X0, X1, X2, Y0, Y1, Y2`; check exact rational coefficients, sextic homogeneity, target degree `6q`, and parity under the sign involution. Maintain precise family scope and avoid claiming that a representative example proves a whole family. The catalogue is representative; solving its current entries need not settle the general conjecture.

Meshes are approximations for navigation and exploration. A real slice and camera do not provide evidence of smoothness, topology, or certificate validity. Preserve exact statements independently of rendering settings.

## Leaderboard

The board is generated from validated accepted solution records. Each distinct accepted instance gives one point to its direct PR author. Equal scores are ordered by when the contributors reached that score: compare the acceptance time (solve PR merge time) of each contributor's latest counted solve, earliest first. Alphabetical login order breaks an exact timestamp tie. Displayed ranks follow that order. Do not edit scores manually or award credit merely for local compilation, an unmerged proof, or a status flag.

`leaderboard/accounts.json` provides optional display names and locally bundled avatars. Other contributors use their GitHub login and GitHub-hosted avatar, including GitHub's default identicon when they have no custom picture. All avatars use the same dimensions within each view. `leaderboard/credits.json` is generated by `scripts/build-content.py` from acceptance-backed records. Scores and attribution have no GitHub API dependency at runtime.

Solver portraits link to the contributor's leaderboard entry; the construction header links to the actual merged PR from its receipt. The explanation records collaborators and prior mathematical sources. Documentation contributions retain their authorship but do not add solve points.

## Verification, sign-off, and publication

Solve contributions are direct GitHub PRs. The protected checker validates the exact target and proof, the owner signs off on the checked commit, and the owner merges it. A separate trusted publisher records acceptance and rebuilds the atlas and leaderboard. No workflow merges a PR automatically.

### Protected checks

Before preparing Lean, CI renders the proposed `solution.md` with the publication renderer, validates local file links against the protected checkout plus proposed files, and checks formulas with the bundled KaTeX. This check does not fetch external URLs or execute proposal code. `scripts/content.py` resolves ordinary Markdown links relative to the instance folder; existing repository-root artifact links remain supported.

`solve-proposal.yml` uses trusted base-branch code. Draft PRs wait until marked ready, or until the owner explicitly dispatches a check. Pinned protected Lean dependencies are cached between runs; each submitted proof is still compiled and checked independently. It fetches the PR as data and freezes the base and head commit IDs. A solve may add only permitted proof, witness, and explanation files to one existing `data/<id>/` folder. Existing target, context, infrastructure, and generated files are protected. A mixed solve/maintenance change fails even with owner approval; split it into separate PRs.

The checker generates `HodgeTarget` from the base record, and optional `HodgeWitness` from exact witness data. It compiles the proposal inside an OS sandbox, replays every submitted and protected module with `leanchecker` in a separate read-only process, and audits the protected theorem type and transitive axioms. Sequential replay bounds memory use even when a submission has many helpers; unused helpers are checked too. A submitted JSON witness requires an additional theorem binding the exact displayed polynomials to the same protected target. Printed claims are never verification evidence.

Candidate code receives no networking, credentials, or repository write access. Protected target artifacts, candidate artifacts, and the final trusted wrapper have separate write permissions. Linux uses Docker; local macOS checking uses `sandbox-exec`. The pinned toolchain, dependencies, verifier, and OS remain trusted components. Verification fails if isolation is unavailable.

The successful report records exact target/source hashes, base/head commits, the PR author, theorem, witness binding, toolchain, kernel replay, and axiom audit. The workflow posts `solve/lean` on the submitted commit and rejects a result if either PR commit changed during checking. For solve PRs, a green check means the proof passed; the result is ready for the owner to merge. No separate approving review is required.

### Owner sign-off

`.github/solve-policy.json` selects `live` mode and the account authorized to merge
solves. After a solve's `solve/lean` check succeeds, the owner reviews its explanation
and uses **Create a merge commit**. That merge is the sign-off. No separate approving
review is required, including when the owner authored the PR. The publisher checks
GitHub's `merged_by` identity against the configured owner; it does not grant credit
for a merge performed by another account. Repository write/merge access should remain
limited to the owner, with the trusted Actions publisher allowed to record acceptance.

If publication of an eligible, already-merged solve failed, rerun **Publish accepted
solve** with its PR number. It reuses the successful Lean check against the original
merge parents and source files. A changed head or base requires fresh verification
before merging. This retry cannot turn a failed or unchecked proof into an acceptance.

Maintenance PRs retain their explicit authorization requirement. For an owner-authored
maintenance PR, dispatch **Solve proposal** with its number and full reviewed head SHA
in `approved_head`. Both the original workflow actor and rerun actor must be the owner.

Use a **merge commit**, preserving the checked head as its second parent. Merge only against the checked base. Squash/rebase merges and base drift fail publication. When merging through GitHub CLI or an owner script, bind the merge request to the reviewed head SHA. Do not merge another solve until the previous publication commit has landed and the next proof has been checked against current main.

Branch protection or repository rulesets can require `solve/lean`, up-to-date branches, and maintainer-controlled merging. A failing workflow status does not itself prevent a merge unless the repository settings enforce it. `preview` mode is available for infrastructure experiments, but its receipts cannot be published as accepted solves.

### Trusted publication

`publish-solve.yml` runs on a merged PR or an explicit retry. It checks out trusted main and invokes `scripts/proposals/publish.py`. The publisher requires:

- The configured owner's merge of the checked head into this repository's main branch. The merge is the sign-off, regardless of PR authorship.
- A successful protected workflow run associated with the exact checked head and base.
- Matching workflow/verifier hashes and a matching preserved verification report.
- A merge commit whose parents are exactly the checked base and head.
- The same target and all proof, witness, and explanation hashes in the merged checkout.
- Contributor attribution matching the PR author.

The PR receives a separate `solve/publication` status linking to this workflow. It reports pending, successful, or failed publication independently of `solve/lean`, so a post-merge failure is visible from the PR. It then writes `data/<id>/acceptance.json`, derives `solution.rec`, and runs the content builder and validators. The workflow commits these derived files to main. A failed or interrupted publication leaves no accepted solve in published output; rerun the workflow once the cause is resolved. The generated acceptance record is durable even after transient CI artifacts expire.

Version 2 verification reports separate proof checking from owner authorization; the acceptance receipt records both. Version 1 reports retain their original meaning: a successful run already required owner authorization. Existing accepted solves and publication retries remain valid under that earlier evidence.

The atlas and leaderboard read generated files and need no GitHub service at runtime. Sign-in and discussions use the backend API. The publisher never awards credit from editable claimed identities, an unmerged proof, or a status flag. After acceptance, edit `solution.md` as ordinary reviewed documentation. The site renders the current explanation; the original submission remains in Git history and its acceptance record. Editorial changes do not require another Lean run or a new acceptance record. Changes to the target, Lean sources, proof manifest, or witness require renewed verification.

### Local checks

```sh
python3 scripts/proposals/test_check.py
python3 scripts/proposals/test_lean.py
```

The first checks file boundaries, schema, identity, and review logic. The second exercises the real Lean/sandbox path, including a small valid certificate and deliberately invalid inputs. These verifier regression tests belong to infrastructure changes; solve PRs run their actual submitted proof, not the regression suite. See [CONTRIBUTING.md](CONTRIBUTING.md#local-verification) for the contributor's local verification recipe.

## Visualization maintenance

`assets/surface.js` provides the page-side `HodgeRenderer` controller. `assets/surface-worker.js` runs `assets/renderer.js` in an OffscreenCanvas worker. The page watchdog pauses an unresponsive view after about five seconds so the atlas remains usable. A temporary background context loss permits one fresh worker and canvas on returning to the page. GPU objects from a lost context are discarded. Browsers without the required worker/canvas support retain the atlas without the 3D view.

The page-side interface is:

```js
const view = HodgeRenderer.create(canvas, {
  onStatus({state, message, meta}) {},
  onModeChange(mode) {}
});
await view.setCase(record);
view.setMode('free');
view.setMode('parallax'); // ease back to the saved pose
view.resetCamera();
view.destroy();
```

Creation is synchronous and does not select a case. `setCase` requests a load; use `onStatus` to observe when the surface is ready. The parent UI manages the challenge content, exploration toggle, status pill, and visualization guide. Free-camera controls are trackball rotation, right/shift-drag panning, wheel/pinch zoom, R or double-click to reset, and Escape to return.

Saved `render.mesh` manifests refer to compressed position/normal and index buffers under `assets/meshes/`. Each record's `render.camera` supplies its saved pose. `slices/` holds the corresponding plane and camera settings; see [slice curation](slices/curation.md). The homepage uses its separately saved Contact cone view in `slices/home.json`. Preserve the box at ±10, x-ray reach at 2.0, and the transparent edge fade. X-ray rendering uses up to six depth-peeling layers.

The numerical surface is obtained from `z = diag(1 or i) B u`, where the columns of the real 6×4 matrix `B` are orthonormal and `u` lies on the unit three-sphere. The phase choices must make the sextic restrict to a scalar-real polynomial. The renderer shows the stereographic projection of the antipodal sphere cover of the projective real slice. Its mesh cannot establish smoothness, topology, or certificate validity. Accepted denominator data controls divisor highlighting independently of the saved geometric mesh.

Meshes are generated offline. The repository ships the saved planes, cameras, and rendered mesh assets. When replacing a mesh, update its instance record and saved slice together. Equal-polynomial instances should share a slice unless an intentional presentation difference is documented.

Check finite values, normals, index bounds, projected extent, edge lengths, and polynomial residuals. Reject non-real phase restrictions rather than silently taking a real part. Compare refinements around narrow joins: a finite grid can miss small features. Use exact or direct polynomial evaluation to cross-check compact denominator evaluators. Renderer safety and denominator evaluation are exercised by `scripts/test-surface.cjs` and `scripts/test-divisor.cjs`; numerical checks remain presentation diagnostics.

A solve can prove the existential contract without the optional `witness.json` export. Such a proof still earns credit; its denominator must be extracted separately before it can be highlighted. A maintenance change may add `data/<id>/display-divisor.json`, citing the relevant definitions and supplying a polynomial program or numerical factors of a fully specified polynomial on a recorded slice. This presentation file does not modify the accepted proof, receipt, witness, or credit. It must not describe an arbitrary geometric curve as the certificate divisor. One reflection's program is compared symbolically with the accepted `fullD` by `python3 scripts/test-divisor-programs.py`.

The quadric-contact export is specified in `data/quadric-contact-broken/display-divisor.md`. Its conservative common clearing is explicit but nonminimal. On the saved slice, both parameters are fixed: the exporter isolates the 27 lines using complex ball arithmetic at 4,096-bit precision, checks their defining equations, pairs conjugate lines, and exports 17 polynomial factors in the six real coordinate amplitudes. Run `scripts/export-quadric-contact-divisor.py` with `numpy`, `PyYAML`, and `python-flint` installed to regenerate these coefficients. The factors are tied to the saved plane and phases; changes to either require a fresh export. A mesh refinement of the same section does not. The renderer evaluates the factors per pixel; it never reconstructs algebraic roots in the browser.

The pole-two holdout export is specified in `data/holdout-q2/display-divisor.md`. It supplies an explicit nonminimal clearing for the two endpoint certificates, then exports 27 conjugate-paired line factors and two coordinate factors on a fixed-ratio slice. Regenerate it with `scripts/export-holdout-q2-divisor.py`; run `scripts/test-holdout-q2-divisor.py` to check the extraction, degree bounds, and numerical norm comparisons. The twelve targets sharing the central holdout sextic now use a different common plane and camera. The old factors are preserved in `data/holdout-q2/fixed-slice-divisor.json`, but the pole-two divisor overlay is disabled: those coefficients must not be applied to a different slice without re-extraction.

All displayed denominators use per-pixel evaluation. Literal polynomials are compiled into multivariate Horner expressions; compact programs retain their arithmetic structure. The fragment shader evaluates each factor and its six ambient derivatives after the inverse stereographic map. Homogeneous coordinate rescaling reduces underflow; dividing by the gradient norm and using pixel derivatives gives curves a consistent antialiased width. Products and powers are displayed as the union of their factors' zero sets, without multiplicity. There is no vertex-sampling fallback. Generated expressions have a 4,096-node budget and run inside the existing visualization worker; context-loss handling and graphics timeouts remain active. Large formulas may still cost more on slower hardware.

`scripts/test-divisor.cjs` compares the generated expressions with independent direct polynomial arithmetic, including all saved divisors and every coordinate phase choice for the two large programs. `scripts/test-divisor-programs.py` checks the extracted One reflection and Hessian-trace formulas against their accepted Lean definitions. Numerical rendering does not replace the surface mesh with an exact surface. A divisor need not intersect a chosen real slice; absence of a bright curve does not imply missing certificate data.

When a literal denominator becomes an exact power on a special slice, a display program may declare `sliceIdentity: {"power": n}`. The content builder checks the polynomial identity `D(Bu) = g(Bu)^n` exactly, with the saved coordinate phases, before displaying `g = 0`. It rejects an incorrect identity or a denominator that vanishes on the entire slice. This removes interpolation artifacts from repeated factors without changing the divisor's support or the accepted witness. Hesse · radial quartic uses `X2 = X0`, where `D = (X0^2 + Y2^2/3)^2`; its displayed square root is only valid on this section.

Off-block tie · quartic similarly uses `Y1 = X0`, where `D = 2*(3*X0^2 + X1^2)^2`. Here `X0` and `Y1` are real and `X1` is imaginary, making the divisor visible as curves. Its display program uses `sqrt(2)*(3*X0^2 + X1^2)`, with the same exact restriction check.
