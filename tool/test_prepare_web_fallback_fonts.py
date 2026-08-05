#!/usr/bin/env python3
"""Deterministic tests for pinned Flutter fallback-font preparation."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from prepare_web_fallback_fonts import (
    FALLBACK_FONTS,
    NOTO_SANS_SYMBOLS_FALLBACK_RELATIVE_PATH,
    ROBOTO_FALLBACK_RELATIVE_PATH,
    FallbackFontError,
    PinnedFallbackFont,
    download_fallback_font,
    validate_fallback_font,
    validate_fallback_fonts,
)


class _MemoryResponse:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    def __enter__(self) -> _MemoryResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, limit: int = -1) -> bytes:
        if limit < 0:
            return self.payload
        return self.payload[:limit]


class FallbackFontPreparationTests(unittest.TestCase):
    def _font(self, payload: bytes) -> PinnedFallbackFont:
        return PinnedFallbackFont(
            name="Test Symbols",
            url="https://example.test/font.woff2",
            relative_path=Path("fallback-fonts/test/font.woff2"),
            sha256=hashlib.sha256(payload).hexdigest(),
            size=len(payload),
            license_relative_path=Path("fallback-fonts/test/OFL.txt"),
            license_copyright_marker="Copyright Test Font Authors",
        )

    def test_runtime_font_paths_match_flutter_requests(self) -> None:
        self.assertEqual(
            {font.relative_path for font in FALLBACK_FONTS},
            {
                ROBOTO_FALLBACK_RELATIVE_PATH,
                NOTO_SANS_SYMBOLS_FALLBACK_RELATIVE_PATH,
            },
        )
        self.assertEqual(len(FALLBACK_FONTS), 2)
        self.assertEqual(len({font.sha256 for font in FALLBACK_FONTS}), 2)

    def test_validate_accepts_exact_woff2_payload(self) -> None:
        payload = b"wOF2" + b"verified-payload"
        font = self._font(payload)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "font.woff2"
            path.write_bytes(payload)
            validate_fallback_font(path, font)

    def test_validate_rejects_same_size_wrong_digest(self) -> None:
        payload = b"wOF2" + b"verified-payload"
        font = self._font(payload)
        corrupted = b"wOF2" + b"corrupted-payload"
        self.assertEqual(len(corrupted), len(payload))

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "font.woff2"
            path.write_bytes(corrupted)
            with self.assertRaisesRegex(FallbackFontError, "checksum"):
                validate_fallback_font(path, font)

    def test_download_replaces_invalid_target_atomically(self) -> None:
        payload = b"wOF2" + b"downloaded-payload"
        font = self._font(payload)

        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / font.relative_path
            target.parent.mkdir(parents=True)
            target.write_bytes(b"invalid")

            with patch(
                "prepare_web_fallback_fonts.urllib.request.urlopen",
                return_value=_MemoryResponse(payload),
            ):
                download_fallback_font(target, font)

            self.assertEqual(target.read_bytes(), payload)
            validate_fallback_font(target, font)
            self.assertEqual(list(target.parent.glob("*.tmp")), [])

    def test_bundle_validation_requires_matching_license(self) -> None:
        payload = b"wOF2" + b"licensed-payload"
        font = self._font(payload)

        with tempfile.TemporaryDirectory() as directory:
            web_dir = Path(directory)
            target = web_dir / font.relative_path
            target.parent.mkdir(parents=True)
            target.write_bytes(payload)

            with patch(
                "prepare_web_fallback_fonts.FALLBACK_FONTS",
                (font,),
            ):
                with self.assertRaisesRegex(FallbackFontError, "license is missing"):
                    validate_fallback_fonts(web_dir)

                license_path = web_dir / font.license_relative_path
                license_path.parent.mkdir(parents=True, exist_ok=True)
                license_path.write_text(
                    f"{font.license_copyright_marker}\n"
                    "SIL OPEN FONT LICENSE Version 1.1\n",
                    encoding="utf-8",
                )
                validate_fallback_fonts(web_dir)


if __name__ == "__main__":
    unittest.main()
