# Mitwirken am Projekt

Vielen Dank für das Interesse an `kicad-din-electrical`.

Das Projekt soll eine hochwertige, frei verfügbare KiCad-Bibliothek für Elektroinstallation, Energieverteilung und Schaltschrankbau aufbauen. Beiträge sind willkommen, wenn sie nachvollziehbar, prüfbar und mit der bestehenden Struktur vereinbar sind.

## Vor einer Änderung

1. Repository aktualisieren.
2. Für die Änderung einen eigenen Branch anlegen.
3. Prüfen, ob bereits ein passendes Issue existiert.
4. Bei größeren neuen Bibliotheken oder Regeländerungen zuerst ein Issue anlegen.

Empfohlene Branchnamen:

```text
symbols/<kurze-beschreibung>
footprints/<kurze-beschreibung>
docs/<kurze-beschreibung>
tests/<kurze-beschreibung>
fix/<kurze-beschreibung>
```

## Symbolbibliotheken

Symbolbibliotheken liegen ausschließlich unter:

```text
symbols/DIN_Electrical_Symbols/
```

Dateinamen verwenden die Endung `.kicad_sym` und beginnen mit `Z_`.

Zu jeder Symbolbibliothek gehört unter `footprints/` ein gleichnamiger `.pretty`-Ordner.

Beispiel:

```text
symbols/DIN_Electrical_Symbols/Z_DIN_Control.kicad_sym
footprints/Z_DIN_Control.pretty/
```

Eine Symbolbibliothek darf mehrere Symbole enthalten.

## Footprintbibliotheken

Footprints liegen nicht direkt unter `footprints/`, sondern in `.pretty`-Bibliotheken:

```text
footprints/<Bibliotheksname>.pretty/<Footprintname>.kicad_mod
```

Eine `.pretty`-Bibliothek darf leer vorbereitet sein oder mehrere `.kicad_mod`-Dateien enthalten.

Dateiname und interner Footprintname müssen übereinstimmen.

## Dokumentation aktualisieren

Nach Änderungen an Symbolbibliotheken, `.pretty`-Ordnern oder Footprints muss die Bibliotheksreferenz neu erzeugt werden:

```text
python tools/generate_library_reference.py
```

Unter Windows kann dafür `run_tests.bat` und anschließend **7 – Bibliotheksreferenz erzeugen** verwendet werden.

Die automatisch erzeugten Dateien sind:

```text
docs/04_Reference/SYMBOL_INDEX.md
docs/04_Reference/FOOTPRINT_INDEX.md
```

Diese beiden Dateien nicht von Hand pflegen.

## Tests ausführen

Unter Windows:

```text
run_tests.bat
```

Für die vollständige lokale Prüfung die Menüauswahl **3 – Alle Prüfungen** verwenden.

Plattformunabhängig:

```text
python -m pip install -r requirements-dev.txt
python -m pytest -q
python tools/generate_library_reference.py --check
```

Ein Beitrag soll erst eingereicht werden, wenn die lokalen Prüfungen erfolgreich sind.

## Pull Request

Ein Pull Request sollte:

- nur eine zusammengehörige Änderung enthalten,
- einen verständlichen deutschen Titel besitzen,
- den Zweck und die geänderten Dateien beschreiben,
- Testergebnisse nennen,
- bei sichtbaren KiCad-Änderungen nach Möglichkeit Vorschaubilder enthalten,
- keine unbeabsichtigten Formatänderungen an anderen Dateien enthalten.

## Commit-Nachrichten

Empfohlene Form:

```text
<bereich>: <kurze beschreibung>
```

Beispiele:

```text
symbols: add distribution board symbols
footprints: add 18 mm DIN module variants
tests: validate symbol and footprint mapping
docs: explain KiCad library installation
fix: correct footprint library assignment
```

## Fachliche Anforderungen

Symbole und Footprints sollen:

- eindeutig benannt sein,
- für den vorgesehenen Anwendungsfall verständlich sein,
- vorhandene Projektregeln einhalten,
- keine ungeprüften Herstellerangaben als allgemein gültige Norm darstellen,
- bei normbezogenen Aussagen die verwendete Grundlage dokumentieren.

## Keine automatischen Änderungen an fremden Inhalten

Vorhandene Symbole, Footprints oder Regeln nicht nebenbei umbenennen oder umgestalten. Solche Änderungen benötigen einen eigenen Pull Request mit Begründung.

## Fragen und Vorschläge

Neue Ideen werden zunächst als GitHub-Issue dokumentiert. Dadurch bleiben Ziel, Diskussion und spätere Umsetzung nachvollziehbar.
