param(
    [string[]]$Args
)

Set-Location $PSScriptRoot
if (-not (Test-Path ".\opc_env\Scripts\python.exe")) {
    Write-Error "Run setup.ps1 first to create opc_env."
}
& ".\opc_env\Scripts\python.exe" ".\Connection-opc.py" @Args
