"""The release boundary must exclude private/server material and symlinks."""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "release_package", Path(__file__).with_name("package.py")
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

retire_spec = importlib.util.spec_from_file_location(
    "retirement", Path(__file__).with_name("retire.py")
)
retirement = importlib.util.module_from_spec(retire_spec)
retire_spec.loader.exec_module(retirement)


class PublicPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / "site"
        self.output = self.root / "release"
        for directory in ["assets", "data/example", "leaderboard", "discussions", "docs"]:
            (self.site / directory).mkdir(parents=True)
        (self.site / "index.html").write_text("<h1>Public site</h1>")

        self.write("data/index.json", {"records": []})
        self.write("assets/home-scene.json", {"mesh": "meshes/selected.json"})
        self.write("assets/meshes/selected.json", {"vertices": "selected.bin.gz"})
        (self.site / "assets/meshes/selected.bin.gz").write_bytes(b"mesh")

    def write(self, name, value):
        target = self.site / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value))

    def build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            release.package(self.site, self.site, self.output, static_only=True)

    def test_public_release_excludes_private_and_unlisted_material(self):
        for name in [
            ".git/config",
            ".env",
            "server/github-app.json",
            "private-services/app.json",
            "node_modules/dependency.js",
            "data/.private/token.json",
            "assets/unexpected.exe",
            "CONTRIBUTING.md",
            "MAINTAINING.md",
        ]:
            target = self.site / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("PRIVATE-TEST-CONTENT")
        (self.site / "data/example/instance.rec").write_text("F = exact target")
        (self.site / "assets/app.js").write_text("/* public code */")
        (self.site / "docs/index.json").write_text('{"pages": []}')
        (self.site / "docs/overview.md").write_text("The mathematical book.")
        (self.site / "docs/overview.html").write_text("<p>The mathematical book.</p>")
        self.build()
        files = {
            str(p.relative_to(self.output / "public"))
            for p in (self.output / "public").rglob("*")
            if p.is_file()
        }
        self.assertEqual(
            files,
            {
                "index.html",
                "assets/app.js",
                "data/example/instance.rec",
                "docs/index.json",
                "docs/overview.md",
                "docs/overview.html",
                "data/index.json",
                "assets/home-scene.json",
                "assets/meshes/selected.json",
                "assets/meshes/selected.bin.gz",
            },
        )
        self.assertFalse((self.output / "lambda.zip").exists())

    def test_symlink_cannot_escape_the_public_boundary(self):
        private = self.root / "private.json"
        private.write_text("PRIVATE-TEST-CONTENT")
        (self.site / "data/example/leak.json").symlink_to(private)
        with self.assertRaisesRegex(ValueError, "Public symlink refused"):
            self.build()

    def test_retirement_removes_obsolete_meshes_and_other_managed_files(self):
        self.assertEqual(
            retirement.retired(
                ["assets/old.js", "assets/meshes/old.gz", "docs/current.html"],
                ["docs/current.html"],
            ),
            ["assets/meshes/old.gz", "assets/old.js"],
        )
        for key in ["notifications/discord-state.json", "../private.json", "/data/file.json"]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                retirement.retired([key], [])

    def test_top_level_symlink_is_refused(self):
        (self.site / "docs").rmdir()
        private = self.root / "private"
        private.mkdir()
        (private / "secret.json").write_text("secret")
        (self.site / "docs").symlink_to(private, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Public symlink refused"):
            self.build()

    def test_unused_meshes_fail_packaging(self):
        self.write("assets/meshes/unused.json", {"vertices": "unused.bin.gz"})
        (self.site / "assets/meshes/unused.bin.gz").write_bytes(b"unused")
        with self.assertRaisesRegex(ValueError, "Unused mesh file"):
            self.build()

    def test_first_release_retires_old_meshes_and_keeps_manifest_on_delete_failure(self):
        manifest = self.root / "build.json"
        manifest.write_text(json.dumps({"publicKeys": ["assets/meshes/selected.json"]}))
        for failed in [False, True]:
            calls = []

            def aws(args, **kwargs):
                calls.append(args)
                if args[2] == "get-object":
                    return CompletedProcess(args, 1, stdout="", stderr="(NoSuchKey)")
                if args[2] == "list-objects-v2":
                    self.assertEqual(args[args.index("--prefix") + 1], "assets/meshes/")
                    return CompletedProcess(
                        args,
                        0,
                        stdout=json.dumps(
                            ["assets/meshes/selected.json", "assets/meshes/unused.json"]
                        ),
                    )
                if args[2] == "delete-objects":
                    self.assertEqual(
                        json.loads(args[args.index("--delete") + 1])["Objects"], [{"Key": "assets/meshes/unused.json"}]
                    )
                    return CompletedProcess(
                        args,
                        0,
                        stdout=json.dumps({"Errors": [{"Code": "AccessDenied"}]} if failed else {}),
                    )
                self.assertEqual(args[:3], ["aws", "s3", "cp"])
                return CompletedProcess(args, 0)

            with patch.object(retirement.subprocess, "run", side_effect=aws):
                if failed:
                    with self.assertRaisesRegex(RuntimeError, "previous manifest"):
                        retirement.publish_manifest("test-bucket", manifest)
                else:
                    with contextlib.redirect_stdout(io.StringIO()):
                        retirement.publish_manifest("test-bucket", manifest)
            self.assertEqual(any(c[1:3] == ["s3", "cp"] for c in calls), not failed)

    def test_mesh_stream_cannot_escape_its_directory(self):
        self.write("assets/meshes/selected.json", {"vertices": "../../server/secret.json"})
        with self.assertRaisesRegex(ValueError, "Unsafe mesh stream"):
            self.build()


if __name__ == "__main__":
    unittest.main()
