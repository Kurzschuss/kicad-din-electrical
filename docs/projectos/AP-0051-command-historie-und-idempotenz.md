# AP-0051 – Persistente Command-Ausführungshistorie und Idempotenzschutz

## Ziel

Projektbezogene Commands dürfen bei Wiederholung nicht unbeabsichtigt mehrfach ausgeführt werden. Jede Verarbeitung wird deshalb dauerhaft in SQLite dokumentiert und über die Command-ID geschützt.

## Komponenten

- `CommandExecutionStatus`
- `CommandExecutionRecord`
- `SQLiteCommandExecutionRepository`
- `IdempotentProjectCommandResult`
- `IdempotentProjectCommandPipeline`
- `command_fingerprint()`

## Persistierte Daten

Die Tabelle `projectos_command_executions` enthält:

- Command-ID und Command-Typ,
- Projekt- und Projektobjektkennung,
- SHA-256-Fingerabdruck des fachlichen Inhalts,
- Ausführungsstatus,
- Verarbeitungszeitpunkt,
- Korrelationskennung,
- strukturierte Meldungskennungen.

## Verbindliches Verhalten

1. Eine neue Command-ID wird über die bestehende Projekt-Command-Pipeline verarbeitet.
2. Das Ergebnis wird innerhalb derselben SQLite-Transaktion in der Historie gespeichert.
3. Eine identische Wiederholung liefert den gespeicherten Status zurück und ruft den Handler nicht erneut auf.
4. Eine bereits verwendete Command-ID mit abweichendem Inhalt wird mit `ERR-PRJ-CMD-0004` abgewiesen.
5. Ein doppeltes direktes Anhängen an die Historie wird mit `ERR-PRJ-CMD-0005` verhindert.

Der Fingerabdruck berücksichtigt Command-Typ, Projekt, Projektobjekt, Payload und erwartete Revision. Zeitstempel und Korrelationskennung gehören bewusst nicht zum fachlichen Inhalt einer Wiederholung.

## Transaktionsgrenze

Die aufrufende `SQLiteUnitOfWork` bestätigt oder verwirft fachliche Ausführung, Audit und Command-Historie gemeinsam. Bei einer Ausnahme bleibt kein erfolgreicher Historieneintrag zurück.

## Tests

Die Tests prüfen:

- einmalige Handler-Ausführung,
- identische Wiederholung ohne erneute Nebenwirkung,
- Ablehnung widersprüchlicher Wiederholungen,
- Wiederherstellung der Historie nach erneutem Öffnen der Datenbank.

## Grenzen

Gespeichert wird ein stabiler Ausführungsstatus, nicht ein beliebiges Python-Rückgabeobjekt. Ein späterer API-Adapter kann fachliche Resultate über explizite, versionsgebundene JSON-Codecs ergänzen.
