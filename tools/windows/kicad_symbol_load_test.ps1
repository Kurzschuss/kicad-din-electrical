param(
    [string]$RepoPath,
    [switch]$NoOpen
)

$ErrorActionPreference = "Stop"

function Invoke-KiCad {
    param(
        [Parameter(Mandatory=$true)][string]$Exe,
        [Parameter(Mandatory=$true)][string[]]$Arguments,
        [string]$CaptureFile
    )

    Write-Host (">> `"{0}`" {1}" -f $Exe, ($Arguments -join " ")) -ForegroundColor Cyan

    if ($CaptureFile) {
        & $Exe @Arguments 2>&1 | Tee-Object -FilePath $CaptureFile
    }
    else {
        & $Exe @Arguments
    }

    if ($LASTEXITCODE -ne 0) {
        throw "KiCad-Befehl fehlgeschlagen (Exit $LASTEXITCODE): $Exe $($Arguments -join ' ')"
    }
}

function Find-KiCadCli {
    $command = Get-Command "kicad-cli.exe" -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @()
    foreach ($root in @($env:ProgramFiles, ${env:ProgramFiles(x86)})) {
        if (-not $root) { continue }
        $base = Join-Path $root "KiCad"
        if (-not (Test-Path $base)) { continue }
        $candidates += Get-ChildItem -Path $base -Filter "kicad-cli.exe" -File -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match "\\bin\\kicad-cli\.exe$" }
    }

    if (-not $candidates) {
        throw "kicad-cli.exe wurde nicht gefunden. KiCad 9 oder neuer installieren bzw. kicad-cli in PATH aufnehmen."
    }

    return ($candidates | Sort-Object FullName -Descending | Select-Object -First 1).FullName
}

function Count-SvgFiles {
    param([Parameter(Mandatory=$true)][string]$Directory)
    if (-not (Test-Path $Directory)) { return 0 }
    return @(Get-ChildItem -Path $Directory -Filter "*.svg" -File).Count
}

function Assert-Count {
    param(
        [Parameter(Mandatory=$true)][string]$Label,
        [Parameter(Mandatory=$true)][int]$Actual,
        [Parameter(Mandatory=$true)][int]$Expected
    )

    if ($Actual -ne $Expected) {
        throw "${Label}: erwartet $Expected SVG-Datei(en), gefunden $Actual."
    }
    Write-Host "${Label}: $Actual/$Expected OK" -ForegroundColor Green
}

if (-not $RepoPath) {
    $RepoPath = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}
else {
    $RepoPath = (Resolve-Path $RepoPath).Path
}

if (-not (Test-Path (Join-Path $RepoPath ".git"))) {
    throw "Kein Git-Repository: $RepoPath"
}

$RcboLibrary = Join-Path $RepoPath "symbols\Z_RCBO_1P_N.kicad_sym"
$ZiLibrary = Join-Path $RepoPath "symbols\Z_I_ElectricalComponents.kicad_sym"

foreach ($library in @($RcboLibrary, $ZiLibrary)) {
    if (-not (Test-Path $library)) {
        throw "Bibliothek fehlt: $library"
    }
}

$KiCadCli = Find-KiCadCli
$OutputRoot = Join-Path $RepoPath "build\kicad-symbol-load-test"
$RcboSvgDir = Join-Path $OutputRoot "rcbo-svg"
$ZiSvgDir = Join-Path $OutputRoot "zi-svg"
$RcboResaved = Join-Path $OutputRoot "Z_RCBO_1P_N.resaved.kicad_sym"
$ZiResaved = Join-Path $OutputRoot "Z_I_ElectricalComponents.resaved.kicad_sym"
$RcboResavedSvgDir = Join-Path $OutputRoot "rcbo-resaved-svg"
$ZiResavedSvgDir = Join-Path $OutputRoot "zi-resaved-svg"
$VersionFile = Join-Path $OutputRoot "KICAD_VERSION.txt"
$ReportFile = Join-Path $OutputRoot "RESULT.txt"
$GalleryFile = Join-Path $OutputRoot "VISUAL_CHECK.html"

if (Test-Path $OutputRoot) {
    Remove-Item -Path $OutputRoot -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $OutputRoot, $RcboSvgDir, $ZiSvgDir, $RcboResavedSvgDir, $ZiResavedSvgDir | Out-Null

Write-Host "" 
Write-Host "KiCad lokaler Symbol-Ladetest" -ForegroundColor Green
Write-Host "============================="
Write-Host "Repository: $RepoPath"
Write-Host "kicad-cli:  $KiCadCli"
Write-Host ""

Invoke-KiCad -Exe $KiCadCli -Arguments @("version", "--format", "about") -CaptureFile $VersionFile

# 1) Originalbibliotheken direkt mit dem echten KiCad-Parser laden und als SVG rendern.
Invoke-KiCad -Exe $KiCadCli -Arguments @(
    "sym", "export", "svg",
    "--black-and-white",
    "--include-hidden-pins",
    "--include-hidden-fields",
    "--output", $RcboSvgDir,
    $RcboLibrary
)

Invoke-KiCad -Exe $KiCadCli -Arguments @(
    "sym", "export", "svg",
    "--black-and-white",
    "--include-hidden-pins",
    "--include-hidden-fields",
    "--output", $ZiSvgDir,
    $ZiLibrary
)

$RcboCount = Count-SvgFiles $RcboSvgDir
$ZiCount = Count-SvgFiles $ZiSvgDir
Assert-Count -Label "RCBO Originalexport" -Actual $RcboCount -Expected 1
Assert-Count -Label "Z_I Originalexport" -Actual $ZiCount -Expected 52

# 2) Nicht-destruktiver Parser/Serializer-Test: Kopie durch KiCad neu speichern lassen.
Invoke-KiCad -Exe $KiCadCli -Arguments @(
    "sym", "upgrade", "--force", "--output", $RcboResaved, $RcboLibrary
)
Invoke-KiCad -Exe $KiCadCli -Arguments @(
    "sym", "upgrade", "--force", "--output", $ZiResaved, $ZiLibrary
)

if ((Get-Item $RcboResaved).Length -le 0) { throw "RCBO-Re-Save ist leer." }
if ((Get-Item $ZiResaved).Length -le 0) { throw "Z_I-Re-Save ist leer." }

# 3) Auch die von KiCad neu gespeicherten Kopien erneut laden/rendern.
Invoke-KiCad -Exe $KiCadCli -Arguments @(
    "sym", "export", "svg",
    "--black-and-white",
    "--include-hidden-pins",
    "--include-hidden-fields",
    "--output", $RcboResavedSvgDir,
    $RcboResaved
)
Invoke-KiCad -Exe $KiCadCli -Arguments @(
    "sym", "export", "svg",
    "--black-and-white",
    "--include-hidden-pins",
    "--include-hidden-fields",
    "--output", $ZiResavedSvgDir,
    $ZiResaved
)

$RcboResavedCount = Count-SvgFiles $RcboResavedSvgDir
$ZiResavedCount = Count-SvgFiles $ZiResavedSvgDir
Assert-Count -Label "RCBO Re-Save-Export" -Actual $RcboResavedCount -Expected 1
Assert-Count -Label "Z_I Re-Save-Export" -Actual $ZiResavedCount -Expected 52

# 4) Strukturelle Kontrolle des vierteiligen Schuetzes in der Z_I-Quelle.
$ZiText = Get-Content -Raw -Encoding UTF8 $ZiLibrary
$ContactorUnits = @(
    "Contactor_3P_1NO_1NC_1_1",
    "Contactor_3P_1NO_1NC_2_1",
    "Contactor_3P_1NO_1NC_3_1",
    "Contactor_3P_1NO_1NC_4_1"
)
foreach ($unitName in $ContactorUnits) {
    if ($ZiText -notmatch [regex]::Escape('(symbol "' + $unitName + '"')) {
        throw "Mehrfacheinheiten-Schuetz: Unit fehlt: $unitName"
    }
}
Write-Host "Contactor_3P_1NO_1NC: 4/4 Units strukturell vorhanden" -ForegroundColor Green

# 5) Visuelle Galerie aus den durch KiCad selbst gerenderten SVGs.
$cards = New-Object System.Collections.Generic.List[string]

$rcboFile = Get-ChildItem -Path $RcboSvgDir -Filter "*.svg" -File | Select-Object -First 1
if ($rcboFile) {
    $relative = "rcbo-svg/$($rcboFile.Name)"
    $cards.Add("<section class='important'><h2>RCBO / FI-LS</h2><img src='$relative' alt='RCBO'><p>Manuell pruefen: 1 / 3 N / 2 / 4 N, T/E-Testkreis, Summenstromwandler, rechter Betaetigungsblock, Verbindung zu 4/N.</p></section>")
}

$ziFiles = Get-ChildItem -Path $ZiSvgDir -Filter "*.svg" -File | Sort-Object Name
$ziCards = foreach ($file in $ziFiles) {
    $title = [System.Net.WebUtility]::HtmlEncode($file.BaseName)
    $src = "zi-svg/$($file.Name)"
    "<article><h3>$title</h3><img src='$src' alt='$title'></article>"
}
$cards.Add("<section><h2>Z_I_ElectricalComponents - 52 KiCad-Renderings</h2><div class='grid'>$($ziCards -join "`n")</div></section>")

$html = @"
<!doctype html>
<html lang='de'>
<head>
<meta charset='utf-8'>
<title>KiCad Symbol-Ladetest</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;margin:24px;background:#f5f5f5;color:#111}
h1,h2{margin:0 0 14px}.important{background:#fff;border:2px solid #222;padding:18px;margin-bottom:24px}
.important img{display:block;max-width:760px;width:100%;height:auto;margin:12px auto}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
article{background:#fff;border:1px solid #bbb;padding:10px;min-height:220px}
article h3{font-size:14px;word-break:break-word;margin:0 0 8px}
article img{display:block;max-width:100%;height:180px;object-fit:contain;margin:auto}
.check{background:#fff;padding:16px;margin:20px 0;border-left:5px solid #333}
</style>
</head>
<body>
<h1>KiCad lokaler Symbol-Ladetest</h1>
<div class='check'>
<strong>Automatischer Teil: PASS</strong><br>
RCBO: 1/1 gerendert und nach Re-Save erneut 1/1.<br>
Z_I: 52/52 gerendert und nach Re-Save erneut 52/52.<br>
Contactor_3P_1NO_1NC: 4/4 Units in der Bibliothek vorhanden.
</div>
$($cards -join "`n")
<div class='check'>
<strong>Noch manuell in KiCad pruefen:</strong>
<ol>
<li>RCBO platzieren: Klemmen 1 / 3 N / 2 / 4 N und Fangpunkte.</li>
<li>Contactor_3P_1NO_1NC im Symbolwaehler: Units A-D einzeln anzeigen.</li>
<li>Potentiale und Pfeile: Anschlussfangpunkte pruefen.</li>
<li>Bei allen 52 Z_I-Symbolen auf abgeschnittene Texte, falsche Rotation und unplausible Pinpositionen achten.</li>
</ol>
</div>
</body>
</html>
"@
Set-Content -Path $GalleryFile -Value $html -Encoding UTF8

$versionSummary = (Get-Content $VersionFile | Select-Object -First 1)
$report = @"
KiCad lokaler Symbol-Ladetest: PASS
Zeit: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss K")
Repository: $RepoPath
KiCad: $versionSummary
kicad-cli: $KiCadCli

Automatische Pruefungen:
- RCBO Originalexport: $RcboCount/1
- Z_I Originalexport: $ZiCount/52
- RCBO Re-Save-Export: $RcboResavedCount/1
- Z_I Re-Save-Export: $ZiResavedCount/52
- Contactor_3P_1NO_1NC Units strukturell: 4/4

Ergebnis: PASS

Manuell offen:
- RCBO Fangpunkte / Beschriftung 1 / 3 N / 2 / 4 N
- Contactor Units A-D im KiCad-Symbolwaehler
- Potential-/Pfeil-Fangpunkte
- Gesamtgalerie auf Text-/Rotations-/Pinfehler

Galerie: $GalleryFile
"@
Set-Content -Path $ReportFile -Value $report -Encoding UTF8

Write-Host ""
Write-Host "AUTOMATISCHER KICAD-LADETEST: PASS" -ForegroundColor Green
Write-Host "Bericht: $ReportFile"
Write-Host "Galerie: $GalleryFile"
Write-Host ""
Write-Host "Jetzt bitte die Galerie und anschliessend die vier manuellen KiCad-Punkte pruefen." -ForegroundColor Yellow

if (-not $NoOpen) {
    Start-Process $GalleryFile
}
