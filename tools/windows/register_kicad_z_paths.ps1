param(
    [Parameter(Mandatory = $true)]
    [string]$RootDirectory
)

$ErrorActionPreference = 'Stop'

$managedVariables = [ordered]@{
    KICAD_Z_ROOT_DIR      = $RootDirectory
    KICAD_Z_3DMODEL_DIR   = Join-Path $RootDirectory '3dmodels'
    KICAD_Z_3RDPARTY_DIR  = Join-Path $RootDirectory '3rdparty'
    KICAD_Z_FOOTPRINT_DIR = Join-Path $RootDirectory 'footprints'
    KICAD_Z_PLUGIN_DIR    = Join-Path $RootDirectory 'plugins'
    KICAD_Z_PROJECT_DIR   = Join-Path $RootDirectory 'projects'
    KICAD_Z_SCRIPTING_DIR = Join-Path $RootDirectory 'scripting'
    KICAD_Z_SYMBOL_DIR    = Join-Path $RootDirectory 'symbols'
    KICAD_Z_TEMPLATE_DIR  = Join-Path $RootDirectory 'template'
}

$configRoot = Join-Path $env:APPDATA 'kicad'
if (-not (Test-Path -LiteralPath $configRoot)) {
    Write-Output 'KICAD_Z_REGISTRATION=NO_CONFIG_ROOT'
    exit 0
}

$configFiles = Get-ChildItem -LiteralPath $configRoot -Directory -ErrorAction SilentlyContinue |
    ForEach-Object { Join-Path $_.FullName 'kicad_common.json' } |
    Where-Object { Test-Path -LiteralPath $_ }

if (-not $configFiles) {
    Write-Output 'KICAD_Z_REGISTRATION=NO_CONFIG_FILE'
    exit 0
}

$registered = 0
$existing = 0

foreach ($configFile in $configFiles) {
    try {
        $raw = Get-Content -LiteralPath $configFile -Raw -Encoding UTF8
        $config = $raw | ConvertFrom-Json

        if (-not $config.environment) {
            $config | Add-Member -MemberType NoteProperty -Name environment -Value ([pscustomobject]@{})
        }
        if (-not $config.environment.vars) {
            $config.environment | Add-Member -MemberType NoteProperty -Name vars -Value ([pscustomobject]@{})
        }

        $changed = $false
        foreach ($entry in $managedVariables.GetEnumerator()) {
            $property = $config.environment.vars.PSObject.Properties[$entry.Key]
            if ($null -eq $property) {
                $config.environment.vars | Add-Member -MemberType NoteProperty -Name $entry.Key -Value $entry.Value
                $registered++
                $changed = $true
            }
            else {
                $existing++
            }
        }

        if ($changed) {
            $backup = "$configFile.z-backup"
            Copy-Item -LiteralPath $configFile -Destination $backup -Force
            $json = $config | ConvertTo-Json -Depth 100
            [System.IO.File]::WriteAllText($configFile, $json + [Environment]::NewLine, [System.Text.UTF8Encoding]::new($false))
        }
    }
    catch {
        Write-Warning "KiCad-Konfiguration konnte nicht aktualisiert werden: $configFile - $($_.Exception.Message)"
    }
}

Write-Output "KICAD_Z_REGISTRATION=OK"
Write-Output "KICAD_Z_REGISTERED=$registered"
Write-Output "KICAD_Z_EXISTING=$existing"
