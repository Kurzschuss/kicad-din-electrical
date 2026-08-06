# AP-0041 – Persistente Outbox und atomare Domänenereignisse

## Status

Implementiert. Die CI-Bestätigung erfolgt über den nachfolgenden Pull-Request-Lauf.

## Ziel

Fachliche Zustandsänderungen und die daraus entstandenen Domänenereignisse müssen innerhalb derselben SQLite-Transaktion gespeichert werden. Dadurch kann ein dauerhaft gespeichertes Gerät nicht ohne zugehöriges Ereignis entstehen.

## Implementierte Komponenten

- `OutboxMessage`
- `SQLiteOutboxRepository`
- `AtomicOutboxResult[T]`
- `add_with_outbox()`

## Datenmodell

Die Tabelle `projectos_outbox` enthält:

- Ereigniskennung,
- Ereignistyp,
- Erzeugungszeitpunkt,
- technische und fachliche Aggregatkennung,
- Aggregatrevision,
- Korrelationskennung,
- JSON-Payload,
- Veröffentlichungszeitpunkt,
- Anzahl der Zustellversuche.

## Transaktionsverhalten

`add_with_outbox()` wird innerhalb einer `SQLiteUnitOfWork` aufgerufen:

1. Entität im typisierten SQLite-Repository anlegen.
2. Domänenereignis in der Outbox ergänzen.
3. Unit of Work bestätigt beide Änderungen gemeinsam.
4. Jede Ausnahme führt zum Rollback beider Änderungen.

Doppelte Ereigniskennungen werden mit `ERR-OUT-0001` abgewiesen.

## Zustellstatus

Offene Ereignisse werden über `pending(limit=...)` in Einfügereihenfolge gelesen. `mark_published()` setzt den UTC-Veröffentlichungszeitpunkt und erhöht die Zahl der Zustellversuche.

Eine eigentliche Hintergrundzustellung, Wiederholungsplanung und Dead-Letter-Ablage sind noch nicht Bestandteil dieses Arbeitspakets.

## Sicherheits- und Architekturregeln

- Nutzdaten werden ausschließlich als JSON gespeichert.
- Beim Laden werden `DomainEvent` und alle Kennungswertobjekte erneut validiert.
- Die Outbox ist append-only; fachliche Ereignisdaten werden nicht nachträglich verändert.
- Produktivzustand und Outbox teilen dieselbe SQLite-Transaktion.

## Tests

Die Tests prüfen:

- atomare Speicherung von Gerät und Ereignis,
- vollständigen Rollback bei doppelter Ereigniskennung,
- persistentes Wiederladen,
- Markierung als veröffentlicht,
- positive Begrenzung der Pending-Abfrage.

## Nicht enthalten

- asynchroner Dispatcher,
- exponentielle Wiederholungsstrategie,
- Dead-Letter-Tabelle,
- konkurrierendes Leasing mehrerer Worker,
- externe Message-Broker.

## Ergebnis

ProjectOS besitzt damit die dauerhafte Grundlage für zuverlässige Ereigniszustellung im Offline-First-Betrieb.
