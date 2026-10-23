#!/usr/bin/env python3
"""Offline curvature refinement for meshes with the stereographic quadratic color field.

Usage: refine-surface.py INPUT_MANIFEST RECORD_JSON OUTPUT_MANIFEST
Requires NumPy. Preserves source vertices and rejects face reversals; does not
change the slice, camera, or atlas selection. New samples lie on the implicit
polynomial to numerical precision, not on a cosmetically smoothed surface.
"""
import json, gzip, sys
from fractions import Fraction
from pathlib import Path
import numpy as np

# Distances below use the mesh's normalized display coordinates.
REFINEMENT_PASSES = 4
PROJECTION_STEPS = 12
MIDPOINT_ERROR = 0.0003
CURVED_NORMAL_COSINE = 0.985
SHARP_NORMAL_COSINE = 0.9659
MIN_SHARP_EDGE_LENGTH = 0.00025
MAX_PROJECTION_STEP_FRACTION = 0.1
MAX_MIDPOINT_SHIFT_FRACTION = 0.4

if len(sys.argv) != 4:
    raise SystemExit(__doc__)
source, record_path, destination = map(Path, sys.argv[1:])
manifest = json.loads(source.read_text())
meta = manifest["meta"]
record = json.loads(record_path.read_text())
if meta.get("stride") != 9:
    raise ValueError("Expected interleaved position/normal/color data")
v = (
    np.frombuffer(gzip.decompress((source.parent / manifest["vertices"]).read_bytes()), dtype="<f4")
    .reshape(-1, 9)
    .astype(float)
)
f = (
    np.frombuffer(gzip.decompress((source.parent / manifest["indices"]).read_bytes()), dtype="<u4")
    .reshape(-1, 3)
    .copy()
)
B = np.array(meta["planeMatrix"])
scale = meta["displayScale"]
center = np.array(meta["centerOriginal"])
if not np.allclose(B, record["render"]["planeMatrix"], rtol=0, atol=1e-14):
    raise ValueError("Record plane does not match mesh")
if meta["phaseSigns"] != record["render"]["phaseSigns"]:
    raise ValueError("Record phases do not match mesh")
terms = []
phases = set()
for coef, exps in record["F"]["terms"]:
    phase = sum(e for e, sign in zip(exps, meta["phaseSigns"]) if sign < 0) % 4
    phases.add(phase % 2)
    terms.append((float(Fraction(str(coef))) * (-1 if phase >= 2 else 1), exps))
if len(phases) > 1:
    raise ValueError("The restricted polynomial is not scalar-real")
# Only regenerate an observable whose identity has been checked against the source.
q = v[:, :3] * scale + center
abc = 2 * q / (1 + np.sum(q * q, axis=1))[:, None]
a, b, c = abc.T
expected = np.column_stack((a * a - b * b + 0.5 * c * c, 2 * a * b)) / meta["complexScale"]
if not np.allclose(expected, v[:, 6:8], atol=2e-5, rtol=2e-5):
    raise ValueError("This mesh uses a different color observable")


def calc(*coords):
    powers = [[np.ones_like(z)] + [z**e for e in range(1, 7)] for z in coords]
    out = [np.zeros_like(coords[0]) for _ in range(7)]
    for coef, exps in terms:
        value = np.full_like(coords[0], coef)
        for i, e in enumerate(exps):
            value *= powers[i][e]
        out[0] += value
        for k, e in enumerate(exps):
            if not e:
                continue
            value = np.full_like(coords[0], coef * e)
            for i, ei in enumerate(exps):
                value *= powers[i][ei - (i == k)]
            out[k + 1] += value
    return out


def field(p):
    q = p * scale + center
    den = 1 + np.sum(q * q, axis=1)
    sphere = np.column_stack((2 * q, den - 2)) / den[:, None]
    ambient = sphere @ B.T
    vals = calc(*ambient.T)
    g = np.column_stack(vals[1:]) @ B
    grad = (
        2 * g[:, :3] / den[:, None]
        + 4 * q * (g[:, 3] - np.sum(q * g[:, :3], axis=1))[:, None] / den[:, None] ** 2
    )
    return vals[0], grad * scale


def project(p, limit):
    out = p.copy()
    for _ in range(PROJECTION_STEPS):
        z, g = field(out)
        delta = z[:, None] * g / np.maximum(np.sum(g * g, axis=1), 1e-30)[:, None]
        delta *= np.minimum(1, limit / np.maximum(np.linalg.norm(delta, axis=1), 1e-30))[:, None]
        out -= delta
    return out


def attributes(p):
    z, g = field(p)
    g /= np.maximum(np.linalg.norm(g, axis=1), 1e-30)[:, None]
    q = p * scale + center
    abc = 2 * q / (1 + np.sum(q * q, axis=1))[:, None]
    a, b, c = abc.T
    phase = np.column_stack((a * a - b * b + 0.5 * c * c, 2 * a * b)) / meta["complexScale"]
    return np.column_stack((p, g, phase, np.zeros(len(p))))


