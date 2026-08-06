# AP-0099 – Alarmbewertung abgelehnter Bearbeitungsversuche

## Ziel

Wiederholte abgelehnte Bestätigungs- und Abschlussversuche aus AP-0097 werden innerhalb eines konfigurierbaren Zeitfensters rein beobachtend bewertet.

## Alarmstufen

- `CLEAR`
- `WARNING`
- `CRITICAL`

## Konfigurierbare Schwellen

- Gesamtzahl der Versuche
- Anzahl je Benutzer
- Anzahl je handelnder Rolle
- Anzahl abgelehnter Bestätigungsversuche
- Anzahl abgelehnter Abschlussversuche
- Anzahl ohne ermittelte Person
- ausdrücklich kritische Ablehnungscodes

Die höchste ausgelöste Stufe bestimmt das Gesamtergebnis. Standardmäßig werden 24 Stunden ausgewertet; Warnung erfolgt insgesamt ab drei und kritisch ab fünf Versuchen. Rollen- und Aktionsschwellen sind standardmäßig deaktiviert.

## Grenzen

Die Bewertung sperrt keine Benutzer, entzieht keine Rollen, verändert keine globale Verantwortung, keinen Alarmstatus und kein Audit. Sie bewertet weder Absicht noch Schuld.

## Meldungen

- `WARN-KICAD-0015` Gesamtwarnschwelle
- `WARN-KICAD-0016` Benutzerwarnschwelle
- `WARN-KICAD-0017` Rollenwarnschwelle
- `WARN-KICAD-0018` Warnschwelle Bestätigungsversuche
- `WARN-KICAD-0019` Warnschwelle Abschlussversuche
- `WARN-KICAD-0020` Warnschwelle ohne ermittelte Person
- `ERR-KICAD-0230` bis `ERR-KICAD-0241` Richtlinien-, Zeit- und kritische Alarmbefunde
