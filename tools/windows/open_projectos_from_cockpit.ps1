param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Uri
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-QueryValue([System.Uri]$ParsedUri, [string]$Name) {
    $query = $ParsedUri.Query.TrimStart('?')
    if (-not $query) { return $null }
    foreach ($part in $query.Split('&')) {
        if (-not $part) { continue }
        $pair = $part.Split('=', 2)
        $key = [System.Uri]::UnescapeDataString($pair[0])
        if ($key -ne $Name) { continue }
        if ($pair.Count -lt 2) { return '' }
        return [System.Uri]::UnescapeDataString($pair[1].Replace('+', ' '))
    }
    return $null
}

function Assert-ProjectName([string]$Value) {
    $name = if ($null -eq $Value) { '' } else { $Value.Trim() }
    if (-not $name) { throw 'Projektname darf nicht leer sein.' }
    if ($name.Length -gt 80) { throw 'Projektname darf höchstens 80 Zeichen enthalten.' }
    $hasControlCharacter = @($name.ToCharArray() | Where-Object { [int]$_ -lt 32 }).Count -gt 0
    if ($name -match '[\\/:*?"<>|]' -or $hasControlCharacter) {
        throw 'Projektname enthält unzulässige Dateinamenzeichen.'
    }
    return $name
}

function Find-Python([string]$RepositoryRoot) {
    $venv = Join-Path $RepositoryRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venv -PathType Leaf) {
        return (Resolve-Path -LiteralPath $venv).Path
    }
    $command = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    throw 'Python wurde nicht gefunden. Starte zuerst run_tests.bat.'
}

$parsed = [System.Uri]$Uri
if ($parsed.Scheme -ne 'projectos-z') {
    throw 'Nur das lokale projectos-z-Protokoll ist zulässig.'
}
if ($parsed.Host.ToLowerInvariant() -ne 'new') {
    throw 'Unbekannte projectos-z-Aktion.'
}

$name = Assert-ProjectName (Get-QueryValue $parsed 'name')
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$python = Find-Python $repositoryRoot

Add-Type -AssemblyName System.Windows.Forms
$dialog = New-Object System.Windows.Forms.SaveFileDialog
$dialog.Title = 'Neues ProjectOS-Projekt speichern'
$dialog.Filter = 'ProjectOS-Projekt (*.projectos.json)|*.projectos.json|JSON-Datei (*.json)|*.json'
$dialog.FileName = "$name.projectos.json"
$dialog.InitialDirectory = [Environment]::GetFolderPath('MyDocuments')
$dialog.OverwritePrompt = $true
$dialog.CheckPathExists = $true
$dialog.RestoreDirectory = $true

if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
    Write-Output 'PROJECTOS_Z_RESULT=CANCELLED'
    exit 0
}

$target = $dialog.FileName
& $python -m tools.projectos_project_cli new --name $name --output $target --overwrite
if ($LASTEXITCODE -ne 0) {
    throw "ProjectOS-Projekt konnte nicht erzeugt werden: $target"
}

& $python -m tools.generate_z_cockpit --project-bundle $target
if ($LASTEXITCODE -ne 0) {
    throw 'Z_Cockpit konnte nach dem Erzeugen des Projekts nicht aktualisiert werden.'
}

$cockpit = Join-Path $repositoryRoot 'docs\site\z-cockpit.html'
if (-not (Test-Path -LiteralPath $cockpit -PathType Leaf)) {
    throw "Z_Cockpit-Datei fehlt: $cockpit"
}
Start-Process -FilePath $cockpit | Out-Null
Write-Output ("PROJECTOS_Z_RESULT=CREATED:{0}" -f $target)
