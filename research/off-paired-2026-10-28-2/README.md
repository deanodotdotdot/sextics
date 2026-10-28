# Off-paired: coupled correction at the double-node slices

> **Agent-only contribution:** generated and computationally checked by OpenAI Codex. `deanodotdotdot` has not personally reviewed or verified the mathematics and does not claim expertise in formal mathematics. This is partial research; no certificate, Lean proof or accepted solve is claimed.

An explicit coupled physical current cancels the double-node factor in all eight actual weighted residuals on both `j=1` and `j=-1`. A cubic patch preserves the previous boundary cancellations: the generic residual has denominator support contained in `i,L,Delta`, and the sixteen expanded slice rows have support only `i,L,H1`. The residual is nonzero. The earlier Delta-only current remains the preferred global support reduction; combining these advantages remains open.

[RESULTS.txt](RESULTS.txt) gives the exact target, formulas, rational Bezout certificate, scope and remaining obligations. [COUPLED-NORMAL-IDEAL.txt](COUPLED-NORMAL-IDEAL.txt) gives the separate characteristic-zero scalar unit-ideal argument. Exact critical-cover residue formulas and twelve logarithmic vector fields are also supplied. [VERIFICATION.json](VERIFICATION.json) records the clean replay.

## Reproduce

Use Python 3.12 with `python-flint==0.9.0` and `sympy==1.14.0`. In a writable copy:

```sh
python bootstrap.py
python code/verify_incremental_release.py
```

The public bootstrap validates and decompresses the exact inputs and expanded residuals. The local uncompressed packet can run the verifier directly. The verifier regenerates both sets of sixteen residual rows, compares their SHA256 hashes, reconstructs the patched rows independently from the native connection, checks exact rational identities with a second polynomial engine, and checks the actual original-coordinate field on both deck branches. Allow several minutes. Replays write audit receipts and logs, so use a copy to preserve the release manifest.

For a short independent arithmetic check after bootstrap:

```sh
python code/independent_two_node_improved_audit.py
python code/independent_patched_audit.py
python code/independent_critical_residue.py
```

The explicit `i^4(1+w^3)` Bezout identity is verified over the rationals. Finite-field rank choices used during its discovery are not its proof. The broader scalar unit-ideal argument exports no global multipliers and does not establish an eight-row closure.

## Sources and credit

This is an incremental continuation of the [first frozen packet](https://github.com/deanodotdotdot/sextics/tree/844dc49f48ecd8109c19bc19503dfcf004c18c88/research/off-paired-2026-10-28), using the [frozen upstream connection](https://github.com/fqlx/sextics/tree/f7a73cf3346e1da8fded079f16b9e827f218902b/research/off-paired-2026-10-23). Necessary exact inputs are included here. Credit to `fqlx`, `benediamond`, and `deanodotdotdot` retains the scopes stated in RESULTS.txt. Discussion: [Broken paired signs](https://github.com/hodge-computer/sextics/discussions/57).

Raw execution logs, machine paths, private chat history and session-control files are excluded from the public packet. Stopped or bounded searches do not establish unrestricted nonexistence.
