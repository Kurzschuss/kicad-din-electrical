# HTML-Bibliotheksreferenz

Die HTML-Bibliotheksreferenz stellt den aktuellen Bibliotheksstand als lokal durchsuchbare Webseite dar.

## Erzeugen

```text
python tools/generate_html_reference.py
```

Dabei wird folgende Datei aktualisiert:

```text
docs/site/index.html
```

Die Datei kann anschließend direkt im Browser geöffnet werden. Ein Webserver und zusätzliche Python-Pakete sind nicht erforderlich.

## Nur prüfen

```text
python tools/generate_html_reference.py --check
```

Der Prüfmodus verändert keine Dateien. Er endet mit Fehlercode 1, wenn `docs/site/index.html` fehlt oder nicht mehr zum aktuellen Bibliotheksstand passt.

## Angezeigte Inhalte

Die Seite zeigt:

- Anzahl der Symbolbibliotheken,
- Anzahl der erkannten Hauptsymbole,
- Anzahl der Footprintbibliotheken,
- Anzahl der Footprints,
- Anzahl der Validator-Fehler und Hinweise,
- Status jeder Symbolbibliothek,
- enthaltene Symbolnamen,
- `Footprint Policy`,
- eingetragenen Standard-Footprint,
- Inhalt jeder `.pretty`-Bibliothek.

## Suche

Das Suchfeld filtert beide Tabellen gleichzeitig. Gesucht werden kann unter anderem nach:

- Bibliotheksname,
- Symbolname,
- Footprintname,
- Status,
- Footprint-Richtlinie.

Die Suche arbeitet vollständig lokal im Browser.

## Empfohlener Ablauf

1. Symbol- oder Footprintbibliothek ändern.
2. Referenz und Qualitätsbericht aktualisieren.
3. HTML-Seite neu erzeugen.
4. Ergebnis im Browser prüfen.
5. Tests ausführen und alle erzeugten Dateien gemeinsam committen.

## CI

GitHub Actions führt den Generator im Prüfmodus aus. Dadurch schlägt ein Pull Request fehl, wenn die gespeicherte HTML-Seite nicht mehr zum Repository passt.

## Späterer Ausbau

Die statische Seite kann später erweitert werden um:

- Vorschaubilder von Symbolen und Footprints,
- getrennte Detailseiten,
- Filter nach Gerätekategorie,
- Hersteller- und Artikeldaten,
- Veröffentlichung über GitHub Pages.
