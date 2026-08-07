param(
    [ValidateSet('status', 'install', 'update')]
    [string]$Mode = 'status',
    [string]$RepositoryUrl = 'https://github.com/Kurzschuss/kicad-din-electrical.git',
    [string]$TargetDirectory = '',
    [string]$DefaultBranch = 'main'
)

$ErrorActionPreference = 'Stop'

function Write-Result([string]$Name, [object]$Value) {
    Write-Output ("{0}={1}" -f $Name, $Value)
}

function Resolve-DocumentsDirectory {
    $documents = [Environment]::GetFolderPath('MyDocuments')
    if ([string]::IsNullOrWhiteSpace($documents)) {
        $documents = Join-Path $env:USERPROFILE 'Documents'
    }
    return $documents
}

function Resolve-GitExecutable {
    $command = Get-Command git.exe -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }

    $candidates = @(
        (Join-Path $env:ProgramFiles 'Git\cmd\git.exe'),
        (Join-Path $env:ProgramFiles 'Git\bin\git.exe'),
        (Join-Path $env:LOCALAPPDATA 'Programs\Git\cmd\git.exe')
    )
    if (${env:ProgramFiles(x86)}) {
        $candidates += Join-Path ${env:ProgramFiles(x86)} 'Git\cmd\git.exe'
    }

    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) { return $candidate }
    }

    $desktopRoot = Join-Path $env:LOCALAPPDATA 'GitHubDesktop'
    if (Test-Path -LiteralPath $desktopRoot) {
        $apps = Get-ChildItem -LiteralPath $desktopRoot -Directory -Filter 'app-*' -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending
        foreach ($app in $apps) {
            foreach ($relative in @('resources\app\git\cmd\git.exe', 'resources\app\git\bin\git.exe')) {
                $candidate = Join-Path $app.FullName $relative
                if (Test-Path -LiteralPath $candidate) { return $candidate }
            }
        }
    }

    return $null
}

if ([string]::IsNullOrWhiteSpace($TargetDirectory)) {
    $TargetDirectory = Join-Path (Resolve-DocumentsDirectory) 'GitHub\kicad-din-electrical'
}

$gitExe = Resolve-GitExecutable
if (-not $gitExe) {
    Write-Result 'PROJECTOS_GIT_EXE' 'nicht verfügbar'
    Write-Result 'PROJECTOS_REPO_STATUS' 'GIT_NOT_FOUND'
    Write-Result 'PROJECTOS_REPO_TARGET' $TargetDirectory
    exit 2
}
Write-Result 'PROJECTOS_GIT_EXE' $gitExe

if ($Mode -eq 'install') {
    if (Test-Path -LiteralPath $TargetDirectory) {
        if (Test-Path -LiteralPath (Join-Path $TargetDirectory '.git')) {
            Write-Result 'PROJECTOS_REPO_STATUS' 'ALREADY_INSTALLED'
            Write-Result 'PROJECTOS_REPO_TARGET' $TargetDirectory
            exit 0
        }
        Write-Result 'PROJECTOS_REPO_STATUS' 'TARGET_EXISTS_NOT_GIT'
        Write-Result 'PROJECTOS_REPO_TARGET' $TargetDirectory
        exit 3
    }

    $parent = Split-Path -Parent $TargetDirectory
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    & $gitExe clone --branch $DefaultBranch --single-branch $RepositoryUrl $TargetDirectory
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Result 'PROJECTOS_REPO_STATUS' 'INSTALLED'
    Write-Result 'PROJECTOS_REPO_TARGET' $TargetDirectory
    exit 0
}

if (-not (Test-Path -LiteralPath (Join-Path $TargetDirectory '.git'))) {
    Write-Result 'PROJECTOS_REPO_STATUS' 'NOT_INSTALLED'
    Write-Result 'PROJECTOS_REPO_TARGET' $TargetDirectory
    exit 0
}

Push-Location $TargetDirectory
try {
    $branch = (& $gitExe branch --show-current).Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) { $branch = $DefaultBranch }
    $localCommit = (& $gitExe rev-parse HEAD).Trim()
    $dirty = -not [string]::IsNullOrWhiteSpace((& $gitExe status --porcelain | Out-String).Trim())

    Write-Result 'PROJECTOS_REPO_TARGET' $TargetDirectory
    Write-Result 'PROJECTOS_REPO_BRANCH' $branch
    Write-Result 'PROJECTOS_REPO_LOCAL_COMMIT' $localCommit
    Write-Result 'PROJECTOS_REPO_DIRTY' $dirty

    & $gitExe fetch origin --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Result 'PROJECTOS_REPO_STATUS' 'REMOTE_UNAVAILABLE'
        Write-Result 'PROJECTOS_REPO_REMOTE_COMMIT' 'nicht verfügbar'
        if ($Mode -eq 'update') { exit 6 }
        exit 0
    }

    $remoteRef = "origin/$branch"
    & $gitExe rev-parse --verify $remoteRef *> $null
    if ($LASTEXITCODE -ne 0) { $remoteRef = "origin/$DefaultBranch" }
    $remoteCommit = (& $gitExe rev-parse $remoteRef).Trim()

    $counts = (& $gitExe rev-list --left-right --count "HEAD...$remoteRef").Trim() -split '\s+'
    $ahead = [int]$counts[0]
    $behind = [int]$counts[1]

    if ($ahead -eq 0 -and $behind -eq 0) { $relation = 'CURRENT' }
    elseif ($ahead -gt 0 -and $behind -eq 0) { $relation = 'AHEAD' }
    elseif ($ahead -eq 0 -and $behind -gt 0) { $relation = 'BEHIND' }
    else { $relation = 'DIVERGED' }

    Write-Result 'PROJECTOS_REPO_STATUS' $relation
    Write-Result 'PROJECTOS_REPO_REMOTE_COMMIT' $remoteCommit
    Write-Result 'PROJECTOS_REPO_AHEAD' $ahead
    Write-Result 'PROJECTOS_REPO_BEHIND' $behind

    if ($Mode -eq 'update') {
        if ($dirty) {
            Write-Result 'PROJECTOS_REPO_UPDATE' 'BLOCKED_DIRTY'
            exit 4
        }
        if ($relation -eq 'BEHIND') {
            & $gitExe pull --ff-only origin $branch
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            Write-Result 'PROJECTOS_REPO_UPDATE' 'UPDATED'
        }
        elseif ($relation -eq 'CURRENT') {
            Write-Result 'PROJECTOS_REPO_UPDATE' 'NOT_NEEDED'
        }
        else {
            Write-Result 'PROJECTOS_REPO_UPDATE' 'BLOCKED_NON_FF'
            exit 5
        }
    }
}
finally {
    Pop-Location
}
