# Sync branding images from Report Solution asset folder into the web GUI static/img folder.
$ErrorActionPreference = "Stop"
$src = "Z:\Project\Report Solution\7- Images for the graphical interface"
$dst = Join-Path $PSScriptRoot "Graphic Interface\static\img"
New-Item -ItemType Directory -Force -Path $dst | Out-Null

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
    if (Test-Path $from) {
        Copy-Item $from (Join-Path $dst $entry.Value) -Force
        Write-Host "OK  $($entry.Value)"
    } else {
        Write-Warning "Missing source: $($entry.Key)"
    }
}

$draeger = Get-ChildItem $src -Filter "*ger*" -File | Where-Object { $_.Name -like "*Logo*" } | Select-Object -First 1
if ($draeger) {
    Copy-Item $draeger.FullName (Join-Path $dst "draeger.png") -Force
    Write-Host "OK  draeger.png"
}

$himaSrc = Join-Path $src "himalogo.jpg"
$himaJpg = Join-Path $dst "himalogo.jpg"
$himaPng = Join-Path $dst "himalogo.png"
if (Test-Path $himaSrc) {
    Copy-Item $himaSrc $himaJpg -Force
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
