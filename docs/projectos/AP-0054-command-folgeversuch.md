# AP-0054 – Verknüpfte erneute Command-Verarbeitung

## Ziel

Ein administrativ wiederaufgenommener Command kann erneut verarbeitet werden. Der Folgeversuch wird dauerhaft mit der ursprünglichen Command-ID und der Wiederaufnahme-ID verknüpft.

## Komponenten

- `CommandRetryRecord`
- `RecoveredCommandExecutionResult`
- `RecoveredCommandExecutionService`
- SQLite-Tabelle `projectos_command_retry_attempts`

## Verbindlicher Ablauf

1. Wiederaufnahme anhand der Wiederaufnahme-ID laden.
2. Zugehörigkeit zur Command-ID prüfen.
3. Sicherstellen, dass für die Wiederaufnahme noch kein Folgeversuch existiert.
4. Command über die idempotente Projekt-Command-Pipeline erneut verarbeiten.
5. Ergebnisstatus als `SUCCEEDED` oder `REJECTED` speichern.
6. Command-ID, Wiederaufnahme-ID, Folgeversuchs-ID und Korrelationskennung dauerhaft verknüpfen.

## Invarianten

- Eine Wiederaufnahme gilt genau für einen Command.
- Eine Wiederaufnahme darf nur einen Folgeversuch erzeugen.
- Der Folgeversuch verwendet weiterhin die normale Autorisierungs-, Audit- und Idempotenzpipeline.
- Ein fehlgeschlagener Folgeversuch wird erneut als `REJECTED` in der Command-Historie und in der Folgeversuchshistorie dokumentiert.
- Die aufrufende `SQLiteUnitOfWork` bildet die gemeinsame Transaktionsgrenze.

## Fehlerkennungen

- `ERR-PRJ-CMD-0009`: Wiederaufnahme nicht gefunden
- `ERR-PRJ-CMD-0010`: Wiederaufnahme gehört zu einem anderen Command
- `ERR-PRJ-CMD-0011`: Für die Wiederaufnahme existiert bereits ein Folgeversuch
- `ERR-PRJ-CMD-0012`: Folgeversuchs-ID wurde bereits verwendet

## Tests

Die Tests prüfen erfolgreiche Verknüpfung und Persistenz, unbekannte Wiederaufnahmen, falsche Command-Zuordnung und den Schutz vor doppelten Folgeversuchen.
