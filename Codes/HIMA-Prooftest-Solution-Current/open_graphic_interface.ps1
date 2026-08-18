# Open the HIMA Prooftest web GUI in the default browser.
# The GUI must be served over HTTP — opening index.html directly (file://) cannot load API data.
$ErrorActionPreference = "Stop"
$host.ui.RawUI.WindowTitle = "HIMA Prooftest - Open GUI"
$root = $PSScriptRoot
$port = 8080
$ini = Join-Path $root "solution.ini"
if (Test-Path $ini) {
    $m = Select-String -Path $ini -Pattern '^\s*port\s*=\s*(\d+)' | Select-Object -First 1
    if ($m) { $port = [int]$m.Matches[0].Groups[1].Value }
}
$url = "http://127.0.0.1:$port/"
Write-Host "Opening $url"
Write-Host "(Do not open Graphic Interface\static\index.html directly — use this URL while the service is running.)"
Start-Process $url
