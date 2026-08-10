# Z_Cockpit – ProjectOS-Projektdatei

Stand: 10. August 2026

Der Bereich `Projekt` ermöglicht das Erzeugen einer gültigen ProjectOS-Projektdatei direkt aus dem Z_Cockpit heraus. Die statische HTML-Oberfläche erzeugt dabei selbst keine fachlichen ProjectOS-Daten und schreibt keinen vom Browser gelieferten Dateipfad.

## Verbindliches Sicherheitsmodell

Eine ProjectOS-Projektdatei kann Benutzer-, Rollen-, Berechtigungs- und weitere Projektdaten enthalten. Deshalb werden zwei Schutzebenen strikt getrennt:

1. **Speicher-/Git-Zugriff** bestimmt, wer die Datei überhaupt sehen oder aus einem Repository herunterladen kann.
2. **ProjectOS-Dateirechte** bestimmen, welche Aktionen ein bereits authentifizierter Benutzer innerhalb einer vertrauenswürdigen ProjectOS-Laufzeit ausführen darf.

Wichtig: GitHub bietet innerhalb eines einzelnen Repositories keine vertrauliche Sichtbarkeit nur für einzelne Dateien. Wer Leserechte auf ein Repository besitzt, kann grundsätzlich auch die darin versionierte ProjectOS-Datei lesen. `CODEOWNERS`, Pull-Request-Regeln oder ein Ruleset können Änderungen kontrollieren, aber keine einzelne Datei vor Repository-Lesern verstecken.

Daraus folgt:

- vertrauliche Teamprojekte gehören **nicht** in das allgemeine Repository `kicad-din-electrical`;
- für vertrauliche Zusammenarbeit ist ein **separates privates Projekt-Repository** mit passend gesetzten GitHub-Benutzer-/Teamrechten vorgesehen;
- rein lokale vertrauliche Projekte werden außerhalb des Repositorys gespeichert;
- nur ausdrücklich `Repository-sichtbar` klassifizierte Projekte dürfen in das allgemeine Repository gelegt werden.

## Schutzklassen

Beim Erzeugen wird eine Schutzklasse gewählt:

| Schutzklasse | Zweck | Speicherregel |
|---|---|---|
| `private_team` | Vertrauliches Teamprojekt | außerhalb des allgemeinen Quell-Repositories; vorgesehen für einen separaten privaten Projekt-Repository-Klon |
| `restricted_local` | Vertrauliches lokales Projekt | außerhalb des allgemeinen Quell-Repositories; keine GitHub-Freigabe |
| `repository_visible` | Für alle Repository-Leser sichtbares Projekt | darf im allgemeinen Repository liegen; Sichtbarkeit muss ausdrücklich bestätigt werden |

Standard ist `private_team`.

Für `private_team` und `restricted_local` blockieren **sowohl der Windows-Handler als auch die Python-CLI** einen Zielpfad innerhalb des allgemeinen Quell-Repositories. Damit wird ein versehentliches Einchecken vertraulicher Projektdateien bereits beim Erzeugen verhindert.

## ProjectOS-Dateirechte

Für Dateioperationen sind folgende Berechtigungs-IDs verbindlich reserviert:

```text
project.file.read   = Projektdatei innerhalb ProjectOS lesen/öffnen
project.file.write  = fachliche Änderungen speichern
project.file.share  = Freigaben/Weitergabe verwalten
project.file.admin  = Dateirechte und Schutzkontext verwalten
```

Die Projektseite zeigt für jeden im `ProjectOSUserManagementState` vorhandenen Benutzer die effektive Entscheidung für diese vier Rechte an. Dabei wird ausschließlich die vorhandene ProjectOS-Autorisierung verwendet; fehlende Rechte werden als `Nicht erteilt` dargestellt und nicht automatisch ergänzt.

