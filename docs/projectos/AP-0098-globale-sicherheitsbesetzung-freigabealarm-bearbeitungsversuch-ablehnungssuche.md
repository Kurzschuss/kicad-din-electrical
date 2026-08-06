# AP-0098 – Suche und Sicherheitsdiagnose abgelehnter Bearbeitungsversuche

## Ziel

Die in AP-0097 unveränderlich protokollierten abgelehnten Bestätigungs- und Abschlussversuche werden paginiert, kombinierbar filterbar und rein beobachtend diagnostizierbar.

## Filter

- Alarmkennung
- Aktion `ACKNOWLEDGE` oder `RESOLVE`
- handelnde Person
- handelnde Rolle
- geprüfte Berechtigung
- Ablehnungscode
- Korrelationskennung
- Freitext in der Ablehnungsbegründung
- einschließlich wirkender Zeitraum

## Pagination

Seitennummern beginnen bei 1. Die Seitengröße liegt zwischen 1 und 200, Standard ist 50. Sortiert wird nach Versuchszeitpunkt und Versuchskennung, jeweils neueste zuerst.

## Diagnose

Die Diagnose liefert Gesamtzahl, betroffene Alarme, unterschiedliche Personen und Rollen, Versuche ohne ermittelte Person, getrennte Bestätigungs- und Abschlusszahlen, ersten und letzten Zeitpunkt sowie die zehn häufigsten Ablehnungscodes, Berechtigungen und Rollen.

Die Auswertung verändert keine Alarmzustände, Rollen, Verantwortungen oder Auditdaten und bewertet weder Absicht noch Schuld.

## Fehlerkennungen

- `ERR-KICAD-0226`: Zeitfilter ohne Zeitzonenbezug
- `ERR-KICAD-0227`: Beginn liegt nach dem Ende
- `ERR-KICAD-0228`: ungültige Seitennummer
- `ERR-KICAD-0229`: ungültige Seitengröße
