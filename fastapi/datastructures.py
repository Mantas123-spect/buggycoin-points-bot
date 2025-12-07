import asyncio
from io import BytesIO
from typing import Any


class UploadFile:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self._file = BytesIO(content)

    async def read(self) -> bytes:
        return self._file.getvalue()


def File(default: Any = None):
    return default
