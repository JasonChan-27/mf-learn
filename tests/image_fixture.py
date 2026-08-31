from __future__ import annotations

import struct
import zlib


def png_bytes(width: int = 90, height: int = 160) -> bytes:
    """Create a deterministic RGB PNG fixture without third-party packages."""
    signature = b"\x89PNG\r\n\x1a\n"

    def chunk(kind: bytes, data: bytes) -> bytes:
        body = kind + data
        return (
            struct.pack(">I", len(data))
            + body
            + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    row = b"\x00" + (b"\xd8\xd0\xc4" * width)
    pixels = row * height
    return (
        signature
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(pixels, level=9))
        + chunk(b"IEND", b"")
    )
