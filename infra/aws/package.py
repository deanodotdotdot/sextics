#!/usr/bin/env python3
"""Build explicit public and Lambda artifacts; never copy the entire checkout."""
import argparse, hashlib, json, shutil, zipfile, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from public_files import POLICY, is_public, checked_file, selected_meshes


def package(source, site, output, static_only=False):
    output.mkdir(parents=True, exist_ok=True)
    public = output / "public"
    if public.exists():
        shutil.rmtree(public)
    public.mkdir()
    meshes = selected_meshes(site)
    keys = []
    for top in POLICY["files"] + POLICY["roots"]:
        item = site / top
        if item.is_symlink():
            raise ValueError(f"Public symlink refused: {item}")
        if not item.exists():
            raise ValueError(f"Missing public content: {top}")
        for file in [item] if item.is_file() else sorted(item.rglob("*")):
            if file.is_symlink():
                raise ValueError(f"Public symlink refused: {file}")
            if not file.is_file():
                continue
            relative = file.relative_to(site).as_posix()
            if not is_public(relative):
                continue
            if relative.startswith("assets/meshes/") and relative not in meshes:
                raise ValueError(f"Unused mesh file: {relative}")
            checked_file(site, relative)
            dest = public / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, dest)
            keys.append(relative)
    digest = None
    if not static_only:
        runtime_files = [
            "auth.mjs",
            "cache.mjs",
            "dynamo-store.mjs",
            "lambda-bridge.mjs",
            "lambda.mjs",
            "github.mjs",
            "comment-leaderboard.mjs",
            "server.mjs",
            "package.json",
            "package-lock.json",
        ]
        if not (source / "server/node_modules/@aws-sdk/client-dynamodb").is_dir():
            raise ValueError("Install the pinned server dependencies before packaging Lambda.")
        archive = output / "lambda.zip"
        with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
            for name in runtime_files:
                z.write(source / "server" / name, "server/" + name)
            for file in sorted((source / "server/node_modules").rglob("*")):
                if file.is_file() and not file.is_symlink():
                    z.write(file, file.relative_to(source))
            for name in [
                "data/catalogue.json",
                "discussions/index.json",
                "leaderboard/credits.json",
            ]:
                z.write(site / name, name)
            for name in ["assets/routes.js", "infra/aws/public-files.json"]:
                z.write(source / name, name)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    manifest = {
        "lambdaSha256": digest,
        "publicKeys": sorted(keys),
        "publicFiles": len(keys),
        "publicBytes": sum(p.stat().st_size for p in public.rglob("*") if p.is_file()),
    }
    (output / "build.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({k: v for k, v in manifest.items() if k != "publicKeys"}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Package content without rebuilding the Lambda service.",
    )
    args = parser.parse_args()
    package(
        Path(__file__).resolve().parents[2],
        args.site.resolve(),
        args.output.resolve(),
        args.static_only,
    )
