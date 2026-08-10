# Arbeitsstand – Z_Cockpit ProjectOS-Projektdatei

Stand: 10. August 2026

## Abgeschlossen

Der neue Z_Cockpit-Bereich `Projekt` ermöglicht das Erzeugen einer ProjectOS-v4-Projektdatei ohne manuellen Python-Befehl.

Ablauf:

```text
Z_Cockpit -> Projekt -> Projektnamen eingeben -> Neues Projekt erstellen
-> nativer Windows-Dialog "Speichern unter"
-> DinEditorProjectManager.save(...)
-> lokales aktives Projekt merken
-> Z_Cockpit mit --project-bundle neu erzeugen und öffnen
```

## Sicherheitsvertrag

Der Browser übergibt ausschließlich den Projektnamen über:

```text
projectos-z://new?name=<name>
```

Ein Dateipfad wird nicht aus HTML oder JavaScript übernommen. Der Zielpfad wird ausschließlich durch `System.Windows.Forms.SaveFileDialog` festgelegt.

Das `projectos-z:`-Protokoll wird nur unter `HKCU` registriert. Die Projektdatei wird ausschließlich über `DinEditorProjectManager` erzeugt. Im Simulationsmodus wird die Dateierzeugung blockiert.

## Aktives Projekt

Lokaler, nicht versionierter Aktivzustand:

```text
build/Z_COCKPIT_ACTIVE_PROJECT.json
```

Gespeichert werden nur Projektname, Pfad, `project_id` und Bundle-Version. Beim nächsten `open_z_cockpit.bat` wird der Zustand erneut gegen die tatsächliche ProjectOS-v4-Datei geprüft. Fehlende oder ungültige Dateien blockieren den Start nicht.

## Technische Dateien

```text
tools/projectos_project_cli.py
tools/z_cockpit/project_page.py
tools/windows/register_z_project_protocol.ps1
tools/windows/open_projectos_from_cockpit.ps1
tools/windows/open_z_cockpit.bat
docs/03_Developer/Z_COCKPIT_PROJEKTDATEI.md
```

## Projektmodell

`projektdatei_workflow` steht in `project_state.yaml` auf `done`.

## Prüfung

PR #200 wurde vor dem finalen Dokumentations-Commit mit vollständiger ProjectOS-CI #551 geprüft:

- 811 Tests erfolgreich;
- Python-Syntax erfolgreich;
- KiCad-Validierung erfolgreich;
- Geräte-/Bibliotheksgeneratoren erfolgreich;
- 3D-Vorschaucheck erfolgreich;
- ProjectOS-Projektvalidator erfolgreich;
- Z_Cockpit-Erzeugung erfolgreich.

Nach diesem Dokumentationsstand muss der finale PR-Head nochmals vollständig grün sein, bevor gemergt wird.

## Unverändert

MCB-/RCD-Symbolgeometrien und Footprintgeometrien wurden nicht verändert. Der GitHub-Ruleset bleibt separat blockiert und wird durch diesen Workflow nicht aktiviert.
