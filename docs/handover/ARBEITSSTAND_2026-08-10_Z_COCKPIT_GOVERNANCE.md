# Arbeitsstand – Z_Cockpit Governance und GitHub-Reporting

Stand: 10. August 2026

## Umgesetzt

Die Benutzer-, Berechtigungs- und Fehlermeldungsbereiche besitzen jetzt eine gemeinsame Governance-Schicht.

### Benutzer

- ProjectOS-Benutzerprofil mit Bezeichnung, Gewichtung und optional eindeutigem `github_login`;
- Benutzerverwaltungs-Persistenz v5, ältere v1–v4 lesbar;
- äußeres ProjectOS-Projektbundle bleibt v4;
- Benutzer anlegen und Profilwerte ändern über vertrauenswürdigen lokalen Schreibpfad;
- Erstadministrator nur bei leerer Benutzerverwaltung, aktuellem offiziellem Repository und authentifiziertem Repository-Whitelist-Benutzer.

### Rechte / White-/Blacklist

Zentrale Rechte:

```text
project.file.read
project.file.write
project.file.share
project.file.admin
project.user.manage
project.permission.manage
cockpit.view
cockpit.edit
github.issue.prepare
github.issue.auto_submit
```

Scopes: `project` sowie die Z_Cockpit-Seiten `page:*`.

Whitelist schreibt `allow`, Blacklist schreibt `deny`; DENY bleibt vorrangig. Regeln können über den ProjectOS-Change-Service angelegt und nachvollziehbar widerrufen werden.

### Vertrauensmodell

Die lokale Cockpit-Identität und Simulation sind **keine Authentifizierung**. Reale Governance-Aktionen verwenden:

```text
gh-authentifizierter GitHub-Benutzer
 -> eindeutige ProjectOS-github_login-Zuordnung
 -> ProjectOSAuthorizationEvaluator
 -> ProjectOSUserManagementChangeService
 -> DinEditorProjectManager.save(...)
```

Vor schreibenden Aktionen wird der Repositoryzustand erneut geprüft.

`cockpit.view/edit` beschreibt die fachliche Sicht-/Bearbeitungspolicy. Bereits vorhandenes statisches HTML beziehungsweise bereits heruntergeladene Projektdateien werden dadurch nicht geheim. Vertraulichkeit bleibt zusätzlich Aufgabe des privaten Repository-/Dateisystemzugriffs.

### Automatische GitHub-Fehlermeldung

Automatisches Senden ist nur zulässig bei:

- aktuellem freigegebenem Repositorystand;
- offiziellem Repository, kein Fork;
- `gh`-Authentifizierung;
- eindeutiger ProjectOS-Benutzerzuordnung;
- aktivem Benutzer;
- effektivem `github.issue.auto_submit`;
- bestätigter Berichtsvorschau;
- keinem Simulationsmodus;
- bestandenem Secret-Heuristik-Scan.

Vor Neuanlage wird nach Dubletten gesucht: zuerst ProjectOS-Fingerprint, dann konservativ nach manuell vorhandenem Issue mit exakt gleichem normalisiertem Titel plus technischer Referenz.

Eine Dublette erzeugt kein zweites Issue. Das bestehende Issue erhält eine gekennzeichnete Wiederholungsmeldung. Reporter und Anzahl der Meldungen bleiben nachvollziehbar. Letzter lokaler Status: `build/Z_ISSUE_REPORTING_RESULT.json`.

## Technische Hauptdateien

```text
distributions/projectos_authorization.py
distributions/projectos_user_management_persistence.py
tools/projectos_governance.py
tools/projectos_governance_cli.py
tools/projectos_issue_reporting.py
tools/projectos_issue_reporting_cli.py
tools/z_cockpit/governance_controls.py
tools/windows/open_projectos_from_cockpit.ps1
tools/check_repository_version.py
```

## Prüfstand

PR #202: erster vollständiger Lauf CI #558 grün mit 824 Tests sowie Python-Syntax, KiCad-, 3D-, Projektvalidator- und Z_Cockpit-Prüfungen. Nach den anschließenden Sicherheits-/Dubletten-/Dokumentationsnachschärfungen muss der finale PR-Head erneut vollständig grün sein.

## Unverändert

- keine MCB-/RCD-Symbolgeometrie geändert;
- keine Footprintgeometrie geändert;
- kein GitHub-Ruleset aktiviert;
- Ruleset bleibt separat `blocked` bis zur ausdrücklichen Freigabe.
