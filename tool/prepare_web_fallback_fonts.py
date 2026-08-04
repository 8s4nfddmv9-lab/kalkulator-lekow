#!/usr/bin/env python3
"""Download and verify the pinned local Flutter fallback font for web builds."""

from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROBOTO_FALLBACK_URL = (
    "https://fonts.gstatic.com/s/roboto/v32/"
    "KFOmCnqEu92Fr1Me4GZLCzYlKw.woff2"
)
ROBOTO_FALLBACK_RELATIVE_PATH = Path(
    "fallback-fonts/roboto/v32/KFOmCnqEu92Fr1Me4GZLCzYlKw.woff2",
)
ROBOTO_FALLBACK_SHA256 = (
    "35b02ca266b79eb4996590f15817425a1ce9ebf48f84471843233ff614656bf2"
)
ROBOTO_FALLBACK_SIZE = 63_464
WOFF2_MAGIC = b"wOF2"


class FallbackFontError(RuntimeError):
    """Raised when the pinned fallback font cannot be trusted or prepared."""


def validate_fallback_font(path: Path) -> None:
    """Validate size, WOFF2 signature and the pinned SHA-256 digest."""

    if not path.is_file():
        raise FallbackFontError(f"Fallback font is missing: {path}")

    payload = path.read_bytes()
    if len(payload) != ROBOTO_FALLBACK_SIZE:
        raise FallbackFontError(
            "Fallback font has an unexpected size: "
            f"{len(payload)} bytes, expected {ROBOTO_FALLBACK_SIZE}.",
        )
    if payload[:4] != WOFF2_MAGIC:
        raise FallbackFontError("Fallback font does not have a WOFF2 signature.")

    digest = hashlib.sha256(payload).hexdigest()
    if digest != ROBOTO_FALLBACK_SHA256:
        raise FallbackFontError(
            "Fallback font checksum does not match the pinned artifact: "
            f"{digest}.",
        )


def download_fallback_font(target: Path) -> None:
    """Download the pinned artifact atomically and verify it before use."""

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        validate_fallback_font(target)
    except FallbackFontError:
        pass
    else:
        print(f"Verified existing fallback font: {target}")
        return

    request = urllib.request.Request(
        ROBOTO_FALLBACK_URL,
        headers={"User-Agent": "InfusionCalc-build/0.1"},
    )
    temporary_path: Path | None = None
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read(ROBOTO_FALLBACK_SIZE + 1)
        if len(payload) > ROBOTO_FALLBACK_SIZE:
            raise FallbackFontError("Fallback font response exceeded the pinned size.")

        with tempfile.NamedTemporaryFile(
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as temporary:
            temporary.write(payload)
            temporary.flush()
            os.fsync(temporary.fileno())
            temporary_path = Path(temporary.name)

        validate_fallback_font(temporary_path)
        temporary_path.replace(target)
        temporary_path = None
    except (OSError, urllib.error.URLError) as error:
        raise FallbackFontError(
            f"Could not download the pinned fallback font: {error}",
        ) from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    print(
        "Prepared verified Roboto fallback font "
        f"{ROBOTO_FALLBACK_SHA256[:12]}… at {target}",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--web-dir", type=Path, default=Path("web"))
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate an existing artifact without network access.",
    )
    args = parser.parse_args()

    target = args.web_dir.resolve() / ROBOTO_FALLBACK_RELATIVE_PATH
    try:
        if args.check_only:
            validate_fallback_font(target)
            print(f"Verified fallback font: {target}")
        else:
            download_fallback_font(target)
    except FallbackFontError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
