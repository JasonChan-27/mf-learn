from __future__ import annotations

import struct
from pathlib import Path
from typing import Any


def _png_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    return struct.unpack(">II", data[16:24])


def _jpeg_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 4 or data[:2] != b"\xff\xd8":
        return None
    offset = 2
    sof_markers = {
        0xC0, 0xC1, 0xC2, 0xC3,
        0xC5, 0xC6, 0xC7,
        0xC9, 0xCA, 0xCB,
        0xCD, 0xCE, 0xCF,
    }
    while offset + 4 <= len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            return None
        marker = data[offset]
        offset += 1
        if marker in {0xD8, 0xD9}:
            continue
        if offset + 2 > len(data):
            return None
        segment_length = struct.unpack(">H", data[offset:offset + 2])[0]
        if segment_length < 2 or offset + segment_length > len(data):
            return None
        if marker in sof_markers and segment_length >= 7:
            height, width = struct.unpack(">HH", data[offset + 3:offset + 7])
            return width, height
        offset += segment_length
    return None


def _webp_dimensions(data: bytes) -> tuple[int, int] | None:
    if len(data) < 20 or data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    offset = 12
    while offset + 8 <= len(data):
        chunk = data[offset:offset + 4]
        size = int.from_bytes(data[offset + 4:offset + 8], "little")
        payload = data[offset + 8:offset + 8 + size]
        if len(payload) < size:
            return None
        if chunk == b"VP8X" and len(payload) >= 10:
            width = 1 + int.from_bytes(payload[4:7], "little")
            height = 1 + int.from_bytes(payload[7:10], "little")
            return width, height
        if chunk == b"VP8 " and len(payload) >= 10 and payload[3:6] == b"\x9d\x01\x2a":
            width = int.from_bytes(payload[6:8], "little") & 0x3FFF
            height = int.from_bytes(payload[8:10], "little") & 0x3FFF
            return width, height
        if chunk == b"VP8L" and len(payload) >= 5 and payload[0] == 0x2F:
            bits = int.from_bytes(payload[1:5], "little")
            width = 1 + (bits & 0x3FFF)
            height = 1 + ((bits >> 14) & 0x3FFF)
            return width, height
        offset += 8 + size + (size % 2)
    return None


def image_dimensions(path: Path) -> tuple[int, int] | None:
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        return None
    data = path.read_bytes()
    for parser in (_png_dimensions, _jpeg_dimensions, _webp_dimensions):
        dimensions = parser(data)
        if dimensions is not None:
            return dimensions
    return None


def image_metadata(path: Path) -> dict[str, Any]:
    dimensions = image_dimensions(path)
    if dimensions is None:
        return {
            "width_pixels": None,
            "height_pixels": None,
            "orientation": None,
        }
    width, height = dimensions
    orientation = (
        "PORTRAIT" if height > width
        else "LANDSCAPE" if width > height
        else "SQUARE"
    )
    return {
        "width_pixels": width,
        "height_pixels": height,
        "orientation": orientation,
    }


def require_portrait_image(path: Path, label: str) -> dict[str, Any]:
    metadata = image_metadata(path)
    if metadata["orientation"] is None:
        raise ValueError(f"{label} 无法读取有效图片尺寸：{path}")
    if metadata["orientation"] != "PORTRAIT":
        raise ValueError(
            f"{label} 必须是竖屏图片，当前为 "
            f"{metadata['width_pixels']}x{metadata['height_pixels']} "
            f"({metadata['orientation']})：{path}"
        )
    return metadata
