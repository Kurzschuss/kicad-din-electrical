# AP-0109 – Alarmbewertung wiederholter abgelehnter Bearbeitungsversuche

## Ziel

AP-0109 bewertet die in AP-0107 protokollierten abgelehnten Bestätigungs- und Abschlussversuche innerhalb eines konfigurierbaren Zeitfensters. Die Bewertung ist ausschließlich beobachtend.

## Alarmstufen

- `CLEAR`
- `WARNING`
- `CRITICAL`

## Konfigurierbare Schwellen

- Gesamtzahl der Versuche
- Anzahl je handelnder Person
- Anzahl je Rolle
- Anzahl `ACKNOWLEDGE`
- Anzahl `RESOLVE`
- Anzahl ohne ermittelte Person
- ausdrücklich kritische Ablehnungscodes

Standardmäßig werden 24 Stunden betrachtet. Warnung erfolgt ab drei und kritisch ab fünf Gesamtversuchen beziehungsweise Versuchen derselben Person. Ohne ermittelte Person gilt standardmäßig Warnung ab einem und kritisch ab drei Versuchen.

## Verhalten

Die höchste ausgelöste Stufe bestimmt das Gesamtergebnis. Die Bewertung sperrt keine Benutzer, entzieht keine Rollen, verändert keine Verantwortung, keinen Alarmstatus und keine Auditdaten.

## Meldungskennungen

Warnungen: `WARN-KICAD-0027` bis `WARN-KICAD-0032`.

Fehler und kritische Findings: `ERR-KICAD-0304` bis `ERR-KICAD-0315`.

## Prüfung

Die Tests decken `CLEAR`, Warnung, kritische Benutzer- und Aktionsschwellen, Zeitfenster, Versuche ohne Person, kritische Ablehnungscodes und ungültige Richtlinien ab.
