#!/usr/bin/env python3
"""Inject a build-specific cache key and validate the Flutter web output."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_FILES = (
    "index.html",
    "flutter_bootstrap.js",
    "main.dart.js",
    "manifest.json",
    "analytics.js",
    "pwa_install.js",
    "pwa_service_worker.js",
    "apple-touch-icon.png",
    "icons/Icon-192.png",
    "icons/Icon-512.png",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", type=Path)
    parser.add_argument("build_id")
    args = parser.parse_args()

    build_dir = args.build_dir.resolve()
    missing = [name for name in REQUIRED_FILES if not (build_dir / name).is_file()]
    if missing:
        raise SystemExit(f"Missing required PWA build files: {', '.join(missing)}")

    worker = build_dir / "pwa_service_worker.js"
    source = worker.read_text(encoding="utf-8")
    if "__BUILD_ID__" not in source:
        raise SystemExit("Service worker cache placeholder is missing.")

    safe_build_id = "".join(character for character in args.build_id if character.isalnum() or character in "-_.")
    if not safe_build_id:
        raise SystemExit("Build ID does not contain any safe characters.")

    worker.write_text(source.replace("__BUILD_ID__", safe_build_id), encoding="utf-8")

    index_source = (build_dir / "index.html").read_text(encoding="utf-8")
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
    if "./analytics.js" not in source:
        raise SystemExit("Analytics bridge is missing from the offline app shell.")

    bridge_source = (build_dir / "pwa_install.js").read_text(encoding="utf-8")
    for required_symbol in (
        "infusionCalcPwaGetState",
        "infusionCalcPwaPrompt",
        "infusionCalcPwaSubscribe",
        "infusionCalcPwaUnsubscribe",
    ):
        if required_symbol not in bridge_source:
            raise SystemExit(
                f"PWA install bridge is missing symbol: {required_symbol}",
            )

    manifest = json.loads((build_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("display") != "standalone":
        raise SystemExit("PWA manifest must use standalone display mode.")
    if manifest.get("name") != "InfusionCalc":
        raise SystemExit("PWA manifest must use the InfusionCalc product name.")

    info = {
        "build_id": safe_build_id,
        "offline_service_worker": "pwa_service_worker.js",
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
    (build_dir / "pwa-build-info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Finalized PWA build {safe_build_id} in {build_dir}")


if __name__ == "__main__":
    main()
