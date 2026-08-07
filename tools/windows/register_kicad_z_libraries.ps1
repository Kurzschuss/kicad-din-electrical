param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot,

    [Parameter(Mandatory = $true)]
    [string]$UserRoot
)

$ErrorActionPreference = 'Stop'

function Escape-SexprString([string]$Value) {
    return $Value.Replace('\', '/').Replace('"', '\"')
}

function Ensure-LibraryTable {
    param(
        [Parameter(Mandatory = $true)][string]$TablePath,
        [Parameter(Mandatory = $true)][string]$RootName,
        [Parameter(Mandatory = $true)][array]$Libraries
    )

    $added = [System.Collections.Generic.List[string]]::new()
    $existing = [System.Collections.Generic.List[string]]::new()
    $mismatch = [System.Collections.Generic.List[string]]::new()

    if (Test-Path -LiteralPath $TablePath) {
        $content = Get-Content -LiteralPath $TablePath -Raw -Encoding UTF8
    }
    else {
        $content = "($RootName`n)`n"
    }

    foreach ($library in $Libraries) {
        $namePattern = '\(name\s+"' + [regex]::Escape($library.Name) + '"\)'
        if ($content -match $namePattern) {
            $uriPattern = '\(uri\s+"' + [regex]::Escape((Escape-SexprString $library.Uri)) + '"\)'
            if ($content -match $uriPattern) { $existing.Add($library.Name) }
            else { $mismatch.Add($library.Name) }
            continue
        }

        $row = "  (lib (name `"$($library.Name)`")(type `"KiCad`")(uri `"$(Escape-SexprString $library.Uri)`")(options `"`")(descr `"Z_-Bibliothek, automatisch registriert`"))`n"
        $lastClose = $content.LastIndexOf(')')
        if ($lastClose -lt 0) { throw "Ungültige KiCad-Bibliothekstabelle: $TablePath" }
        $content = $content.Insert($lastClose, $row)
        $added.Add($library.Name)
    }

    if ($added.Count -gt 0) {
        $parent = Split-Path -Parent $TablePath
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
        if (Test-Path -LiteralPath $TablePath) {
            Copy-Item -LiteralPath $TablePath -Destination "$TablePath.z-backup" -Force
        }
        [System.IO.File]::WriteAllText($TablePath, $content, [System.Text.UTF8Encoding]::new($false))
    }

    return [pscustomobject]@{ Added = $added; Existing = $existing; Mismatch = $mismatch }
}

$symbolSource = Join-Path $RepositoryRoot 'symbols'
$footprintSource = Join-Path $RepositoryRoot 'footprints'
$designBlockSource = Join-Path $RepositoryRoot 'designblocks'
$modelSource = Join-Path $RepositoryRoot 'models'

$symbolTarget = Join-Path $UserRoot 'symbols'
$footprintTarget = Join-Path $UserRoot 'footprints'
$designBlockTarget = Join-Path $UserRoot 'designblocks'
$modelTarget = Join-Path $UserRoot '3dmodels\Z_3DModell.3dshapes'

foreach ($directory in @($symbolTarget, $footprintTarget, $designBlockTarget, $modelTarget)) {
    New-Item -ItemType Directory -Path $directory -Force | Out-Null
}

$symbolLibraries = @()
if (Test-Path -LiteralPath $symbolSource) {
    Get-ChildItem -LiteralPath $symbolSource -File -Filter 'Z_*.kicad_sym' | Sort-Object Name | ForEach-Object {
        $target = Join-Path $symbolTarget $_.Name
        Copy-Item -LiteralPath $_.FullName -Destination $target -Force
        $symbolLibraries += [pscustomobject]@{ Name = $_.BaseName; Uri = '${KICAD_Z_SYMBOL_DIR}/' + $_.Name }
    }
}

$footprintLibraries = @()
if (Test-Path -LiteralPath $footprintSource) {
    Get-ChildItem -LiteralPath $footprintSource -Directory -Filter 'Z_*.pretty' | Sort-Object Name | ForEach-Object {
        $target = Join-Path $footprintTarget $_.Name
        Copy-Item -LiteralPath $_.FullName -Destination $target -Recurse -Force
        $footprintLibraries += [pscustomobject]@{ Name = $_.BaseName; Uri = '${KICAD_Z_FOOTPRINT_DIR}/' + $_.Name }
    }
}

$designBlockLibraries = @()
if (Test-Path -LiteralPath $designBlockSource) {
    Get-ChildItem -LiteralPath $designBlockSource -Directory -Filter 'Z_*.kicad_blocks' | Sort-Object Name | ForEach-Object {
        $target = Join-Path $designBlockTarget $_.Name
        Copy-Item -LiteralPath $_.FullName -Destination $target -Recurse -Force
        $designBlockLibraries += [pscustomobject]@{ Name = $_.BaseName; Uri = '${KICAD_Z_DESIGN_BLOCK_DIR}/' + $_.Name }
    }
}

# ProjectOS-3D-Artefakte werden aus dem Repository in die produktive KiCad-Laufzeit gespiegelt.
# Die relative Struktur unter models/ bleibt erhalten, damit Footprints portable Pfade verwenden können.
$modelFiles = @()
if (Test-Path -LiteralPath $modelSource) {
    $modelFiles = Get-ChildItem -LiteralPath $modelSource -File -Recurse |
        Where-Object { $_.Extension.ToLowerInvariant() -in @('.step', '.stp', '.wrl') }
    foreach ($model in $modelFiles) {
        $relative = $model.FullName.Substring($modelSource.Length).TrimStart('\', '/')
        $target = Join-Path $modelTarget $relative
        New-Item -ItemType Directory -Path (Split-Path -Parent $target) -Force | Out-Null
        Copy-Item -LiteralPath $model.FullName -Destination $target -Force
    }
}

$configRoot = Join-Path $env:APPDATA 'kicad'
$configDirectories = @()
if (Test-Path -LiteralPath $configRoot) {
    $configDirectories = Get-ChildItem -LiteralPath $configRoot -Directory -ErrorAction SilentlyContinue
}

$totalAdded = 0
$totalExisting = 0
$totalMismatch = 0

foreach ($configDirectory in $configDirectories) {
    $results = @(
        Ensure-LibraryTable -TablePath (Join-Path $configDirectory.FullName 'sym-lib-table') -RootName 'sym_lib_table' -Libraries $symbolLibraries
        Ensure-LibraryTable -TablePath (Join-Path $configDirectory.FullName 'fp-lib-table') -RootName 'fp_lib_table' -Libraries $footprintLibraries
        Ensure-LibraryTable -TablePath (Join-Path $configDirectory.FullName 'design-block-lib-table') -RootName 'design_block_lib_table' -Libraries $designBlockLibraries
    )
    foreach ($result in $results) {
        $totalAdded += $result.Added.Count
        $totalExisting += $result.Existing.Count
        $totalMismatch += $result.Mismatch.Count
    }
}

if ($configDirectories.Count -eq 0) { Write-Output 'KICAD_Z_LIBRARY_REGISTRATION=NO_CONFIG' }
else { Write-Output 'KICAD_Z_LIBRARY_REGISTRATION=OK' }
Write-Output "KICAD_Z_LIBRARY_ADDED=$totalAdded"
Write-Output "KICAD_Z_LIBRARY_EXISTING=$totalExisting"
Write-Output "KICAD_Z_LIBRARY_MISMATCH=$totalMismatch"
Write-Output "KICAD_Z_SYMBOL_LIBRARIES=$($symbolLibraries.Count)"
Write-Output "KICAD_Z_FOOTPRINT_LIBRARIES=$($footprintLibraries.Count)"
Write-Output "KICAD_Z_DESIGN_BLOCK_LIBRARIES=$($designBlockLibraries.Count)"
Write-Output "KICAD_Z_3DMODEL_FILES=$($modelFiles.Count)"
Write-Output "KICAD_Z_REQUIRED_ENTRIES=$($symbolLibraries.Count + $footprintLibraries.Count + $designBlockLibraries.Count + 11)"
