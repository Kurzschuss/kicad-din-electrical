# AP-0104 – Alarmbewertung abgelehnter Bearbeitungsversuche

## Ziel

Wiederholte, in AP-0102 protokollierte Ablehnungen werden innerhalb eines konfigurierbaren Zeitfensters rein beobachtend bewertet.

## Alarmstufen

- `CLEAR`
- `WARNING`
- `CRITICAL`

## Konfigurierbare Schwellen

- Gesamtzahl
- Anzahl je Benutzer
- Anzahl je Rolle
- `ACKNOWLEDGE`-Versuche
- `RESOLVE`-Versuche
- Versuche ohne ermittelte Person
- kritische Ablehnungscodes
- Zeitfenster

Die höchste ausgelöste Stufe bestimmt das Ergebnis. Die Bewertung sperrt keine Benutzer, verändert keine Rollen, Verantwortungen, Alarmzustände oder Auditdaten.

## Meldungen

Warnungen: `WARN-KICAD-0021` bis `WARN-KICAD-0026`.

Fehler beziehungsweise kritische Findings: `ERR-KICAD-0267` bis `ERR-KICAD-0278`.
