# Bibliotheksreferenz automatisch erzeugen

Das Skript `tools/generate_library_reference.py` erstellt die beiden Indexseiten der Symbol- und Footprintbibliotheken direkt aus der Repositorystruktur.

## Erzeugen

```text
python tools/generate_library_reference.py
```

Dabei werden aktualisiert:

```text
docs/04_Reference/SYMBOL_INDEX.md
docs/04_Reference/FOOTPRINT_INDEX.md
```

Unter Windows kann alternativ `run_tests.bat` gestartet und **7 – Bibliotheksreferenz erzeugen** gewählt werden.

## Nur prüfen

```text
python tools/generate_library_reference.py --check
```

Das Skript verändert dabei keine Datei. Es beendet sich mit Fehlercode 1, wenn mindestens ein Index nicht mehr zur Repositorystruktur passt.

Im Windows-Menü steht dafür **8 – Bibliotheksreferenz prüfen** zur Verfügung.

## Ausgewertete Dateien

Der Generator liest:

- `symbols/DIN_Electrical_Symbols/Z_*.kicad_sym`
- `footprints/Z_*.pretty/`
- alle darin enthaltenen `*.kicad_mod`-Dateien

## Symbolanalyse

Für jede `.kicad_sym`-Datei werden die Hauptsymbole direkt unter `kicad_symbol_lib` ausgewertet. Interne KiCad-Unterblöcke für Grafikdarstellungen oder Einheiten werden nicht als eigenständige Symbole gezählt.

Der Symbolindex zeigt pro Bibliothek:

- leerer oder befüllter Status,
- Anzahl der Hauptsymbole,
- alphabetisch sortierte Symbolnamen,
- den erwarteten gleichnamigen `.pretty`-Ordner,
- die Anzahl der dort enthaltenen Footprints.

Eine leere Symbolbibliothek wird als **vorbereitet, noch leer** gekennzeichnet. Ein fehlender gleichnamiger `.pretty`-Ordner wird ausdrücklich angezeigt.

## Footprintanalyse

Leere `.pretty`-Bibliotheken werden als vorbereitet gekennzeichnet. Befüllte Bibliotheken zeigen die Anzahl und Namen ihrer Footprints. Eine `.pretty`-Bibliothek darf mehrere `.kicad_mod`-Dateien enthalten.

## Empfohlener Ablauf

1. Symbolbibliothek, `.pretty`-Ordner oder Footprint ändern.
2. Referenz neu erzeugen.
3. Änderungen an den beiden Indexdateien kontrollieren.
4. Lokale Tests starten.
5. Dateien gemeinsam committen.

Detailseiten wie `Z_DIN_Control.md` bleiben handgepflegt. Der Generator überschreibt nur die beiden Gesamtindizes.
