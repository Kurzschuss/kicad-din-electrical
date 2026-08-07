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

if ([string]::IsNullOrWhiteSpace($TargetDirectory)) {
    $TargetDirectory = Join-Path (Resolve-DocumentsDirectory) 'GitHub\kicad-din-electrical'
}

$git = Get-Command git.exe -ErrorAction SilentlyContinue
if (-not $git) {
    Write-Result 'PROJECTOS_REPO_STATUS' 'GIT_NOT_FOUND'
    Write-Result 'PROJECTOS_REPO_TARGET' $TargetDirectory
    exit 2
}

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
    & $git.Source clone --branch $DefaultBranch --single-branch $RepositoryUrl $TargetDirectory
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
    $branch = (& $git.Source branch --show-current).Trim()
    if ([string]::IsNullOrWhiteSpace($branch)) { $branch = $DefaultBranch }
    $localCommit = (& $git.Source rev-parse HEAD).Trim()
    $dirty = -not [string]::IsNullOrWhiteSpace((& $git.Source status --porcelain | Out-String).Trim())

    & $git.Source fetch origin --quiet
    $remoteRef = "origin/$branch"
    & $git.Source rev-parse --verify $remoteRef *> $null
    if ($LASTEXITCODE -ne 0) {
        $remoteRef = "origin/$DefaultBranch"
    }
    $remoteCommit = (& $git.Source rev-parse $remoteRef).Trim()

    $counts = (& $git.Source rev-list --left-right --count "HEAD...$remoteRef").Trim() -split '\s+'
    $ahead = [int]$counts[0]
    $behind = [int]$counts[1]

    if ($ahead -eq 0 -and $behind -eq 0) { $relation = 'CURRENT' }
    elseif ($ahead -gt 0 -and $behind -eq 0) { $relation = 'AHEAD' }
    elseif ($ahead -eq 0 -and $behind -gt 0) { $relation = 'BEHIND' }
    else { $relation = 'DIVERGED' }

    Write-Result 'PROJECTOS_REPO_STATUS' $relation
    Write-Result 'PROJECTOS_REPO_TARGET' $TargetDirectory
    Write-Result 'PROJECTOS_REPO_BRANCH' $branch
    Write-Result 'PROJECTOS_REPO_LOCAL_COMMIT' $localCommit
    Write-Result 'PROJECTOS_REPO_REMOTE_COMMIT' $remoteCommit
    Write-Result 'PROJECTOS_REPO_AHEAD' $ahead
    Write-Result 'PROJECTOS_REPO_BEHIND' $behind
    Write-Result 'PROJECTOS_REPO_DIRTY' $dirty

    if ($Mode -eq 'update') {
        if ($dirty) {
            Write-Result 'PROJECTOS_REPO_UPDATE' 'BLOCKED_DIRTY'
            exit 4
        }
        if ($relation -eq 'BEHIND') {
            & $git.Source pull --ff-only origin $branch
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
