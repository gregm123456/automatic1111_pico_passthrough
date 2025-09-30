from pydantic import BaseSettings, AnyHttpUrl
from typing import Optional


class Settings(BaseSettings):
    A1111_BASE_URL: AnyHttpUrl
    A1111_USERNAME: Optional[str] = None
    A1111_PASSWORD: Optional[str] = None
    A1111_TIMEOUT: int = 60

    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8080
    SERVICE_API_KEY: Optional[str] = None
    DEBUG_MODE: bool = False

    TARGET_WIDTH: int = 240
    TARGET_HEIGHT: int = 240
    LUMINANCE_INVERT: bool = True

    ENABLE_CACHING: bool = False
    CACHE_DIR: Optional[str] = None

    class Config:
        env_file = ".env"
