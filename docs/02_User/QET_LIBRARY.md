# QElectroTech-Masterbibliothek

Die QElectroTech-Konvertierung erzeugt die KiCad-Symbolbibliothek:

```text
Z_Q_QElectroTech.kicad_sym
```

Die Datei wird reproduzierbar in GitHub Actions gebaut und bewusst nicht als große generierte Datei im normalen Git-Verlauf unter `symbols/` gespeichert. Nach einem erfolgreichen Masterlauf auf `main` wird stattdessen ein dauerhafter GitHub-Release-Snapshot veröffentlicht. Das Actions-Artefakt bleibt zusätzlich als CI-Nachweis erhalten.

## Validierter Stand

- QElectroTech-Quelle: Commit `42692ea76d2fcc3c6cf1ca335951584cd0978922`
- Symbole gesamt: 8.755
- 0-Pin-Symbole: 2.759
- verbleibende Fälle ohne deutschen sichtbaren Namen: 0
- Konvertierungsfehler: 0
- unsupported XML-Knoten: 0
- KiCad-10-Renderprüfung: 8.755 / 8.755, 0 leere SVG-Dateien

## Erzeugung und Veröffentlichung

Der vollständige Build läuft über:

```text
.github/workflows/qet-master-integration.yml
```

Der Workflow baut alle fünf QET-Sammlungen aus dem gepinnten Upstream-Commit neu auf, führt sie deterministisch zusammen und prüft die resultierende Bibliothek mit KiCad 10.

Auf `main` wird dieser vollständige Master-Build bei relevanten QET-Änderungen automatisch über `qet-master-main-dispatch.yml` gestartet. Nach einem erfolgreichen Masterlauf veröffentlicht `qet-master-release.yml` einen unveränderlichen Release-Snapshot mit einem Tag nach dem Schema:

```text
qet-master-<Repository-Commit-SHA, 12 Zeichen>
```

Der QET-Release wird ausdrücklich nicht als allgemeiner `Latest`-Release des Gesamtprojekts markiert.

Jeder QET-Release enthält mindestens:

- `Z_Q_QElectroTech.kicad_sym`
- `qet-master-manifest.json`
- `qet-master-merge-report.json`
- `qet-master-kicad-smoke-report.json`
- `kicad-version.txt`
- `qet-source-commit.txt`
- `SHA256SUMS.txt`

Das Workflow-Artefakt `qet-master-library-validation` enthält denselben validierten Build samt Reports, ist aber primär als CI-Artefakt gedacht.

## Installation

1. Auf GitHub den gewünschten `qet-master-*`-Release öffnen.
2. Das Release-Asset `Z_Q_QElectroTech.kicad_sym` herunterladen.
3. Die Datei an einem dauerhaften Speicherort ablegen.
4. In KiCad **Einstellungen → Symbolbibliotheken verwalten → Vorhandene Bibliothek hinzufügen** wählen und die Datei einbinden.

Als Bibliotheksname kann verwendet werden:

```text
Z_Q_QElectroTech
```

Bei Bedarf kann die heruntergeladene Datei gegen `SHA256SUMS.txt` geprüft werden.

Die übrigen, direkt im Repository enthaltenen Bibliotheken werden weiterhin aus `symbols/` eingebunden.
