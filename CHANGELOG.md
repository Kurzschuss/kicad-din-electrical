# Änderungsverlauf

Dieses Dokument fasst größere, benutzer- oder entwicklerrelevante Änderungen am Repository zusammen.

Bis eine repositoryweite Versionsstrategie festgelegt ist, verwendet der Changelog datierte Abschnitte statt erfundener Versionsnummern. Für vollständige technische Details bleiben Git-Historie, Pull Requests, Issues und die Dateien unter `docs/handover/` maßgeblich.

## Unreleased

### Dokumentation

- Einsteiger- und Entwicklerdokumentation wird unter Issue #62 konsolidiert.
- Veraltete Symbolpfade und CI-Verweise werden an die aktuelle Repositorystruktur angepasst.
- Root-README und Dokumentationsindex verlinken zentrale Benutzer-, Mitwirkungs-, Entwicklungs-, Lizenz- und Änderungsdokumente direkt.

## 2026-08-13

### DIN-Editor und KiCad-Sync

- Issue #5 abgeschlossen: KiCad-Schematic-Export schreibt atomar über eine temporäre Datei im Zielverzeichnis, synchronisiert vor dem Replace und bewahrt bei Fehlern den vorherigen gültigen Stand.
- Fehlerpfade für Build-, Replace-, Manifest- und Referenzfehler sind durch Integrationstests abgesichert.
- Issue #6 abgeschlossen: neue GUI-neutrale `DinEditorWorkflowViewModel`-Fassade für New/Open, Edit, Save, Save-As, KiCad-Sync, explizite Konfliktentscheidungen, Fehlerfeedback sowie Undo/Redo.
- Der vollständige Benutzerworkflow einschließlich Fehlerfällen, Save-As, Reload und post-reload Undo/Redo ist durch Regressionstests abgedeckt.

### QElectroTech-Masterbibliothek

- Die QElectroTech-Konvertierung wurde für die vorgesehenen Sammlungen vollständig integriert.
- Der validierte Master umfasst 8.755 konvertierte Symbole.
- `Z_Q_QElectroTech.kicad_sym` wird reproduzierbar erzeugt und wegen seiner Größe als dauerhaftes GitHub-Release-Asset verteilt.
- Deutscher sichtbarer Value, QET-Quellmetadaten, Kategoriepfade und dokumentierte Anpassungen werden erhalten beziehungsweise nachvollziehbar erzeugt.
- Post-Merge-Validierung und Release-Publishing laufen im abgesicherten QET-Dispatcher-Workflow.

### Dokumentation und Nachvollziehbarkeit

- Ein vollständiger Gesamt-Handover für den Arbeitsstand vom 13.08.2026 wurde unter `docs/handover/` aufgenommen.
- Nach Abschluss der DIN-Editor-Issues #5 und #6 wurde der Handover fortgeschrieben.

## Frühere Änderungen

Der Changelog wurde erst nach bereits umfangreicher Projektentwicklung eingeführt. Frühere Änderungen werden nicht nachträglich als scheinbar vollständige Release-Historie rekonstruiert. Für diese Zeiträume gelten die Git-Historie, vorhandene Pull Requests, Issues, Roadmap-/Projektprotokolle und Handover-Dokumente als Primärquellen.
