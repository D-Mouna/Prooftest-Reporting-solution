from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

from fastapi import Request

from layers.presentation.web_app import create_app as _create_app

if TYPE_CHECKING:
    from prooftest.service import ProoftestService

STATIC_DIR = Path(__file__).resolve().parent / "static"
APP_VERSION = "1.73.0"

def _is_local_client(request: Request) -> bool:
    """Gate tests patch this symbol to bypass localhost-only checks."""
    if request.client is None:
        return False
    host = request.client.host
    return host in ("127.0.0.1", "::1", "localhost")


def create_app(
    service: "ProoftestService",
    on_shutdown: Optional[Callable[[str], None]] = None,
):
    return _create_app(
        service,
        on_shutdown=on_shutdown,
        static_dir=STATIC_DIR,
        version=APP_VERSION,
    )
