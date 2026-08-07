# AP-0072 – Persistente KiCad-Validierungshistorie und Vergleich

**Status:** Implementiert

## Ziel

Projektweite KiCad-Validierungsergebnisse werden unveränderlich in SQLite gespeichert, historisch gelesen und paarweise verglichen. Dadurch bleiben Qualitätsentwicklungen, Regressionen und dokumentierte Ausnahmen nachvollziehbar.

## Bestandteile

- `KiCadValidationHistoryRecord`
- `KiCadValidationComparison`
- `SQLiteKiCadValidationHistoryRepository`

## Gespeicherte Daten

- Validierungskennung
- Projektkennung
- Zeitzonenbezogener Zeitpunkt
- Korrelationskennung
- Gültigkeitsstatus
- Anzahl der Validierungsziele
- Anzahl dokumentierter KiCad-Ausnahmen
- vollständige strukturierte Findings
- SHA-256-Fingerabdruck des kanonischen Ergebnisses

## Regeln

1. Historieneinträge werden ausschließlich angehängt.
2. Validierungskennungen sind eindeutig.
3. Zeitpunkte benötigen einen Zeitzonenbezug.
4. Projektverläufe werden neuester Eintrag zuerst ausgegeben.
5. Nur Validierungen desselben Projekts dürfen verglichen werden.
6. Der Vergleich unterscheidet hinzugekommene und entfernte Findings.
7. Dokumentierte KiCad-Ausnahmen bleiben reguläre Informationen und werden über `exception_delta` ausgewertet.
8. Die Speicherung verändert weder KiCad-Dateien noch Bibliotheken.

## Fehlerkennungen

- `ERR-KICAD-0055` – Validierungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0056` – Validierungskennung bereits vorhanden
- `ERR-KICAD-0057` – Historieneintrag nicht gefunden
- `ERR-KICAD-0058` – Vergleich unterschiedlicher Projekte

## Tests

Die Tests prüfen Persistenz, Wiederherstellung, Sortierung, Fingerabdruck, Vergleich, doppelte Kennungen, fehlende Zeitzone und projektübergreifende Vergleiche.
