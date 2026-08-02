# Bibliotheks-Validator

Der Bibliotheks-Validator prüft die grundlegende Konsistenz der KiCad-Symbol- und Footprintbibliotheken.

## Ausführen

```text
python tools/validate_libraries.py
```

Der Rückgabecode ist `0`, wenn keine Fehler gefunden wurden. Hinweise werden angezeigt, stoppen den Lauf aber nicht.

## Fehler und Hinweise

Phase 1 unterscheidet bewusst zwei Stufen:

- **ERROR**: echte Inkonsistenz; CI schlägt fehl.
- **WARNING**: Bibliothek ist technisch gültig, aber noch nicht vollständig ausgebaut.

## Geprüfte Fehler

- zu einer Symbolbibliothek fehlt der gleichnamige `.pretty`-Ordner,
- eine gesetzte Footprint-ID ist nicht vollständig qualifiziert,
- ein gesetzter Standard-Footprint existiert nicht,
- der in einer `.kicad_mod`-Datei deklarierte Name stimmt nicht mit dem Dateinamen überein,
- ein Footprint liegt nicht in einer `.pretty`-Bibliothek,
- der Footprintkopf kann nicht gelesen werden.

## Ausgegebene Hinweise

- Symbolbibliothek ist noch leer,
- Beschreibung fehlt,
- Datenblatt fehlt,
- Hersteller fehlt,
- Standard-Footprint ist noch nicht zugeordnet,
- eine `.pretty`-Bibliothek besitzt derzeit keine gleichnamige Symbolbibliothek.

## Footprint-ID

Eine vollständige Footprint-ID verwendet dieses Format:

```text
<Bibliothek>:<Footprint>
```

Beispiel:

```text
Z_DIN_Module_18mm:Z_DIN_Module_18mm
```

Dazu muss diese Datei existieren:

```text
footprints/Z_DIN_Module_18mm.pretty/Z_DIN_Module_18mm.kicad_mod
```

## CI

GitHub Actions führt den Validator nach der vollständigen Pytest-Suite aus. Nur Fehler beenden den Workflow mit Fehlercode 1. Hinweise bleiben im Protokoll sichtbar und können schrittweise abgearbeitet werden.

## Geplanter Ausbau

Spätere Phasen können zusätzlich prüfen:

- Pflichtfelder und Schlüsselwörter nach vereinbarten Qualitätsstufen,
- Pinbezeichnungen und Pin-Nummern,
- elektrische Pintypen,
- grafische Mindestanforderungen,
- 3D-Modell-Verknüpfungen,
- automatisch erzeugten Qualitätsbericht.
