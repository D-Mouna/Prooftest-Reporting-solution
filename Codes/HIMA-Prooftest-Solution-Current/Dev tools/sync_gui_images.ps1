# DEV TOOL — sync GUI brand images (not used at runtime)
#
# Purpose:
#   Copy logos / hero images from the Report Solution asset folder
#   ("7- Images for the graphical interface") into
#   Graphic Interface\static\img\ for the web UI.
#
# When to run:
#   - After updating an existing brand logo in the asset folder
#   - Before shipping UI branding changes
#
# Not needed:
#   - For normal service start / reboot auto-start / report generation
#
# New brand:
#   1. Add the source file under "7- Images for the graphical interface"
#   2. Add a mapping in $map below (source name -> static/img name)
#   3. Reference the new image from the Graphic Interface HTML/CSS/JS
#
# Run from anywhere:
#   powershell -ExecutionPolicy Bypass -File ".\Dev tools\sync_gui_images.ps1"

$ErrorActionPreference = "Stop"
$SolutionRoot = Split-Path -Parent $PSScriptRoot
$dst = Join-Path $SolutionRoot "Graphic Interface\static\img"
New-Item -ItemType Directory -Force -Path $dst | Out-Null

$srcCandidates = @(
    (Join-Path (Split-Path -Parent (Split-Path -Parent $SolutionRoot)) "7- Images for the graphical interface"),
    "C:\Users\Administrator\Documents\Report Solution\7- Images for the graphical interface",
    "Z:\Project\Report Solution\7- Images for the graphical interface"
)
$src = $srcCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
if (-not $src) {
    throw "Asset folder not found. Tried:`n  $($srcCandidates -join "`n  ")"
}
Write-Host "Source: $src"
Write-Host "Destination: $dst"

$map = @{
    "ABB_logo.png" = "abb.png"
    "EMERSON Rosemount Logo.png" = "emerson.png"
    "Endress & Hauser logo.png" = "eh.png"
    "ehheartbeat.png" = "eh-sil.png"
    "Samson logo.png" = "samson.png"
    "WIKA_Logo.svg.png" = "wika.png"
    "SIL logo.png" = "sil.png"
    "HART-Communication-Protocol- Logo.jpg" = "hart.jpg"
    "Krohne Logo.png" = "krohne.png"
    "HIMA Automated Prooftest.jpg" = "hero-plant.jpg"
    "HIMA Automated Prooftest2 .jpg.png" = "ui-reference.png"
}

foreach ($entry in $map.GetEnumerator()) {
    $from = Join-Path $src $entry.Key
    if (Test-Path -LiteralPath $from) {
        Copy-Item -LiteralPath $from -Destination (Join-Path $dst $entry.Value) -Force
        Write-Host "OK  $($entry.Value)"
    } else {
        Write-Warning "Missing source: $($entry.Key)"
    }
}

$draeger = Get-ChildItem -LiteralPath $src -Filter "*ger*" -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "*Logo*" } |
    Select-Object -First 1
if ($draeger) {
    Copy-Item -LiteralPath $draeger.FullName -Destination (Join-Path $dst "draeger.png") -Force
    Write-Host "OK  draeger.png"
}

$himaSrc = Join-Path $src "himalogo.jpg"
$himaJpg = Join-Path $dst "himalogo.jpg"
$himaPng = Join-Path $dst "himalogo.png"
if (Test-Path -LiteralPath $himaSrc) {
    Copy-Item -LiteralPath $himaSrc -Destination $himaJpg -Force
    python -c @"
from PIL import Image
im = Image.open(r'$himaJpg').convert('RGBA')
w, h = im.size
px = im.load()

def white(rgb):
    return rgb[0] > 235 and rgb[1] > 235 and rgb[2] > 235

stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
seen = set()
while stack:
    x, y = stack.pop()
    if x < 0 or x >= w or y < 0 or y >= h or (x, y) in seen:
        continue
    r, g, b, a = px[x, y]
    if not white((r, g, b)):
        continue
    seen.add((x, y))
    px[x, y] = (r, g, b, 0)
    stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])
im.save(r'$himaPng')
"@
    Write-Host "OK  himalogo.jpg + himalogo.png (transparent border)"
} else {
    Write-Warning "Missing source: himalogo.jpg"
}

Write-Host "Done. Images in $dst"
