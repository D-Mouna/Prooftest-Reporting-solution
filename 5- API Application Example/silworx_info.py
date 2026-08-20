"""Connect to SILworX via SAPI and call /silworx/info."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SAPI_EXAMPLE_DIR = Path(r"Z:\Project\Report Solution\5- API Application Example")
if str(SAPI_EXAMPLE_DIR) not in sys.path:
    sys.path.insert(0, str(SAPI_EXAMPLE_DIR))

from sapi import SapiClient, SapiError  # noqa: E402


def main() -> int:
    host = "localhost"
    port = 51712

    client = SapiClient(host=host, port=port)
    try:
        info = client.silworx_info()
    except SapiError as exc:
        print(f"SAPI error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(info, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
