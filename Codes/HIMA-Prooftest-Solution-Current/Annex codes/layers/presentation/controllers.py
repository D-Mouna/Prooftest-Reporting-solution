"""Presentation layer — FastAPI controllers. Call Application only (no OPC/SQL/PDF/annex)."""

from __future__ import annotations

import os
import tempfile
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

if TYPE_CHECKING:
    from prooftest.service import ProoftestService


def is_local_client(request: Request) -> bool:
    if request.client is None:
        return False
    host = request.client.host
    return host in ("127.0.0.1", "::1", "localhost")


def _is_local_client(request: Request) -> bool:
    """
    Test compatibility:
    Gate tests patch `prooftest.web.app._is_local_client`.
    Controllers should consult that symbol so localhost-only endpoints
    can be bypassed during tests.
    """
    try:
        from prooftest.web import app as app_mod

        fn = getattr(app_mod, "_is_local_client", None)
        if callable(fn):
            return bool(fn(request))
    except Exception:
        pass
    return is_local_client(request)


def auth_ok(request: Request, service: "ProoftestService") -> bool:
    if not service.config.web_auth_enabled:
        return True
    if service.config.web_localhost_bypass and _is_local_client(request):
        return True
    token = request.headers.get("X-Prooftest-Token") or request.query_params.get("token")
    return bool(token and token == service.config.web_auth_token)


def application(service: "ProoftestService"):
    """
    Return the Application facade — Presentation's only door.

    Production always wires ``service.app``. Tests must attach a facade (or MagicMock
    with the same use-case methods) on ``service.app``.
    """
    app = getattr(service, "app", None)
    if app is None:
        raise RuntimeError("ApplicationFacade is not wired on the service host")
    return app


class WebApp:
    def __init__(
        self,
        service: "ProoftestService",
        *,
        static_dir: Path,
        version: str,
    ) -> None:
        self.service = service
        self.static_dir = static_dir
        self.version = version
        self.alarms_cache_lock = threading.Lock()
        self.alarms_cache: dict[str, object] = {"alarms": [], "cached_at": 0.0}
        self.alarms_cache_ttl_sec = 3.0

    def index_html(self) -> str:
        html = (self.static_dir / "index.html").read_text(encoding="utf-8")
        if "<base " not in html:
            html = html.replace("<head>", '<head>\n  <base href="/static/">', 1)
        return html


class StatusController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        service = self.ctx.service

        @app.get("/api/health")
        def health():
            return application(service).get_engine_status()

        @app.get("/api/running-tests")
        def running_tests():
            try:
                return application(service).list_running_tests()
            except Exception:
                return []

        @app.get("/api/test-history")
        def test_history():
            try:
                return application(service).list_test_history()
            except Exception:
                return []


