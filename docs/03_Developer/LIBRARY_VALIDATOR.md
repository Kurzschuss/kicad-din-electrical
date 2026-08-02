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

## Footprint-Richtlinie für Symbole

Nicht jedes Symbol benötigt einen Footprint. Rein logische, dokumentierende oder schematische Symbole dürfen ausdrücklich ohne Footprint verwendet werden.

Dafür kann ein Symbol das zusätzliche Feld `Footprint Policy` erhalten:

```text
(property "Footprint Policy" "optional")
```

Erlaubte Werte:

- `required` – das Symbol muss einen gültigen, vorhandenen Footprint besitzen.
- `optional` – ein Footprint darf zugeordnet werden, ist aber nicht erforderlich.
- `none` – für dieses Symbol ist ausdrücklich kein Footprint vorgesehen.

Fehlt das Feld, gilt automatisch:

```text
optional
```

Damit ist ein leeres `Footprint`-Feld grundsätzlich erlaubt und erzeugt weder Fehler noch Hinweis.

### Bewertungsregeln

| Footprint Policy | Leeres Footprint-Feld | Gesetzter gültiger Footprint |
|---|---|---|
| `required` | Fehler | erlaubt |
| `optional` | erlaubt | erlaubt |
| `none` | erlaubt | Fehler |

Ein gesetzter Footprint-Verweis wird unabhängig von der Richtlinie immer geprüft. Eine unvollständige ID oder ein Verweis auf eine nicht vorhandene Datei ist ein Fehler.

## Geprüfte Fehler

- zu einer Symbolbibliothek fehlt der gleichnamige `.pretty`-Ordner,
- eine gesetzte Footprint-ID ist nicht vollständig qualifiziert,
- ein gesetzter Standard-Footprint existiert nicht,
- `Footprint Policy` enthält einen unbekannten Wert,
- bei `required` fehlt die Footprint-Zuordnung,
- bei `none` ist widersprüchlich ein Footprint eingetragen,
- der in einer `.kicad_mod`-Datei deklarierte Name stimmt nicht mit dem Dateinamen überein,
- ein Footprint liegt nicht in einer `.pretty`-Bibliothek,
- der Footprintkopf kann nicht gelesen werden.

## Ausgegebene Hinweise

- Symbolbibliothek ist noch leer,
- Beschreibung fehlt,
- Datenblatt fehlt,
- Hersteller fehlt,
- eine `.pretty`-Bibliothek besitzt derzeit keine gleichnamige Symbolbibliothek.

Ein fehlender Footprint ist bei der Standardrichtlinie `optional` ausdrücklich kein Hinweis.

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
