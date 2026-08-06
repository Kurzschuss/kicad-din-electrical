# AP-0088 – Suche und Sicherheitsdiagnose globaler Besetzungsfreigabeversuche

## Ziel

Abgelehnte globale Sicherheitsbesetzungs-Freigabeversuche werden paginiert, kombinierbar gefiltert und ausschließlich beobachtend diagnostiziert.

## Filter

- handelnde Person
- angegebene Rolle
- geprüfte Berechtigung
- Ablehnungscode
- Korrelationskennung
- Text in der Ablehnungsbegründung
- einschließlich wirkender Zeitraum

## Pagination

- Seitennummer ab 1
- Seitengröße 1 bis 200
- Standardgröße 50
- neuester Versuch zuerst

## Sicherheitsdiagnose

Die Diagnose liefert Gesamtzahl, unterschiedliche Personen und Rollen, Versuche ohne ermittelte Person, ersten und letzten Zeitpunkt sowie die zehn häufigsten Ablehnungscodes, Berechtigungen und Rollen.

Sie bewertet keine Absicht und verändert keine Benutzer, Rollen, Verantwortungen oder Freigabeentscheidungen.

## Fehlerkennungen

- `ERR-KICAD-0154`: Zeitfilter ohne Zeitzone
- `ERR-KICAD-0155`: Beginn nach Ende
- `ERR-KICAD-0156`: ungültige Seitennummer
- `ERR-KICAD-0157`: ungültige Seitengröße
