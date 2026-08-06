# AP-0055 – Vollständige Command-Lebenszyklusansicht

## Ziel

AP-0055 führt die bisher getrennten Daten über Command-Ausführung, administrative Wiederaufnahme und Folgeversuche in einer chronologischen, unveränderlichen Sicht zusammen.

## Archivierung der ursprünglichen Ausführung

Vor einer administrativen Wiederaufnahme wird der abgelehnte Ausführungsstand vollständig in `projectos_command_execution_archive` kopiert. Erst danach wird der aktuelle Historieneintrag für eine erneute Verarbeitung entfernt.

Archiviert werden:

- Command-ID und Command-Typ,
- Projekt- und Objektkennung,
- Payload-Fingerabdruck,
- ursprünglicher Status,
- Verarbeitungszeitpunkt,
- Korrelationskennung,
- strukturierte Meldungskennungen,
- zugehörige Wiederaufnahme-ID.

Damit bleibt die ursprüngliche Ablehnung auch nach einer erfolgreichen Wiederholung dauerhaft nachweisbar.

## Lebenszyklusmodell

`CommandLifecycleService` verbindet:

1. archivierte ursprüngliche Ausführungen,
2. den aktuellen Historieneintrag,
3. administrative Wiederaufnahmen,
4. dokumentierte Folgeversuche.

Das Ergebnis ist `CommandLifecycleView`.

Unterstützte Zustände:

- `NOT_FOUND`
- `REJECTED`
- `READY_FOR_RETRY`
- `RETRY_REJECTED`
- `SUCCEEDED`

## Invarianten

- Archivierte Ausführungen werden nicht verändert.
- Eine Wiederaufnahme löscht nicht den historischen Nachweis der Ablehnung.
- Der aktuelle Status wird ausschließlich aus persistenten Daten abgeleitet.
- Unbekannte Commands liefern eine leere Sicht mit `NOT_FOUND`.
- Die ursprüngliche Ausführung ist über `original_execution` direkt zugänglich.

## Dateien

- `projectos/project_command_lifecycle.py`
- `tests/test_projectos_project_command_lifecycle.py`
- `docs/projectos/AP-0055-command-lebenszyklus.md`

## Abgrenzung

AP-0055 ist eine lesende Projektion. Exportformate, Benutzeroberfläche, Pagination und projektweite Suchindizes folgen in späteren Arbeitspaketen.
