#!/usr/bin/env python3
"""Generate deterministic PNG assets for the InfusionCalc web/PWA target."""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path

RGBA = tuple[int, int, int, int]
TEAL: RGBA = (15, 118, 110, 255)
DARK: RGBA = (19, 78, 74, 255)
LIGHT: RGBA = (225, 241, 239, 255)
MUTED: RGBA = (54, 95, 92, 255)
OUTLINE: RGBA = (204, 222, 220, 255)
SURFACE: RGBA = (245, 247, 247, 255)
WHITE: RGBA = (255, 255, 255, 255)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _png(path: Path, width: int, height: int, pixels: bytearray) -> None:
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        start = y * stride
        raw.extend(pixels[start : start + stride])
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    data = signature + _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def _rect(
    pixels: bytearray,
    width: int,
    height: int,
    box: tuple[int, int, int, int],
    color: RGBA,
) -> None:
    x0, y0, x1, y1 = box
    x0, x1 = max(0, x0), min(width, x1)
    y0, y1 = max(0, y0), min(height, y1)
    row = bytes(color) * max(0, x1 - x0)
    for y in range(y0, y1):
        start = (y * width + x0) * 4
        pixels[start : start + len(row)] = row


def _icon(path: Path, size: int, *, maskable: bool) -> None:
    pixels = bytearray(bytes(TEAL) * size * size)
    margin = int(size * (0.18 if maskable else 0.12))
    radius = int(size * 0.10)
    _rect(pixels, size, size, (margin + radius, margin, size - margin - radius, size - margin), DARK)
    _rect(pixels, size, size, (margin, margin + radius, size - margin, size - margin - radius), DARK)

    cx, cy = size // 2, int(size * 0.39)
    arm, thick = int(size * 0.17), max(2, int(size * 0.055))
    _rect(pixels, size, size, (cx - thick, cy - arm, cx + thick, cy + arm), WHITE)
    _rect(pixels, size, size, (cx - arm, cy - thick, cx + arm, cy + thick), WHITE)
    _rect(pixels, size, size, (int(size * 0.30), int(size * 0.62), int(size * 0.70), int(size * 0.70)), WHITE)
    key = max(2, int(size * 0.055))
    for fraction in (0.36, 0.50, 0.64):
        key_x, key_y = int(size * fraction), int(size * 0.79)
        _rect(pixels, size, size, (key_x - key, key_y - key, key_x + key, key_y + key), WHITE)
    _png(path, size, size, pixels)


def _preview(path: Path) -> None:
    width, height = 1200, 630
    pixels = bytearray(bytes(SURFACE) * width * height)
    _rect(pixels, width, height, (54, 54, 1146, 576), WHITE)
    _rect(pixels, width, height, (54, 54, 84, 576), TEAL)

    # Infusion/calculator glyph.
    _rect(pixels, width, height, (122, 112, 262, 282), LIGHT)
    _rect(pixels, width, height, (184, 132, 200, 212), TEAL)
    _rect(pixels, width, height, (152, 164, 232, 180), TEAL)
    _rect(pixels, width, height, (150, 232, 234, 244), DARK)
    for x in (154, 184, 214):
        _rect(pixels, width, height, (x, 254, x + 16, 270), DARK)

    # Abstract title, description and feature lines. Accessible text lives in metadata.
    for box, color in (
        ((322, 118, 870, 178), DARK),
        ((322, 206, 790, 236), MUTED),
        ((322, 280, 1070, 283), OUTLINE),
        ((322, 414, 820, 468), LIGHT),
        ((348, 432, 790, 450), DARK),
        ((322, 520, 520, 540), MUTED),
        ((838, 520, 1070, 540), MUTED),
    ):
        _rect(pixels, width, height, box, color)

    x = 322
    for line_width in (132, 142, 110, 164):
        _rect(pixels, width, height, (x, 332, x + 18, 350), TEAL)
        _rect(pixels, width, height, (x + 30, 329, x + 30 + line_width, 354), DARK)
        x += line_width + 72
    _png(path, width, height, pixels)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--web-dir", type=Path, default=Path("web"))
    args = parser.parse_args()
    icons = args.web_dir / "icons"
    _icon(icons / "Icon-192.png", 192, maskable=False)
    _icon(icons / "Icon-maskable-192.png", 192, maskable=True)
    _icon(icons / "Icon-512.png", 512, maskable=False)
    _icon(icons / "Icon-maskable-512.png", 512, maskable=True)
    _icon(args.web_dir / "apple-touch-icon.png", 180, maskable=False)
    _preview(args.web_dir / "social" / "infusioncalc-preview.png")
    print(f"Generated deterministic PWA and social preview assets in {args.web_dir}")


if __name__ == "__main__":
    main()
