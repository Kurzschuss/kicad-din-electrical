# Automatische Symbolvorschauen

Mit `tools/generate_symbol_previews.py` werden einfache SVG-Vorschauen aus den vorhandenen `.kicad_sym`-Dateien erzeugt.

## Erzeugen

Vom Stammordner des Repositorys aus:

```text
python tools/generate_symbol_previews.py
```

Die Dateien werden hier abgelegt:

```text
docs/site/symbol-previews/<Bibliothek>/<Symbol>.svg
```

Beispiel:

```text
docs/site/symbol-previews/Z_MCB/MCB.svg
```

## Aktualität prüfen

```text
python tools/generate_symbol_previews.py --check
```

Der Prüfmodus liefert Fehlercode 1, wenn eine Vorschau fehlt, veraltet ist oder eine nicht mehr erwartete SVG-Datei vorhanden ist.

## Unterstützte Grafikformen in Phase 1

- Rechtecke
- Pins mit Position, Winkel und Länge

Diese Formen werden direkt aus der KiCad-Symboldatei gelesen. Leere Symbolbibliotheken erzeugen keine Vorschau.

## Bewusste Begrenzung

Die Vorschau ist eine technische Schnellansicht und noch kein vollständiger Ersatz für den KiCad-Symboleditor. Komplexere Formen wie Bögen, Kreise, Polygone und Texte werden in einer späteren Phase ergänzt.

Wenn ein Symbol keine der bislang unterstützten Formen enthält, zeigt die SVG-Datei den Hinweis `Keine unterstützte Grafik`. Es werden keine grafischen Elemente erfunden.

## Ziel

Die SVG-Dateien sollen später automatisch in die HTML-Bibliotheksreferenz eingebunden werden. Dadurch können Symbole direkt im Browser gesucht und visuell verglichen werden.