Die ProjectOS-Dateirechte ersetzen **nicht** die GitHub-/Dateisystemrechte. Insbesondere kann `project.file.read = deny` eine Datei nicht geheim halten, wenn der Benutzer sie bereits über GitHub lesen darf. Vertraulichkeit muss daher immer zuerst auf Speicher-/Repository-Ebene erzwungen werden.

Die lokale `Aktive ProjectOS-Identität` im statischen Cockpit ist weiterhin keine Authentifizierung. Sie darf deshalb keine echten Dateirechte erteilen oder sicherheitsrelevante Schreiboperationen freischalten. Echte schreibende Rechteänderungen müssen über die vorhandenen autorisierten ProjectOS-Change-/Command-Services beziehungsweise später über eine vertrauenswürdige Laufzeit erfolgen.

## Bedienung

1. Z_Cockpit unter Windows über `tools\windows\open_z_cockpit.bat` starten.
2. Menü `Projekt` öffnen.
3. Unter `Neues Projekt` einen Projektnamen eingeben.
4. Schutzklasse wählen; Standard ist `Vertraulich · Team`.
5. `Neues Projekt erstellen` wählen.
6. Im Windows-Dialog `Speichern unter` den Zielordner und Dateinamen bestätigen.

Die vorgeschlagene Dateiendung lautet:

```text
.projectos.json
```

Der Projektname dient als Anzeigename und als vorgeschlagener Dateiname. Das ProjectOS-v4-Bundle besitzt derzeit kein separates persistiertes Namensfeld; die dauerhafte Projektbezeichnung ergibt sich deshalb aus dem Dateinamen. Die stabile fachliche Identität bleibt die `project_id` im Bundle.

## Erzeugung

Der Browser öffnet ausschließlich einen URI der Form:

```text
projectos-z://new?name=<URL-kodierter Projektname>&protection=<Schutzklasse>
```

Es wird bewusst **kein Dateipfad** aus HTML oder JavaScript an den lokalen Handler übergeben.

Der unter HKCU registrierte Handler

```text
tools/windows/open_projectos_from_cockpit.ps1
```

validiert Projektname und Schutzklasse und öffnet anschließend `System.Windows.Forms.SaveFileDialog`. Erst dieser Windows-Dateidialog bestimmt den Zielpfad. Für vertrauliche Schutzklassen wird ein Ziel innerhalb des allgemeinen Quell-Repositories abgewiesen. Bei `repository_visible` wird die Repository-Sichtbarkeit vor dem Erzeugen ausdrücklich bestätigt.

Danach ruft der Handler auf:

```text
python -m tools.projectos_project_cli new --name <name> --output <Pfad> --protection <Schutzklasse> --overwrite
```

`tools.projectos_project_cli` prüft die Speicherregel erneut und erzeugt die Projektdatei ausschließlich über:

```text
DinEditorProjectManager().save(...)
```

Dadurch gelten dieselben ProjectOS-Persistenz- und Validierungsregeln wie bei allen anderen Projektdateien.

Ein neues Projekt enthält insbesondere:

- Bundle-Version `4`;
- automatisch erzeugte stabile `project_id`;
- leere DIN-Editor-Sitzung;
- leeren Synchronisationsstand;
- leeren `ProjectOSUserManagementState` mit derselben `project_id`.

Die Schutzklasse wird nicht als neue fachliche Wahrheit in das v4-Bundle eingeschrieben. Sie gehört zum lokalen Speicher-/Workflowkontext. Die tatsächliche Vertraulichkeit ergibt sich aus dem Speicherort beziehungsweise den Zugriffsrechten des separaten Projekt-Repositories.

## Aktives Projekt

Nach erfolgreicher Erzeugung wird lokal unter

```text
build/Z_COCKPIT_ACTIVE_PROJECT.json
```

ein kleiner Aktivzustand gespeichert. Schema v2 enthält:

- Projektname;
- absoluten Projektdateipfad;
- `project_id`;
- Bundle-Version;
- gewählte Schutzklasse.

