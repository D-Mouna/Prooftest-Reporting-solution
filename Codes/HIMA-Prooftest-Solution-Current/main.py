#!/usr/bin/env python3
"""HIMA Automated Prooftest Solution — SPEC-001 v1.18."""

from __future__ import annotations

import argparse
import logging
import signal
import sys
from pathlib import Path

import uvicorn

_ROOT = Path(__file__).resolve().parent
_ANNEX_PY = _ROOT / "Annex codes"
if str(_ANNEX_PY) not in sys.path:
    sys.path.insert(0, str(_ANNEX_PY))

from prooftest.config import AppConfig
from prooftest.service import ProoftestService
from prooftest.web.app import create_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("main")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HIMA Automated Prooftest reporting service")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(__file__).resolve().parent / "solution.ini",
        help="Path to solution.ini",
    )
    parser.add_argument("--host", default=None, help="Web host override")
    parser.add_argument("--port", type=int, default=None, help="Web port override")
    return parser.parse_args()


def main() -> int:
    if sys.platform != "win32":
        log.error("This solution requires Microsoft Windows for OPC DA.")
        return 1

    args = parse_args()
    config = AppConfig.load(args.config)
    host = args.host or config.web_host
    port = args.port or config.web_port

    service = ProoftestService(config)
    service.start()

    server_holder: dict[str, uvicorn.Server] = {}

    def trigger_shutdown(reason: str) -> None:
        log.info("Process shutdown: %s", reason)
        server = server_holder.get("server")
        if server is not None:
            server.should_exit = True

    app = create_app(service, on_shutdown=trigger_shutdown)
    uv_config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(uv_config)
    server_holder["server"] = server

    def _signal_handler(signum: int, _frame) -> None:
        service.request_shutdown(f"signal_{signum}")

    signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _signal_handler)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, _signal_handler)

    log.info("Web UI: http://%s:%s/", host, port)
    log.info("Engine stop (UI stays up): POST http://%s:%s/api/stop (localhost only)", host, port)
    log.info("Process exit (G-11): POST http://%s:%s/api/shutdown (localhost only)", host, port)
    try:
        server.run()
    except KeyboardInterrupt:
        log.info("Shutting down...")
    finally:
        service.stop("process_exit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
