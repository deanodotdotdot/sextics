# Off-paired: verified compact residual reduction

> **Agent-only contribution:** generated and computationally checked by OpenAI Codex. `deanodotdotdot` has not personally reviewed or verified the mathematics. No certificate, unrestricted nonexistence proof, Lean proof, or accepted solve is claimed.

The preferred coupled current leaves an actual nonzero eight-row residual with common denominator Delta^3 only. [RESULTS.txt](RESULTS.txt) states the exact target, cutoff, source/field transport, corrected earlier local i-lift defect, complete single-direction exclusions, and remaining obligations. [VERIFICATION.json](VERIFICATION.json) records the 40-step exact replay and byte-for-byte residual reproduction.

## Reproduce

Use Python 3.12 with python-flint 0.9.0 and SymPy 1.14.0. In a writable copy of this directory:

```sh
python bootstrap.py
python code/verify_release.py --full
```

The bootstrap checks SHA256 before unpacking each exact JSON input. The full replay takes about 15 minutes in the recorded run. It regenerates the eight large residual numerator files, which are deliberately omitted from this compact public packet; their hashes are supplied. It then independently checks the generic product identity, the original-coordinate field on both deck branches, complete rational single-direction bounds, and the exact augmented minors. No network access is needed after obtaining this directory.

For a shorter check, after bootstrap:

```sh
python code/audit_actual_source.py
python code/independent_taylor_cutoff.py
python code/audit_source_fiber_normalization.py
python code/algebraic_taylor_original_field_check.py
DECK_SIGN=-1 python code/algebraic_taylor_original_field_check.py
python code/verify_bare_source_i_witness_stdlib.py
python code/verify_bare_source_j_witness_stdlib.py
python code/verify_bare_source_w_witness_stdlib.py
```

The final bare-source numerator bounds are i=12, j=8, w=20; the fixed preferred-current completion bounds are i=72, j=61, w=166. These exclude only the specified single-direction rational currents. Coupled changes and the unrestricted original certificate remain open. The current's nonzero original divergence is the expected audit outcome.

The old i-global-correction.json is retained as an input with a known j=0 defect. Its creation-time support assertion is superseded by i-original-lift-defect.json. The repaired current's creation-time audit-pending label is superseded by i-corrected-independent-audit.json and i-corrected-support-and-fiber-audit.json. Earlier Delta^12/Delta^11 constructions are superseded by taylor-discriminant-current.json.

Raw execution logs, local machine paths, private chat history and session-control files are excluded. The reproducible scripts, exact arrays, receipts and input hashes are supplied.

## Credit and source

Credit to `fqlx` for the frozen full compact connection, source interface and earlier pole currents; `benediamond` for the preceding contact obstruction and endpoint connection; and `deanodotdotdot` for earlier coordinate/character restrictions and authorization of this continuation. The new calculations and prose were produced by Codex.

Frozen upstream: [fqlx/sextics, commit f7a73cf](https://github.com/fqlx/sextics/tree/f7a73cf3346e1da8fded079f16b9e827f218902b/research/off-paired-2026-10-23). Discussion: [Broken paired signs](https://github.com/hodge-computer/sextics/discussions/57).
