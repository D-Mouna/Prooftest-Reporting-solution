# Dev tools (helpers — not the service engine)

Scripts here are **not** imported by `main.py`.  
One of them is the **Desktop shortcut target** so operators can open the UI by double-click.

| Script | Role |
|--------|------|
| [`open_graphic_interface.ps1`](./open_graphic_interface.ps1) | Opens the web UI in the browser. **Desktop shortcut** “HIMA Prooftest Report” (created on first run) points here. |
| [`sync_gui_images.ps1`](./sync_gui_images.ps1) | Optional: copy / refresh brand logos into `Graphic Interface/static/img/`. |

Production start/stop stay at solution root: `run_service.ps1`, `stop_service.ps1`, `install_auto_start.ps1`.
