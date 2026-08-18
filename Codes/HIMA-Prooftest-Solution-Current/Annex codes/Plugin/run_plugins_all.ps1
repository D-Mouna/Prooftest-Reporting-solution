# Start prooftest_session_plugin on all configured SILworX plugin ports (G-21 / Gate 8).
# Reads api_port_start, api_port_count, api_plugin_port_start from solution.ini.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$SolutionIni = Join-Path (Split-Path (Split-Path $Root -Parent) -Parent) "solution.ini"
$Py32 = "C:\Python 312_32bit\python.exe"
$TlsCert = "C:\ProgramData\SILworX_v16.0.0 R3326\settings\api_cert.pem"

if (-not (Test-Path $Py32)) { throw "32-bit Python not found at $Py32" }
if (-not (Test-Path $SolutionIni)) { throw "solution.ini not found at $SolutionIni" }

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

$ApiStart = [int](Get-IniValue "SILworX" "api_port_start" "51710")
$ApiCount = [int](Get-IniValue "SILworX" "api_port_count" "10")
$PluginStart = [int](Get-IniValue "SILworX" "api_plugin_port_start" "8400")
$CertFromIni = Get-IniValue "SILworX" "api_cert" ""
if ($CertFromIni -and (Test-Path $CertFromIni)) { $TlsCert = $CertFromIni }

Write-Host "Starting plugins for ports $PluginStart..$($PluginStart + $ApiCount - 1) (API $ApiStart..$($ApiStart + $ApiCount - 1))"
Write-Host "Requires SILworX settings.ini: [Plugin_Server] Development=prooftest_session_plugin (set manually per instance)"
Set-Location $Root

for ($i = 0; $i -lt $ApiCount; $i++) {
    $ApiPort = $ApiStart + $i
    $PluginPort = $PluginStart + $i
    Write-Host "  -> wss://127.0.0.1:$PluginPort (API $ApiPort)"
    Start-Process -FilePath $Py32 `
        -ArgumentList @(
            "annex_plugin.py",
            "--plugin-port", "$PluginPort",
            "--api-port", "$ApiPort",
            "--api-address", "127.0.0.1",
            "--language", "en",
            "--silworx-version", "16.0.0",
            "--tls-certificate", $TlsCert
        ) `
        -WorkingDirectory $Root `
        -WindowStyle Hidden
    Start-Sleep -Milliseconds 300
}

Write-Host "Done. Use run_plugin.ps1 for a single preferred instance only."
