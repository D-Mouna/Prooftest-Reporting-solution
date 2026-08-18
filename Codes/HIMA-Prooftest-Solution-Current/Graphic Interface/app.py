from __future__ import annotations

import os
import tempfile
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

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

STATIC_DIR = Path(__file__).resolve().parent / "static"
APP_VERSION = "1.61.8"


def _is_local_client(request: Request) -> bool:
    if request.client is None:
        return False
    host = request.client.host
    return host in ("127.0.0.1", "::1", "localhost")


def _auth_ok(request: Request, service: "ProoftestService") -> bool:
    if not service.config.web_auth_enabled:
        return True
    if service.config.web_localhost_bypass and _is_local_client(request):
        return True
    token = request.headers.get("X-Prooftest-Token") or request.query_params.get("token")
    return bool(token and token == service.config.web_auth_token)


def create_app(
    service: "ProoftestService",
    on_shutdown: Optional[Callable[[str], None]] = None,
) -> FastAPI:
    if on_shutdown is not None:
        service.set_shutdown_callback(on_shutdown)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        service.stop("uvicorn_shutdown")

    app = FastAPI(title="HIMA Automated Prooftest", version=APP_VERSION, lifespan=lifespan)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    alarms_cache_lock = threading.Lock()
    alarms_cache: dict[str, object] = {"alarms": [], "cached_at": 0.0}
    alarms_cache_ttl_sec = 3.0

    @app.middleware("http")
    async def web_auth_middleware(request: Request, call_next):
        path = request.url.path
        if service.config.web_auth_enabled and (
            path.startswith("/api/") or path in ("/", "/ui")
        ):
            if not _auth_ok(request, service):
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Authentication required (X-Prooftest-Token or ?token=)"},
                )
        return await call_next(request)

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        if "<base " not in html:
            html = html.replace("<head>", '<head>\n  <base href="/static/">', 1)
        return HTMLResponse(html)

    @app.get("/ui", response_class=HTMLResponse)
    async def ui_redirect() -> HTMLResponse:
        """Alias for operators bookmarking /ui."""
        html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        if "<base " not in html:
            html = html.replace("<head>", '<head>\n  <base href="/static/">', 1)
        return HTMLResponse(html)

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

    @app.get("/api/devices")
    def devices(view: str = "all"):
        try:
            return service.db.list_devices(view=view)
        except Exception:
            return []

    @app.get("/api/reports")
    def reports(device: str, results_type: Optional[str] = None):
        return list_reports_for_device(
            service.config.report_output,
            device,
            results_type=results_type,
        )

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

    @app.get("/api/reports/open")
    def open_report(path: str):
        file_path = Path(path).resolve()
        output_root = service.config.report_output.resolve()
        mirror_root = service.config.report_mirror.resolve()
        if not (str(file_path).startswith(str(output_root)) or str(file_path).startswith(str(mirror_root))):
            raise HTTPException(status_code=403, detail="Path not allowed")
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        return FileResponse(file_path)

    @app.get("/api/alarms")
    def alarms():
        now = time.monotonic()
        cached_rows = alarms_cache.get("alarms") if isinstance(alarms_cache.get("alarms"), list) else []
        cached_at = float(alarms_cache.get("cached_at") or 0.0)

        if now - cached_at > alarms_cache_ttl_sec and alarms_cache_lock.acquire(blocking=False):
            try:
                try:
                    keys = service.alarms.active_error_keys()
                    active_keys = set(keys) if isinstance(keys, (set, list, tuple, frozenset)) else set()
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
                alarms_cache["alarms"] = enriched
                alarms_cache["cached_at"] = time.monotonic()
                cached_rows = enriched
            finally:
                alarms_cache_lock.release()
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
        """Restart the Prooftest engine in-process (web host already running)."""
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
        """Stop OPC/API/plugin workers; keep the graphic interface (web host) alive."""
        if not _is_local_client(request):
            raise HTTPException(status_code=403, detail="Stop is allowed from localhost only")
        reason = request.query_params.get("reason", "ui_stop")
        # Set flags in this request so the UI sees stopped immediately and any
        # in-flight Start is invalidated before cleanup runs.
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
        """Full process exit (G-11) — for stop_service.ps1 / SILworX uninstall."""
        if not _is_local_client(request):
            raise HTTPException(status_code=403, detail="Shutdown is allowed from localhost only")
        reason = request.query_params.get("reason", "api_shutdown")

        def _run() -> None:
            service.request_shutdown(reason, exit_process=True)

        threading.Thread(target=_run, daemon=True, name="api-shutdown").start()
        return {"status": "shutdown_started", "reason": reason, "web_host_alive": False}

    return app
