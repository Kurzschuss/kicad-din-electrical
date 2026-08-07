# AP-0044 – Autorisierte administrative Aktionen mit Audit-Nachweis

## Ziel

Administrative Dead-Letter-Wiederaufnahmen dürfen nur mit einer wirksamen Berechtigung erfolgen und müssen dauerhaft sowie manipulationsnachweisbar dokumentiert werden.

## Berechtigung

Die Aktion benötigt die Berechtigung:

```text
PERM-OUTBOX-DEAD-LETTER-RECOVER
```

Die Prüfung verwendet unverändert die ProjectOS-Reihenfolge aus dem Authorization-Framework: Blacklist, Rollen, Whitelist, Ausnahmerechte und abschließende Ablehnung.

## Ablauf

Innerhalb einer gemeinsamen `SQLiteUnitOfWork` werden nacheinander ausgeführt:

1. Berechtigung des Benutzers prüfen.
2. Aktive handelnde Rolle prüfen.
3. Outbox-Nachricht und bisherigen Delivery-Zustand laden.
4. Dead Letter kontrolliert in den Zustand `RETRY` überführen.
5. Verketteten Audit-Eintrag speichern.
6. Gemeinsame Transaktion bestätigen.

Schlägt die Autorisierung, die Wiederaufnahme oder der Audit-Eintrag fehl, wird die gesamte Transaktion zurückgerollt.

## Audit-Inhalt

Der Audit-Eintrag enthält insbesondere:

- Benutzerkennung,
- handelnde Rolle,
- verwendete Berechtigung,
- Ereigniskennung,
- Korrelationskennung,
- zwingende Begründung,
- vorherigen Status, Versuche und letzten Fehler,
- neuen Status, zurückgesetzte Versuche und nächsten Ausführungszeitpunkt,
- Hash-Verkettung mit dem vorherigen Audit-Eintrag.

## Implementierung

```text
projectos/outbox_authorization.py
tests/test_projectos_outbox_authorization.py
```

Öffentliche Bestandteile:

- `PERM_OUTBOX_DEAD_LETTER_RECOVER`
- `AuthorizedDeadLetterRecovery`
- `AuthorizedOutboxAdministrationService`

## Tests

Die Tests prüfen:

- erfolgreiche rollenbasierte Autorisierung,
- persistente Wiederaufnahme und Audit-Verkettung,
- Ablehnung ohne Berechtigung,
- vollständigen Rollback bei einem Audit-Fehler.

## Grenzen

AP-0044 stellt noch keine Benutzeroberfläche und keinen externen Administrationsendpunkt bereit. Diese bauen später auf dem jetzt verbindlichen Anwendungsdienst auf.
