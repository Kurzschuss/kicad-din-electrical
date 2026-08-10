# Z_Cockpit – Berechtigungen, White-/Blacklist und Zugriffsbereiche

Stand: 10. August 2026

Die Seite `Berechtigungen` verbindet die vorhandene ProjectOS-Autorisierung mit einer vertrauenswürdigen Verwaltung von White-/Blacklist-Regeln. Die Repository-Entwickler-Whitelist und tatsächliche Datei-/GitHub-Rechte bleiben davon getrennte Schutzebenen.

## Drei getrennte Schutzebenen

1. **ProjectOS-Rechte** aus `ProjectOSUserManagementState` regeln fachliche Aktionen.
2. **Repository-Entwickler-Whitelist** `config/authorized_developers.json` regelt den speziellen Bootstrap/Entwicklerkontext des Quell-Repositories.
3. **Datei-/GitHub-Zugriff** bestimmt, wer eine vertrauliche ProjectOS-Projektdatei tatsächlich herunterladen oder lesen kann.

Keine dieser Ebenen wird durch eine andere ersetzt.

## White- und Blacklist

ProjectOS verwendet vorhandene `ProjectOSPermissionAssignment`-Objekte:

- `source_type=whitelist`, `effect=allow` für eine Whitelist-Regel;
- `source_type=blacklist`, `effect=deny` für eine Blacklist-Regel.

Ein wirksames DENY/Blacklist hat Vorrang vor erlaubenden Quellen. Widerrufe, Benutzer-Lifecycle und Gültigkeitszeiten werden weiterhin vom vorhandenen `ProjectOSAuthorizationEvaluator` ausgewertet.

Im Z_Cockpit können jetzt Benutzer, Recht, Zugriffsbereich, Liste und Risikoklasse ausgewählt und eine Regel über den vertrauenswürdigen lokalen Governance-Pfad angelegt werden. Aktive White-/Blacklist-Zuweisungen können mit Begründung widerrufen werden. Das JavaScript schreibt nicht selbst in das Projektbundle.

## Vertrauenswürdiger Schreibpfad

```text
projectos-z://governance
 -> tools/windows/open_projectos_from_cockpit.ps1
 -> tools/projectos_governance_cli.py
 -> tools/projectos_governance.py
 -> ProjectOSUserManagementChangeService
 -> DinEditorProjectManager.save(...)
```

Vor Änderungen werden Repositoryzustand, tatsächlicher `gh`-Benutzer, dessen eindeutige ProjectOS-Zuordnung und das erforderliche Verwaltungsrecht erneut geprüft.

Für Benutzeränderungen ist `project.user.manage`, für White-/Blacklist und Rechteänderungen `project.permission.manage` erforderlich. Eine lokale Cockpit-Identität oder Simulation reicht nicht aus.

## Rechtekatalog

Der Governance-Katalog enthält:

```text
project.file.read          Projektdatei lesen
project.file.write         Projektdatei ändern
project.file.share         Projekt teilen/freigeben
project.file.admin         Projektzugriff verwalten
project.user.manage        Benutzer verwalten
project.permission.manage  Rechte/White-/Blacklist verwalten
cockpit.view               Cockpit-Bereich sehen
cockpit.edit               Cockpit-Bereich bearbeiten
github.issue.prepare       GitHub-Fehlerbericht vorbereiten
github.issue.auto_submit   GitHub-Fehlerbericht automatisch senden
```

Fehlende Grants gelten als `Nicht erteilt`; sie werden nicht implizit erlaubt.

## Zugriffsbereiche

Berechtigungen können projektweit oder für Cockpit-Bereiche vergeben werden. Vorgesehene Scopes sind unter anderem:

```text
project
page:start
page:projekt
page:geraete
page:bibliotheken
page:hersteller
page:qualitaet
page:diagnose
page:sicherheit
page:dokumentation
page:einstellungen
page:benutzer
page:berechtigungen
page:fehlerbericht
```

Die Benutzerverwaltung zeigt je Benutzer eine Matrix der effektiven Projekt-Rechte sowie `cockpit.view`/`cockpit.edit` je Bereich.

## Was „sehen dürfen“ technisch bedeutet

Die Matrix beschreibt die **ProjectOS-Policy**. Das statische HTML selbst ist keine sichere Daten-Redaktion: Wer bereits das Projektbundle oder das generierte HTML lesen kann, kann lokale Inhalte grundsätzlich untersuchen. Vertrauliche Projekte müssen deshalb zusätzlich in einem separaten privaten Projekt-Repository oder geschützten lokalen Speicher liegen.

Eine spätere authentifizierte ProjectOS-Laufzeit kann dieselben `cockpit.view/edit`-Scopes für echte serverseitige Sicht-/Bearbeitungsgates verwenden; dafür wird keine zweite Rechtequelle benötigt.

## Repository-Entwickler-Whitelist

`config/authorized_developers.json` bleibt separat. Sie wird insbesondere beim einmaligen Erstadministrator-Bootstrap eines leeren Projekts berücksichtigt. Sie ist weder die ProjectOS-Benutzer-Whitelist noch die Mitgliederliste eines privaten Projekt-Repositories.

## Audit und Widerruf

Rechteänderungen werden über den bestehenden ProjectOS-Change-Service und die vorhandene Persistenz geschrieben. Widerrufe erzeugen eigene fachliche Revocation-Objekte mit Akteur, Zeitpunkt, Grund und Quellenreferenz. Die effektive Entscheidung bleibt reproduzierbar.

## Sicherheitsgrenzen

- Kein Recht wird aus Browser-`localStorage` abgeleitet.
- Simulation kann keine echte Regel schreiben.
- Blacklist/DENY bleibt vorrangig.
- GitHub-/Dateisystemrechte bleiben für tatsächliche Dateisichtbarkeit maßgeblich.
- GitHub-Tokens werden nicht in ProjectOS-Berechtigungsdaten gespeichert.
- Der separat blockierte GitHub-Ruleset wird durch diese Verwaltung nicht aktiviert.
