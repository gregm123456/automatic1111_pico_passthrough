from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class A1111Txt2ImgRequest(BaseModel):
    prompt: Optional[str]
    negative_prompt: Optional[str]
    # Keep flexible - A1111 has many params
    params: Optional[Dict[str, Any]] = None


class PicoBinaryResponse(BaseModel):
    width: int
    height: int
    format: str = "rgb565-be"
    length: int
