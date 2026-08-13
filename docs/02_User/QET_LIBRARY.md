# QElectroTech-Masterbibliothek

Die QElectroTech-Konvertierung erzeugt die KiCad-Symbolbibliothek:

```text
Z_Q_QElectroTech.kicad_sym
```

Sie wird reproduzierbar in GitHub Actions gebaut und dauerhaft als GitHub-Release-Asset bereitgestellt. Die Datei ist wegen ihrer Größe nicht Bestandteil des normalen `symbols/`-Verzeichnisses im Git-Repository.

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

## Dauerhafte Releases

Nach einem erfolgreichen Master-Build auf `main` veröffentlicht `qet-master-release.yml` einen unveränderlichen Snapshot mit einem Tag der Form:

```text
qet-master-<main-commit-sha-12>
```

Der Release enthält mindestens:

- `Z_Q_QElectroTech.kicad_sym`
- `qet-master-manifest.json`
- `qet-master-merge-report.json`
- `qet-master-kicad-smoke-report.json`
- `kicad-version.txt`
- `qet-source-commit.txt`
- `SHA256SUMS.txt`

Der QET-Snapshot wird nicht als allgemeiner `Latest`-Release des Projekts markiert.

GitHub-Actions-Artefakte bleiben zusätzlich als CI-Nachweis erhalten, sind aber nicht der dauerhafte Installationsweg.

## Installation

Auf der GitHub-Seite des Repositories unter **Releases** den gewünschten `qet-master-*`-Snapshot öffnen und `Z_Q_QElectroTech.kicad_sym` herunterladen.

Die Datei an einem dauerhaften Speicherort ablegen und in KiCad über **Einstellungen → Symbolbibliotheken verwalten → Vorhandene Bibliothek hinzufügen** einbinden.

Als Bibliotheksname kann verwendet werden:

```text
Z_Q_QElectroTech
```

Die Datei `SHA256SUMS.txt` im selben Release ermöglicht die Integritätsprüfung des Downloads.

Die übrigen, direkt im Repository enthaltenen Bibliotheken werden weiterhin aus `symbols/` eingebunden.
