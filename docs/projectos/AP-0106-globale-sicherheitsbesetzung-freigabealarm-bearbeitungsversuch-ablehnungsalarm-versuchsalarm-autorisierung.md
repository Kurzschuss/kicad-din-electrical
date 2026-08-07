# AP-0106 – Autorisierung und Bearbeitungsaudit der AP-0105-Alarmklasse

## Ziel

Bestätigung und Abschluss der in AP-0105 persistent gespeicherten Sicherheitsalarme werden über die globale Sicherheitsverantwortung autorisiert und unveränderlich protokolliert.

## Berechtigungen

- `PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-ACTION-ATTEMPT-ACKNOWLEDGE`
- `PERM-KICAD-GLOBAL-SECURITY-STAFFING-RELEASE-ALERT-ATTEMPT-ACTION-ATTEMPT-ACTION-ATTEMPT-RESOLVE`

Bestätigung und Abschluss sind getrennt delegierbar. Neben der Benutzerautorisierung muss die angegebene handelnde Rolle die jeweilige Berechtigung tatsächlich erteilen.

## Ablauf

1. globale Hauptverantwortung auflösen,
2. bei dokumentierter Abwesenheit die Stellvertretung verwenden,
3. Benutzerberechtigung und handelnde Rolle prüfen,
4. Alarmstatus ändern,
5. append-only Bearbeitungsaudit speichern.

Bei einer Autorisierungsablehnung bleiben Alarmstatus und Erfolgs-Audit unverändert.

## Auditdaten

Gespeichert werden Aktionskennung, Alarmkennung, Aktion, Zeitpunkt, handelnde Person, Rolle, Berechtigung, verwendete Verantwortung, Begründung und Korrelationskennung.

## Fehlerkennungen

- `ERR-KICAD-0289` – Auditzeitpunkt ohne Zeitzone
- `ERR-KICAD-0290` – Auditbegründung fehlt
- `ERR-KICAD-0291` – Aktionskennung bereits vorhanden
- `ERR-KICAD-0292` – Benutzerautorisierung lehnt die Bearbeitung ab
- `ERR-KICAD-0293` – handelnde Rolle erteilt die Berechtigung nicht

## Grenzen

Die Bearbeitung sperrt keine Benutzer, verändert keine Rollen oder Verantwortungen und erzeugt keine Freigabeentscheidung.
