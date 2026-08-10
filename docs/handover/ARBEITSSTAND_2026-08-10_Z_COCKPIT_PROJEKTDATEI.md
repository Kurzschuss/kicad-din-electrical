# Arbeitsstand – Z_Cockpit ProjectOS-Projektdatei

Stand: 10. August 2026

## Abgeschlossen

Der Z_Cockpit-Bereich `Projekt` ermöglicht das Erzeugen einer ProjectOS-v4-Projektdatei ohne manuellen Python-Befehl und berücksichtigt jetzt von Anfang an Mehrbenutzer- und Vertraulichkeitsanforderungen.

Ablauf:

```text
Z_Cockpit -> Projekt -> Projektnamen eingeben -> Schutzklasse wählen
-> Neues Projekt erstellen -> nativer Windows-Dialog "Speichern unter"
-> Speicherregel prüfen -> DinEditorProjectManager.save(...)
-> lokales aktives Projekt merken
-> Z_Cockpit mit --project-bundle neu erzeugen und öffnen
```

## Sicherheitsvertrag

Es gibt zwei getrennte Schutzebenen:

1. Speicher-/Git-Zugriff entscheidet, wer die Projektdatei überhaupt sehen kann.
2. ProjectOS-Rechte entscheiden, was ein authentifizierter Benutzer innerhalb ProjectOS mit dem Projekt tun darf.

GitHub kann innerhalb eines einzelnen Repositories keine einzelne Datei vor bestimmten Repository-Lesern verbergen. Vertrauliche Teamprojekte dürfen deshalb nicht im allgemeinen Repository `kicad-din-electrical` liegen.

Schutzklassen:

```text
private_team        Vertraulich · Team
restricted_local    Vertraulich · lokal
repository_visible  Repository-sichtbar
```

`private_team` ist Standard. Für `private_team` und `restricted_local` wird ein Speicherziel innerhalb des allgemeinen Quell-Repositories sowohl im Windows-Handler als auch in der Python-CLI abgewiesen. `repository_visible` darf dort gespeichert werden, erfordert aber eine ausdrückliche Sichtbarkeitsbestätigung.

Für vertrauliche Zusammenarbeit ist ein separates privates GitHub-Projekt-Repository mit passenden Mitglieder-/Teamrechten vorgesehen.

## ProjectOS-Dateirechte

Verbindlich reserviert sind:

```text
project.file.read
project.file.write
project.file.share
project.file.admin
```

Die Projektseite zeigt diese Rechte für vorhandene ProjectOS-Benutzer als Zugriffsmatrix an. Die Entscheidungen werden aus dem bestehenden `ProjectOSUserManagementState` übernommen; fehlende Grants werden nicht erfunden.

Die lokale Cockpit-Identität und der Simulationsmodus bleiben ausdrücklich **keine Authentifizierung**. Sie dürfen daher keine echten Dateirechte erteilen.

## Aktives Projekt

Lokaler, nicht versionierter Aktivzustand:

```text
build/Z_COCKPIT_ACTIVE_PROJECT.json
```

Schema v2 speichert Projektname, Pfad, `project_id`, Bundle-Version und Schutzklasse. Schema-v1-Zustände bleiben lesbar und werden mit Schutzklasse `Nicht festgelegt` behandelt. Beim nächsten `open_z_cockpit.bat` wird der Zustand erneut gegen die tatsächliche ProjectOS-v4-Datei geprüft. Fehlende oder ungültige Dateien blockieren den Start nicht.

## Technische Dateien

```text
tools/projectos_project_cli.py
tools/z_cockpit/project_page.py
tools/z_cockpit/project_access.py
tools/windows/register_z_project_protocol.ps1
tools/windows/open_projectos_from_cockpit.ps1
tools/windows/open_z_cockpit.bat
docs/03_Developer/Z_COCKPIT_PROJEKTDATEI.md
docs/03_Developer/Z_COCKPIT_BERECHTIGUNGEN.md
```

## Projektmodell

`projektdatei_workflow` und `projektdatei_zugriffsschutz` stehen in `project_state.yaml` auf `done`.

## Noch bewusst getrennt

Ein serverseitiger GitHub-Ruleset ist weiterhin nicht automatisch aktiviert. Für verpflichtende PR-/Review-Regeln eines späteren privaten Projekt-Repositories muss dessen Serverkonfiguration separat eingerichtet werden. Der bestehende Ruleset-Punkt bleibt blockiert, bis eine ausdrückliche Freigabe erfolgt.

## Unverändert

MCB-/RCD-Symbolgeometrien und Footprintgeometrien werden durch diese Erweiterung nicht verändert.
