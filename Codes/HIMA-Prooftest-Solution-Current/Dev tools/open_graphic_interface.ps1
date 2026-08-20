# DEV TOOL / Desktop shortcut target — open HIMA Prooftest Report UI
#
# Purpose:
#   Open the web UI in the default browser (http://127.0.0.1:<port>/).
#   Port is read from solution.ini [Web] port (default 8080).
#
# How users normally open the UI:
#   Double-click the Desktop shortcut "HIMA Prooftest Report"
#   (created automatically on first service start).
#
# This script is the target of that shortcut. It does not start the service —
# run_service.ps1 / Windows auto-start must already be running.
#
# Manual run:
#   powershell -ExecutionPolicy Bypass -File ".\Dev tools\open_graphic_interface.ps1"

$ErrorActionPreference = "Stop"
$SolutionRoot = Split-Path -Parent $PSScriptRoot
$port = 8080
$ini = Join-Path $SolutionRoot "solution.ini"
if (Test-Path -LiteralPath $ini) {
    $m = Select-String -Path $ini -Pattern '^\s*port\s*=\s*(\d+)' | Select-Object -First 1
    if ($m) { $port = [int]$m.Matches[0].Groups[1].Value }
}
$url = "http://127.0.0.1:$port/"
Start-Process $url
