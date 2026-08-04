#!/usr/bin/env python3
"""Deterministic tests for the generated InfusionCalc offline bundle."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from offline_pwa import (
    OFFLINE_MANIFEST_FILENAME,
    OfflinePwaError,
    collect_offline_files,
    inject_service_worker,
    sanitize_build_id,
    validate_offline_build,
    write_build_info,
    write_offline_manifest,
)


class OfflinePwaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.build_dir = Path(self.temporary_directory.name) / "build"
        self.build_dir.mkdir()
        self.build_id = "test-build-123"

        repository_root = Path(__file__).resolve().parents[1]
        shutil.copyfile(
            repository_root / "web" / "pwa_service_worker.js",
            self.build_dir / "pwa_service_worker.js",
        )

        files = {
            "index.html": "<html></html>",
            "flutter_bootstrap.js": "bootstrap();",
            "main.dart.js": "main();",
            "manifest.json": json.dumps(
                {
                    "name": "InfusionCalc",
                    "display": "standalone",
                    "start_url": ".",
                },
            ),
            "analytics.js": "analytics();",
            "pwa_install.js": "install();",
            "apple-touch-icon.png": "icon",
            "icons/Icon-192.png": "icon",
            "icons/Icon-512.png": "icon",
            "assets/AssetManifest.bin.json": "{}",
            "assets/fonts/MaterialIcons-Regular.otf": "font",
            "canvaskit/canvaskit.wasm": "wasm",
            "canvaskit/canvaskit.js": "renderer();",
        }
        for relative, content in files.items():
            path = self.build_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def _finalize(self) -> list[str]:
        files = collect_offline_files(self.build_dir)
        manifest = json.loads(
            (self.build_dir / "manifest.json").read_text(encoding="utf-8"),
        )
        write_offline_manifest(
            self.build_dir,
            build_id=self.build_id,
            files=files,
        )
        write_build_info(
            self.build_dir,
            build_id=self.build_id,
            files=files,
            manifest=manifest,
        )
        inject_service_worker(
            self.build_dir / "pwa_service_worker.js",
            build_id=self.build_id,
            files=files,
        )
        return files

    def test_manifest_contains_every_nested_runtime_file(self) -> None:
        files = self._finalize()

        self.assertIn("./main.dart.js", files)
        self.assertIn("./assets/AssetManifest.bin.json", files)
        self.assertIn("./assets/fonts/MaterialIcons-Regular.otf", files)
        self.assertIn("./canvaskit/canvaskit.wasm", files)
        self.assertIn("./offline-manifest.json", files)
        self.assertIn("./pwa-build-info.json", files)
        self.assertNotIn("./pwa_service_worker.js", files)
        validate_offline_build(self.build_dir, build_id=self.build_id)

    def test_validation_rejects_one_missing_manifest_entry(self) -> None:
        self._finalize()
        manifest_path = self.build_dir / OFFLINE_MANIFEST_FILENAME
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["files"].remove("./canvaskit/canvaskit.wasm")
        manifest["file_count"] -= 1
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(
            OfflinePwaError,
            "does not match the production build",
        ):
            validate_offline_build(self.build_dir, build_id=self.build_id)

    def test_service_worker_requires_both_build_placeholders(self) -> None:
        worker = self.build_dir / "pwa_service_worker.js"
        source = worker.read_text(encoding="utf-8")
        worker.write_text(
            source.replace("__OFFLINE_FILES__", "[]"),
            encoding="utf-8",
        )

        with self.assertRaisesRegex(OfflinePwaError, "offline-files placeholder"):
            inject_service_worker(
                worker,
                build_id=self.build_id,
                files=collect_offline_files(self.build_dir),
            )

    def test_build_id_is_sanitized_and_empty_values_are_rejected(self) -> None:
        self.assertEqual(sanitize_build_id(" release/19? "), "release19")
        with self.assertRaisesRegex(OfflinePwaError, "safe characters"):
            sanitize_build_id("/// ???")


if __name__ == "__main__":
    unittest.main()
