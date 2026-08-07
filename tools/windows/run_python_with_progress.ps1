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

# Start-Process liefert unter Windows/Windows PowerShell in einzelnen Fällen
# keinen auswertbaren ExitCode, obwohl der Kindprozess sauber beendet wurde.
# Deshalb schreibt ein kleiner temporaerer CMD-Wrapper den Python-Exitcode
# explizit in eine Statusdatei. Die Konsolenausgabe des Python-Prozesses bleibt
# dabei sichtbar und die Fortschrittsanzeige kann weiterhin parallel laufen.
$tempBase = Join-Path ([System.IO.Path]::GetTempPath()) ("projectos-progress-" + [guid]::NewGuid().ToString('N'))
$wrapper = $tempBase + '.cmd'
$statusFile = $tempBase + '.exitcode'

function Escape-CmdArgument([string]$Value) {
    return '"' + ($Value -replace '"', '""') + '"'
}

$pythonArg = Escape-CmdArgument $Python
$scriptArg = Escape-CmdArgument $Script
$statusArg = Escape-CmdArgument $statusFile
$argumentText = ''
if (-not [string]::IsNullOrWhiteSpace($Argument)) {
    $argumentText = ' ' + $Argument
}

$wrapperContent = @"
@echo off
$pythonArg $scriptArg$argumentText
set "PROJECTOS_EXITCODE=%ERRORLEVEL%"
> $statusArg echo %PROJECTOS_EXITCODE%
exit /b %PROJECTOS_EXITCODE%
"@
Set-Content -LiteralPath $wrapper -Value $wrapperContent -Encoding ASCII

try {
    $process = Start-Process -FilePath $env:ComSpec -ArgumentList @('/d', '/c', ('"' + $wrapper + '"')) -PassThru -NoNewWindow
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

    if (-not (Test-Path -LiteralPath $statusFile)) {
        throw "Der Python-Exitcode konnte nicht ermittelt werden: Statusdatei fehlt."
    }

    $rawExitCode = (Get-Content -LiteralPath $statusFile -Raw).Trim()
    $exitCode = 0
    if (-not [int]::TryParse($rawExitCode, [ref]$exitCode)) {
        throw "Der Python-Exitcode ist ungueltig: '$rawExitCode'."
    }

    if ($exitCode -eq 0) {
        Write-Host ("`r[OK]     {0} - erfolgreich beendet nach {1}s                    " -f $Label, $elapsed)
    }
    else {
        Write-Host ("`r[FEHLER] {0} - beendet nach {1}s (Exitcode {2})               " -f $Label, $elapsed, $exitCode)
    }

    exit $exitCode
}
finally {
    Remove-Item -LiteralPath $wrapper -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $statusFile -Force -ErrorAction SilentlyContinue
}
