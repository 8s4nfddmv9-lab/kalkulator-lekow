#!/usr/bin/env python3
"""Generate and validate the versioned offline bundle for InfusionCalc."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CACHE_PREFIX = "infusioncalc-pwa-"
SERVICE_WORKER_FILENAME = "pwa_service_worker.js"
OFFLINE_MANIFEST_FILENAME = "offline-manifest.json"
BUILD_INFO_FILENAME = "pwa-build-info.json"
BUILD_ID_PLACEHOLDER = "__BUILD_ID__"
OFFLINE_FILES_PLACEHOLDER = "__OFFLINE_FILES__"
NAVIGATION_FALLBACK = "./index.html"
NOT_FOUND_DOCUMENT = "./404.html"
ROBOTO_FALLBACK_URL = (
    "./fallback-fonts/roboto/v32/KFOmCnqEu92Fr1Me4GZLCzYlKw.woff2"
)
ROBOTO_LICENSE_URL = "./fallback-fonts/roboto/OFL.txt"

CRITICAL_OFFLINE_FILES = frozenset(
    {
        "./index.html",
        "./404.html",
        "./about/index.html",
        "./privacy/index.html",
        "./changelog/index.html",
        "./site.css",
        "./robots.txt",
        "./sitemap.xml",
        "./social/infusioncalc-preview.png",
        "./flutter.js",
        "./flutter_bootstrap.js",
        "./main.dart.js",
        "./manifest.json",
        "./analytics.js",
        "./pwa_install.js",
        "./apple-touch-icon.png",
        "./icons/Icon-192.png",
        "./icons/Icon-512.png",
        ROBOTO_FALLBACK_URL,
        ROBOTO_LICENSE_URL,
        f"./{OFFLINE_MANIFEST_FILENAME}",
        f"./{BUILD_INFO_FILENAME}",
    },
)


class OfflinePwaError(RuntimeError):
    """Raised when a build cannot provide a complete, coherent offline bundle."""


def sanitize_build_id(raw_build_id: str) -> str:
    """Return a cache-safe build identifier or reject an unusable value."""

    safe = "".join(
        character
        for character in raw_build_id
        if character.isalnum() or character in "-_."
    )
    if not safe:
        raise OfflinePwaError("Build ID does not contain any safe characters.")
    return safe


def cache_name(build_id: str) -> str:
    """Return the isolated cache name for one immutable application build."""

    return f"{CACHE_PREFIX}{build_id}"


def _offline_url(build_dir: Path, path: Path) -> str:
    relative = path.relative_to(build_dir).as_posix()
    if relative.startswith("../") or relative.startswith("/"):
        raise OfflinePwaError(f"Unsafe offline path: {relative}")
    return f"./{relative}"


def _is_public_build_file(build_dir: Path, path: Path) -> bool:
    """Return whether a generated file is intended to be served publicly.

    Flutter may leave internal metadata such as `.last_build_id` in the web
    output. Such files are not runtime dependencies and static hosts may omit
    them. Including one in `cache.addAll()` would reject the complete atomic
    installation, so every hidden path component is excluded.
    """

    relative = path.relative_to(build_dir)
    return not any(part.startswith(".") for part in relative.parts)


def collect_offline_files(build_dir: Path) -> list[str]:
    """Collect every public same-origin file required by the web build.

    The service-worker script itself is excluded because browser update checks
    fetch it independently. The generated manifest and build-info documents are
    included even before they are written, making the resulting list stable.
    Hidden build metadata is deliberately excluded because it is not part of the
    public runtime and may not be served by GitHub Pages or another static host.
    """

    build_dir = build_dir.resolve()
    if not build_dir.is_dir():
        raise OfflinePwaError(f"Build directory does not exist: {build_dir}")

    files = {
        _offline_url(build_dir, path)
        for path in build_dir.rglob("*")
        if path.is_file()
        and path.name != SERVICE_WORKER_FILENAME
        and _is_public_build_file(build_dir, path)
    }
    files.add(f"./{OFFLINE_MANIFEST_FILENAME}")
    files.add(f"./{BUILD_INFO_FILENAME}")
    return sorted(files)


def write_offline_manifest(
    build_dir: Path,
    *,
    build_id: str,
    files: list[str],
) -> Path:
    """Write the auditable offline manifest consumed by validation and support."""

    payload = {
        "schema_version": 1,
        "build_id": build_id,
        "cache_name": cache_name(build_id),
        "strategy": "versioned-cache-first",
        "navigation_fallback": NAVIGATION_FALLBACK,
        "not_found_document": NOT_FOUND_DOCUMENT,
        "file_count": len(files),
        "files": files,
    }
    path = build_dir / OFFLINE_MANIFEST_FILENAME
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def write_build_info(
    build_dir: Path,
    *,
    build_id: str,
    files: list[str],
    manifest: dict[str, Any],
) -> Path:
    """Write public, non-sensitive metadata about the deployed PWA build."""

    payload = {
        "build_id": build_id,
        "offline_service_worker": SERVICE_WORKER_FILENAME,
        "offline_manifest": OFFLINE_MANIFEST_FILENAME,
        "offline_cache_name": cache_name(build_id),
        "offline_strategy": "versioned-cache-first",
        "offline_not_found_document": NOT_FOUND_DOCUMENT.removeprefix("./"),
        "offline_file_count": len(files),
        "start_url": manifest.get("start_url"),
        "display": manifest.get("display"),
        "install_bridge": "pwa_install.js",
        "analytics_bridge": "analytics.js",
        "analytics_provider": "Umami Cloud",
        "analytics_domain": "infusioncalc.eu",
        "analytics_respects_do_not_track": True,
        "analytics_excludes_url_search": True,
        "analytics_excludes_url_hash": True,
        "local_font_fallback": ROBOTO_FALLBACK_URL.removeprefix("./"),
        "local_font_license": ROBOTO_LICENSE_URL.removeprefix("./"),
    }
    path = build_dir / BUILD_INFO_FILENAME
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def inject_service_worker(
    worker_path: Path,
    *,
    build_id: str,
    files: list[str],
) -> None:
    """Inject one build ID and the exact offline file list into the worker."""

    source = worker_path.read_text(encoding="utf-8")
    if source.count(BUILD_ID_PLACEHOLDER) != 1:
        raise OfflinePwaError(
            "Service worker must contain exactly one build ID placeholder.",
        )
    if source.count(OFFLINE_FILES_PLACEHOLDER) != 1:
        raise OfflinePwaError(
            "Service worker must contain exactly one offline-files placeholder.",
        )

    serialized_files = json.dumps(
        files,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    finalized = source.replace(BUILD_ID_PLACEHOLDER, build_id).replace(
        OFFLINE_FILES_PLACEHOLDER,
        serialized_files,
    )
    worker_path.write_text(finalized, encoding="utf-8")


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise OfflinePwaError(f"Invalid JSON file {path}: {error}") from error
    if not isinstance(value, dict):
        raise OfflinePwaError(f"Expected a JSON object in {path}.")
    return value


def validate_offline_build(build_dir: Path, *, build_id: str) -> None:
    """Validate that the manifest, worker and generated files are coherent."""

    build_dir = build_dir.resolve()
    manifest_path = build_dir / OFFLINE_MANIFEST_FILENAME
    worker_path = build_dir / SERVICE_WORKER_FILENAME
    build_info_path = build_dir / BUILD_INFO_FILENAME

    for path in (manifest_path, worker_path, build_info_path):
        if not path.is_file():
            raise OfflinePwaError(f"Missing offline build file: {path.name}")

    manifest = _load_json_object(manifest_path)
    files = manifest.get("files")
    if not isinstance(files, list) or not all(
        isinstance(item, str) for item in files
    ):
        raise OfflinePwaError("Offline manifest must contain a string file list.")
    if files != sorted(set(files)):
        raise OfflinePwaError("Offline manifest file list must be sorted and unique.")

    expected_files = collect_offline_files(build_dir)
    if files != expected_files:
        missing = sorted(set(expected_files) - set(files))
        unexpected = sorted(set(files) - set(expected_files))
        raise OfflinePwaError(
            "Offline manifest does not match the production build. "
            f"Missing: {missing or 'none'}; unexpected: {unexpected or 'none'}.",
        )

    if manifest.get("schema_version") != 1:
        raise OfflinePwaError("Unsupported offline manifest schema version.")
    if manifest.get("build_id") != build_id:
        raise OfflinePwaError("Offline manifest build ID does not match.")
    if manifest.get("cache_name") != cache_name(build_id):
        raise OfflinePwaError("Offline manifest cache name does not match.")
    if manifest.get("strategy") != "versioned-cache-first":
        raise OfflinePwaError("Offline manifest strategy must be versioned-cache-first.")
    if manifest.get("navigation_fallback") != NAVIGATION_FALLBACK:
        raise OfflinePwaError("Offline navigation fallback must be index.html.")
    if manifest.get("not_found_document") != NOT_FOUND_DOCUMENT:
        raise OfflinePwaError("Offline not-found document must be 404.html.")
    if manifest.get("file_count") != len(files):
        raise OfflinePwaError("Offline manifest file count is inconsistent.")

    missing_critical = sorted(CRITICAL_OFFLINE_FILES - set(files))
    if missing_critical:
        raise OfflinePwaError(
            f"Critical offline files are missing: {', '.join(missing_critical)}",
        )

    for url in files:
        if not url.startswith("./") or ".." in url.split("/"):
            raise OfflinePwaError(f"Unsafe offline URL: {url}")
        if "://" in url:
            raise OfflinePwaError(f"External URL cannot be precached: {url}")
        if not (build_dir / url.removeprefix("./")).is_file():
            raise OfflinePwaError(f"Manifest file does not exist: {url}")

    worker_source = worker_path.read_text(encoding="utf-8")
    if BUILD_ID_PLACEHOLDER in worker_source or OFFLINE_FILES_PLACEHOLDER in worker_source:
        raise OfflinePwaError("Service worker still contains build placeholders.")
    serialized_files = json.dumps(
        files,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    required_worker_fragments = (
        f"const OFFLINE_FILES = {serialized_files};",
        f"{CACHE_PREFIX}{build_id}",
        "const LEGACY_CACHE_PREFIXES = ['kalkulator-lekow-'];",
        "cache: 'reload'",
        "await caches.delete(CACHE_NAME)",
        "managedPrefixes.some",
        "const NOT_FOUND_DOCUMENT = './404.html';",
        "const CANONICAL_DOCUMENTS = new Map([",
        "const CANONICAL_REDIRECTS = new Map([",
        "function canonicalRedirectFor(url)",
        "Response.redirect(redirectUrl.href, 308)",
        "cache.match(navigationDocument",
        "async function cachedNotFoundResponse(cache)",
        "status: 404",
        "cachedNavigationOrNetwork(request)",
        "await self.skipWaiting()",
        "await self.clients.claim()",
        "ignoreSearch: true",
        "ignoreVary: true",
    )
    for fragment in required_worker_fragments:
        if fragment not in worker_source:
            raise OfflinePwaError(
                f"Service worker is missing offline behavior: {fragment}",
            )

    if f"./{SERVICE_WORKER_FILENAME}" in files:
        raise OfflinePwaError("The service-worker script must not cache itself.")
