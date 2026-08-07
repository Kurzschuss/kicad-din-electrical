# AP-0103 – Suche und Sicherheitsdiagnose abgelehnter Bearbeitungsversuche

## Ziel

Die in AP-0102 unveränderlich protokollierten abgelehnten Bestätigungs- und Abschlussversuche werden suchbar, paginierbar und diagnostisch auswertbar.

## Filter

Kombinierbar sind Alarmkennung, Aktion, handelnde Person, handelnde Rolle, geprüfte Berechtigung, Ablehnungscode, Korrelationskennung, Freitext in der Ablehnungsbegründung und ein einschließlich wirkender Zeitraum.

## Pagination

Seitennummern beginnen bei 1. Die Seitengröße liegt zwischen 1 und 200 und beträgt standardmäßig 50. Sortiert wird nach dem neuesten Versuch zuerst; die Versuchskennung stabilisiert die Reihenfolge bei identischen Zeitpunkten.

## Sicherheitsdiagnose

Ausgegeben werden Gesamtzahl, betroffene Alarme, unterschiedliche Personen und Rollen, Versuche ohne ermittelte Person, Verteilung auf ACKNOWLEDGE und RESOLVE, erster und letzter Zeitpunkt sowie die zehn häufigsten Ablehnungscodes, Berechtigungen und Rollen.

## Grenzen

Die Auswertung ist ausschließlich beobachtend. Sie verändert keine Alarmzustände, Benutzer, Rollen, Verantwortungen oder Auditdaten und bewertet keine Absicht oder Schuld.

## Fehlerkennungen

- ERR-KICAD-0263: Zeitfilter ohne Zeitzonenbezug
- ERR-KICAD-0264: Beginn nach Ende
- ERR-KICAD-0265: ungültige Seitennummer
- ERR-KICAD-0266: ungültige Seitengröße
