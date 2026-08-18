#!/usr/bin/env python3
"""
SILworX development plugin: expose API session id only (no globals CSV export).

Register in SILworX settings.ini [Plugin_Server] Development=prooftest_session_plugin
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

PLUGIN_ROOT = Path(
    r"C:\Program Files\HIMA\SILworX_v16.0.0 R3326\c3\asyncapi\documentation\plugin_example"
)
sys.path.insert(0, str(PLUGIN_ROOT))

from plugin_example.base.plugin_base import PluginBase  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("prooftest_session_plugin")


class ProoftestSessionPlugin(PluginBase):
  """Minimal plugin so REST clients can receive TRIGGER_SESSION_ID_CHANGED."""

  def __init__(self) -> None:
    super().__init__(name="prooftest_session_plugin", version="1.0.0")

  async def on_project_opened(self) -> None:
    log.info("Prooftest session plugin ready (no globals CSV export)")


if __name__ == "__main__":
    ProoftestSessionPlugin().run()
