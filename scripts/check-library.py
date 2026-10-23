#!/usr/bin/env python3
"""Build/replay changed shared Lean modules and recheck their accepted applications."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/proposals"))
from check import module_order, strip_comments
from sandbox import verify


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", args.base, "HEAD", "--", "formal/lean"], cwd=ROOT, text=True
    ).splitlines()
    if not changed:
        print("No shared Lean changes.")
        return
    lean = ROOT / "formal/lean"
    sources = {
        p.relative_to(lean).with_suffix("").as_posix().replace("/", "."): p
        for p in lean.rglob("*.lean")
        if ".lake" not in p.relative_to(lean).parts
    }
    imports = {
        name: set(re.findall(r"^import\s+([^\n]+)", strip_comments(p.read_text()), re.M))
        for name, p in sources.items()
    }
    imports = {
        name: {item for line in lines for item in line.split()} for name, lines in imports.items()
    }
    affected = {
        Path(p).relative_to("formal/lean").with_suffix("").as_posix().replace("/", ".")
        for p in changed
        if p.endswith(".lean")
    }
    if any(not p.endswith(".lean") for p in changed):
        affected.update(sources)
    while True:
        expanded = affected | {name for name, deps in imports.items() if deps & affected}
        if expanded == affected:
            break
        affected = expanded
    modules = sorted(affected & sources.keys())
    if modules:
        subprocess.run(["lake", "build", *modules], cwd=lean, check=True)
        for module in modules:
            subprocess.run(
                ["lake", "env", "leanchecker", "--verbose", module], cwd=lean, check=True
            )
    policy = json.loads((ROOT / ".github/solve-policy.json").read_text())
    applications = 0
    for receipt in sorted((ROOT / "data").glob("*/acceptance.json")):
        folder = receipt.parent
        files = {p.name: p.read_bytes() for p in folder.glob("*.lean")}
        if (folder / "witness.json").exists():
            files["witness.json"] = (folder / "witness.json").read_bytes()
        order, used = module_order(files)
        # Every application imports the protected target, hence Verify implicitly.
        if not (set(used) | {"HodgeComputer.Verify"}) & affected:
            continue
        with tempfile.TemporaryDirectory(prefix="hodge-library-") as temporary:
            verify(
                ROOT,
                files,
                yaml.safe_load((folder / "instance.rec").read_text()),
                json.loads((folder / "proof.json").read_text()),
                order,
                used,
                policy,
                Path(temporary),
            )
        applications += 1
        print(f"Checked protected application: {folder.name}", flush=True)
    print(
        f"Replayed {len(modules)} shared modules and checked {applications} accepted applications."
    )


if __name__ == "__main__":
    main()
