#!/usr/bin/env python3
"""Generate deterministic PNG icons for the web/PWA target without dependencies."""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path

TEAL = (15, 118, 110, 255)
TEAL_DARK = (19, 78, 74, 255)
WHITE = (255, 255, 255, 255)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _write_png(path: Path, size: int, *, maskable: bool) -> None:
    pixels = [[TEAL for _ in range(size)] for _ in range(size)]

    def rectangle(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int, int]) -> None:
        for y in range(max(0, y0), min(size, y1)):
            for x in range(max(0, x0), min(size, x1)):
                pixels[y][x] = color

    margin = int(size * (0.18 if maskable else 0.12))
    radius = int(size * 0.10)

    # Dark rounded-looking tile, drawn with a central rectangle and side bars.
    rectangle(margin + radius, margin, size - margin - radius, size - margin, TEAL_DARK)
    rectangle(margin, margin + radius, size - margin, size - margin - radius, TEAL_DARK)

    # White medical cross in the upper half.
    cross_center_x = size // 2
    cross_center_y = int(size * 0.39)
    arm = int(size * 0.17)
    thickness = max(2, int(size * 0.055))
    rectangle(
        cross_center_x - thickness,
        cross_center_y - arm,
        cross_center_x + thickness,
        cross_center_y + arm,
        WHITE,
    )
    rectangle(
        cross_center_x - arm,
        cross_center_y - thickness,
        cross_center_x + arm,
        cross_center_y + thickness,
        WHITE,
    )

    # Calculator display and three keys in the lower half.
    rectangle(
        int(size * 0.30),
        int(size * 0.62),
        int(size * 0.70),
        int(size * 0.70),
        WHITE,
    )
    key_size = max(2, int(size * 0.055))
    for center_x in (0.36, 0.50, 0.64):
        cx = int(size * center_x)
        cy = int(size * 0.79)
        rectangle(cx - key_size, cy - key_size, cx + key_size, cy + key_size, WHITE)

    raw = bytearray()
    for row in pixels:
        raw.append(0)  # PNG filter type: None
        for rgba in row:
            raw.extend(rgba)

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    png = signature + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + _chunk(b"IEND", b"")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--web-dir", type=Path, default=Path("web"))
    args = parser.parse_args()

    icons = args.web_dir / "icons"
    _write_png(icons / "Icon-192.png", 192, maskable=False)
    _write_png(icons / "Icon-maskable-192.png", 192, maskable=True)
    _write_png(icons / "Icon-512.png", 512, maskable=False)
    _write_png(icons / "Icon-maskable-512.png", 512, maskable=True)
    _write_png(args.web_dir / "apple-touch-icon.png", 180, maskable=False)

    print(f"Generated deterministic PWA icons in {args.web_dir}")


if __name__ == "__main__":
    main()
