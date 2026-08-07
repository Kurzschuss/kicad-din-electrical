# AP-0046 – Persistente Projektverantwortungen

## Ziel

Projektbezogene Verantwortungen werden dauerhaft, zeitlich nachvollziehbar und eindeutig in SQLite gespeichert.

## Unterstützte Funktionen

- Projektleiter
- Stellvertretung
- Vertrauensperson
- Nachfolger

## Implementierung

`ProjectResponsibility` beschreibt eine Zuordnung aus Projekt, Funktion, Benutzer, Gültigkeitszeitraum und Begründung. `SQLiteProjectResponsibilityRepository` speichert diese Zuordnungen in `projectos_project_responsibilities`.

Für ein Projekt und eine Funktion dürfen sich Gültigkeitszeiträume nicht überschneiden. Direkt aufeinanderfolgende Zuordnungen sind zulässig. Nur vorhandene und aktive Benutzer können zugeordnet werden.

`ProjectResponsibilitySnapshot` löst die vier aktuell gültigen Verantwortungen zu einem bestimmten UTC-Zeitpunkt auf und liefert die zugehörigen Benutzerstammsätze.

## Fehlerkennungen

- `ERR-PRJ-0001`: Benutzer nicht gefunden
- `ERR-PRJ-0002`: Benutzer deaktiviert
- `ERR-PRJ-0003`: überlappende Projektfunktionszuordnung

## Transaktionsverhalten

Alle Schreiboperationen verwenden die bestehende `SQLiteUnitOfWork`. Bei einem Fehler wird die gesamte umgebende Transaktion zurückgerollt.

## Tests

Die Tests prüfen Persistenz und Wiederherstellung aller vier Funktionen, Überlappungsschutz, zulässige zeitliche Nachfolge und die Abweisung deaktivierter Benutzer.

## Ergebnis

AP-0046 bildet die im Architecture Freeze geforderten Projektfunktionen erstmals als persistentes und zeitlich auswertbares Runtime-Modell ab.
