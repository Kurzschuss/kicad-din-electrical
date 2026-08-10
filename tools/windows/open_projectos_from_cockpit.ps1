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

function Assert-Text([string]$Value, [string]$Label, [int]$MaxLength, [bool]$AllowEmpty = $false) {
    $text = if ($null -eq $Value) { '' } else { $Value.Trim() }
    if (-not $AllowEmpty -and -not $text) { throw "$Label darf nicht leer sein." }
    if ($text.Length -gt $MaxLength) { throw "$Label ist zu lang." }
    $hasControlCharacter = @($text.ToCharArray() | Where-Object { [int]$_ -lt 32 }).Count -gt 0
    if ($hasControlCharacter) { throw "$Label enthält Steuerzeichen." }
    return $text
}

function Assert-ProjectName([string]$Value) {
    $name = Assert-Text $Value 'Projektname' 80 $false
    if ($name -match '[\\/:*?"<>|]') { throw 'Projektname enthält unzulässige Dateinamenzeichen.' }
    return $name
}

function Assert-Protection([string]$Value) {
    $mode = if ($null -eq $Value) { '' } else { $Value.Trim().ToLowerInvariant() }
    if ($mode -notin @('private_team', 'restricted_local', 'repository_visible')) {
        throw 'Ungültige ProjectOS-Schutzklasse.'
    }
    return $mode
}

function Assert-Uuid([string]$Value, [string]$Label) {
    $parsedUuid = [Guid]::Empty
    if (-not [Guid]::TryParse((Assert-Text $Value $Label 40 $false), [ref]$parsedUuid)) {
        throw "$Label ist keine gültige UUID."
    }
    return $parsedUuid.ToString()
}

function Assert-Github([string]$Value) {
    $login = Assert-Text $Value 'GitHub-Benutzer' 39 $true
    if ($login -and $login -notmatch '^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$') {
        throw 'GitHub-Benutzername ist ungültig.'
    }
    return $login
}

function Assert-Weight([string]$Value) {
    $number = 0
    if (-not [int]::TryParse((Assert-Text $Value 'Gewichtung' 4 $false), [ref]$number) -or $number -lt 0 -or $number -gt 1000) {
        throw 'Gewichtung muss zwischen 0 und 1000 liegen.'
    }
    return $number
}

function Assert-Permission([string]$Value) {
    $permission = Assert-Text $Value 'Recht' 80 $false
    $allowed = @(
        'project.file.read','project.file.write','project.file.share','project.file.admin',
        'project.user.manage','project.permission.manage','cockpit.view','cockpit.edit',
        'github.issue.prepare','github.issue.auto_submit'
    )
    if ($permission -notin $allowed) { throw 'Unbekanntes ProjectOS-Recht.' }
    return $permission
}

function Assert-Scope([string]$Value) {
    $scope = Assert-Text $Value 'Zugriffsbereich' 80 $false
    $allowed = @(
        'project','page:start','page:projekt','page:geraete','page:bibliotheken','page:hersteller',
        'page:qualitaet','page:diagnose','page:sicherheit','page:dokumentation','page:einstellungen',
        'page:benutzer','page:berechtigungen','page:fehlerbericht'
    )
    if ($scope -notin $allowed) { throw 'Unbekannter ProjectOS-Zugriffsbereich.' }
    return $scope
}

