# AP-0095 – Persistente Alarme abgelehnter Alarmbearbeitungsversuche

## Ziel

Alarmbewertungen aus AP-0094 werden als nachvollziehbare SQLite-Ereignisse gespeichert und kontrolliert bearbeitet.

## Lebenszyklus

`OPEN → ACKNOWLEDGED → RESOLVED`

Ein direkter Wechsel von `OPEN` nach `RESOLVED` ist unzulässig. Bestätigung und Abschluss benötigen jeweils Person, Zeitzonenzeitpunkt und Begründung.

## Persistenz

Tabelle: `projectos_global_security_staffing_release_alert_attempt_alerts`

Gespeichert werden Alarmstufe, Zeitfenster, Gesamtzahl, Bestätigungs- und Abschlussversuche, Versuche ohne ermittelte Person, Finding-Codes, Korrelationskennung sowie dokumentierte Bearbeitungsdaten.

## Grenzen

`CLEAR` wird nicht gespeichert. Die Bearbeitung sperrt keine Benutzer, verändert keine Rollen, Verantwortungen oder Freigaben und bewertet keine Absicht oder Schuld.

## Fehlerkennungen

- `ERR-KICAD-0205` CLEAR darf nicht gespeichert werden
- `ERR-KICAD-0206` Alarmzeitpunkt ohne Zeitzone
- `ERR-KICAD-0207` doppelte Alarmkennung
- `ERR-KICAD-0208` unzulässige Bestätigung
- `ERR-KICAD-0209` Bestätigung vor Erzeugung
- `ERR-KICAD-0210` unzulässiger Abschluss
- `ERR-KICAD-0211` Abschluss vor Bestätigung
- `ERR-KICAD-0212` Alarm nicht gefunden
- `ERR-KICAD-0213` Bearbeitungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0214` Bearbeitungsbegründung fehlt
