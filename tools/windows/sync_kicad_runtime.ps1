param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,

    [string]$UserRoot = '',

    [ValidateSet('Preview', 'Interactive')]
    [string]$Mode = 'Interactive'
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($UserRoot)) {
    $documents = [Environment]::GetFolderPath('MyDocuments')
    if ([string]::IsNullOrWhiteSpace($documents)) {
        $documents = Join-Path $env:USERPROFILE 'Documents'
    }
    $UserRoot = Join-Path $documents 'kicad'
}

$RepositoryRoot = [System.IO.Path]::GetFullPath($RepositoryRoot)
$UserRoot = [System.IO.Path]::GetFullPath($UserRoot)

function Get-FileHashSafe([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
}

function Add-Comparison {
    param(
        [System.Collections.Generic.List[object]]$Changes,
        [string]$Category,
        [string]$Source,
        [string]$Target,
        [string]$DisplayPath
    )

    if (-not (Test-Path -LiteralPath $Target -PathType Leaf)) {
        $Changes.Add([pscustomobject]@{ Status='NEU'; Category=$Category; Source=$Source; Target=$Target; Path=$DisplayPath })
        return
    }

    $sourceHash = Get-FileHashSafe $Source
    $targetHash = Get-FileHashSafe $Target
    if ($sourceHash -ne $targetHash) {
        $Changes.Add([pscustomobject]@{ Status='AKTUALISIEREN'; Category=$Category; Source=$Source; Target=$Target; Path=$DisplayPath })
    }
}

$changes = [System.Collections.Generic.List[object]]::new()

# Symbole
$symbolSource = Join-Path $RepositoryRoot 'symbols'
$symbolTarget = Join-Path $UserRoot 'symbols'
if (Test-Path -LiteralPath $symbolSource) {
    Get-ChildItem -LiteralPath $symbolSource -File -Filter 'Z_*.kicad_sym' | Sort-Object Name | ForEach-Object {
        Add-Comparison -Changes $changes -Category 'Symbol' -Source $_.FullName -Target (Join-Path $symbolTarget $_.Name) -DisplayPath ("symbols\" + $_.Name)
    }
}

# Footprints: jede Datei der freigegebenen Z_*.pretty-Bibliotheken vergleichen.
$footprintSource = Join-Path $RepositoryRoot 'footprints'
$footprintTarget = Join-Path $UserRoot 'footprints'
if (Test-Path -LiteralPath $footprintSource) {
    Get-ChildItem -LiteralPath $footprintSource -Directory -Filter 'Z_*.pretty' | Sort-Object Name | ForEach-Object {
        $library = $_
        $targetLibrary = Join-Path $footprintTarget $library.Name
        Get-ChildItem -LiteralPath $library.FullName -File -Recurse | Sort-Object FullName | ForEach-Object {
            $relative = $_.FullName.Substring($library.FullName.Length).TrimStart('\','/')
            $display = "footprints\$($library.Name)\$relative"
            Add-Comparison -Changes $changes -Category 'Footprint' -Source $_.FullName -Target (Join-Path $targetLibrary $relative) -DisplayPath $display
        }
        if (Test-Path -LiteralPath $targetLibrary) {
            Get-ChildItem -LiteralPath $targetLibrary -File -Recurse | ForEach-Object {
                $relative = $_.FullName.Substring($targetLibrary.Length).TrimStart('\','/')
                $sourcePeer = Join-Path $library.FullName $relative
                if (-not (Test-Path -LiteralPath $sourcePeer -PathType Leaf)) {
                    $changes.Add([pscustomobject]@{ Status='ENTFERNEN'; Category='Footprint'; Source=''; Target=$_.FullName; Path=("footprints\$($library.Name)\$relative") })
                }
            }
        }
    }
}

# 3D-Artefakte
$modelSource = Join-Path $RepositoryRoot 'models'
$modelTarget = Join-Path $UserRoot '3dmodels\Z_3DModell.3dshapes'
if (Test-Path -LiteralPath $modelSource) {
    Get-ChildItem -LiteralPath $modelSource -File -Recurse | Where-Object {
        $_.Extension.ToLowerInvariant() -in @('.step', '.stp', '.wrl')
    } | Sort-Object FullName | ForEach-Object {
        $relative = $_.FullName.Substring($modelSource.Length).TrimStart('\','/')
        Add-Comparison -Changes $changes -Category '3D' -Source $_.FullName -Target (Join-Path $modelTarget $relative) -DisplayPath ("3dmodels\Z_3DModell.3dshapes\" + $relative)
    }
}

# Designblocks werden ebenfalls gespiegelt; im Bericht getrennt ausweisen.
$designSource = Join-Path $RepositoryRoot 'designblocks'
$designTarget = Join-Path $UserRoot 'designblocks'
if (Test-Path -LiteralPath $designSource) {
    Get-ChildItem -LiteralPath $designSource -Directory -Filter 'Z_*.kicad_blocks' | Sort-Object Name | ForEach-Object {
        $library = $_
        $targetLibrary = Join-Path $designTarget $library.Name
        Get-ChildItem -LiteralPath $library.FullName -File -Recurse | Sort-Object FullName | ForEach-Object {
            $relative = $_.FullName.Substring($library.FullName.Length).TrimStart('\','/')
            Add-Comparison -Changes $changes -Category 'Designblock' -Source $_.FullName -Target (Join-Path $targetLibrary $relative) -DisplayPath ("designblocks\$($library.Name)\$relative")
        }
    }
}

Write-Host ''
Write-Host '============================================================'
Write-Host '  KiCad-Laufzeitabgleich Repository -> Benutzerverzeichnis'
Write-Host '============================================================'
Write-Host ''
Write-Host "Repository : $RepositoryRoot"
Write-Host "KiCad-Ziel : $UserRoot"
Write-Host ''

if ($changes.Count -eq 0) {
    Write-Host '[OK] Symbole, Footprints und 3D-Modelle sind bereits aktuell.'
    Write-Host '     Es werden keine Dateien kopiert oder ersetzt.'
    exit 0
}

$groups = @('Symbol','Footprint','3D','Designblock')
foreach ($category in $groups) {
    $items = @($changes | Where-Object Category -eq $category)
    if ($items.Count -eq 0) { continue }
    Write-Host "$category`e[n]:"
    foreach ($item in $items) {
        Write-Host ("  [{0}] {1}" -f $item.Status, $item.Path)
    }
    Write-Host ''
}

$newCount = @($changes | Where-Object Status -eq 'NEU').Count
$updateCount = @($changes | Where-Object Status -eq 'AKTUALISIEREN').Count
$removeCount = @($changes | Where-Object Status -eq 'ENTFERNEN').Count
Write-Host ("Zusammenfassung: neu={0}, aktualisieren={1}, entfernen={2}" -f $newCount, $updateCount, $removeCount)
Write-Host ''

if ($Mode -eq 'Preview') { exit 0 }

$answer = Read-Host 'Diese Aenderungen jetzt in das KiCad-Benutzerverzeichnis uebernehmen? [J/N]'
if ($answer -notmatch '^[JjYy]$') {
    Write-Host ''
    Write-Host '[NICHT AUSGEFUEHRT] Die KiCad-Laufzeit wurde nicht veraendert.'
    exit 0
}

Write-Host ''
Write-Host 'Synchronisierung wird ausgefuehrt ...'
$registerScript = Join-Path $RepositoryRoot 'tools\windows\register_kicad_z_libraries.ps1'
& powershell -NoProfile -ExecutionPolicy Bypass -File $registerScript -RepositoryRoot $RepositoryRoot -UserRoot $UserRoot | ForEach-Object {
    if ($_ -match '^KICAD_Z_') { Write-Host "  $_" }
}
if ($LASTEXITCODE -ne 0) {
    throw "KiCad-Synchronisierung fehlgeschlagen (Exitcode $LASTEXITCODE)."
}

Write-Host ''
Write-Host '[FERTIG] KiCad-Benutzerverzeichnis wurde aktualisiert.'
exit 0
