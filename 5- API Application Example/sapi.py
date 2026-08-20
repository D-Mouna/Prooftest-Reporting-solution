"""SILworX SAPI client foundation for the CI/CD MVP."""

from __future__ import annotations

import http.client
import json
import socket
import ssl
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode

from silworx_registry import discover_silworx_versions


class SapiError(Exception):
    """Base class for SILworX SAPI client failures."""


class SapiSessionError(SapiError):
    """Raised when an operation requires a missing project session."""


class SapiHttpError(SapiError):
    """Raised for non-success HTTP status codes."""


class SapiConnectionError(SapiError):
    """Raised for transport-level failures."""


class SapiResponseError(SapiError):
    """Raised for invalid SAPI responses."""


class SapiVersionError(SapiError):
    """Raised when a requested SILworX version cannot be resolved."""


class SapiProcessError(SapiError):
    """Raised when SILworX process lifecycle operations fail."""


ConnectionFactory = Callable[..., http.client.HTTPSConnection]


class SapiClient:
    """Small session-aware HTTPS client for `/api/v1` SILworX endpoints."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 51710,
        *,
        verify_tls: bool = False,
        timeout_s: int = 900,
        connection_factory: ConnectionFactory | None = None,
    ) -> None:
        self.host = host
        self.port = int(port)
        self.timeout_s = int(timeout_s)
        self.user_session_id: str | None = None
        self.process: subprocess.Popen | None = None
        self._connection_factory = connection_factory or http.client.HTTPSConnection
        self._ssl_context = (
            ssl.create_default_context()
            if verify_tls
            else ssl._create_unverified_context()
        )

    def start_silworx(
        self,
        version: str,
        *,
        installed_versions: list[dict[str, str]] | None = None,
        startup_timeout_s: float = 30.0,
    ) -> dict[str, Any]:
        """Start a local headless SILworX instance for the requested version."""
        if is_port_open(self.host, self.port):
            raise SapiProcessError(f"port {self.port} is already in use")

        match = resolve_installed_version(
            version,
            installed_versions if installed_versions is not None else discover_silworx_versions(),
        )
        exe = Path(match["path"]) / "c3" / "bin" / "c3.exe"
        if not exe.exists():
            raise SapiProcessError(f"SILworX executable not found: {exe}")

        args = [
            str(exe),
            f"-DAPI_Server.Port={self.port}",
            # "-DAPI_Server.NoGUI=TRUE",
        ]
        try:
            self.process = subprocess.Popen(
                args,
                creationflags=_windows_detached_flags(),
                close_fds=True,
            )
        except OSError as exc:
            raise SapiProcessError(f"failed to start SILworX: {exc}") from exc

        deadline = time.monotonic() + startup_timeout_s
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise SapiProcessError("SILworX process exited during startup")
            if is_port_open(self.host, self.port):
                return {
                    "ok": True,
                    "version": match["version"],
                    "path": str(exe),
                    "port": self.port,
                }
            time.sleep(0.25)

        self.force_close()
        raise SapiProcessError(f"SILworX API did not open port {self.port}")

    def force_close(self) -> None:
        """Best-effort termination of a locally spawned SILworX process."""
        proc = self.process
        self.process = None
        if proc is None:
            return
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=2.0)
                except subprocess.TimeoutExpired:
                    proc.kill()
        except Exception:
            pass

    def silworx_info(self) -> dict[str, Any]:
        resp = self.call_json("/silworx/info", require_session=False)
        return resp.get("results", {})

    def close_silworx(self) -> dict[str, Any]:
        return self.call_json("/silworx/close", require_session=False)

    def open_project(
        self,
        project_file: str | Path,
        *,
        username: str | None = None,
        password: str | None = None,
        advice_level: str | None = None,
    ) -> dict[str, Any]:
        """Upload and open a project file through `/project/open`."""
        path = Path(project_file)
        content_type, body = encode_multipart(
            files=[("body", path.name, path.read_bytes())],
        )
        headers = {"Content-Type": content_type}
        if username is not None:
            headers["HIMA_SAPI_username"] = username
        if password is not None:
            headers["HIMA_SAPI_password"] = password
        query = {"advice_level": advice_level} if advice_level else None
        return self.call_json(
            "/project/open",
            query=query,
            raw_body=body,
            extra_headers=headers,
            require_session=False,
        )

    def close_project(self) -> dict[str, Any]:
        return self.call_json("/project/close", require_session=True)

    def structuretree_info(self) -> dict[str, Any]:
        resp = self.call_json("/project/structuretree/info", require_session=True)
        return resp.get("results", {})

    def create_node(
        self,
        internal_address: str,
        node_type: str,
        node_name: str,
        *,
        advice_level: str | None = None,
    ) -> dict[str, Any]:
        query = {
            "internal_address": internal_address,
            "node_type": node_type,
            "node_name": node_name,
        }
        if advice_level:
            query["advice_level"] = advice_level
        return self.call_json("/node/create", query=query, require_session=True)

    def restore_node_archive(
        self,
        internal_address: str,
        archive_file: str | Path,
        *,
        advice_level: str | None = None,
    ) -> dict[str, Any]:
        query = {"internal_address": internal_address}
        if advice_level:
            query["advice_level"] = advice_level
        return self.call_json(
            "/node/archive/restore",
            query=query,
            raw_body=Path(archive_file).read_bytes(),
            extra_headers={"Content-Type": "application/octet-stream"},
            require_session=True,
        )

    def create_node_archive(
        self,
        internal_address: str,
        archive_file: str | Path,
        *,
        advice_level: str | None = None,
    ) -> Path:
        query = {"internal_address": internal_address}
        if advice_level:
            query["advice_level"] = advice_level
        data = self.call_bytes("/node/archive/create", query=query, require_session=True)
        output = Path(archive_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(data)
        return output

    def write_st_function_block_content(
        self,
        internal_address: str,
        *,
        var_externals: list[dict[str, Any]],
        instances: list[dict[str, Any]],
        local_variables: list[dict[str, Any]],
        st_text: dict[str, Any] | str,
        advice_level: str | None = None,
    ) -> dict[str, Any]:
        query = {"internal_address": internal_address}
        if advice_level:
            query["advice_level"] = advice_level
        st_text_payload = {"code": st_text} if isinstance(st_text, str) else st_text
        return self.call_json(
            "/node/stfunctionblock/content/write",
            query=query,
            json_body={
                "var_externals": var_externals,
                "instances": instances,
                "local_variables": local_variables,
                "st_text": st_text_payload,
            },
            require_session=True,
        )

    def codegen_resource(
        self,
        internal_address: str,
        *,
        advice_level: str | None = None,
    ) -> dict[str, Any]:
        query = {"internal_address": internal_address}
        if advice_level:
            query["advice_level"] = advice_level
        return self.call_json("/node/codegen", query=query, require_session=True)

    def read_resource_properties(
        self,
        internal_address: str,
        *,
        advice_level: str | None = None,
    ) -> dict[str, Any]:
        query = {"internal_address": internal_address}
        if advice_level:
            query["advice_level"] = advice_level
        resp = self.call_json("/node/resource/properties/read", query=query, require_session=True)
        return resp.get("results", {})

    def call_json(
        self,
        path: str,
        *,
        method: str = "POST",
        query: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        raw_body: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
        require_session: bool = True,
    ) -> dict[str, Any]:
        status, data, full_path = self._request(
            path,
            method=method,
            query=query,
            json_body=json_body,
            raw_body=raw_body,
            extra_headers=extra_headers,
            require_session=require_session,
        )
        if status < 200 or status >= 300:
            detail = data.decode("utf-8", errors="replace") if data else ""
            raise SapiHttpError(f"HTTP error {status} for {full_path}: {detail[:1000]}")
        if not data:
            return {}
        try:
            payload = json.loads(data.decode("utf-8"))
        except Exception as exc:
            raise SapiResponseError(f"non-JSON response for {full_path}: {exc}") from exc
        self._capture_session(payload)
        return payload

    def call_bytes(
        self,
        path: str,
        *,
        method: str = "POST",
        query: dict[str, Any] | None = None,
        require_session: bool = True,
    ) -> bytes:
        status, data, full_path = self._request(
            path,
            method=method,
            query=query,
            require_session=require_session,
        )
        if status < 200 or status >= 300:
            detail = data.decode("utf-8", errors="replace") if data else ""
            raise SapiHttpError(f"HTTP error {status} for {full_path}: {detail[:1000]}")
        return data

    def _request(
        self,
        path: str,
        *,
        method: str,
        query: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        raw_body: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
        require_session: bool = True,
    ) -> tuple[int, bytes, str]:
        if not path.startswith("/"):
            raise ValueError("path must start with '/'")
        if json_body is not None and raw_body is not None:
            raise ValueError("provide json_body or raw_body, not both")

        headers = {"Accept": "application/json"}
        if extra_headers:
            headers.update({key: str(value) for key, value in extra_headers.items()})
        if require_session:
            if not self.user_session_id:
                raise SapiSessionError("SILworX project session is required")
            headers["HIMA_SAPI_user_session_id"] = self.user_session_id

        body: bytes | None = None
        if json_body is not None:
            body = json.dumps(json_body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        elif raw_body is not None:
            body = raw_body

        full_path = f"/api/v1{path}"
        if query:
            full_path = f"{full_path}?{urlencode(query, doseq=True)}"

        conn = self._connection_factory(
            self.host,
            self.port,
            context=self._ssl_context,
            timeout=self.timeout_s,
        )
        try:
            conn.request(method.upper(), full_path, body=body, headers=headers)
            response = conn.getresponse()
            status = response.status
            data = response.read()
        except (TimeoutError, socket.timeout) as exc:
            raise SapiConnectionError(f"request timed out for {full_path}: {exc}") from exc
        except Exception as exc:
            raise SapiConnectionError(f"request failed for {full_path}: {exc}") from exc
        finally:
            conn.close()

        return status, data, full_path

    def _capture_session(self, payload: dict[str, Any]) -> None:
        results = payload.get("results")
        if isinstance(results, dict):
            session_id = results.get("user_session_id")
            if isinstance(session_id, str) and session_id:
                self.user_session_id = session_id


def resolve_installed_version(
    requested_version: str,
    installed_versions: list[dict[str, str]],
) -> dict[str, str]:
    """Resolve a requested version prefix against registry discovery results."""
    if not requested_version:
        raise SapiVersionError("requested SILworX version is required")
    for candidate in installed_versions:
        version = candidate.get("version", "")
        if version.startswith(requested_version):
            return candidate
    raise SapiVersionError(f"SILworX version not found: {requested_version}")


def is_port_open(host: str, port: int) -> bool:
    """Return whether a TCP port accepts a connection."""
    try:
        with socket.create_connection((host, int(port)), timeout=0.5):
            return True
    except OSError:
        return False


def encode_multipart(
    *,
    fields: list[tuple[str, str]] | None = None,
    files: list[tuple[str, str, bytes]] | None = None,
) -> tuple[str, bytes]:
    """Encode multipart/form-data with binary file parts."""
    boundary = f"----SAPIFormBoundary{uuid.uuid4().hex}"
    body_parts: list[bytes] = []
    for name, value in fields or []:
        body_parts.append(f"--{boundary}\r\n".encode("utf-8"))
        body_parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body_parts.append(f"{value}\r\n".encode("utf-8"))
    for name, filename, content in files or []:
        body_parts.append(f"--{boundary}\r\n".encode("utf-8"))
        body_parts.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode("utf-8")
        )
        body_parts.append(b"Content-Type: application/octet-stream\r\n\r\n")
        body_parts.append(content)
        body_parts.append(b"\r\n")
    body_parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return f"multipart/form-data; boundary={boundary}", b"".join(body_parts)


def _windows_detached_flags() -> int:
    if not hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        return 0
    return (
        subprocess.DETACHED_PROCESS
        | subprocess.CREATE_NEW_PROCESS_GROUP
        | getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0)
    )
