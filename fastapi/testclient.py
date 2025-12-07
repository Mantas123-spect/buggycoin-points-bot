import asyncio
import inspect
from typing import Any, Dict, List

from fastapi.app import FastAPI
from fastapi.datastructures import UploadFile
from fastapi.responses import JSONResponse, Response
from app.models import Operation, PartMetadata
from dataclasses import is_dataclass, asdict


class TestResponse:
    def __init__(self, status_code: int, content: Any):
        self.status_code = status_code
        self._content = content

    def json(self):
        content = self._content
        if isinstance(content, Response):
            return content.json()
        if hasattr(content, "to_dict"):
            return content.to_dict()
        if is_dataclass(content):
            return asdict(content)
        return content


class TestClient:
    def __init__(self, app: FastAPI):
        self.app = app

    def _match(self, method: str, path: str):
        route, params = self.app.route_for(method, path)
        if not route:
            raise AssertionError(f"Route {method} {path} not found")
        return route, params

    def _invoke(self, route, params: Dict[str, str], body: Any = None, files: Dict[str, Any] | None = None):
        handler = route.handler
        sig = inspect.signature(handler)
        kwargs = {}
        for name, param in sig.parameters.items():
            if name in params:
                kwargs[name] = params[name]
            elif name == "file" and files:
                filename, content, _ = files.get("file")
                kwargs[name] = UploadFile(filename, content.encode() if isinstance(content, str) else content)
            elif name == "operations" and body is not None:
                kwargs[name] = [Operation(**op) for op in body]
            elif name == "metadata" and body is not None:
                kwargs[name] = PartMetadata(**body)
            elif name != "self" and body is not None:
                kwargs[name] = body

        if inspect.iscoroutinefunction(handler):
            result = asyncio.run(handler(**kwargs))
        else:
            result = handler(**kwargs)

        if isinstance(result, Response):
            return TestResponse(result.status_code, result)
        return TestResponse(200, result)

    def post(self, path: str, files: Dict[str, Any] | None = None, json: Any | None = None):
        route, params = self._match("POST", path)
        return self._invoke(route, params, body=json, files=files)

    def put(self, path: str, json: Any | None = None):
        route, params = self._match("PUT", path)
        return self._invoke(route, params, body=json)

    def get(self, path: str):
        route, params = self._match("GET", path)
        response = self._invoke(route, params)
        return response
