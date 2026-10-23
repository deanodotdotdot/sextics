#!/usr/bin/env python3
"""Validate static records. This script is not a formal proof verifier."""
import argparse
import json
import math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def polynomial(poly, degree, parity=None):
    require(
        isinstance(poly.get("expression"), str) and poly["expression"], "missing exact expression"
    )
    terms = poly.get("terms")
    require(bool(terms), "zero polynomial supplied as a target or denominator")
    seen = set()
    for coefficient, powers in terms:
        require(isinstance(coefficient, str), "exact coefficient must be a rational string")
        require(Fraction(coefficient) != 0, "zero coefficient in sparse data")
        require(
            len(powers) == 6 and all(type(e) is int and e >= 0 for e in powers),
            "invalid exponent vector",
        )
        require(sum(powers) == degree, f"nonhomogeneous polynomial of expected degree {degree}")
        if parity is not None:
            require(sum(powers[3:]) % 2 == parity, "wrong simultaneous Y parity")
        require(tuple(powers) not in seen, "duplicate monomial")
        seen.add(tuple(powers))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    index = json.loads((ROOT / "assets/atlas/index.json").read_text())
    ids = set()
    explicit = 0
    proved = 0
    for summary in index["records"]:
        rid = summary["id"]
        require(rid not in ids and "/" not in rid and ".." not in rid, "duplicate or unsafe ID")
        ids.add(rid)
        record = json.loads((ROOT / summary['path']).read_text())
        folder = ROOT / "data" / rid
        require(
            (folder / "why.md").is_file() and (folder / "provenance.json").is_file(),
            f"{rid}: missing rationale or audit",
        )
        require(
            record["status"] == ("solved" if (folder / "solution.rec").exists() else "open"),
            f"{rid}: status is not derived from solution",
        )
        require(summary["status"] == record["status"], f"{rid}: status index mismatch")
        require(record["id"] == rid, f"{rid}: mismatched ID")
        require(record["q"] in (1, 2), f"{rid}: invalid q")
        polynomial(record["F"], 6, 0)
        polynomial(record["A"], 6 * record["q"], 1)
        available = record.get("certificateAvailable", False)
        if available:
            explicit += 1
            require(
                record.get("evidenceKind") in ("explicit-certificate", "existence-proof"),
                f"{rid}: inconsistent evidence kind",
            )
            if "D" in record:
                polynomial(record["D"], record["D"]["degree"])
            require(record.get("credit", {}).get("githubLogin"), f"{rid}: missing attribution")
            require((folder / "solution.md").stat().st_size > 0, f"{rid}: missing explanation")
        else:
            require("D" not in record, f"{rid}: open target has a displayed denominator")
            require(
                not record["render"].get("divisorTerms"),
                f"{rid}: open target has divisor rendering",
            )
            require(
                not record["render"].get("divisorProgram"),
                f"{rid}: open target has divisor rendering",
            )
        if record.get("formalStatus") == "proved":
            proved += 1
            require(
                (ROOT / "data" / rid / "acceptance.json").is_file(),
                f"{rid}: missing acceptance receipt",
            )
        require(
            record.get("formalStatus") == ("proved" if available else "unproved"),
            f"{rid}: inconsistent formal status",
        )
        render = record["render"]
        require(
            render.get("phaseSigns") and len(render["phaseSigns"]) == 6,
            f"{rid}: missing phase choice",
        )
        require(
            render.get("planeMatrix") and len(render["planeMatrix"]) == 6,
            f"{rid}: missing saved plane",
        )
        plane = render["planeMatrix"]
        require(
            all(
                len(row) == 4 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in row)
                for row in plane
            ),
            f"{rid}: invalid plane matrix",
        )
        require(
            all(
                abs(sum(row[i] * row[j] for row in plane) - int(i == j)) < 1e-10
                for i in range(4)
                for j in range(4)
            ),
            f"{rid}: plane columns are not orthonormal",
        )
        camera = render.get("camera", {})
        require(
            set(camera) == {"orientation", "distance", "center"}
            and isinstance(camera.get("distance"), (int, float))
            and math.isfinite(camera["distance"]),
            f"{rid}: missing finite saved camera",
        )
        require(
            camera["distance"] > 0
            and len(camera.get("center", [])) == 3
            and all(math.isfinite(v) for v in camera["center"]),
            f"{rid}: invalid camera framing",
        )
        orientation = camera.get("orientation")
        require(
            isinstance(orientation, list)
            and len(orientation) == 4
            and all(isinstance(v, (int, float)) and math.isfinite(v) for v in orientation),
            f"{rid}: invalid camera orientation",
        )
        require(
            abs(sum(v * v for v in orientation) - 1) < 1e-10,
            f"{rid}: camera orientation is not a unit quaternion",
        )
        phases = {
            sum(e for e, sign in zip(powers, render["phaseSigns"]) if sign < 0) % 2
            for _, powers in record["F"]["terms"]
        }
        require(
            len(phases) == 1, f"{rid}: phase choice does not yield a real polynomial up to scalar"
        )
        mesh_relative = render.get("mesh")
        require(mesh_relative, f"{rid}: missing mesh reference")
        mesh_path = (ROOT / "assets" / mesh_relative).resolve()
        require(
            mesh_path.is_relative_to(ROOT / "assets/meshes") and mesh_path.exists(),
            f"{rid}: missing local mesh",
        )
        mesh = json.loads(mesh_path.read_text())
        require(
            mesh.get("meta", {}).get("planeMatrix") == plane,
            f"{rid}: mesh does not match the saved plane",
        )
        require(
            mesh.get("projectionBox", mesh.get("meta", {}).get("projectionBox")) == 10,
            f"{rid}: incorrect box",
        )
        for value in mesh.values():
            if isinstance(value, str) and value.endswith(".gz"):
                require((mesh_path.parent / value).exists(), f"{rid}: missing binary mesh asset")
        require(
            summary.get("formalStatus") == record["formalStatus"],
            f"{rid}: index formal status mismatch",
        )
        for source in record.get("sources", []):
            require((ROOT / source["path"]).is_file(), f"{rid}: missing research source")
        if record.get("certificate", {}).get("packet"):
            require(
                (ROOT / record["certificate"]["packet"]).is_file(), f"{rid}: missing witness packet"
            )

    print(
        f"Validated {len(ids)} records: {explicit} accepted certificates, {len(ids)-explicit} open targets, {proved} accepted Lean proofs."
    )
    print(
        "Exact coefficient encodings, degrees, parities, saved real slices, and local asset references passed."
    )


if __name__ == "__main__":
    main()
