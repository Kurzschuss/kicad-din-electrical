# AP-0070 – Vollständiger KiCad-Bibliotheks-Snapshot

**Status:** Abgeschlossen  
**Sprint:** SPRINT-005 – Engineering Domain

## Ziel

Die in AP-0069 eingelesenen `sym-lib-table`- und `fp-lib-table`-Einträge werden mit den nativen Dateilesern aus AP-0068 verbunden. Das Ergebnis ist ein deterministischer lokaler Bibliotheks-Snapshot für die Validierung aus AP-0067.

## Grundsatz

`kicad_standard_first` bleibt verbindlich. ProjectOS liest die von KiCad deklarierten Bibliotheken ausschließlich lesend ein und verändert weder Tabellen noch Bibliotheksdateien.

Symbol-, Footprint- und 3D-Quellen sind unabhängig:

- Eine Symboltabelle benötigt keine Footprinttabelle.
- Eine Footprinttabelle benötigt keine Symboltabelle.
- 3D-Modelle werden nur aufgenommen, wenn entsprechende Quellen bereitgestellt werden.
- Das Fehlen einer nicht deklarierten Artefaktart ist kein Fehler.
- Eine deklarierte, aber nicht lesbare Bibliothek ist ein Fehler.

## Komponenten

### `KiCadLocalFileSet`

Explizit bereitgestellte, unveränderliche Dateiquellen. Es erfolgt kein versteckter Zugriff auf das Betriebssystem oder Netzwerk.

### `KiCadCompleteSnapshotBuilder`

Verbindet:

1. aufgelöste Bibliothekstabellen,
2. lokale native KiCad-Dateien,
3. optionale 3D-Modellquellen,
4. den nativen Snapshot-Parser.

### `KiCadCompleteSnapshotResult`

Enthält die erzeugten `KiCadLibraryItemSnapshot`-Einträge und Zähler der eingelesenen Symbol-, Footprint- und 3D-Quellen.

## Footprintbibliotheken

Ein `fp-lib-table`-Eintrag verweist üblicherweise auf ein `.pretty`-Verzeichnis. Eingelesen werden die unmittelbar darin liegenden `.kicad_mod`-Dateien. Verschachtelte Unterverzeichnisse werden nicht als Bestandteil derselben KiCad-Footprintbibliothek interpretiert.

## Fehlerkennungen

| Kennung | Bedeutung |
|---|---|
| `ERR-KICAD-0045` | Dateipfad fehlt |
| `ERR-KICAD-0046` | Dateiquelle ist doppelt vorhanden |
| `ERR-KICAD-0047` | deklarierte KiCad-Datei wurde nicht gefunden |
| `ERR-KICAD-0048` | falscher Tabellentyp als Symboltabelle |
| `ERR-KICAD-0049` | falscher Tabellentyp als Footprinttabelle |
| `ERR-KICAD-0050` | deklarierte Footprintbibliothek enthält keine `.kicad_mod`-Datei |

## Tests

Die Tests prüfen:

- vollständigen Snapshot aus Symbol-, Footprint- und 3D-Quellen,
- Symboltabelle ohne Footprinttabelle,
- Footprinttabelle ohne Symboltabelle,
- fehlende deklarierte Symbolbibliothek,
- leere deklarierte Footprintbibliothek,
- Ausschluss verschachtelter Footprintdateien.

## Abgrenzung

Nicht Bestandteil dieses Arbeitspakets sind automatische Dateisystemsuche, Netzwerkbibliotheken, Schreiben von KiCad-Dateien und projektweite Synchronisation.
