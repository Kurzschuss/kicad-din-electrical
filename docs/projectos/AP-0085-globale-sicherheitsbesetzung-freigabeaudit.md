# AP-0085 – Auditierbare Freigabeentscheidungen zur globalen Sicherheitsbesetzung

## Ziel

Technische Freigabeentscheidungen des Quality Gates aus AP-0084 werden unveränderlich und nachvollziehbar in SQLite gespeichert.

## Gespeicherte Angaben

- Freigabeentscheidungskennung
- Entscheidungszeitpunkt mit Zeitzone
- Entscheidung `APPROVED`, `REJECTED` oder `INSUFFICIENT_DATA`
- handelnde Person und Rolle
- verpflichtende Begründung
- Korrelationskennung
- zum Entscheidungszeitpunkt zugeordnete Hauptverantwortung und Stellvertretung
- Aktivstatus beider Personen
- Anzahl historisierter Verantwortungswechsel
- Zeitpunkt des letzten Wechsels
- Finding-Codes des Quality Gates

## Persistenz

Die nur anhängbare Tabelle lautet:

`projectos_global_security_staffing_release_audit`

Bereits verwendete Freigabeentscheidungskennungen können nicht überschrieben werden.

## Grenzen

Die gespeicherte Entscheidung ist eine technische ProjectOS-Freigabe. Sie verändert keine Benutzer, Rollen oder Verantwortungen und ersetzt keine organisatorische, rechtliche oder personelle Freigabe.

## Fehlerkennungen

- `ERR-KICAD-0142` – Freigabezeitpunkt ohne Zeitzone
- `ERR-KICAD-0143` – Begründung fehlt
- `ERR-KICAD-0144` – Freigabeentscheidungskennung bereits vorhanden
- `ERR-KICAD-0145` – Freigabeentscheidung nicht gefunden
