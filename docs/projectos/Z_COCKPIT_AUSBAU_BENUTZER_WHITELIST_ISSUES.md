# Z_Cockpit – Benutzer, White-/Blacklist, Zugriffe und Fehlermeldungen

Stand: 10. August 2026

Der ursprüngliche Dreierausbau Benutzerverwaltung → Whitelist/Berechtigungen → Fehlermeldung ist inzwischen um eine gemeinsame **Zugriffs- und Reporting-Governance** erweitert. Es gibt weiterhin keine parallele Benutzer-, Rechte- oder Fehlerdatenbank im Z_Cockpit.

## Verbindliche Quellen

- Benutzer/Lifecycle/Rollen/Rechte: `ProjectOSUserManagementState`;
- effektive Autorisierung: `ProjectOSAuthorizationEvaluator`;
- schreibende Benutzer-/Rechteänderungen: `ProjectOSUserManagementChangeService` über `tools/projectos_governance.py`;
- Repository-Entwickler-Whitelist: `config/authorized_developers.json`;
- Repositorystand: `tools/check_repository_version.py`;
- automatische GitHub-Meldung/Dubletten: `tools/projectos_issue_reporting.py`;
- tatsächliche Projektdateisichtbarkeit: Dateisystem-/GitHub-Zugriff gemäß `Z_COCKPIT_PROJEKTDATEI.md`.

## Benutzerverwaltung

ProjectOS-Benutzer besitzen stabile ID, Bezeichnung, Gewichtung, Rollen, Lifecycle und optional einen eindeutigen `github_login`. Die Benutzerverwaltungs-Persistenz ist Version `5`; ProjectOS-Projektbundle v4 bleibt das äußere Dateiformat und ältere Benutzerverwaltungsstände bleiben lesbar.

Die Cockpit-Verwaltung kann Benutzer anlegen und Bezeichnung, Gewichtung und GitHub-Zuordnung ändern. Schreibende Aktionen werden nicht durch die Browseridentität autorisiert. Der lokale Handler ermittelt den tatsächlich über `gh` authentifizierten GitHub-Benutzer, ordnet ihn einem eindeutigen ProjectOS-Profil zu und prüft das erforderliche Recht fail-closed.

Der lokale Testuser und Simulationsmodus bleiben rein read-only.

## Erstadministrator

Ein neues Projekt wird weiterhin ohne erfundenen Benutzer erzeugt. Ein erster Administrator kann nur gebootstrappt werden, wenn Benutzerverwaltung leer, Repository aktuell und offiziell, GitHub CLI authentifiziert und der GitHub-Benutzer in der Repository-Entwickler-Whitelist freigegeben ist.

Nach dem Bootstrap gelten die normalen ProjectOS-Rechte; die Repository-Whitelist ersetzt sie nicht.

## White-/Blacklist und Berechtigungen

Whitelist und Blacklist sind echte `ProjectOSPermissionAssignment`-Quellen:

```text
whitelist -> allow
blacklist -> deny
```

DENY/Blacklist bleibt vorrangig. Regeln können über den vertrauenswürdigen Governance-Pfad angelegt und mit eigener Revocation nachvollziehbar widerrufen werden.

Zentraler Rechtekatalog:

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

Scopes umfassen das Gesamtprojekt sowie die einzelnen Z_Cockpit-Bereiche (`page:*`). Dadurch ist abbildbar, wer fachlich sehen oder bearbeiten darf und wer Benutzer/Rechte verwalten darf.

### Sicherheitsgrenze der Sichtrechte

`cockpit.view/edit` ist die ProjectOS-Zugriffspolicy. Ein bereits statisch erzeugtes HTML oder ein bereits heruntergeladenes Projektbundle kann dadurch nicht kryptographisch versteckt werden. Vertrauliche Dateien müssen zusätzlich durch einen privaten Repository-/Dateisystemzugriff geschützt werden. Das Cockpit darf diesen Unterschied nie als Scheinsicherheit darstellen.

## Automatische GitHub-Fehlermeldungen

Der manuelle Bericht und `GitHub-Issue vorbereiten` bleiben erhalten. Zusätzlich darf ein Benutzer automatisch senden, wenn **alle** Gates unmittelbar vor der Aktion erfüllt sind:

- offizielles Repository, kein Fork/anderer Remote;
- Version nicht hinter `origin/main`;
- Repositorystand `current=true`;
- `gh`-Authentifizierung vorhanden;
- eindeutige GitHub→ProjectOS-Benutzerzuordnung;
- Benutzer aktiv und `github.issue.auto_submit` effektiv erlaubt;
- kein Simulationsmodus;
- sichtbarer Bericht wurde geprüft/bestätigt;
- Secret-Heuristik findet kein offensichtliches Token/Passwort/Private-Key-Muster.

Die lokal in `localStorage` gewählte Cockpit-Identität reicht dafür nicht aus.

## Dubletten und Meldehistorie

ProjectOS berechnet einen SHA-256-Fingerprint aus Kategorie, technischer Referenz und normalisiertem Kurztitel. Vor Neuanlage wird zweistufig gesucht:

1. exakte ProjectOS-Fingerprint-Markierung;
2. konservativer Fallback auf bereits manuell angelegte Issues mit exakt gleichem normalisiertem Titel und – wenn angegeben – derselben technischen Referenz.

Bei einer Dublette wird **kein zweites Issue** angelegt. Stattdessen wird das bestehende Issue kommentiert. ProjectOS kann ursprünglichen Reporter, weitere Reporter, Meldeanzahl, Issue-Nummer/-URL und Fingerprint nachvollziehen. Das letzte Ergebnis liegt lokal unter `build/Z_ISSUE_REPORTING_RESULT.json`.

## Repository-Entwickler-Whitelist

`config/authorized_developers.json` bleibt separat von ProjectOS-Whitelist/Blacklist. Sie ist insbesondere für den kontrollierten Bootstrap und bestehende Entwicklerfreigaben relevant, aber weder ProjectOS-Benutzerliste noch Zugriffssteuerung eines privaten Projekt-Repositories.

## Umgesetzter Vertrauenspfad

```text
Z_Cockpit
 -> projectos-z://governance oder projectos-z://report
 -> Windows-Handler
 -> ProjectOS Governance-/Reporting-CLI
 -> erneute Repository-/GitHub-/ProjectOS-Prüfung
 -> ProjectOS-Projektdatei oder GitHub
```

Die Browserseite liefert Bedienparameter beziehungsweise die bestätigte Berichtsvorschau; sie erteilt selbst keine Sicherheitsfreigabe.

## Dokumentation

- `docs/03_Developer/Z_COCKPIT_BENUTZERVERWALTUNG.md`
- `docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md`
- `docs/03_Developer/Z_COCKPIT_FEHLERMELDUNG.md`
- `docs/03_Developer/Z_COCKPIT_PROJEKTDATEI.md`
- `docs/handover/ARBEITSSTAND_2026-08-10_Z_COCKPIT_GOVERNANCE.md`

## Projektstatus

`benutzerverwaltung`, `whitelist_verwaltung`, `issue_fehlermeldung` und `zugriffs_reporting_governance` stehen in `project_state.yaml` auf `done`. Die früheren Folgepunkte 3D-Vorschauen, KiCad-Editoraufrufe und Laufzeitdiagnose-Persistenz sind ebenfalls abgeschlossen.

Separat offen bleibt nur die serverseitige Aktivierung des vorbereiteten GitHub-Rulesets; dieser Punkt bleibt bis zu ausdrücklicher Freigabe `blocked`.
