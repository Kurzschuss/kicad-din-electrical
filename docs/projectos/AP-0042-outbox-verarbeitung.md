# AP-0042 – Outbox-Verarbeitung mit Wiederholungslogik und Dead Letter

## Status

Abgeschlossen.

## Ziel

Persistente Outbox-Nachrichten werden deterministisch verarbeitet. Vorübergehende Fehler führen zu einem späteren Wiederholungsversuch. Dauerhaft nicht zustellbare Nachrichten werden nach einer konfigurierbaren Zahl von Versuchen in einen Dead-Letter-Zustand überführt.

## Komponenten

- `DeliveryStatus`
- `DeliveryState`
- `SQLiteDeliveryRepository`
- `OutboxProcessor`
- `OutboxProcessingResult`

## Zustände

- `PENDING`: noch kein Zustellversuch
- `RETRY`: fehlgeschlagen, erneuter Versuch nach `next_attempt_at`
- `PUBLISHED`: erfolgreich veröffentlicht
- `DEAD_LETTER`: maximale Anzahl von Versuchen erreicht

## Verbindliches Verhalten

1. Nachrichten werden in der Reihenfolge der persistenten Outbox verarbeitet.
2. Noch nicht fällige Wiederholungen werden übersprungen.
3. Jeder Zustellversuch wird gezählt.
4. Fehlerart und Fehlermeldung werden gespeichert.
5. Nach `max_attempts` erfolgt keine automatische erneute Zustellung.
6. Erfolgreich veröffentlichte Ereignisse werden in der bestehenden Outbox als veröffentlicht markiert.
7. Outbox-Nutzdaten bleiben von Zustellmetadaten getrennt.

## Transaktionsgrenze

Der Aufrufer führt `OutboxProcessor.process()` innerhalb einer `SQLiteUnitOfWork` aus. Zustellstatus und Veröffentlichungsmarkierung werden dadurch gemeinsam bestätigt oder zurückgerollt.

## Grenzen

Nicht enthalten sind parallele Worker, verteilte Sperren, exponentielles Backoff, manuelle Dead-Letter-Wiederaufnahme und externe Brokeradapter. Diese Funktionen bauen auf dem jetzt festgelegten Zustellvertrag auf.

## Tests

Die Tests prüfen erfolgreiche Zustellung, Sperrzeit vor einem Retry, Zählung mehrerer Versuche, Dead-Letter-Überführung und Ausschluss endgültig gescheiterter Nachrichten aus weiteren Läufen.
