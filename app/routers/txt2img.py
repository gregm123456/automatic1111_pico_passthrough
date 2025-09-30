from fastapi import APIRouter, Body, Depends, HTTPException, Response, Header
from fastapi.responses import JSONResponse
from app.config import Settings
from app.services.a1111_client import A1111Client
from app.services.image_processor import png_to_pico_rgb565
import base64
import json

router = APIRouter(prefix="/sdapi/v1")


def get_settings():
    return Settings()


@router.post("/txt2img")
async def txt2img(payload: dict = Body(...), settings: Settings = Depends(get_settings), x_api_key: str | None = Header(None)):
    # Simple API key auth
    if settings.SERVICE_API_KEY:
        if not x_api_key or x_api_key != settings.SERVICE_API_KEY:
            raise HTTPException(status_code=401, detail={"error": "Unauthorized"})
    client = A1111Client(settings)
    try:
        resp = await client.txt2img(payload)
    except Exception as e:
        raise HTTPException(status_code=502, detail={"error": "Upstream A1111 service unavailable", "msg": str(e)})

    # A1111 returns JSON {images: [base64_png], ...} normally
    try:
        body = resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail={"error": "Upstream returned non-json response"})

    images = body.get("images")
    if not images or not isinstance(images, list):
        raise HTTPException(status_code=422, detail={"error": "No images in upstream response"})

    b64png = images[0]
    # In some A1111 setups, images may already be rgb data; assume base64 PNG
    try:
        png_bytes = base64.b64decode(b64png)
    except Exception:
        raise HTTPException(status_code=422, detail={"error": "Failed to decode base64 image"})

    try:
        rgb565 = png_to_pico_rgb565(png_bytes, width=settings.TARGET_WIDTH, height=settings.TARGET_HEIGHT, luminance_invert=settings.LUMINANCE_INVERT)
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": f"Failed to process image: {e}"})

    # If client requested binary (default when Accept: application/octet-stream), return bytes
    headers = {
        "Content-Type": "application/octet-stream",
        "Content-Length": str(len(rgb565)),
        "X-Image-Width": str(settings.TARGET_WIDTH),
        "X-Image-Height": str(settings.TARGET_HEIGHT),
        "X-Image-Format": "rgb565-be",
    }
    return Response(content=rgb565, media_type="application/octet-stream", headers=headers)
