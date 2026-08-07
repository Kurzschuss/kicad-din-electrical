# AP-0068 – Einlesen nativer KiCad-Bibliotheksdateien

## Status

Implementiert.

## Ziel

Native KiCad-Bibliotheksdateien werden ausschließlich lesend verarbeitet und in den lokalen `KiCadLibraryItemSnapshot` aus AP-0067 überführt. KiCad bleibt die führende Datenquelle; ProjectOS erfindet kein konkurrierendes Bibliotheksformat.

## Unterstützte Quellen

- moderne Symbolbibliotheken: `.kicad_sym`
- einzelne Footprints: `.kicad_mod`
- 3D-Modelle: `.step`, `.stp`, `.wrl`

Alte Legacy-Symbolbibliotheken (`.lib`) gehören nicht zum Umfang dieses Arbeitspakets.

## Komponenten

- `NativeKiCadSource`
- `KiCadSnapshotBuildResult`
- `KiCadNativeSnapshotBuilder`

## Verarbeitung

1. Der relative Quellpfad wird auf Sicherheit geprüft.
2. Symbol- und Footprint-Dateien werden als KiCad-S-Expression gelesen.
3. Symbolnamen und Pinnummern werden aus der nativen Struktur übernommen.
4. Footprintnamen werden aus der nativen Footprint-Struktur übernommen.
5. 3D-Modellnamen werden aus dem Dateinamen abgeleitet.
6. Für jede Quelldatei wird eine SHA-256-Prüfsumme erzeugt.
7. Die Ergebnisse werden deterministisch sortiert und auf Dubletten geprüft.

## Optionale Artefakte

Symbol-, Footprint- und 3D-Quellen werden unabhängig voneinander verarbeitet. Eine Symbolbibliothek benötigt weder eine Footprint- noch eine 3D-Modellquelle. Ob diese Artefakte fachlich erforderlich sind, entscheidet ausschließlich `KiCadTargetRequirements` aus AP-0067.

## Grenzen

- Keine Änderung nativer KiCad-Dateien.
- Keine automatische Erzeugung fehlender Footprints oder 3D-Modelle.
- Keine Verpflichtung, dass zu jedem Symbol weitere Artefakte existieren.
- Keine vollständige KiCad-Projektanalyse in diesem Arbeitspaket.

## Fehlerkennungen

- `ERR-KICAD-0023`: Bibliotheksname fehlt
- `ERR-KICAD-0024`: unsicherer oder absoluter Quellpfad
- `ERR-KICAD-0025`: nicht unterstütztes Dateiformat
- `ERR-KICAD-0026`: doppelter Bibliothekseintrag
- `ERR-KICAD-0027`: keine native Symbolbibliothek
- `ERR-KICAD-0028`: Symbolbibliothek enthält keine Symbole
- `ERR-KICAD-0029`: kein natives Footprint
- `ERR-KICAD-0030`: KiCad-Textdatei ist nicht UTF-8
- `ERR-KICAD-0031`: ungültige KiCad-S-Expression

## Tests

Die Tests prüfen Symbol- und Pinimport, unabhängigen Footprint- und Modellimport, reine Symbolbibliotheken ohne Footprint, Dubletten, unsichere Pfade und ungültige Formate.
