# AP-0073 – KiCad-Validierungssuche und Trenddiagnose

## Ziel

Gespeicherte projektweite KiCad-Validierungsläufe werden filterbar, paginiert und als zeitlicher Trend auswertbar. Die Auswertung verändert keine Historieneinträge.

## Komponenten

- `KiCadValidationSearchFilter`
- `KiCadValidationSearchPage`
- `KiCadValidationTrend`
- `KiCadValidationSearchService`

## Filter

Kombinierbar sind:

- Projektkennung,
- gültige oder ungültige Läufe,
- Läufe mit oder ohne dokumentierte Ausnahmen,
- konkreter Finding-Code,
- einschließlich wirkender Zeitraum.

Zeitfilter benötigen einen Zeitzonenbezug. Der Beginn darf nicht nach dem Ende liegen.

## Pagination

- Seitennummer ab 1,
- Seitengröße 1 bis 200,
- Standardgröße 50,
- Sortierung nach neuestem Zeitpunkt und Validierungskennung.

## Trenddiagnose

Die Trenddiagnose liefert:

- Gesamtzahl der Läufe,
- gültige und ungültige Läufe,
- Gültigkeitsquote,
- ersten und letzten Gültigkeitsstatus,
- erkennbare Verbesserung von ungültig zu gültig,
- Fehleranzahl am Anfang und Ende,
- Fehlerdifferenz,
- Entwicklung dokumentierter KiCad-Ausnahmen,
- zehn häufigste Finding-Codes.

Ein leeres Ergebnis besitzt definierte Nullwerte und keinen ersten oder letzten Status.

## Fehlerkennungen

- `ERR-KICAD-0059`: Zeitfilter ohne Zeitzone
- `ERR-KICAD-0060`: widersprüchlicher Zeitraum
- `ERR-KICAD-0061`: ungültige Seitennummer
- `ERR-KICAD-0062`: ungültige Seitengröße

## Grenzen

Die Diagnose beschreibt gespeicherte Validierungsläufe. Sie ersetzt weder die fachliche Bewertung einzelner Befunde noch die Prüfung, ob eine dokumentierte KiCad-Ausnahme weiterhin notwendig ist.
