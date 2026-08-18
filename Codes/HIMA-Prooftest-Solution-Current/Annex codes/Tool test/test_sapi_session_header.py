#!/usr/bin/env python3
"""Regression: SILworX session header must keep exact casing (not urllib capitalize)."""

from __future__ import annotations

import urllib.request
from pathlib import Path

from _paths import setup_path

setup_path()

from prooftest.annex_api_connexion import SESSION_HEADER_NAME, SilworxApiClient


class _FakeResponse:
    status = 200

    def read(self) -> bytes:
        return b'{"results":{}}'


class _FakeConn:
    last_headers = None
    last_path = None

    def __init__(self, host, port, **kwargs):
        self.host = host
        self.port = port

    def request(self, method, path, body=None, headers=None):
        type(self).last_headers = dict(headers or {})
        type(self).last_path = path

    def getresponse(self):
        return _FakeResponse()

    def close(self):
        pass


def main() -> int:
    req = urllib.request.Request(
        "https://127.0.0.1/api/v1/project/structuretree/info",
        method="POST",
        headers={SESSION_HEADER_NAME: "token-abc"},
    )
    urllib_names = list(req.headers.keys())
    if SESSION_HEADER_NAME in urllib_names:
        print("FAIL urllib unexpectedly preserved exact header casing")
        return 1
    mangled = [name for name in urllib_names if name.lower() == SESSION_HEADER_NAME.lower()]
    if not mangled:
        print(f"FAIL expected urllib to send a mangled session header, got {urllib_names}")
        return 1

    _FakeConn.last_headers = None
    client = SilworxApiClient(
        host="127.0.0.1",
        port=51710,
        server_ca_cert=Path("."),
        connection_factory=_FakeConn,
    )
    client.user_session_id = "token-abc"
    client._request("/project/structuretree/info", require_session=True)
    headers = _FakeConn.last_headers or {}
    if SESSION_HEADER_NAME not in headers:
        print(f"FAIL client did not send exact {SESSION_HEADER_NAME!r}; got {list(headers)}")
        return 1
    if headers[SESSION_HEADER_NAME] != "token-abc":
        print("FAIL session token value mismatch")
        return 1
    print("OK  session header sent with exact HIMA_SAPI_user_session_id casing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
