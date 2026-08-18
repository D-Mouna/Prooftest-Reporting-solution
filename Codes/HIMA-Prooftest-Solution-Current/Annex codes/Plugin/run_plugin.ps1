# Start SILworX development plugin (session bridge for API Mode B)
# Ports are read from solution.ini — must match the SILworX instance with the open project.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$SolutionIni = Join-Path (Split-Path (Split-Path $Root -Parent) -Parent) "solution.ini"
$Py32 = "C:\Python 312_32bit\python.exe"
$TlsCert = "C:\ProgramData\SILworX_v16.0.0 R3326\settings\api_cert.pem"
if (-not (Test-Path $Py32)) {
    throw "32-bit Python not found at $Py32"
}
if (-not (Test-Path $SolutionIni)) {
    throw "solution.ini not found at $SolutionIni"
}

function Get-IniValue([string]$Section, [string]$Key, [string]$Default) {
    $inSection = $false
    foreach ($line in Get-Content $SolutionIni) {
        $trimmed = $line.Trim()
        if ($trimmed -match '^\[(.+)\]$') {
            $inSection = ($Matches[1] -eq $Section)
            continue
        }
        if ($inSection -and $trimmed -match "^$Key\s*=\s*(.+)$") {
            return $Matches[1].Trim()
        }
    }
    return $Default
}

$ApiPort = [int](Get-IniValue "SILworX" "api_port" "51711")
$PluginPort = [int](Get-IniValue "SILworX" "api_plugin_port" "8401")
$CertFromIni = Get-IniValue "SILworX" "api_cert" ""
if ($CertFromIni -and (Test-Path $CertFromIni)) {
    $TlsCert = $CertFromIni
}

Write-Host "Starting prooftest_session_plugin -> wss://127.0.0.1:$PluginPort (API $ApiPort)"
Write-Host "Requires SILworX settings.ini: [Plugin_Server] Development=prooftest_session_plugin (set manually)"
Set-Location $Root
& $Py32 annex_plugin.py `
    --plugin-port $PluginPort `
    --api-port $ApiPort `
    --api-address 127.0.0.1 `
    --language en `
    --silworx-version 16.0.0 `
    --tls-certificate $TlsCert
