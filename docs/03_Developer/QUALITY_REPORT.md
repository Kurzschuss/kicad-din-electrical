# Automatischer Bibliotheks-Qualitätsbericht

Das Skript `tools/generate_quality_report.py` erzeugt eine verständliche Zusammenfassung des aktuellen Bibliothekszustands.

## Bericht erzeugen

```text
python tools/generate_quality_report.py
```

Dabei wird diese Datei aktualisiert:

```text
docs/04_Reference/QUALITY_REPORT.md
```

## Bericht nur prüfen

```text
python tools/generate_quality_report.py --check
```

Der Prüfmodus verändert keine Datei und liefert Fehlercode 1, wenn der gespeicherte Bericht nicht mehr zum Repository passt.

## Enthaltene Kennzahlen

Der Bericht zeigt unter anderem:

- Anzahl der Symbolbibliotheken,
- befüllte und noch leere Symbolbibliotheken,
- Anzahl der erkannten Hauptsymbole,
- Anzahl der `.pretty`-Bibliotheken und Footprints,
- Verteilung der Richtlinien `required`, `optional` und `none`,
- vorhandene und nicht vorhandene Footprint-Zuordnungen,
- Fehler und Hinweise des Bibliotheks-Validators.

## Wichtige Einordnung

Ein Symbol ohne Footprint ist nicht automatisch unvollständig. Ohne ausdrücklich gesetzte `Footprint Policy` gilt `optional`. Rein schematische oder dokumentierende Symbole dürfen daher ohne Footprint bleiben.

Nur echte Inkonsistenzen werden als Fehler ausgewiesen, beispielsweise:

- `required` ohne Footprint,
- `none` mit eingetragenem Footprint,
- ungültige Footprint-ID,
- Verweis auf eine nicht vorhandene `.kicad_mod`-Datei.

## CI

GitHub Actions erzeugt den Bericht bei jedem Pull Request neu und vergleicht ihn mit der gespeicherten Datei. Ändern sich Bibliotheken, Symbole, Footprints oder Richtlinien, muss der Qualitätsbericht im selben Pull Request aktualisiert werden.
