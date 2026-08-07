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

## Unterstützte Grafikformen

- Rechtecke
- Polylinien
- Pins mit Position, Winkel und Länge

Diese Formen werden direkt aus der KiCad-Symboldatei gelesen. Damit kann insbesondere die Funktionsgrafik des MCB-1P-Goldstandards vollständig in der technischen SVG-Vorschau dargestellt werden. Leere Symbolbibliotheken erzeugen keine Vorschau.

## Bewusste Begrenzung

Die Vorschau ist eine technische Schnellansicht und kein vollständiger Ersatz für den KiCad-Symboleditor. Komplexere Formen wie Bögen, Kreise und freie Texte werden derzeit nicht gerendert.

Wenn ein Symbol keine der unterstützten Formen enthält, zeigt die SVG-Datei den Hinweis `Keine unterstützte Grafik`. Es werden keine grafischen Elemente erfunden.

## Ziel

Die SVG-Dateien werden in die HTML-Bibliotheksreferenz eingebunden. Dadurch können Symbole direkt im Browser gesucht und visuell verglichen werden. Der Prüfmodus stellt sicher, dass Änderungen an den KiCad-Symbolen nicht unbemerkt mit veralteten Vorschauen veröffentlicht werden.
