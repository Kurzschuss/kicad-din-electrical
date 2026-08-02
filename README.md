# KiCad DIN Electrical

## Professionelle Open-Source-Bibliotheken für die Elektroplanung mit KiCad

**Aufbau der umfassendsten frei verfügbaren Bibliothek für Gebäudeinstallation, Energieverteilung und Schaltschrankbau.**

Dieses Projekt stellt KiCad-Bibliotheken für DIN-Schaltgeräte, Reiheneinbaugeräte und zugehörige Footprints bereit. Neben den Bibliotheken entstehen schrittweise Dokumentation, Beispiele, Vorlagen, Tests und Referenzseiten.

## Schnellzugriff

- [Bibliotheken in KiCad einbinden](docs/02_User/INSTALL.md)
- [Lokale Tests ausführen](docs/02_User/TESTING.md)
- [Vision](docs/00_Project/VISION.md)
- [Manifest](docs/00_Project/MANIFESTO.md)
- [Projekt-Roadmap](docs/01_Roadmap/PROJECT_ROADMAP.md)
- [Ideensammlung](docs/01_Roadmap/IDEAS.md)
- [Gesamte Dokumentation](docs/README.md)

## Bibliotheksnamen

Alle projektinternen Bibliotheken verwenden das Präfix `Z_`, damit sie in KiCad eindeutig erkennbar und alphabetisch gebündelt sind.

### Symbole

Alle Symbolbibliotheken liegen unter:

```text
symbols/DIN_Electrical_Symbols/
```

Jede Symbolbibliotheksdatei beginnt mit `Z_`, zum Beispiel:

- `Z_MCB.kicad_sym`
- `Z_CONTACTOR.kicad_sym`
- `Z_MAIN_SWITCH.kicad_sym`

Qualifizierte Symbol-IDs verwenden das Format:

```text
Z_<Bibliothek>:<Symbol>
```

Beispiel:

```text
Z_MCB:MCB
```

Die alte Sammelbibliotheks-ID `DIN_Electrical_Symbols:<Symbol>` darf nicht mehr verwendet werden.

### Footprints

Die Footprintbibliotheken liegen unter:

```text
footprints/
```

Für jede `.kicad_sym`-Datei existiert ein gleichnamiger `.pretty`-Ordner. Beispiel:

```text
symbols/DIN_Electrical_Symbols/Z_DIN_Control.kicad_sym
footprints/Z_DIN_Control.pretty/
```

Eine `.pretty`-Bibliothek darf mehrere `.kicad_mod`-Dateien enthalten. Jede Footprintdatei beginnt mit `Z_`, und ihr interner Footprintname muss dem Dateinamen ohne Endung entsprechen.

Qualifizierte Footprint-IDs verwenden den Namen des `.pretty`-Ordners und den Namen des enthaltenen Footprints:

```text
Z_<Bibliothek>:Z_<Footprint>
```

Die Namen links und rechts vom Doppelpunkt dürfen unterschiedlich sein, wenn mehrere Footprints in derselben Bibliothek liegen.

Die alten Bibliotheks-IDs `DIN_Rail:<Footprint>` und `Z_DIN_Rail:<Footprint>` dürfen nicht mehr verwendet werden.

## KiCad-Einrichtung

Die vollständige Schritt-für-Schritt-Anleitung steht in [docs/02_User/INSTALL.md](docs/02_User/INSTALL.md).

Kurz zusammengefasst:

- Symbolbibliotheken aus `symbols/DIN_Electrical_Symbols/` registrieren.
- Footprintbibliotheken aus den einzelnen `.pretty`-Ordnern unter `footprints/` registrieren.
- Dabei jeweils den Dateinamen beziehungsweise Ordnernamen ohne Endung als Bibliotheksnamen verwenden.

## Tests

Unter Windows startet ein Doppelklick auf `run_tests.bat` das Testmenü. Es bietet schnelle, ausführliche und zusätzliche Prüfungen sowie einen Hilfebereich.

Unter Linux und macOS steht `run_tests.sh` zur Verfügung.

Weitere Informationen enthält [docs/02_User/TESTING.md](docs/02_User/TESTING.md).

Die CI-Prüfungen stellen sicher, dass Dateinamen, interne Namen, Ordnerstruktur und Referenzen konsistent bleiben.
