# Run Tool test gate scripts (service must be running for test_smoke.py)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Solution = Split-Path -Parent (Split-Path -Parent $Root)
$Py32 = "C:\Python 312_32bit\python.exe"
if (-not (Test-Path $Py32)) {
    throw "32-bit Python not found at $Py32"
}

Set-Location $Root
$scripts = @(
    "_step1_audit.py",
    "test_step4_install.py",
    "test_step5_sql.py",
    "test_silworx_api.py",
    "test_sapi_session_header.py",
    "test_plugin_session_refresh.py",
    "test_device_list_retention.py",
    "test_list_archive.py",
    "test_layers.py",
    "test_alarm_status.py",
    "test_step11_web_ui.py",
    "test_step6_devices.py",
    "test_step8_triggers.py",
    "test_smoke.py"
)

foreach ($script in $scripts) {
    Write-Host "`n=== $script ===" -ForegroundColor Cyan
    & $Py32 $script
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "$script failed with exit code $LASTEXITCODE"
    }
}
