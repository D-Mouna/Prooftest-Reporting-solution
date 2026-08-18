# Run HIMA Prooftest solution with 32-bit Python (required for OPC DA)
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Py32 = "C:\Python 312_32bit\python.exe"
if (-not (Test-Path $Py32)) {
    $Py32 = "C:\Users\Administrator\Desktop\Report-Tool\opc_env\Scripts\python.exe"
}
if (-not (Test-Path $Py32)) {
    throw "32-bit Python not found. Install Python 3.12 32-bit for OPC DA."
}

function Read-IniValue {
    param([string]$IniPath, [string]$Section, [string]$Key, [string]$Default)
    if (-not (Test-Path $IniPath)) { return $Default }
    $current = ""
    foreach ($line in Get-Content $IniPath) {
        if ($line -match '^\s*\[(.+)\]\s*$') { $current = $Matches[1]; continue }
        if ($current -ne $Section) { continue }
        if ($line -match "^\s*$Key\s*=\s*(.+?)\s*$") { return $Matches[1].Trim() }
    }
    return $Default
}

$bootLog = Join-Path $Root "auto_start.log"
try {
    "[$(Get-Date -Format o)] run_service.ps1 start root=$Root" | Add-Content -Path $bootLog -Encoding UTF8
    Set-Location $Root

    $Ini = Join-Path $Root "solution.ini"
    $Port = 8080
    if (Test-Path $Ini) {
        $match = Select-String -Path $Ini -Pattern '^\s*port\s*=\s*(\d+)' | Select-Object -First 1
        if ($match) { $Port = [int]$match.Matches[0].Groups[1].Value }
    }
    Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
        Select-Object OwningProcess -Unique |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $Py32 -m pip install -r requirements.txt -q --disable-pip-version-check 2>&1 | Out-Null
    $ErrorActionPreference = $prevEap

    $stderrLog = Join-Path $Root "service_stderr.log"
    Write-Host "Starting Prooftest service in background..."
    $proc = Start-Process -FilePath $Py32 -ArgumentList @("main.py", "--config", "solution.ini") -WorkingDirectory $Root -WindowStyle Hidden -RedirectStandardError $stderrLog -PassThru

    $healthWaitSec = [int](Read-IniValue $Ini "Service" "health_check_wait_sec" "120")
    if ($healthWaitSec -lt 30) { $healthWaitSec = 30 }
    if ($healthWaitSec -gt 600) { $healthWaitSec = 600 }

    $healthUrl = "http://127.0.0.1:$Port/api/health"
    $deadline = (Get-Date).AddSeconds($healthWaitSec)
    $health = $null
    $pollSec = 10

    while ((Get-Date) -lt $deadline) {
        if (-not (Get-Process -Id $proc.Id -ErrorAction SilentlyContinue)) {
            Write-Warning "Service process (PID $($proc.Id)) exited before health check passed."
            Write-Host "See $stderrLog for details."
            "[$(Get-Date -Format o)] ERROR process $($proc.Id) exited early" | Add-Content -Path $bootLog -Encoding UTF8
            exit 1
        }
        try {
            $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 15
            break
        } catch {
            $remaining = [math]::Max(0, [int]($deadline - (Get-Date)).TotalSeconds)
            if ($remaining -le 0) { break }
            Start-Sleep -Seconds ([math]::Min($pollSec, $remaining))
        }
    }

    if ($health) {
        Write-Host "OK  Service running (PID $($proc.Id))"
        Write-Host "    Web UI: http://127.0.0.1:$Port/"
        Write-Host "    Devices: $($health.active_devices)"
        Write-Host "    SILworX open: $($health.silworx.silworx_open)"
        "[$(Get-Date -Format o)] OK pid=$($proc.Id) devices=$($health.active_devices)" | Add-Content -Path $bootLog -Encoding UTF8
    } elseif (Get-Process -Id $proc.Id -ErrorAction SilentlyContinue) {
        Write-Warning "Service started (PID $($proc.Id)) but health check not ready within ${healthWaitSec}s."
        Write-Host "Startup can take ~90-120s. Open http://127.0.0.1:$Port/ shortly or check $stderrLog"
        "[$(Get-Date -Format o)] WARN pid=$($proc.Id) health not ready in ${healthWaitSec}s" | Add-Content -Path $bootLog -Encoding UTF8
    }

    Write-Host "Stop with: .\stop_service.ps1"

    $AutoStart = $false
    if (Test-Path $Ini) {
        $as = Select-String -Path $Ini -Pattern '^\s*auto_start\s*=\s*(\w+)' | Select-Object -First 1
        if ($as -and $as.Matches[0].Groups[1].Value -match '^(?i:true|1|yes)$') { $AutoStart = $true }
    }
    if ($AutoStart) {
        Write-Host "Syncing Windows auto-start task (auto_start=true)..."
        & "$Root\Annex codes\Stop service\annex_windows_auto_start.ps1" -Sync
    }
    exit 0
} catch {
    "[$(Get-Date -Format o)] ERROR $($_.Exception.Message)" | Add-Content -Path $bootLog -Encoding UTF8
    if ($_.ScriptStackTrace) {
        $_.ScriptStackTrace -split "`n" | ForEach-Object { "[$(Get-Date -Format o)]   $_" | Add-Content -Path $bootLog -Encoding UTF8 }
    }
    throw
}
