# AP-0111 – Autorisierung und unveränderliches Bearbeitungsaudit

## Ziel

Bestätigung und Abschluss der in AP-0110 eingeführten Alarmklasse werden über die globale Sicherheitsverantwortung autorisiert und append-only auditiert.

## Regeln

- `ACKNOWLEDGE` und `RESOLVE` besitzen getrennte Berechtigungen.
- Zuerst wird die globale Hauptverantwortung ermittelt; bei dokumentierter Abwesenheit wird die Stellvertretung verwendet.
- Neben der Benutzerberechtigung muss die angegebene handelnde Rolle die erforderliche Berechtigung tatsächlich erteilen.
- Nur erfolgreiche Bearbeitungen erzeugen einen Eintrag im Erfolgs-Audit.
- Bei fehlender Berechtigung oder unpassender Rolle bleiben Alarmstatus und Erfolgs-Audit unverändert.
- Das Bearbeitungsaudit ist ausschließlich anhängbar.

## Persistenz

Tabelle:

`projectos_global_security_staffing_release_alert_attempt_action_attempt_alert_action_attempt_alert_action_attempt_alert_action_audit`

Gespeichert werden Aktionskennung, Alarmkennung, Aktion, Zeitpunkt, handelnde Person, Rolle, Berechtigung, Verantwortungsquelle, Begründung und Korrelationskennung.

## Fehlerkennungen

- `ERR-KICAD-0326` Auditzeitpunkt ohne Zeitzone
- `ERR-KICAD-0327` fehlende Auditbegründung
- `ERR-KICAD-0328` doppelte Aktionskennung
- `ERR-KICAD-0329` Benutzerautorisierung abgelehnt
- `ERR-KICAD-0330` handelnde Rolle erteilt die Berechtigung nicht

## Grenzen

Die Funktion sperrt keine Benutzer, entzieht keine Rollen und verändert keine globale Sicherheitsverantwortung.
