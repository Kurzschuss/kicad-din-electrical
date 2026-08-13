# KiCad DIN Electrical

## Professionelle Open-Source-Bibliotheken für die Elektroplanung mit KiCad

**Aufbau der umfassendsten frei verfügbaren Bibliothek für Gebäudeinstallation, Energieverteilung und Schaltschrankbau.**

Dieses Projekt stellt KiCad-Bibliotheken für DIN-Schaltgeräte, Reiheneinbaugeräte und zugehörige Footprints bereit. Neben den Bibliotheken entstehen schrittweise Dokumentation, Beispiele, Vorlagen, Tests und Referenzseiten.

## Schnellzugriff

- [Schnellstart: erstes Symbol verwenden](docs/02_User/QUICKSTART.md)
- [Bibliotheken in KiCad einbinden](docs/02_User/INSTALL.md)
- [Häufig gestellte Fragen](docs/02_User/FAQ.md)
- [QElectroTech-Masterbibliothek mit 8.755 Symbolen](docs/02_User/QET_LIBRARY.md)
- [Technischen Gerätekatalog verwenden](docs/02_User/DEVICE_CATALOG.md)
- [Durchsuchbaren Gerätekatalog öffnen](docs/site/devices.html)
- [Lokale Tests und CI verstehen](docs/02_User/TESTING.md)
- [Am Projekt mitwirken](CONTRIBUTING.md)
- [Entwicklerleitfaden](docs/03_Developer/DEVELOPER.md)
- [Änderungsverlauf](CHANGELOG.md)
- [Lizenz](LICENSE)
- [Vision](docs/00_Project/VISION.md)
- [Manifest](docs/00_Project/MANIFESTO.md)
- [Projekt-Roadmap](docs/01_Roadmap/PROJECT_ROADMAP.md)
- [Ideensammlung](docs/01_Roadmap/IDEAS.md)
- [Gesamte Dokumentation](docs/README.md)

## Bibliotheksnamen

Alle projektinternen Bibliotheken verwenden das Präfix `Z_`, damit sie in KiCad eindeutig erkennbar und alphabetisch gebündelt sind.

### Symbole

Alle direkt im Repository enthaltenen Symbolbibliotheken liegen unter:

```text
symbols/
```

Die große, reproduzierbar erzeugte QElectroTech-Masterbibliothek `Z_Q_QElectroTech.kicad_sym` wird wegen ihrer Dateigröße als permanentes GitHub-Release-Asset verteilt; siehe [QElectroTech-Masterbibliothek](docs/02_User/QET_LIBRARY.md).

Jede direkt eingecheckte Symbolbibliotheksdatei beginnt mit `Z_`, zum Beispiel:

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

Für jede direkt eingecheckte `.kicad_sym`-Datei existiert ein gleichnamiger `.pretty`-Ordner. Beispiel:

```text
symbols/Z_DIN_Control.kicad_sym
footprints/Z_DIN_Control.pretty/
```

Eine `.pretty`-Bibliothek darf mehrere `.kicad_mod`-Dateien enthalten. Jede Footprintdatei beginnt mit `Z_`, und ihr interner Footprintname muss dem Dateinamen ohne Endung entsprechen.

Vorhandene Beispiele:

- `Z_DIN_Module_18mm.kicad_mod`
- `Z_DIN_Terminal_Block.kicad_mod`

Qualifizierte Footprint-IDs verwenden den Namen des `.pretty`-Ordners und den Namen des enthaltenen Footprints:

```text
Z_<Bibliothek>:Z_<Footprint>
```

Vorhandenes Beispiel:

```text
Z_DIN_Module_18mm:Z_DIN_Module_18mm
```

Die Namen links und rechts vom Doppelpunkt dürfen unterschiedlich sein, wenn mehrere Footprints in derselben Bibliothek liegen.

Die alten Bibliotheks-IDs `DIN_Rail:<Footprint>` und `Z_DIN_Rail:<Footprint>` dürfen nicht mehr verwendet werden.

## KiCad-Einrichtung

Für den kürzesten Einstieg siehe [docs/02_User/QUICKSTART.md](docs/02_User/QUICKSTART.md).

Die vollständige Schritt-für-Schritt-Anleitung steht in [docs/02_User/INSTALL.md](docs/02_User/INSTALL.md).

Kurz zusammengefasst:

- Direkt eingecheckte Symbolbibliotheken aus `symbols/` registrieren.
- Die QElectroTech-Masterbibliothek separat aus einem `qet-master-*`-Release herunterladen und registrieren.
- Footprintbibliotheken aus den einzelnen `.pretty`-Ordnern unter `footprints/` registrieren.
- Dabei jeweils den Dateinamen beziehungsweise Ordnernamen ohne Endung als Bibliotheksnamen verwenden.

## Tests

Unter Windows startet ein Doppelklick auf `run_tests.bat` das Testmenü. Es bietet schnelle, ausführliche und zusätzliche Prüfungen sowie einen Hilfebereich.

Unter Linux und macOS steht `run_tests.sh` zur Verfügung.

Weitere Informationen enthält [docs/02_User/TESTING.md](docs/02_User/TESTING.md).

Die zentrale CI `ProjectOS complete test suite` prüft zusätzlich Qualitätsprofile, KiCad-Bibliotheken, Generatoren, Kataloge, Vorschauen, HTML-Ausgaben und den ProjectOS-Projektzustand.