`build/` ist kein versionierter Projektbestand. Der Aktivzustand ist ausschließlich eine lokale Startpräferenz und keine zweite fachliche Projektquelle. Aktivzustände aus Schema v1 bleiben lesbar und werden als Schutzklasse `Nicht festgelegt` behandelt.

Beim nächsten Start von

```text
tools\windows\open_z_cockpit.bat
```

wird der Aktivzustand geprüft. Nur wenn die Datei noch existiert, als ProjectOS-v4-Bundle geladen werden kann und dieselbe `project_id` besitzt, wird sie automatisch mit

```text
python -m tools.generate_z_cockpit --project-bundle <projektdatei>
```

angebunden. Ein fehlender, verschobener oder ungültiger Aktivzustand wird ignoriert; das Cockpit startet dann ohne Projektbundle.

## Sicherheit

Verbindliche Grenzen:

- Registrierung des `projectos-z:`-Protokolls nur unter `HKCU`;
- keine Administratorrechte erforderlich;
- der Browser übergibt nur Projektname und Schutzklasse, niemals einen Dateipfad;
- Dateipfade werden ausschließlich im nativen Windows-Speicherdialog gewählt;
- Projektname maximal 80 Zeichen und ohne Dateipfad-/Steuerzeichen;
- Schutzklasse wird in Browser, Handler und CLI gegen eine feste Wertemenge validiert;
- vertrauliche Projekte werden im allgemeinen Quell-Repository blockiert;
- `repository_visible` im allgemeinen Repository erfordert eine sichtbare Bestätigung;
- Erzeugung erfolgt über `DinEditorProjectManager`, nicht über JavaScript;
- im Z_Cockpit-Simulationsmodus ist die Dateierzeugung gesperrt;
- vorhandene Dateien werden nur nach Bestätigung des Windows-Overwrite-Dialogs überschrieben;
- lokale Cockpit-Identität/Simulation gilt nicht als vertrauenswürdiger Authentifizierungsnachweis.

## GitHub-Mehrbenutzerbetrieb

Für ein vertrauliches Teamprojekt ist folgende Struktur vorgesehen:

```text
kicad-din-electrical/        allgemeines Programm-/Bibliotheks-Repository
project-meine-anlage/        separates privates GitHub-Projekt-Repository
  MeineAnlage.projectos.json
```

Die Sichtbarkeit wird über die GitHub-Mitglieder-/Teamrechte des privaten Projekt-Repositories bestimmt. Benutzer, die die Datei sehen dürfen, aber nicht ändern sollen, erhalten dort nur Leserechte. Benutzer mit Änderungsrecht benötigen eine passende GitHub-Schreibrolle. Für verpflichtende PR-/Review-Regeln ist zusätzlich ein serverseitiger Branch-/Ruleset-Schutz erforderlich; der bestehende Ruleset-Punkt des Hauptprojekts bleibt bis zur separaten Freigabe blockiert.

## Manuelle Alternative

Der Workflow bleibt auch ohne Browser verwendbar:

```text
python -m tools.projectos_project_cli new --name "Werkstatt" --output "C:\Projekte\Werkstatt.projectos.json" --protection private_team
```

Ohne `--overwrite` verweigert die CLI das Überschreiben einer vorhandenen Datei.

Das aktive Projekt kann geprüft werden mit:

```text
python -m tools.projectos_project_cli active
python -m tools.projectos_project_cli active --path-only
```

## Technische Dateien

```text
tools/projectos_project_cli.py
tools/z_cockpit/project_page.py
tools/z_cockpit/project_access.py
tools/windows/register_z_project_protocol.ps1
tools/windows/open_projectos_from_cockpit.ps1
tools/windows/open_z_cockpit.bat
```

Die vorhandenen ProjectOS-v4-Persistenzbausteine bleiben unverändert:

```text
distributions/din_editor_project_manager.py
distributions/projectos_project_bundle_v4.py
```