for it in range(REFINEMENT_PASSES):
    p = v[:, :3]
    edges, inv = np.unique(
        np.sort(f[:, [[0, 1], [1, 2], [2, 0]]].reshape(-1, 2), axis=1), axis=0, return_inverse=True
    )
    inv = inv.reshape(-1, 3)
    mids = p[edges].mean(axis=1)
    length = np.linalg.norm(p[edges[:, 0]] - p[edges[:, 1]], axis=1)
    corrected = project(mids, MAX_PROJECTION_STEP_FRACTION * length)
    err = np.linalg.norm(corrected - mids, axis=1)
    normals = v[edges, 3:6]
    angle = np.sum(normals[:, 0] * normals[:, 1], axis=1)
    curved = (err > MIDPOINT_ERROR) & (angle < CURVED_NORMAL_COSINE)
    sharp = (angle < SHARP_NORMAL_COSINE) & (length > MIN_SHARP_EDGE_LENGTH)
    safe_shift = err < MAX_MIDPOINT_SHIFT_FRACTION * length
    selected = (curved | sharp) & safe_shift
    print(
        it,
        "faces",
        len(f),
        "split",
        int(selected.sum()),
        "error quantiles",
        np.quantile(err, [0.5, 0.9, 0.99, 1]).tolist(),
        "unresolved",
        int((~safe_shift).sum()),
        flush=True,
    )
    if not selected.any():
        break
    oldn = len(v)
    oldv = v
    oldf = f

    def triangulate(ids):
        new = []
        parents = []
        for parent, ((a, b, c), (ab, bc, ca)) in enumerate(zip(oldf, ids[inv])):
            mask = int(ab >= 0) + 2 * int(bc >= 0) + 4 * int(ca >= 0)
            if mask == 0:
                tris = [(a, b, c)]
            elif mask == 1:
                tris = [(a, ab, c), (ab, b, c)]
            elif mask == 2:
                tris = [(b, bc, a), (bc, c, a)]
            elif mask == 4:
                tris = [(c, ca, b), (ca, a, b)]
            elif mask == 3:
                tris = [(ab, b, bc), (a, ab, c), (ab, bc, c)]
            elif mask == 6:
                tris = [(bc, c, ca), (b, bc, a), (bc, ca, a)]
            elif mask == 5:
                tris = [(ca, a, ab), (c, ca, b), (ca, ab, b)]
            else:
                tris = [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
            new.extend(tris)
            parents.extend([parent] * len(tris))
        return np.array(new, dtype="<u4"), np.array(parents)

    oldcross = np.cross(p[oldf[:, 1]] - p[oldf[:, 0]], p[oldf[:, 2]] - p[oldf[:, 0]])
    for retry in range(20):
        ids = np.full(len(edges), -1, dtype=np.int64)
        ids[selected] = np.arange(oldn, oldn + selected.sum())
        v = np.vstack((oldv, attributes(corrected[selected])))
        f, parents = triangulate(ids)
        q = v[:, :3]
        cross = np.cross(q[f[:, 1]] - q[f[:, 0]], q[f[:, 2]] - q[f[:, 0]])
        bad = (np.sum(cross * v[f, 3:6].sum(axis=1), axis=1) <= 0) | (
            np.sum(cross * oldcross[parents], axis=1) <= 0
        )
        if not bad.any():
            break
        remove = np.unique(inv[np.unique(parents[bad])])
        count = int(selected[remove].sum())
        selected[remove] = False
        print("  reject unsafe splits", count, flush=True)
        if not count:
            raise ValueError("Original invalid face")
    else:
        raise ValueError("Refinement orientation did not converge")
# Report winding consistency rather than silently invert problematic faces.
p = v[:, :3]
cross = np.cross(p[f[:, 1]] - p[f[:, 0]], p[f[:, 2]] - p[f[:, 0]])
alignment = np.sum(cross * v[f, 3:6].sum(axis=1), axis=1)
print("faces vs smooth normal negative", int((alignment < 0).sum()), "total", len(f), flush=True)
key = destination.stem
mdir = destination.parent
mdir.mkdir(parents=True, exist_ok=True)
data = v.astype("<f4")
out = {
    **manifest,
    "vertices": key + ".vertices.bin.gz",
    "indices": key + ".indices.bin.gz",
    "meta": {**meta},
}
m = out["meta"]
m.update(
    vertexCount=len(v),
    triangleCount=len(f),
    geometryBytes=data.nbytes + f.nbytes,
    adaptiveRefinement="4 conforming edge-subdivision passes; curvature-weighted implicit midpoint error 0.0003; 15-degree normal refinement; bounded Newton projection; reject face reversals",
)
m["min"] = v[:, :3].min(axis=0).tolist()
m["max"] = v[:, :3].max(axis=0).tolist()
if not np.isfinite(data).all() or not np.isfinite(f).all():
    raise ValueError("Nonfinite mesh")
if f.max() >= len(data):
    raise ValueError("Invalid index")
if (alignment <= 0).any():
    raise ValueError("Face orientation failed")
if np.max(np.abs(np.linalg.norm(v[:, 3:6], axis=1) - 1)) > 0.015:
    raise ValueError("Invalid normal")
if np.max(abs(v[:, :3])) > 1.01:
    raise ValueError("Mesh exceeds display bounds")
m["maxEdge"] = float(np.linalg.norm(p[f] - np.roll(p[f], 1, axis=1), axis=2).max())
m["edgeBound"] = max(m["edgeBound"], m["maxEdge"] + 1e-5)
for name, a in [("vertices", data), ("indices", f)]:
    (mdir / out[name]).write_bytes(gzip.compress(a.tobytes(), compresslevel=9, mtime=0))
destination.write_text(json.dumps(out) + "\n")
print("bytes", sum((mdir / out[k]).stat().st_size for k in ["vertices", "indices"]), flush=True)
