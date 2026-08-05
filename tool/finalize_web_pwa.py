#!/usr/bin/env python3
"""Finalize, version and validate the production InfusionCalc PWA build."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from offline_pwa import (
    BUILD_ID_PLACEHOLDER,
    OFFLINE_FILES_PLACEHOLDER,
    OfflinePwaError,
    collect_offline_files,
    inject_service_worker,
    sanitize_build_id,
    validate_offline_build,
    write_build_info,
    write_offline_manifest,
)
from prepare_web_fallback_fonts import (
    FallbackFontError,
    ROBOTO_FALLBACK_RELATIVE_PATH,
    validate_fallback_font,
)
from validate_web_routing import WebRoutingError, validate_web_routing
from validate_web_seo import WebSeoError, validate_web_seo

REQUIRED_FILES = (
    "index.html",
    "404.html",
    "flutter.js",
    "flutter_bootstrap.js",
    "main.dart.js",
    "manifest.json",
    "analytics.js",
    "pwa_install.js",
    "pwa_service_worker.js",
    "apple-touch-icon.png",
    "icons/Icon-192.png",
    "icons/Icon-512.png",
    "robots.txt",
    "sitemap.xml",
    "site.css",
    "about/index.html",
    "privacy/index.html",
    "changelog/index.html",
    "social/infusioncalc-preview.png",
    str(ROBOTO_FALLBACK_RELATIVE_PATH),
    "fallback-fonts/roboto/OFL.txt",
)


def _validate_index(index_source: str) -> None:
    if 'src="pwa_install.js"' not in index_source:
        raise OfflinePwaError("PWA install bridge is not loaded by index.html.")

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
            raise OfflinePwaError(
                f"Umami analytics markup is missing: {required_analytics_markup}",
            )

    for required_offline_markup in (
        "pwa_service_worker.js",
        "updateViaCache: 'none'",
        "registration.update()",
        "offline-manifest.json",
        "waitForCompleteOfflineBundle",
        "caches.open(manifest.cache_name)",
        "manifest.files.map",
        "dataset.offlineReady",
        "dataset.offlineBuild",
        "infusioncalc-offline-ready",
        "fileCount: manifest.file_count",
    ):
        if required_offline_markup not in index_source:
            raise OfflinePwaError(
                f"Offline registration behavior is missing: {required_offline_markup}",
            )

    if "navigator.serviceWorker.ready" in index_source:
        raise OfflinePwaError(
            "Offline readiness must verify every cached file, not only an active worker.",
        )


def _validate_self_contained_runtime(build_dir: Path) -> None:
    """Require local renderers and the pinned local Flutter fallback font.

    Flutter's generated loader can retain dormant fallback URL constants even
    when ``--no-web-resources-cdn`` is active. Static string matching therefore
    produces false positives. The build-time checks below require complete
    same-origin assets; the real-browser smoke test separately clears the
    ordinary HTTP cache and rejects every actually requested external startup
    resource except optional Umami analytics.
    """

    renderer_dir = build_dir / "canvaskit"
    renderer_files = [path for path in renderer_dir.rglob("*") if path.is_file()]
    if not renderer_files:
        raise OfflinePwaError(
            "Self-contained Flutter build is missing local CanvasKit assets. "
            "Build with --no-web-resources-cdn.",
        )

    wasm_files = [path for path in renderer_files if path.suffix == ".wasm"]
    javascript_files = [path for path in renderer_files if path.suffix == ".js"]
    if not wasm_files or not javascript_files:
        raise OfflinePwaError(
            "Local CanvasKit bundle must include both JavaScript and WebAssembly files.",
        )

    bootstrap_source = (build_dir / "flutter_bootstrap.js").read_text(
        encoding="utf-8",
    )
    for required_font_config in (
        "fontFallbackBaseUrl",
        "fallback-fonts/",
    ):
        if required_font_config not in bootstrap_source:
            raise OfflinePwaError(
                f"Flutter bootstrap is missing local fallback-font config: "
                f"{required_font_config}",
            )

    try:
        validate_fallback_font(build_dir / ROBOTO_FALLBACK_RELATIVE_PATH)
    except FallbackFontError as error:
        raise OfflinePwaError(str(error)) from error


def _validate_analytics(build_dir: Path, index_source: str) -> None:
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
            raise OfflinePwaError(
                f"Analytics bridge is missing symbol: {required_symbol}",
            )
    if "umami.identify" in analytics_source or "umami.identify" in index_source:
        raise OfflinePwaError("InfusionCalc must not identify analytics users.")


def _validate_install_bridge(build_dir: Path) -> None:
    bridge_source = (build_dir / "pwa_install.js").read_text(encoding="utf-8")
    for required_symbol in (
        "infusionCalcPwaGetState",
        "infusionCalcPwaPrompt",
        "infusionCalcPwaSubscribe",
        "infusionCalcPwaUnsubscribe",
    ):
        if required_symbol not in bridge_source:
            raise OfflinePwaError(
                f"PWA install bridge is missing symbol: {required_symbol}",
            )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("build_dir", type=Path)
    parser.add_argument("build_id")
    args = parser.parse_args()

    try:
        build_dir = args.build_dir.resolve()
        missing = [
            name for name in REQUIRED_FILES if not (build_dir / name).is_file()
        ]
        if missing:
            raise OfflinePwaError(
                f"Missing required PWA build files: {', '.join(missing)}",
            )

        safe_build_id = sanitize_build_id(args.build_id)
        index_source = (build_dir / "index.html").read_text(encoding="utf-8")
        _validate_index(index_source)
        _validate_self_contained_runtime(build_dir)
        _validate_analytics(build_dir, index_source)
        _validate_install_bridge(build_dir)
        validate_web_seo(build_dir)
        validate_web_routing(build_dir)

        manifest_path = build_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("display") != "standalone":
            raise OfflinePwaError("PWA manifest must use standalone display mode.")
        if manifest.get("name") != "InfusionCalc":
            raise OfflinePwaError("PWA manifest must use the InfusionCalc name.")

        worker_path = build_dir / "pwa_service_worker.js"
        worker_template = worker_path.read_text(encoding="utf-8")
        if BUILD_ID_PLACEHOLDER not in worker_template:
            raise OfflinePwaError("Service worker cache placeholder is missing.")
        if OFFLINE_FILES_PLACEHOLDER not in worker_template:
            raise OfflinePwaError("Service worker file-list placeholder is missing.")

        offline_files = collect_offline_files(build_dir)
        write_offline_manifest(
            build_dir,
            build_id=safe_build_id,
            files=offline_files,
        )
        write_build_info(
            build_dir,
            build_id=safe_build_id,
            files=offline_files,
            manifest=manifest,
        )
        inject_service_worker(
            worker_path,
            build_id=safe_build_id,
            files=offline_files,
        )
        validate_offline_build(build_dir, build_id=safe_build_id)
    except (
        OfflinePwaError,
        WebRoutingError,
        WebSeoError,
        json.JSONDecodeError,
        OSError,
    ) as error:
        raise SystemExit(str(error)) from error

    print(
        f"Finalized self-contained PWA build {safe_build_id} with "
        f"{len(offline_files)} offline files in {build_dir}",
    )


if __name__ == "__main__":
    main()
