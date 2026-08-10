param(
    [Parameter(Mandatory = $true)]
    [string]$RepositoryRoot
)

$ErrorActionPreference = 'Stop'

$resolvedRoot = (Resolve-Path -LiteralPath $RepositoryRoot).Path
if ($resolvedRoot.Contains('"')) {
    throw 'RepositoryRoot darf kein Anführungszeichen enthalten.'
}

$handler = Join-Path $resolvedRoot 'tools\windows\open_kicad_from_cockpit.ps1'
if (-not (Test-Path -LiteralPath $handler -PathType Leaf)) {
    throw "KiCad-Protokollhandler fehlt: $handler"
}

$protocolRoot = 'HKCU:\Software\Classes\kicad-z'
$commandKey = Join-Path $protocolRoot 'shell\open\command'

New-Item -Path $protocolRoot -Force | Out-Null
Set-Item -Path $protocolRoot -Value 'URL:Z_Cockpit KiCad Launcher'
New-ItemProperty -Path $protocolRoot -Name 'URL Protocol' -Value '' -PropertyType String -Force | Out-Null
New-Item -Path $commandKey -Force | Out-Null

$command = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "{0}" "%1"' -f $handler
Set-Item -Path $commandKey -Value $command

Write-Output 'KICAD_Z_PROTOCOL=OK'
Write-Output ("KICAD_Z_PROTOCOL_HANDLER={0}" -f $handler)
