"""Presentation layer — FastAPI controllers. No OPC COM or SILworX HTTP here."""

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

from prooftest.annex_list_archive import (
    ListArchiveError,
    clear_keep_opc_only,
    create_list_archive,
    list_list_archives,
    restore_from_uploaded_file,
    restore_list_archive,
)
from prooftest.annex_pdf_generation import list_reports_for_device

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
            return service.health()

        @app.get("/api/running-tests")
        def running_tests():
            try:
                return service.db.list_running_tests()
            except Exception:
                return []

        @app.get("/api/test-history")
        def test_history():
            try:
                return service.db.list_test_history()
            except Exception:
                return []


class EngineController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        service = self.ctx.service

        @app.post("/api/refresh")
        def refresh():
            if service._stopped:
                return {
                    "status": "engine_stopped",
                    "detail": "Start the service before Refresh",
                    "popups": service.alarms.pop_pending_popups(),
                }

            def _run() -> None:
                service.refresh(manual=True)

            threading.Thread(target=_run, daemon=True, name="manual-refresh").start()
            return {"status": "refresh_started", "popups": service.alarms.pop_pending_popups()}

        @app.post("/api/start")
        def start_service(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Start is allowed from localhost only")
            if service._starting:
                return {
                    "status": "start_in_progress",
                    "port": service.config.web_port,
                    "starting": True,
                    "web_host_alive": True,
                }
            if not service._stopped and service.engine_running:
                return {
                    "status": "already_running",
                    "port": service.config.web_port,
                    "engine_running": True,
                }

            def _run() -> None:
                try:
                    service.start()
                except Exception:
                    import logging

                    logging.getLogger("prooftest.web").exception("Engine start failed")

            threading.Thread(target=_run, daemon=True, name="engine-start").start()
            return {
                "status": "engine_start_requested",
                "port": service.config.web_port,
                "starting": True,
                "web_host_alive": True,
            }

        @app.post("/api/stop")
        def stop_engine(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Stop is allowed from localhost only")
            reason = request.query_params.get("reason", "ui_stop")
            service.request_stop_flags(reason)

            def _run() -> None:
                from prooftest.annex_stop_service import perform_graceful_shutdown

                perform_graceful_shutdown(service, reason)

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
                service.request_shutdown(reason, exit_process=True)

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
            return service.close_silworx_connection()

        @app.post("/api/silworx/connect")
        def silworx_connect(request: Request):
            if not _is_local_client(request):
                raise HTTPException(
                    status_code=403, detail="SILworX connect is allowed from localhost only"
                )
            return service.resume_silworx_connection()


class DeviceController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        service = self.ctx.service

        @app.get("/api/devices")
        def devices(view: str = "all"):
            try:
                return service.db.list_devices(view=view)
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
                return list_list_archives(service.config)
            except Exception:
                return []

        @app.post("/api/archives")
        def create_archive(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Archive is allowed from localhost only")
            try:
                return create_list_archive(service.db, service.config)
            except ListArchiveError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc

        @app.post("/api/archives/restore")
        def restore_archive(request: Request, archive_id: str = ""):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Restore is allowed from localhost only")
            try:
                return restore_list_archive(service.db, service.config, archive_id)
            except ListArchiveError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            except Exception as exc:
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
                return restore_from_uploaded_file(service.db, service.config, tmp_path, filename)
            except ListArchiveError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            finally:
                tmp_path.unlink(missing_ok=True)

        @app.post("/api/devices/keep-opc")
        def keep_opc_devices(request: Request, archive: bool = True):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Clear is allowed from localhost only")
            try:
                return clear_keep_opc_only(service.db, service.config, archive_first=archive)
            except ListArchiveError as exc:
                raise HTTPException(status_code=409, detail=str(exc)) from exc
            except Exception as exc:
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
            return list_reports_for_device(
                service.config.report_output,
                device,
                results_type=results_type,
                project=project,
                device_id=device_id,
            )

        @app.get("/api/reports/open")
        def open_report(path: str):
            file_path = Path(path).resolve()
            output_root = service.config.report_output.resolve()
            mirror_root = service.config.report_mirror.resolve()
            if not (
                str(file_path).startswith(str(output_root))
                or str(file_path).startswith(str(mirror_root))
            ):
                try:
                    service.alarms.raise_alarm("GUI", "Path outside report root", action="OpenReport")
                except Exception:
                    pass
                raise HTTPException(status_code=403, detail="Path not allowed")
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Report not found")
            return FileResponse(file_path)


class AlarmController:
    def __init__(self, ctx: WebApp) -> None:
        self.ctx = ctx

    def register(self, app: FastAPI) -> None:
        ctx = self.ctx
        service = ctx.service

        @app.get("/api/alarms")
        def alarms():
            now = time.monotonic()
            cached_rows = (
                ctx.alarms_cache.get("alarms")
                if isinstance(ctx.alarms_cache.get("alarms"), list)
                else []
            )
            cached_at = float(ctx.alarms_cache.get("cached_at") or 0.0)

            if now - cached_at > ctx.alarms_cache_ttl_sec and ctx.alarms_cache_lock.acquire(
                blocking=False
            ):
                try:
                    try:
                        keys = service.alarms.active_error_keys()
                        active_keys = (
                            set(keys) if isinstance(keys, (set, list, tuple, frozenset)) else set()
                        )
                    except Exception:
                        active_keys = set()
                    try:
                        alarm_rows = service.db.list_recent_alarms()
                    except Exception:
                        alarm_rows = service.alarms.recent_alarms()

                    enriched = []
                    for row in alarm_rows:
                        item = dict(row)
                        key = item.get("error_key") or f"{item.get('step')}|{str(item.get('message') or '')[:120]}"
                        acknowledged = bool(item.get("acknowledged"))
                        item["error_key"] = key
                        item["acknowledged"] = acknowledged
                        item["active"] = key in active_keys
                        enriched.append(item)
                    ctx.alarms_cache["alarms"] = enriched
                    ctx.alarms_cache["cached_at"] = time.monotonic()
                    cached_rows = enriched
                finally:
                    ctx.alarms_cache_lock.release()
            return {
                "alarms": cached_rows,
                "popups": service.alarms.pop_pending_popups(),
            }

        @app.post("/api/alarms/{alarm_id}/ack")
        def acknowledge_alarm(request: Request, alarm_id: int):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Acknowledge is allowed from localhost only")
            row = service.db.acknowledge_alarm(alarm_id)
            if not row:
                raise HTTPException(status_code=404, detail="Alarm not found")
            try:
                service.alarms.acknowledge_error_key(row.get("error_key") or "")
            except Exception:
                pass
            return {"id": alarm_id, "acknowledged": True}

        @app.post("/api/alarms/reset")
        def reset_alarms(request: Request):
            if not _is_local_client(request):
                raise HTTPException(status_code=403, detail="Reset is allowed from localhost only")
            try:
                service.db.reset_alarms()
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
            try:
                service.alarms.reset_all()
            except Exception:
                pass
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
