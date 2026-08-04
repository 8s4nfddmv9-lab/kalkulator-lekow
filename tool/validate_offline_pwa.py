#!/usr/bin/env python3
"""Independently validate a finalized InfusionCalc offline PWA build."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

REQUIRED_ASSETS = {
    "./index.html",
    "./flutter.js",
    "./flutter_bootstrap.js",
    "./main.dart.js",
    "./manifest.json",
    "./analytics.js",
    "./pwa_install.js",
    "./offline-assets.json",
    "./pwa-build-info.json",
}


def validate(build_dir: Path) -> None:
    build_dir = build_dir.resolve()
    manifest_path = build_dir / "offline-assets.json"
    info_path = build_dir / "pwa-build-info.json"
    worker_path = build_dir / "pwa_service_worker.js"

    for path in (manifest_path, info_path, worker_path):
        if not path.is_file():
            raise SystemExit(f"Missing finalized offline PWA file: {path.name}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    info = json.loads(info_path.read_text(encoding="utf-8"))
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not all(
        isinstance(asset, str) for asset in assets
    ):
        raise SystemExit("offline-assets.json must contain a string asset list.")

    if assets != sorted(set(assets)):
        raise SystemExit("Offline asset list must be sorted and unique.")

    missing_required = sorted(REQUIRED_ASSETS.difference(assets))
    if missing_required:
        raise SystemExit(
            "Offline build is missing required assets: "
            + ", ".join(missing_required),
        )

    if not any(asset.startswith("./assets/") for asset in assets):
        raise SystemExit("Offline build does not contain Flutter assets/ files.")
    if not any(asset.startswith("./canvaskit/") for asset in assets):
        raise SystemExit("Offline build does not contain CanvasKit files.")

    for asset in assets:
        if not asset.startswith("./") or "://" in asset or asset.startswith("//"):
            raise SystemExit(f"Unsafe or external precache URL: {asset}")
        if asset == "./pwa_service_worker.js":
            raise SystemExit("The service worker must not precache itself.")
        if not (build_dir / asset.removeprefix("./")).is_file():
            raise SystemExit(f"Precached file is missing from the build: {asset}")

    digest = hashlib.sha256("\n".join(assets).encode("utf-8")).hexdigest()
    if manifest.get("asset_count") != len(assets):
        raise SystemExit("offline-assets.json contains an incorrect asset count.")
    if manifest.get("asset_list_sha256") != digest:
        raise SystemExit("offline-assets.json contains an incorrect asset digest.")
    if info.get("offline_asset_count") != len(assets):
        raise SystemExit("pwa-build-info.json contains an incorrect asset count.")
    if info.get("offline_asset_list_sha256") != digest:
        raise SystemExit("pwa-build-info.json contains an incorrect asset digest.")
    if info.get("offline_strategy") != "precache-all-cache-first":
        raise SystemExit("Unexpected offline cache strategy metadata.")

    worker_source = worker_path.read_text(encoding="utf-8")
    if "__BUILD_ID__" in worker_source or "__OFFLINE_ASSETS__" in worker_source:
        raise SystemExit("Finalized service worker still contains placeholders.")

    match = re.search(
        r"const OFFLINE_ASSETS = (\[.*?\]);",
        worker_source,
        flags=re.DOTALL,
    )
    if match is None:
        raise SystemExit("Could not read the injected service worker asset list.")
    worker_assets = json.loads(match.group(1))
    if worker_assets != assets:
        raise SystemExit(
            "Service worker asset list differs from offline-assets.json.",
        )

    for required_marker in (
        "cache.addAll(OFFLINE_ASSETS)",
        "caches.match(OFFLINE_INDEX)",
        "caches.match(request)",
        "url.origin !== self.location.origin",
        "keys.filter((key) => key.startsWith(CACHE_PREFIX)",
    ):
        if required_marker not in worker_source:
            raise SystemExit(
                f"Service worker is missing offline behavior: {required_marker}",
            )

    print(
        f"Offline PWA validation passed: {len(assets)} assets, "
        f"manifest {digest[:12]}…",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", type=Path)
    args = parser.parse_args()
    validate(args.build_dir)


if __name__ == "__main__":
    main()
