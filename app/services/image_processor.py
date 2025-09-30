from io import BytesIO
from typing import Tuple
from PIL import Image
from app.config import Settings


def png_to_pico_rgb565(png_bytes: bytes, width: int = 240, height: int = 240, luminance_invert: bool = True) -> bytes:
    img = Image.open(BytesIO(png_bytes)).convert("RGB")
    img = img.resize((width, height), Image.LANCZOS)

    data = bytearray()
    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            if luminance_invert:
                r, g, b = 255 - r, 255 - g, 255 - b
            rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            data.append((rgb565 >> 8) & 0xFF)
            data.append(rgb565 & 0xFF)

    out = bytes(data)
    expected = width * height * 2
    if len(out) != expected:
        raise ValueError(f"RGB565 output size mismatch: {len(out)} != {expected}")
    return out
