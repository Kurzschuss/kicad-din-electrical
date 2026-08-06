# AP-0105 – Persistente Alarmereignisse

## Ziel

Alarmresultate aus AP-0104 werden persistent und nachvollziehbar gespeichert. Nur `WARNING` und `CRITICAL` erzeugen einen Alarmdatensatz.

## Lebenszyklus

`OPEN → ACKNOWLEDGED → RESOLVED`

Ein direkter Abschluss eines offenen Alarms ist ausgeschlossen.

## Persistente Daten

- Alarmkennung und Alarmstufe
- Status
- Erzeugungszeitpunkt und Beginn des Bewertungsfensters
- Gesamt-, Bestätigungs- und Abschlussversuche
- Versuche ohne ermittelte Person
- Finding-Codes und Korrelationskennung
- bestätigende und abschließende Person, Zeit und Begründung

## Sicherheitsgrenzen

Die Bearbeitung verändert keine Benutzer, Rollen, Verantwortungen, Freigaben oder zugrunde liegenden Versuchsaudits.

## Fehlerkennungen

- `ERR-KICAD-0279` CLEAR darf nicht gespeichert werden
- `ERR-KICAD-0280` Alarmzeitpunkt ohne Zeitzone
- `ERR-KICAD-0281` doppelte Alarmkennung
- `ERR-KICAD-0282` ungültige Bestätigung
- `ERR-KICAD-0283` Bestätigung vor Erzeugung
- `ERR-KICAD-0284` ungültiger Abschluss
- `ERR-KICAD-0285` Abschluss vor Bestätigung
- `ERR-KICAD-0286` Alarm nicht gefunden
- `ERR-KICAD-0287` Bearbeitungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0288` Bearbeitungsbegründung fehlt
