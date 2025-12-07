import asyncio
import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from fastapi.datastructures import UploadFile
from fastapi.responses import JSONResponse, Response


@dataclass
class Route:
    method: str
    path: str
    handler: Callable[..., Any]


class FastAPI:
    def __init__(self, title: str = "", version: str = ""):
        self.title = title
        self.version = version
        self.routes: List[Route] = []

    def _register(self, method: str, path: str):
        def decorator(func: Callable[..., Any]):
            self.routes.append(Route(method=method, path=path, handler=func))
            return func

        return decorator

    def get(self, path: str, response_model: Any | None = None):
        return self._register("GET", path)

    def post(self, path: str, response_model: Any | None = None):
        return self._register("POST", path)

    def put(self, path: str, response_model: Any | None = None):
        return self._register("PUT", path)

    def route_for(self, method: str, path: str) -> Tuple[Route, Dict[str, str]] | Tuple[None, None]:
        for route in self.routes:
            params = self._match_route(route.path, path)
            if route.method == method and params is not None:
                return route, params
        return None, None

    @staticmethod
    def _match_route(template: str, path: str) -> Optional[Dict[str, str]]:
        template_parts = template.strip("/").split("/")
        path_parts = path.strip("/").split("/")
        if len(template_parts) != len(path_parts):
            return None
        params: Dict[str, str] = {}
        for t, p in zip(template_parts, path_parts):
            if t.startswith("{") and t.endswith("}"):
                params[t.strip("{}")] = p
            elif t != p:
                return None
        return params

    async def __call__(self, scope, receive, send):
        raise NotImplementedError("ASGI support not implemented in stub")
