# Reproduce the frozen handoff

This is an unsolved research snapshot, not a solve submission. Start with `HANDOFF-2026-10-23.md`. The prior 43-file published packet is linked there and remains unchanged. Some earlier scripts refer to unavailable original Mac files; no audit of those files is claimed.

## Environment

The principal current verifiers use Python 3.11 or later, SymPy, and python-flint 0.9.0. NumPy is optional for some older modular experiments. The snapshot's observed package versions are recorded in `environment-snapshot.json`. A fresh environment can be prepared with:

```sh
python3 -m venv .venv
.venv/bin/pip install sympy numpy python-flint==0.9.0
```

Run from this packet directory. Most current audit paths are relative to the scripts. Historical exploratory programs sometimes hard-code `/workspace/off-paired-research-new`, `/workspace/off-paired-sextics`, or other paths. Adapt those explicit paths before rerunning those programs, or reconstruct that directory layout. The complete frozen record is `live-instance.rec`; the original research worktree record differs only in rendering. Do not edit F,A,q or variable order when adapting paths.

## Principal exact checks

```sh
.venv/bin/python audit/theta/verify_generic_compact_connection.py
.venv/bin/python audit/theta/verify_full_base_connection.py
.venv/bin/python coupled-fresh/ruling-source/full-base-connection/build_source_euler_current.py
.venv/bin/python audit/theta/verify_source_euler_current.py
.venv/bin/python audit/theta/verify_j_source_current.py
.venv/bin/python coupled-fresh/genus4-gm-independent/verify_full_base_polynomial_potentials.py
.venv/bin/python coupled-fresh/theta-compact/remove_actual_N_j_poles.py
.venv/bin/python original-current/build_degree24_partial.py
```

Their results and scope are saved beside the scripts or in the audit directory. These are rational polynomial/quotient-ring identities, not Lean kernel checks. Producer scripts can rewrite their result JSON; the frozen manifest hashes refer to the files before any rerun. The last joint w/j extension has only its five scalar checks, not an independent rerun of the full rank-eight identity. Some older bounded modular screens and exploratory layouts have pending audits and must not be promoted to global obstructions.

The source-Euler builder is included before its audit because its input-hash dictionary uses absolute resolved paths and must be rebound after relocation. See `coupled-fresh/theta-compact/final-handoff.md` for complete array regeneration order.

The original-coordinate degree-24 script is self-contained except for python-flint, SymPy, and the standard library; it checks its embedded immutable F,A. A successful run verifies a **partial** identity and its nonzero remainder. It must not be treated as a certificate generator.

## Snapshot integrity and exclusions

`manifest.json` lists SHA256 hashes of all included files, except itself. Caches, machine-code executables, `.bin` modular matrices, and the saved HTML rendering of the public thread are omitted; source code, JSON arrays, mathematical notes, plain-text logs, the target record, and the complete API thread snapshot are retained. The manifest records every omitted path with its hash and size. The large exact JSON arrays are included without the old four-MiB cutoff.

Run the following from the packet directory to verify the frozen files:

```sh
python3 - <<'PY'
import hashlib,json,pathlib
m=json.load(open('manifest.json'))
for name,want in m['files'].items():
    p=pathlib.Path(name)
    assert p.is_file(), name
    assert hashlib.sha256(p.read_bytes()).hexdigest()==want, name
print('Verified', len(m['files']), 'files')
PY
```

Publication status and readback URLs are recorded outside the hashed mathematical snapshot to avoid a self-referential commit hash. No proof.json, Solution.lean, acceptance file or solve PR is supplied by this research publication.
