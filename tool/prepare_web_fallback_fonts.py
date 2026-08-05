#!/usr/bin/env python3
"""Download and verify pinned local Flutter fallback fonts for web builds."""

from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

WOFF2_MAGIC = b"wOF2"


@dataclass(frozen=True)
class PinnedFallbackFont:
    """One immutable fallback-font artifact and its shipped license."""

    name: str
    url: str
    relative_path: Path
    sha256: str
    size: int
    license_relative_path: Path
    license_copyright_marker: str


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

NOTO_SANS_SYMBOLS_FALLBACK_URL = (
    "https://fonts.gstatic.com/s/notosanssymbols/v43/"
    "rP2up3q65FkAtHfwd-eIS2brbDN6gxP34F9jRRCe4W3gfQ8gb_VFRkzrbQ.woff2"
)
NOTO_SANS_SYMBOLS_FALLBACK_RELATIVE_PATH = Path(
    "fallback-fonts/notosanssymbols/v43/"
    "rP2up3q65FkAtHfwd-eIS2brbDN6gxP34F9jRRCe4W3gfQ8gb_VFRkzrbQ.woff2",
)
NOTO_SANS_SYMBOLS_FALLBACK_SHA256 = (
    "08202e258ea583254c036cff46a7077bb5af4f82c41a6c0a6775f6e44d99f1aa"
)
NOTO_SANS_SYMBOLS_FALLBACK_SIZE = 69_116

ROBOTO_FALLBACK_FONT = PinnedFallbackFont(
    name="Roboto Regular",
    url=ROBOTO_FALLBACK_URL,
    relative_path=ROBOTO_FALLBACK_RELATIVE_PATH,
    sha256=ROBOTO_FALLBACK_SHA256,
    size=ROBOTO_FALLBACK_SIZE,
    license_relative_path=Path("fallback-fonts/roboto/OFL.txt"),
    license_copyright_marker="Copyright 2011 The Roboto Project Authors",
)
NOTO_SANS_SYMBOLS_FALLBACK_FONT = PinnedFallbackFont(
    name="Noto Sans Symbols",
    url=NOTO_SANS_SYMBOLS_FALLBACK_URL,
    relative_path=NOTO_SANS_SYMBOLS_FALLBACK_RELATIVE_PATH,
    sha256=NOTO_SANS_SYMBOLS_FALLBACK_SHA256,
    size=NOTO_SANS_SYMBOLS_FALLBACK_SIZE,
    license_relative_path=Path("fallback-fonts/notosanssymbols/OFL.txt"),
    license_copyright_marker="Copyright 2022 The Noto Project Authors",
)
FALLBACK_FONTS = (
    ROBOTO_FALLBACK_FONT,
    NOTO_SANS_SYMBOLS_FALLBACK_FONT,
)


class FallbackFontError(RuntimeError):
    """Raised when a pinned fallback font cannot be trusted or prepared."""


def validate_fallback_font(path: Path, font: PinnedFallbackFont) -> None:
    """Validate size, WOFF2 signature and the pinned SHA-256 digest."""

    if not path.is_file():
        raise FallbackFontError(f"{font.name} fallback font is missing: {path}")

    payload = path.read_bytes()
    if len(payload) != font.size:
        raise FallbackFontError(
            f"{font.name} fallback font has an unexpected size: "
            f"{len(payload)} bytes, expected {font.size}.",
        )
    if payload[:4] != WOFF2_MAGIC:
        raise FallbackFontError(
            f"{font.name} fallback font does not have a WOFF2 signature.",
        )

    digest = hashlib.sha256(payload).hexdigest()
    if digest != font.sha256:
        raise FallbackFontError(
            f"{font.name} fallback font checksum does not match the pinned "
            f"artifact: {digest}.",
        )


def validate_fallback_font_license(
    web_dir: Path,
    font: PinnedFallbackFont,
) -> None:
    """Require the matching SIL OFL notice beside every bundled font."""

    license_path = web_dir / font.license_relative_path
    if not license_path.is_file():
        raise FallbackFontError(
            f"{font.name} fallback-font license is missing: {license_path}",
        )

    source = license_path.read_text(encoding="utf-8")
    for marker in (
        font.license_copyright_marker,
        "SIL OPEN FONT LICENSE Version 1.1",
    ):
        if marker not in source:
            raise FallbackFontError(
                f"{font.name} fallback-font license is incomplete: "
                f"missing {marker!r} in {license_path}.",
            )


def validate_fallback_fonts(web_dir: Path) -> None:
    """Validate the complete same-origin Flutter fallback-font bundle."""

    for font in FALLBACK_FONTS:
        validate_fallback_font(web_dir / font.relative_path, font)
        validate_fallback_font_license(web_dir, font)


def download_fallback_font(target: Path, font: PinnedFallbackFont) -> None:
    """Download one pinned artifact atomically and verify it before use."""

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        validate_fallback_font(target, font)
    except FallbackFontError:
        pass
    else:
        print(f"Verified existing {font.name} fallback font: {target}")
        return

    request = urllib.request.Request(
        font.url,
        headers={"User-Agent": "InfusionCalc-build/0.1.5"},
    )
    temporary_path: Path | None = None
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = response.read(font.size + 1)
        if len(payload) > font.size:
            raise FallbackFontError(
                f"{font.name} fallback-font response exceeded the pinned size.",
            )

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

        validate_fallback_font(temporary_path, font)
        temporary_path.replace(target)
        temporary_path = None
    except (OSError, urllib.error.URLError) as error:
        raise FallbackFontError(
            f"Could not download the pinned {font.name} fallback font: {error}",
        ) from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    print(
        f"Prepared verified {font.name} fallback font "
        f"{font.sha256[:12]}… at {target}",
    )


def prepare_fallback_fonts(web_dir: Path, *, check_only: bool) -> None:
    """Prepare or validate every required Flutter fallback font."""

    for font in FALLBACK_FONTS:
        validate_fallback_font_license(web_dir, font)
        target = web_dir / font.relative_path
        if check_only:
            validate_fallback_font(target, font)
            print(f"Verified {font.name} fallback font: {target}")
        else:
            download_fallback_font(target, font)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--web-dir", type=Path, default=Path("web"))
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate existing artifacts without network access.",
    )
    args = parser.parse_args()

    try:
        prepare_fallback_fonts(
            args.web_dir.resolve(),
            check_only=args.check_only,
        )
    except FallbackFontError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
