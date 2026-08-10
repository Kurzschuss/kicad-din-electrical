param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$Uri
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-QueryValue([System.Uri]$ParsedUri, [string]$Name) {
    $query = $ParsedUri.Query.TrimStart('?')
    if (-not $query) {
        return $null
    }

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

function Assert-SafeIdentifier([string]$Value, [string]$Label) {
    if (-not $Value -or $Value -notmatch '^[A-Za-z0-9_.+-]+$') {
        throw "Ungültige $Label-ID."
    }
}

function Find-KiCadExecutable {
    $candidates = [System.Collections.Generic.List[string]]::new()

    foreach ($name in @('kicad.exe', 'kicad-cli.exe')) {
        try {
            $found = & where.exe $name 2>$null
            foreach ($item in $found) {
                if (-not $item) { continue }
                if ($name -eq 'kicad-cli.exe') {
                    $item = Join-Path (Split-Path -Parent $item) 'kicad.exe'
                }
                if (-not $candidates.Contains($item)) {
                    $candidates.Add($item)
                }
            }
        }
        catch {
            # PATH-Treffer sind optional; anschließend werden Standardpfade geprüft.
        }
    }

    $programRoots = @($env:ProgramFiles)
    if (${env:ProgramFiles(x86)}) {
        $programRoots += ${env:ProgramFiles(x86)}
    }
    foreach ($root in $programRoots) {
        if (-not $root) { continue }
        $kicadRoot = Join-Path $root 'KiCad'
        if (-not (Test-Path -LiteralPath $kicadRoot -PathType Container)) { continue }
        foreach ($directory in (Get-ChildItem -LiteralPath $kicadRoot -Directory | Sort-Object Name -Descending)) {
            $candidate = Join-Path $directory.FullName 'bin\kicad.exe'
            if (-not $candidates.Contains($candidate)) {
                $candidates.Add($candidate)
            }
        }
    }

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    throw 'KiCad wurde nicht gefunden. Starte zuerst run_tests.bat oder prüfe die KiCad-Installation.'
}

function Open-SymbolEditor([string]$KiCadExe, [string]$Reference) {
    # KiCad stellt für den Symbol-Editor aktuell keinen stabilen CLI-Aufruf bereit,
    # der eine konkrete Bibliothek:Symbol-ID direkt selektiert. Die Referenz wird
    # deshalb für die Bibliothekssuche in die Zwischenablage gelegt und der vom
    # KiCad-Manager dokumentierte Symbol-Editor-Aufruf (Ctrl+L) ausgelöst.
    Set-Clipboard -Value $Reference
    $process = Start-Process -FilePath $KiCadExe -PassThru
    $shell = New-Object -ComObject WScript.Shell
    $activated = $false

    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        Start-Sleep -Milliseconds 250
        try {
            if (-not $process.HasExited -and $shell.AppActivate($process.Id)) {
                $activated = $true
                break
            }
        }
        catch {
            break
        }
    }

    if (-not $activated) {
        $existing = Get-Process -Name 'kicad' -ErrorAction SilentlyContinue |
            Sort-Object StartTime -Descending |
            Select-Object -First 1
        if ($existing) {
            $activated = $shell.AppActivate($existing.Id)
        }
    }

    if (-not $activated) {
        throw 'KiCad-Manager konnte nicht für den Symbol-Editor aktiviert werden.'
    }

    Start-Sleep -Milliseconds 300
    $shell.SendKeys('^l')
}

$parsed = [System.Uri]$Uri
if ($parsed.Scheme -ne 'kicad-z') {
    throw 'Nur das lokale kicad-z-Protokoll ist zulässig.'
}

$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$kiCadExe = Find-KiCadExecutable
$action = $parsed.Host.ToLowerInvariant()

switch ($action) {
    'footprint' {
        $name = Get-QueryValue $parsed 'name'
        Assert-SafeIdentifier $name 'Footprint'
        $footprintFile = Join-Path $repositoryRoot ("footprints\{0}.pretty\{0}.kicad_mod" -f $name)
        if (-not (Test-Path -LiteralPath $footprintFile -PathType Leaf)) {
            throw "Repository-Footprint nicht gefunden: $name"
        }
        Start-Process -FilePath $kiCadExe -ArgumentList @('-f', 'fpedit', ('"{0}"' -f $footprintFile)) | Out-Null
        Write-Output ("KICAD_Z_OPENED=footprint:{0}" -f $name)
    }
    'symbol' {
        $reference = Get-QueryValue $parsed 'reference'
        if (-not $reference) {
            throw 'Symbolreferenz fehlt.'
        }
        $parts = $reference.Split(':')
        if ($parts.Count -ne 2) {
            throw 'Symbolreferenz muss Bibliothek:Symbol entsprechen.'
        }
        Assert-SafeIdentifier $parts[0] 'Symbolbibliothek'
        Assert-SafeIdentifier $parts[1] 'Symbol'
        $libraryFile = Join-Path $repositoryRoot ("symbols\{0}.kicad_sym" -f $parts[0])
        if (-not (Test-Path -LiteralPath $libraryFile -PathType Leaf)) {
            throw "Repository-Symbolbibliothek nicht gefunden: $($parts[0])"
        }
        $needle = '  (symbol "{0}"' -f $parts[1]
        if (-not (Select-String -LiteralPath $libraryFile -SimpleMatch $needle -Quiet)) {
            throw "Repository-Symbol nicht gefunden: $reference"
        }
        Open-SymbolEditor $kiCadExe $reference
        Write-Output ("KICAD_Z_OPENED=symbol:{0}" -f $reference)
    }
    default {
        throw 'Unbekannte kicad-z-Aktion.'
    }
}
