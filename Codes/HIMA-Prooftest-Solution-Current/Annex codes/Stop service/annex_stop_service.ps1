# Stop HIMA Prooftest background service before SILworX uninstall (SPEC G-11)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
$Ini = Join-Path $Root "solution.ini"
$Port = 8080

if (Test-Path $Ini) {
    $match = Select-String -Path $Ini -Pattern '^\s*port\s*=\s*(\d+)' | Select-Object -First 1
    if ($match) {
        $Port = [int]$match.Matches[0].Groups[1].Value
    }
}

$Url = "http://127.0.0.1:$Port/api/shutdown?reason=silworx_uninstall"
Write-Host "Requesting graceful shutdown: $Url"
try {
    Invoke-WebRequest -Method POST -Uri $Url -TimeoutSec 10 -UseBasicParsing | Out-Null
} catch {
    Write-Warning "Shutdown endpoint not reachable ($($_.Exception.Message)); trying to stop process directly."
}

$deadline = (Get-Date).AddSeconds(30)
do {
    $procs = Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='pythonw.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -like "*HIMA-Prooftest-Solution*main.py*" }
    if (-not $procs) {
        Write-Host "Prooftest service stopped."
        exit 0
    }
    Start-Sleep -Seconds 1
} while ((Get-Date) -lt $deadline)

Write-Warning "Service still running after 30s. Force-stopping Python process(es)."
foreach ($p in $procs) {
    Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
}
Write-Host "Done."
