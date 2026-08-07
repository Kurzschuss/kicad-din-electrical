# AP-0093 – Suche und Sicherheitsdiagnose abgelehnter Alarmbearbeitungen

## Ziel

Abgelehnte Bestätigungs- und Abschlussversuche globaler Sicherheitsbesetzungs-Freigabealarme werden paginiert, kombinierbar gefiltert und rein beobachtend diagnostiziert.

## Filter

- Alarmkennung
- Aktion `ACKNOWLEDGE` oder `RESOLVE`
- handelnde Person
- handelnde Rolle
- geprüfte Berechtigung
- Ablehnungscode
- Korrelationskennung
- Freitext der Ablehnungsbegründung
- einschließlich wirkender Zeitraum

## Pagination

Seitennummern beginnen bei 1. Die Seitengröße liegt zwischen 1 und 200; Standard ist 50. Sortiert wird nach dem neuesten Versuch zuerst.

## Diagnose

Die Diagnose liefert Gesamtzahl, betroffene Alarme, Benutzer und Rollen, Versuche ohne ermittelte Person, Verteilung auf Bestätigung und Abschluss, ersten und letzten Zeitpunkt sowie häufigste Ablehnungscodes, Berechtigungen und Rollen.

## Grenzen

Die Auswertung sperrt keine Benutzer, verändert keine Rollen oder Verantwortungen und ändert weder Alarmstatus noch Freigabe- oder Bearbeitungsaudits.

## Meldungscodes

- `ERR-KICAD-0189`: Zeitfilter ohne Zeitzone
- `ERR-KICAD-0190`: Beginn nach Ende
- `ERR-KICAD-0191`: ungültige Seitennummer
- `ERR-KICAD-0192`: ungültige Seitengröße
