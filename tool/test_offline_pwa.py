#!/usr/bin/env python3
"""Deterministic tests for the generated InfusionCalc offline bundle."""

from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from finalize_web_pwa import _validate_self_contained_runtime
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
from prepare_web_fallback_fonts import ROBOTO_FALLBACK_RELATIVE_PATH


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
            "404.html": (
                '<html><body data-page="not-found">404</body></html>'
            ),
            "about/index.html": "<html><h1>About</h1></html>",
            "privacy/index.html": "<html><h1>Privacy</h1></html>",
            "changelog/index.html": "<html><h1>Changelog</h1></html>",
            "site.css": "body { font-family: sans-serif; }",
            "robots.txt": "User-agent: *\nAllow: /\n",
            "sitemap.xml": "<urlset></urlset>",
            "social/infusioncalc-preview.png": "png-placeholder",
            "flutter.js": "window._flutter = {};",
            "flutter_bootstrap.js": (
                "_flutter.loader.load({config: {"
                "fontFallbackBaseUrl: 'fallback-fonts/'}});"
            ),
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
            str(ROBOTO_FALLBACK_RELATIVE_PATH): "test-font-placeholder",
            "fallback-fonts/roboto/OFL.txt": "SIL Open Font License 1.1",
            ".last_build_id": "internal-build-metadata",
            "assets/.internal-index": "internal-asset-metadata",
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

    def _validate_runtime(self) -> None:
        with patch("finalize_web_pwa.validate_fallback_font") as validate_font:
            _validate_self_contained_runtime(self.build_dir)
            validate_font.assert_called_once_with(
                self.build_dir / ROBOTO_FALLBACK_RELATIVE_PATH,
            )

    def test_manifest_contains_every_public_nested_runtime_file(self) -> None:
        files = self._finalize()

        self.assertIn("./main.dart.js", files)
        self.assertIn("./flutter.js", files)
        self.assertIn("./404.html", files)
        self.assertIn("./about/index.html", files)
        self.assertIn("./privacy/index.html", files)
        self.assertIn("./changelog/index.html", files)
        self.assertIn("./site.css", files)
        self.assertIn("./robots.txt", files)
        self.assertIn("./sitemap.xml", files)
        self.assertIn("./social/infusioncalc-preview.png", files)
        self.assertIn("./assets/AssetManifest.bin.json", files)
        self.assertIn("./assets/fonts/MaterialIcons-Regular.otf", files)
        self.assertIn("./canvaskit/canvaskit.wasm", files)
        self.assertIn(f"./{ROBOTO_FALLBACK_RELATIVE_PATH.as_posix()}", files)
        self.assertIn("./fallback-fonts/roboto/OFL.txt", files)
        self.assertIn("./offline-manifest.json", files)
        self.assertIn("./pwa-build-info.json", files)
        self.assertNotIn("./pwa_service_worker.js", files)
        self.assertNotIn("./.last_build_id", files)
        self.assertNotIn("./assets/.internal-index", files)
        validate_offline_build(self.build_dir, build_id=self.build_id)

    def test_self_contained_runtime_accepts_local_canvaskit_and_font(self) -> None:
        self._validate_runtime()

    def test_self_contained_runtime_ignores_dormant_loader_fallback_constants(
        self,
    ) -> None:
        # Generated Flutter loader code may retain a fallback CDN constant even
        # when --no-web-resources-cdn selects and ships the local renderer. The
        # real-browser smoke test, not static substring matching, verifies which
        # resources are actually requested during startup.
        bootstrap = self.build_dir / "flutter_bootstrap.js"
        bootstrap.write_text(
            "const dormantFallback = "
            "'https://www.gstatic.com/flutter-canvaskit/fallback/canvaskit.js';"
            "_flutter.loader.load({config:{"
            "fontFallbackBaseUrl:'fallback-fonts/'}});",
            encoding="utf-8",
        )

        self._validate_runtime()

    def test_self_contained_runtime_requires_local_font_configuration(self) -> None:
        (self.build_dir / "flutter_bootstrap.js").write_text(
            "_flutter.loader.load();",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(
            OfflinePwaError,
            "local fallback-font config",
        ):
            self._validate_runtime()

    def test_self_contained_runtime_requires_local_javascript_and_wasm(self) -> None:
        (self.build_dir / "canvaskit" / "canvaskit.wasm").unlink()

        with self.assertRaisesRegex(
            OfflinePwaError,
            "both JavaScript and WebAssembly",
        ):
            self._validate_runtime()

    def test_finalized_worker_activates_and_routes_static_documents(self) -> None:
        self._finalize()
        worker_source = (self.build_dir / "pwa_service_worker.js").read_text(
            encoding="utf-8",
        )

        self.assertIn("await self.skipWaiting()", worker_source)
        self.assertIn("await self.clients.claim()", worker_source)
        self.assertIn("ignoreVary: true", worker_source)
        self.assertIn(
            "const NOT_FOUND_DOCUMENT = './404.html';",
            worker_source,
        )
        self.assertIn("const CANONICAL_DOCUMENTS = new Map([", worker_source)
        self.assertIn("const CANONICAL_REDIRECTS = new Map([", worker_source)
        self.assertIn("function canonicalRedirectFor(url)", worker_source)
        self.assertIn("Response.redirect(redirectUrl.href, 308)", worker_source)
        self.assertIn("cache.match(navigationDocument", worker_source)
        self.assertIn("async function cachedNotFoundResponse(cache)", worker_source)
        self.assertIn("status: 404", worker_source)
        self.assertIn("cachedNavigationOrNetwork(request)", worker_source)
        self.assertNotIn("relativePath.endsWith('/')", worker_source)

    def test_validation_rejects_missing_not_found_document(self) -> None:
        (self.build_dir / "404.html").unlink()
        self._finalize()

        with self.assertRaisesRegex(
            OfflinePwaError,
            "Critical offline files are missing",
        ):
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
