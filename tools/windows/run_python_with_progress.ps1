param(
    [Parameter(Mandatory = $true)]
    [string]$Python,
    [Parameter(Mandatory = $true)]
    [string]$Script,
    [string]$Argument = '',
    [Parameter(Mandatory = $true)]
    [string]$Label
)

$ErrorActionPreference = 'Stop'

$arguments = @($Script)
if (-not [string]::IsNullOrWhiteSpace($Argument)) {
    $arguments += $Argument
}

$process = Start-Process -FilePath $Python -ArgumentList $arguments -PassThru -NoNewWindow
$started = Get-Date
$width = 20
$position = 0
$direction = 1

while (-not $process.HasExited) {
    $elapsed = [int]((Get-Date) - $started).TotalSeconds
    $cells = @(' ') * $width
    $cells[$position] = '#'
    $bar = '[' + ($cells -join '') + ']'
    Write-Host ("`r{0} {1}  laeuft seit {2,3}s" -f $bar, $Label, $elapsed) -NoNewline

    $position += $direction
    if ($position -ge ($width - 1)) {
        $position = $width - 1
        $direction = -1
    }
    elseif ($position -le 0) {
        $position = 0
        $direction = 1
    }

    Start-Sleep -Seconds 2
    $process.Refresh()
}

# WICHTIG: ExitCode erst nach WaitForExit auslesen. Bei Start-Process kann
# HasExited bereits true sein, bevor PowerShell den finalen Exitcode sauber
# aktualisiert hat. Genau das fuehrte zu falschen [FEHLER]-Meldungen trotz
# erfolgreichem Python-Lauf.
$process.WaitForExit()
$process.Refresh()
$exitCode = $process.ExitCode
$elapsed = [int]((Get-Date) - $started).TotalSeconds

if ($exitCode -eq 0) {
    Write-Host ("`r[OK]     {0} - erfolgreich beendet nach {1}s                    " -f $Label, $elapsed)
}
else {
    Write-Host ("`r[FEHLER] {0} - beendet nach {1}s (Exitcode {2})               " -f $Label, $elapsed, $exitCode)
}

exit $exitCode