function Test-IsWithinRoot([string]$Path, [string]$Root) {
    $fullPath = [System.IO.Path]::GetFullPath($Path).TrimEnd('\')
    $fullRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd('\')
    if ($fullPath.Equals($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
    return $fullPath.StartsWith($fullRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)
}

function Find-Python([string]$RepositoryRoot) {
    $venv = Join-Path $RepositoryRoot '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venv -PathType Leaf) { return (Resolve-Path -LiteralPath $venv).Path }
    $command = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($command) { return $command.Source }
    throw 'Python wurde nicht gefunden. Starte zuerst run_tests.bat.'
}

function Get-ActiveProjectPath([string]$Python) {
    $path = (& $Python -m tools.projectos_project_cli active --path-only 2>$null | Select-Object -First 1)
    if ($LASTEXITCODE -ne 0 -or -not $path) { throw 'Kein aktives ProjectOS-Projekt vorhanden.' }
    return $path.Trim()
}

function Refresh-Cockpit([string]$Python, [string]$RepositoryRoot) {
    $project = Get-ActiveProjectPath $Python
    & $Python -m tools.check_repository_version > $null 2>&1
    & $Python -m tools.generate_z_cockpit --project-bundle $project
    if ($LASTEXITCODE -ne 0) { throw 'Z_Cockpit konnte nach der ProjectOS-Aktion nicht aktualisiert werden.' }
    $cockpit = Join-Path $RepositoryRoot 'docs\site\z-cockpit.html'
    if (-not (Test-Path -LiteralPath $cockpit -PathType Leaf)) { throw "Z_Cockpit-Datei fehlt: $cockpit" }
    Start-Process -FilePath $cockpit | Out-Null
}

$parsed = [System.Uri]$Uri
if ($parsed.Scheme -ne 'projectos-z') { throw 'Nur das lokale projectos-z-Protokoll ist zulässig.' }
$action = $parsed.Host.ToLowerInvariant()
$repositoryRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\..')).Path
$python = Find-Python $repositoryRoot

if ($action -eq 'new') {
    $name = Assert-ProjectName (Get-QueryValue $parsed 'name')
    $protection = Assert-Protection (Get-QueryValue $parsed 'protection')
    Add-Type -AssemblyName System.Windows.Forms
    $dialog = New-Object System.Windows.Forms.SaveFileDialog
    $dialog.Title = if ($protection -eq 'private_team') {
        'Vertrauliches Teamprojekt speichern – separaten privaten Projekt-Repository-Klon verwenden'
    } elseif ($protection -eq 'restricted_local') {
        'Vertrauliches lokales ProjectOS-Projekt speichern'
    } else {
        'Repository-sichtbares ProjectOS-Projekt speichern'
    }
    $dialog.Filter = 'ProjectOS-Projekt (*.projectos.json)|*.projectos.json|JSON-Datei (*.json)|*.json'
    $dialog.FileName = "$name.projectos.json"
    $dialog.InitialDirectory = [Environment]::GetFolderPath('MyDocuments')
    $dialog.OverwritePrompt = $true
    $dialog.CheckPathExists = $true
    $dialog.RestoreDirectory = $true
    if ($dialog.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
        Write-Output 'PROJECTOS_Z_RESULT=CANCELLED'; exit 0
    }
    $target = $dialog.FileName
    $insideSourceRepository = Test-IsWithinRoot $target $repositoryRoot
    if ($protection -in @('private_team', 'restricted_local') -and $insideSourceRepository) {
        [System.Windows.Forms.MessageBox]::Show(
            'Vertrauliche ProjectOS-Projekte dürfen nicht im allgemeinen Quell-Repository gespeichert werden. Verwende einen lokalen geschützten Ordner oder einen separaten privaten Projekt-Repository-Klon.',
            'ProjectOS – Speicherort nicht zulässig', [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Warning) | Out-Null
        exit 2
    }
    if ($protection -eq 'repository_visible' -and $insideSourceRepository) {
        $answer = [System.Windows.Forms.MessageBox]::Show(
            'Diese Projektdatei liegt im allgemeinen Repository und ist damit für alle Benutzer mit Leserechten auf dieses Repository sichtbar. Wirklich fortfahren?',
            'ProjectOS – Repository-Sichtbarkeit bestätigen', [System.Windows.Forms.MessageBoxButtons]::YesNo,
            [System.Windows.Forms.MessageBoxIcon]::Warning)
        if ($answer -ne [System.Windows.Forms.DialogResult]::Yes) { Write-Output 'PROJECTOS_Z_RESULT=CANCELLED'; exit 0 }
    }
    & $python -m tools.projectos_project_cli new --name $name --output $target --protection $protection --overwrite
    if ($LASTEXITCODE -ne 0) { throw "ProjectOS-Projekt konnte nicht erzeugt werden: $target" }
    Refresh-Cockpit $python $repositoryRoot
    Write-Output ("PROJECTOS_Z_RESULT=CREATED:{0}" -f $target)
    exit 0
}

if ($action -eq 'governance') {
    $op = Assert-Text (Get-QueryValue $parsed 'op') 'Governance-Aktion' 32 $false
    switch ($op) {
        'bootstrap' {
            $name = Assert-Text (Get-QueryValue $parsed 'name') 'Bezeichnung' 80 $false
            $weight = Assert-Weight (Get-QueryValue $parsed 'weight')
            & $python -m tools.projectos_governance_cli bootstrap --name $name --weight $weight
        }
        'user-create' {
            $name = Assert-Text (Get-QueryValue $parsed 'name') 'Bezeichnung' 80 $false
            $weight = Assert-Weight (Get-QueryValue $parsed 'weight')
            $github = Assert-Github (Get-QueryValue $parsed 'github')
            & $python -m tools.projectos_governance_cli user-create --name $name --weight $weight --github $github
        }
        'user-update' {
            $userId = Assert-Uuid (Get-QueryValue $parsed 'user_id') 'Benutzer-ID'
            $name = Assert-Text (Get-QueryValue $parsed 'name') 'Bezeichnung' 80 $false
            $weight = Assert-Weight (Get-QueryValue $parsed 'weight')
            $github = Assert-Github (Get-QueryValue $parsed 'github')
            & $python -m tools.projectos_governance_cli user-update --user-id $userId --name $name --weight $weight --github $github
        }
        'rule-add' {
            $userId = Assert-Uuid (Get-QueryValue $parsed 'user_id') 'Benutzer-ID'
            $permission = Assert-Permission (Get-QueryValue $parsed 'permission')
            $scope = Assert-Scope (Get-QueryValue $parsed 'scope')
            $listType = Assert-Text (Get-QueryValue $parsed 'list_type') 'Listentyp' 16 $false
            if ($listType -notin @('whitelist','blacklist')) { throw 'Listentyp muss whitelist oder blacklist sein.' }
            $risk = Assert-Text (Get-QueryValue $parsed 'risk') 'Risikoklasse' 16 $false
            if ($risk -notin @('low','medium','high','critical')) { throw 'Ungültige Risikoklasse.' }
            & $python -m tools.projectos_governance_cli rule-add --user-id $userId --permission $permission --scope $scope --list-type $listType --risk $risk
        }
        'rule-revoke' {
            $assignmentId = Assert-Uuid (Get-QueryValue $parsed 'assignment_id') 'Zuweisungs-ID'
            $reason = Assert-Text (Get-QueryValue $parsed 'reason') 'Widerrufsgrund' 200 $false
            & $python -m tools.projectos_governance_cli rule-revoke --assignment-id $assignmentId --reason $reason
        }
        default { throw 'Unbekannte Governance-Aktion.' }
    }
    if ($LASTEXITCODE -ne 0) { throw 'ProjectOS-Verwaltungsänderung wurde verweigert oder ist fehlgeschlagen.' }
    Refresh-Cockpit $python $repositoryRoot
    Write-Output 'PROJECTOS_Z_RESULT=GOVERNANCE_UPDATED'
    exit 0
}

if ($action -eq 'report') {
    $mode = Assert-Text (Get-QueryValue $parsed 'mode') 'Meldemodus' 16 $false
    if ($mode -ne 'auto') { throw 'Unbekannter Meldemodus.' }
    $report = Get-Clipboard -Raw -Format Text
    if (-not $report) { throw 'Keine Berichtsvorschau in der Zwischenablage gefunden.' }
    if ($report.Length -gt 65536) { throw 'Fehlerbericht ist zu groß.' }
    $temp = Join-Path ([System.IO.Path]::GetTempPath()) ("projectos-report-{0}.md" -f [Guid]::NewGuid().ToString('N'))
    try {
        [System.IO.File]::WriteAllText($temp, $report, (New-Object System.Text.UTF8Encoding($false)))
        & $python -m tools.projectos_issue_reporting_cli auto --report-file $temp
        if ($LASTEXITCODE -ne 0) { throw 'Automatische GitHub-Meldung wurde verweigert oder ist fehlgeschlagen.' }
    } finally {
        Remove-Item -LiteralPath $temp -Force -ErrorAction SilentlyContinue
    }
    Refresh-Cockpit $python $repositoryRoot
    Write-Output 'PROJECTOS_Z_RESULT=REPORT_PROCESSED'
    exit 0
}

throw 'Unbekannte projectos-z-Aktion.'
