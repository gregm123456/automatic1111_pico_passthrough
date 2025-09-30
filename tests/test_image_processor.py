import pytest
from app.services.image_processor import png_to_pico_rgb565
from PIL import Image
from io import BytesIO


def make_test_png(w=240, h=240, color=(10, 20, 30)) -> bytes:
    img = Image.new("RGB", (w, h), color)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_rgb565_size_and_consistency():
    png = make_test_png()
    out = png_to_pico_rgb565(png)
    assert len(out) == 240 * 240 * 2
