import hashlib
import os
from typing import Optional


class FileCache:
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _path(self, key: str) -> str:
        h = hashlib.sha1(key.encode("utf-8")).hexdigest()
        return os.path.join(self.cache_dir, h)

    def get(self, key: str) -> Optional[bytes]:
        p = self._path(key)
        if os.path.exists(p):
            with open(p, "rb") as f:
                return f.read()
        return None

    def put(self, key: str, data: bytes) -> None:
        p = self._path(key)
        with open(p, "wb") as f:
            f.write(data)
