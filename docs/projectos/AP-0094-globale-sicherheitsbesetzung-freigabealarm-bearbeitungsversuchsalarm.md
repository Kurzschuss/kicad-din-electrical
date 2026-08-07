# AP-0094 – Alarmbewertung abgelehnter Alarmbearbeitungsversuche

## Ziel

Wiederholte abgelehnte Bestätigungs- und Abschlussversuche globaler Sicherheitsbesetzungs-Freigabealarme werden innerhalb eines konfigurierbaren Zeitfensters deterministisch bewertet.

## Alarmstufen

- `CLEAR`
- `WARNING`
- `CRITICAL`

## Bewertbare Grenzen

- Gesamtzahl abgelehnter Bearbeitungsversuche
- Anzahl je Benutzer
- Anzahl je handelnder Rolle
- Anzahl abgelehnter Bestätigungsversuche
- Anzahl abgelehnter Abschlussversuche
- Anzahl der Versuche ohne ermittelte Person
- ausdrücklich kritische Ablehnungscodes

Standardmäßig gelten ein Zeitfenster von 24 Stunden, eine Gesamtwarnung ab drei und eine kritische Gesamtbewertung ab fünf Versuchen. Benutzergrenzen entsprechen denselben Standardwerten. Versuche ohne ermittelte Person warnen ab einem und werden ab drei Versuchen kritisch. Rollen- und Aktionsgrenzen sind standardmäßig deaktiviert.

## Sicherheitsgrenze

Die Bewertung ist ausschließlich beobachtend. Sie sperrt keine Benutzer, entzieht keine Rollen, verändert keine globale Verantwortung, ändert keinen Alarmstatus und erzeugt keine fachliche Freigabeentscheidung.

## Meldungskennungen

- `WARN-KICAD-0009` Gesamtwarnschwelle
- `WARN-KICAD-0010` Benutzerwarnschwelle
- `WARN-KICAD-0011` Rollenwarnschwelle
- `WARN-KICAD-0012` Warnschwelle Bestätigungsversuche
- `WARN-KICAD-0013` Warnschwelle Abschlussversuche
- `WARN-KICAD-0014` Warnschwelle ohne ermittelte Person
- `ERR-KICAD-0193` ungültiges Zeitfenster
- `ERR-KICAD-0194` ungültige Gesamtschwellen
- `ERR-KICAD-0195` ungültige optionale Schwelle
- `ERR-KICAD-0196` kritische Schwelle unter Warnschwelle
- `ERR-KICAD-0197` Bewertungszeitpunkt ohne Zeitzone
- `ERR-KICAD-0198` kritische Gesamtzahl
- `ERR-KICAD-0199` kritische Benutzerzahl
- `ERR-KICAD-0200` kritische Rollenzahl
- `ERR-KICAD-0201` kritische Bestätigungszahl
- `ERR-KICAD-0202` kritische Abschlusszahl
- `ERR-KICAD-0203` kritische Zahl ohne ermittelte Person
- `ERR-KICAD-0204` kritischer Ablehnungscode
