"""WebApp factory — Presentation entry. Routes live in controllers."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from layers.presentation.controllers import WebApp, auth_ok, register_routes

if TYPE_CHECKING:
    from prooftest.service import ProoftestService


def create_app(
    service: "ProoftestService",
    on_shutdown: Optional[Callable[[str], None]] = None,
    *,
    static_dir: Path,
    version: str,
) -> FastAPI:
    if on_shutdown is not None:
        service.set_shutdown_callback(on_shutdown)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        service.stop("uvicorn_shutdown")

    app = FastAPI(title="HIMA Automated Prooftest", version=version, lifespan=lifespan)
    ctx = WebApp(service, static_dir=static_dir, version=version)

    @app.middleware("http")
    async def web_auth_middleware(request: Request, call_next):
        path = request.url.path
        if service.config.web_auth_enabled and (
            path.startswith("/api/") or path in ("/", "/ui")
        ):
            if not auth_ok(request, service):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authentication required (X-Prooftest-Token or ?token=)"},
                )
        return await call_next(request)

    register_routes(app, ctx)
    return app
