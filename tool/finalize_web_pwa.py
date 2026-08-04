#!/usr/bin/env python3
"""Finalize and validate the production InfusionCalc PWA build."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BUILD_ID_PLACEHOLDER = "__BUILD_ID__"
OFFLINE_ASSETS_PLACEHOLDER = "__OFFLINE_ASSETS__"
SERVICE_WORKER = "pwa_service_worker.js"
OFFLINE_MANIFEST = "offline-assets.json"
BUILD_INFO = "pwa-build-info.json"

REQUIRED_FILES = (
    "index.html",
    "flutter.js",
    "flutter_bootstrap.js",
    "main.dart.js",
    "manifest.json",
    "analytics.js",
    "pwa_install.js",
    SERVICE_WORKER,
    "apple-touch-icon.png",
    "icons/Icon-192.png",
    "icons/Icon-512.png",
)

REQUIRED_OFFLINE_ASSETS = (
    "./index.html",
    "./flutter.js",
    "./flutter_bootstrap.js",
    "./main.dart.js",
    "./manifest.json",
    "./analytics.js",
    "./pwa_install.js",
    f"./{OFFLINE_MANIFEST}",
    f"./{BUILD_INFO}",
)


def _safe_build_id(source: str) -> str:
    safe = "".join(
        character
        for character in source
        if character.isalnum() or character in "-_."
    )
    if not safe:
        raise SystemExit("Build ID does not contain any safe characters.")
    return safe


def _is_hidden(relative_path: Path) -> bool:
    return any(part.startswith(".") for part in relative_path.parts)


def _offline_assets(build_dir: Path) -> list[str]:
    assets: set[str] = {
        f"./{OFFLINE_MANIFEST}",
        f"./{BUILD_INFO}",
    }

    for path in build_dir.rglob("*"):
        if not path.is_file():
            continue

        relative = path.relative_to(build_dir)
        if _is_hidden(relative):
            continue
        if relative.as_posix() == SERVICE_WORKER:
            continue
        if relative.name.endswith(".tmp"):
            continue

        assets.add(f"./{relative.as_posix()}")

    return sorted(assets)


def _validate_offline_assets(build_dir: Path, assets: list[str]) -> None:
    if len(assets) != len(set(assets)):
        raise SystemExit("Offline asset manifest contains duplicate paths.")

    for asset in assets:
        if not asset.startswith("./") or "://" in asset or asset.startswith("//"):
            raise SystemExit(f"Offline manifest contains an unsafe URL: {asset}")

        path = build_dir / asset.removeprefix("./")
        if not path.is_file():
            raise SystemExit(f"Offline manifest points to a missing file: {asset}")

    missing_required = [
        asset for asset in REQUIRED_OFFLINE_ASSETS if asset not in assets
    ]
    if missing_required:
        raise SystemExit(
            "Offline manifest is missing required assets: "
            + ", ".join(missing_required),
        )

    if not any(asset.startswith("./assets/") for asset in assets):
        raise SystemExit("Offline manifest must contain Flutter assets/ files.")
    if not any(asset.startswith("./canvaskit/") for asset in assets):
        raise SystemExit("Offline manifest must contain CanvasKit runtime files.")


def _validate_index(index_source: str) -> None:
    if 'src="pwa_install.js"' not in index_source:
        raise SystemExit("PWA install bridge is not loaded by index.html.")

    for required_analytics_markup in (
        'src="analytics.js"',
        'src="https://cloud.umami.is/script.js"',
        'data-website-id="a75601c3-4636-4210-b309-c54736e06843"',
        'data-domains="infusioncalc.eu"',
        'data-do-not-track="true"',
        'data-exclude-search="true"',
        'data-exclude-hash="true"',
    ):
        if required_analytics_markup not in index_source:
            raise SystemExit(
                f"Umami analytics markup is missing: {required_analytics_markup}",
            )


def _validate_local_bridges(build_dir: Path, index_source: str) -> None:
    analytics_source = (build_dir / "analytics.js").read_text(encoding="utf-8")
    for required_symbol in (
        "infusionCalcAnalyticsTrack",
        "app_open",
        "install_prompt_opened",
        "install_button_clicked",
        "pwa_installed",
        "warning_opened",
        "privacy_opened",
        "github_clicked",
        "contact_clicked",
    ):
        if required_symbol not in analytics_source:
            raise SystemExit(
                f"Analytics bridge is missing symbol: {required_symbol}",
            )

    if "umami.identify" in analytics_source or "umami.identify" in index_source:
        raise SystemExit("InfusionCalc must not identify analytics users.")

    install_source = (build_dir / "pwa_install.js").read_text(encoding="utf-8")
    for required_symbol in (
        "infusionCalcPwaGetState",
        "infusionCalcPwaPrompt",
        "infusionCalcPwaSubscribe",
        "infusionCalcPwaUnsubscribe",
    ):
        if required_symbol not in install_source:
            raise SystemExit(
                f"PWA install bridge is missing symbol: {required_symbol}",
            )


def _write_metadata(
    build_dir: Path,
    build_id: str,
    assets: list[str],
) -> str:
    manifest_digest = hashlib.sha256(
        "\n".join(assets).encode("utf-8"),
    ).hexdigest()

    offline_manifest = {
        "build_id": build_id,
        "asset_count": len(assets),
        "asset_list_sha256": manifest_digest,
        "assets": assets,
    }
    (build_dir / OFFLINE_MANIFEST).write_text(
        json.dumps(offline_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    manifest = json.loads(
        (build_dir / "manifest.json").read_text(encoding="utf-8"),
    )
    if manifest.get("display") != "standalone":
        raise SystemExit("PWA manifest must use standalone display mode.")
    if manifest.get("name") != "InfusionCalc":
        raise SystemExit("PWA manifest must use the InfusionCalc product name.")

    info = {
        "build_id": build_id,
        "offline_service_worker": SERVICE_WORKER,
        "offline_asset_manifest": OFFLINE_MANIFEST,
        "offline_asset_count": len(assets),
        "offline_asset_list_sha256": manifest_digest,
        "offline_strategy": "precache-all-cache-first",
        "start_url": manifest.get("start_url"),
        "display": manifest.get("display"),
        "install_bridge": "pwa_install.js",
        "analytics_bridge": "analytics.js",
        "analytics_provider": "Umami Cloud",
        "analytics_domain": "infusioncalc.eu",
        "analytics_respects_do_not_track": True,
        "analytics_excludes_url_search": True,
        "analytics_excludes_url_hash": True,
    }
    (build_dir / BUILD_INFO).write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return manifest_digest


def finalize(build_dir: Path, build_id_source: str) -> None:
    build_dir = build_dir.resolve()
    missing = [name for name in REQUIRED_FILES if not (build_dir / name).is_file()]
    if missing:
        raise SystemExit(
            f"Missing required PWA build files: {', '.join(missing)}",
        )

    build_id = _safe_build_id(build_id_source)
    assets = _offline_assets(build_dir)
    manifest_digest = _write_metadata(build_dir, build_id, assets)
    _validate_offline_assets(build_dir, assets)

    worker = build_dir / SERVICE_WORKER
    worker_source = worker.read_text(encoding="utf-8")
    if worker_source.count(BUILD_ID_PLACEHOLDER) != 1:
        raise SystemExit("Service worker build ID placeholder is missing or duplicated.")
    if worker_source.count(OFFLINE_ASSETS_PLACEHOLDER) != 1:
        raise SystemExit(
            "Service worker offline asset placeholder is missing or duplicated.",
        )

    serialized_assets = json.dumps(
        assets,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    finalized_worker = worker_source.replace(BUILD_ID_PLACEHOLDER, build_id)
    finalized_worker = finalized_worker.replace(
        OFFLINE_ASSETS_PLACEHOLDER,
        serialized_assets,
    )
    worker.write_text(finalized_worker, encoding="utf-8")

    if BUILD_ID_PLACEHOLDER in finalized_worker:
        raise SystemExit("Finalized service worker still contains the build ID placeholder.")
    if OFFLINE_ASSETS_PLACEHOLDER in finalized_worker:
        raise SystemExit(
            "Finalized service worker still contains the asset placeholder.",
        )
    if serialized_assets not in finalized_worker:
        raise SystemExit("Finalized service worker does not contain the asset manifest.")

    index_source = (build_dir / "index.html").read_text(encoding="utf-8")
    _validate_index(index_source)
    _validate_local_bridges(build_dir, index_source)

    print(
        "Finalized PWA build "
        f"{build_id} with {len(assets)} offline assets "
        f"({manifest_digest[:12]}…) in {build_dir}",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", type=Path)
    parser.add_argument("build_id")
    args = parser.parse_args()

    finalize(args.build_dir, args.build_id)


if __name__ == "__main__":
    main()
