# AP-0057 – Standardisierte Query-Pipeline

## Status

Implementiert.

## Ziel

ProjectOS erhält eine einheitliche, zustandsfreie Abfrageschnittstelle für Command-Lebenszyklen, projektweite Command-Suchen und administrative Diagnosewerte.

## Bestandteile

- `ProjectQueryPipeline`
- `ProjectQueryExecutionResult`
- `CommandQueryHandlers`
- `QUERY_COMMAND_LIFECYCLE`
- `QUERY_COMMAND_SEARCH`
- `QUERY_COMMAND_DIAGNOSTIC`

## Query-Typen

### `project.command.lifecycle`

Pflichtparameter:

- `command_id`

Ergebnis:

- `CommandLifecycleView`

### `project.command.search`

Optionale Parameter:

- `project_id`
- `command_type`
- `state`
- `processed_from`
- `processed_until`
- `text`
- `page`
- `page_size`

Ergebnis:

- `CommandSearchPage`

### `project.command.diagnostic`

Die Query akzeptiert keine Parameter.

Ergebnis:

- `CommandExecutionDiagnostic`

## Ergebnisvertrag

Jede erfolgreiche Query liefert ein `ProjectQueryExecutionResult` mit:

- ursprünglichem Query-Objekt,
- typisiertem fachlichem Ergebnis,
- unveränderter Korrelationskennung im umgebenden `Result`.

## Fehlerverträge

- `ERR-PRJ-QRY-0001`: Kein Handler für den Query-Typ registriert.
- `ERR-PRJ-QRY-0002`: Parameter fehlen oder sind ungültig.

Fehlerhafte Eingaben werden als strukturiertes `Result` zurückgegeben und nicht als ungefangene Ausnahme an die aufrufende Schicht weitergereicht.

## Registrierungsregeln

- Jeder Query-Typ besitzt genau einen Handler.
- Query-Typen verwenden das Schema `<domäne>.<objekt>.<aktion>`.
- Doppelte Registrierungen werden abgelehnt.
- Queries verändern keinen fachlichen Zustand.

## Tests

Die Tests prüfen:

- Lebenszyklusabfrage,
- Suchparameter und Pagination,
- Diagnoseabfrage,
- unbekannte Query-Typen,
- fehlende Pflichtparameter,
- ungültige Parametertypen,
- doppelte Handler-Registrierung.

## Abgrenzung

AP-0057 führt noch keine Berechtigungsprüfung für lesende Zugriffe ein. Projektbezogene Sichtrechte und die Auditierung sensibler Diagnoseabfragen folgen in einem eigenen Arbeitspaket.
