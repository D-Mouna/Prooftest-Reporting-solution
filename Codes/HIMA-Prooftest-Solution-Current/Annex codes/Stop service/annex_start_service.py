"""
Annex — cold-start helper when no web host is listening (SPEC §5.4 / §5.5).

When the graphic interface is already up, Start uses in-process ``service.start()``.
This module only spawns ``main.py`` for a dead process (e.g. scripts).
"""

from __future__ import annotations

import socket
import subprocess
import sys
from pathlib import Path
from typing import Dict, Union


def is_port_listening(host: str, port: int, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def find_python32() -> Path:
    candidates = [
        Path(r"C:\Python 312_32bit\python.exe"),
        Path(r"C:\Python3.11_32bit\python.exe"),
        Path(r"C:\Users\Administrator\Desktop\Report-Tool\opc_env\Scripts\python.exe"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return Path(sys.executable)


def spawn_background_service(solution_root: Path, config_path: Path, port: int) -> Dict[str, Union[str, int]]:
    if is_port_listening("127.0.0.1", port):
        return {"status": "already_running", "port": port}

    python_exe = find_python32()
    creationflags = 0
    if sys.platform == "win32":
        creationflags = (
            subprocess.CREATE_NEW_PROCESS_GROUP
            | subprocess.DETACHED_PROCESS
            | getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        )

    proc = subprocess.Popen(
        [str(python_exe), "main.py", "--config", str(config_path)],
        cwd=str(solution_root),
        creationflags=creationflags,
        close_fds=True,
    )
    return {"status": "start_requested", "pid": proc.pid, "port": port}
