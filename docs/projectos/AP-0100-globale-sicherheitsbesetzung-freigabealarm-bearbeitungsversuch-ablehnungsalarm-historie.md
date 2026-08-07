# AP-0100 – Persistente Alarme für wiederholte abgelehnte Bearbeitungsversuche

## Ziel

Alarmbewertungen aus AP-0099 werden als nachvollziehbare SQLite-Historie gespeichert und über einen dokumentierten Lebenszyklus bearbeitet.

## Lebenszyklus

`OPEN → ACKNOWLEDGED → RESOLVED`

Ein direkter Abschluss eines offenen Alarms ist unzulässig. Bestätigung und Abschluss benötigen jeweils eine handelnde Person, einen Zeitzonenzeitpunkt und eine Begründung.

## Persistenz

Tabelle: `projectos_global_security_staffing_release_alert_attempt_action_attempt_alerts`

Gespeichert werden Alarmstufe, Status, Bewertungszeitraum, Gesamtzahl, Bestätigungs- und Abschlussversuche, Versuche ohne ermittelte Person, Finding-Codes, Korrelationskennung und die dokumentierten Bearbeitungsschritte.

## Grenzen

`CLEAR`-Ergebnisse werden nicht gespeichert. Die Historie sperrt keine Benutzer, verändert keine Rollen oder Verantwortungen und trifft keine fachliche Freigabeentscheidung.

## Fehlerkennungen

- `ERR-KICAD-0242` bis `ERR-KICAD-0251`
