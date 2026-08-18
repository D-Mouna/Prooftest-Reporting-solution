# Register / remove Windows Task Scheduler auto-start for HIMA Prooftest (SPEC-001 v1.33)
param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Sync
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path))
$Ini = Join-Path $Root "solution.ini"
$TaskName = "HIMA-Prooftest-Service"
$RunScript = Join-Path $Root "run_service.ps1"

function Read-IniValue {
    param([string]$Section, [string]$Key, [string]$Default)
    if (-not (Test-Path $Ini)) { return $Default }
    $current = ""
    foreach ($line in Get-Content $Ini) {
        if ($line -match '^\s*\[(.+)\]\s*$') { $current = $Matches[1]; continue }
        if ($current -ne $Section) { continue }
        if ($line -match "^\s*$Key\s*=\s*(.+?)\s*$") { return $Matches[1].Trim() }
    }
    return $Default
}

function Test-TaskExists {
    $null -ne (Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue)
}

function Resolve-PathForScheduledTask {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $Path
    }
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if ($resolved -notmatch '^([A-Z]):\\(.*)$') {
        return $resolved
    }
    $drive = $Matches[1]
    $rest = $Matches[2]
    $netUse = (net use "${drive}:" 2>&1) | Out-String
    if ($netUse -match 'Remote name\s+(.+?)\s*(\r?\n|$)') {
        $uncRoot = $Matches[1].Trim()
        return (Join-Path $uncRoot $rest)
    }
    return $resolved
}

function Install-AutoStartTask {
    if (-not (Test-Path $RunScript)) {
        throw "run_service.ps1 not found: $RunScript"
    }

    $triggerMode = (Read-IniValue "Service" "auto_start_trigger" "logon").ToLowerInvariant()
    if ($triggerMode -notin @("logon", "startup")) {
        throw "auto_start_trigger must be 'logon' or 'startup' (got '$triggerMode')"
    }

    $delaySec = [int](Read-IniValue "Service" "auto_start_delay_sec" "90")
    if ($delaySec -lt 0) { $delaySec = 0 }
    if ($delaySec -gt 600) { $delaySec = 600 }

    $taskScript = if ($triggerMode -eq "logon") { (Resolve-Path -LiteralPath $RunScript).Path } else { Resolve-PathForScheduledTask $RunScript }
    $taskRoot = if ($triggerMode -eq "logon") { (Resolve-Path -LiteralPath $Root).Path } else { Resolve-PathForScheduledTask $Root }
    $psArgs = "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$taskScript`""
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $psArgs -WorkingDirectory $taskRoot

    if ($triggerMode -eq "startup") {
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        $triggerLabel = "At system startup"
    } else {
        $trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
        $principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
        $triggerLabel = "At logon ($env:USERDOMAIN\$env:USERNAME)"
    }
    if ($delaySec -gt 0) {
        $trigger.Delay = "PT${delaySec}S"
    }

    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 5)

    if (Test-TaskExists) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }

    $desc = "HIMA Automated Prooftest - auto-start (SPEC-001 v1.33, trigger=$triggerMode)"
    Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description $desc | Out-Null

    Write-Host "OK  Registered scheduled task '$TaskName' ($triggerLabel, delay ${delaySec}s)"
    Write-Host "    Action: $taskScript"
    Write-Host "    WorkingDirectory: $taskRoot"
}

function Remove-AutoStartTask {
    if (Test-TaskExists) {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "OK  Removed scheduled task '$TaskName'"
    } else {
        Write-Host "OK  Scheduled task '$TaskName' was not registered"
    }
}

function Sync-AutoStartTask {
    $enabled = (Read-IniValue "Service" "auto_start" "false").ToLowerInvariant()
    if ($enabled -in @("true", "1", "yes")) {
        Install-AutoStartTask
    } else {
        Remove-AutoStartTask
    }
}

if ($Install) {
    Install-AutoStartTask
} elseif ($Uninstall) {
    Remove-AutoStartTask
} elseif ($Sync) {
    Sync-AutoStartTask
} else {
    Write-Host "Usage: annex_windows_auto_start.ps1 -Install | -Uninstall | -Sync"
    Write-Host "  -Sync reads auto_start from solution.ini"
}
