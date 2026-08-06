# AP-0090 – Persistente Alarmereignisse für globale Besetzungsfreigabeversuche

## Ziel

Alarmbewertungen aus AP-0089 werden dauerhaft und nachvollziehbar gespeichert. Die Bearbeitung folgt dem verbindlichen Lebenszyklus:

`OPEN → ACKNOWLEDGED → RESOLVED`

## Regeln

- `CLEAR` wird nicht gespeichert.
- Alarm- und Bearbeitungszeitpunkte benötigen eine Zeitzone.
- Nur offene Alarme können bestätigt werden.
- Nur bestätigte Alarme können abgeschlossen werden.
- Bestätigung und Abschluss benötigen Person und Begründung.
- Zeitpunkte müssen chronologisch sein.
- Die Bearbeitung verändert keine Benutzer, Rollen, Verantwortungen oder Freigaben.

## Persistenz

SQLite-Tabelle: `projectos_global_security_staffing_release_alerts`

Gespeichert werden Alarmstufe, Status, Zeitfenster, Versuchszahlen, Finding-Codes, Korrelationskennung sowie dokumentierte Bestätigung und Bearbeitung.

## Fehlerkennungen

- `ERR-KICAD-0168` CLEAR darf nicht gespeichert werden
- `ERR-KICAD-0169` Alarmzeitpunkt ohne Zeitzone
- `ERR-KICAD-0170` doppelte Alarmkennung
- `ERR-KICAD-0171` ungültige Bestätigung
- `ERR-KICAD-0172` Bestätigung vor Erzeugung
- `ERR-KICAD-0173` ungültiger Abschluss
- `ERR-KICAD-0174` Abschluss vor Bestätigung
- `ERR-KICAD-0175` Alarm nicht gefunden
- `ERR-KICAD-0176` Bearbeitungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0177` Bearbeitungsbegründung fehlt
