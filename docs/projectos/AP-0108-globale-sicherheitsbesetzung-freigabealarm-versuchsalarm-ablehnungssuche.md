# AP-0108 – Suche und Sicherheitsdiagnose abgelehnter Alarmbearbeitungsversuche

## Ziel

Die in AP-0107 protokollierten abgelehnten Bestätigungs- und Abschlussversuche werden kombinierbar durchsuchbar und diagnostisch auswertbar. Die Funktion ist ausschließlich lesend.

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

- Seitennummer ab 1
- Seitengröße 1 bis 200, Standard 50
- stabile Sortierung nach Versuchszeitpunkt und Versuchskennung, jeweils absteigend
- Gesamtzahl, Gesamtseiten, `has_previous` und `has_next`

## Diagnose

Die Diagnose umfasst Gesamtzahl, betroffene Alarme, unterschiedliche Personen und Rollen, Versuche ohne Person, Bestätigungs- und Abschlussversuche, ersten und letzten Zeitpunkt sowie die zehn häufigsten Ablehnungscodes, Berechtigungen und Rollen.

## Sicherheitsgrenze

Die Auswertung verändert weder Alarmstatus noch Benutzer, Rollen, Verantwortungen, Freigaben oder Auditdaten.

## Fehlerkennungen

- `ERR-KICAD-0300`: Zeitfilter ohne Zeitzonenbezug
- `ERR-KICAD-0301`: Beginn nach Ende
- `ERR-KICAD-0302`: ungültige Seitennummer
- `ERR-KICAD-0303`: ungültige Seitengröße
