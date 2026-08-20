# Setup 32-bit Python venv for HIMA X-OPC DA (X_OPC-25138)
# Requires: OPCDAAuto.dll registered in C:\Windows\SysWOW64 (regsvr32)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".\opc_env\Scripts\python.exe")) {
    py -3.11-32 -m venv opc_env
}

.\opc_env\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete. Test with:"
Write-Host "  .\opc_env\Scripts\Activate.ps1"
Write-Host "  python Connection-opc.py --discover-only"
Write-Host "  python Connection-opc.py --list-only"
Write-Host "  python Connection-opc.py --tag 200S2503-I11_IN"
