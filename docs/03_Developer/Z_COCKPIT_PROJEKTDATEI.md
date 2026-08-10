# Z_Cockpit – ProjectOS-Projektdatei

Stand: 10. August 2026

Der Bereich `Projekt` ermöglicht das Erzeugen einer gültigen ProjectOS-Projektdatei direkt aus dem Z_Cockpit heraus. Die statische HTML-Oberfläche erzeugt dabei selbst keine fachlichen ProjectOS-Daten und schreibt keinen vom Browser gelieferten Dateipfad.

## Bedienung

1. Z_Cockpit unter Windows über `tools\windows\open_z_cockpit.bat` starten.
2. Menü `Projekt` öffnen.
3. Unter `Neues Projekt` einen Projektnamen eingeben.
4. `Neues Projekt erstellen` wählen.
5. Im Windows-Dialog `Speichern unter` den Zielordner und Dateinamen bestätigen.

Die vorgeschlagene Dateiendung lautet:

```text
.projectos.json
```

Der Projektname dient als Anzeigename und als vorgeschlagener Dateiname. Das ProjectOS-v4-Bundle besitzt derzeit kein separates persistiertes Namensfeld; die dauerhafte Projektbezeichnung ergibt sich deshalb aus dem Dateinamen. Die stabile fachliche Identität bleibt die `project_id` im Bundle.

## Erzeugung

Der Browser öffnet ausschließlich einen URI der Form:

```text
projectos-z://new?name=<URL-kodierter Projektname>
```

Es wird bewusst **kein Dateipfad** aus HTML oder JavaScript an den lokalen Handler übergeben.

Der unter HKCU registrierte Handler

```text
tools/windows/open_projectos_from_cockpit.ps1
```

validiert den Projektnamen und öffnet anschließend `System.Windows.Forms.SaveFileDialog`. Erst dieser Windows-Dateidialog bestimmt den Zielpfad.

Danach ruft der Handler auf:

```text
python -m tools.projectos_project_cli new --name <name> --output <vom Windows-Dialog gewählter Pfad> --overwrite
```

`tools.projectos_project_cli` erzeugt die Projektdatei ausschließlich über:

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

## Aktives Projekt

Nach erfolgreicher Erzeugung wird lokal unter

```text
build/Z_COCKPIT_ACTIVE_PROJECT.json
```

ein kleiner Aktivzustand gespeichert. Er enthält nur:

- Projektname;
- absoluten Projektdateipfad;
- `project_id`;
- Bundle-Version.

`build/` ist kein versionierter Projektbestand. Der Aktivzustand ist ausschließlich eine lokale Startpräferenz und keine zweite fachliche Projektquelle.

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
- der Browser übergibt nur den Projektnamen;
- Dateipfade werden ausschließlich im nativen Windows-Speicherdialog gewählt;
- Projektname maximal 80 Zeichen und ohne Dateipfad-/Steuerzeichen;
- Erzeugung erfolgt über `DinEditorProjectManager`, nicht über JavaScript;
- im Z_Cockpit-Simulationsmodus ist die Dateierzeugung gesperrt;
- vorhandene Dateien werden nur nach Bestätigung des Windows-Overwrite-Dialogs überschrieben.

## Manuelle Alternative

Der Workflow bleibt auch ohne Browser verwendbar:

```text
python -m tools.projectos_project_cli new --name "Werkstatt" --output "C:\Projekte\Werkstatt.projectos.json"
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
tools/windows/register_z_project_protocol.ps1
tools/windows/open_projectos_from_cockpit.ps1
tools/windows/open_z_cockpit.bat
```

Die vorhandenen ProjectOS-v4-Persistenzbausteine bleiben unverändert:

```text
distributions/din_editor_project_manager.py
distributions/projectos_project_bundle_v4.py
```
