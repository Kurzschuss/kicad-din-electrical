# AP-0043 – Dead-Letter-Wiederaufnahme und Outbox-Diagnose

## Ziel

Dieses Arbeitspaket ergänzt die persistente Outbox um administrative Diagnosefunktionen und eine kontrollierte manuelle Wiederaufnahme endgültig gescheiterter Nachrichten.

## Komponenten

- `OutboxDiagnostic` fasst die Zustände Pending, Retry, Published und Dead Letter zusammen.
- `OutboxAdministrationService.diagnose()` erzeugt einen konsistenten Laufzeitüberblick.
- `DeadLetterRecovery` dokumentiert Ereigniskennung, handelnden Benutzer, Begründung und Wiederaufnahmezeitpunkt.
- `recover_dead_letter()` setzt ausschließlich echte Dead-Letter-Nachrichten auf Retry zurück.

## Verbindliche Regeln

1. Eine Wiederaufnahme benötigt eine nicht leere Begründung.
2. Der handelnde Benutzer wird über eine `BusinessId` dokumentiert.
3. Zeitpunkte benötigen einen Zeitzonenbezug und werden nach UTC normalisiert.
4. Nur Nachrichten im Zustand `DEAD_LETTER` dürfen wiederaufgenommen werden.
5. Die Versuchszählung beginnt nach manueller Freigabe erneut bei null.
6. Der letzte technische Fehler wird bei der Wiederaufnahme gelöscht.
7. Die unveränderlichen Outbox-Nutzdaten werden nicht verändert.

## Tests

Die Tests prüfen die Diagnose aller Zustände, die erfolgreiche begründete Wiederaufnahme sowie die Ablehnung fehlender Begründungen und unzulässiger Ausgangszustände.
