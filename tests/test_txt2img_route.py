from fastapi.testclient import TestClient
from app.main import create_app
import base64
from PIL import Image
from io import BytesIO


def make_base64_png():
    img = Image.new("RGB", (240, 240), (5, 10, 15))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


def test_txt2img_endpoint_returns_binary(monkeypatch):
    # Ensure no SERVICE_API_KEY blocks the test
    import os
    os.environ.pop("SERVICE_API_KEY", None)
    app = create_app()

    # Mock A1111Client.txt2img to return an object with .json() => {images: [b64]}
    class DummyResp:
        def __init__(self, b64):
            self._b = b64

        def json(self):
            return {"images": [self._b]}

    async def fake_txt2img(self, payload):
        return DummyResp(make_base64_png())

    # Patch the A1111Client.txt2img method
    import app.services.a1111_client as ac
    monkeypatch.setattr(ac.A1111Client, "txt2img", fake_txt2img)

    client = TestClient(app)
    res = client.post("/sdapi/v1/txt2img", json={"prompt": "test"})
    assert res.status_code == 200
    assert res.headers.get("X-Image-Format") == "rgb565-be"
    assert int(res.headers.get("Content-Length")) == 240 * 240 * 2
