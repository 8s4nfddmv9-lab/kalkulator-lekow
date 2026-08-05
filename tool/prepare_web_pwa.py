#!/usr/bin/env python3
"""Generate deterministic PNG assets for the InfusionCalc web/PWA target."""

from __future__ import annotations

import argparse
import struct
import zlib
from pathlib import Path

TEAL = (15, 118, 110, 255)
TEAL_DARK = (19, 78, 74, 255)
TEAL_LIGHT = (225, 241, 239, 255)
MUTED = (54, 95, 92, 255)
OUTLINE = (204, 222, 220, 255)
SURFACE = (245, 247, 247, 255)
WHITE = (255, 255, 255, 255)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _encode_png(
    path: Path,
    *,
    width: int,
    height: int,
    pixels: bytearray,
) -> None:
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)  # PNG filter type: None
        start = y * stride
        raw.extend(pixels[start : start + stride])

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png = (
        signature
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + _chunk(b"IEND", b"")
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)


def _rectangle(
    pixels: bytearray,
    *,
    width: int,
    height: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int, int],
) -> None:
    left = max(0, min(width, x0))
    right = max(left, min(width, x1))
    top = max(0, min(height, y0))
    bottom = max(top, min(height, y1))
    row = bytes(color) * (right - left)
    for y in range(top, bottom):
        start = (y * width + left) * 4
        pixels[start : start + len(row)] = row


def _write_icon(path: Path, size: int, *, maskable: bool) -> None:
    pixels = bytearray(bytes(TEAL) * (size * size))

    margin = int(size * (0.18 if maskable else 0.12))
    radius = int(size * 0.10)

    # Dark rounded-looking tile, drawn with a central rectangle and side bars.
    _rectangle(
        pixels,
        width=size,
        height=size,
        x0=margin + radius,
        y0=margin,
        x1=size - margin - radius,
        y1=size - margin,
        color=TEAL_DARK,
    )
    _rectangle(
        pixels,
        width=size,
        height=size,
        x0=margin,
        y0=margin + radius,
        x1=size - margin,
        y1=size - margin - radius,
        color=TEAL_DARK,
    )

    # White medical cross in the upper half.
    cross_center_x = size // 2
    cross_center_y = int(size * 0.39)
    arm = int(size * 0.17)
    thickness = max(2, int(size * 0.055))
    _rectangle(
        pixels,
        width=size,
        height=size,
        x0=cross_center_x - thickness,
        y0=cross_center_y - arm,
        x1=cross_center_x + thickness,
        y1=cross_center_y + arm,
        color=WHITE,
    )
    _rectangle(
        pixels,
        width=size,
        height=size,
        x0=cross_center_x - arm,
        y0=cross_center_y - thickness,
        x1=cross_center_x + arm,
        y1=cross_center_y + thickness,
        color=WHITE,
    )

    # Calculator display and three keys in the lower half.
    _rectangle(
        pixels,
        width=size,
        height=size,
        x0=int(size * 0.30),
        y0=int(size * 0.62),
        x1=int(size * 0.70),
        y1=int(size * 0.70),
        color=WHITE,
    )
    key_size = max(2, int(size * 0.055))
    for center_x in (0.36, 0.50, 0.64):
        cx = int(size * center_x)
        cy = int(size * 0.79)
        _rectangle(
            pixels,
            width=size,
            height=size,
            x0=cx - key_size,
            y0=cy - key_size,
            x1=cx + key_size,
            y1=cy + key_size,
            color=WHITE,
        )

    _encode_png(path, width=size, height=size, pixels=pixels)


def _write_social_preview(path: Path) -> None:
    width = 1200
    height = 630
    pixels = bytearray(bytes(SURFACE) * (width * height))

    # Main card and brand accent.
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=54,
        y0=54,
        x1=1146,
        y1=576,
        color=WHITE,
    )
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=54,
        y0=54,
        x1=84,
        y1=576,
        color=TEAL,
    )

    # Infusion/calculator symbol.
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=122,
        y0=112,
        x1=262,
        y1=282,
        color=TEAL_LIGHT,
    )
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=184,
       y0=132,
       x1=200,
       y1=212,
       color=TEAL,
    )
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=152,
       y0=164,
       x1=232,
       y1=180,
       color=TEAL,
    )
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=150,
       y0=232,
       x1=234,
       y1=244,
       color=TEAL_DARK,
    )
    for x0 in (154, 184, 214):
        _rectangle(
            pixels,
            width=width,
            height=height,
            x0=x0,
            y0=254,
            x1=x0 + 16,
            y1=270,
            color=TEAL_DARK,
        )

    # Typographic shapes: the actual accessible title and description live in
    # Open Graph metadata; these bars keep the generated image dependency-free.
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=322,
        y0=118,
        x1=870,
       y1=178,
       color=TEAL_DARK,
    )
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=322,
        y0=206,
       x1=790,
       y1=236,
       color=MUTED,
    )
    _rectangle(
        pixels,
        width=width,
        height=height,
        x0=322,
        y0=280,
        x1=1070,
        y1=283,
        color=OUTLINE