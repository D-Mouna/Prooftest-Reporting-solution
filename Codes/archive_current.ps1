# Archive HIMA-Prooftest-Solution-Current before code changes (Codes versioning policy)
param(
    [string]$Reason = ""
)

$ErrorActionPreference = "Stop"
$CodesRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Current = Join-Path $CodesRoot "HIMA-Prooftest-Solution-Current"
$ArchiveRoot = Join-Path $CodesRoot "Archive"
$IndexPath = Join-Path $ArchiveRoot "ARCHIVE_INDEX.json"

if (-not (Test-Path $Current)) {
    throw "Active folder not found: $Current"
}

if (-not (Test-Path $ArchiveRoot)) {
    New-Item -ItemType Directory -Path $ArchiveRoot -Force | Out-Null
}

if (-not (Test-Path $IndexPath)) {
    @{
        policy = "Archive HIMA-Prooftest-Solution-Current before every code change."
        next_archive_version = "1.32"
        archives = @()
    } | ConvertTo-Json -Depth 5 | Set-Content -Path $IndexPath -Encoding UTF8
}

$index = Get-Content $IndexPath -Raw | ConvertFrom-Json
$version = [string]$index.next_archive_version
$dest = Join-Path $ArchiveRoot "HIMA-Prooftest-Solution-v$version"

if (Test-Path $dest) {
    throw "Archive already exists: $dest"
}

Write-Host "Archiving Current -> $dest"
robocopy $Current $dest /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
if (-not (Test-Path (Join-Path $dest "main.py"))) {
    throw "Archive copy failed - main.py missing in $dest"
}

$versionJsonPath = Join-Path $dest "VERSION.json"
$versionData = @{
    spec_id = "SPEC-001"
    spec_version = $version
    status = "archived"
    archived_at = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
    archive_version = $version
    description = if ($Reason) { $Reason } else { "Snapshot before code change" }
}
$versionData | ConvertTo-Json | Set-Content -Path $versionJsonPath -Encoding UTF8

$entry = [ordered]@{
    version = $version
    path = "Archive/HIMA-Prooftest-Solution-v$version"
    archived_at = $versionData.archived_at
    reason = $versionData.description
}
$index.archives += $entry

$parts = $version.Split(".")
$minor = [int]$parts[1] + 1
$index.next_archive_version = "$($parts[0]).$minor"
$index | ConvertTo-Json -Depth 5 | Set-Content -Path $IndexPath -Encoding UTF8

Write-Host "OK  Archived as v$version"
Write-Host "    Next archive version: $($index.next_archive_version)"
Write-Host "    Edit only: $Current"
