# QElectroTech-Masterbibliothek

Die QElectroTech-Konvertierung erzeugt die KiCad-Symbolbibliothek:

```text
Z_Q_QElectroTech.kicad_sym
```

Sie wird derzeit reproduzierbar in GitHub Actions gebaut und als Workflow-Artefakt bereitgestellt. Die Datei ist wegen ihrer Größe nicht Bestandteil des normalen `symbols/`-Verzeichnisses im Git-Repository.

## Validierter Stand

- QElectroTech-Quelle: Commit `42692ea76d2fcc3c6cf1ca335951584cd0978922`
- Symbole gesamt: 8.755
- 0-Pin-Symbole: 2.759
- verbleibende Fälle ohne deutschen sichtbaren Namen: 0
- Konvertierungsfehler: 0
- unsupported XML-Knoten: 0
- KiCad-10-Renderprüfung: 8.755 / 8.755, 0 leere SVG-Dateien

## Erzeugung

Der vollständige Build läuft über:

```text
.github/workflows/qet-master-integration.yml
```

Der Workflow baut alle fünf QET-Sammlungen aus dem gepinnten Upstream-Commit neu auf, führt sie deterministisch zusammen und prüft die resultierende Bibliothek mit KiCad 10.

Auf `main` wird dieser vollständige Master-Build bei relevanten QET-Änderungen automatisch über `qet-master-main-dispatch.yml` gestartet.

## Installation

Nach dem Download des Workflow-Artefakts `qet-master-library-validation` die Datei `Z_Q_QElectroTech.kicad_sym` an einen dauerhaften Speicherort entpacken und in KiCad über **Einstellungen → Symbolbibliotheken verwalten → Vorhandene Bibliothek hinzufügen** einbinden.

Als Bibliotheksname kann verwendet werden:

```text
Z_Q_QElectroTech
```

Die übrigen, direkt im Repository enthaltenen Bibliotheken werden weiterhin aus `symbols/` eingebunden.
