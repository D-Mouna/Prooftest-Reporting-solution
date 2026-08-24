"""
Annex — graceful service shutdown (G-11).
"""

from __future__ import annotations

import logging
import threading
import time

log = logging.getLogger(__name__)

SHUTDOWN_JOIN_TIMEOUT_SEC = 10.0
# Soft deadline for the whole Stop path (joins can burn 10s each).
STOP_WATCHDOG_SEC = 30.0


def clear_stop_in_progress(service, *, reason: str = "") -> None:
    """Always clear the UI 'Stopping' flag and drop stale health cache."""
    try:
        service._stop_in_progress = False
    except Exception:
        pass
    try:
        service._health_cache = {}
        service._health_cache_at = 0.0
    except Exception:
        pass
    if reason:
        log.info("Stop in-progress cleared (%s)", reason)


def perform_graceful_shutdown(service, reason: str = "") -> None:
    """Release OPC, SILworX API, monitor, DB — used by ProoftestService.stop()."""
    if reason:
        log.info("Stopping Prooftest service: %s", reason)
    else:
        log.info("Stopping Prooftest service")

    try:
        # Stop background work and plugin WebSockets first. OPC disconnect can block
        # on the COM lock; if it runs before plugin shutdown, SILworX keeps seeing
        # registration retries after the UI Stop button.
        service._stop.set()
        try:
            service._case1_sync.shutdown()
        except Exception as exc:
            log.warning("Case1 sync shutdown failed: %s", exc)
        if service.monitor:
            try:
                service.monitor.shutdown()
            except Exception as exc:
                log.warning("Monitor shutdown failed: %s", exc)
        try:
            service.db.interrupt_open_tests()
        except Exception as exc:
            log.warning("Could not mark open tests interrupted: %s", exc)
        try:
            service.opc.invalidate_cache()
        except Exception as exc:
            log.warning("OPC invalidate during shutdown failed: %s", exc)
        current = threading.current_thread()
        for thread in list(getattr(service, "_threads", []) or []):
            if thread is current:
                continue
            thread.join(timeout=SHUTDOWN_JOIN_TIMEOUT_SEC)
            if thread.is_alive():
                log.warning(
                    "Background thread %s did not stop within %.0fs",
                    thread.name,
                    SHUTDOWN_JOIN_TIMEOUT_SEC,
                )
        try:
            service.db.set_service_state("stopped_at", time.strftime("%Y-%m-%d %H:%M:%S"))
            service.db.set_service_state("engine", "stopped")
            if reason:
                service.db.set_service_state("stop_reason", reason)
        except Exception:
            pass
        try:
            service.db.close()
        except Exception:
            pass
        log.info(
            "Prooftest engine stopped (%s) — web host remains available for Start",
            reason or "no reason",
        )
    finally:
        # Must run even if OPC/DB teardown raises — otherwise Status stays on Stopping.
        clear_stop_in_progress(service, reason=reason or "shutdown_complete")
