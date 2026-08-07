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

$process.WaitForExit()
$elapsed = [int]((Get-Date) - $started).TotalSeconds
Write-Host ("`r[{0}] {1} - beendet nach {2}s                    " -f ($(if ($process.ExitCode -eq 0) { 'OK' } else { 'FEHLER' })), $Label, $elapsed)
exit $process.ExitCode
