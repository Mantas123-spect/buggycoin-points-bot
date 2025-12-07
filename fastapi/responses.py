import json
from io import BytesIO
from typing import Any


class Response:
    def __init__(self, content: Any, status_code: int = 200, media_type: str | None = None):
        self.content = content
        self.status_code = status_code
        self.media_type = media_type

    def json(self):
        if isinstance(self.content, (dict, list)):
            return self.content
        try:
            return json.loads(self.content)
        except Exception:
            return self.content


class JSONResponse(Response):
    def __init__(self, content: Any, status_code: int = 200):
        super().__init__(content=content, status_code=status_code, media_type="application/json")


class StreamingResponse(Response):
    def __init__(self, stream: BytesIO, media_type: str = "application/octet-stream"):
        self.body = stream.getvalue()
        super().__init__(content=self.body, status_code=200, media_type=media_type)