class EngineController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        service = self.ctx.service

        @app.post("/api/refresh")
        def refresh():
            facade = application(service)
            if service._stopped:
                return {
                    "status": "engine_stopped",
                    "detail": "Start the service before Refresh",
                    "popups": facade.alarms.pop_pending_popups(),
                }

            def _run() -> None:
                application(service).refresh_catalog()

            threading.Thread(target=_run, daemon=True, name="manual-refresh").start()
            return {"status": "refresh_started", "popups": facade.alarms.pop_pending_popups()}

        @app.post("/api/start")
        def start_service(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Start is allowed from localhost only")
            facade = application(service)
            if service._starting:
                return {
                    "status": "start_in_progress",
                    "port": facade.config.web_port,
                    "starting": True,
                    "web_host_alive": True,
                }
            if not service._stopped and facade.engine_running:
                return {
                    "status": "already_running",
                    "port": facade.config.web_port,
                    "engine_running": True,
                }

            def _run() -> None:
                try:
                    application(service).start_engine()
                except Exception:
                    import logging

                    logging.getLogger("prooftest.web").exception("Engine start failed")

            threading.Thread(target=_run, daemon=True, name="engine-start").start()
            return {
                "status": "engine_start_requested",
                "port": facade.config.web_port,
                "starting": True,
                "web_host_alive": True,
            }

        @app.post("/api/stop")
        def stop_engine(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Stop is allowed from localhost only")
            reason = request.query_params.get("reason", "ui_stop")
            facade = application(service)
            facade.request_stop_flags(reason)

            def _run() -> None:
                application(service).stop_engine(reason)

            threading.Thread(target=_run, daemon=True, name="engine-stop").start()
            return {
                "status": "engine_stop_requested",
                "reason": reason,
                "web_host_alive": True,
                "stopping": True,
                "engine_running": False,
            }

        @app.post("/api/shutdown")
        def shutdown(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Shutdown is allowed from localhost only")
            reason = request.query_params.get("reason", "api_shutdown")

            def _run() -> None:
                application(service).request_shutdown(reason, exit_process=True)

            threading.Thread(target=_run, daemon=True, name="api-shutdown").start()
            return {"status": "shutdown_started", "reason": reason, "web_host_alive": False}


class SilworxController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        service = self.ctx.service

        @app.post("/api/silworx/disconnect")
        def silworx_disconnect(request: Request):
            if not _is_local_client(request):
                raise HTTPException(
                    status_code=403, detail="SILworX disconnect is allowed from localhost only"
                )
            return application(service).close_silworx_connection()

        @app.post("/api/silworx/connect")
        def silworx_connect(request: Request):
            if not _is_local_client(request):
                raise HTTPException(
                    status_code=403, detail="SILworX connect is allowed from localhost only"
                )
            return application(service).resume_silworx_connection()


class DeviceController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        service = self.ctx.service

        @app.get("/api/devices")
        def devices(view: str = "all"):
            try:
                return application(service).list_devices(view)
            except Exception:
                return []


class CatalogController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        service = self.ctx.service

        @app.get("/api/archives")
        def archives():
            try:
                return application(service).list_archives()
            except Exception:
                return []

        @app.post("/api/archives")
        def create_archive(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Archive is allowed from localhost only")
            try:
                return application(service).create_archive()
            except Exception as exc:
                name = type(exc).__name__
                if name == "ListArchiveError":
                    raise HTTPException(status_code=409, detail=str(exc)) from exc
                raise HTTPException(status_code=500, detail=str(exc)) from exc

        @app.post("/api/archives/restore")
        def restore_archive(request: Request, archive_id: str = ""):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Restore is allowed from localhost only")
            try:
                return application(service).restore_archive(archive_id)
            except Exception as exc:
                if type(exc).__name__ == "ListArchiveError":
                    raise HTTPException(status_code=409, detail=str(exc)) from exc
                raise HTTPException(status_code=500, detail=str(exc)) from exc

        @app.post("/api/archives/upload-restore")
        async def upload_restore(request: Request, file: UploadFile = File(...)):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Restore is allowed from localhost only")
            filename = file.filename or "restore.bin"
            suffix = Path(filename).suffix or ".bin"
            fd, tmp_name = tempfile.mkstemp(prefix="list_restore_", suffix=suffix)
            os.close(fd)
            tmp_path = Path(tmp_name)
            try:
                content = await file.read()
                tmp_path.write_bytes(content)
                return application(service).restore_archive_upload(tmp_path, filename)
            except Exception as exc:
                if type(exc).__name__ == "ListArchiveError":
                    raise HTTPException(status_code=409, detail=str(exc)) from exc
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            finally:
                tmp_path.unlink(missing_ok=True)

        @app.post("/api/devices/keep-opc")
        def keep_opc_devices(request: Request, archive: bool = True):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Clear is allowed from localhost only")
            try:
                return application(service).clear_keep_opc_only(archive_first=archive)
            except Exception as exc:
                if type(exc).__name__ == "ListArchiveError":
                    raise HTTPException(status_code=409, detail=str(exc)) from exc
                raise HTTPException(status_code=500, detail=str(exc)) from exc


class ReportController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        service = self.ctx.service

        @app.get("/api/reports")
        def reports(
            device: str,
            results_type: Optional[str] = None,
            project: Optional[str] = None,
            device_id: Optional[str] = None,
        ):
            return application(service).list_reports(
                device, results_type, project=project, device_id=device_id
            )

        @app.get("/api/reports/open")
        def open_report(path: str):
            code, resolved = application(service).open_report(path)
            if code == 403:
                raise HTTPException(status_code=403, detail="Path not allowed")
            if code == 404 or not resolved:
                raise HTTPException(status_code=404, detail="Report not found")
            return FileResponse(resolved)


class AlarmController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        ctx = self.ctx
        service = ctx.service

        @app.get("/api/alarms")
        def alarms():
            facade = application(service)
            now = time.monotonic()
            cached_at = float(ctx.alarms_cache.get("cached_at") or 0.0)
            if now - cached_at <= ctx.alarms_cache_ttl_sec:
                cached_rows = ctx.alarms_cache.get("alarms") or []
                return {
                    "alarms": cached_rows,
                    "popups": facade.alarms.pop_pending_popups(),
                }
            payload = facade.list_alarms()
            ctx.alarms_cache["alarms"] = payload.get("alarms") or []
            ctx.alarms_cache["cached_at"] = time.monotonic()
            return payload

        @app.post("/api/alarms/{alarm_id}/ack")
        def acknowledge_alarm(request: Request, alarm_id: int):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Acknowledge is allowed from localhost only")
            row = application(service).acknowledge_alarm(alarm_id)
            if not row:
                raise HTTPException(status_code=404, detail="Alarm not found")
            return {"id": alarm_id, "acknowledged": True}

        @app.post("/api/alarms/reset")
        def reset_alarms(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Reset is allowed from localhost only")
            try:
                application(service).reset_alarms()
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            return {"reset": True}


def register_routes(app: FastAPI, ctx: WebApp) -> None:
    app.mount("/static", StaticFiles(directory=str(ctx.static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        return HTMLResponse(ctx.index_html())

    @app.get("/ui", response_class=HTMLResponse)
    async def ui_redirect() -> HTMLResponse:
        return HTMLResponse(ctx.index_html())

    StatusController(ctx).register(app)
    EngineController(ctx).register(app)
    SilworxController(ctx).register(app)
    DeviceController(ctx).register(app)
    CatalogController(ctx).register(app)
    ReportController(ctx).register(app)
    AlarmController(ctx).register(app)
