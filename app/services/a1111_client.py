import httpx
from typing import Any, Dict, Optional
from app.config import Settings


class A1111Client:
    def __init__(self, settings: Settings):
        self.base_url = str(settings.A1111_BASE_URL)
        self.timeout = settings.A1111_TIMEOUT
        self.auth = None
        if settings.A1111_USERNAME and settings.A1111_PASSWORD:
            self.auth = (settings.A1111_USERNAME, settings.A1111_PASSWORD)

    async def txt2img(self, payload: Dict[str, Any]) -> httpx.Response:
        url = f"{self.base_url}/sdapi/v1/txt2img"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload, auth=self.auth)
            resp.raise_for_status()
            return resp
