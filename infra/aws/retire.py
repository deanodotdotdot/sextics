#!/usr/bin/env python3
"""Retire previously published files and all unselected meshes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from public_files import is_public, is_safe_path

MANIFEST_KEY = "deployment/public-files.json"


def retired(previous, current):
    # The previous release establishes ownership even when a public root is removed.
    for keys, valid in ((previous, is_safe_path), (current, is_public)):
        if not isinstance(keys, list) or any(
            not isinstance(k, str) or not valid(k) for k in keys
        ):
            raise ValueError("Invalid public release manifest")
    return sorted(set(previous) - set(current))


def publish_manifest(bucket, manifest):
    current = json.loads(manifest.read_text())["publicKeys"]
    retired([], current)  # Validate before contacting storage.
    with tempfile.TemporaryDirectory(prefix="hodge-retire-") as directory:
        previous_file = Path(directory) / "previous.json"
        fetched = subprocess.run(
            [
                "aws",
                "s3api",
                "get-object",
                "--bucket",
                bucket,
                "--key",
                MANIFEST_KEY,
                str(previous_file),
            ],
            capture_output=True,
            text=True,
        )
        if fetched.returncode:
            if "(NoSuchKey)" not in fetched.stderr:
                raise RuntimeError(fetched.stderr)
            previous = []  # Other files need an earlier release manifest to establish ownership.
        else:
            previous = json.loads(previous_file.read_text())["publicKeys"]
        # Meshes predate release manifests. Inventory only their owned prefix so
        # the first managed deployment also removes old, unselected geometry.
        listed = subprocess.run(
            [
                "aws",
                "s3api",
                "list-objects-v2",
                "--bucket",
                bucket,
                "--prefix",
                "assets/meshes/",
                "--query",
                "Contents[].Key",
                "--output",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        meshes = json.loads(listed.stdout) or []
        if not isinstance(meshes, list) or any(
            not isinstance(key, str) or not key.startswith("assets/meshes/") for key in meshes
        ):
            raise ValueError("Invalid mesh inventory")
        obsolete = retired(previous + meshes, current)
        for offset in range(0, len(obsolete), 1000):
            result = subprocess.run(
                [
                    "aws",
                    "s3api",
                    "delete-objects",
                    "--bucket",
                    bucket,
                    "--delete",
                    json.dumps(
                        {
                            "Objects": [{"Key": key} for key in obsolete[offset : offset + 1000]],
                        }
                    ),
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            if json.loads(result.stdout).get("Errors"):
                raise RuntimeError(
                    "Some retired public files could not be deleted; retain the previous manifest for retry."
                )
        subprocess.run(
            [
                "aws",
                "s3",
                "cp",
                str(manifest),
                f"s3://{bucket}/{MANIFEST_KEY}",
                "--sse",
                "AES256",
                "--only-show-errors",
            ],
            check=True,
        )
        print(f"Retired {len(obsolete)} obsolete public files, including unused meshes.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    publish_manifest(args.bucket, args.manifest)
